# Jekyll Sites Analysis Summary

**Analysis Date:** 2025-11-23
**Total Repositories Analyzed:** 12

---

## Quick Reference Matrix

| Repository | Theme | i18n | Algolia | Responsive Images | E-commerce | Deployment |
|------------|-------|------|---------|-------------------|------------|------------|
| BrightSoftwares/corporate-website | Custom (flexstart) | en/fr folders | Yes | Yes | No | github-pages |
| BrightSoftwares/foolywise.com | minima | No | Yes | No | No | jekyll.yml |
| BrightSoftwares/ieatmyhealth.com | minima | yml (4 langs) | Yes | No | Products | jekyll.yml |
| BrightSoftwares/joyousbyflora-posts | minima (biolife) | yml (4 langs) | Yes | No | Full | netlify |
| BrightSoftwares/keke.li | minima | yml (4 langs) | Yes | No | No | jekyll.yml |
| BrightSoftwares/modabyflora-corporate | Custom (belle) | No (FR only) | Yes | No | Full | netlify |
| BrightSoftwares/olympics-paris2024.com | minima (magz) | folder (6 langs) | Yes | No | No | jekyll.yml |
| Causting/causting.com | minima | No | Yes | No | No | jekyll.yml |
| Causting/space-up-planet.com | minima | yml (4 langs) | Yes | No | No | jekyll.yml |
| sergioafanou/smart-cv | Custom (ceramic) | No | Yes | No | No | github-pages |
| sergioafanou/blog | mediumish | No | No | No | No | manual |
| BrightSoftwares/eagles-techs.com | minima | No | Yes | No | Products | github-pages |

---

## Feature Distribution

### Multi-Language Support (i18n)

**Folder-based (en/_posts, fr/_posts):**
- BrightSoftwares/corporate-website (2 languages: en, fr)

