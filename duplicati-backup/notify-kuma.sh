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

# ---------------------------------------------------------------------------
# CRITICAL: do NOT use "set -e" or "set -euo pipefail" here.
# grep returns exit code 1 when it finds no matches, which would silently
# kill the script mid-execution under -e. We handle errors explicitly instead.
# ---------------------------------------------------------------------------
set -uo pipefail

dbg() { echo "LOG:INFO [notify-kuma] $*" >&2; }
warn() { echo "LOG:WARN [notify-kuma] $*" >&2; }
err()  { echo "LOG:ERROR [notify-kuma] $*" >&2; }

dbg "============================================================"
dbg "Script started. Bash version: ${BASH_VERSION}"
dbg "Script path: $0"
dbg "Arguments: $*"
dbg "============================================================"

# ---------------------------------------------------------------------------
# 1. Resolve the push URL (arg > env > fail)
# ---------------------------------------------------------------------------
PUSH_URL="${1:-${KUMA_PUSH_URL:-}}"
dbg "Resolved PUSH_URL: ${PUSH_URL:-<empty>}"

if [[ -z "$PUSH_URL" ]]; then
  err "No Uptime Kuma push URL provided."
  err "Pass it as the first argument or set KUMA_PUSH_URL env var."
  exit 1
fi

# ---------------------------------------------------------------------------
# 2. Dump all DUPLICATI__ environment variables for debugging
# ---------------------------------------------------------------------------
dbg "--- Duplicati environment variables ---"
while IFS='=' read -r key val; do
  dbg "  $key=$val"
done < <(env | grep '^DUPLICATI__' | sort)
dbg "--- End of Duplicati env vars ---"

# ---------------------------------------------------------------------------
# 3. Only act on AFTER events — ignore BEFORE calls
# ---------------------------------------------------------------------------
EVENT="${DUPLICATI__EVENTNAME:-}"
dbg "DUPLICATI__EVENTNAME = '${EVENT}'"

if [[ "$EVENT" != "AFTER" ]]; then
  dbg "Skipping: event is '${EVENT}', not 'AFTER'. Exiting cleanly."
  exit 0
fi

# Only monitor Backup operations (skip Cleanup, Restore, etc.)
OPERATION="${DUPLICATI__OPERATIONNAME:-}"
dbg "DUPLICATI__OPERATIONNAME = '${OPERATION}'"

if [[ "$OPERATION" != "Backup" ]]; then
  dbg "Skipping: operation is '${OPERATION}', not 'Backup'. Exiting cleanly."
  exit 0
fi

# ---------------------------------------------------------------------------
# 4. Determine status from PARSED_RESULT
#    Success / Warning → "up"   |   Error / Fatal / Unknown → "down"
# ---------------------------------------------------------------------------
PARSED_RESULT="${DUPLICATI__PARSED_RESULT:-Unknown}"
dbg "DUPLICATI__PARSED_RESULT = '${PARSED_RESULT}'"

case "$PARSED_RESULT" in
  Success|Warning)
    STATUS="up"
    ;;
  *)
    STATUS="down"
    ;;
esac
dbg "Resolved Kuma status: '${STATUS}'"

# ---------------------------------------------------------------------------
# 5. Parse the result file for rich stats
#    Duplicati writes a structured text report to DUPLICATI__RESULTFILE
# ---------------------------------------------------------------------------
RESULT_FILE="${DUPLICATI__RESULTFILE:-}"
dbg "DUPLICATI__RESULTFILE = '${RESULT_FILE:-<not set>}'"

EXAMINED_FILES=""
OPENED_FILES=""
ADDED_FILES=""
DELETED_FILES=""
MODIFIED_FILES=""
SIZE_OF_EXAMINED=""
SIZE_OF_ADDED=""
UPLOAD_SIZE=""
DURATION=""
BEGIN_TIME=""
END_TIME=""
WARNINGS="0"
ERRORS="0"

if [[ -z "$RESULT_FILE" ]]; then
  warn "DUPLICATI__RESULTFILE is not set — no stats will be included in the message."
elif [[ ! -f "$RESULT_FILE" ]]; then
  warn "Result file '${RESULT_FILE}' does not exist or is not readable."
  dbg "Directory listing of result file parent:"
  ls -la "$(dirname "$RESULT_FILE")" >&2 || true
