#!/bin/bash
#
# Switch GitHub Actions runners between ubuntu-latest and self-hosted
#

GITHUB_TOKEN="$1"
TARGET_RUNNER="$2"

if [[ -z "$GITHUB_TOKEN" ]] || [[ -z "$TARGET_RUNNER" ]]; then
    echo "Usage: $0 <github_token> <ubuntu-latest|self-hosted>"
    echo ""
    echo "Examples:"
    echo "  $0 \$TOKEN ubuntu-latest   # Switch to ubuntu-latest"
    echo "  $0 \$TOKEN self-hosted     # Switch to self-hosted"
    exit 1
fi

if [[ "$TARGET_RUNNER" != "ubuntu-latest" ]] && [[ "$TARGET_RUNNER" != "self-hosted" ]]; then
    echo "Error: TARGET_RUNNER must be 'ubuntu-latest' or 'self-hosted'"
    exit 1
fi

log_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }
log_warning() { echo -e "\033[33m[WARNING]\033[0m $1"; }

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

echo "=========================================="
echo "Switch GitHub Actions Runners"
echo "=========================================="
echo ""
echo "Target runner: $TARGET_RUNNER"
echo "Repos: ${#ALL_REPOS[@]}"
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

    # Find workflow file
    workflows_dir=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/.github/workflows?ref=$default_branch")

    workflow_file=$(echo "$workflows_dir" | jq -r '.[] | select(.name | test("jekyll|github-pages|pages"; "i")) | .name' | head -1)

    if [[ -z "$workflow_file" || "$workflow_file" == "null" ]]; then
        log_error "No Jekyll workflow found"
        ((failed++))
        continue
    fi

    log_info "Workflow file: $workflow_file"

    # Get workflow content
    workflow_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file?ref=$default_branch")

    sha=$(echo "$workflow_info" | jq -r '.sha')
    content=$(echo "$workflow_info" | jq -r '.content' | base64 -d)

    # Check current runner
    current_runner=$(echo "$content" | grep -oP 'runs-on:\s*\K[^\s#]+' | head -1)

    if [[ "$current_runner" == "$TARGET_RUNNER" ]]; then
        log_info "Already using $TARGET_RUNNER"
        ((skipped++))
        echo ""
        continue
    fi

    log_info "Current runner: $current_runner"
    log_info "Switching to: $TARGET_RUNNER"

    # Perform the switch
    if [[ "$TARGET_RUNNER" == "ubuntu-latest" ]]; then
        # Switch to ubuntu-latest
        updated_content=$(echo "$content" | sed -E 's/runs-on:\s*self-hosted/runs-on: ubuntu-latest/g')
        updated_content=$(echo "$updated_content" | sed -E 's/^(\s*)#\s*runs-on:\s*ubuntu-latest/\1runs-on: ubuntu-latest/g')
    else
        # Switch to self-hosted
        updated_content=$(echo "$content" | sed -E 's/runs-on:\s*ubuntu-latest/runs-on: self-hosted/g')
    fi

    # Check if changes were made
    if [[ "$content" == "$updated_content" ]]; then
        log_warning "No changes needed (pattern not found)"
        ((skipped++))
        echo ""
        continue
    fi

    # Encode and update
    encoded=$(echo -n "$updated_content" | base64 -w 0)

    result=$(curl -s -X PUT \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"message\":\"Switch runner to $TARGET_RUNNER\",\"content\":\"$encoded\",\"sha\":\"$sha\",\"branch\":\"$default_branch\"}" \
        "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file")

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        log_success "Switched to $TARGET_RUNNER"
        ((success++))
    else
        log_error "Failed: $(echo "$result" | jq -r '.message')"
        ((failed++))
    fi

    echo ""
    sleep 1
done

echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "✅ Successfully switched: $success"
echo "⏭️  Already correct: $skipped"
echo "❌ Failed: $failed"
echo ""

if [[ $success -gt 0 ]]; then
    echo "✓ $success repos now using $TARGET_RUNNER"
fi

if [[ $failed -gt 0 ]]; then
    echo "⚠️  $failed repos failed to switch. Review errors above."
fi

echo ""
echo "Recommendation:"
if [[ "$TARGET_RUNNER" == "ubuntu-latest" ]]; then
    echo "  - ubuntu-latest provides faster, consistent builds"
    echo "  - No self-hosted runner maintenance required"
    echo "  - Recommended for most use cases"
else
    echo "  - self-hosted requires active runners to be configured"
    echo "  - Ensure runners are properly set up before triggering workflows"
    echo "  - May provide cost savings for high-volume builds"
fi
echo ""
