# Jekyll Websites Feature Audit & Migration Plan

**Date:** 2025-11-23
**Scope:** All organizations (BrightSoftwares, Full3right, sergioafanou, Hayes-Tech, Causting, sweethome33, sweethome228)

---

## 1. Executive Summary

This document provides a comprehensive audit of all Jekyll websites across organizations, identifying:
- Features implemented in individual repos but not centralized in `blogpost-tools`
- Reusable workflows already in `blogpost-tools` but not deployed to all repos
- Folder structure inconsistencies requiring harmonization
- Migration paths for standardization

---

## 2. Repository Inventory

### 2.1 Jekyll Websites Identified

| Organization | Repository | Type | Workflows | Status |
|--------------|-----------|------|-----------|--------|
| BrightSoftwares | eagles-techs.com | Blog | 19 | Mature |
| BrightSoftwares | ieatmyhealth.com | Blog + E-commerce | 17 | Mature |
| BrightSoftwares | keke.li | Blog | 5 | Basic |
| BrightSoftwares | olympics-paris2024.com | News/Events | 19 | Mature |
| BrightSoftwares | foolywise.com | Blog | 5 | Basic |
| BrightSoftwares | joyousbyflora-posts | E-commerce | 9 | Specialized |
| sergioafanou | blog | Personal Blog | 0 | Legacy |
| Causting | causting.com | Blog | 4 | Basic |
| Causting | space-up-planet.com | Blog | 5 | Basic |
| Hayes-Tech | hayestech-website | Corporate | 0 | Legacy |

---

## 3. Feature Matrix

### 3.1 Workflows & Automation Features

| Feature | blogpost-tools Reusable | eagles-techs | ieatmyhealth | olympics-paris | keke.li | foolywise | joyousbyflora | causting | space-up-planet | sergioafanou/blog | hayestech |
|---------|------------------------|--------------|--------------|----------------|---------|-----------|---------------|----------|-----------------|-------------------|-----------|
| **Internal Linking** | reusable-auto-internal-linking.yml | YES | YES | YES | YES | YES | YES | YES | YES | NO | NO |
| **Keyword Suggestion** | reusable_keywordsuggestionandytvidsposts.yml | YES | YES | YES | YES | YES | YES | YES | YES | NO | NO |
| **Auto Move & Publish** | reusable-automoveandpublish-posts.yml | YES | YES | YES | YES | YES | NO | NO | YES | NO | NO |
| **OpenAI Generation** | reusable_openaigenerateblogpost.yml | YES | YES | YES | YES | YES | YES | YES | YES | NO | NO |
| **Indexation Issues** | reusable_indexation-issues.yml | YES | NO | NO | NO | NO | NO | NO | NO | NO | NO |
| **Commit Generated Files** | reusable_commit-generated-files.yml | - | - | - | - | - | - | - | - | - | - |
| **Featured Image Finder** | (NOT REUSABLE YET) | YES | YES | YES | NO | NO | NO | NO | NO | NO | NO |
| **Post Summarizer** | post_summarizer.yml (not reusable) | YES | NO | YES | NO | NO | NO | NO | NO | NO | NO |
| **Translate Posts** | translate-blogpost.yml (not reusable) | YES | YES | YES | NO | NO | NO | NO | NO | NO | NO |
| **SEO Diagnostics** | seo-analysis.yml (not reusable) | YES | YES | YES | NO | NO | YES | NO | NO | NO | NO |
| **RSS to Blogpost** | news-to-blogpost.yml (not reusable) | YES | YES | YES | NO | NO | YES | NO | NO | NO | NO |
| **YouTube Transcription** | (IN REUSABLE) | YES | YES | YES | NO | NO | NO | NO | NO | NO | NO |
| **Semantic Clustering** | (NOT REUSABLE YET) | YES | YES | YES | NO | NO | NO | NO | NO | NO | NO |
| **Generate Aliases** | (NOT REUSABLE YET) | YES | YES | YES | NO | NO | NO | NO | NO | NO | NO |
| **Algolia Search** | (NOT REUSABLE YET) | YES | YES | YES | YES | YES | NO | YES | YES | NO | NO |

### 3.2 i18n / Internationalization

| Repository | Has i18n | Method | Languages | Folder Structure |
|------------|----------|--------|-----------|------------------|
| eagles-techs.com | Partial | Collection-based | en, fr | `_authors/{lang}`, `_products/{lang}` |
| ieatmyhealth.com | YES | `_i18n` folder | de, en, es, fr | `_i18n/{lang}.yml` |
| keke.li | YES | `_i18n` folder | de, en, es, fr | `_i18n/{lang}.yml` |
| olympics-paris2024.com | YES | Post folders | de, en, es, fr, it, pt | `_posts/{lang}/` |
| foolywise.com | NO | - | - | - |
| joyousbyflora-posts | YES | `_i18n` folder | de, en, es, fr | `_i18n/{lang}.yml` |
| causting.com | NO | - | - | - |
| space-up-planet.com | YES | `_i18n` folder | de, en, es, fr | `_i18n/{lang}.yml` |
| sergioafanou/blog | NO | - | - | - |
| hayestech-website | NO | - | - | - |

