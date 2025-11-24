#!/bin/bash
#
# Switch all Jekyll repo workflows from self-hosted to ubuntu-latest
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
echo "Switching to ubuntu-latest runners"
echo "=========================================="
echo ""

for repo in "${ALL_REPOS[@]}"; do
    log_info "Processing: $repo"

    # Get default branch
    default_branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo" | jq -r '.default_branch')

    # Find workflow file
    workflows_dir=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/.github/workflows?ref=$default_branch")

    workflow_file=$(echo "$workflows_dir" | jq -r '.[] | select(.name | test("jekyll|github-pages|pages"; "i")) | .name' | head -1)

    if [[ -z "$workflow_file" || "$workflow_file" == "null" ]]; then
        log_error "No Jekyll workflow found"
        echo ""
        continue
    fi

    log_info "Workflow file: $workflow_file"

    # Get workflow content
    workflow_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file?ref=$default_branch")

    sha=$(echo "$workflow_info" | jq -r '.sha')
    content=$(echo "$workflow_info" | jq -r '.content' | base64 -d)

    # Check current runner setting
    if echo "$content" | grep -q "runs-on: ubuntu-latest" && ! echo "$content" | grep -q "# runs-on: ubuntu-latest"; then
        log_info "Already using ubuntu-latest"
        echo ""
        continue
    fi

    # Update: change self-hosted to ubuntu-latest with comment
    # Handle: # runs-on: ubuntu-latest\n    runs-on: self-hosted -> runs-on: ubuntu-latest\n    # runs-on: self-hosted
    new_content=$(echo "$content" | sed 's/# runs-on: ubuntu-latest/runs-on: ubuntu-latest/' | sed 's/runs-on: self-hosted/# runs-on: self-hosted/')

    # Encode and update
    encoded=$(echo -n "$new_content" | base64 -w 0)

    result=$(curl -s -X PUT \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"message\":\"Switch to ubuntu-latest runner (self-hosted commented)\",\"content\":\"$encoded\",\"sha\":\"$sha\",\"branch\":\"$default_branch\"}" \
        "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file")

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        log_success "Updated workflow in $repo"

        # Trigger workflow
        curl -s -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -d "{\"ref\":\"$default_branch\"}" \
            "https://api.github.com/repos/$repo/actions/workflows/$workflow_file/dispatches" > /dev/null
        log_info "Triggered workflow"
    else
        log_error "Failed: $(echo "$result" | jq -r '.message')"
    fi

    echo ""
    sleep 1
done

echo "=========================================="
echo "Done!"
echo "=========================================="
