#!/bin/bash
#
# Deploy reusable Jekyll workflow to all repositories
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

BRANCH_NAME="claude/use-reusable-workflow-${SESSION_ID}"

echo "=========================================="
echo "Deploy Reusable Jekyll Workflow"
echo "=========================================="
echo ""
echo "Branch: $BRANCH_NAME"
echo "Reusable workflow: BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main"
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

    # Get latest commit SHA from default branch
    default_sha=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/git/refs/heads/$default_branch" | \
        jq -r '.object.sha')

    if [[ -z "$default_sha" || "$default_sha" == "null" ]]; then
        log_error "Could not get default branch SHA"
        ((failed++))
        continue
    fi

    # Check if branch already exists
    branch_exists=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/git/refs/heads/$BRANCH_NAME" | \
        jq -r '.object.sha')

    if [[ "$branch_exists" != "null" && -n "$branch_exists" ]]; then
        log_info "Branch already exists, will update it"
    else
        # Create new branch from default
        log_info "Creating branch from $default_branch..."
        curl -s -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            -d "{\"ref\":\"refs/heads/$BRANCH_NAME\",\"sha\":\"$default_sha\"}" \
            "https://api.github.com/repos/$repo/git/refs" > /dev/null
        log_success "Branch created"
    fi

    # Find existing Jekyll workflow file
    workflows=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/.github/workflows?ref=$default_branch" 2>/dev/null)

    workflow_file=$(echo "$workflows" | jq -r '.[] | select(.name | test("jekyll|github-pages|pages"; "i")) | .name' | head -1)

    if [[ -z "$workflow_file" || "$workflow_file" == "null" ]]; then
        workflow_file="jekyll.yml"
        log_info "No existing workflow found, will create: $workflow_file"
    else
        log_info "Found existing workflow: $workflow_file"
    fi

    # Create new workflow content using reusable workflow
    workflow_content=$(cat <<'EOF'
name: Jekyll Build with Reusable Workflow

on:
  push:
    branches:
      - main
      - master
  pull_request:
    branches:
      - main
      - master
  workflow_dispatch:

jobs:
  build:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main
    with:
      ruby-version: '3.4.1'
      jekyll-version: '4.3.4'
      runner: 'ubuntu-latest'
      enable-algolia: false
    secrets:
      SUBMODULE_SSH_PRIVATE_KEY: ${{ secrets.SUBMODULE_SSH_PRIVATE_KEY }}
EOF
)

    # Check for ImageMagick requirement (rmagick gem)
    needs_imagemagick=false
    gemfile=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/Gemfile?ref=$default_branch" 2>/dev/null)

    if echo "$gemfile" | jq -e '.content' > /dev/null 2>&1; then
        gemfile_content=$(echo "$gemfile" | jq -r '.content' | base64 -d)
        if echo "$gemfile_content" | grep -qE "rmagick|jekyll-responsive-image"; then
            needs_imagemagick=true
            log_info "Detected ImageMagick requirement (rmagick/jekyll-responsive-image)"
        fi
    fi

    # Get existing workflow to preserve Algolia settings if present
    existing_workflow=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file?ref=$default_branch" 2>/dev/null)

    enable_algolia=false
    if echo "$existing_workflow" | jq -e '.content' > /dev/null 2>&1; then
        existing_content=$(echo "$existing_workflow" | jq -r '.content' | base64 -d)

        # Check if Algolia is used
        if echo "$existing_content" | grep -q "algolia"; then
            enable_algolia=true
            log_info "Detected Algolia usage"
        fi
    fi

    # Generate workflow based on detected requirements
    if [[ "$needs_imagemagick" == "true" ]]; then
        if [[ "$enable_algolia" == "true" ]]; then
            log_info "Generating workflow with ImageMagick and Algolia"
            workflow_content=$(cat <<'EOF'
name: Jekyll Build with Reusable Workflow

on:
  push:
    branches:
      - main
      - master
  pull_request:
    branches:
      - main
      - master
  workflow_dispatch:

jobs:
  build:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main
    with:
      ruby-version: '3.4.1'
      jekyll-version: '4.3.4'
      runner: 'ubuntu-latest'
      enable-algolia: true
      pre-build-commands: 'sudo apt-get update && sudo apt-get install -y imagemagick libmagickwand-dev'
    secrets:
      ALGOLIA_API_KEY: ${{ secrets.ALGOLIA_API_KEY }}
      SUBMODULE_SSH_PRIVATE_KEY: ${{ secrets.SUBMODULE_SSH_PRIVATE_KEY }}
EOF
)
        else
            log_info "Generating workflow with ImageMagick"
            workflow_content=$(cat <<'EOF'
name: Jekyll Build with Reusable Workflow

on:
  push:
    branches:
      - main
      - master
  pull_request:
    branches:
      - main
      - master
  workflow_dispatch:

jobs:
  build:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main
    with:
      ruby-version: '3.4.1'
      jekyll-version: '4.3.4'
      runner: 'ubuntu-latest'
      pre-build-commands: 'sudo apt-get update && sudo apt-get install -y imagemagick libmagickwand-dev'
      enable-algolia: false
    secrets:
      SUBMODULE_SSH_PRIVATE_KEY: ${{ secrets.SUBMODULE_SSH_PRIVATE_KEY }}
EOF
)
        fi
    elif [[ "$enable_algolia" == "true" ]]; then
        log_info "Generating workflow with Algolia"
        workflow_content=$(cat <<'EOF'
name: Jekyll Build with Reusable Workflow

on:
  push:
    branches:
      - main
      - master
  pull_request:
    branches:
      - main
      - master
  workflow_dispatch:

jobs:
  build:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main
    with:
      ruby-version: '3.4.1'
      jekyll-version: '4.3.4'
      runner: 'ubuntu-latest'
      enable-algolia: true
    secrets:
      ALGOLIA_API_KEY: ${{ secrets.ALGOLIA_API_KEY }}
      SUBMODULE_SSH_PRIVATE_KEY: ${{ secrets.SUBMODULE_SSH_PRIVATE_KEY }}
EOF
)
    fi

    # Upload workflow file to branch
    log_info "Uploading workflow file to branch..."

    # Check if file exists on branch to get SHA for update
    branch_file=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file?ref=$BRANCH_NAME" 2>/dev/null)

    file_sha=$(echo "$branch_file" | jq -r '.sha')

    workflow_b64=$(echo "$workflow_content" | base64 -w 0)

    if [[ "$file_sha" != "null" && -n "$file_sha" ]]; then
        # Update existing file
        curl -s -X PUT \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            -d "{\"message\":\"Use reusable Jekyll workflow\\n\\n- Migrate to centralized workflow\\n- Ruby 3.4.1 + Jekyll 4.3.4\\n- Preserve Algolia settings\\n- Use ubuntu-latest runner\",\"content\":\"$workflow_b64\",\"branch\":\"$BRANCH_NAME\",\"sha\":\"$file_sha\"}" \
            "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file" > /dev/null
    else
        # Create new file
        curl -s -X PUT \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            -d "{\"message\":\"Use reusable Jekyll workflow\\n\\n- Migrate to centralized workflow\\n- Ruby 3.4.1 + Jekyll 4.3.4\\n- Preserve Algolia settings\\n- Use ubuntu-latest runner\",\"content\":\"$workflow_b64\",\"branch\":\"$BRANCH_NAME\"}" \
            "https://api.github.com/repos/$repo/contents/.github/workflows/$workflow_file" > /dev/null
    fi

    log_success "Workflow deployed to branch: $BRANCH_NAME"
    ((success++))
    echo ""
    sleep 1
done

echo "=========================================="
echo "DEPLOYMENT SUMMARY"
echo "=========================================="
echo "✅ Successfully deployed: $success"
echo "⏭️  Skipped: $skipped"
echo "❌ Failed: $failed"
echo ""

if [[ $success -gt 0 ]]; then
    echo "🎉 Reusable workflows deployed to branches!"
    echo ""
    echo "Next steps:"
    echo "1. Test workflows: ./test-reusable-workflow.sh $GITHUB_TOKEN"
    echo "2. Check status: ./check-reusable-workflow-status.sh $GITHUB_TOKEN"
    echo "3. After validation: merge branches to production"
fi