else
  dbg "Result file found. Size: $(wc -c < "$RESULT_FILE") bytes."
  dbg "--- Result file contents ---"
  cat "$RESULT_FILE" >&2 || true
  dbg "--- End of result file ---"

  # parse_field: grep for a key, return the value. Returns "" if not found.
  # The "|| true" prevents -o pipefail from killing the script on no-match.
  parse_field() {
    local field="$1"
    local result
    result=$(grep -i "^${field}:" "$RESULT_FILE" 2>/dev/null | head -1 | sed 's/^[^:]*: *//' | tr -d '\r') || true
    echo "$result"
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

  # grep -c returns 0 lines as "0" and exit code 1 — the "|| echo" handles that
  WARNINGS=$(grep -c "^Warning:" "$RESULT_FILE" 2>/dev/null || echo "0")
  ERRORS=$(grep -c "^Error:"   "$RESULT_FILE" 2>/dev/null || echo "0")

  dbg "Parsed fields:"
  dbg "  ExaminedFiles    = '${EXAMINED_FILES}'"
  dbg "  OpenedFiles      = '${OPENED_FILES}'"
  dbg "  AddedFiles       = '${ADDED_FILES}'"
  dbg "  ModifiedFiles    = '${MODIFIED_FILES}'"
  dbg "  DeletedFiles     = '${DELETED_FILES}'"
  dbg "  SizeOfExamined   = '${SIZE_OF_EXAMINED}'"
  dbg "  SizeOfAdded      = '${SIZE_OF_ADDED}'"
  dbg "  CompressedSize   = '${UPLOAD_SIZE}'"
  dbg "  Duration         = '${DURATION}'"
  dbg "  BeginTime        = '${BEGIN_TIME}'"
  dbg "  EndTime          = '${END_TIME}'"
  dbg "  Warnings         = '${WARNINGS}'"
  dbg "  Errors           = '${ERRORS}'"
fi

# ---------------------------------------------------------------------------
# 6. Compute backup duration in milliseconds for Kuma's "ping" field
#    Duration format from Duplicati: "00:03:42.1234567"
# ---------------------------------------------------------------------------
PING_MS=""
if [[ -n "$DURATION" ]]; then
  IFS=: read -r DUR_H DUR_M DUR_S <<< "$DURATION"
  DUR_S_INT="${DUR_S%%.*}"   # drop sub-second fraction
  PING_MS=$(( (10#$DUR_H * 3600 + 10#$DUR_M * 60 + 10#${DUR_S_INT:-0}) * 1000 )) || true
  dbg "Duration '${DURATION}' → ping = ${PING_MS} ms"
else
  dbg "No Duration found; ping field will be omitted."
fi

# ---------------------------------------------------------------------------
# 7. Build the msg string (max ~250 chars for Uptime Kuma)
# ---------------------------------------------------------------------------
MSG_PARTS=()
MSG_PARTS+=("${PARSED_RESULT}")

[[ -n "$DURATION" ]]       && MSG_PARTS+=("⏱${DURATION}")
[[ -n "$ADDED_FILES" ]]    && MSG_PARTS+=("➕${ADDED_FILES} added")
[[ -n "$MODIFIED_FILES" ]] && MSG_PARTS+=("✏${MODIFIED_FILES} mod")
[[ -n "$DELETED_FILES" ]]  && MSG_PARTS+=("🗑${DELETED_FILES} del")
[[ -n "$EXAMINED_FILES" ]] && MSG_PARTS+=("🔍${EXAMINED_FILES} files")
[[ -n "$SIZE_OF_ADDED" ]]  && MSG_PARTS+=("📦${SIZE_OF_ADDED}")
[[ -n "$UPLOAD_SIZE" ]]    && MSG_PARTS+=("☁${UPLOAD_SIZE} uploaded")

if [[ "${WARNINGS}" -gt 0 ]] 2>/dev/null; then
  MSG_PARTS+=("⚠${WARNINGS}w")
fi
if [[ "${ERRORS}" -gt 0 ]] 2>/dev/null; then
  MSG_PARTS+=("❌${ERRORS}e")
fi

# Join with pipe separator and trim to 250 chars
MSG=$(printf '%s' "$(IFS="|"; echo "${MSG_PARTS[*]}")" | cut -c1-250)
dbg "Raw MSG (pre-encode): '${MSG}'"

# URL-encode using python3 (always available in this image)
MSG_ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$MSG" 2>/dev/null || true)
if [[ -z "$MSG_ENCODED" ]]; then
  warn "python3 URL-encoding failed, falling back to basic sed encoding."
  MSG_ENCODED=$(printf '%s' "$MSG" | sed 's/ /%20/g; s/|/%7C/g')
fi
dbg "Encoded MSG: '${MSG_ENCODED}'"

# ---------------------------------------------------------------------------
# 8. Build the final URL and push to Uptime Kuma
# ---------------------------------------------------------------------------
PUSH_URL="${PUSH_URL%/}"   # strip trailing slash

FINAL_URL="${PUSH_URL}?status=${STATUS}&msg=${MSG_ENCODED}"
[[ -n "$PING_MS" ]] && FINAL_URL="${FINAL_URL}&ping=${PING_MS}"

dbg "Final push URL: '${FINAL_URL}'"
dbg "Sending push to Uptime Kuma..."

HTTP_RESPONSE=$(curl \
  --silent \
  --max-time 15 \
  --retry 3 \
  --retry-delay 5 \
  --write-out "%{http_code}" \
  --output /tmp/kuma_response.txt \
  "$FINAL_URL" 2>&1) || true

HTTP_BODY=$(cat /tmp/kuma_response.txt 2>/dev/null || echo "<no response body>")

if [[ "$HTTP_RESPONSE" == "200" ]]; then
  dbg "Uptime Kuma acknowledged push (HTTP 200). Response: ${HTTP_BODY}"
else
  warn "Uptime Kuma responded HTTP ${HTTP_RESPONSE}. Response body: ${HTTP_BODY}"
fi

dbg "Script completed successfully."

# Always exit 0 — a notification failure must never abort the backup report
exit 0
