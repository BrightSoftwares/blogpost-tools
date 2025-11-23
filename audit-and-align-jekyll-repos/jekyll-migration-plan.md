# Jekyll Sites Migration & Standardization Plan

**Generated:** 2025-11-23
**Total Sites:** 12
**Total blogpost-tools Actions:** 24
**Total Reusable Workflows:** 7

---

## Part 1: Available Tools in blogpost-tools

### Reusable Workflows

| Workflow | Purpose | Used By Sites |
|----------|---------|---------------|
| `reusable_jekyll_build_and_deploy.yml` | Jekyll build + Netlify deploy | **NEW - Not deployed yet** |
| `reusable_openaigenerateblogpost.yml` | OpenAI blog post generation | 11 sites |
| `reusable_keywordsuggestionandytvidsposts.yml` | Keywords + YouTube videos | 11 sites |
| `reusable-auto-internal-linking.yml` | Internal linking automation | 11 sites |
| `reusable-automoveandpublish-posts.yml` | Move drafts to posts | 6 sites |
| `reusable_commit-generated-files.yml` | Commit generated files | 10 sites |
| `reusable_indexation-issues.yml` | SEO indexation diagnostics | 10 sites |

### Available Actions

| Action | Purpose | Deployment Status |
|--------|---------|-------------------|
| `jekyll-action` | Build Jekyll sites | ✅ Deployed to all |
| `action-netlify-deploy` | Deploy to Netlify | ✅ Deployed to all |
| `openai-generate-blogpost` | Generate posts with AI | ✅ Deployed |
| `keyword-suggestion` | Google keyword suggestions | ✅ Deployed |
| `youtube-vid-finder` | Find relevant YouTube videos | ✅ Deployed |
| `transcript-downloader` | Download YouTube transcripts | ✅ Deployed |
| `internal-linking` | Generate internal links | ✅ Deployed |
| `generate-aliases-file` | Create aliases.csv | ✅ Deployed |
| `translate-blogpost` | Translate posts | ⚠️ Partial (5 sites) |
| `post-summarizer` | Summarize posts | ⚠️ Partial (5 sites) |
| `auto-schedule-posts` | Schedule post publishing | ⚠️ Partial (6 sites) |
| `auto-move-to-destination` | Move posts when ready | ⚠️ Partial (6 sites) |
| `unsplash-to-cloudinary` | Find & upload images | ⚠️ Partial (6 sites) |
| `seo-analysis` | SEO analysis | ⚠️ Partial |
| `indexation-issues` | Fix indexation problems | ⚠️ Partial |
| `jekyll-filename-pretifier` | Standardize filenames | ❌ Not deployed |
| `blogpost-candidates-generation` | Generate post candidates | ❌ Not deployed |
| `suggestions-to-blogpost` | Convert keywords to posts | ❌ Not deployed |
| `news-to-blogpost` | Convert RSS to posts | ⚠️ Partial (8 sites) |
| `bloginspritation-converter` | Convert inspiration content | ❌ Not deployed |
| `rosaenlg-post-generator` | NLG post generation | ❌ Not deployed |
| `google-autocomplete` | Harvest autocomplete | ❌ Not deployed |
| `markdown-linting` | Lint markdown files | ❌ Not deployed |
| `check-runner` | Check runner availability | ❌ Not deployed |

---

## Part 2: Feature Matrix by Site

### Core Features

| Feature | corporate | foolywise | ieatmyhealth | joyousbyflora | keke.li | modabyflora | olympics | causting | space-up | smart-cv | blog | eagles |
|---------|-----------|-----------|--------------|---------------|---------|-------------|----------|----------|----------|----------|------|--------|
| Jekyll 4.2.2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ruby 3.4 gems | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Algolia Search | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| ffi pinned | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |

### Content Features

| Feature | corporate | foolywise | ieatmyhealth | joyousbyflora | keke.li | modabyflora | olympics | causting | space-up | smart-cv | blog | eagles |
|---------|-----------|-----------|--------------|---------------|---------|-------------|----------|----------|----------|----------|------|--------|
| Multi-language | ✅ en/fr | ❌ | ✅ 4 lang | ✅ 4 lang | ✅ 4 lang | ❌ FR | ✅ 6 lang | ❌ | ✅ 4 lang | ❌ | ❌ | ❌ |
| Responsive Images | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| TOC | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| Wikilinks | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Redirects | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |

### E-commerce Features

