#!/bin/bash
#
# Jekyll Sites Migration & Alignment Master Script
#
# This script orchestrates the migration of Jekyll sites to use
# standardized configurations from blogpost-tools.
#
# Usage:
#   ./migrate-all.sh [OPTIONS]
#
# Options:
#   --token TOKEN       GitHub token for API access (required)
#   --dry-run           Show what would be done without making changes
#   --phase N           Run only phase N (1-4)
#   --site REPO         Migrate only specific site (e.g., BrightSoftwares/foolywise.com)
#   --skip-tests        Skip workflow execution tests
#   --verbose           Enable verbose output
#   --help              Show this help message

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/results"
LOGS_DIR="${SCRIPT_DIR}/logs"
TEMPLATES_DIR="${SCRIPT_DIR}/templates"

# Default values
DRY_RUN=false
VERBOSE=false
SKIP_TESTS=false
PHASE=""
SINGLE_SITE=""
GITHUB_TOKEN=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# All Jekyll sites to migrate
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

# Sites missing Algolia
SITES_NEED_ALGOLIA=(
    "sergioafanou/blog"
)

# Sites missing _seo and _system folders
SITES_NEED_FOLDERS=(
    "sergioafanou/blog"
)

#######################################
# Utility Functions
#######################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    head -30 "$0" | tail -25
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --token)
                GITHUB_TOKEN="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --phase)
                PHASE="$2"
                shift 2
                ;;
            --site)
                SINGLE_SITE="$2"
                shift 2
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help)
                show_help
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                ;;
        esac
    done

    if [[ -z "$GITHUB_TOKEN" ]]; then
        log_error "GitHub token is required. Use --token TOKEN"
        exit 1
    fi
}

setup_directories() {
    mkdir -p "$RESULTS_DIR" "$LOGS_DIR"

    # Create timestamped results file
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    RESULTS_FILE="${RESULTS_DIR}/migration_results_${TIMESTAMP}.json"
    LOG_FILE="${LOGS_DIR}/migration_${TIMESTAMP}.log"

    # Initialize results JSON
    echo '{"timestamp": "'$TIMESTAMP'", "sites": {}}' > "$RESULTS_FILE"

    log_info "Results will be saved to: $RESULTS_FILE"
    log_info "Logs will be saved to: $LOG_FILE"
}

#######################################
# GitHub API Functions
#######################################

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
    local branch="${3:-main}"

    # Try main first, then master
    local content=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://raw.githubusercontent.com/$repo/$branch/$path" 2>/dev/null)

    if [[ "$content" == "404: Not Found" ]] || [[ -z "$content" ]]; then
        content=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://raw.githubusercontent.com/$repo/master/$path" 2>/dev/null)
    fi

    echo "$content"
}

update_file() {
    local repo="$1"
    local path="$2"
    local content="$3"
    local message="$4"
    local branch="${5:-main}"

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

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would update $repo/$path"
        return 0
    fi

    github_api "/repos/$repo/contents/$path" "PUT" "$data"
}

create_file() {
    local repo="$1"
    local path="$2"
    local content="$3"
    local message="$4"
    local branch="${5:-main}"

    local encoded_content=$(echo -n "$content" | base64 -w 0)

    local data=$(jq -n \
        --arg message "$message" \
        --arg content "$encoded_content" \
        --arg branch "$branch" \
        '{message: $message, content: $content, branch: $branch}')

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would create $repo/$path"
        return 0
    fi

    github_api "/repos/$repo/contents/$path" "PUT" "$data"
}

trigger_workflow() {
    local repo="$1"
    local workflow="$2"
    local branch="${3:-main}"

    local data=$(jq -n --arg ref "$branch" '{ref: $ref}')

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would trigger $workflow in $repo"
        return 0
    fi

    github_api "/repos/$repo/actions/workflows/$workflow/dispatches" "POST" "$data"
}

get_workflow_runs() {
    local repo="$1"
    local workflow="$2"
    local count="${3:-5}"

    github_api "/repos/$repo/actions/workflows/$workflow/runs?per_page=$count"
}

#######################################
# Migration Functions
#######################################

