#!/bin/bash
#
# Fix self-hosted runner issues by updating to ubuntu-latest
#
GITHUB_TOKEN="$1"
BRANCH="migration/standardize-jekyll-20251123_182523"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Usage: $0 <github_token>"
    exit 1
fi

# Repos that need runner fix
FAILED_REPOS=(
    "BrightSoftwares/ieatmyhealth.com"
    "BrightSoftwares/eagles-techs.com"
    "BrightSoftwares/olympics-paris2024.com"
    "Causting/space-up-planet.com"
    "sergioafanou/smart-cv"
)

github_api() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="${3:-}"

    if [[ -n "$data" ]]; then
        curl -s -X "$method" \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "https://api.github.com$endpoint"
    else
        curl -s -X "$method" \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com$endpoint"
    fi
}

get_workflow_file() {
    local repo="$1"
    local branch="$2"

    # Find the Jekyll workflow file
    for wf in "jekyll.yml" "github-pages.yml" "build.yml"; do
        content=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://raw.githubusercontent.com/$repo/$branch/.github/workflows/$wf" 2>/dev/null)
        if [[ "$content" != "404: Not Found" && -n "$content" ]]; then
            echo "$wf"
            return 0
        fi
    done
    echo ""
}

update_workflow() {
    local repo="$1"
    local workflow_file="$2"
    local branch="$3"

    echo "Updating $repo/.github/workflows/$workflow_file"

    # Get current content
    local current=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://raw.githubusercontent.com/$repo/$branch/.github/workflows/$workflow_file")

    if [[ -z "$current" || "$current" == "404: Not Found" ]]; then
        echo "  ERROR: Could not fetch workflow file"
        return 1
    fi

    # Replace self-hosted with ubuntu-latest
    local updated=$(echo "$current" | sed 's/runs-on: self-hosted/runs-on: ubuntu-latest/g')
    updated=$(echo "$updated" | sed 's/runs-on: \[self-hosted.*\]/runs-on: ubuntu-latest/g')

    if [[ "$current" == "$updated" ]]; then
        echo "  No changes needed (already using ubuntu-latest or different format)"
        return 0
    fi

    # Get file SHA
    local file_info=$(github_api "/repos/$repo/contents/.github/workflows/$workflow_file?ref=$branch")
    local sha=$(echo "$file_info" | jq -r '.sha')

    # Update file
    local encoded=$(echo -n "$updated" | base64 -w 0)
    local data=$(jq -n \
        --arg message "fix: Change from self-hosted to ubuntu-latest runner" \
        --arg content "$encoded" \
        --arg sha "$sha" \
        --arg branch "$branch" \
        '{message: $message, content: $content, sha: $sha, branch: $branch}')

    local result=$(github_api "/repos/$repo/contents/.github/workflows/$workflow_file" "PUT" "$data")

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        echo "  SUCCESS: Updated workflow"
        return 0
    else
        echo "  ERROR: Failed to update - $(echo "$result" | jq -r '.message')"
        return 1
    fi
}

trigger_workflow() {
    local repo="$1"
    local workflow="$2"
    local branch="$3"

    echo "Triggering $workflow in $repo"

    local data=$(jq -n --arg ref "$branch" '{ref: $ref}')
    github_api "/repos/$repo/actions/workflows/$workflow/dispatches" "POST" "$data"
}

echo "=========================================="
echo "Applying Runner Fixes"
echo "=========================================="

for repo in "${FAILED_REPOS[@]}"; do
    echo ""
    echo "Processing: $repo"

    workflow_file=$(get_workflow_file "$repo" "$BRANCH")

    if [[ -z "$workflow_file" ]]; then
        echo "  No workflow file found, skipping"
        continue
    fi

    echo "  Found workflow: $workflow_file"

    if update_workflow "$repo" "$workflow_file" "$BRANCH"; then
        sleep 2
        trigger_workflow "$repo" "$workflow_file" "$BRANCH"
        echo "  Workflow re-triggered"
    fi

    sleep 3
done

echo ""
echo "=========================================="
echo "Fix Applied - Wait for workflows to re-run"
echo "=========================================="
