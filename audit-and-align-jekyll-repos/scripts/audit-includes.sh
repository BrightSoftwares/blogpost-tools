#!/bin/bash
#
# Audit _includes directories across all repositories
#

GITHUB_TOKEN="$1"

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Usage: $0 <github_token>"
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

OUTPUT_DIR="audit-and-align-jekyll-repos/scripts/results/includes-audit"
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "Jekyll _includes Directory Audit"
echo "=========================================="
echo ""

# Create summary file
SUMMARY_FILE="$OUTPUT_DIR/includes-summary.txt"
echo "# _includes Directory Audit" > "$SUMMARY_FILE"
echo "Generated: $(date)" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

declare -A include_files
total_repos=0
repos_with_includes=0

for repo in "${ALL_REPOS[@]}"; do
    echo "================================================"
    log_info "Repository: $repo"
    echo "================================================"

    ((total_repos++))

    # Get default branch
    default_branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo" | jq -r '.default_branch')

    if [[ -z "$default_branch" || "$default_branch" == "null" ]]; then
        log_error "Could not determine default branch"
        continue
    fi

    log_info "Default branch: $default_branch"

    # Create repo output directory
    repo_dir="$OUTPUT_DIR/${repo//\//_}"
    mkdir -p "$repo_dir"

    # Check if _includes directory exists
    includes_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$repo/contents/_includes?ref=$default_branch")

    if echo "$includes_response" | jq -e '.[0]' > /dev/null 2>&1; then
        ((repos_with_includes++))
        log_success "_includes directory found"

        # List all include files
        echo "" > "$repo_dir/includes-list.txt"

        echo "$includes_response" | jq -r '.[] | "\(.type)|\(.name)|\(.size)|\(.path)"' | while IFS='|' read -r type name size path; do
            if [[ "$type" == "file" ]]; then
                echo "$name" >> "$repo_dir/includes-list.txt"

                # Track file across repos
                include_files["$name"]="${include_files[$name]:-}$repo "

                # Download file content for analysis
                file_content=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                    "https://api.github.com/repos/$repo/contents/$path?ref=$default_branch" | \
                    jq -r '.content' | base64 -d 2>/dev/null)

                if [[ -n "$file_content" ]]; then
                    echo "$file_content" > "$repo_dir/$name"
                    echo "  ✓ $name (${size} bytes)"
                fi
            elif [[ "$type" == "dir" ]]; then
                echo "  📁 $name/ (subdirectory)"
            fi
        done

        # Count files
        file_count=$(echo "$includes_response" | jq -r '[.[] | select(.type=="file")] | length')
        echo "  Total files: $file_count"

    else
        log_error "No _includes directory found"
        echo "No _includes directory" > "$repo_dir/includes-list.txt"
    fi

    echo ""
    sleep 1
done

echo "=========================================="
echo "Generating Summary Report"
echo "=========================================="

# Generate frequency report
echo "" >> "$SUMMARY_FILE"
echo "## Summary Statistics" >> "$SUMMARY_FILE"
echo "- Total repos: $total_repos" >> "$SUMMARY_FILE"
echo "- Repos with _includes: $repos_with_includes" >> "$SUMMARY_FILE"
echo "- Repos without _includes: $((total_repos - repos_with_includes))" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

echo "## Include Files by Frequency" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

for file in "${!include_files[@]}"; do
    count=$(echo "${include_files[$file]}" | wc -w)
    echo "$count|$file|${include_files[$file]}"
done | sort -rn -t'|' -k1 | while IFS='|' read -r count file repos; do
    echo "### $file [$count repos]" >> "$SUMMARY_FILE"
    echo "Used in: $repos" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"
done

# Generate recommendations
echo "" >> "$SUMMARY_FILE"
echo "## Recommendations" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# Find common includes (in 50%+ of repos)
common_threshold=$((repos_with_includes / 2))
echo "### Common Includes (used in $common_threshold+ repos)" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

for file in "${!include_files[@]}"; do
    count=$(echo "${include_files[$file]}" | wc -w)
    if [[ $count -ge $common_threshold ]]; then
        echo "- $file ($count repos)" >> "$SUMMARY_FILE"
    fi
done

echo "" >> "$SUMMARY_FILE"
echo "### Unique/Rare Includes (used in 1-2 repos)" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

for file in "${!include_files[@]}"; do
    count=$(echo "${include_files[$file]}" | wc -w)
    if [[ $count -le 2 ]]; then
        repos=$(echo "${include_files[$file]}" | tr ' ' '\n' | head -2 | tr '\n' ', ' | sed 's/,$//')
        echo "- $file ($repos)" >> "$SUMMARY_FILE"
    fi
done

echo ""
echo "=========================================="
echo "AUDIT COMPLETE"
echo "=========================================="
echo ""
echo "Results saved to: $OUTPUT_DIR"
echo ""
echo "Summary file: $SUMMARY_FILE"
echo ""
echo "Individual repo files saved in: $OUTPUT_DIR/<repo-name>/"
echo ""

# Display summary
cat "$SUMMARY_FILE"
