#!/bin/bash
#
# Check status of WikiLinks deployment workflows
#

GITHUB_TOKEN="$1"
SESSION_ID="${2:-013RT2p6ZWMC68HcLvtApUVV}"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Usage: $0 <github_token> [session_id]"
    exit 1
fi

log_success() { echo -e "\033[32m✓\033[0m $1"; }
log_error() { echo -e "\033[31m✗\033[0m $1"; }
log_warning() { echo -e "\033[33m⏳\033[0m $1"; }

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
echo "WikiLinks Plugin Status Check"
echo "=========================================="
echo "Branch: $BRANCH_NAME"
echo ""

success=0
failed=0
pending=0
no_run=0

for repo in "${ALL_REPOS[@]}"; do
    runs=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$repo/actions/runs?branch=$BRANCH_NAME&per_page=1")

    run_id=$(echo "$runs" | jq -r '.workflow_runs[0].id')
    run_status=$(echo "$runs" | jq -r '.workflow_runs[0].status')
    run_conclusion=$(echo "$runs" | jq -r '.workflow_runs[0].conclusion')

    if [[ "$run_id" == "null" || -z "$run_id" ]]; then
        echo "$repo: No run found"
        ((no_run++))
    elif [[ "$run_status" == "completed" ]]; then
        if [[ "$run_conclusion" == "success" ]]; then
            log_success "$repo"
            ((success++))
        else
            log_error "$repo ($run_conclusion) - https://github.com/$repo/actions/runs/$run_id"
            ((failed++))
        fi
    else
        log_warning "$repo ($run_status) - https://github.com/$repo/actions/runs/$run_id"
        ((pending++))
    fi
done

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "✓ Success: $success"
echo "✗ Failed: $failed"
echo "⏳ Pending: $pending"
echo "❓ No Run: $no_run"
echo ""

if [[ $failed -gt 0 ]]; then
    echo "⚠️  Failed workflows (copy URLs above and paste logs for analysis)"
fi

if [[ $pending -gt 0 ]]; then
    echo "⏳ Some workflows still running. Check again in a few minutes."
fi

if [[ $success -eq 11 && $failed -eq 0 && $pending -eq 0 ]]; then
    echo "🎉 ALL WORKFLOWS PASSED! WikiLinks plugin ready to merge."
fi
