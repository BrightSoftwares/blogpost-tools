# Jekyll Multi-Language Tools

**Purpose:** Python utilities for managing multi-language Jekyll blogs with e-commerce integration.

**Created:** 2026-01-20
**Author:** Kékéli Afanou
**Project:** Beacon Harbor Blog Setup & Migration

---

## Tools Included

### 0. `detect_post_languages.py` (SP14.5-1)

**Purpose:** Read-only audit of a Jekyll site's `_posts/`, `_pages/`,
`_products/` collections — reports which files already comply with the
`<collection>/<lang>/` folder architecture, which need to be moved, and which
need a `lang:` frontmatter field added or guessed from content.

**Use Case:**
- Phase 1 of the SP14.5 blog migration: run before `migrate_jekyll_repo.py`
  to know exactly what will move.
- Post-migration audit: run again after a migration to confirm 100%
  compliance (exit code 0) or spot regressions.

**Usage:**
```bash
# Human-readable report to stdout
python detect_post_languages.py /path/to/jekyll-site

# Machine-readable JSON, for feeding into migrate_jekyll_repo.py
python detect_post_languages.py /path/to/jekyll-site --format json --output report.json
```

**Features:**
- Classifies every file as `COMPLIANT`, `NEEDS_MOVE`, `NEEDS_FRONTMATTER`,
  `MIXED` (language conflict/anomaly), or `UNKNOWN` (needs manual review).