| Feature | corporate | foolywise | ieatmyhealth | joyousbyflora | keke.li | modabyflora | olympics | causting | space-up | smart-cv | blog | eagles |
|---------|-----------|-----------|--------------|---------------|---------|-------------|----------|----------|----------|----------|------|--------|
| Products | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Cart/Checkout | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Stripe | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Cloudinary | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Contentful | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### Automation Workflows

| Workflow | corporate | foolywise | ieatmyhealth | joyousbyflora | keke.li | modabyflora | olympics | causting | space-up | smart-cv | blog | eagles |
|----------|-----------|-----------|--------------|---------------|---------|-------------|----------|----------|----------|----------|------|--------|
| OpenAI Generate | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Internal Linking | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Keyword/YouTube | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| SEO Diagnostics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Translation | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Post Scheduling | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Image Finder | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| RSS to Blog | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## Part 3: Harmonized Folder Structure

### Standard Folder Structure (All Sites Should Have)

```
/
├── _config.yml                 # Main configuration
├── Gemfile                     # Dependencies (standardized)
├── Gemfile.lock                # Locked dependencies
│
├── _posts/                     # Blog posts (single-language sites)
│   └── YYYY-MM-DD-title.md
│
├── _drafts/                    # Draft posts
│   └── title.md
│
├── _pages/                     # Static pages
│   ├── about.md
│   ├── contact.md
│   └── privacy.md
│
├── _includes/                  # Reusable components
│   ├── common/                 # Shared includes (submodule)
│   ├── header.html
│   ├── footer.html
│   └── responsive-image.html
│
├── _layouts/                   # Page templates
│   ├── default.html
│   ├── post.html
│   └── page.html
│
├── _data/                      # Data files
│   ├── navigation.yml
│   ├── authors.yml
│   └── site.yml
│
├── _sass/                      # Stylesheets (optional)
│   └── main.scss
│
├── _plugins/                   # Custom plugins (optional)
│
├── assets/                     # Static assets
│   ├── css/
│   ├── js/
│   ├── images/
│   └── resized/                # Generated responsive images
│
├── _seo/                       # SEO configuration
│   ├── internal-linking/
│   │   └── aliases.csv
│   ├── keywords/
│   └── jekyll-filename-pretifier/
│
├── _system/                    # System/automation files
│   ├── candidates/
│   ├── suggestions/
│   └── scheduled/
│
└── .github/
    └── workflows/
        ├── jekyll.yml          # Main deployment
        ├── seo_diagnostics.yml
        ├── auto-internal_linking.yml
        ├── auto-openaigenerateblogpost.yml
        └── auto-keywordandyoutubegen-posts.yml
```

### Multi-Language Structure (Option A: Folder-based)

```
/
├── en/
│   ├── _posts/
│   └── _drafts/
├── fr/
│   ├── _posts/
│   └── _drafts/
├── de/                         # Optional
│   ├── _posts/
│   └── _drafts/
└── es/                         # Optional
    ├── _posts/
    └── _drafts/
```

### Multi-Language Structure (Option B: YML-based)

```
/
├── _posts/                     # All posts
├── _i18n/
│   ├── en.yml
│   ├── fr.yml
│   ├── de.yml
│   └── es.yml
└── _config.yml                 # Configure languages
```

### E-commerce Structure (Optional)

```
/
├── _products/                  # Product collection
│   ├── en/
│   │   └── product-name.md
│   └── fr/
│       └── product-name.md
├── _categories/                # Product categories
├── cart.html
├── checkout.html
├── wishlist.html
└── orders.html
```

---

## Part 4: Migration Plan by Priority

### Phase 1: Critical (Week 1)

#### 1.1 Add Ruby 3.4 Compatibility to All Sites
**Sites needing update:** foolywise, ieatmyhealth, keke.li, olympics, causting, space-up-planet, blog, eagles-techs

**Add to Gemfile:**
```ruby
# Required for Ruby 3.4+
gem "csv"
gem "logger"
gem "base64"
gem "bigdecimal"
gem "observer"
gem "ostruct"
```

#### 1.2 Standardize Jekyll Version
**Change in all Gemfiles:**
```ruby
gem 'jekyll', '~> 4.2.2'
```

#### 1.3 Pin ffi gem
**Add to sites missing it:**
```ruby
gem 'ffi', '= 1.16.3'
```

---

### Phase 2: Standardization (Week 2)

#### 2.1 Add Missing Standard Folders

| Site | Missing Folders |
|------|-----------------|
| foolywise.com | _includes, _layouts, _data, _pages, assets |
| causting.com | _includes, _layouts, _data, _pages, assets |
| sergioafanou/blog | _seo, _system, _drafts |

#### 2.2 Add Algolia to sergioafanou/blog

