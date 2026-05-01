# Social Publishing Automation

Reusable GitHub Actions workflows for automated social post generation and publishing to LinkedIn and Facebook, driven by blog post frontmatter.

## Overview

Two reusable workflows in `BrightSoftwares/blogpost-tools`:

| Workflow | Trigger | Action |
|----------|---------|--------|
| `reusable_social-generate.yml` | Cron / manual | Picks next unscheduled blog post, composes LinkedIn + Facebook copy, generates a social card image via Smart Assets Manager, opens a PR with a draft YAML for review |
| `reusable_social-publish.yml` | PR merge / manual | Publishes all `status: approved` draft YAMLs to LinkedIn and Facebook, commits results back, updates `social-calendar.md` |

## Quick Start

### 1. Blog Post Frontmatter

Add these fields to any Jekyll post to make it eligible for social publishing:

```yaml
---
title: "Your Post Title"
excerpt: "One or two sentence summary shown in the social card body."
permalink: /en/your-post-slug/
tags: [gmail, productivity, automation]
auto_social: true               # required — must be true
social_stat: "74% fewer rules"  # optional — shown on stat-card template
pain_point: "Too many rules?"   # optional — overrides brand voice default
cta: "Try it free →"           # optional — overrides config default
---
```

### 2. Site Config (`_data/social_config.yml`)

```yaml
brand:
  name: "Bright Softwares"
  voice_url: ""                   # URL to brand voice document (optional)
  primary_color: "#0066CC"
  secondary_color: "#00CC66"
  accent_color: "#FF6600"

site_url: "https://bright-softwares.com"

defaults:
  pain_point: "Struggling with manual workflows?"
  cta: "Read the full guide →"
  hashtags:
    - brightsoftwares
    - productivity
    - automation
    - devtools
    - saas
```

### 3. Caller Workflows

Add both files to `BrightSoftwares/corporate-website/.github/workflows/`:

**`social-generate.yml`** — runs Mon & Thu at 07:00 UTC, opens a PR:

```yaml
name: Social Generate
on:
  schedule:
    - cron: "0 7 * * 1,4"
  workflow_dispatch:
    inputs:
      target_slug:
        description: "Specific slug to schedule (optional)"
        required: false
      dry_run:
        type: boolean
        default: false

jobs:
  generate:
    uses: brightsoftwares/blogpost-tools/.github/workflows/reusable_social-generate.yml@main
    with:
      posts_dir: "_posts/en/"
      drafts_dir: "_social_drafts/"
      schedule_path: "_data/social_schedule.yml"
      config_path: "_data/social_config.yml"
      target_slug: ${{ inputs.target_slug }}
      dry_run: ${{ inputs.dry_run || false }}
    secrets:
      SMART_ASSETS_API_KEY: ${{ secrets.SMART_ASSETS_API_KEY }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**`social-publish.yml`** — triggers on draft YAML changes + safety-net cron at 09:00 UTC:

```yaml
name: Social Publish
on:
  push:
    branches: [main]
    paths:
      - "_social_drafts/**"
  workflow_dispatch:
    inputs:
      dry_run:
        type: boolean
        default: false
  schedule:
    - cron: "0 9 * * 1,4"

jobs:
  publish:
    uses: brightsoftwares/blogpost-tools/.github/workflows/reusable_social-publish.yml@main
    with:
      drafts_dir: "_social_drafts/"
      published_dir: "_social_published/"
      schedule_path: "_data/social_schedule.yml"
      config_path: "_data/social_config.yml"
      dry_run: ${{ inputs.dry_run || false }}
    secrets:
      LINKEDIN_ACCESS_TOKEN: ${{ secrets.LINKEDIN_ACCESS_TOKEN }}
      LINKEDIN_ORG_URN: ${{ secrets.LINKEDIN_ORG_URN }}
      FACEBOOK_PAGE_ACCESS_TOKEN: ${{ secrets.FACEBOOK_PAGE_ACCESS_TOKEN }}
      FACEBOOK_PAGE_ID: ${{ secrets.FACEBOOK_PAGE_ID }}
