#!/bin/bash
#
# Migration Runner with Branch Support
# Creates dedicated branches in each repo and runs migrations
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GITHUB_TOKEN="${1:-}"
BRANCH_PREFIX="migration/standardize-jekyll"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="${SCRIPT_DIR}/results/migration_run_${TIMESTAMP}.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Usage: $0 <github_token>"
    exit 1
fi

mkdir -p "${SCRIPT_DIR}/results"

# All Jekyll sites
JEKYLL_SITES=(
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

# Sites needing Ruby 3.4 gems
SITES_NEED_RUBY34=(
    "BrightSoftwares/foolywise.com"
    "BrightSoftwares/ieatmyhealth.com"
    "BrightSoftwares/keke.li"
    "BrightSoftwares/olympics-paris2024.com"
    "BrightSoftwares/eagles-techs.com"
    "Causting/causting.com"
    "Causting/space-up-planet.com"
    "sergioafanou/blog"
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

get_default_branch() {
    local repo="$1"
    github_api "/repos/$repo" | jq -r '.default_branch'
}

create_branch() {
    local repo="$1"
    local new_branch="$2"
    local base_branch="$3"

    log_info "Creating branch $new_branch from $base_branch in $repo"

    # Get SHA of base branch
    local sha=$(github_api "/repos/$repo/git/ref/heads/$base_branch" | jq -r '.object.sha')

    if [[ -z "$sha" || "$sha" == "null" ]]; then
        log_error "Could not get SHA for $base_branch in $repo"
        return 1
    fi

    # Create new branch
    local data=$(jq -n --arg ref "refs/heads/$new_branch" --arg sha "$sha" '{ref: $ref, sha: $sha}')
    local result=$(github_api "/repos/$repo/git/refs" "POST" "$data")

    if echo "$result" | jq -e '.ref' > /dev/null 2>&1; then
        log_success "Created branch $new_branch in $repo"
        return 0
    else
        local msg=$(echo "$result" | jq -r '.message // "Unknown error"')
        if [[ "$msg" == *"Reference already exists"* ]]; then
            log_warning "Branch $new_branch already exists in $repo"
            return 0
        fi
        log_error "Failed to create branch: $msg"
        return 1
    fi
}

get_file_content() {
    local repo="$1"
    local path="$2"
    local branch="$3"

    curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://raw.githubusercontent.com/$repo/$branch/$path" 2>/dev/null
}

update_file() {
    local repo="$1"
    local path="$2"
    local content="$3"
    local message="$4"
    local branch="$5"

    # Get current file SHA
    local file_info=$(github_api "/repos/$repo/contents/$path?ref=$branch")
    local sha=$(echo "$file_info" | jq -r '.sha // empty')

    # Base64 encode content
    local encoded_content=$(echo -n "$content" | base64 -w 0)

    local data
    if [[ -n "$sha" ]]; then
        data=$(jq -n \
            --arg message "$message" \
            --arg content "$encoded_content" \
            --arg sha "$sha" \
            --arg branch "$branch" \
            '{message: $message, content: $content, sha: $sha, branch: $branch}')
    else
        data=$(jq -n \
            --arg message "$message" \
            --arg content "$encoded_content" \
            --arg branch "$branch" \
            '{message: $message, content: $content, branch: $branch}')
    fi

    local result=$(github_api "/repos/$repo/contents/$path" "PUT" "$data")

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        return 0
    else
        log_error "Failed to update $path: $(echo "$result" | jq -r '.message // "Unknown"')"
        return 1
    fi
}

add_ruby34_gems() {
    local repo="$1"
    local branch="$2"

    local gemfile=$(get_file_content "$repo" "Gemfile" "$branch")

    if [[ -z "$gemfile" || "$gemfile" == "404: Not Found" ]]; then
        log_error "Could not fetch Gemfile from $repo"
        return 1
    fi

    # Check if already has the gems
    if echo "$gemfile" | grep -q 'gem "csv"'; then
        log_info "Ruby 3.4 gems already present in $repo"
        return 0
    fi

    # Add Ruby 3.4 gems
    local ruby34_gems='
# Required for Ruby 3.4+ (no longer bundled in stdlib)
gem "csv"
gem "logger"
gem "base64"
gem "bigdecimal"
gem "observer"
gem "ostruct"
'
    # Insert after first source line
    local new_gemfile=$(echo "$gemfile" | awk -v gems="$ruby34_gems" '
        /^source/ && !done { print; print gems; done=1; next }
        { print }
    ')

    update_file "$repo" "Gemfile" "$new_gemfile" "Add Ruby 3.4 compatibility gems" "$branch"
}

trigger_workflow() {
    local repo="$1"
    local branch="$2"

    log_info "Triggering workflow in $repo on branch $branch"

    # Find Jekyll workflow
    local workflows=$(github_api "/repos/$repo/actions/workflows")
    local workflow_id=$(echo "$workflows" | jq -r '.workflows[] | select(.name | test("jekyll|build|deploy"; "i")) | .id' | head -1)

    if [[ -z "$workflow_id" || "$workflow_id" == "null" ]]; then
        log_warning "No Jekyll workflow found in $repo"
        return 1
    fi

    local data=$(jq -n --arg ref "$branch" '{ref: $ref}')
    github_api "/repos/$repo/actions/workflows/$workflow_id/dispatches" "POST" "$data"
    log_success "Workflow triggered in $repo"
}

get_latest_run() {
    local repo="$1"
    local branch="$2"

    github_api "/repos/$repo/actions/runs?branch=$branch&per_page=1" | jq '.workflow_runs[0]'
}

# Initialize results
echo '{"timestamp": "'$TIMESTAMP'", "results": []}' > "$RESULTS_FILE"

log_info "=========================================="
log_info "Starting Jekyll Migration with Branches"
log_info "=========================================="

for repo in "${JEKYLL_SITES[@]}"; do
    log_info ""
    log_info "=========================================="
    log_info "Processing: $repo"
    log_info "=========================================="

    result="{\"repo\": \"$repo\", \"status\": \"pending\"}"

    # Get default branch
    default_branch=$(get_default_branch "$repo")
    if [[ -z "$default_branch" || "$default_branch" == "null" ]]; then
        log_error "Could not determine default branch for $repo"
        result="{\"repo\": \"$repo\", \"status\": \"error\", \"error\": \"Could not determine default branch\"}"
        jq --argjson r "$result" '.results += [$r]' "$RESULTS_FILE" > tmp.json && mv tmp.json "$RESULTS_FILE"
        continue
    fi

    log_info "Default branch: $default_branch"

    # Create migration branch
    migration_branch="${BRANCH_PREFIX}-${TIMESTAMP}"
    if ! create_branch "$repo" "$migration_branch" "$default_branch"; then
        result="{\"repo\": \"$repo\", \"status\": \"error\", \"error\": \"Failed to create branch\"}"
        jq --argjson r "$result" '.results += [$r]' "$RESULTS_FILE" > tmp.json && mv tmp.json "$RESULTS_FILE"
        continue
    fi

    # Check if needs Ruby 3.4 gems
    needs_ruby34=false
    for site in "${SITES_NEED_RUBY34[@]}"; do
        if [[ "$site" == "$repo" ]]; then
            needs_ruby34=true
            break
        fi
    done

    changes_made=false

    if [[ "$needs_ruby34" == "true" ]]; then
        log_info "Adding Ruby 3.4 compatibility gems..."
        if add_ruby34_gems "$repo" "$migration_branch"; then
            changes_made=true
            log_success "Added Ruby 3.4 gems"
        fi
    else
        log_info "Ruby 3.4 gems not needed for this site"
    fi

    # Trigger workflow
    sleep 2
    if trigger_workflow "$repo" "$migration_branch"; then
        log_success "Workflow triggered"
    fi

    result="{\"repo\": \"$repo\", \"status\": \"migrated\", \"branch\": \"$migration_branch\", \"changes_made\": $changes_made}"
    jq --argjson r "$result" '.results += [$r]' "$RESULTS_FILE" > tmp.json && mv tmp.json "$RESULTS_FILE"

    # Small delay to avoid rate limiting
    sleep 3
done

log_info ""
log_info "=========================================="
log_info "Migration Complete - Waiting for Workflows"
log_info "=========================================="

# Wait for workflows to start
log_info "Waiting 60 seconds for workflows to initialize..."
sleep 60

# Collect results
log_info "Collecting workflow results..."

final_results='{"timestamp": "'$TIMESTAMP'", "summary": {"total": 0, "success": 0, "failed": 0, "pending": 0}, "details": []}'

for repo in "${JEKYLL_SITES[@]}"; do
    migration_branch="${BRANCH_PREFIX}-${TIMESTAMP}"

    log_info "Checking $repo..."

    run_info=$(get_latest_run "$repo" "$migration_branch")
    status=$(echo "$run_info" | jq -r '.status // "unknown"')
    conclusion=$(echo "$run_info" | jq -r '.conclusion // "pending"')
    html_url=$(echo "$run_info" | jq -r '.html_url // ""')

    detail="{\"repo\": \"$repo\", \"branch\": \"$migration_branch\", \"status\": \"$status\", \"conclusion\": \"$conclusion\", \"url\": \"$html_url\"}"

    final_results=$(echo "$final_results" | jq --argjson d "$detail" '.details += [$d]')

    # Update summary
    if [[ "$conclusion" == "success" ]]; then
        final_results=$(echo "$final_results" | jq '.summary.success += 1')
    elif [[ "$conclusion" == "failure" ]]; then
        final_results=$(echo "$final_results" | jq '.summary.failed += 1')
    else
        final_results=$(echo "$final_results" | jq '.summary.pending += 1')
    fi
    final_results=$(echo "$final_results" | jq '.summary.total += 1')
done

# Save final results
echo "$final_results" | jq '.' > "${SCRIPT_DIR}/results/final_results_${TIMESTAMP}.json"

log_info ""
log_info "=========================================="
log_info "RESULTS SUMMARY"
log_info "=========================================="

echo "$final_results" | jq -r '
    "Total: \(.summary.total)",
    "Success: \(.summary.success)",
    "Failed: \(.summary.failed)",
    "Pending: \(.summary.pending)",
    "",
    "Details:",
    (.details[] | "  \(.repo): \(.conclusion) (\(.status))")
'

echo ""
log_info "Full results saved to: ${SCRIPT_DIR}/results/final_results_${TIMESTAMP}.json"

# Output failed repos for auto-fix
failed_repos=$(echo "$final_results" | jq -r '.details[] | select(.conclusion == "failure") | .repo')
if [[ -n "$failed_repos" ]]; then
    log_warning ""
    log_warning "Failed repos that need auto-fix:"
    echo "$failed_repos"
fi
