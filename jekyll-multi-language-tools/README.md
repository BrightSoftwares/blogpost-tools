# Jekyll Multi-Language Tools

**Purpose:** Python utilities for managing multi-language Jekyll blogs with e-commerce integration.

**Created:** 2026-01-20
**Author:** Kékéli Afanou
**Project:** Beacon Harbor Blog Setup & Migration

---

## Tools Included

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
