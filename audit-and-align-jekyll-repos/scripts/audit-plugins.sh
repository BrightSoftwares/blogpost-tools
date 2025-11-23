#!/bin/bash
#
# Analyze and report on plugin differences across Jekyll repos
#

GITHUB_TOKEN="$1"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Usage: $0 <github_token>"
    exit 1
fi

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
echo "PLUGIN AUDIT ACROSS REPOS"
echo "=========================================="
echo ""

# Standard plugins that should be in all repos
STANDARD_PLUGINS=(
    "jekyll-feed"
    "jekyll-sitemap"
    "jekyll-seo-tag"
    "jekyll-last-modified-at"
)

# Create temp file for all gems
all_gems=$(mktemp)

for repo in "${ALL_REPOS[@]}"; do
    echo "Analyzing: $repo"

    # Get default branch
    default_branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo" | jq -r '.default_branch')

    # Get Gemfile
    gemfile=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://raw.githubusercontent.com/$repo/$default_branch/Gemfile" 2>/dev/null)

    if [[ -z "$gemfile" || "$gemfile" == "404: Not Found" ]]; then
        echo "  [SKIP] No Gemfile found"
        echo ""
        continue
    fi

    # Extract plugins from :jekyll_plugins group
    echo "  Plugins:"
    plugins=$(echo "$gemfile" | grep -E "^\s*gem\s+['\"]jekyll-" | grep -v "^#" | sed "s/.*gem ['\"]\\([^'\"]*\\).*/\\1/" | sort -u)
    echo "$plugins" | while read plugin; do
        if [[ -n "$plugin" ]]; then
            echo "    - $plugin"
            echo "$plugin" >> "$all_gems"
        fi
    done

    # Check for standard plugins
    echo "  Standard plugins check:"
    for std_plugin in "${STANDARD_PLUGINS[@]}"; do
        if echo "$gemfile" | grep -q "$std_plugin"; then
            echo "    ✓ $std_plugin"
        else
            echo "    ✗ $std_plugin (missing)"
        fi
    done

    echo ""
done

echo "=========================================="
echo "ALL UNIQUE PLUGINS ACROSS REPOS"
echo "=========================================="
sort "$all_gems" | uniq -c | sort -rn

rm -f "$all_gems"
