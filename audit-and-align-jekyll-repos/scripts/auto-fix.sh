#!/bin/bash
#
# Automated Fix Mechanism for Jekyll Workflow Failures
#
# This script analyzes workflow failures, applies fixes, and re-runs tests
# until all issues are resolved or max iterations reached.
#
# Usage:
#   ./auto-fix.sh --token TOKEN [OPTIONS]
#
# Options:
#   --token TOKEN       GitHub token for API access (required)
#   --max-iterations N  Maximum fix iterations (default: 5)
#   --dry-run           Analyze without applying fixes
#   --site REPO         Fix only specific site

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/../results"
FIXES_DIR="${SCRIPT_DIR}/../fixes"
LOGS_DIR="${SCRIPT_DIR}/../logs"

# Default values
GITHUB_TOKEN=""
MAX_ITERATIONS=5
DRY_RUN=false
SINGLE_SITE=""
ITERATION=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_fix() { echo -e "${CYAN}[FIX]${NC} $1"; }

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --token) GITHUB_TOKEN="$2"; shift 2 ;;
            --max-iterations) MAX_ITERATIONS="$2"; shift 2 ;;
            --dry-run) DRY_RUN=true; shift ;;
            --site) SINGLE_SITE="$2"; shift 2 ;;
            *) log_error "Unknown option: $1"; exit 1 ;;
        esac
    done

    if [[ -z "$GITHUB_TOKEN" ]]; then
        log_error "GitHub token required. Use --token TOKEN"
        exit 1
    fi
}

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

get_workflow_logs() {
    local repo="$1"
    local run_id="$2"
    local log_file="${LOGS_DIR}/${repo//\//_}_${run_id}.log"

    mkdir -p "$LOGS_DIR"

    # Get download URL for logs
    local logs_url=$(github_api "/repos/$repo/actions/runs/$run_id/logs" | head -1)

    # Download logs
    curl -sL \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$repo/actions/runs/$run_id/logs" \
        -o "${log_file}.zip" 2>/dev/null || true

    # Extract if zip exists
    if [[ -f "${log_file}.zip" ]] && file "${log_file}.zip" | grep -q "Zip"; then
        unzip -o "${log_file}.zip" -d "${LOGS_DIR}/${repo//\//_}_${run_id}" 2>/dev/null || true
        echo "${LOGS_DIR}/${repo//\//_}_${run_id}"
    else
        rm -f "${log_file}.zip"
        echo ""
    fi
}

