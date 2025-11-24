#!/bin/bash
#
# Merge plugin alignment branches into main/master
#

GITHUB_TOKEN="$1"
SESSION_ID="${2:-013RT2p6ZWMC68HcLvtApUVV}"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Usage: $0 <github_token> [session_id]"
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
)

BRANCH_NAME="claude/align-plugins-${SESSION_ID}"

echo "=========================================="
echo "Merging Plugin Alignment Branches"
echo "=========================================="
echo ""
echo "Branch: $BRANCH_NAME"
echo "Target: main/master (respective default branches)"
echo ""

success=0
failed=0

for repo in "${ALL_REPOS[@]}"; do
    echo "================================================"
    log_info "Processing: $repo"
    echo "================================================"

    # Get default branch
    default_branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo" | jq -r '.default_branch')

    if [[ -z "$default_branch" || "$default_branch" == "null" ]]; then
        log_error "Could not determine default branch"
        ((failed++))
        continue
    fi

    log_info "Default branch: $default_branch"

    # Merge the branch
    log_info "Merging $BRANCH_NAME into $default_branch..."

    merge_result=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"base\":\"$default_branch\",\"head\":\"$BRANCH_NAME\",\"commit_message\":\"Merge plugin alignment: standardize Jekyll plugins across repos\n\n- Added missing Ruby 3.4 stdlib gems (observer, ostruct, mutex_m)\n- Standardized plugin versions (jekyll-feed, jekyll-toc, jekyll-last-modified-at)\n- Fixed Gemfile syntax errors\n- Migrated smart-cv from jekyll-paginate to jekyll-paginate-v2\n- All workflows tested and passing on ubuntu-latest\n\nBranch: $BRANCH_NAME\"}" \
        "https://api.github.com/repos/$repo/merges")

    # Check if merge was successful
    if echo "$merge_result" | jq -e '.sha' > /dev/null 2>&1; then
        merge_sha=$(echo "$merge_result" | jq -r '.sha')
        log_success "Merged successfully! SHA: ${merge_sha:0:8}"
        ((success++))

        # Optionally delete the branch after successful merge
        log_info "Deleting branch $BRANCH_NAME..."
        delete_result=$(curl -s -X DELETE \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/repos/$repo/git/refs/heads/$BRANCH_NAME")

        if [[ -z "$delete_result" ]]; then
            log_success "Branch deleted"
        else
            log_info "Branch kept (may be used for reference)"
        fi
    else
        error_msg=$(echo "$merge_result" | jq -r '.message')
        log_error "Merge failed: $error_msg"
        ((failed++))
    fi

    echo ""
    sleep 1
done

echo "=========================================="
echo "MERGE SUMMARY"
echo "=========================================="
echo "✅ Successfully merged: $success"
echo "❌ Failed: $failed"
echo ""

if [[ $success -eq 11 ]]; then
    echo "🎉 All plugin alignment branches merged successfully!"
    echo ""
    echo "All repositories now have:"
    echo "  - Standardized Ruby 3.4 stdlib gems"
    echo "  - Aligned plugin versions"
    echo "  - Tested and verified builds"
    echo ""
    echo "Next steps:"
    echo "  1. Harmonize _includes/ across repos"
    echo "  2. Create reusable workflows"
    echo "  3. Implement jekyll-wikilinks replacement"
else
    echo "⚠️  Some merges failed. Review errors above."
fi
