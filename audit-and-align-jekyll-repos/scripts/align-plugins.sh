#!/bin/bash
#
# Align Jekyll plugins across all repositories
# Creates dedicated branches and standardizes Gemfile plugins
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

BRANCH_NAME="claude/align-plugins-${SESSION_ID}"

echo "=========================================="
echo "Jekyll Plugin Alignment"
echo "=========================================="
echo ""
echo "Branch: $BRANCH_NAME"
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

    # Get latest commit SHA from default branch
    latest_sha=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/git/refs/heads/$default_branch" | jq -r '.object.sha')

    if [[ -z "$latest_sha" || "$latest_sha" == "null" ]]; then
        log_error "Could not get latest commit SHA"
        ((failed++))
        continue
    fi

    log_info "Latest SHA: ${latest_sha:0:8}"

    # Create or update branch
    log_info "Creating/updating branch: $BRANCH_NAME"

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

    log_success "Branch ready: $BRANCH_NAME"

    # Fetch current Gemfile
    log_info "Fetching Gemfile..."
    gemfile_info=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/Gemfile?ref=$default_branch")

    gemfile_sha=$(echo "$gemfile_info" | jq -r '.sha')
    current_gemfile=$(echo "$gemfile_info" | jq -r '.content' | base64 -d)

    if [[ -z "$gemfile_sha" || "$gemfile_sha" == "null" ]]; then
        log_error "Could not fetch Gemfile"
        ((failed++))
        continue
    fi

    # Determine updates needed based on repo
    log_info "Analyzing Gemfile for required updates..."

    updated_gemfile="$current_gemfile"
    changes_made=""

    # Priority 1: Ensure all Ruby 3.4 stdlib gems are present
    log_info "Checking Ruby 3.4 stdlib gems..."

    for gem in csv logger base64 bigdecimal observer ostruct mutex_m; do
        if ! echo "$updated_gemfile" | grep -q "^gem ['\"]$gem['\"]"; then
            log_warning "Adding missing gem: $gem"
            # Add after bigdecimal or after jekyll line
            if echo "$updated_gemfile" | grep -q "^gem ['\"]jekyll['\"]"; then
                updated_gemfile=$(echo "$updated_gemfile" | sed "/^gem ['\"]jekyll['\"]/a gem \"$gem\"")
            else
                # Add at beginning after source line
                updated_gemfile=$(echo "$updated_gemfile" | sed "/^source/a gem \"$gem\"")
            fi
            changes_made="${changes_made}add-$gem "
        fi
    done

    # Priority 2: Fix pagination for smart-cv
    if [[ "$repo" == "sergioafanou/smart-cv" ]]; then
        if echo "$updated_gemfile" | grep -q "jekyll-paginate['\"]"; then
            log_warning "Migrating jekyll-paginate to jekyll-paginate-v2"
            updated_gemfile=$(echo "$updated_gemfile" | sed "s/gem ['\"]jekyll-paginate['\"], ['\"][^'\"]*['\"]/gem 'jekyll-paginate-v2', '~> 3.0'/g")
            changes_made="${changes_made}paginate-v2 "
        fi
    fi

    # Priority 3: Standardize versions
    log_info "Standardizing plugin versions..."

    # jekyll-feed: standardize to 0.16.0
    if echo "$updated_gemfile" | grep -q "jekyll-feed.*0\.15\."; then
        updated_gemfile=$(echo "$updated_gemfile" | sed "s/\(jekyll-feed.*\)0\.15\.[0-9]/\10.16.0/g")
        changes_made="${changes_made}feed-version "
    fi

    # jekyll-toc: ensure version is specified
    if echo "$updated_gemfile" | grep -q "gem ['\"]jekyll-toc['\"]$"; then
        updated_gemfile=$(echo "$updated_gemfile" | sed "s/gem ['\"]jekyll-toc['\"]/gem 'jekyll-toc', '~> 0.18.0'/g")
        changes_made="${changes_made}toc-version "
    fi

    # jekyll-last-modified-at: ensure version is specified
    if echo "$updated_gemfile" | grep -q "gem ['\"]jekyll-last-modified-at['\"]$"; then
        updated_gemfile=$(echo "$updated_gemfile" | sed "s/gem ['\"]jekyll-last-modified-at['\"]/gem 'jekyll-last-modified-at', '~> 1.3.2'/g")
        changes_made="${changes_made}last-modified-version "
    fi

    # rexml: standardize to ~> 3.2.4 (fix >= to ~>)
    if echo "$updated_gemfile" | grep -q "rexml.*>="; then
        updated_gemfile=$(echo "$updated_gemfile" | sed "s/\(rexml.*\)>= \([0-9.]*\)/\1~> \2/g")
        changes_made="${changes_made}rexml-constraint "
    fi

    # Priority 4: Remove duplicates (modabyflora-corporate)
    if [[ "$repo" == "BrightSoftwares/modabyflora-corporate" ]]; then
        log_info "Removing duplicate gems..."
        # This is complex - we'll do it by keeping only first occurrence
        updated_gemfile=$(echo "$updated_gemfile" | awk '!seen[$0]++')
        changes_made="${changes_made}remove-duplicates "
    fi

    # Check if any changes were made
    if [[ "$updated_gemfile" == "$current_gemfile" ]]; then
        log_info "No changes needed"
        ((success++))
        echo ""
        continue
    fi

    log_info "Changes: $changes_made"

    # Encode and commit to branch
    encoded_gemfile=$(echo -n "$updated_gemfile" | base64 -w 0)

    commit_msg="Align Jekyll plugins: $changes_made"
    log_info "Committing changes..."

    commit_result=$(curl -s -X PUT \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -d "{\"message\":\"$commit_msg\",\"content\":\"$encoded_gemfile\",\"sha\":\"$gemfile_sha\",\"branch\":\"$BRANCH_NAME\"}" \
        "https://api.github.com/repos/$repo/contents/Gemfile")

    if echo "$commit_result" | jq -e '.commit' > /dev/null 2>&1; then
        log_success "Changes committed to $BRANCH_NAME"
        ((success++))
    else
        log_error "Failed to commit: $(echo "$commit_result" | jq -r '.message')"
        ((failed++))
    fi

    echo ""
    sleep 1
done

echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo "Success: $success"
echo "Failed: $failed"
echo ""
echo "Branch created in all repos: $BRANCH_NAME"
echo ""
echo "Next: Run trigger-plugin-tests.sh to test all workflows"
