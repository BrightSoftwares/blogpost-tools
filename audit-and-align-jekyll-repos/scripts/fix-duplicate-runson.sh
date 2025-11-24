#!/bin/bash
#
# Fix duplicate runs-on lines in workflow files
# Ensures only one runs-on: ubuntu-latest line exists
#

GITHUB_TOKEN="$1"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Usage: $0 <github_token>"
    exit 1
fi

log_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }

repos="BrightSoftwares/ieatmyhealth.com
BrightSoftwares/modabyflora-corporate
BrightSoftwares/olympics-paris2024.com
BrightSoftwares/eagles-techs.com"

echo "=========================================="
echo "Fixing duplicate runs-on lines"
echo "=========================================="
echo ""

for repo in $repos; do
    log_info "Processing: $repo"

    # Get default branch
    default_branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo" | jq -r '.default_branch')

    # Find workflow file
    workflows=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/.github/workflows?ref=$default_branch")

    workflow_file=$(echo "$workflows" | jq -r '.[] | select(.name | test("jekyll|github-pages"; "i")) | .name' | head -1)

    if [ -z "$workflow_file" ]; then
        log_error "No workflow found"
        echo ""
        continue
    fi

    log_info "Workflow: $workflow_file"

    # Get content
    workflow_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file?ref=$default_branch")

    sha=$(echo "$workflow_info" | jq -r '.sha')
    content=$(echo "$workflow_info" | jq -r '.content' | base64 -d)

    # Check if there are duplicate runs-on lines
    runson_count=$(echo "$content" | grep -c "runs-on:")
    if [ "$runson_count" -le 1 ]; then
        log_info "No duplicates found"
        echo ""
        continue
    fi

    log_info "Found $runson_count runs-on lines, fixing..."

    # Fix: Remove all runs-on lines and add single one after "jobs:" section
    # Strategy: Keep only first uncommented runs-on and remove rest

    # Create temp file for processing
    tmpfile=$(mktemp)
    echo "$content" > "$tmpfile"

    # Remove all runs-on lines (both commented and uncommented)
    new_content=$(grep -v "runs-on:" "$tmpfile")

    # Add back single runs-on: ubuntu-latest after "jekyll:" job line
    new_content=$(echo "$new_content" | sed '/^  jekyll:$/a\    runs-on: ubuntu-latest')

    rm "$tmpfile"

    # Encode and update
    encoded=$(echo -n "$new_content" | base64 -w 0)

    result=$(curl -s -X PUT \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"message\":\"Fix duplicate runs-on lines in workflow\",\"content\":\"$encoded\",\"sha\":\"$sha\",\"branch\":\"$default_branch\"}" \
        "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file")

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        log_success "Fixed workflow in $repo"

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
