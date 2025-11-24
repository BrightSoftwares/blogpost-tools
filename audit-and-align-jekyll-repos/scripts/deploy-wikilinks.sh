#!/bin/bash
#
# Deploy jekyll-wikilinks-v2 plugin to all repositories
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

BRANCH_NAME="claude/add-wikilinks-plugin-${SESSION_ID}"
PLUGIN_FILE="jekyll-plugins/jekyll-wikilinks-v2/_plugins/wikilinks.rb"

# Check if plugin file exists
if [[ ! -f "$PLUGIN_FILE" ]]; then
    log_error "Plugin file not found: $PLUGIN_FILE"
    exit 1
fi

# Read plugin content
PLUGIN_CONTENT=$(cat "$PLUGIN_FILE")

echo "=========================================="
echo "Deploy WikiLinks Plugin"
echo "=========================================="
echo ""
echo "Branch: $BRANCH_NAME"
echo "Plugin: jekyll-wikilinks-v2"
echo "Repos: ${#ALL_REPOS[@]}"
echo ""

success=0
failed=0

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

    # Get latest commit SHA
    latest_sha=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/git/refs/heads/$default_branch" | jq -r '.object.sha')

    if [[ -z "$latest_sha" || "$latest_sha" == "null" ]]; then
        log_error "Could not get latest commit SHA"
        ((failed++))
        continue
    fi

    log_info "Latest SHA: ${latest_sha:0:8}"

    # Create branch
    log_info "Creating branch: $BRANCH_NAME"
    branch_result=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"ref\":\"refs/heads/$BRANCH_NAME\",\"sha\":\"$latest_sha\"}" \
        "https://api.github.com/repos/$repo/git/refs")

    # If branch exists, update it
    if echo "$branch_result" | jq -e '.message' | grep -q "Reference already exists"; then
        log_warning "Branch exists, updating..."
        curl -s -X PATCH \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            -d "{\"sha\":\"$latest_sha\",\"force\":true}" \
            "https://api.github.com/repos/$repo/git/refs/heads/$BRANCH_NAME" > /dev/null
    fi

    log_success "Branch ready"

    # Check if _plugins directory exists
    plugins_check=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/_plugins?ref=$default_branch")

    # Get SHA if file already exists
    existing_file=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/_plugins/wikilinks.rb?ref=$BRANCH_NAME")

    existing_sha=""
    if echo "$existing_file" | jq -e '.sha' > /dev/null 2>&1; then
        existing_sha=$(echo "$existing_file" | jq -r '.sha')
        log_info "File exists, will update (SHA: ${existing_sha:0:8})"
    else
        log_info "File doesn't exist, will create"
    fi

    # Encode plugin content
    encoded_plugin=$(echo -n "$PLUGIN_CONTENT" | base64 -w 0)

    # Create or update the plugin file
    log_info "Deploying wikilinks.rb..."

    if [[ -n "$existing_sha" ]]; then
        # Update existing file
        result=$(curl -s -X PUT \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            -d "{\"message\":\"Add jekyll-wikilinks-v2 plugin\",\"content\":\"$encoded_plugin\",\"sha\":\"$existing_sha\",\"branch\":\"$BRANCH_NAME\"}" \
            "https://api.github.com/repos/$repo/contents/_plugins/wikilinks.rb")
    else
        # Create new file
        result=$(curl -s -X PUT \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            -d "{\"message\":\"Add jekyll-wikilinks-v2 plugin\",\"content\":\"$encoded_plugin\",\"branch\":\"$BRANCH_NAME\"}" \
            "https://api.github.com/repos/$repo/contents/_plugins/wikilinks.rb")
    fi

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        log_success "Plugin deployed to $BRANCH_NAME"
        ((success++))
    else
        log_error "Failed: $(echo "$result" | jq -r '.message')"
        ((failed++))
    fi

    echo ""
    sleep 1
done

echo "=========================================="
echo "DEPLOYMENT SUMMARY"
echo "=========================================="
echo "✅ Successfully deployed: $success"
echo "❌ Failed: $failed"
echo ""
echo "Branch created in all repos: $BRANCH_NAME"
echo ""
echo "Next: Run test-wikilinks.sh to trigger workflows and test"
