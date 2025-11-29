# Workflow Analysis Summary

**Analysis Date:** 2025-11-29
**Analysis Period:** Last 30 days (2025-10-29 to 2025-11-29)

---

## Overview

| Metric | Value |
|--------|-------|
| Total Jekyll Repositories | 15 |
| Repositories with Workflows | 12 |
| Repositories without Workflows | 3 |
| Total Workflow Files | 131 |
| Total Workflow Runs Analyzed | ~1,200 |
| Average Workflows per Repo | 8.7 |

---

## Repository Breakdown

### By Workflow Count

| Repository | Workflows | Status |
|------------|-----------|--------|
| BrightSoftwares/olympics-paris2024.com | 19 | 🔴 High activity |
| BrightSoftwares/eagles-techs.com | 19 | 🔴 High activity |
| BrightSoftwares/ieatmyhealth.com | 17 | 🔴 High activity |
| BrightSoftwares/modabyflora-corporate | 16 | 🔴 High activity |
| BrightSoftwares/corporate-website | 16 | 🔴 High activity |
| sergioafanou/smart-cv | 14 | 🟡 Medium activity |
| BrightSoftwares/joyousbyflora-posts | 9 | 🟡 Medium activity |
| Causting/space-up-planet.com | 5 | 🟡 Medium activity |
| BrightSoftwares/keke.li | 5 | 🟡 Medium activity |
| BrightSoftwares/foolywise.com | 5 | 🟡 Medium activity |
| Causting/causting.com | 4 | 🟢 Low activity |
| sergioafanou/latexcv | 2 | 🟢 Low activity |
| Hayes-Tech/hayestech-website | 0 | ⚪ No workflows |
| BrightSoftwares/hosting_frontend | 0 | ⚪ No workflows |
| BrightSoftwares/automatic-app-landing-page | 0 | ⚪ No workflows |

---

## Failure Rate Analysis

### Critical Failures (>75% failure rate)

| Workflow Name | Repos Affected | Avg Failure Rate | Status |
|---------------|----------------|------------------|--------|
| `.github/workflows/jekyll.yml` | 5 | 100% | 🔴 CRITICAL |
| `.github/workflows/github-pages.yml` | 3 | 100% | 🔴 CRITICAL |
| Build and deploy Jekyll site to GitHub Pages | 2 | 75% | 🔴 CRITICAL |
| Analyse jekyll generated html | 3 | 75-100% | 🔴 CRITICAL |

### High Failures (50-75% failure rate)

| Workflow Name | Repos Affected | Avg Failure Rate | Status |
|---------------|----------------|------------------|--------|
| Jekyll GitHub Pages publication | 8 | 58-71% | 🟠 HIGH |
| Jekyll Build with Reusable Workflow | 2 | 71% | 🟠 HIGH |
| SEO Diagnostics | 2 | 50-100% | 🟠 HIGH |

### Good Performance (<10% failure rate)

| Workflow Name | Repos Affected | Avg Failure Rate | Status |
|---------------|----------------|------------------|--------|
| Auto Internal Linking | 12 | 7-8% | ✅ GOOD |
| OpenAI Generate Blog posts | 12 | 4-8% | ✅ GOOD |
| Translate posts | 5 | 7% | ✅ GOOD |
| Keyword Suggestion | 7 | 5-10% | ✅ GOOD |

---

## Workflow Categories

### 1. Jekyll Build & Deploy (11 repos)

**Current State:**
- ✅ All using reusable-jekyll-build.yml
- 🔴 58-100% failure rate (CRITICAL ISSUE)
- 🔴 Build-only, no deployment

**Common Features:**
- Ruby 3.4.1, Jekyll 4.3.4
- Submodules: 11/11
- Algolia: Enabled but disabled in all (0/11 active)
- Netlify: 0/11 deploying
- Caching: 0/11 using cache

**Variations:**
- Pre-build commands (imagemagick): 2/11
- Multi-language (EN/FR): 3/11

### 2. SEO & Analysis (8 repos)

**Current State:**
- ❌ NOT using reusable workflows
- 🔴 66-100% failure rate
- 🔴 High resource usage (self-hosted)

**Workflows:**
- seo-html-analysis.yml (4 repos)
- seo_diagnotics.yml (8 repos)
- semantic_clustering.yml (6 repos)

