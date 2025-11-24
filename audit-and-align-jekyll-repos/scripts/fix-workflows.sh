#!/bin/bash
#
# Comprehensive fix for Jekyll workflows:
# 1. Switch from self-hosted to ubuntu-latest
# 2. Fix typo: pre_build_commmands -> pre_build_commands
# 3. Update checkout actions to v4
#

GITHUB_TOKEN="$1"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Usage: $0 <github_token>"
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
echo "Comprehensive Jekyll Workflow Fix"
echo "=========================================="
echo ""
echo "Fixes applied:"
echo "  1. Switch self-hosted -> ubuntu-latest"
echo "  2. Fix typo: pre_build_commmands -> pre_build_commands"
echo "  3. Update checkout@v2 -> checkout@v4"
echo ""

fixed=0
skipped=0
failed=0

for repo in "${ALL_REPOS[@]}"; do
    log_info "Processing: $repo"

    # Get default branch
    default_branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo" | jq -r '.default_branch')

    if [[ -z "$default_branch" || "$default_branch" == "null" ]]; then
        log_error "Could not determine default branch"
        ((failed++))
        echo ""
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
        echo ""
        continue
    fi

    log_info "Workflow file: $workflow_file"

    # Get workflow content
    workflow_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file?ref=$default_branch")

    sha=$(echo "$workflow_info" | jq -r '.sha')
    content=$(echo "$workflow_info" | jq -r '.content' | base64 -d)

    # Track changes
    changes_made=""

    # Store original for comparison
    original_content="$content"

    # Fix 1: Switch to ubuntu-latest
    # Pattern: uncomment ubuntu-latest, comment self-hosted
    if echo "$content" | grep -q "runs-on: self-hosted"; then
        # Uncomment ubuntu-latest lines
        content=$(echo "$content" | sed 's/^[[:space:]]*#[[:space:]]*runs-on: ubuntu-latest/    runs-on: ubuntu-latest/')
        content=$(echo "$content" | sed 's/^[[:space:]]*##[[:space:]]*runs-on: ubuntu-latest/    runs-on: ubuntu-latest/')
        # Comment out self-hosted lines
        content=$(echo "$content" | sed 's/^[[:space:]]*runs-on: self-hosted/    # runs-on: self-hosted/')
        changes_made="${changes_made}runner "
    fi

    # Fix 2: Fix typo pre_build_commmands -> pre_build_commands
    if echo "$content" | grep -q "pre_build_commmands"; then
        content=$(echo "$content" | sed 's/pre_build_commmands/pre_build_commands/g')
        changes_made="${changes_made}typo "
    fi

    # Fix 3: Update checkout@v2 to checkout@v4
    if echo "$content" | grep -q "checkout@v2"; then
        content=$(echo "$content" | sed 's/checkout@v2/checkout@v4/g')
        changes_made="${changes_made}checkout "
    fi

    # Check if any changes were made
    if [[ "$content" == "$original_content" ]]; then
        log_info "No changes needed"
        ((skipped++))
        echo ""
        continue
    fi

    log_info "Changes: $changes_made"

    # Encode and update
    encoded=$(echo -n "$content" | base64 -w 0)

    result=$(curl -s -X PUT \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"message\":\"Fix Jekyll workflow: $changes_made\",\"content\":\"$encoded\",\"sha\":\"$sha\",\"branch\":\"$default_branch\"}" \
        "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file")

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        log_success "Updated workflow in $repo"
        ((fixed++))

        # Trigger workflow
        curl -s -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -d "{\"ref\":\"$default_branch\"}" \
            "https://api.github.com/repos/$repo/actions/workflows/$workflow_file/dispatches" > /dev/null 2>&1
        log_info "Triggered workflow"
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
echo "Fixed: $fixed"
echo "Skipped (no changes needed): $skipped"
echo "Failed: $failed"
echo ""
echo "Run check-results.sh in a few minutes to verify all workflows pass."