### 3.3 E-commerce Features

| Repository | Has E-commerce | Products Collection | Stripe | WooCommerce | Cloudinary |
|------------|---------------|---------------------|--------|-------------|------------|
| eagles-techs.com | YES | `_products/{lang}` | NO | NO | NO |
| ieatmyhealth.com | YES | `_products` | NO | NO | YES |
| joyousbyflora-posts | YES | `_products` | YES | YES (migrated) | YES |
| Others | NO | - | - | - | - |

### 3.4 SEO & Search Features

| Repository | Sitemap | SEO Tag | Algolia | SEO Workflows | Google Analytics |
|------------|---------|---------|---------|---------------|------------------|
| eagles-techs.com | YES | YES | YES | YES | - |
| ieatmyhealth.com | YES | YES | YES | YES | - |
| olympics-paris2024.com | YES | YES | YES | YES | - |
| keke.li | YES | YES | YES | NO | - |
| foolywise.com | YES | YES | YES | NO | - |
| joyousbyflora-posts | YES | YES | NO | YES | - |
| causting.com | YES | YES | YES | NO | - |
| space-up-planet.com | YES | YES | YES | NO | - |
| sergioafanou/blog | YES | YES | NO | NO | YES |
| hayestech-website | NO | NO | NO | NO | NO |

---

## 4. Reusable Workflows Status in blogpost-tools

### 4.1 Existing Reusable Workflows (Ready to Deploy)

| Workflow File | Purpose | Deployed To |
|---------------|---------|-------------|
| `reusable-auto-internal-linking.yml` | Internal linking automation | 8 repos |
| `reusable-automoveandpublish-posts.yml` | Post pipeline automation | 5 repos |
| `reusable_commit-generated-files.yml` | Commit automation | Used internally |
| `reusable_indexation-issues.yml` | SEO indexation fixes | 1 repo |
| `reusable_keywordsuggestionandytvidsposts.yml` | Keyword research + YouTube | 8 repos |
| `reusable_openaigenerateblogpost.yml` | AI content generation | 8 repos |

### 4.2 Workflows NOT YET Reusable (Need Migration to blogpost-tools)

| Feature | Current Location | Migration Priority | Complexity |
|---------|------------------|-------------------|------------|
| Featured Image Finder | eagles-techs, ieatmyhealth, olympics | HIGH | Medium |
| Post Summarizer | eagles-techs, olympics | MEDIUM | Low |
| Translation | eagles-techs, ieatmyhealth, olympics | HIGH | Medium |
| SEO Diagnostics | eagles-techs, ieatmyhealth, olympics, joyousbyflora | HIGH | Medium |
| RSS News to Blogpost | eagles-techs, ieatmyhealth, olympics, joyousbyflora | HIGH | Low |
| Semantic Clustering | eagles-techs, ieatmyhealth, olympics | LOW | High |
| Generate Aliases | eagles-techs, ieatmyhealth, olympics | MEDIUM | Low |
| Algolia Indexing | Multiple repos | MEDIUM | Medium |
| Google Autocomplete | joyousbyflora | LOW | Low |
| Improve Blogpost Files | joyousbyflora | LOW | Low |
| Matrix Internal Linking | olympics-paris2024 | LOW | Medium |
| Game Scheduling | olympics-paris2024 | LOW | Specialized |

---

## 5. Folder Structure Harmonization

### 5.1 Standard Folder Structure (Target)

```
/_data/
  ├── affiliate_links.csv
  ├── authors.yml
  ├── menus.yml
  ├── translations.yml
  └── [feature-specific data files]

/_drafts/
  ├── 100_keyword_suggestions/
  ├── 200_rss_inspired_posts/
  ├── 300_generated_raw_content/
  ├── 400_refined_content/
  ├── 500_featured_image_generated/
  ├── 501_beautified_content/
  ├── 600_auto_scheduled/
  ├── keywords.csv
  ├── keyword_suggestions.csv
  ├── youtube_search_results.csv
  └── youtube_videos_used.csv

/_i18n/
  ├── de.yml
  ├── en.yml
  ├── es.yml
  └── fr.yml

/_includes/
  └── [partial templates]

/_layouts/
  └── [page layouts]

/_pages/
  └── [static pages]

/_posts/
  ├── en/
  ├── fr/
  ├── de/
  └── es/

/_products/          # If e-commerce enabled
  ├── en/
  ├── fr/
  └── [other langs]

/_seo/
  ├── internal-linking/
  │   ├── aliases.yml
  │   ├── aliases.csv
  │   └── anchor_text_to_post.csv
  ├── keyword-generation/
  │   └── [keyword files]
  └── jekyll-filename-pretifier/
      ├── silot_term_to_links.csv
      └── silot_term_to_categories.csv

/_system/
  └── [system configuration files]

/assets/
  ├── css/
  ├── js/
  └── images/
```

