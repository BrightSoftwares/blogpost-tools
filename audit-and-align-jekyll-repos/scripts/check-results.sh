#!/bin/bash
GITHUB_TOKEN="$1"
BRANCH="migration/standardize-jekyll-20251123_182523"

echo "=========================================="
echo "WORKFLOW RESULTS"
echo "=========================================="

repos=(
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

success=0
failed=0
pending=0

for repo in "${repos[@]}"; do
    result=$(curl -s -H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github.v3+json" "https://api.github.com/repos/$repo/actions/runs?branch=$BRANCH&per_page=1")
    status=$(echo "$result" | jq -r '.workflow_runs[0].status // "no_run"')
    conclusion=$(echo "$result" | jq -r '.workflow_runs[0].conclusion // "pending"')

    if [[ "$conclusion" == "success" ]]; then
        echo -e "\033[32m✓\033[0m $repo: SUCCESS"
        ((success++))
    elif [[ "$conclusion" == "failure" ]]; then
        echo -e "\033[31m✗\033[0m $repo: FAILED"
        ((failed++))
    else
        echo -e "\033[33m○\033[0m $repo: $conclusion ($status)"
        ((pending++))
    fi
done

echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Success: $success"
echo "Failed: $failed"
echo "Pending: $pending"