analyze_failure() {
    local repo="$1"
    local run_id="$2"
    local jobs_json="$3"

    local analysis=""
    local fix_type=""

    # Get failed step info
    local failed_steps=$(echo "$jobs_json" | jq -r '
        .jobs[] |
        select(.conclusion == "failure") |
        .steps[] |
        select(.conclusion == "failure") |
        .name
    ')

    # Get job logs for detailed analysis
    local job_logs=$(github_api "/repos/$repo/actions/runs/$run_id/jobs" | jq -r '
        .jobs[] |
        select(.conclusion == "failure") |
        {name: .name, steps: [.steps[] | {name: .name, conclusion: .conclusion}]}
    ')

    # Pattern matching for common errors
    if echo "$failed_steps" | grep -qi "bundle install\|gem"; then
        fix_type="gemfile"
        analysis="Gemfile/bundle issue - likely Ruby 3.4 compatibility or missing gems"
    elif echo "$failed_steps" | grep -qi "jekyll build"; then
        fix_type="jekyll_config"
        analysis="Jekyll build failure - check _config.yml and includes"
    elif echo "$failed_steps" | grep -qi "checkout\|clone"; then
        fix_type="checkout"
        analysis="Checkout failure - possibly submodule or permission issue"
    elif echo "$failed_steps" | grep -qi "algolia"; then
        fix_type="algolia"
        analysis="Algolia indexing failure - check API key or config"
    elif echo "$failed_steps" | grep -qi "deploy\|netlify"; then
        fix_type="deploy"
        analysis="Deployment failure - check deployment credentials"
    else
        fix_type="unknown"
        analysis="Unknown failure pattern - manual investigation needed"
    fi

    echo "{\"fix_type\": \"$fix_type\", \"analysis\": \"$analysis\", \"failed_steps\": $(echo "$failed_steps" | jq -R -s 'split("\n") | map(select(length > 0))')}"
}

get_file_content() {
    local repo="$1"
    local path="$2"

    github_api "/repos/$repo/contents/$path" | jq -r '.content' | base64 -d 2>/dev/null
}

update_file_in_repo() {
    local repo="$1"
    local path="$2"
    local content="$3"
    local message="$4"

    # Get current file SHA
    local current=$(github_api "/repos/$repo/contents/$path")
    local sha=$(echo "$current" | jq -r '.sha')
    local branch=$(github_api "/repos/$repo" | jq -r '.default_branch')

    # Encode content
    local encoded=$(echo -n "$content" | base64 -w 0)

    # Update file
    local data=$(jq -n \
        --arg message "$message" \
        --arg content "$encoded" \
        --arg sha "$sha" \
        --arg branch "$branch" \
        '{message: $message, content: $content, sha: $sha, branch: $branch}'
    )

    github_api "/repos/$repo/contents/$path" "PUT" "$data"
}

create_file_in_repo() {
    local repo="$1"
    local path="$2"
    local content="$3"
    local message="$4"

    local branch=$(github_api "/repos/$repo" | jq -r '.default_branch')
    local encoded=$(echo -n "$content" | base64 -w 0)

    local data=$(jq -n \
        --arg message "$message" \
        --arg content "$encoded" \
        --arg branch "$branch" \
        '{message: $message, content: $content, branch: $branch}'
    )

    github_api "/repos/$repo/contents/$path" "PUT" "$data"
}

apply_gemfile_fix() {
    local repo="$1"

    log_fix "Applying Gemfile fix for Ruby 3.4 compatibility: $repo"

    # Get current Gemfile
    local current_gemfile=$(get_file_content "$repo" "Gemfile")

    if [[ -z "$current_gemfile" ]]; then
        log_error "Could not fetch Gemfile from $repo"
        return 1
    fi

    # Check if already has Ruby 3.4 compatibility gems
    if echo "$current_gemfile" | grep -q "gem \"csv\""; then
        log_info "Gemfile already has Ruby 3.4 compatibility gems"
        return 0
    fi

    # Add Ruby 3.4 compatibility gems after source line
    local new_gemfile=$(echo "$current_gemfile" | sed '/^source/a\
\
# Required for Ruby 3.4+ (no longer bundled in stdlib)\
gem "csv"\
gem "logger"\
gem "base64"\
gem "bigdecimal"\
gem "observer"\
gem "ostruct"')

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would update Gemfile in $repo"
        return 0
    fi

    # Update file
    update_file_in_repo "$repo" "Gemfile" "$new_gemfile" "fix: Add Ruby 3.4 compatibility gems"
    log_success "Updated Gemfile in $repo"
}

apply_workflow_fix() {
    local repo="$1"

    log_fix "Applying workflow fix for standardized Jekyll build: $repo"

    # Check if jekyll.yml exists
    local current_workflow=$(get_file_content "$repo" ".github/workflows/jekyll.yml")

    if [[ -z "$current_workflow" ]]; then
        log_warning "No jekyll.yml found, checking other workflow names..."

        # Try common workflow names
        for wf in "build.yml" "deploy.yml" "github-pages.yml"; do
            current_workflow=$(get_file_content "$repo" ".github/workflows/$wf")
            if [[ -n "$current_workflow" ]]; then
                log_info "Found workflow: $wf"
                break
            fi
        done
    fi

    # Create standardized workflow
    local new_workflow='name: Jekyll Build and Deploy

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - uses: BrightSoftwares/blogpost-tools/jekyll-action@main
        with:
          jekyll_src: "."
          gem_src: "."
          pre_build_commands: ""
'

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would update/create jekyll.yml in $repo"
        return 0
    fi

    if [[ -n "$current_workflow" ]]; then
        update_file_in_repo "$repo" ".github/workflows/jekyll.yml" "$new_workflow" "fix: Update to standardized Jekyll workflow"
    else
        create_file_in_repo "$repo" ".github/workflows/jekyll.yml" "$new_workflow" "fix: Add standardized Jekyll workflow"
    fi

    log_success "Updated workflow in $repo"
}

apply_fix() {
    local repo="$1"
    local fix_type="$2"

    case "$fix_type" in
        gemfile)
            apply_gemfile_fix "$repo"
            ;;
        jekyll_config)
            # For Jekyll config issues, often need to update workflow
            apply_workflow_fix "$repo"
            apply_gemfile_fix "$repo"
            ;;
        checkout)
            log_warning "Checkout issues typically need manual intervention"
            ;;
        algolia)
            log_warning "Algolia issues need API key verification"
            ;;
        deploy)
            log_warning "Deploy issues need credential verification"
            ;;
        *)
            log_warning "No automatic fix available for: $fix_type"
            ;;
    esac
}

