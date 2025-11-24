#!/bin/bash
#
# Remove jekyll-wikilinks from _config.yml across all repos
# This fixes the build error when the gem is not in Gemfile but still in config
#

GITHUB_TOKEN="$1"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Usage: $0 <github_token>"
    exit 1
fi

log_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }

repos="BrightSoftwares/corporate-website
BrightSoftwares/foolywise.com
BrightSoftwares/ieatmyhealth.com
BrightSoftwares/joyousbyflora-posts
BrightSoftwares/keke.li
BrightSoftwares/modabyflora-corporate
BrightSoftwares/olympics-paris2024.com
BrightSoftwares/eagles-techs.com
Causting/causting.com
Causting/space-up-planet.com
sergioafanou/smart-cv"

echo "=========================================="
echo "Removing jekyll-wikilinks from _config.yml"
echo "=========================================="
echo ""

fixed=0
skipped=0
failed=0

for repo in $repos; do
    log_info "Processing: $repo"

    # Get default branch
    default_branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo" | jq -r '.default_branch')

    # Get _config.yml content
    config_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/_config.yml?ref=$default_branch")

    sha=$(echo "$config_info" | jq -r '.sha')
    content=$(echo "$config_info" | jq -r '.content' | base64 -d 2>/dev/null)

    if [ -z "$content" ]; then
        log_error "Could not read _config.yml"
        failed=$((failed + 1))
        echo ""
        continue
    fi

    # Check if wikilinks is referenced
    if ! echo "$content" | grep -q "jekyll-wikilinks"; then
        log_info "No wikilinks reference found"
        skipped=$((skipped + 1))
        echo ""
        continue
    fi

    # Remove the wikilinks line (handles various formats)
    new_content=$(echo "$content" | grep -v "jekyll-wikilinks")

    # Encode and update
    encoded=$(echo -n "$new_content" | base64 -w 0)

    result=$(curl -s -X PUT \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"message\":\"Remove jekyll-wikilinks from config (incompatible with Jekyll 4.3.4)\",\"content\":\"$encoded\",\"sha\":\"$sha\",\"branch\":\"$default_branch\"}" \
        "https://api.github.com/repos/$repo/contents/_config.yml")

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        log_success "Removed wikilinks from $repo"
        fixed=$((fixed + 1))

        # Trigger workflow
        workflows_dir=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$repo/contents/.github/workflows?ref=$default_branch")
        workflow_file=$(echo "$workflows_dir" | jq -r '.[] | select(.name | test("jekyll|github-pages"; "i")) | .name' | head -1)

        if [ -n "$workflow_file" ] && [ "$workflow_file" != "null" ]; then
            curl -s -X POST \
                -H "Authorization: token $GITHUB_TOKEN" \
                -d "{\"ref\":\"$default_branch\"}" \
                "https://api.github.com/repos/$repo/actions/workflows/$workflow_file/dispatches" > /dev/null
            log_info "Triggered workflow"
        fi
    else
        log_error "Failed: $(echo "$result" | jq -r '.message')"
        failed=$((failed + 1))
    fi

    echo ""
    sleep 1
done

echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Fixed: $fixed"
echo "Skipped (no wikilinks): $skipped"
echo "Failed: $failed"
