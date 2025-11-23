#!/bin/bash
#
# Workflow Test Runner and Results Collector
#
# This script triggers workflows, monitors their execution,
# collects results, and identifies failures for debugging.
#
# Usage:
#   ./test-and-collect.sh --token TOKEN [OPTIONS]
#
# Options:
#   --token TOKEN       GitHub token for API access (required)
#   --site REPO         Test only specific site
#   --wait              Wait for workflow completion
#   --timeout MINS      Timeout in minutes (default: 30)
#   --output FILE       Output results to file

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/../results"
LOGS_DIR="${SCRIPT_DIR}/../logs"

# Default values
GITHUB_TOKEN=""
SINGLE_SITE=""
WAIT_FOR_COMPLETION=false
TIMEOUT_MINS=30
OUTPUT_FILE=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --token) GITHUB_TOKEN="$2"; shift 2 ;;
            --site) SINGLE_SITE="$2"; shift 2 ;;
            --wait) WAIT_FOR_COMPLETION=true; shift ;;
            --timeout) TIMEOUT_MINS="$2"; shift 2 ;;
            --output) OUTPUT_FILE="$2"; shift 2 ;;
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

get_default_branch() {
    local repo="$1"
    github_api "/repos/$repo" | jq -r '.default_branch'
}

trigger_workflow() {
    local repo="$1"
    local workflow="${2:-jekyll.yml}"
    local branch=$(get_default_branch "$repo")

    log_info "Triggering $workflow in $repo (branch: $branch)"

    local data=$(jq -n --arg ref "$branch" '{ref: $ref}')
    local response=$(github_api "/repos/$repo/actions/workflows/$workflow/dispatches" "POST" "$data")

    if [[ -z "$response" ]]; then
        log_success "Workflow triggered successfully"
        return 0
    else
        log_warning "Response: $response"
        return 1
    fi
}

get_latest_run() {
    local repo="$1"
    local workflow="${2:-jekyll.yml}"

    github_api "/repos/$repo/actions/workflows/$workflow/runs?per_page=1" | \
        jq '.workflow_runs[0]'
}

get_run_status() {
    local repo="$1"
    local run_id="$2"

    github_api "/repos/$repo/actions/runs/$run_id" | \
        jq -r '{status: .status, conclusion: .conclusion, html_url: .html_url}'
}

get_run_logs() {
    local repo="$1"
    local run_id="$2"

    # Get jobs for this run
    local jobs=$(github_api "/repos/$repo/actions/runs/$run_id/jobs")
    echo "$jobs" | jq '.jobs[] | {name: .name, status: .status, conclusion: .conclusion, steps: [.steps[] | {name: .name, status: .status, conclusion: .conclusion}]}'
}

get_failed_step_logs() {
    local repo="$1"
    local run_id="$2"

    local jobs=$(github_api "/repos/$repo/actions/runs/$run_id/jobs")

    # Find failed jobs and steps
    echo "$jobs" | jq -r '
        .jobs[] |
        select(.conclusion == "failure") |
        "Job: \(.name)\n" +
        (.steps[] | select(.conclusion == "failure") | "  Failed Step: \(.name)\n")
    '
}

wait_for_completion() {
    local repo="$1"
    local run_id="$2"
    local timeout_secs=$((TIMEOUT_MINS * 60))
    local elapsed=0
    local interval=30

    log_info "Waiting for workflow completion (timeout: ${TIMEOUT_MINS}m)..."

    while [[ $elapsed -lt $timeout_secs ]]; do
        local status=$(github_api "/repos/$repo/actions/runs/$run_id" | jq -r '.status')

        if [[ "$status" == "completed" ]]; then
            return 0
        fi

        log_info "Status: $status (${elapsed}s elapsed)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    log_error "Timeout waiting for workflow completion"
    return 1
}

collect_all_results() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local results_file="${OUTPUT_FILE:-${RESULTS_DIR}/workflow_results_${timestamp}.json}"

    mkdir -p "$(dirname "$results_file")"

    log_info "Collecting results from all sites..."

    echo '{"timestamp": "'$timestamp'", "results": [' > "$results_file"

    local first=true
    local sites=("${JEKYLL_SITES[@]}")
    if [[ -n "$SINGLE_SITE" ]]; then
        sites=("$SINGLE_SITE")
    fi

    for repo in "${sites[@]}"; do
        log_info "Collecting results for: $repo"

        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$results_file"
        fi

        local latest_run=$(get_latest_run "$repo")
        local run_id=$(echo "$latest_run" | jq -r '.id')
        local status=$(echo "$latest_run" | jq -r '.status')
        local conclusion=$(echo "$latest_run" | jq -r '.conclusion')
        local html_url=$(echo "$latest_run" | jq -r '.html_url')
        local created_at=$(echo "$latest_run" | jq -r '.created_at')

        local jobs_info=""
        if [[ "$run_id" != "null" ]]; then
            jobs_info=$(get_run_logs "$repo" "$run_id" 2>/dev/null | jq -s '.')
        fi

        cat >> "$results_file" << EOF
{
  "repo": "$repo",
  "run_id": "$run_id",
  "status": "$status",
  "conclusion": "$conclusion",
  "html_url": "$html_url",
  "created_at": "$created_at",
  "jobs": $jobs_info
}
EOF
    done

    echo "]}" >> "$results_file"

    log_success "Results saved to: $results_file"
    echo "$results_file"
}

print_summary() {
    local results_file="$1"

    echo ""
    log_info "=========================================="
    log_info "WORKFLOW RESULTS SUMMARY"
    log_info "=========================================="

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
        jq -r '.results[] | select(.conclusion == "failure") | "  - \(.repo): \(.html_url)"' "$results_file"
    fi

    if [[ $pending -gt 0 ]]; then
        log_warning "Pending workflows:"
        jq -r '.results[] | select(.status != "completed") | "  - \(.repo): \(.status)"' "$results_file"
    fi
}

trigger_all_workflows() {
    local sites=("${JEKYLL_SITES[@]}")
    if [[ -n "$SINGLE_SITE" ]]; then
        sites=("$SINGLE_SITE")
    fi

    for repo in "${sites[@]}"; do
        trigger_workflow "$repo" "jekyll.yml" || true
        sleep 2  # Avoid rate limiting
    done
}

main() {
    parse_args "$@"
    mkdir -p "$RESULTS_DIR" "$LOGS_DIR"

    log_info "=========================================="
    log_info "Workflow Test Runner"
    log_info "=========================================="

    # Trigger workflows
    trigger_all_workflows

    # Wait if requested
    if [[ "$WAIT_FOR_COMPLETION" == "true" ]]; then
        log_info "Waiting for workflows to complete..."
        sleep 60  # Initial wait

        local sites=("${JEKYLL_SITES[@]}")
        if [[ -n "$SINGLE_SITE" ]]; then
            sites=("$SINGLE_SITE")
        fi

        for repo in "${sites[@]}"; do
            local latest_run=$(get_latest_run "$repo")
            local run_id=$(echo "$latest_run" | jq -r '.id')

            if [[ "$run_id" != "null" ]]; then
                wait_for_completion "$repo" "$run_id" || true
            fi
        done
    fi

    # Collect results
    local results_file=$(collect_all_results)

    # Print summary
    print_summary "$results_file"

    # Return exit code based on failures
    local failed=$(jq '[.results[] | select(.conclusion == "failure")] | length' "$results_file")
    if [[ $failed -gt 0 ]]; then
        exit 1
    fi
}

main "$@"
