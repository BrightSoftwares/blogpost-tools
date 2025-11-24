#!/bin/bash
#
# Upgrade all Jekyll repos to Jekyll 4.3.4
#

GITHUB_TOKEN="$1"
NEW_JEKYLL_VERSION="4.3.4"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Usage: $0 <github_token>"
    exit 1
fi

log_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }

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
    "sergioafanou/blog"
)

echo "=========================================="
echo "Upgrading Jekyll to $NEW_JEKYLL_VERSION"
echo "=========================================="
echo ""

for repo in "${ALL_REPOS[@]}"; do
    log_info "Processing: $repo"

    # Get default branch
    default_branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo" | jq -r '.default_branch')

    if [[ -z "$default_branch" || "$default_branch" == "null" ]]; then
        log_error "Could not get default branch"
        echo ""
        continue
    fi

    log_info "Branch: $default_branch"

    # Get Gemfile
    gemfile_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/Gemfile?ref=$default_branch")

    sha=$(echo "$gemfile_info" | jq -r '.sha')
    content=$(echo "$gemfile_info" | jq -r '.content' | base64 -d 2>/dev/null)

    if [[ -z "$content" ]]; then
        log_error "Could not get Gemfile content"
        echo ""
        continue
    fi

    # Check current version
    current_version=$(echo "$content" | grep -oP 'gem "jekyll".*?"~>\s*\K[0-9.]+' || \
                     echo "$content" | grep -oP "gem 'jekyll'.*?'~>\s*\K[0-9.]+" || echo "unknown")
    log_info "Current Jekyll version: $current_version"

    if [[ "$current_version" == "$NEW_JEKYLL_VERSION" ]]; then
        log_info "Already at $NEW_JEKYLL_VERSION"
        echo ""
        continue
    fi

    # Update Jekyll version in Gemfile
    # Handle both single and double quote formats
    new_content=$(echo "$content" | sed -E "s/gem ['\"]jekyll['\"],\s*['\"]~>\s*[0-9.]+['\"]/gem \"jekyll\", \"~> $NEW_JEKYLL_VERSION\"/g")

    # Encode and update
    encoded=$(echo -n "$new_content" | base64 -w 0)

    result=$(curl -s -X PUT \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"message\":\"Upgrade Jekyll to $NEW_JEKYLL_VERSION\",\"content\":\"$encoded\",\"sha\":\"$sha\",\"branch\":\"$default_branch\"}" \
        "https://api.github.com/repos/$repo/contents/Gemfile")

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        log_success "Updated Gemfile to Jekyll $NEW_JEKYLL_VERSION"

        # Delete Gemfile.lock to force fresh bundle
        lock_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$repo/contents/Gemfile.lock?ref=$default_branch")
        lock_sha=$(echo "$lock_info" | jq -r '.sha // empty')

        if [[ -n "$lock_sha" && "$lock_sha" != "null" ]]; then
            curl -s -X DELETE \
                -H "Authorization: token $GITHUB_TOKEN" \
                -d "{\"message\":\"Remove Gemfile.lock for Jekyll upgrade\",\"sha\":\"$lock_sha\",\"branch\":\"$default_branch\"}" \
                "https://api.github.com/repos/$repo/contents/Gemfile.lock" > /dev/null
            log_info "Deleted Gemfile.lock"
        fi

        # Trigger workflow
        workflows=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$repo/actions/workflows")
        workflow_file=$(echo "$workflows" | jq -r '.workflows[] | select(.name | test("jekyll|build|deploy|pages"; "i")) | .path' | head -1 | xargs basename 2>/dev/null)

        if [[ -n "$workflow_file" && "$workflow_file" != "null" ]]; then
            curl -s -X POST \
                -H "Authorization: token $GITHUB_TOKEN" \
                -d "{\"ref\":\"$default_branch\"}" \
                "https://api.github.com/repos/$repo/actions/workflows/$workflow_file/dispatches" > /dev/null
            log_success "Triggered workflow: $workflow_file"
        fi
    else
        log_error "Failed: $(echo "$result" | jq -r '.message')"
    fi

    echo ""
    sleep 1
done

echo "=========================================="
echo "Upgrade complete! Run check-results.sh to verify."
echo "=========================================="