### 3. Content Automation (12 repos)

**Current State:**
- ✅ Most using reusable workflows
- ✅ 4-8% failure rate (GOOD)

**Workflows:**
- auto-internal_linking.yml (12 repos) - NOT reusable yet
- auto-moveandpublish-posts.yml (7 repos) - ✅ Reusable
- auto-keywordandyoutubegen-posts.yml (12 repos) - ✅ Reusable
- auto-openaigenerateblogpost.yml (12 repos) - ✅ Reusable

### 4. Content Generation (9 repos)

**Current State:**
- ❌ NOT using reusable workflows
- ✅ Low-medium failure rate

**Workflows:**
- keyword_suggestion.yml (7 repos)
- rss-news-to-blogpost.yml (9 repos)
- yt_vids_and_transcribe.yml (7 repos)
- post-summarizer.yml (4 repos)

### 5. Content Enhancement (6 repos)

**Current State:**
- ❌ NOT using reusable workflows
- ✅ Low failure rate

**Workflows:**
- featured-image-finder.yml (6 repos)
- translate_posts.yml (5 repos)
- improve_blogpost_files.yml (1 repo)

### 6. Utilities (7 repos)

**Current State:**
- Mixed (some reusable, some not)

**Workflows:**
- generate_aliases_file.yml (6 repos)
- fix-indexation-issues.yml (1 repo) - ✅ Reusable
- google_autocomplete.yml (1 repo)
- auto-schedule-posts.yml (6 repos)

---

## Reusable Workflow Adoption

### Currently Using Reusable Workflows

| Reusable Workflow | Adopters | Failure Rate | Status |
|-------------------|----------|--------------|--------|
| reusable-jekyll-build.yml | 11 repos | 58-100% | 🔴 BROKEN |
| reusable-automoveandpublish-posts.yml | 7 repos | Low-Med | 🟡 OK |
| reusable_keywordsuggestionandytvidsposts.yml | 12 repos | Low | ✅ GOOD |
| reusable_openaigenerateblogpost.yml | 12 repos | 4-8% | ✅ GOOD |
| reusable_indexation-issues.yml | 1 repo | Unknown | ⚪ Unknown |

### Not Yet Using Reusable Workflows

| Workflow Type | Repos | Candidate for Migration? |
|---------------|-------|--------------------------|
| auto-internal_linking | 12 | ✅ YES - High usage |
| seo-html-analysis | 4 | ✅ YES - High failures |
| seo_diagnotics | 8 | ✅ YES - High usage |
| keyword_suggestion | 7 | ✅ YES - High usage |
| rss-news-to-blogpost | 9 | ✅ YES - High usage |
| yt_vids_and_transcribe | 7 | ✅ YES - High usage |
| featured-image-finder | 6 | ✅ YES - Medium usage |
| translate_posts | 5 | ✅ YES - Medium usage |
| generate_aliases_file | 6 | ✅ YES - Medium usage |
| auto-schedule-posts | 6 | ✅ YES - Medium usage |
| post-summarizer | 4 | 🟡 MAYBE - Low usage |
| semantic_clustering | 6 | 🟡 MAYBE - Needs review |

---

## Duplicate/Obsolete Workflows

### Confirmed Duplicates

| Old Version | Status | Action Needed |
|-------------|--------|---------------|
| keyword_suggestion_old.yml | eagles-techs.com | 🗑️ DELETE |
| keyword_generation_old.yml | ieatmyhealth.com | 🗑️ DELETE |

### Potential Duplicates (Need Clarification)

| Workflow A | Workflow B | Repos | Investigation Needed |
|------------|------------|-------|---------------------|
| openai-posts-generator.yml | auto-openaigenerateblogpost.yml | 2 vs 12 | Same functionality? |
| auto-internal_linking.yml | auto-internal-linking-matrix.yml | 12 vs 1 | Matrix variant purpose? |

---

## Runner Usage

### By Runner Type

| Runner Type | Workflows | Usage Pattern |
|-------------|-----------|---------------|
| ubuntu-latest | ~60% | Default for most workflows |
| self-hosted | ~30% | SEO, some content automation |
| Dynamic (check-runner) | ~10% | Auto-internal-linking, some others |

### Check-Runner Usage