**YML-based (_i18n/*.yml):**
- BrightSoftwares/ieatmyhealth.com (4 languages: en, fr, de, es)
- BrightSoftwares/joyousbyflora-posts (4 languages: en, fr, de, es)
- BrightSoftwares/keke.li (4 languages: en, fr, de, es)
- Causting/space-up-planet.com (4 languages: en, fr, de, es)

**Folder-based Multi-Language (_posts/en, _posts/fr, etc.):**
- BrightSoftwares/olympics-paris2024.com (6 languages: en, fr, de, es, pt, it)

**No i18n:**
- BrightSoftwares/foolywise.com
- BrightSoftwares/modabyflora-corporate (French only)
- Causting/causting.com
- sergioafanou/smart-cv
- sergioafanou/blog
- BrightSoftwares/eagles-techs.com

---

### Algolia Search Configuration

| Repository | App ID | Index Name |
|------------|--------|------------|
| corporate-website | A9C0HJSAZ0 | jekyll_website |
| foolywise.com | B11B73255V | jekyll_website |
| ieatmyhealth.com | BBHI3TOVYE | jekyll_website |
| joyousbyflora-posts | 5964G05HW3 | jekyll_website |
| keke.li | 2KWKJB7VZ9 | jekyll_website |
| modabyflora-corporate | WAKWLQMATN | jekyll_website |
| olympics-paris2024.com | MZ6T4W5WF8 | jekyll_website |
| causting.com | ELY34M5A3O | jekyll_website |
| space-up-planet.com | 08VCDQYLDB | jekyll_website |
| smart-cv | 0XXRLGPNEB | jekyll_website |
| eagles-techs.com | H4TXZVGN1Z | jekyll_eaglestechs_website |
| sergioafanou/blog | **Not configured** | - |

---

### E-commerce & Products

**Full E-commerce (Cart, Checkout, Payments):**
- **BrightSoftwares/joyousbyflora-posts**
  - Stripe payments
  - Commerce Layer integration
  - Cloudinary images
  - WooCommerce migration support
  - Cart, checkout, wishlist, orders pages

- **BrightSoftwares/modabyflora-corporate**
  - Stripe LIVE payments
  - Cloudinary images
  - Mautic newsletter
  - FreeScout support
  - Belle theme

**Product Collections Only:**
- BrightSoftwares/ieatmyhealth.com (_products, with Contentful)
- BrightSoftwares/eagles-techs.com (_products, _authors, _study)

---

### Responsive Images

Only **BrightSoftwares/corporate-website** has responsive images configured:
- Plugin: jekyll-responsive-image
- Sizes: 480, 800, 856, 1400px (plus various aspect ratios)
- Also uses: jekyll-minimagick, mini_magick, rmagick, image_optim

---

### Cloudinary Integration

| Repository | Cloud Name |
|------------|------------|
| joyousbyflora-posts | dwys8su2w |
| modabyflora-corporate | modabyflora |

---

### Contentful CMS

| Repository | Space ID |
|------------|----------|
| ieatmyhealth.com | 6cpp5r1yippa |
| modabyflora-corporate | (in Gemfile, not configured in _config.yml) |

---

## Plugin Usage Across Sites

### Universal Plugins (all sites)
- jekyll-sitemap
- jekyll-feed
- jekyll-seo-tag
- jekyll-archives

### Very Common Plugins (10+ sites)
- jekyll-algolia
- jekyll-wikilinks
- jekyll-redirect-from
- jekyll-last-modified-at
- jekyll-timeago
- jekyll-paginate-v2

### Common Plugins (5+ sites)
- jekyll-toc

### Specialized Plugins
- jekyll-responsive-image (1 site)
- jekyll-minimagick (1 site)
- jekyll-contentful-data-import (2 sites)
- jekyll-admin (1 site)

---

## Workflow Distribution

### Core Workflows (present in most sites)

| Workflow | Purpose | Sites |
|----------|---------|-------|
| auto-internal_linking.yml | Internal linking automation | 11 |
| auto-keywordandyoutubegen-posts.yml | Keyword & YouTube generation | 11 |
| auto-openaigenerateblogpost.yml | OpenAI blog post generation | 11 |
| seo_diagnotics.yml | SEO diagnostics | 10 |
| jekyll.yml / github-pages.yml | Deployment | 11 |

### Advanced Workflows (selective sites)

| Workflow | Purpose | Sites Count |
|----------|---------|-------------|
| auto-schedule-posts.yml | Post scheduling | 6 |
| featured-image-finder.yml | Image automation | 6 |
| keyword_suggestion.yml | Keyword suggestions | 7 |
| post-summarizer.yml | Post summarization | 5 |
| yt_vids_and_transcribe.yml | YouTube video transcription | 7 |
| translate_posts.yml | Translation | 5 |
| semantic_clustering.yml | Content clustering | 6 |
| rss-news-to-blogpost.yml | RSS to blog conversion | 8 |

---

## Directory Structure Comparison

### Standard Directories

| Directory | corporate | foolywise | ieatmyhealth | joyousbyflora | keke.li | modabyflora | olympics | causting | space-up | smart-cv | blog | eagles |
|-----------|-----------|-----------|--------------|---------------|---------|-------------|----------|----------|----------|----------|------|--------|
| _posts | No* | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| en/_posts | Yes | No | No | No | No | No | No | No | No | No | No | No |
| fr/_posts | Yes | No | No | No | No | No | No | No | No | No | No | No |
| _drafts | No | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Yes |
| _pages | Yes | No | Yes | No | Yes | Yes | Yes | No | No | Yes | Yes | No |
| _includes | Yes | No | Yes | Yes | No | Yes | Yes | No | No | Yes | Yes | Yes |
| _layouts | Yes | No | Yes | Yes | Yes | Yes | Yes | No | Yes | Yes | Yes | Yes |
| _data | Yes | No | Yes | Yes | No | Yes | Yes | No | No | Yes | No | No |
| _sass | Yes | No | No | No | No | No | No | No | No | Yes | Yes | No |
| _plugins | Yes | No | No | Yes | No | No | No | No | No | No | No | No |
| _seo | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Yes |
| _system | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Yes |
| assets | Yes | No | Yes | Yes | Yes | Yes | Yes | No | Yes | Yes | Yes | Yes |
| _products | No | No | Yes | Yes | No | Yes | No | No | No | No | No | Yes |
| _i18n | No | No | Yes | Yes | Yes | No | No | No | Yes | No | No | No |

*corporate-website uses en/_posts and fr/_posts instead

---

## Standardization Recommendations

### High Priority

1. **Standardize Jekyll Version**
   - Current: Mix of `~> 4.2` and `~> 4.2.2`
   - Recommended: `~> 4.2.2` for all sites

2. **Add Ruby 3.4+ Compatibility Gems**
   - Add to ALL Gemfiles:
   ```ruby
   gem "csv"
   gem "logger"
   gem "base64"
   gem "bigdecimal"
   ```
   - Currently missing from: foolywise, ieatmyhealth, keke.li, olympics, causting, space-up-planet, blog, eagles-techs

3. **Standardize Plugin Versions**
   - jekyll-sitemap: `~> 1.4.0`
   - jekyll-feed: `~> 0.16.0`
   - jekyll-seo-tag: `~> 2.7.1`
   - jekyll-archives: `~> 2.2.1`
   - jekyll-wikilinks: `~> 0.0.8`
   - jekyll-redirect-from: `~> 0.16.0`

### Medium Priority

4. **Add _seo and _system folders to sergioafanou/blog**
   - Only site missing these standard folders

5. **Add Algolia to sergioafanou/blog**
   - Only site without search capability

6. **Standardize i18n approach**
   - Document when to use folder-based vs yml-based
   - Consider consolidating to one approach

### Low Priority

7. **Add responsive images to image-heavy sites**
   - Consider for: ieatmyhealth, joyousbyflora, modabyflora

8. **Standardize deployment workflows**
   - Create reusable workflow that all sites can reference

---

## Site Categories

### Blogs (Simple content sites)
- BrightSoftwares/foolywise.com
- BrightSoftwares/keke.li
- Causting/causting.com
- Causting/space-up-planet.com
- sergioafanou/blog

### Corporate/Portfolio Sites
- BrightSoftwares/corporate-website
- BrightSoftwares/eagles-techs.com
- sergioafanou/smart-cv

### E-commerce Sites
- BrightSoftwares/joyousbyflora-posts (Full)
- BrightSoftwares/modabyflora-corporate (Full)
- BrightSoftwares/ieatmyhealth.com (Products)

### Specialty Sites
- BrightSoftwares/olympics-paris2024.com (Sports/Events)

---

## Files Generated

1. `/home/user/blogpost-tools/jekyll-sites-analysis.json` - Complete JSON analysis
2. `/home/user/blogpost-tools/jekyll-sites-analysis-summary.md` - This summary document
