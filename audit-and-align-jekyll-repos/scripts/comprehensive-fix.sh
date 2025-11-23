#!/bin/bash
#
# Comprehensive Jekyll Fix Script
# Fixes all identified issues across all repos
#

set -e

GITHUB_TOKEN="$1"
BRANCH="migration/standardize-jekyll-20251123_182523"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Usage: $0 <github_token>"
    exit 1
fi

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

# All repos
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

# Repos with posix-spawn issue (need jekyll-last-modified-at update)
POSIX_SPAWN_REPOS=(
    "BrightSoftwares/ieatmyhealth.com"
    "BrightSoftwares/eagles-techs.com"
    "BrightSoftwares/olympics-paris2024.com"
    "Causting/space-up-planet.com"
)

# Repos needing mutex_m gem
MUTEX_M_REPOS=(
    "sergioafanou/smart-cv"
)

# Repos needing actions/cache update
CACHE_UPDATE_REPOS=(
    "BrightSoftwares/keke.li"
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

    # Get file SHA
    local file_info=$(github_api "/repos/$repo/contents/$path?ref=$branch")
    local sha=$(echo "$file_info" | jq -r '.sha // empty')

    local encoded=$(echo -n "$content" | base64 -w 0)

    local data
    if [[ -n "$sha" ]]; then
        data=$(jq -n \
            --arg message "$message" \
            --arg content "$encoded" \
            --arg sha "$sha" \
            --arg branch "$branch" \
            '{message: $message, content: $content, sha: $sha, branch: $branch}')
    else
        data=$(jq -n \
            --arg message "$message" \
            --arg content "$encoded" \
            --arg branch "$branch" \
            '{message: $message, content: $content, branch: $branch}')
    fi

    local result=$(github_api "/repos/$repo/contents/$path" "PUT" "$data")

    if echo "$result" | jq -e '.commit' > /dev/null 2>&1; then
        return 0
    else
        log_error "Failed: $(echo "$result" | jq -r '.message // "Unknown"')"
        return 1
    fi
}

fix_jekyll_last_modified_at() {
    local repo="$1"
    log_info "Fixing jekyll-last-modified-at in $repo"

    local gemfile=$(get_file_content "$repo" "Gemfile" "$BRANCH")

    if [[ -z "$gemfile" || "$gemfile" == "404: Not Found" ]]; then
        log_warning "Could not fetch Gemfile from $repo"
        return 1
    fi

    # Update jekyll-last-modified-at to version 1.3.2
    local new_gemfile=$(echo "$gemfile" | sed "s/gem 'jekyll-last-modified-at'.*/gem 'jekyll-last-modified-at', '~> 1.3.2'/g")
    new_gemfile=$(echo "$new_gemfile" | sed 's/gem "jekyll-last-modified-at".*/gem "jekyll-last-modified-at", "~> 1.3.2"/g')

    if [[ "$gemfile" == "$new_gemfile" ]]; then
        # Try to add version constraint if gem exists without version
        new_gemfile=$(echo "$gemfile" | sed "s/gem 'jekyll-last-modified-at'/gem 'jekyll-last-modified-at', '~> 1.3.2'/g")
        new_gemfile=$(echo "$new_gemfile" | sed 's/gem "jekyll-last-modified-at"/gem "jekyll-last-modified-at", "~> 1.3.2"/g')
    fi

    if [[ "$gemfile" != "$new_gemfile" ]]; then
        if update_file "$repo" "Gemfile" "$new_gemfile" "fix: Update jekyll-last-modified-at to 1.3.2 (fixes posix-spawn issue)" "$BRANCH"; then
            log_success "Updated jekyll-last-modified-at in $repo"
            return 0
        fi
    else
        log_info "No changes needed for jekyll-last-modified-at in $repo"
        return 0
    fi
}

