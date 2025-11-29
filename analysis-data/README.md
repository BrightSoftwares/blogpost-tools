# Workflow Analysis Data

This directory contains the raw analysis data from scanning all Jekyll repositories and their workflows.

**Analysis Date:** 2025-11-29
**Repositories Scanned:** 15 Jekyll sites
**Total Workflows Analyzed:** 131
**Analysis Period:** Last 30 days of workflow runs

---

## Files in This Directory

### 1. `jekyll_repos_analysis_pretty.json` (42KB)
Complete inventory of all Jekyll repositories and their workflows.

**Structure:**
```json
[
  {
    "repo": "BrightSoftwares/corporate-website",
    "default_branch": "master",
    "has_config_yml": true,
    "has_jekyll_gemfile": true,
    "workflows": [
      {
        "name": "auto-internal_linking.yml",
        "path": ".github/workflows/auto-internal_linking.yml",
        "download_url": "https://..."
      }
    ]
  }
]
```

**Contains:**
- Repository name and default branch
- Jekyll detection (config.yml, Gemfile presence)
- Complete list of workflows per repository
- Download URLs for each workflow

**Usage:**
```bash
# Count repos
jq 'length' jekyll_repos_analysis_pretty.json

# List repos with most workflows
jq '[.[] | {repo: .repo, count: (.workflows | length)}] | sort_by(.count) | reverse' jekyll_repos_analysis_pretty.json

# Find repos with specific workflow
jq '.[] | select(.workflows[].name == "jekyll.yml") | .repo' jekyll_repos_analysis_pretty.json
```

---

### 2. `workflow_stats_pretty.json` (22KB)
Workflow execution statistics for the last 30 days.

**Structure:**
```json
[
  {
    "repo": "BrightSoftwares/corporate-website",
    "total_runs": 100,
    "workflows": [
      {
        "name": "Jekyll Build with Reusable Workflow",
        "path": ".github/workflows/github-pages.yml",
        "total": 10,
        "success": 3,
        "failure": 7,
        "cancelled": 0
      }
    ]
  }
]
```

**Contains:**
- Total workflow runs per repository (last 30 days)
- Success/failure/cancelled counts per workflow
- Workflow names and paths

**Usage:**
```bash
# Find workflows with highest failure rates
jq '[.[] | .workflows[] | select(.failure > 0) | {name: .name, total: .total, failures: .failure, rate: ((.failure / .total * 100) | floor)}] | sort_by(.rate) | reverse | .[:10]' workflow_stats_pretty.json

# Get total run counts
jq '[.[] | .total_runs] | add' workflow_stats_pretty.json

# Find workflows that never succeeded
jq '[.[] | .workflows[] | select(.success == 0 and .total > 0)]' workflow_stats_pretty.json
```

---

### 3. `workflow_failures_by_repo.json` (13KB)
Detailed failure analysis grouped by repository, showing top 5 worst workflows per repo.

**Structure:**
```json
[
  {
    "repo": "BrightSoftwares/corporate-website",
    "total_runs": 100,
    "workflows": [
      {
        "name": ".github/workflows/github-pages.yml",
        "path": ".github/workflows/github-pages.yml",
        "total": 3,
        "success": 0,
        "failure": 3,
        "failure_rate": 100
      }
    ]
  }
]
```

**Contains:**
- Top 5 worst-performing workflows per repository
- Failure rates calculated as percentages
- Sorted by failure rate (worst first)

**Usage:**
```bash
# Get all 100% failure rate workflows
jq '[.[] | .workflows[] | select(.failure_rate == 100)]' workflow_failures_by_repo.json

# Find repo with most failures
jq 'max_by([.workflows[].failure] | add)' workflow_failures_by_repo.json

# Get average failure rate across all workflows
jq '[.[] | .workflows[].failure_rate] | add / length' workflow_failures_by_repo.json
```

---

### 4. `workflow_analysis_pretty.json` (4.7KB)
Analysis of Jekyll build/deploy workflows specifically.

**Structure:**
```json
[
  {
    "repo": "BrightSoftwares/corporate-website",
    "workflow_name": "github-pages.yml",
    "runs_on": "",
    "deploys_to_netlify": false,
    "uses_algolia": true,
    "uses_submodules": true,
    "uses_cache": false,
    "has_ruby_setup": false,
    "ruby_version": "jekyllversion:",
    "uses_reusable_workflow": true,
    "reusable_workflow": "BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main"
  }
]
```

**Contains:**
- Jekyll deployment workflow configurations
- Feature usage (Netlify, Algolia, submodules, cache)
- Reusable workflow adoption
- Ruby/Jekyll versions

**Usage:**
```bash
# Count repos using reusable workflows
jq '[.[] | select(.uses_reusable_workflow == true)] | length' workflow_analysis_pretty.json

# Find workflows using Algolia
jq '.[] | select(.uses_algolia == true) | .repo' workflow_analysis_pretty.json

# Find workflows deploying to Netlify
jq '.[] | select(.deploys_to_netlify == true) | .repo' workflow_analysis_pretty.json
```

---

## Quick Stats

