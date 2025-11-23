#!/bin/bash
#
# Fix smart-cv - add missing jekyll-paginate gem
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

# Check if jekyll-paginate is already present
if echo "$gemfile" | grep -q "gem 'jekyll-paginate'" || echo "$gemfile" | grep -q 'gem "jekyll-paginate"'; then
    log_info "jekyll-paginate already present"
else
    log_info "Adding jekyll-paginate gem..."
    # Add jekyll-paginate after jekyll-paginate-v2
    gemfile=$(echo "$gemfile" | sed "/jekyll-paginate-v2/a\\  gem 'jekyll-paginate', '~> 1.1.0'")
fi

echo "Updated Gemfile:"
echo "$gemfile"

# Get SHA
log_info "Getting file SHA..."
file_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$REPO/contents/Gemfile?ref=$BRANCH")
sha=$(echo "$file_info" | jq -r '.sha')

if [[ -z "$sha" || "$sha" == "null" ]]; then
    log_error "Could not get file SHA"
    exit 1
fi

# Update file
log_info "Updating Gemfile..."
encoded=$(echo -n "$gemfile" | base64 -w 0)

result=$(curl -s -X PUT \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    -d "{\"message\":\"fix: Add jekyll-paginate gem for compatibility\",\"content\":\"$encoded\",\"sha\":\"$sha\",\"branch\":\"$BRANCH\"}" \
    "https://api.github.com/repos/$REPO/contents/Gemfile")

if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
    log_success "Updated Gemfile in $REPO"
else
    log_error "Failed to update Gemfile: $(echo "$result" | jq -r '.message')"
    exit 1
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
fi

log_info "Done!"
