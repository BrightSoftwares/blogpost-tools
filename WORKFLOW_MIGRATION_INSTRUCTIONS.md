# Jekyll Workflows Migration & Consolidation Plan

**Date:** 2025-11-29
**Analysis Scope:** 15 Jekyll repositories, 131 workflow files
**Purpose:** Centralize, harmonize, and improve GitHub Actions workflows

---

## TABLE OF CONTENTS

1. [Repository Overview](#repository-overview)
2. [Workflow Inventory & Instructions](#workflow-inventory--instructions)
3. [Check-Runner Enhancement Requirements](#check-runner-enhancement-requirements)
4. [Reusable Workflows - Current State](#reusable-workflows---current-state)
5. [Edge Cases & Special Scenarios](#edge-cases--special-scenarios)
6. [Questions for Clarification](#questions-for-clarification)
7. [Additional Workflows/Features Not Listed](#additional-workflowsfeatures-not-listed)
8. [Migration Execution Plan](#migration-execution-plan)

---

## REPOSITORY OVERVIEW

| Repository | Workflows | Current State | Notes |
|------------|-----------|---------------|-------|
| BrightSoftwares/olympics-paris2024.com | 19 | Mixed (some reusable) | Highest workflow count |
| BrightSoftwares/eagles-techs.com | 19 | Mixed (some reusable) | High failure rates |
| BrightSoftwares/ieatmyhealth.com | 17 | Mixed (some reusable) | SEO workflows failing |
| BrightSoftwares/modabyflora-corporate | 16 | Mixed (some reusable) | Multi-language (EN/FR) |
| BrightSoftwares/corporate-website | 16 | Mixed (some reusable) | Multi-language (EN/FR) |
| sergioafanou/smart-cv | 14 | Mixed (some reusable) | |
| BrightSoftwares/joyousbyflora-posts | 9 | Mixed (some reusable) | |
| Causting/space-up-planet.com | 5 | Mixed (some reusable) | |
| BrightSoftwares/keke.li | 5 | Mixed (some reusable) | |
| BrightSoftwares/foolywise.com | 5 | Mixed (some reusable) | |
| Causting/causting.com | 4 | Mixed (some reusable) | |
| sergioafanou/latexcv | 2 | Custom (CV generation) | |
| Hayes-Tech/hayestech-website | 0 | No workflows | Needs setup? |
| BrightSoftwares/hosting_frontend | 0 | No workflows | Needs setup? |
| BrightSoftwares/automatic-app-landing-page | 0 | No workflows | Needs setup? |

---

## WORKFLOW INVENTORY & INSTRUCTIONS

### INSTRUCTIONS KEY:
- **ACTION:** MIGRATE / ENHANCE / DELETE / KEEP-AS-IS / CREATE-NEW / MERGE
- **PRIORITY:** HIGH / MEDIUM / LOW
- **TARGET:** Name of reusable workflow to migrate to (if applicable)
- **NOTES:** Your specific instructions

---

### CATEGORY 1: Jekyll Build & Deploy Workflows

#### 1.1 Jekyll Build (jekyll.yml / github-pages.yml)

**Current Analysis:**
- Used in: 11 repositories
- Current State: ALL using `reusable-jekyll-build.yml@main`
- Failure Rate: **58-100%** (CRITICAL)
- Runs-on: Dynamic (via check-runner) or ubuntu-latest
- Features:
  - Ruby 3.4.1 / Jekyll 4.3.4
  - Algolia indexing (optional)
  - Submodule support
  - Pre-build commands (imagemagick install in some)
  - Artifact upload
  - Build-only (no deployment)

**Variations Found:**
- corporate-website: Has `pre-build-commands: 'sudo apt-get update && sudo apt-get install -y imagemagick libmagickwand-dev'`
- foolywise.com: No pre-build commands
- smart-cv: Has imagemagick pre-build

**YOUR INSTRUCTIONS:**

| Repository | ACTION | PRIORITY | TARGET | NOTES |
|------------|--------|----------|--------|-------|
| ALL (11 repos) | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN: Should I fix existing reusable-jekyll-build.yml or create new version?]_ |

**Specific Features to Address:**

| Feature | Current State | ACTION | NOTES |
|---------|---------------|--------|-------|
| Pre-build imagemagick install | Duplicated in some workflows | _[FILL IN]_ | _[Should this be in reusable workflow or keep as parameter?]_ |
| Algolia indexing | Currently enabled=false in all | _[FILL IN]_ | _[Why disabled? Remove or fix?]_ |
| Submodule checkout | Hardcoded repo path | _[FILL IN]_ | _[Make configurable?]_ |
| Build artifact upload | Always uploads | _[FILL IN]_ | _[Make optional?]_ |
| Netlify deployment | Not in current workflows | _[FILL IN]_ | _[Add to reusable workflow?]_ |
| GitHub Pages deployment | Not in current workflows | _[FILL IN]_ | _[Add to reusable workflow?]_ |
| Caching (bundle, images) | Not in reusable-jekyll-build.yml | _[FILL IN]_ | _[Add caching to improve speed?]_ |

---

### CATEGORY 2: SEO & Analysis Workflows

#### 2.1 SEO HTML Analysis (seo-html-analysis.yml)

**Current Analysis:**
- Used in: 4 repositories (corporate-website, eagles-techs.com, olympics-paris2024.com, ieatmyhealth.com)
- Current State: NOT using reusable workflow
- Failure Rate: **66-100%** (CRITICAL)
- Runs-on: self-hosted
- Features:
  - Clones repo + submodules
  - Jekyll build
  - HTMLProofer validation
  - Commits results to repo
  - Uses caching for vendor/bundle

**Common Pattern:**
```yaml
- Jekyll build
- HTMLProofer check
- Save results to _drafts/html_analysis.txt
- Commit if changes
```

**YOUR INSTRUCTIONS:**

| Feature/Action | ACTION | PRIORITY | NOTES |
|----------------|--------|----------|-------|
| Create reusable workflow | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |
| Fix current failures | _[FILL IN]_ | _[FILL IN]_ | _[What's causing 100% failure?]_ |
| Keep committing results to repo | _[FILL IN]_ | _[FILL IN]_ | _[Or use artifacts instead?]_ |
| Merge with Jekyll build workflow | _[FILL IN]_ | _[FILL IN]_ | _[Or keep separate?]_ |

#### 2.2 SEO Diagnostics (seo_diagnotics.yml)

**Current Analysis:**
- Used in: 8 repositories
- Current State: NOT using reusable workflow
- Failure Rate: **50-100%** (varies by repo)
- Runs-on: Varies (self-hosted or ubuntu-latest)
- Features: _[Need to analyze specific workflow]_

**YOUR INSTRUCTIONS:**

| Repository | ACTION | PRIORITY | NOTES |
|------------|--------|----------|-------|
| ALL (8 repos) | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN: Keep, delete, or fix?]_ |

#### 2.3 Semantic Clustering (semantic_clustering.yml)

**Current Analysis:**
- Used in: 6 repositories
- Current State: NOT using reusable workflow
- Features: _[Need details on what this does]_

**YOUR INSTRUCTIONS:**

| Feature | ACTION | NOTES |
|---------|--------|-------|
| Semantic clustering workflow | _[FILL IN]_ | _[FILL IN: What does this do? Keep or delete?]_ |

---

### CATEGORY 3: Content Automation Workflows

#### 3.1 Auto Internal Linking (auto-internal_linking.yml)

**Current Analysis:**
- Used in: 12 repositories
- Current State: NOT using reusable workflow (custom implementation in each repo)
- Failure Rate: **7-8%** (GOOD)
- Runs-on: Dynamic (check-runner)
- Features:
  - Check-runner for dynamic runner selection
  - Multi-language support (EN/FR in some repos)
  - Uses `BrightSoftwares/blogpost-tools/internal-linking@main` action
  - Uses `BrightSoftwares/blogpost-tools/markdown-linting@main` action
  - Commits changes back to repo
  - Scheduled (cron: "40 01 * * *")

**Variations Found:**
- Single language repos: Only process one language
- Multi-language repos (corporate-website, modabyflora-corporate): Process EN and FR
- olympics-paris2024.com: Has `auto-internal-linking-matrix.yml` variant

**YOUR INSTRUCTIONS:**

| Feature/Action | ACTION | PRIORITY | NOTES |
|----------------|--------|----------|-------|
| Create reusable workflow | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |
| Multi-language support | _[FILL IN]_ | _[FILL IN]_ | _[How to handle EN/FR/both?]_ |
| Keep check-runner | _[FILL IN]_ | _[FILL IN]_ | _[See check-runner section below]_ |
| Matrix strategy variant | _[FILL IN]_ | _[FILL IN]_ | _[What is auto-internal-linking-matrix.yml for?]_ |

#### 3.2 Auto Move and Publish Posts (auto-moveandpublish-posts*.yml)

**Current Analysis:**
- Used in: 7 repositories (various language variants)
- Current State: **ALREADY using** `reusable-automoveandpublish-posts.yml@main`
- Failure Rate: Low-Medium
- Runs-on: Dynamic (check-runner in reusable workflow)
- Features:
  - Transcript downloader
  - RSS converter
  - Featured image finder
  - Prettifier
  - Auto scheduler
  - Manual publication

**Variants Found:**
- `auto-moveandpublish-posts.yml` (EN only)
- `auto-moveandpublish-posts-en.yml` (EN explicit)
- `auto-moveandpublish-posts-fr.yml` (FR explicit)
- `auto-moveandpublish-posts-news.yml` (News content)
- `auto-moveandpublish-posts-news-en.yml` (News EN)

**YOUR INSTRUCTIONS:**

| Variant | ACTION | PRIORITY | NOTES |
|---------|--------|----------|-------|
| EN variant | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |
| FR variant | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |
| News variant | _[FILL IN]_ | _[FILL IN]_ | _[How is "news" different?]_ |
| Reusable workflow enhancement | _[FILL IN]_ | _[FILL IN]_ | _[Any improvements needed?]_ |

#### 3.3 Auto Keyword and YouTube Generate Posts (auto-keywordandyoutubegen-posts.yml)

**Current Analysis:**
- Used in: 12 repositories
- Current State: **ALREADY using** `reusable_keywordsuggestionandytvidsposts.yml@main`
- Failure Rate: Low
- Features: Keyword suggestion + YouTube video posts generation

**YOUR INSTRUCTIONS:**

| Feature | ACTION | NOTES |
|---------|--------|-------|
| Current reusable workflow | _[FILL IN]_ | _[Keep as-is or enhance?]_ |

#### 3.4 Auto OpenAI Generate Blogpost (auto-openaigenerateblogpost.yml)

**Current Analysis:**
- Used in: 12 repositories
- Current State: **ALREADY using** `reusable_openaigenerateblogpost.yml@main`
- Failure Rate: **4-8%** (GOOD)
- Features: AI-powered blog post generation

**YOUR INSTRUCTIONS:**

| Feature | ACTION | NOTES |
|---------|--------|-------|
| Current reusable workflow | _[FILL IN]_ | _[Keep as-is or enhance?]_ |

#### 3.5 Auto Schedule Posts (auto-schedule-posts.yml)

**Current Analysis:**
- Used in: 6 repositories
- Current State: NOT using reusable workflow (custom in each)
- Features: Schedule posts for future publication

**YOUR INSTRUCTIONS:**

| Feature | ACTION | PRIORITY | NOTES |
|---------|--------|----------|-------|
| Create reusable workflow | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |

**Special Variant:**
- `auto-schedule-games-posts.yml` (olympics-paris2024.com) - What makes this different?

| Feature | ACTION | NOTES |
|---------|--------|-------|
| Games-specific scheduling | _[FILL IN]_ | _[FILL IN: Keep separate or merge?]_ |

---

### CATEGORY 4: Content Generation Workflows

#### 4.1 Keyword Suggestion (keyword_suggestion.yml)

**Current Analysis:**
- Used in: 7 repositories
- Current State: NOT using reusable workflow
- Features: Keyword research and suggestions

**Old Versions Found:**
- `keyword_suggestion_old.yml` (eagles-techs.com)
- `keyword_generation_old.yml` (ieatmyhealth.com)

**YOUR INSTRUCTIONS:**

| Feature | ACTION | PRIORITY | NOTES |
|---------|--------|----------|-------|
| Create reusable workflow | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |
| Delete old versions | _[FILL IN]_ | _[FILL IN]_ | _[DELETE old .yml files?]_ |

#### 4.2 RSS News to Blogpost (rss-news-to-blogpost.yml)

**Current Analysis:**
- Used in: 9 repositories
- Current State: NOT using reusable workflow
- Features: Convert RSS feeds to blog posts

**YOUR INSTRUCTIONS:**

| Feature | ACTION | PRIORITY | NOTES |
|---------|--------|----------|-------|
| Create reusable workflow | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |

#### 4.3 YouTube Videos and Transcribe (yt_vids_and_transcribe.yml)

**Current Analysis:**
- Used in: 7 repositories
- Current State: NOT using reusable workflow
- Features: Download YouTube videos and create transcriptions

**YOUR INSTRUCTIONS:**

| Feature | ACTION | PRIORITY | NOTES |
|---------|--------|----------|-------|
| Create reusable workflow | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |

#### 4.4 OpenAI Posts Generator (openai-posts-generator.yml)

**Current Analysis:**
- Used in: 2 repositories (corporate-website, olympics-paris2024.com)
- Current State: NOT using reusable workflow
- Note: Similar to `auto-openaigenerateblogpost.yml` but different name

**YOUR INSTRUCTIONS:**

| Feature | ACTION | NOTES |
|---------|--------|-------|
| Difference from auto-openaigenerateblogpost | _[FILL IN]_ | _[Are these duplicates? Merge or keep separate?]_ |

#### 4.5 Post Summarizer (post-summarizer.yml)

**Current Analysis:**
- Used in: 4 repositories
- Current State: NOT using reusable workflow
- Features: Generate summaries of blog posts

**YOUR INSTRUCTIONS:**

| Feature | ACTION | PRIORITY | NOTES |
|---------|--------|----------|-------|
| Create reusable workflow | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |

#### 4.6 Post Paraphraser (post-paraphraser.yml)

**Current Analysis:**
- Used in: 1 repository (sergioafanou/smart-cv)
- Current State: NOT using reusable workflow
- Features: Paraphrase/rewrite content

**YOUR INSTRUCTIONS:**

| Feature | ACTION | NOTES |
|---------|--------|-------|
| Post paraphraser | _[FILL IN]_ | _[Keep, migrate, or delete?]_ |

---

### CATEGORY 5: Content Enhancement Workflows

#### 5.1 Featured Image Finder (featured-image-finder.yml)

**Current Analysis:**
- Used in: 6 repositories
- Current State: NOT using reusable workflow
- Features: Find and add featured images to posts

**YOUR INSTRUCTIONS:**

| Feature | ACTION | PRIORITY | NOTES |
|---------|--------|----------|-------|
| Create reusable workflow | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |

#### 5.2 Translate Posts (translate_posts.yml)

**Current Analysis:**
- Used in: 5 repositories
- Current State: NOT using reusable workflow
- Failure Rate: **7%** (GOOD)
- Features: Translate posts between languages

**YOUR INSTRUCTIONS:**

| Feature | ACTION | PRIORITY | NOTES |
|---------|--------|----------|-------|
| Create reusable workflow | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |

#### 5.3 Improve Blogpost Files (improve_blogpost_files.yml)

**Current Analysis:**
- Used in: 1 repository (joyousbyflora-posts)
- Current State: NOT using reusable workflow
- Features: Lean files, retrieve CCs, etc.

**YOUR INSTRUCTIONS:**

| Feature | ACTION | NOTES |
|---------|--------|-------|
| Improve blogpost files | _[FILL IN]_ | _[What does this do specifically?]_ |

---

### CATEGORY 6: Utility Workflows

#### 6.1 Generate Aliases File (generate_aliases_file.yml)

**Current Analysis:**
- Used in: 6 repositories
- Current State: NOT using reusable workflow
- Features: Generate Jekyll aliases for redirects

**YOUR INSTRUCTIONS:**

| Feature | ACTION | PRIORITY | NOTES |
|---------|--------|----------|-------|
| Create reusable workflow | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |

#### 6.2 Fix Indexation Issues (fix-indexation-issues.yml)

**Current Analysis:**
- Used in: 1 repository (eagles-techs.com)
- Current State: Uses `reusable_indexation-issues.yml@main`
- Features: Fix search engine indexation issues

**YOUR INSTRUCTIONS:**

| Feature | ACTION | NOTES |
|---------|--------|-------|
| Current reusable workflow | _[FILL IN]_ | _[Keep as-is or enhance?]_ |

#### 6.3 Google Autocomplete (google_autocomplete.yml)

**Current Analysis:**
- Used in: 1 repository (joyousbyflora-posts)
- Current State: NOT using reusable workflow
- Features: _[Need to analyze]_

**YOUR INSTRUCTIONS:**

| Feature | ACTION | NOTES |
|---------|--------|-------|
| Google autocomplete | _[FILL IN]_ | _[What does this do?]_ |

---

### CATEGORY 7: Special Purpose Workflows

#### 7.1 LaTeX CV Workflows (sergioafanou/latexcv)

**Current Analysis:**
- Used in: sergioafanou/latexcv
- Files:
  - `blank.yml`
  - `generate-my-cv.yml`
- Current State: Custom, not related to Jekyll
- Features: Generate CV from LaTeX

**YOUR INSTRUCTIONS:**

| Feature | ACTION | NOTES |
|---------|--------|-------|
| LaTeX CV workflows | _[FILL IN]_ | _[Keep as custom or include in analysis?]_ |

---

## CHECK-RUNNER ENHANCEMENT REQUIREMENTS

### Current Implementation Analysis

**File Location:** `blogpost-tools/check-runner` (action)

**Current Behavior:**
- Checks if self-hosted runners are available
- Returns runner label: `self-hosted` or `ubuntu-latest`
- Used in multiple workflows to route jobs dynamically

**Issues Found:** _[To be filled after analyzing the action]_

### YOUR REQUIREMENTS:

#### Feature 1: Force Runner Selection

| Requirement | IMPLEMENTATION NOTES |
|-------------|---------------------|
| Force self-hosted | _[FILL IN: How should this be triggered? Workflow input? Secret? Environment variable?]_ |
| Force ubuntu-latest | _[FILL IN: How should this be triggered?]_ |
| Override mechanism | _[FILL IN: Should override be per-workflow or global?]_ |

#### Feature 2: Free Tier Threshold Management

| Requirement | IMPLEMENTATION NOTES |
|-------------|---------------------|
| Track remaining GitHub Actions minutes | _[FILL IN: How to get this data? API? Manual update?]_ |
| Threshold configuration | _[FILL IN: What threshold(s)? E.g., "When <500 minutes left, use self-hosted for X workflows"]_ |
| Workflow priority levels | _[FILL IN: Which workflows should switch to self-hosted first?]_ |
| Threshold behavior | _[FILL IN: Hard cutoff or gradual shift?]_ |

**Example Scenario:**
```
Remaining minutes: 1000 → All on ubuntu-latest
Remaining minutes: 500  → Priority: LOW workflows → self-hosted
Remaining minutes: 200  → Priority: MEDIUM+LOW workflows → self-hosted
Remaining minutes: 50   → ALL workflows → self-hosted (except critical?)
```

| Priority Level | Workflows | YOUR ASSIGNMENT |
|----------------|-----------|-----------------|
| CRITICAL (always ubuntu-latest) | _[FILL IN]_ | _[Which workflows should always use GitHub runners?]_ |
| HIGH | _[FILL IN]_ | _[Switch to self-hosted at what threshold?]_ |
| MEDIUM | _[FILL IN]_ | _[Switch to self-hosted at what threshold?]_ |
| LOW | _[FILL IN]_ | _[Switch to self-hosted at what threshold?]_ |

#### Feature 3: Fallback Behavior

| Scenario | DESIRED BEHAVIOR |
|----------|------------------|
| Self-hosted unavailable but forced | _[FILL IN: Fail? Fallback to ubuntu-latest? Wait?]_ |
| Ubuntu-latest quota exhausted | _[FILL IN: Force self-hosted? Fail? Queue?]_ |
| Both unavailable | _[FILL IN: What should happen?]_ |

#### Feature 4: Monitoring & Reporting

| Feature | REQUIREMENT |
|---------|-------------|
| Log runner selection decisions | _[FILL IN: Yes/No? Where to log?]_ |
| Track minutes usage | _[FILL IN: How to track and report?]_ |
| Alerts when threshold reached | _[FILL IN: Notification method?]_ |
| Dashboard/summary | _[FILL IN: Needed?]_ |

#### Feature 5: Configuration

**How should check-runner be configured?**

| Method | USE THIS? | NOTES |
|--------|-----------|-------|
| Repository secrets | _[FILL IN]_ | _[FILL IN]_ |
| Workflow inputs | _[FILL IN]_ | _[FILL IN]_ |
| Central config file in blogpost-tools | _[FILL IN]_ | _[FILL IN]_ |
| API/external service | _[FILL IN]_ | _[FILL IN]_ |

**Configuration Values Needed:**

```yaml
# Example configuration structure - MODIFY AS NEEDED
check-runner-config:
  free_tier_quota: 2000  # Total monthly minutes
  current_usage: 0       # Updated automatically?

  thresholds:
    - remaining: 500
      action: switch_low_priority
    - remaining: 200
      action: switch_medium_priority
    - remaining: 50
      action: switch_all

  workflow_priorities:
    jekyll-build: HIGH
    seo-analysis: LOW
    # ... etc

  force_runner: null  # Or "self-hosted" / "ubuntu-latest"

  fallback_strategy: "fail"  # Or "fallback" / "wait"
```

**YOUR PREFERRED CONFIGURATION:**
```yaml
_[FILL IN YOUR PREFERRED CONFIG STRUCTURE]_
```

#### Edge Cases to Handle

| Edge Case | HOW TO HANDLE |
|-----------|---------------|
| Self-hosted runner offline mid-job | _[FILL IN]_ |
| Multiple self-hosted runners (load balancing?) | _[FILL IN]_ |
| Different runner capabilities (docker, etc.) | _[FILL IN]_ |
| Billing cycle rollover | _[FILL IN: Reset counters when?]_ |
| Manual minutes adjustment | _[FILL IN: How to manually set remaining minutes?]_ |
| Concurrent workflow limit reached | _[FILL IN]_ |

#### Additional Features Requested

| Feature | DESCRIPTION | PRIORITY |
|---------|-------------|----------|
| _[ADD ANY OTHER FEATURES YOU WANT]_ | _[FILL IN]_ | _[FILL IN]_ |

---

## REUSABLE WORKFLOWS - CURRENT STATE

### Existing Reusable Workflows in blogpost-tools

| Workflow Name | Status | Used By | Failure Rate | YOUR ACTION |
|---------------|--------|---------|--------------|-------------|
| reusable-jekyll-build.yml | ✅ Active | 11 repos | 58-100% | _[FILL IN: Fix/Replace/Enhance]_ |
| reusable_jekyll_build_and_deploy.yml | ✅ Active | 0 repos? | Unknown | _[FILL IN: Use this instead? Why unused?]_ |
| reusable-automoveandpublish-posts.yml | ✅ Active | 7 repos | Low-Med | _[FILL IN]_ |
| reusable-auto-internal-linking.yml | ❓ Exists | 0 repos | N/A | _[FILL IN: Why not used?]_ |
| reusable_keywordsuggestionandytvidsposts.yml | ✅ Active | 12 repos | Low | _[FILL IN]_ |
| reusable_openaigenerateblogpost.yml | ✅ Active | 12 repos | 4-8% | _[FILL IN]_ |
| reusable_commit-generated-files.yml | ✅ Active | Unknown | Unknown | _[FILL IN: Audit usage]_ |
| reusable_indexation-issues.yml | ✅ Active | 1 repo | Unknown | _[FILL IN]_ |
| reusable_deploy-application.yml | ✅ Active | Unknown | Unknown | _[FILL IN: Related to Jekyll?]_ |
| reusable_deploy-to-aws.yml | ✅ Active | Unknown | Unknown | _[FILL IN: Needed for Jekyll sites?]_ |
| reusable_deploy-to-azure.yml | ✅ Active | Unknown | Unknown | _[FILL IN: Needed for Jekyll sites?]_ |
| reusable_deploy-to-gcp.yml | ✅ Active | Unknown | Unknown | _[FILL IN: Needed for Jekyll sites?]_ |
| reusable_deploy-to-o2switch.yml | ✅ Active | Unknown | Unknown | _[FILL IN: Needed for Jekyll sites?]_ |
| reusable_crm-support-setup.yml | ✅ Active | Unknown | Unknown | _[FILL IN: Related to Jekyll?]_ |
| reusable_marketing-tools-setup.yml | ✅ Active | Unknown | Unknown | _[FILL IN: Related to Jekyll?]_ |
| reusable_product-infrastructure-setup.yml | ✅ Active | Unknown | Unknown | _[FILL IN: Related to Jekyll?]_ |

### Reusable Workflows to Create

| Workflow Name | Purpose | PRIORITY | FEATURES NEEDED |
|---------------|---------|----------|-----------------|
| _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |
| _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |
| _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |

---

## EDGE CASES & SPECIAL SCENARIOS

### Multi-Language Support

**Repos with Multi-Language:**
- BrightSoftwares/corporate-website (EN/FR)
- BrightSoftwares/modabyflora-corporate (EN/FR)
- olympics-paris2024.com (EN/FR)

**Current Handling:**
- Separate workflow files for each language OR
- Single workflow with multiple steps/jobs

**YOUR DECISION:**

| Scenario | APPROACH |
|----------|----------|
| Jekyll sites with EN/FR | _[FILL IN: Matrix strategy? Separate workflows? Single workflow with params?]_ |
| Future language additions | _[FILL IN: How to make extensible?]_ |
| Language-specific customization | _[FILL IN: How to handle differences?]_ |

### Repository-Specific Configurations

**Different folder structures found:**
- `/en/_posts/` vs `/_posts/en/` vs `/_posts/`
- `/_drafts/` with numbered subfolders (200_, 300_, etc.)
- Different paths for SEO results

**YOUR DECISION:**

| Scenario | APPROACH |
|----------|----------|
| Path configuration | _[FILL IN: Workflow inputs? Convention over configuration?]_ |
| Standardization | _[FILL IN: Force repos to match structure or flexible?]_ |

### Deployment Targets

**Targets mentioned:**
- Netlify (you mentioned this)
- GitHub Pages (in workflow names)
- No actual deployment in current workflows (build-only)

**YOUR DECISION:**

| Target | SUPPORT? | IMPLEMENTATION |
|--------|----------|----------------|
| Netlify | _[FILL IN]_ | _[FILL IN: Always? Optional? Default?]_ |
| GitHub Pages | _[FILL IN]_ | _[FILL IN: Support or deprecate?]_ |
| Both (conditional) | _[FILL IN]_ | _[FILL IN: Auto-detect or explicit param?]_ |
| Custom deployment | _[FILL IN]_ | _[FILL IN: Allow custom deploy script?]_ |

### Secrets Management

**Secrets used across workflows:**
- `SUBMODULE_SSH_PRIVATE_KEY`
- `ALGOLIA_API_KEY`
- `NETLIFY_AUTH_TOKEN`
- `NETLIFY_SITE_ID`
- `UNSPLASH_ACCESS_KEY`
- `CLOUDINARY_URL`
- `CHECK_RUNNER_ACCESS_TOKEN`
- `GITHB_TOKEN` (typo in some workflows)
- `OPENAI_API_KEY` (assumed)

**YOUR DECISION:**

| Secret | REQUIRED? | NOTES |
|--------|-----------|-------|
| SUBMODULE_SSH_PRIVATE_KEY | _[FILL IN]_ | _[All repos need this?]_ |
| ALGOLIA_API_KEY | _[FILL IN]_ | _[Still using Algolia?]_ |
| NETLIFY_AUTH_TOKEN | _[FILL IN]_ | _[Organization-level secret?]_ |
| GITHB_TOKEN typo | _[FILL IN]_ | _[Fix typo in workflows]_ |
| _[Others]_ | _[FILL IN]_ | _[FILL IN]_ |

### Scheduled Workflows

**Scheduling patterns found:**
- Daily: `"40 01 * * *"` (auto-internal-linking)
- Weekly: `"0 7 * * 2"` (seo-html-analysis - Tuesdays)
- Custom: `"Tue"` for auto-schedule

**YOUR DECISION:**

| Workflow Type | SCHEDULE | NOTES |
|---------------|----------|-------|
| Auto internal linking | _[FILL IN]_ | _[Keep daily? Change?]_ |
| SEO analysis | _[FILL IN]_ | _[Keep weekly? Change?]_ |
| Content generation | _[FILL IN]_ | _[When should these run?]_ |

### Commit Behavior

**Many workflows commit changes back to repo:**
- Internal linking results
- SEO analysis results
- Generated aliases
- Auto-scheduled posts
- Improved files

**Concerns:**
- Potential for commit loops
- Merge conflicts
- Git history clutter

**YOUR DECISION:**

| Scenario | APPROACH |
|----------|----------|
| Auto-commits | _[FILL IN: Keep current behavior or change?]_ |
| Commit messages | _[FILL IN: Standardize format?]_ |
| Branch strategy | _[FILL IN: Commit to main or create branches?]_ |
| PR creation | _[FILL IN: Auto-create PRs instead of direct commits?]_ |

### Self-Hosted Runner Dependencies

**Requirements detected:**
- Docker (for some actions)
- Imagemagick / libmagickwand
- Ruby/Jekyll
- Node.js
- Git

**YOUR DECISION:**

| Dependency | ENSURE ON SELF-HOSTED? | NOTES |
|------------|------------------------|-------|
| Docker | _[FILL IN]_ | _[FILL IN]_ |
| Imagemagick | _[FILL IN]_ | _[FILL IN]_ |
| Pre-installed gems | _[FILL IN]_ | _[Speed up builds?]_ |

### Failure Recovery

**When workflows fail:**
- Currently: Manual intervention needed
- No retry logic detected
- No notifications detected

**YOUR DECISION:**

| Scenario | APPROACH |
|----------|----------|
| Transient failures | _[FILL IN: Auto-retry?]_ |
| Failure notifications | _[FILL IN: Email? Slack? GitHub issues?]_ |
| Rollback strategy | _[FILL IN: How to handle failed deploys?]_ |

---

## QUESTIONS FOR CLARIFICATION

### Priority & Strategy Questions

1. **Overall Migration Approach:**
   - [ ] Migrate all repos at once?
   - [ ] Pilot with 1-2 repos first?
   - [ ] Gradual rollout (how many per week)?

   **YOUR ANSWER:** _[FILL IN]_

2. **Testing Strategy:**
   - How should I test changes before deploying to production?
   - Use staging branches? Test repos?

   **YOUR ANSWER:** _[FILL IN]_

3. **Backward Compatibility:**
   - Should new reusable workflows maintain compatibility with current callers?
   - Or can I do breaking changes?

   **YOUR ANSWER:** _[FILL IN]_

4. **Documentation:**
   - Update README in `.github/workflows/`?
   - Create migration guides for each workflow type?

   **YOUR ANSWER:** _[FILL IN]_

### Technical Questions

5. **Jekyll Build Failures (58-100% failure rate):**
   - What are the typical error messages?
   - Is it a specific step failing (build, submodules, algolia)?
   - Should I investigate recent runs first or just rebuild the workflow?

   **YOUR ANSWER:** _[FILL IN]_

6. **Netlify Deployment:**
   - Currently NO workflows deploy to Netlify - they only build
   - How are sites currently deployed? Manual? Netlify auto-deploy from git?
   - Should the new workflow include Netlify deployment?

   **YOUR ANSWER:** _[FILL IN]_

7. **Algolia Search:**
   - All Jekyll workflows have `enable-algolia: false`
   - Is Algolia deprecated? Should I remove it entirely?
   - Or fix it to work again?

   **YOUR ANSWER:** _[FILL IN]_

8. **reusable_jekyll_build_and_deploy.yml:**
   - This exists but isn't used anywhere
   - Should I use this as the base for improvements?
   - Or stick with reusable-jekyll-build.yml?

   **YOUR ANSWER:** _[FILL IN]_

9. **Submodule Repository Hardcoding:**
   - Currently hardcoded to `BrightSoftwares/jekyll-theme-common-includes`
   - Make this configurable?
   - Or assume all repos use this?

   **YOUR ANSWER:** _[FILL IN]_

10. **Duplicate Workflow Names:**
    - `openai-posts-generator.yml` vs `auto-openaigenerateblogpost.yml`
    - Are these actually different or duplicates?

    **YOUR ANSWER:** _[FILL IN]_

### Organization & Process Questions

11. **Repository Consolidation:**
    - 15 Jekyll repos found - is this expected?
    - Any repos that should be archived/deprecated?
    - Any missing repos I should know about?

    **YOUR ANSWER:** _[FILL IN]_

12. **Self-Hosted Runners:**
    - How many self-hosted runners do you have?
    - What are their specs/capabilities?
    - Are they always available or intermittent?

    **YOUR ANSWER:** _[FILL IN]_

13. **GitHub Actions Free Tier:**
    - Current usage patterns?
    - What's your monthly quota?
    - When does it typically run low?

    **YOUR ANSWER:** _[FILL IN]_

14. **Success Criteria:**
    - What failure rate is acceptable? <5%? <1%?
    - What's the target build time?
    - Any other KPIs?

    **YOUR ANSWER:** _[FILL IN]_

### Feature-Specific Questions

15. **SEO Workflows (66-100% failure):**
    - Are these still valuable or can they be deprecated?
    - What's causing the failures?
    - Should they be fixed or replaced?

    **YOUR ANSWER:** _[FILL IN]_

16. **Content Automation Pipeline:**
    - What's the desired flow? (RSS → Draft → Featured Image → Schedule → Publish?)
    - Should these be separate workflows or one orchestrated workflow?

    **YOUR ANSWER:** _[FILL IN]_

17. **Multi-Language Content:**
    - Future plans for more languages beyond EN/FR?
    - Should workflows support this from the start?

    **YOUR ANSWER:** _[FILL IN]_

### Additional Questions

18. _[ADD YOUR OWN QUESTION]_

    **YOUR ANSWER:** _[FILL IN]_

19. _[ADD YOUR OWN QUESTION]_

    **YOUR ANSWER:** _[FILL IN]_

20. _[ADD YOUR OWN QUESTION]_

    **YOUR ANSWER:** _[FILL IN]_

---

## ADDITIONAL WORKFLOWS/FEATURES NOT LISTED

**Did I miss anything? Add workflows or features I should analyze:**

| Workflow/Feature Name | Repository | Description | YOUR INSTRUCTIONS |
|-----------------------|------------|-------------|-------------------|
| _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |
| _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |
| _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |

**Other considerations:**

| Topic | NOTES |
|-------|-------|
| Security concerns | _[FILL IN: Any security requirements?]_ |
| Compliance requirements | _[FILL IN]_ |
| Cost constraints | _[FILL IN: Budget limits for GitHub Actions?]_ |
| Performance requirements | _[FILL IN: Max acceptable build time?]_ |
| _[Other topic]_ | _[FILL IN]_ |

---

## MIGRATION EXECUTION PLAN

**Once you fill in the above, I'll create a detailed execution plan. For now, indicate your preferences:**

### Execution Order Preference

Rank these in order (1 = highest priority):

- [ ] ____ Fix Jekyll build workflows (critical failures)
- [ ] ____ Enhance check-runner (free tier management)
- [ ] ____ Fix SEO workflows (high failure rate)
- [ ] ____ Create new reusable workflows for content automation
- [ ] ____ Delete duplicate/obsolete workflows
- [ ] ____ Consolidate multi-language workflows
- [ ] ____ Standardize repository structures
- [ ] ____ Add deployment (Netlify/GitHub Pages)
- [ ] ____ Improve caching and performance
- [ ] ____ Documentation and testing

### Timeline

**YOUR PREFERENCES:**

| Phase | Workflows to Address | Target Completion | NOTES |
|-------|---------------------|-------------------|-------|
| Phase 1 | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |
| Phase 2 | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |
| Phase 3 | _[FILL IN]_ | _[FILL IN]_ | _[FILL IN]_ |

### Rollback Plan

**If something goes wrong:**

| Scenario | ROLLBACK APPROACH |
|----------|-------------------|
| Reusable workflow breaks all sites | _[FILL IN: Keep old workflows temporarily? How long?]_ |
| Check-runner routing issues | _[FILL IN: Fallback to static runner?]_ |
| Deployment failures | _[FILL IN: Manual deployment process?]_ |

---

## SUMMARY CHECKLIST

Before submitting this document back to me, please ensure:

- [ ] All `_[FILL IN]_` sections are completed (or marked N/A)
- [ ] Priority levels assigned (HIGH/MEDIUM/LOW)
- [ ] Actions specified (MIGRATE/ENHANCE/DELETE/KEEP-AS-IS/CREATE-NEW/MERGE)
- [ ] Check-runner requirements detailed
- [ ] Questions answered
- [ ] Edge cases addressed
- [ ] Migration priorities ranked
- [ ] Any missed workflows added

---

**NEXT STEPS:**

1. Fill in this document with your detailed instructions
2. Return it to me
3. I'll ask any clarifying questions
4. I'll create a detailed implementation plan with:
   - Specific code changes needed
   - Step-by-step migration guide
   - Testing procedures
   - Rollback procedures
5. We'll execute the plan systematically

---

**Document Version:** 1.0
**Last Updated:** 2025-11-29
**Status:** AWAITING YOUR INPUT
