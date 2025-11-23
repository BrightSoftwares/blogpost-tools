#!/bin/bash
#
# Fix smart-cv Gemfile - ensure clean Ruby 3.4 stdlib gems
#

GITHUB_TOKEN="$1"
BRANCH="migration/standardize-jekyll-20251123_182523"
REPO="sergioafanou/smart-cv"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Usage: $0 <github_token>"
    exit 1
fi

log_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }

log_info "Fetching current Gemfile from $REPO..."

# Get current Gemfile
gemfile=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://raw.githubusercontent.com/$REPO/$BRANCH/Gemfile")

if [[ -z "$gemfile" || "$gemfile" == "404: Not Found" ]]; then
    log_error "Could not fetch Gemfile"
    exit 1
fi

echo "Current Gemfile:"
echo "$gemfile"
echo ""

# Remove all existing Ruby 3.4 stdlib gem declarations (clean slate)
new_gemfile=$(echo "$gemfile" | grep -v 'gem "csv"' | grep -v 'gem "mutex_m"' | grep -v 'gem "logger"' | grep -v 'gem "base64"' | grep -v 'gem "bigdecimal"' | grep -v 'gem "observer"' | grep -v 'gem "ostruct"' | grep -v '# Required for Ruby 3.4')

# Remove empty lines at the start after source
new_gemfile=$(echo "$new_gemfile" | awk '
    /^source/ { print; getline; while (/^$/) getline; print; next }
    { print }
')

# Add clean Ruby 3.4 gems block after source line
ruby34_gems='
# Required for Ruby 3.4+ (no longer bundled in stdlib)
gem "csv"
gem "mutex_m"
gem "logger"
gem "base64"
gem "bigdecimal"
gem "observer"
gem "ostruct"'

new_gemfile=$(echo "$new_gemfile" | awk -v gems="$ruby34_gems" '
    /^source/ && !done { print; print gems; done=1; next }
    { print }
')

echo "New Gemfile:"
echo "$new_gemfile"
echo ""

# Get SHA
log_info "Getting file SHA..."
file_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$REPO/contents/Gemfile?ref=$BRANCH")
sha=$(echo "$file_info" | jq -r '.sha')

if [[ -z "$sha" || "$sha" == "null" ]]; then
    log_error "Could not get file SHA"
    exit 1
fi

log_info "SHA: $sha"

# Update file
log_info "Updating Gemfile..."
encoded=$(echo -n "$new_gemfile" | base64 -w 0)

result=$(curl -s -X PUT \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    -d "{\"message\":\"fix: Clean up Ruby 3.4 stdlib gems - add observer and ostruct, remove duplicates\",\"content\":\"$encoded\",\"sha\":\"$sha\",\"branch\":\"$BRANCH\"}" \
    "https://api.github.com/repos/$REPO/contents/Gemfile")

if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
    log_success "Updated Gemfile in $REPO"
else
    log_error "Failed to update Gemfile: $(echo "$result" | jq -r '.message')"
    exit 1
fi

# Delete Gemfile.lock to force fresh bundle
log_info "Checking for Gemfile.lock..."
lock_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$REPO/contents/Gemfile.lock?ref=$BRANCH")
lock_sha=$(echo "$lock_info" | jq -r '.sha // empty')

if [[ -n "$lock_sha" && "$lock_sha" != "null" ]]; then
    log_info "Deleting Gemfile.lock..."
    curl -s -X DELETE \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"message\":\"fix: Remove Gemfile.lock to force fresh bundle\",\"sha\":\"$lock_sha\",\"branch\":\"$BRANCH\"}" \
        "https://api.github.com/repos/$REPO/contents/Gemfile.lock" > /dev/null
    log_success "Deleted Gemfile.lock"
fi

# Trigger workflow
log_info "Triggering workflow..."
workflows=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$REPO/actions/workflows")
workflow_file=$(echo "$workflows" | jq -r '.workflows[] | select(.name | test("jekyll|build|deploy"; "i")) | .path' | head -1 | xargs basename)

if [[ -n "$workflow_file" && "$workflow_file" != "null" ]]; then
    curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"ref\":\"$BRANCH\"}" \
        "https://api.github.com/repos/$REPO/actions/workflows/$workflow_file/dispatches"
    log_success "Workflow triggered: $workflow_file"
else
    log_error "No workflow found to trigger"
fi

echo ""
log_info "Done! Wait for workflow to complete, then check results."
