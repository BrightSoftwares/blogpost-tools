#!/bin/bash
#
# Audit Jekyll plugins across all repositories
# Fetches Gemfile and _config.yml to analyze plugin usage
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

OUTPUT_DIR="audit-and-align-jekyll-repos/scripts/results/plugin-audit"
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "Jekyll Plugin Audit"
echo "=========================================="
echo ""
echo "Auditing plugins across ${#ALL_REPOS[@]} repositories"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Create summary files
GEMFILE_SUMMARY="$OUTPUT_DIR/gemfile-plugins-summary.txt"
CONFIG_SUMMARY="$OUTPUT_DIR/config-plugins-summary.txt"
COMBINED_SUMMARY="$OUTPUT_DIR/all-plugins-summary.txt"

echo "# Gemfile Plugins Summary" > "$GEMFILE_SUMMARY"
echo "Generated: $(date)" >> "$GEMFILE_SUMMARY"
echo "" >> "$GEMFILE_SUMMARY"

echo "# Config Plugins Summary" > "$CONFIG_SUMMARY"
echo "Generated: $(date)" >> "$CONFIG_SUMMARY"
echo "" >> "$CONFIG_SUMMARY"

declare -A gemfile_plugins
declare -A config_plugins

for repo in "${ALL_REPOS[@]}"; do
    echo "================================================"
    echo "Repository: $repo"
    echo "================================================"

    # Get default branch
    default_branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo" | jq -r '.default_branch')

    if [[ -z "$default_branch" || "$default_branch" == "null" ]]; then
        echo "❌ Could not determine default branch"
        continue
    fi

    echo "Default branch: $default_branch"

    # Create repo output directory
    repo_dir="$OUTPUT_DIR/${repo//\//_}"
    mkdir -p "$repo_dir"

    # Fetch Gemfile
    echo "Fetching Gemfile..."
    gemfile_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/Gemfile?ref=$default_branch")

    if echo "$gemfile_response" | jq -e '.content' > /dev/null 2>&1; then
        echo "$gemfile_response" | jq -r '.content' | base64 -d > "$repo_dir/Gemfile"
        echo "✅ Gemfile saved"

        # Extract gem lines
        echo -e "\n--- Gemfile Plugins ---"
        grep -E "^\s*gem\s+" "$repo_dir/Gemfile" | tee "$repo_dir/gemfile-plugins.txt"

        # Track unique plugins
        while IFS= read -r line; do
            plugin=$(echo "$line" | sed -E 's/.*gem\s+["\x27]([^"\x27]+)["\x27].*/\1/')
            if [[ -n "$plugin" ]]; then
                gemfile_plugins["$plugin"]="${gemfile_plugins[$plugin]:-}$repo "
            fi
        done < "$repo_dir/gemfile-plugins.txt"
    else
        echo "⚠️  Gemfile not found"
    fi

    # Fetch _config.yml
    echo -e "\nFetching _config.yml..."
    config_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/_config.yml?ref=$default_branch")

    if echo "$config_response" | jq -e '.content' > /dev/null 2>&1; then
        echo "$config_response" | jq -r '.content' | base64 -d > "$repo_dir/_config.yml"
        echo "✅ _config.yml saved"

        # Extract plugins section
        echo -e "\n--- Config Plugins ---"
        awk '/^plugins:/,/^[^ ]/' "$repo_dir/_config.yml" | grep -E "^\s+-\s+" | tee "$repo_dir/config-plugins.txt"

        # Track unique plugins
        while IFS= read -r line; do
            plugin=$(echo "$line" | sed -E 's/^\s*-\s+//')
            if [[ -n "$plugin" ]]; then
                config_plugins["$plugin"]="${config_plugins[$plugin]:-}$repo "
            fi
        done < "$repo_dir/config-plugins.txt"
    else
        echo "⚠️  _config.yml not found"
    fi

    echo ""
    sleep 1
done

echo "=========================================="
echo "Generating Summary Reports"
echo "=========================================="

# Generate Gemfile plugins summary
echo "" >> "$GEMFILE_SUMMARY"
echo "## Plugins by Frequency (Gemfile)" >> "$GEMFILE_SUMMARY"
echo "" >> "$GEMFILE_SUMMARY"

for plugin in "${!gemfile_plugins[@]}"; do
    count=$(echo "${gemfile_plugins[$plugin]}" | wc -w)
    echo "$count|$plugin|${gemfile_plugins[$plugin]}"
done | sort -rn -t'|' -k1 | while IFS='|' read -r count plugin repos; do
    echo "[$count repos] $plugin" >> "$GEMFILE_SUMMARY"
    echo "  Repos: $repos" >> "$GEMFILE_SUMMARY"
    echo "" >> "$GEMFILE_SUMMARY"
done

# Generate Config plugins summary
echo "" >> "$CONFIG_SUMMARY"
echo "## Plugins by Frequency (_config.yml)" >> "$CONFIG_SUMMARY"
echo "" >> "$CONFIG_SUMMARY"

for plugin in "${!config_plugins[@]}"; do
    count=$(echo "${config_plugins[$plugin]}" | wc -w)
    echo "$count|$plugin|${config_plugins[$plugin]}"
done | sort -rn -t'|' -k1 | while IFS='|' read -r count plugin repos; do
    echo "[$count repos] $plugin" >> "$CONFIG_SUMMARY"
    echo "  Repos: $repos" >> "$CONFIG_SUMMARY"
    echo "" >> "$CONFIG_SUMMARY"
done

# Generate combined summary
cat > "$COMBINED_SUMMARY" << 'EOF'
# Combined Plugin Analysis
Generated: $(date)

This report combines plugins from both Gemfile and _config.yml

EOF

echo "" >> "$COMBINED_SUMMARY"
echo "## All Unique Plugins" >> "$COMBINED_SUMMARY"
echo "" >> "$COMBINED_SUMMARY"

# Combine all plugins
declare -A all_plugins
for plugin in "${!gemfile_plugins[@]}"; do
    all_plugins["$plugin"]="Gemfile"
done
for plugin in "${!config_plugins[@]}"; do
    if [[ -n "${all_plugins[$plugin]:-}" ]]; then
        all_plugins["$plugin"]="Both"
    else
        all_plugins["$plugin"]="Config"
    fi
done

for plugin in "${!all_plugins[@]}"; do
    echo "- $plugin (${all_plugins[$plugin]})" >> "$COMBINED_SUMMARY"
done | sort >> "$COMBINED_SUMMARY"

echo ""
echo "=========================================="
echo "AUDIT COMPLETE"
echo "=========================================="
echo ""
echo "Results saved to: $OUTPUT_DIR"
echo ""
echo "Summary files:"
echo "  - Gemfile plugins: $GEMFILE_SUMMARY"
echo "  - Config plugins: $CONFIG_SUMMARY"
echo "  - Combined: $COMBINED_SUMMARY"
echo ""
echo "Individual repo files saved in: $OUTPUT_DIR/<repo-name>/"
echo ""
