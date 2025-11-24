#!/bin/bash
#
# Remove jekyll-wikilinks from all repos (incompatible with Jekyll 4.3.4)
#

GITHUB_TOKEN="$1"

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
echo "Removing jekyll-wikilinks (incompatible with Jekyll 4.3.4)"
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

    # Check if jekyll-wikilinks exists
    if ! echo "$content" | grep -q "jekyll-wikilinks"; then
        log_info "No jekyll-wikilinks found"
        echo ""
        continue
    fi

    # Remove jekyll-wikilinks line
    new_content=$(echo "$content" | grep -v "jekyll-wikilinks")

    # Encode and update
    encoded=$(echo -n "$new_content" | base64 -w 0)

    result=$(curl -s -X PUT \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"message\":\"Remove jekyll-wikilinks (incompatible with Jekyll 4.3.4)\",\"content\":\"$encoded\",\"sha\":\"$sha\",\"branch\":\"$default_branch\"}" \
        "https://api.github.com/repos/$repo/contents/Gemfile")

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        log_success "Removed jekyll-wikilinks from Gemfile"

        # Delete Gemfile.lock
        lock_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$repo/contents/Gemfile.lock?ref=$default_branch")
        lock_sha=$(echo "$lock_info" | jq -r '.sha // empty')

        if [[ -n "$lock_sha" && "$lock_sha" != "null" ]]; then
            curl -s -X DELETE \
                -H "Authorization: token $GITHUB_TOKEN" \
                -d "{\"message\":\"Remove Gemfile.lock\",\"sha\":\"$lock_sha\",\"branch\":\"$default_branch\"}" \
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
            log_success "Triggered workflow"
        fi
    else
        log_error "Failed: $(echo "$result" | jq -r '.message')"
    fi

    echo ""
    sleep 1
done

echo "=========================================="
echo "Done!"
echo "=========================================="
