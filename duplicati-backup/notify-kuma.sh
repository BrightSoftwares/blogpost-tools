#!/bin/bash
# =============================================================================
# notify-kuma.sh — Duplicati → Uptime Kuma push notification script
#
# Usage (set in Duplicati advanced options):
#   --run-script-after=/scripts/notify-kuma.sh
#   --run-script-with-arguments=true
#
# The push URL is passed as the first argument:
#   --run-script-after="/scripts/notify-kuma.sh https://kuma.example.com/api/push/TOKEN123"
#
# Or set via environment variable KUMA_PUSH_URL (useful in Docker compose).
# Argument takes precedence over the environment variable.
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# 1. Resolve the push URL (arg > env > fail)
# ---------------------------------------------------------------------------
PUSH_URL="${1:-${KUMA_PUSH_URL:-}}"

if [[ -z "$PUSH_URL" ]]; then
  echo "ERROR: No Uptime Kuma push URL provided." >&2
  echo "  Pass it as the first argument or set KUMA_PUSH_URL env var." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# 2. Only act on AFTER events — ignore BEFORE calls
# ---------------------------------------------------------------------------
if [[ "${DUPLICATI__EVENTNAME:-}" != "AFTER" ]]; then
  exit 0
fi

# Only monitor Backup operations (skip Cleanup, Restore, etc.)
if [[ "${DUPLICATI__OPERATIONNAME:-}" != "Backup" ]]; then
  exit 0
fi

# ---------------------------------------------------------------------------
# 3. Determine status from PARSED_RESULT
#    Success / Warning → "up"   |   Error / Fatal / Unknown → "down"
# ---------------------------------------------------------------------------
PARSED_RESULT="${DUPLICATI__PARSED_RESULT:-Unknown}"

case "$PARSED_RESULT" in
  Success|Warning)
    STATUS="up"
    ;;
  *)
    STATUS="down"
    ;;
esac

# ---------------------------------------------------------------------------
# 4. Parse the result file for rich stats (no relay needed — pure bash+awk)
#    Duplicati writes a structured text report to DUPLICATI__RESULTFILE
# ---------------------------------------------------------------------------
RESULT_FILE="${DUPLICATI__RESULTFILE:-}"

EXAMINED_FILES=""
OPENED_FILES=""
ADDED_FILES=""
DELETED_FILES=""
MODIFIED_FILES=""
SIZE_OF_EXAMINED=""
SIZE_OF_ADDED=""
UPLOAD_SIZE=""
UPLOAD_SPEED=""
DURATION=""
BEGIN_TIME=""
END_TIME=""
WARNINGS=""
ERRORS=""

if [[ -n "$RESULT_FILE" && -f "$RESULT_FILE" ]]; then
  # Extract key/value lines from the Duplicati result report
  parse_field() {
    grep -i "^$1:" "$RESULT_FILE" 2>/dev/null | head -1 | sed 's/^[^:]*: *//' | tr -d '\r'
  }

  EXAMINED_FILES=$(parse_field "ExaminedFiles")
  OPENED_FILES=$(parse_field "OpenedFiles")
  ADDED_FILES=$(parse_field "AddedFiles")
  DELETED_FILES=$(parse_field "DeletedFiles")
  MODIFIED_FILES=$(parse_field "ModifiedFiles")
  SIZE_OF_EXAMINED=$(parse_field "SizeOfExaminedFiles")
  SIZE_OF_ADDED=$(parse_field "SizeOfAddedFiles")
  UPLOAD_SIZE=$(parse_field "CompressedFileSize")
  DURATION=$(parse_field "Duration")
  BEGIN_TIME=$(parse_field "BeginTime")
  END_TIME=$(parse_field "EndTime")

  # Count warnings and errors (lines starting with "Warning:" or "Error:")
  WARNINGS=$(grep -c "^Warning:" "$RESULT_FILE" 2>/dev/null || echo "0")
  ERRORS=$(grep -c "^Error:" "$RESULT_FILE" 2>/dev/null || echo "0")