### 5.2 Current Structure vs Target

| Repository | Missing Folders | Structure Issues |
|------------|-----------------|------------------|
| eagles-techs.com | `_data`, `_pages` | Products by lang OK, posts not by lang |
| ieatmyhealth.com | Posts not by lang | Uses `_i18n` folder |
| keke.li | `_data`, `_includes` | Minimal structure |
| olympics-paris2024.com | - | Good structure with lang posts |
| foolywise.com | Most folders | Very minimal |
| joyousbyflora-posts | - | Good but different naming |
| causting.com | Most folders | Very minimal |
| space-up-planet.com | `_data`, `_includes` | Minimal |
| sergioafanou/blog | `_data`, `_seo`, `_system`, `_drafts` | Legacy structure |
| hayestech-website | `_seo`, `_system`, `_drafts`, `_i18n` | Legacy structure |

---

## 6. Migration Plan by Feature

### 6.1 Phase 1: Deploy Existing Reusable Workflows (Immediate)

**Target Repos:** sergioafanou/blog, hayestech-website, joyousbyflora-posts (partial)

| Task | Repos Affected | Effort |
|------|---------------|--------|
| Deploy internal linking workflow | 2 (sergioafanou, hayestech) | Low |
| Deploy keyword suggestion workflow | 2 (sergioafanou, hayestech) | Low |
| Deploy OpenAI generation workflow | 2 (sergioafanou, hayestech) | Low |
| Deploy auto move & publish workflow | 3 (joyousbyflora, causting) | Medium |
| Deploy indexation issues workflow | 9 (all except eagles-techs) | Low |

**Pre-requisites for each repo:**
1. Create `_drafts/` folder structure
2. Create `_seo/` folder structure
3. Add required secrets to repo settings
4. Create/update `_config.yml` with required plugins

### 6.2 Phase 2: Create New Reusable Workflows (1-2 weeks)

| Workflow | Source Repo | Priority |
|----------|------------|----------|
| `reusable_featured-image-finder.yml` | eagles-techs.com | HIGH |
| `reusable_translate-posts.yml` | eagles-techs.com | HIGH |
| `reusable_seo-diagnostics.yml` | eagles-techs.com | HIGH |
| `reusable_rss-news-to-blogpost.yml` | eagles-techs.com | HIGH |
| `reusable_post-summarizer.yml` | eagles-techs.com | MEDIUM |
| `reusable_generate-aliases.yml` | eagles-techs.com | MEDIUM |
| `reusable_algolia-indexing.yml` | Multiple | MEDIUM |
| `reusable_semantic-clustering.yml` | eagles-techs.com | LOW |

### 6.3 Phase 3: Folder Structure Standardization

**For each repo without proper structure:**

```bash
# Create standard folder structure
mkdir -p _data _drafts/{100_keyword_suggestions,200_rss_inspired_posts,300_generated_raw_content,400_refined_content,500_featured_image_generated,501_beautified_content,600_auto_scheduled}
mkdir -p _i18n _pages _seo/{internal-linking,keyword-generation,jekyll-filename-pretifier} _system
mkdir -p _posts/{en,fr,de,es}
```

### 6.4 Phase 4: i18n Standardization

**Recommended Approach: Hybrid**
- Use `_i18n/` folder for UI translations (labels, menus)
- Use `_posts/{lang}/` for post organization
- Use `_products/{lang}/` for product organization (if applicable)

**Migration Steps:**
1. Create `_i18n/{lang}.yml` files with UI translations
2. Reorganize posts into language folders
3. Update `_config.yml` with language settings
4. Update layouts to use i18n includes

### 6.5 Phase 5: E-commerce Standardization

**For repos needing e-commerce (ready to activate):**

1. Create `_products/` collection folder
2. Add product layout (`_layouts/product.html`)
3. Add `_data/stripe_products.json` (empty placeholder)
4. Add Stripe/payment includes (disabled by default)
5. Configure in `_config.yml`:
   ```yaml
   collections:
     products:
       output: true
       permalink: /products/:path/
   ecommerce:
     enabled: false  # Toggle when ready
     provider: stripe
   ```

---