add_ruby34_gems() {
    local repo="$1"
    log_info "Adding Ruby 3.4 gems to $repo"

    local gemfile=$(get_file_content "$repo" "Gemfile")

    if [[ -z "$gemfile" ]]; then
        log_error "Could not fetch Gemfile from $repo"
        return 1
    fi

    # Check if already has the gems
    if echo "$gemfile" | grep -q 'gem "csv"'; then
        log_info "Ruby 3.4 gems already present in $repo"
        return 0
    fi

    # Add Ruby 3.4 gems after source line
    local ruby34_gems='
# Required for Ruby 3.4+ (no longer bundled in stdlib)
gem "csv"
gem "logger"
gem "base64"
gem "bigdecimal"
gem "observer"
gem "ostruct"
'

    local new_gemfile=$(echo "$gemfile" | sed "/^source/a\\
$ruby34_gems")

    update_file "$repo" "Gemfile" "$new_gemfile" "Add Ruby 3.4 compatibility gems"
    log_success "Added Ruby 3.4 gems to $repo"
}

standardize_jekyll_version() {
    local repo="$1"
    log_info "Standardizing Jekyll version in $repo"

    local gemfile=$(get_file_content "$repo" "Gemfile")

    # Update Jekyll version
    local new_gemfile=$(echo "$gemfile" | sed "s/gem 'jekyll', '~> [0-9.]*'/gem 'jekyll', '~> 4.2.2'/g")
    new_gemfile=$(echo "$new_gemfile" | sed 's/gem "jekyll", "~> [0-9.]*"/gem "jekyll", "~> 4.2.2"/g')

    if [[ "$gemfile" != "$new_gemfile" ]]; then
        update_file "$repo" "Gemfile" "$new_gemfile" "Standardize Jekyll version to 4.2.2"
        log_success "Standardized Jekyll version in $repo"
    else
        log_info "Jekyll version already standardized in $repo"
    fi
}

pin_ffi_gem() {
    local repo="$1"
    log_info "Pinning ffi gem in $repo"

    local gemfile=$(get_file_content "$repo" "Gemfile")

    # Check if already pinned
    if echo "$gemfile" | grep -q "gem ['\"]ffi['\"], ['\"]= 1.16.3['\"]"; then
        log_info "ffi gem already pinned in $repo"
        return 0
    fi

    # Check if ffi exists but not pinned
    if echo "$gemfile" | grep -q "gem ['\"]ffi['\"]"; then
        local new_gemfile=$(echo "$gemfile" | sed "s/gem ['\"]ffi['\"].*/gem 'ffi', '= 1.16.3'/g")
        update_file "$repo" "Gemfile" "$new_gemfile" "Pin ffi gem to 1.16.3"
    else
        # Add ffi gem
        local new_gemfile=$(echo "$gemfile" | sed "/gem 'jekyll'/a\\
gem 'ffi', '= 1.16.3'")
        update_file "$repo" "Gemfile" "$new_gemfile" "Add and pin ffi gem to 1.16.3"
    fi

    log_success "Pinned ffi gem in $repo"
}

add_algolia() {
    local repo="$1"
    log_info "Adding Algolia configuration to $repo"

    local gemfile=$(get_file_content "$repo" "Gemfile")
    local config=$(get_file_content "$repo" "_config.yml")

    # Add to Gemfile if not present
    if ! echo "$gemfile" | grep -q "jekyll-algolia"; then
        local new_gemfile=$(echo "$gemfile" | sed "/group :jekyll_plugins do/a\\
  gem 'jekyll-algolia', '~> 1.7.1'")
        update_file "$repo" "Gemfile" "$new_gemfile" "Add jekyll-algolia gem"
    fi

    # Add to config if not present
    if ! echo "$config" | grep -q "algolia:"; then
        local algolia_config='
# Algolia search configuration
algolia:
  application_id: "YOUR_APP_ID"
  index_name: "jekyll_website"
  search_only_api_key: "YOUR_SEARCH_KEY"
'
        local new_config="${config}${algolia_config}"
        update_file "$repo" "_config.yml" "$new_config" "Add Algolia search configuration"
    fi

    log_success "Added Algolia to $repo"
}

create_standard_folders() {
    local repo="$1"
    log_info "Creating standard folders in $repo"

    # Create _seo folder with README
    local seo_readme="# SEO Configuration

This folder contains SEO-related configuration files.

## Structure
- \`internal-linking/\` - Internal linking configuration
- \`keywords/\` - Keyword research files
- \`jekyll-filename-pretifier/\` - Filename standardization config
"
    create_file "$repo" "_seo/README.md" "$seo_readme" "Add _seo folder structure"

    # Create _system folder with README
    local system_readme="# System Configuration

This folder contains automation and system files.

## Structure
- \`candidates/\` - Blog post candidates
- \`suggestions/\` - Keyword suggestions
- \`scheduled/\` - Scheduled posts
"
    create_file "$repo" "_system/README.md" "$system_readme" "Add _system folder structure"

    log_success "Created standard folders in $repo"
}

update_to_reusable_workflow() {
    local repo="$1"
    log_info "Updating to reusable workflow in $repo"

    local workflow_content='name: Jekyll Build and Deploy

on:
  push:
    branches:
      - main
      - master
    paths:
      - "_posts/**"
      - "_drafts/**"
      - "en/_posts/**"
      - "fr/_posts/**"
      - "_config.yml"
      - "Gemfile"
  workflow_dispatch:
  schedule:
    - cron: "0 7 * * *"

jobs:
  build-deploy:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable_jekyll_build_and_deploy.yml@main
    with:
      build_dir: "./build"
      deploy_to_netlify: true
      use_common_includes: true
    secrets:
      github_token: ${{ secrets.GITHUB_TOKEN }}
      submodule_ssh_key: ${{ secrets.SUBMODULE_SSH_PRIVATE_KEY }}
      algolia_api_key: ${{ secrets.ALGOLIA_API_KEY }}
      netlify_auth_token: ${{ secrets.NETLIFY_AUTH_TOKEN }}
      netlify_site_id: ${{ secrets.NETLIFY_SITE_ID }}
'

    update_file "$repo" ".github/workflows/jekyll.yml" "$workflow_content" "Update to reusable Jekyll workflow"
    log_success "Updated to reusable workflow in $repo"
}

#######################################
# Phase Execution Functions
#######################################

run_phase1() {
    log_info "=========================================="
    log_info "PHASE 1: Ruby 3.4 Compatibility"
    log_info "=========================================="

    local sites=("${JEKYLL_SITES[@]}")
    if [[ -n "$SINGLE_SITE" ]]; then
        sites=("$SINGLE_SITE")
    fi

    for repo in "${sites[@]}"; do
        log_info "Processing: $repo"

        # Check if needs Ruby 3.4 gems
        if [[ " ${SITES_NEED_RUBY34[*]} " =~ " ${repo} " ]]; then
            add_ruby34_gems "$repo"
        fi

        standardize_jekyll_version "$repo"
        pin_ffi_gem "$repo"

        echo ""
    done
}

run_phase2() {
    log_info "=========================================="
    log_info "PHASE 2: Standardization"
    log_info "=========================================="

    local sites=("${JEKYLL_SITES[@]}")
    if [[ -n "$SINGLE_SITE" ]]; then
        sites=("$SINGLE_SITE")
    fi

    for repo in "${sites[@]}"; do
        log_info "Processing: $repo"

        # Check if needs folders
        if [[ " ${SITES_NEED_FOLDERS[*]} " =~ " ${repo} " ]]; then
            create_standard_folders "$repo"
        fi

        # Check if needs Algolia
        if [[ " ${SITES_NEED_ALGOLIA[*]} " =~ " ${repo} " ]]; then
            add_algolia "$repo"
        fi

        echo ""
    done
}

run_phase3() {
    log_info "=========================================="
    log_info "PHASE 3: Deploy Reusable Workflow"
    log_info "=========================================="

    local sites=("${JEKYLL_SITES[@]}")
    if [[ -n "$SINGLE_SITE" ]]; then
        sites=("$SINGLE_SITE")
    fi

    for repo in "${sites[@]}"; do
        log_info "Processing: $repo"
        update_to_reusable_workflow "$repo"
        echo ""
    done
}

run_phase4() {
    log_info "=========================================="
    log_info "PHASE 4: Advanced Features"
    log_info "=========================================="

    log_info "Phase 4 requires manual intervention for:"
    log_info "  - i18n standardization"
    log_info "  - E-commerce template deployment"
    log_info "  - Site-specific configurations"
    log_info ""
    log_info "Please refer to jekyll-migration-plan.md for details."
}

#######################################
# Test Functions
#######################################

run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_info "Skipping tests as requested"
        return 0
    fi

    log_info "=========================================="
    log_info "Running Workflow Tests"
    log_info "=========================================="

    local sites=("${JEKYLL_SITES[@]}")
    if [[ -n "$SINGLE_SITE" ]]; then
        sites=("$SINGLE_SITE")
    fi

    for repo in "${sites[@]}"; do
        log_info "Triggering workflow test for: $repo"
        trigger_workflow "$repo" "jekyll.yml"
        sleep 2  # Avoid rate limiting
    done

    log_info "Workflows triggered. Use collect-results.sh to gather results."
}

#######################################
# Main Execution
#######################################

main() {
    parse_args "$@"
    setup_directories

    log_info "=========================================="
    log_info "Jekyll Sites Migration Script"
    log_info "=========================================="
    log_info "Dry Run: $DRY_RUN"
    log_info "Phase: ${PHASE:-all}"
    log_info "Single Site: ${SINGLE_SITE:-none}"
    log_info ""

    if [[ -n "$PHASE" ]]; then
        case $PHASE in
            1) run_phase1 ;;
            2) run_phase2 ;;
            3) run_phase3 ;;
            4) run_phase4 ;;
            *) log_error "Invalid phase: $PHASE" ;;
        esac
    else
        run_phase1
        run_phase2
        run_phase3
        run_phase4
    fi

    run_tests

    log_success "=========================================="
    log_success "Migration Complete!"
    log_success "=========================================="
}

main "$@"