fi

# ---------------------------------------------------------------------------
# 5. Compute backup duration in milliseconds for Kuma's "ping" field
#    Duration format from Duplicati: "00:03:42.1234567"
# ---------------------------------------------------------------------------
PING_MS=""
if [[ -n "$DURATION" ]]; then
  # Parse HH:MM:SS.fraction
  IFS=: read -r DUR_H DUR_M DUR_S <<< "$DURATION"
  DUR_S_INT="${DUR_S%%.*}"  # drop sub-second fraction
  PING_MS=$(( (10#$DUR_H * 3600 + 10#$DUR_M * 60 + 10#${DUR_S_INT:-0}) * 1000 ))
fi

# ---------------------------------------------------------------------------
# 6. Build the msg string (max ~250 chars for Uptime Kuma)
#    Priority order: result, key stats, errors/warnings
# ---------------------------------------------------------------------------
MSG_PARTS=()
MSG_PARTS+=("${PARSED_RESULT}")

[[ -n "$DURATION" ]]       && MSG_PARTS+=("⏱${DURATION}")
[[ -n "$ADDED_FILES" ]]    && MSG_PARTS+=("➕${ADDED_FILES} added")
[[ -n "$MODIFIED_FILES" ]] && MSG_PARTS+=("✏️${MODIFIED_FILES} mod")
[[ -n "$DELETED_FILES" ]]  && MSG_PARTS+=("🗑${DELETED_FILES} del")
[[ -n "$EXAMINED_FILES" ]] && MSG_PARTS+=("🔍${EXAMINED_FILES} files")
[[ -n "$SIZE_OF_ADDED" ]]  && MSG_PARTS+=("📦${SIZE_OF_ADDED}")
[[ -n "$UPLOAD_SIZE" ]]    && MSG_PARTS+=("☁️${UPLOAD_SIZE} uploaded")

if [[ "$WARNINGS" -gt 0 ]] 2>/dev/null; then
  MSG_PARTS+=("⚠️${WARNINGS}w")
fi
if [[ "$ERRORS" -gt 0 ]] 2>/dev/null; then
  MSG_PARTS+=("❌${ERRORS}e")
fi

# Join parts with " | " and trim to 250 chars
MSG=$(printf '%s' "$(IFS="|"; echo "${MSG_PARTS[*]}")" | cut -c1-250)

# URL-encode the message (encode spaces and special chars)
MSG_ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$MSG" 2>/dev/null \
  || printf '%s' "$MSG" | sed 's/ /%20/g; s/|/%7C/g; s/⏱/%E2%8F%B1/g')

# ---------------------------------------------------------------------------
# 7. Build the final URL and push
# ---------------------------------------------------------------------------
# Strip trailing slash from push URL if present
PUSH_URL="${PUSH_URL%/}"

FINAL_URL="${PUSH_URL}?status=${STATUS}&msg=${MSG_ENCODED}"
[[ -n "$PING_MS" ]] && FINAL_URL="${FINAL_URL}&ping=${PING_MS}"

# Log to Duplicati's own log system
echo "LOG:INFO notify-kuma.sh: pushing status=${STATUS} to Uptime Kuma"

HTTP_RESPONSE=$(curl \
  --silent \
  --max-time 15 \
  --retry 3 \
  --retry-delay 5 \
  --write-out "%{http_code}" \
  --output /tmp/kuma_response.txt \
  "$FINAL_URL" 2>&1)

HTTP_BODY=$(cat /tmp/kuma_response.txt 2>/dev/null || echo "")

if [[ "$HTTP_RESPONSE" == "200" ]]; then
  echo "LOG:INFO notify-kuma.sh: Uptime Kuma acknowledged (HTTP 200). Body: ${HTTP_BODY}"
else
  echo "LOG:WARN notify-kuma.sh: Uptime Kuma responded HTTP ${HTTP_RESPONSE}. Body: ${HTTP_BODY}" >&2
fi

# Always exit 0 — a notification failure must never abort the backup report
exit 0