add_mutex_m_gem() {
    local repo="$1"
    log_info "Adding mutex_m gem to $repo"

    local gemfile=$(get_file_content "$repo" "Gemfile" "$BRANCH")

    if [[ -z "$gemfile" || "$gemfile" == "404: Not Found" ]]; then
        log_warning "Could not fetch Gemfile from $repo"
        return 1
    fi

    # Check if mutex_m already exists
    if echo "$gemfile" | grep -q 'gem.*mutex_m'; then
        log_info "mutex_m gem already present in $repo"
        return 0
    fi

    # Add mutex_m after other Ruby 3.4 gems
    local new_gemfile=$(echo "$gemfile" | sed '/gem "ostruct"/a gem "mutex_m"')

    # If ostruct line not found, try adding after csv
    if [[ "$gemfile" == "$new_gemfile" ]]; then
        new_gemfile=$(echo "$gemfile" | sed '/gem "csv"/a gem "mutex_m"')
    fi

    # If still no change, add after source line
    if [[ "$gemfile" == "$new_gemfile" ]]; then
        new_gemfile=$(echo "$gemfile" | sed '/^source/a gem "mutex_m"')
    fi

    if [[ "$gemfile" != "$new_gemfile" ]]; then
        if update_file "$repo" "Gemfile" "$new_gemfile" "fix: Add mutex_m gem for Ruby 3.4 compatibility" "$BRANCH"; then
            log_success "Added mutex_m gem to $repo"
            return 0
        fi
    fi
    return 1
}

fix_actions_cache() {
    local repo="$1"
    log_info "Fixing actions/cache version in $repo"

    # Find workflow files
    local workflows=$(github_api "/repos/$repo/contents/.github/workflows?ref=$BRANCH")
    local workflow_files=$(echo "$workflows" | jq -r '.[].name' 2>/dev/null)

    for wf in $workflow_files; do
        local content=$(get_file_content "$repo" ".github/workflows/$wf" "$BRANCH")

        if [[ -z "$content" || "$content" == "404: Not Found" ]]; then
            continue
        fi

        # Check if has actions/cache@v2
        if echo "$content" | grep -q 'actions/cache@v2'; then
            log_info "  Updating $wf"

            # Replace v2 with v4
            local new_content=$(echo "$content" | sed 's/actions\/cache@v2/actions\/cache@v4/g')

            if [[ "$content" != "$new_content" ]]; then
                if update_file "$repo" ".github/workflows/$wf" "$new_content" "fix: Update actions/cache from v2 to v4" "$BRANCH"; then
                    log_success "  Updated actions/cache in $wf"
                fi
            fi
        fi
    done
}

trigger_workflow() {
    local repo="$1"

    # Find Jekyll workflow
    local workflows=$(github_api "/repos/$repo/actions/workflows")
    local workflow_file=$(echo "$workflows" | jq -r '.workflows[] | select(.name | test("jekyll|github.pages|build"; "i")) | .path' | head -1)

    if [[ -z "$workflow_file" || "$workflow_file" == "null" ]]; then
        log_warning "No Jekyll workflow found in $repo"
        return 1
    fi

    local workflow_name=$(basename "$workflow_file")
    log_info "Triggering $workflow_name in $repo"

    local data=$(jq -n --arg ref "$BRANCH" '{ref: $ref}')
    github_api "/repos/$repo/actions/workflows/$workflow_name/dispatches" "POST" "$data"
    return 0
}

echo "=========================================="
echo "Comprehensive Jekyll Fix Script"
echo "=========================================="
echo ""

# Phase 1: Fix posix-spawn issue (jekyll-last-modified-at)
log_info "Phase 1: Fixing posix-spawn issue (jekyll-last-modified-at to 1.3.2)"
echo ""
for repo in "${POSIX_SPAWN_REPOS[@]}"; do
    fix_jekyll_last_modified_at "$repo"
    sleep 1
done

echo ""

# Phase 2: Add mutex_m gem
log_info "Phase 2: Adding mutex_m gem"
echo ""
for repo in "${MUTEX_M_REPOS[@]}"; do
    add_mutex_m_gem "$repo"
    sleep 1
done

echo ""

# Phase 3: Fix actions/cache
log_info "Phase 3: Fixing actions/cache v2 -> v4"
echo ""
for repo in "${CACHE_UPDATE_REPOS[@]}"; do
    fix_actions_cache "$repo"
    sleep 1
done

echo ""

# Phase 4: Trigger all workflows in parallel
log_info "Phase 4: Triggering all workflows"
echo ""

triggered_repos=()
for repo in "${ALL_REPOS[@]}"; do
    if trigger_workflow "$repo"; then
        triggered_repos+=("$repo")
    fi
    sleep 1
done

echo ""
log_success "=========================================="
log_success "Fixes Applied - ${#triggered_repos[@]} workflows triggered"
log_success "=========================================="
echo ""
echo "Triggered repos:"
for repo in "${triggered_repos[@]}"; do
    echo "  - $repo"
done