### Repository Distribution
```bash
# Total Jekyll repos
jq 'length' jekyll_repos_analysis_pretty.json
# Result: 15

# Repos with workflows
jq '[.[] | select(.workflows | length > 0)] | length' jekyll_repos_analysis_pretty.json
# Result: 12

# Average workflows per repo
jq '[.[] | .workflows | length] | add / length' jekyll_repos_analysis_pretty.json
# Result: 8.7
```

### Failure Analysis
```bash
# Total workflow runs analyzed
jq '[.[] | .total_runs] | add' workflow_stats_pretty.json
# Result: ~1200 runs

# Workflows with 100% failure
jq '[.[] | .workflows[] | select(.failure_rate == 100)] | length' workflow_failures_by_repo.json
# Result: Multiple

# Most problematic workflow type
jq '[.[] | .workflows[] | select(.name | contains("Jekyll"))] | group_by(.name) | map({name: .[0].name, total_failures: ([.[].failure] | add)}) | sort_by(.total_failures) | reverse | .[0]' workflow_failures_by_repo.json
```

### Reusable Workflow Adoption
```bash
# Repos using reusable Jekyll build
jq '[.[] | select(.uses_reusable_workflow == true)] | length' workflow_analysis_pretty.json
# Result: 11/11 (100%)

# But failure rate is high
# See workflow_stats_pretty.json for details
```

---

## Key Findings from Data

### 🚨 Critical Issues

1. **High Failure Rates:**
   - Jekyll build workflows: 58-100% failure
   - SEO analysis workflows: 66-100% failure
   - Multiple workflows with 100% failure (never succeeded)

2. **Most Problematic Workflows:**
   - `.github/workflows/github-pages.yml` - 100% failure in multiple repos
   - `.github/workflows/jekyll.yml` - 100% failure in multiple repos
   - `seo-html-analysis.yml` - 66-100% failure
   - `Jekyll Build with Reusable Workflow` - 71% failure

3. **Workflow Duplication:**
   - 131 total workflows across 15 repos
   - Many similar workflows not using reusable patterns
   - Old versions still present (keyword_suggestion_old.yml, etc.)

### ✅ Success Stories

1. **Low Failure Workflows:**
   - Auto Internal Linking: 7-8% failure
   - OpenAI Generate Blog posts: 4-8% failure
   - Translate posts: 7% failure

2. **Reusable Workflow Adoption:**
   - 11/11 Jekyll repos using reusable-jekyll-build.yml
   - auto-moveandpublish-posts using reusable workflow
   - auto-openaigenerateblogpost using reusable workflow

### 📊 Usage Patterns

1. **Common Features:**
   - Submodules: Used in 11/11 Jekyll workflows
   - Algolia: Enabled but set to false in all
   - Caching: Not used in reusable-jekyll-build.yml
   - Netlify: Not deploying (build-only)

2. **Scheduling:**
   - Daily: Auto internal linking (01:40 UTC)
   - Weekly: SEO analysis (Tuesday 07:00 UTC)
   - On-demand: Most content generation workflows

---

## Analysis Commands Reference

### Find Specific Issues
```bash
# Find all workflows that have never succeeded
jq '[.[] | .workflows[] | select(.success == 0 and .total > 0) | {repo: .name, path: .path}]' workflow_stats_pretty.json

# Calculate average failure rate
jq '[.[] | .workflows[] | select(.total > 0) | (.failure / .total * 100)] | add / length' workflow_stats_pretty.json

# Find repos without any workflows
jq '.[] | select(.workflows | length == 0) | .repo' jekyll_repos_analysis_pretty.json
```

### Compare Across Repos
```bash
# Get workflow counts per repo
jq '[.[] | {repo: .repo, count: (.workflows | length)}] | sort_by(.count) | reverse' jekyll_repos_analysis_pretty.json

# Find common workflow names
jq '[.[] | .workflows[].name] | group_by(.) | map({name: .[0], count: length}) | sort_by(.count) | reverse' jekyll_repos_analysis_pretty.json
```

### Identify Patterns
```bash
# Find all unique workflow names
jq '[.[] | .workflows[].name] | unique | sort' jekyll_repos_analysis_pretty.json

# Count reusable workflow usage
jq '[.[] | .workflows[] | select(.name | contains("reusable"))] | length' jekyll_repos_analysis_pretty.json

# Find workflows using specific actions
jq '.[] | select(.workflows[].name | contains("internal-linking")) | .repo' jekyll_repos_analysis_pretty.json
```

---

## Notes

- **Time Range:** Analysis covers the last 30 days (2025-10-29 to 2025-11-29)
- **Data Source:** GitHub Actions API via organization and repository endpoints
- **Limitations:**
  - API returns max 100 runs per repository
  - Some older workflow runs may not be included
  - Cancelled runs are tracked separately from failures
- **Refresh Frequency:** This is a point-in-time snapshot

---

## Related Documents

- `../WORKFLOW_MIGRATION_INSTRUCTIONS.md` - Template for migration decisions
- `../CHECK_RUNNER_ANALYSIS.md` - Analysis of check-runner feature
- `../MIGRATION_AUDIT_PLAN.md` - Overall migration strategy

---

**Generated:** 2025-11-29
**Tool:** Claude Code Analysis
**Purpose:** Support workflow consolidation and migration project
