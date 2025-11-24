#!/bin/bash
#
# Test WikiLinks plugin by triggering workflows
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

BRANCH_NAME="claude/add-wikilinks-plugin-${SESSION_ID}"

echo "=========================================="
echo "Test WikiLinks Plugin"
echo "=========================================="
echo ""
echo "Branch: $BRANCH_NAME"
echo "Triggering workflows in parallel..."
echo ""

# Trigger all workflows in parallel
for repo in "${ALL_REPOS[@]}"; do
    (
        default_branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$repo" | jq -r '.default_branch')

        workflow_file=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$repo/contents/.github/workflows?ref=$default_branch" | \
            jq -r '.[] | select(.name | test("jekyll|github-pages|pages"; "i")) | .name' | head -1)

        if [[ -n "$workflow_file" && "$workflow_file" != "null" ]]; then
            curl -s -X POST \
                -H "Authorization: token $GITHUB_TOKEN" \
                -H "Accept: application/vnd.github.v3+json" \
                -d "{\"ref\":\"$BRANCH_NAME\"}" \
                "https://api.github.com/repos/$repo/actions/workflows/$workflow_file/dispatches" > /dev/null 2>&1
            echo "✓ Triggered: $repo"
        else
            echo "✗ No workflow found: $repo"
        fi
    ) &
done

wait

log_success "All workflows triggered!"
echo ""
echo "Waiting 30 seconds for workflows to start..."
sleep 30

echo ""
echo "=========================================="
echo "Workflow Status"
echo "=========================================="
echo ""

for repo in "${ALL_REPOS[@]}"; do
    log_info "Checking: $repo"

    runs=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$repo/actions/runs?branch=$BRANCH_NAME&per_page=1")

    run_id=$(echo "$runs" | jq -r '.workflow_runs[0].id')
    run_status=$(echo "$runs" | jq -r '.workflow_runs[0].status')
    run_conclusion=$(echo "$runs" | jq -r '.workflow_runs[0].conclusion')

    if [[ "$run_id" == "null" || -z "$run_id" ]]; then
        echo "  ⚠️  No run found"
    else
        echo "  Run ID: $run_id"
        echo "  Status: $run_status"
        echo "  Conclusion: $run_conclusion"
        echo "  URL: https://github.com/$repo/actions/runs/$run_id"
    fi

    echo ""
done

echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "Check individual run URLs above for detailed logs"
echo ""
echo "To check status again, run:"
echo "  ./check-wikilinks-status.sh $GITHUB_TOKEN"
echo ""