trigger_workflow() {
    local repo="$1"
    local workflow="${2:-jekyll.yml}"
    local branch=$(github_api "/repos/$repo" | jq -r '.default_branch')

    log_info "Triggering $workflow in $repo (branch: $branch)"

    local data=$(jq -n --arg ref "$branch" '{ref: $ref}')
    github_api "/repos/$repo/actions/workflows/$workflow/dispatches" "POST" "$data"

    log_success "Workflow triggered"
}

wait_for_run() {
    local repo="$1"
    local timeout_secs=600  # 10 minutes
    local elapsed=0
    local interval=30

    log_info "Waiting for workflow to start and complete..."
    sleep 10  # Initial wait for workflow to register

    while [[ $elapsed -lt $timeout_secs ]]; do
        local latest=$(github_api "/repos/$repo/actions/workflows/jekyll.yml/runs?per_page=1")
        local status=$(echo "$latest" | jq -r '.workflow_runs[0].status')
        local conclusion=$(echo "$latest" | jq -r '.workflow_runs[0].conclusion')

        if [[ "$status" == "completed" ]]; then
            echo "$latest" | jq '.workflow_runs[0]'
            return 0
        fi

        log_info "Status: $status (${elapsed}s elapsed)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    log_error "Timeout waiting for workflow"
    return 1
}

collect_results() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local results_file="${RESULTS_DIR}/iteration_${ITERATION}_${timestamp}.json"

    mkdir -p "$RESULTS_DIR"

    log_info "Collecting results (iteration $ITERATION)..."

    echo '{"iteration": '$ITERATION', "timestamp": "'$timestamp'", "results": [' > "$results_file"

    local first=true
    local sites=()

    if [[ -n "$SINGLE_SITE" ]]; then
        sites=("$SINGLE_SITE")
    else
        sites=(
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
    fi

    for repo in "${sites[@]}"; do
        log_info "Checking: $repo"

        [[ "$first" == "true" ]] && first=false || echo "," >> "$results_file"

        local latest=$(github_api "/repos/$repo/actions/workflows/jekyll.yml/runs?per_page=1")
        local run_id=$(echo "$latest" | jq -r '.workflow_runs[0].id')
        local status=$(echo "$latest" | jq -r '.workflow_runs[0].status')
        local conclusion=$(echo "$latest" | jq -r '.workflow_runs[0].conclusion')
        local html_url=$(echo "$latest" | jq -r '.workflow_runs[0].html_url')

        local analysis="{}"
        if [[ "$conclusion" == "failure" && "$run_id" != "null" ]]; then
            local jobs=$(github_api "/repos/$repo/actions/runs/$run_id/jobs")
            analysis=$(analyze_failure "$repo" "$run_id" "$jobs")
        fi

        cat >> "$results_file" << EOF
{
  "repo": "$repo",
  "run_id": "$run_id",
  "status": "$status",
  "conclusion": "$conclusion",
  "html_url": "$html_url",
  "analysis": $analysis
}
EOF
    done

    echo "]}" >> "$results_file"

    echo "$results_file"
}