**Workflows Using Dynamic Routing:**
- auto-internal_linking.yml (12 repos)
- auto-moveandpublish-posts.yml (via reusable workflow)
- seo-html-analysis.yml (4 repos - hardcoded self-hosted)

**Issues:**
- 🔴 3 bugs in check-runner code
- ❌ No free tier management
- ❌ No force self-hosted option
- ❌ No threshold-based routing

---

## Scheduling Patterns

| Schedule | Workflows | Example |
|----------|-----------|---------|
| Daily | 12 | auto-internal_linking (01:40 UTC) |
| Weekly | 8 | seo-html-analysis (Tue 07:00 UTC) |
| On-demand only | 111 | Most content generation workflows |

---

## Critical Action Items

### Immediate (High Priority)

1. **Fix Jekyll Build Workflows** 🔴
   - Issue: 58-100% failure rate
   - Impact: ALL 11 repos affected
   - Action: Debug and fix reusable-jekyll-build.yml

2. **Fix Check-Runner Bugs** 🔴
   - Issue: 3 bugs identified
   - Impact: Dynamic routing broken
   - Action: Fix logic errors, implement enhancements

3. **Fix SEO Workflows** 🔴
   - Issue: 66-100% failure rate
   - Impact: 8 repos affected
   - Action: Debug or create reusable version

### Short Term (Medium Priority)

4. **Create Reusable Workflows** 🟡
   - auto-internal_linking (12 repos)
   - keyword_suggestion (7 repos)
   - rss-news-to-blogpost (9 repos)
   - yt_vids_and_transcribe (7 repos)

5. **Delete Obsolete Workflows** 🟡
   - keyword_suggestion_old.yml
   - keyword_generation_old.yml

6. **Enhance Check-Runner** 🟡
   - Free tier threshold management
   - Force runner options
   - Monitoring

### Long Term (Low Priority)

7. **Consolidate Similar Workflows** 🟢
   - Multi-language variants (EN/FR)
   - News variants
   - Investigate openai-posts-generator vs auto-openaigenerateblogpost

8. **Add Deployment** 🟢
   - Netlify deployment to Jekyll workflows
   - GitHub Pages option

9. **Performance Optimization** 🟢
   - Add caching to Jekyll builds
   - Optimize self-hosted runner usage

---

## Success Metrics (Current vs Target)

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Jekyll Build Success Rate | 0-42% | >95% | -53% 🔴 |
| SEO Workflow Success Rate | 0-34% | >90% | -56% 🔴 |
| Content Automation Success Rate | 92-96% | >95% | On track ✅ |
| Reusable Workflow Adoption | 42% (11/26 types) | >80% | -38% 🟡 |
| Average Build Time | Unknown | <5 min | TBD |
| Free Tier Usage Efficiency | Unmanaged | <80% quota | TBD |

---

## Recommendations Priority

### Priority 1: Fix Broken Workflows
1. Debug Jekyll build failures (58-100% failure)
2. Fix check-runner bugs
3. Fix or deprecate SEO workflows (66-100% failure)

### Priority 2: Migrate to Reusable
1. Create reusable workflow for auto-internal-linking (12 repos)
2. Create reusable workflow for keyword_suggestion (7 repos)
3. Create reusable workflow for rss-news-to-blogpost (9 repos)

### Priority 3: Enhance & Optimize
1. Implement check-runner free tier management
2. Add caching to Jekyll builds
3. Add Netlify deployment option
4. Consolidate duplicate workflows

### Priority 4: Clean Up
1. Delete obsolete workflows
2. Standardize naming conventions
3. Update documentation
4. Create migration guides

---

## Next Steps

1. ✅ User fills in WORKFLOW_MIGRATION_INSTRUCTIONS.md with detailed decisions
2. ✅ User reviews CHECK_RUNNER_ANALYSIS.md and provides configuration preferences
3. ⏳ Clarify questions about Jekyll build failures, Algolia, Netlify deployment
4. ⏳ Create detailed implementation plan
5. ⏳ Execute migration systematically by priority

---

**Document Version:** 1.0
**Generated:** 2025-11-29
**Source Data:** analysis-data/*.json files
**Related Docs:** WORKFLOW_MIGRATION_INSTRUCTIONS.md, CHECK_RUNNER_ANALYSIS.md
