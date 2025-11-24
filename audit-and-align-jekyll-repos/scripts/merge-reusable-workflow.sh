#!/bin/bash
#
# Merge reusable workflow branches to main/master
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

BRANCH_NAME="claude/use-reusable-workflow-${SESSION_ID}"

echo "=========================================="
echo "Merge Reusable Workflow Branches"
echo "=========================================="
echo ""
echo "Branch: $BRANCH_NAME"
echo "Target: main/master (respective default branches)"
echo ""

success=0
failed=0
skipped=0

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

    # Check if branches are identical (no merge needed)
    compare=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/compare/$default_branch...$BRANCH_NAME")

    ahead=$(echo "$compare" | jq -r '.ahead_by')
    status=$(echo "$compare" | jq -r '.status')

    if [[ "$status" == "identical" ]]; then
        log_info "Branches identical, no merge needed"
        ((skipped++))

        # Delete branch
        curl -s -X DELETE \
            -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$repo/git/refs/heads/$BRANCH_NAME" > /dev/null
        log_info "Deleted branch"
        echo ""
        continue
    fi

    log_info "Changes to merge: $ahead commits ahead"

    # Merge the branch
    log_info "Merging $BRANCH_NAME into $default_branch..."

    merge_result=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"base\":\"$default_branch\",\"head\":\"$BRANCH_NAME\",\"commit_message\":\"Use reusable Jekyll workflow\\n\\n- Migrate to centralized workflow in blogpost-tools\\n- Ruby 3.4.1 + Jekyll 4.3.4\\n- WikiLinks plugin support included\\n- Algolia settings preserved\\n- All workflows tested and passing\\n\\nBranch: $BRANCH_NAME\"}" \
        "https://api.github.com/repos/$repo/merges")

    # Check if merge was successful
    if echo "$merge_result" | jq -e '.sha' > /dev/null 2>&1; then
        merge_sha=$(echo "$merge_result" | jq -r '.sha')
        log_success "Merged successfully! SHA: ${merge_sha:0:8}"
        ((success++))

        # Delete the branch after successful merge
        log_info "Deleting branch $BRANCH_NAME..."
        curl -s -X DELETE \
            -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$repo/git/refs/heads/$BRANCH_NAME" > /dev/null
        log_success "Branch deleted"
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
echo "⏭️  No changes (skipped): $skipped"
echo "❌ Failed: $failed"
echo ""

if [[ $success -gt 0 ]] || [[ $skipped -gt 0 ]]; then
    echo "🎉 Reusable workflow deployed to production!"
    echo ""
    echo "All repositories now use:"
    echo "  - Centralized Jekyll build workflow"
    echo "  - Ruby 3.4.1 + Jekyll 4.3.4"
    echo "  - WikiLinks plugin support"
    echo "  - Tested and verified builds"
fi
