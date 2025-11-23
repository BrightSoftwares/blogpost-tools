#!/bin/bash
#
# Fix remaining issues in all repos
#

GITHUB_TOKEN="$1"
BRANCH="migration/standardize-jekyll-20251123_182523"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Usage: $0 <github_token>"
    exit 1
fi

log_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }

# All repos that need fixes
ALL_REPOS=(
    "BrightSoftwares/ieatmyhealth.com"
    "BrightSoftwares/keke.li"
    "BrightSoftwares/eagles-techs.com"
    "BrightSoftwares/olympics-paris2024.com"
    "Causting/space-up-planet.com"
    "sergioafanou/smart-cv"
)

update_gemfile() {
    local repo="$1"
    log_info "Updating Gemfile in $repo"

    # Get current Gemfile
    local gemfile=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://raw.githubusercontent.com/$repo/$BRANCH/Gemfile")

    if [[ -z "$gemfile" || "$gemfile" == "404: Not Found" ]]; then
        log_error "Could not fetch Gemfile from $repo"
        return 1
    fi

    local new_gemfile="$gemfile"

    # 1. Ensure mutex_m gem is present
    if ! echo "$new_gemfile" | grep -q 'gem.*mutex_m'; then
        log_info "  Adding mutex_m gem"
        new_gemfile=$(echo "$new_gemfile" | sed '/gem "ostruct"/a gem "mutex_m"')
    fi

    # 2. Update jekyll-last-modified-at to 1.3.2
    if echo "$new_gemfile" | grep -q "jekyll-last-modified-at"; then
        if ! echo "$new_gemfile" | grep -q "jekyll-last-modified-at.*1.3"; then
            log_info "  Updating jekyll-last-modified-at to 1.3.2"
            new_gemfile=$(echo "$new_gemfile" | sed "s/gem 'jekyll-last-modified-at'.*/gem 'jekyll-last-modified-at', '~> 1.3.2'/g")
            new_gemfile=$(echo "$new_gemfile" | sed 's/gem "jekyll-last-modified-at".*/gem "jekyll-last-modified-at", "~> 1.3.2"/g')
        fi
    fi

    # 3. Remove Gemfile.lock cache issues by ensuring certain gems are updated
    # (The issue might be cached Gemfile.lock)

    if [[ "$gemfile" == "$new_gemfile" ]]; then
        log_info "  No Gemfile changes needed"
        return 0
    fi

    # Get SHA
    local file_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/Gemfile?ref=$BRANCH")
    local sha=$(echo "$file_info" | jq -r '.sha')

    # Update
    local encoded=$(echo -n "$new_gemfile" | base64 -w 0)

    local result=$(curl -s -X PUT \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"message\":\"fix: Add mutex_m and update jekyll-last-modified-at for Ruby 3.4\",\"content\":\"$encoded\",\"sha\":\"$sha\",\"branch\":\"$BRANCH\"}" \
        "https://api.github.com/repos/$repo/contents/Gemfile")

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        log_success "  Updated Gemfile in $repo"
        return 0
    else
        log_error "  Failed to update Gemfile: $(echo "$result" | jq -r '.message')"
        return 1
    fi
}

delete_gemfile_lock() {
    local repo="$1"
    log_info "Checking Gemfile.lock in $repo"

    # Check if Gemfile.lock exists
    local file_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/Gemfile.lock?ref=$BRANCH")
    local sha=$(echo "$file_info" | jq -r '.sha // empty')

    if [[ -n "$sha" && "$sha" != "null" ]]; then
        log_info "  Deleting Gemfile.lock to force fresh bundle install"

        local result=$(curl -s -X DELETE \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            -d "{\"message\":\"fix: Remove Gemfile.lock to force fresh bundle\",\"sha\":\"$sha\",\"branch\":\"$BRANCH\"}" \
            "https://api.github.com/repos/$repo/contents/Gemfile.lock")

        if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
            log_success "  Deleted Gemfile.lock in $repo"
        else
            log_error "  Failed to delete Gemfile.lock"
        fi
    else
        log_info "  No Gemfile.lock found"
    fi
}

trigger_workflow() {
    local repo="$1"

    local workflows=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/actions/workflows")
    local workflow_name=$(echo "$workflows" | jq -r '.workflows[] | select(.name | test("jekyll|github.pages|build"; "i")) | .path' | head -1 | xargs basename)

    if [[ -z "$workflow_name" || "$workflow_name" == "null" ]]; then
        log_info "No workflow found for $repo"
        return 1
    fi

    log_info "Triggering $workflow_name in $repo"
    curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"ref\":\"$BRANCH\"}" \
        "https://api.github.com/repos/$repo/actions/workflows/$workflow_name/dispatches"
}

echo "=========================================="
echo "Fixing Remaining Issues"
echo "=========================================="
echo ""

for repo in "${ALL_REPOS[@]}"; do
    echo "Processing: $repo"
    update_gemfile "$repo"
    delete_gemfile_lock "$repo"
    echo ""
    sleep 2
done

echo ""
echo "=========================================="
echo "Triggering Workflows"
echo "=========================================="
echo ""

for repo in "${ALL_REPOS[@]}"; do
    trigger_workflow "$repo"
    sleep 1
done

echo ""
echo "Done! Wait for workflows to complete."