- Uses the `lang:` frontmatter field when present; falls back to the optional
  `langdetect` package on the post body when absent (degrades gracefully —
  reports `UNKNOWN` with a note — if `langdetect` isn't installed).
- Never writes to the site directory.
- Exit code 0 = fully compliant, 1 = action items found (dry-run signal),
  usable as a CI gate.

**Requirements (optional):**
```bash
pip install langdetect  # only needed for content-based detection fallback
```

---

### 0b. `migrate_jekyll_repo.py` (SP14.5-3)

**Purpose:** Apply the mechanical steps of the multi-language migration
checklist — folder restructure (`git mv`, preserves history) + `lang:`/`ref:`
frontmatter — to a single blog repo. Codifies the recipe validated by hand on
the eagles-techs.com pilot migration, per the Solutions Catalog batch-recipe
protocol (probe repo 1 → capture recipe → script repos 2-N).

**Use Case:**
- Migrating the remaining blogs (SP14.5-8 through -16) onto the new
  architecture without hand-editing hundreds of posts per repo.

**Usage:**
```bash
# Dry-run (default, safe — prints the plan, changes nothing)
python migrate_jekyll_repo.py /path/to/jekyll-site

# Actually perform the moves + frontmatter fixups
python migrate_jekyll_repo.py /path/to/jekyll-site --apply

# Tag the current HEAD as a rollback anchor first
python migrate_jekyll_repo.py /path/to/jekyll-site --apply --tag-backup
```

**Features:**
- Defaults to dry-run; `--apply` required to write anything.
- `git mv`, never a plain filesystem move — preserves file history.
- Adds `lang:`/`ref:` frontmatter only when missing — never overwrites an
  existing value.
- Skips (never guesses) anything the detector flagged `UNKNOWN` or `MIXED` —
  those need a human decision.
- Idempotent: safe to run twice; the second run is a no-op once everything is
  compliant. Verified against a fixture repo (moved 1 file first run, 0 on
  re-run) and read-only-validated against the already-migrated
  eagles-techs.com pilot (0 changes needed).
- Before/after markdown file count check — refuses to report success if any
  file appears lost.

**Explicitly out of scope** (left to review, see script docstring): editing
`_config.yml` `defaults:`/`collections:` (schema differs per repo), the
shared-includes submodule setup (URL/path is NOT uniform across repos — see
`ACT_SETUP.md` sibling note and the flagged divergence in
`951.156.AINOTE...#SP14.4: Migration Checklist`), e-commerce setup, git
push/PR creation.

**See also:** [`ACT_SETUP.md`](ACT_SETUP.md) for local `act` testing before
pushing a migration branch (SP14.5-2).

---

### 1. `generate_redirects.py`

**Purpose:** Generate 301 redirects from old date-based URLs to new SEO-friendly permalinks.

**Use Case:**
- Changing permalink structure from `/:year/:month/:day/:title/` to `/:lang/:categories/:title/`
- Preventing broken links and SEO penalties
- Maintaining link equity after permalink changes

**Usage:**
```bash
# Preview changes (dry run)
python generate_redirects.py --posts-dir _posts --dry-run

# Apply redirects to frontmatter
python generate_redirects.py --posts-dir _posts

# Specify languages
python generate_redirects.py --posts-dir _posts --languages en,fr
```

**Features:**
- Scans all post files in `_posts/` subdirectories
- Extracts date from filename (`YYYY-MM-DD-slug.md`)
- Adds `redirect_from` to frontmatter with old URL
- Uses `jekyll-redirect-from` plugin for 301 redirects
- Preserves existing frontmatter

**Requirements:**
- Jekyll blog with `jekyll-redirect-from` plugin
- Post filenames in format: `YYYY-MM-DD-slug.md`

---

### 2. `stripe_product_sync.py`

**Purpose:** Sync Jekyll product markdown files to Stripe API and update files with real price IDs.

**Use Case:**
- Creating Stripe products from Jekyll product files
- Multi-currency support (USD, EUR, etc.)
- Automating e-commerce setup for digital products

**Usage:**
```bash
# Dry run (show what would be created)
python stripe_product_sync.py \
  --products-dir ./_products \
  --stripe-key sk_test_... \
  --dry-run

# Create products and update files
python stripe_product_sync.py \
  --products-dir ./_products \
  --stripe-key sk_test_...

# Specify languages
python stripe_product_sync.py \
  --products-dir ./_products \
  --stripe-key sk_test_... \
  --languages en,fr
```

**Features:**
- Reads product frontmatter (title, description, price)
- Creates Stripe Product and Price objects
- Updates markdown files with real Stripe IDs
- Supports multiple currencies (extracts from price string)
- Handles language-specific products separately
- Replaces placeholder IDs (`price_PLACEHOLDER_001`)

**Requirements:**
- Stripe API key (test or live)
- `stripe` Python package: `pip install stripe`
- Product files with frontmatter:
  ```yaml
  title: "Product Name"
  price: "$29" or "29€"
  stripe_price_id: "price_PLACEHOLDER_001"
  description: "Product description"
  ```

---

### 3. `scan_completed_subprojects.py`

**Purpose:** Scan Obsidian vault for completed sub-projects eligible for blog post generation.

**Use Case:**
- Retroactive blog post generation from project documentation
- Identifying high-value content candidates
- Prioritizing which sub-projects to turn into posts

**Usage:**
```bash
# Scan vault and generate report
python scan_completed_subprojects.py \
  --vault-root /home/user/my-obsidian \
  --output-file blog-candidates.md

# Limit to top N candidates
python scan_completed_subprojects.py \
  --vault-root /home/user/my-obsidian \
  --top-n 20
```

**Features:**
- Scans `.PRJ.` files for completed sub-projects
- Extracts: task count, completion status, project type
- Calculates publishing interest score:
  - Storytelling potential (task count, complexity)
  - Recruiter appeal (work projects = higher)
  - Priority (P0 > P1 > P2 > P3)
- Determines post type: single (<8 tasks) vs series (≥8 tasks)
- Generates markdown report with top candidates

**Requirements:**
- Obsidian vault with PARA structure
- Project files with frontmatter:
  ```yaml
  Priority: "P0" | "P1" | "P2" | "P3"
  money_potential: "High" | "Medium" | "Low"
  ```
- Sub-projects with `Status::` dataview fields

**Scoring Formula:**
```
score = money_potential × publishing_interest × priority_weight
```

**Output:**
- Top 20 candidates ranked by score
- Post type recommendation (single/series)
- Task count and completion percentage
- Publishing interest breakdown

---

### 4. `translate_posts.py`

**Purpose:** Batch translate Jekyll posts from one language to another by translating frontmatter metadata (lang, title, redirect_from paths) while preserving body content.

**Use Case:**
- Closing the translation gap between EN and FR posts
- Deterministic translation (no external API needed)
- Batch processing with configurable batch sizes

**Usage:**
```bash
# Dry-run: show what would be translated
python translate_posts.py /path/to/jekyll-site --dry-run

# Translate next 20 untranslated posts (newest first)
python translate_posts.py /path/to/jekyll-site --batch-size 20

# Translate ALL remaining posts
python translate_posts.py /path/to/jekyll-site --all

# Oldest posts first
python translate_posts.py /path/to/jekyll-site --batch-size 30 --sort oldest
```

**Features:**
- Finds untranslated posts by comparing `en/_posts/` vs `fr/_posts/`
- Translates `lang:` field and `redirect_from:` paths (adds `/fr/` prefix)
- Preserves body content as-is (matches bright-softwares.com pattern)
- Supports `--dry-run`, `--batch-size`, `--sort` (newest/oldest)
- No external dependencies (stdlib only)

**Requirements:**
- Jekyll site with `en/_posts/` and `fr/_posts/` structure
- Post files with YAML frontmatter

---

## Installation

**Dependencies:**
```bash
pip install stripe pyyaml
```

**Optional (for Obsidian vault scanning):**
```bash
pip install pathlib
```

---

## Important: .gitkeep Files for Empty Folders

**Git doesn't track empty directories.** To preserve folder structure in your repository, you MUST add `.gitkeep` files to all empty folders.

**Why this matters:**
- Empty workflow folders (_drafts subfolders) won't appear in GitHub unless they contain a file
- Missing folders break the content workflow
- Other developers cloning the repo won't have the complete structure

**Quick fix command:**
```bash
# Add .gitkeep to all empty folders in your Jekyll blog
find _drafts -type d -empty -exec touch {}/.gitkeep \;
find _seo -type d -empty -exec touch {}/.gitkeep \;
find _pages -type d -empty -exec touch {}/.gitkeep \;
find _products -type d -empty -exec touch {}/.gitkeep \;

# Add and commit
git add .
git commit -m "feat: Add .gitkeep files to preserve folder structure"
```

**When to use:**
- After creating new blog repository
- After adding new language folders
- When setting up workflow folders (_drafts/en/200_*, 300_*, etc.)
- Before first commit to ensure complete folder structure

---

## Integration with Jekyll Blogs

These tools are designed for Jekyll blogs following this structure:

```
blog-name/
├── _posts/
│   ├── en/
│   │   └── YYYY-MM-DD-post.md
│   └── fr/
│       └── YYYY-MM-DD-post.md
├── _products/
│   ├── en/
│   │   └── product-name.md
│   └── fr/
│       └── product-name.md
└── _config.yml
```

**Recommended Jekyll plugins:**
```ruby
group :jekyll_plugins do
  gem "jekyll-redirect-from"  # For generate_redirects.py
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
end
```

---

## Related Workflows

**Blog Post Generation Workflow:**
1. Scan vault for candidates: `scan_completed_subprojects.py`
2. Generate blog post from sub-project (manual or automated)
3. Generate redirects if changing permalinks: `generate_redirects.py`
4. Create Stripe products: `stripe_product_sync.py`
5. Deploy to Netlify/GitHub Pages

**GitHub Actions Integration:**
See `.github/workflows/` in individual blog repositories for automated workflows.

---

## Examples

### Full Blog Setup Example (Beacon Harbor)

```bash
# 1. Clone blog repository
git clone https://github.com/sergioafanou/beaconharbor.afanou.com.git
cd beaconharbor.afanou.com

# 2. Add .gitkeep files to empty folders (IMPORTANT!)
find _drafts -type d -empty -exec touch {}/.gitkeep \;
find _seo -type d -empty -exec touch {}/.gitkeep \;
git add .
git commit -m "feat: Add .gitkeep files to preserve folder structure"

# 3. Sync products to Stripe
python ../blogpost-tools/jekyll-multi-language-tools/stripe_product_sync.py \
  --products-dir ./_products \
  --stripe-key $STRIPE_SECRET_KEY

# 4. Generate redirects (if changing permalink structure)
python ../blogpost-tools/jekyll-multi-language-tools/generate_redirects.py \
  --posts-dir _posts

# 5. Commit changes
git add .
git commit -m "chore: Sync Stripe products and generate redirects"
git push

# 6. Deploy (Netlify auto-deploys on push)
```

---

## Documentation

**Full setup guide:** See `task_executor/docs/beacon-harbor-setup-complete.md` in my-obsidian vault

**Blog configuration:** See `BLOG.beaconharbor-afanou.md` in 70-79.resources/79.standards-and-conventions/

**ALGO workflow:** See `10.38.ALGO.solo.blog-post-generation-from-subprojects.md` in 70-79.resources/73.tasks_automation/

---

## License

MIT License - Free to use, modify, and distribute.

---

## Contributing

Pull requests welcome at: https://github.com/BrightSoftwares/blogpost-tools

**Contact:** Kékéli Afanou (Bright Softwares)
