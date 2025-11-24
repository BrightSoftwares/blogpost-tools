#!/bin/bash
GITHUB_TOKEN="$1"

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
echo "WORKFLOW STATUS"
echo "=========================================="

success=0
failed=0
pending=0

for repo in $repos; do
    result=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/actions/runs?per_page=1")

    status=$(echo "$result" | jq -r '.workflow_runs[0].status // "no_run"')
    conclusion=$(echo "$result" | jq -r '.workflow_runs[0].conclusion // "pending"')

    if [ "$status" = "in_progress" ] || [ "$status" = "queued" ]; then
        echo "RUNNING  $repo"
        pending=$((pending + 1))
    elif [ "$conclusion" = "success" ]; then
        echo "SUCCESS  $repo"
        success=$((success + 1))
    elif [ "$conclusion" = "failure" ]; then
        echo "FAILED   $repo"
        failed=$((failed + 1))
    else
        echo "PENDING  $repo ($status/$conclusion)"
        pending=$((pending + 1))
    fi
done

echo ""
echo "=========================================="
echo "Summary: Success=$success, Failed=$failed, Pending=$pending"
echo "=========================================="