process_failures() {
    local results_file="$1"
    local fixed=0

    log_info "Processing failures from: $results_file"

    local failures=$(jq -r '.results[] | select(.conclusion == "failure") | @base64' "$results_file")

    if [[ -z "$failures" ]]; then
        log_success "No failures to process!"
        return 0
    fi

    for failure in $failures; do
        local decoded=$(echo "$failure" | base64 -d)
        local repo=$(echo "$decoded" | jq -r '.repo')
        local fix_type=$(echo "$decoded" | jq -r '.analysis.fix_type')
        local analysis=$(echo "$decoded" | jq -r '.analysis.analysis')

        log_info "Processing failure: $repo"
        log_info "  Analysis: $analysis"
        log_info "  Fix type: $fix_type"

        if [[ "$fix_type" != "null" && "$fix_type" != "unknown" ]]; then
            apply_fix "$repo" "$fix_type"
            fixed=$((fixed + 1))

            # Re-trigger workflow after fix
            if [[ "$DRY_RUN" != "true" ]]; then
                sleep 2
                trigger_workflow "$repo"
            fi
        fi
    done

    echo "$fixed"
}

print_summary() {
    local results_file="$1"

    echo ""
    log_info "==========================================="
    log_info "ITERATION $ITERATION SUMMARY"
    log_info "==========================================="

    local total=$(jq '.results | length' "$results_file")
    local success=$(jq '[.results[] | select(.conclusion == "success")] | length' "$results_file")
    local failed=$(jq '[.results[] | select(.conclusion == "failure")] | length' "$results_file")
    local pending=$(jq '[.results[] | select(.status != "completed")] | length' "$results_file")

    echo ""
    echo "Total Sites: $total"
    echo -e "${GREEN}Success: $success${NC}"
    echo -e "${RED}Failed: $failed${NC}"
    echo -e "${YELLOW}Pending: $pending${NC}"
    echo ""

    if [[ $failed -gt 0 ]]; then
        log_error "Failed workflows:"
        jq -r '.results[] | select(.conclusion == "failure") | "  - \(.repo): \(.analysis.analysis // "unknown")"' "$results_file"
    fi

    echo "$failed"
}

main() {
    parse_args "$@"
    mkdir -p "$RESULTS_DIR" "$FIXES_DIR" "$LOGS_DIR"

    log_info "==========================================="
    log_info "Automated Fix Mechanism"
    log_info "Max iterations: $MAX_ITERATIONS"
    log_info "Dry run: $DRY_RUN"
    log_info "==========================================="

    while [[ $ITERATION -lt $MAX_ITERATIONS ]]; do
        ITERATION=$((ITERATION + 1))
        log_info ""
        log_info "========== ITERATION $ITERATION =========="

        # Collect current results
        local results_file=$(collect_results)

        # Print summary and get failure count
        local failures=$(print_summary "$results_file")

        # If no failures, we're done!
        if [[ "$failures" -eq 0 ]]; then
            log_success ""
            log_success "==========================================="
            log_success "ALL WORKFLOWS PASSING!"
            log_success "==========================================="
            exit 0
        fi

        # Process and fix failures
        local fixed=$(process_failures "$results_file")

        if [[ "$fixed" -eq 0 ]]; then
            log_warning "No automatic fixes could be applied"
            log_warning "Manual intervention may be required"
            break
        fi

        log_info "Applied $fixed fixes, waiting for workflows to complete..."

        if [[ "$DRY_RUN" != "true" ]]; then
            sleep 120  # Wait 2 minutes for workflows to run
        fi
    done

    log_warning ""
    log_warning "==========================================="
    log_warning "Max iterations reached or no more fixes available"
    log_warning "Manual investigation may be required"
    log_warning "==========================================="

    # Final results
    local final_results=$(collect_results)
    print_summary "$final_results"

    exit 1
}

main "$@"
