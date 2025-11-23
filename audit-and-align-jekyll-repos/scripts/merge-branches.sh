#!/bin/bash
#
# Merge migration branches to default branch for successful repos
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
log_warning() { echo -e "\033[33m[WARNING]\033[0m $1"; }

# Get default branch for a repo
get_default_branch() {
    local repo="$1"
    curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo" | jq -r '.default_branch'
}

# Check if workflow succeeded for a repo
check_workflow_success() {
    local repo="$1"
    local result=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/actions/runs?branch=$BRANCH&per_page=1")
    local conclusion=$(echo "$result" | jq -r '.workflow_runs[0].conclusion // "pending"')
    [[ "$conclusion" == "success" ]]
}

# Merge branch using GitHub API
merge_branch() {
    local repo="$1"
    local base="$2"
    local head="$BRANCH"

    log_info "Merging $head -> $base in $repo"

    local result=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"base\":\"$base\",\"head\":\"$head\",\"commit_message\":\"Merge migration: Ruby 3.4 compatibility and Jekyll standardization\"}" \
        "https://api.github.com/repos/$repo/merges")

    if echo "$result" | jq -e '.sha' > /dev/null 2>&1; then
        log_success "Merged successfully in $repo"
        return 0
    elif echo "$result" | jq -r '.message' | grep -q "nothing to merge"; then
        log_info "Nothing to merge in $repo (already up to date)"
        return 0
    else
        log_error "Failed to merge: $(echo "$result" | jq -r '.message // "Unknown error"')"
        return 1
    fi
}

# Delete migration branch after merge
delete_branch() {
    local repo="$1"

    log_info "Deleting migration branch in $repo"

    local result=$(curl -s -X DELETE \
        -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/git/refs/heads/$BRANCH")

    if [[ -z "$result" ]]; then
        log_success "Deleted branch in $repo"
    else
        log_warning "Could not delete branch: $(echo "$result" | jq -r '.message // "Unknown"')"
    fi
}

# All repos to process
ALL_REPOS=(
    "BrightSoftwares/corporate-website"
    "BrightSoftwares/foolywise.com"
    "BrightSoftwares/ieatmyhealth.com"
    "BrightSoftwares/joyousbyflora-posts"
    "BrightSoftwares/keke.li"
    "BrightSoftwares/modabyflora-corporate"
    "BrightSoftwares/olympics-paris2024.com"
    "BrightSoftwares/eagles-techs.com"
    "Causting/causting.com"
    "Causting/space-up-planet.com"
    "sergioafanou/smart-cv"
)

echo "=========================================="
echo "Merging Migration Branches"
echo "=========================================="
echo ""

merged=0
skipped=0
failed=0

for repo in "${ALL_REPOS[@]}"; do
    echo "Processing: $repo"

    # Check if workflow succeeded
    if ! check_workflow_success "$repo"; then
        log_warning "Skipping $repo - workflow not successful"
        ((skipped++))
        echo ""
        continue
    fi

    # Get default branch
    default_branch=$(get_default_branch "$repo")
    if [[ -z "$default_branch" || "$default_branch" == "null" ]]; then
        log_error "Could not determine default branch for $repo"
        ((failed++))
        echo ""
        continue
    fi

    log_info "Default branch: $default_branch"

    # Merge
    if merge_branch "$repo" "$default_branch"; then
        # Delete migration branch
        delete_branch "$repo"
        ((merged++))
    else
        ((failed++))
    fi

    echo ""
    sleep 1
done

echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Merged: $merged"
echo "Skipped: $skipped"
echo "Failed: $failed"