```

### 4. GitHub Secrets

Set these at the **repository level** (GitHub Free does not support org-level secrets):

| Secret | Description |
|--------|-------------|
| `SMART_ASSETS_API_KEY` | Bearer token for Smart Assets Manager API |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn OAuth2 bearer token (`w_organization_social` scope) |
| `LINKEDIN_ORG_URN` | Organization URN, e.g. `urn:li:organization:12345678` |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Long-lived Facebook Page access token |
| `FACEBOOK_PAGE_ID` | Numeric Facebook Page ID |

> **Important:** Each brand's tokens must target **that brand's** LinkedIn company page and Facebook Page. Do not mix tokens across brands.

## Workflow

```
Monday/Thursday 07:00 UTC
  → social-generate.yml runs
  → select_next_post: picks oldest post with auto_social: true not yet scheduled
  → compose_post: generates LinkedIn (≤ 3000 chars) and Facebook (≤ 400-char excerpt) copy
  → sam_client: calls Smart Assets Manager deterministic endpoint for 1200×627 + 1200×1200 images
  → saves draft YAML to _social_drafts/YYYY-MM-DD-{slug}.yml (status: draft)
  → opens PR titled "social: schedule {slug} for YYYY-MM-DD"

You review and approve
  → edit draft YAML: change `status: draft` → `status: approved`
  → merge PR

Monday/Thursday 09:00 UTC (or on merge push)
  → social-publish.yml runs
  → finds all approved YAMLs in _social_drafts/
  → publishes to LinkedIn (3-step: initializeUpload → PUT image bytes → POST /rest/posts)
  → publishes to Facebook (2-step: POST /photos unpublished → POST /feed with attached_media)
  → moves file to _social_published/, updates social_schedule.yml
  → renders social-calendar.md
  → commits and pushes
```

## Post Copy Templates

Templates live in `scripts/social/templates/`:

- `linkedin.j2` — LinkedIn post (≤ 3000 chars total)
- `facebook.j2` — Facebook post (excerpt truncated at 400 chars)

Variables available in templates:

| Variable | Source |
|----------|--------|
| `pain_point` | Post frontmatter → brand_voice.default_pain_point → config.defaults.pain_point |
| `excerpt` | Post frontmatter `excerpt` → first non-empty body paragraph |
| `cta` | Post frontmatter → config.defaults.cta |
| `permalink` | Post frontmatter → `/{slug}/` |
| `hashtags` | Post frontmatter `tags` (lowercased) → config.defaults.hashtags |

## Social Card Image Styles

Set `image_style` in post frontmatter (or defaults to `quote-card`):

| Template ID | Best for |
|-------------|---------|
| `quote-card` | Posts with a memorable excerpt or insight |
| `stat-card` | Posts with a quantified result (requires `social_stat` field) |
| `question-hook` | Posts framed as a question or problem |

## Troubleshooting

**LinkedIn 401** — Token expired. Refresh via LinkedIn Developer Portal. Tokens last ~60 days.

**Facebook error 190** — Page access token expired. Refresh via Graph API Explorer with `pages_manage_posts` + `publish_pages` permissions.

**Facebook error 100** — Image URL not publicly reachable by Facebook servers. Ensure Cloudinary asset visibility is `public`.

**SAM image missing** — Set `SMART_ASSETS_API_KEY` secret. Run with `--dry-run` to skip image generation during testing.

## Running Tests

```bash
cd /path/to/blogpost-tools
pip install -r scripts/social/requirements.txt
pytest tests/social/ --cov=scripts/social --cov-fail-under=80
```

## File Layout

```
scripts/social/
├── requirements.txt
├── yaml_io.py             # YAML load/save helpers
├── select_next_post.py    # Pick next eligible post
├── brand_voice_fetcher.py # Fetch brand voice from remote URL
├── compose_post.py        # Render LinkedIn + Facebook copy
├── sam_client.py          # Smart Assets Manager API client
├── render_calendar.py     # Render social-calendar.md
├── generate_main.py       # Generate workflow entrypoint
├── publish_main.py        # Publish workflow entrypoint
└── templates/
    ├── linkedin.j2
    └── facebook.j2

.github/workflows/
├── reusable_social-generate.yml
└── reusable_social-publish.yml

tests/social/
├── fixtures/
│   ├── sample_post.md
│   ├── sample_schedule.yml
│   └── sample_config.yml
├── test_select_next_post.py
├── test_compose_post.py
├── test_render_calendar.py
├── test_linkedin_publish.py
└── test_facebook_publish.py

docs/
└── social-publishing.md   ← this file
```