## 7. Secrets & Configuration Required

### 7.1 Required Secrets for Full Feature Set

| Secret | Used By | Required For |
|--------|---------|--------------|
| `CHECK_RUNNER_ACCESS_TOKEN` | All workflows | Self-hosted runner selection |
| `UNSPLASH_ACCESS_KEY` | Featured image finder | Image sourcing |
| `CLOUDINARY_URL` | Image optimization | Image CDN |
| `YOUTUBE_API_KEY` | YouTube finder | Video transcription |
| `OPENAI_API_KEY` | AI generation | Content generation |
| `ALGOLIA_API_KEY` | Search indexing | Algolia search |
| `ALGOLIA_APP_ID` | Search indexing | Algolia search |
| `STRIPE_SECRET_KEY` | E-commerce | Payments |
| `STRIPE_PUBLISHABLE_KEY` | E-commerce | Payments |

### 7.2 Configuration Template

Add to each repo's `_config.yml`:

```yaml
# Feature flags
features:
  i18n:
    enabled: true
    languages: [en, fr, de, es]
    default_lang: en
  ecommerce:
    enabled: false
    provider: stripe
  seo:
    algolia: true
    sitemap: true
    seo_tag: true
  automation:
    internal_linking: true
    keyword_generation: true
    ai_generation: true
    featured_image: true
    post_summarizer: true
    translation: true
```

---

## 8. Action Items Summary

### Immediate (This Week)
- [ ] Deploy existing reusable workflows to sergioafanou/blog
- [ ] Deploy existing reusable workflows to hayestech-website
- [ ] Create folder structure templates
- [ ] Document required secrets

### Short-term (Next 2 Weeks)
- [ ] Create `reusable_featured-image-finder.yml`
- [ ] Create `reusable_translate-posts.yml`
- [ ] Create `reusable_seo-diagnostics.yml`
- [ ] Create `reusable_rss-news-to-blogpost.yml`

### Medium-term (1 Month)
- [ ] Standardize folder structure across all repos
- [ ] Implement i18n in repos without it
- [ ] Create e-commerce readiness template
- [ ] Create post-summarizer reusable workflow
- [ ] Create generate-aliases reusable workflow

### Long-term
- [ ] Migrate all individual workflows to call reusable workflows
- [ ] Remove duplicate code from individual repos
- [ ] Create documentation for each reusable workflow
- [ ] Set up automated testing for workflows

---

## 9. Feature Deployment Quick Reference

### For NEW Jekyll websites, deploy these workflows:

```yaml
# .github/workflows/auto-internal_linking.yml
name: Auto Internal Linking
on:
  workflow_dispatch:
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday
jobs:
  internal-linking:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable-auto-internal-linking.yml@main
    with:
      internallinking_src_folder_toscan: /github/workspace/_posts/
      internallinking_dst_folder_tosaveresults: /github/workspace/_seo/internal-linking/
      internallinking_internal_link_text_file: internal_link_text.csv
      internallinking_anchor_text_to_post: anchor_text_to_post.csv
      internallinking_aliases_yml_file: /github/workspace/_seo/internal-linking/aliases.yml
      internallinking_aliases_csv_file: /github/workspace/_seo/internal-linking/aliases.csv
      internallinking_aliases_new_csv_file: /github/workspace/_seo/internal-linking/aliases_new.csv
      internallinking_dry_run: false
      internallinking_lang: en
      markdownlinting_folder_to_lint: /github/workspace/_posts/
      github_repo_owner: ${{ github.repository_owner }}
      github_repository: ${{ github.repository }}
    secrets: inherit
```

---

## 10. Repository-Specific Migration Notes

### sergioafanou/blog
- **Theme:** Mediumish (different from others)
- **Priority:** Create basic automation structure
- **Actions:**
  - Add `_drafts/`, `_seo/`, `_system/` folders
  - Deploy 4 core reusable workflows
  - Consider theme migration if standardization needed

### hayestech-website
- **Theme:** Custom corporate
- **Priority:** Create basic automation structure
- **Actions:**
  - Add `_drafts/`, `_seo/`, `_system/` folders
  - Add Jekyll plugins (sitemap, seo-tag)
  - Deploy 4 core reusable workflows

### joyousbyflora-posts
- **Status:** Most advanced e-commerce
- **Priority:** Document e-commerce patterns for other repos
- **Actions:**
  - Add missing reusable workflow calls
  - Document WooCommerce migration process
  - Document Stripe integration pattern

### foolywise.com, causting.com
- **Status:** Minimal structure
- **Priority:** Full structure deployment
- **Actions:**
  - Create complete folder structure
  - Deploy all reusable workflows
  - Add i18n support

---

*Document generated by audit process on 2025-11-23*
