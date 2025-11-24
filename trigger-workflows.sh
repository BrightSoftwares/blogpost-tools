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

echo "=== Re-triggering workflows ==="

for repo in $repos; do
    default_branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo" | jq -r '.default_branch')

    workflows_dir=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/.github/workflows?ref=$default_branch")

    workflow_file=$(echo "$workflows_dir" | jq -r '.[] | select(.name | test("jekyll|github-pages"; "i")) | .name' | head -1)

    if [ -n "$workflow_file" ] && [ "$workflow_file" != "null" ]; then
        result=$(curl -s -w "%{http_code}" -o /dev/null -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -d "{\"ref\":\"$default_branch\"}" \
            "https://api.github.com/repos/$repo/actions/workflows/$workflow_file/dispatches")

        if [ "$result" = "204" ]; then
            echo "OK $repo: Triggered ($workflow_file)"
        else
            echo "FAIL $repo: HTTP $result"
        fi
    else
        echo "SKIP $repo: No workflow found"
    fi

    sleep 0.5
done

echo ""
echo "Done triggering workflows."