**Add to Gemfile:**
```ruby
gem 'jekyll-algolia', '~> 1.7.1'
```

**Add to _config.yml:**
```yaml
algolia:
  application_id: 'YOUR_APP_ID'
  index_name: 'jekyll_blog'
  search_only_api_key: 'YOUR_SEARCH_KEY'

plugins:
  - jekyll-algolia
```

#### 2.3 Deploy Missing Workflows

| Workflow | Deploy To |
|----------|-----------|
| seo_diagnostics.yml | eagles-techs |
| All automation workflows | sergioafanou/blog |
| translation workflow | corporate, modabyflora, causting, smart-cv |
| post scheduling | corporate, modabyflora, causting, smart-cv |

---

### Phase 3: Feature Deployment (Week 3)

#### 3.1 Deploy Reusable Jekyll Workflow
**Update ALL sites to use:**
```yaml
jobs:
  build-deploy:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable_jekyll_build_and_deploy.yml@main
    with:
      build_dir: './build'
      deploy_to_netlify: true
    secrets:
      github_token: ${{ secrets.GITHUB_TOKEN }}
      submodule_ssh_key: ${{ secrets.SUBMODULE_SSH_PRIVATE_KEY }}
      algolia_api_key: ${{ secrets.ALGOLIA_API_KEY }}
      netlify_auth_token: ${{ secrets.NETLIFY_AUTH_TOKEN }}
      netlify_site_id: ${{ secrets.NETLIFY_SITE_ID }}
```

#### 3.2 Deploy jekyll-filename-pretifier
- Add to ALL sites (disabled by default)
- Create standardized config in _seo/jekyll-filename-pretifier/

#### 3.3 Add Responsive Images Capability
- Add jekyll-responsive-image to ALL Gemfiles (commented out)
- Add responsive_image config to ALL _config.yml (commented out)
- Sites can enable by uncommenting

---

### Phase 4: Advanced Features (Week 4)

#### 4.1 Standardize i18n Approach
**Recommended:** YML-based for new sites, folder-based for existing corporate-website

**Standard _config.yml for i18n:**
```yaml
# Multi-language support
languages: ["en", "fr"]
default_lang: "en"
exclude_from_localization: ["assets", "js", "css"]
parallel_localization: true
```

#### 4.2 E-commerce Template
- Create standard _products collection template
- Create cart/checkout page templates
- Document Stripe/Cloudinary integration

#### 4.3 Deploy Unused Actions
| Action | Purpose | Deploy To |
|--------|---------|-----------|
| markdown-linting | Quality check | All sites |
| blogpost-candidates-generation | Content ideation | All sites |
| google-autocomplete | Trend research | All sites |

---

## Part 5: Site-Specific Migration Notes

### BrightSoftwares/corporate-website
- **Status:** Most complete, reference implementation
- **Action:** Use as template for other sites
- **Unique:** Only site with responsive images - consider deploying to others

### BrightSoftwares/foolywise.com
- **Status:** Missing many standard folders
- **Action:** Add _includes, _layouts, _data, _pages, assets
- **Priority:** High

### sergioafanou/blog
- **Status:** Most outdated, missing many features
- **Action:** Full standardization needed
- **Missing:** _seo, _system, Algolia, all automation workflows
- **Priority:** High

### E-commerce Sites (joyousbyflora, modabyflora)
- **Status:** Feature-complete for e-commerce
- **Action:** Document and create reusable e-commerce template
- **Note:** Keep Stripe/Cloudinary configs site-specific

---

## Part 6: Execution Checklist

### Per-Site Checklist

```markdown
- [ ] Update Gemfile with Ruby 3.4 gems
- [ ] Standardize Jekyll version to 4.2.2
- [ ] Pin ffi to 1.16.3
- [ ] Standardize plugin versions
- [ ] Add missing standard folders (_seo, _system)
- [ ] Update to reusable Jekyll workflow
- [ ] Verify Algolia configuration
- [ ] Add common includes submodule
- [ ] Test build locally
- [ ] Test deployment
- [ ] Verify all workflows run successfully
```

### Automation Script

A bash script will be provided to automate the migration for each site. See `migrate-site.sh` in blogpost-tools.

---

## Summary Statistics

| Metric | Current | Target |
|--------|---------|--------|
| Sites with Ruby 3.4 gems | 4/12 | 12/12 |
| Sites with Algolia | 11/12 | 12/12 |
| Sites using reusable workflow | 0/12 | 12/12 |
| Sites with standard folder structure | 3/12 | 12/12 |
| Sites with all automation workflows | 2/12 | 12/12 |
