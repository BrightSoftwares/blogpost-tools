# Schema Markup Generator

A GitHub Action that generates schema.org `BlogPosting` JSON-LD for Jekyll
blog posts from their frontmatter. Never edits the source post.

Fills a confirmed gap in `blogpost-tools`: no JSON-LD/structured-data
script existed anywhere in this repo before this action (verified by
grepping the full repo for "json-ld", "jsonld", "structured_data",
"schema.markup", "schema_markup" — zero hits — see `blog-post-writer`
skill's SP14.5 addendum in `sergioafanou/my-obsidian`).

## What it does

1. Expands `posts_glob` to a list of markdown files.
2. Parses each post's frontmatter (`python-frontmatter`) and builds a
   schema.org `BlogPosting` JSON-LD object: `@context`, `@type`,
   `headline`, `datePublished`, `dateModified` (if available), `author`,
   `image`, `description`, plus `url`/`mainEntityOfPage`/`publisher` when
   `site_url` is given.
3. Writes **one `<post>.schema.json` sidecar file next to each source
   post**, plus a combined `schema_markup_latest.json` report — mirroring
   the `seo-analysis` action's output-directory convention.

## Required vs. best-effort fields

Only two fields are treated as **unavoidable** — a post missing either is
**skipped with a clear warning**, not a crash:

- `title` (becomes `headline`)
- `date` (becomes `datePublished`)

Every other field (`author`, `image`, `description`, `dateModified`,
`url`/`publisher`) is generated **best-effort**: if the frontmatter data
isn't there, the field is simply omitted from the JSON-LD (with a logged
warning) rather than blocking generation — valid JSON-LD does not require
every schema.org property to be present.

`image` is looked up under several common frontmatter field names, in
order: `image`, `og_image`, `header_image`, `hero_image`, `cover_image`,
`thumbnail`. `dateModified` is looked up under `date_modified`,
`last_modified_at`, `updated`.

## Inputs

| Input | Default | Description |
|---|---|---|
| `posts_glob` | `_posts/**/*.md` | Glob pattern (relative to the workspace root) matching the posts to process. |
| `site_url` | _(none)_ | Base site URL, e.g. `https://bright-softwares.com`. Used to build absolute image/post URLs and the `publisher` Organization. When omitted, `url`/`mainEntityOfPage`/`publisher` are omitted rather than guessed. |
| `publisher_name` | _(none)_ | Organization name for schema.org `publisher`, and the fallback `author` when a post has none. |
| `output_dir` | `_seo/schema-markup-generator/output` | Where the combined report is written. |

## Outputs

| Output | Description |
|---|---|
| `report_file` | Path to `schema_markup_latest.json`. |
| `posts_processed` | Number of posts a JSON-LD block was generated for. |
| `posts_skipped` | Number of posts skipped for missing `title` or `date`. |

## Usage

```yaml
name: Generate Schema Markup

on:
  pull_request:
    paths:
      - '_posts/**/*.md'

jobs:
  schema-markup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: BrightSoftwares/blogpost-tools/schema-markup-generator@main
        with:
          posts_glob: '_posts/**/*.md'
          site_url: 'https://bright-softwares.com'
          publisher_name: 'Bright Softwares'
```

## Committing the generated sidecar files

This action writes `.schema.json` files into the working tree but does not
commit them. Pair it with this repo's
[`reusable_commit-generated-files.yml`](../.github/workflows/reusable_commit-generated-files.yml)
workflow (the same pattern used to persist other actions' generated
output) in the calling repository's CI.

## Development

```bash
pip install -r requirements-test.txt
pytest tests/ -v --tb=short
```

Run against a single post locally:

```bash
INPUT_POSTS_GLOB="_posts/2026-01-01-example.md" INPUT_OUTPUT_DIR=/tmp/smg-output \
  INPUT_SITE_URL="https://bright-softwares.com" python3 src/main.py
```

## Open question for the human reviewer (flagged, not resolved here)

**Where the JSON-LD actually gets embedded into the rendered page is a
`corporate-website` Jekyll `_layouts` change, out of scope for this
`blogpost-tools`-only session.** Two options were considered:

- **A — Sidecar file (implemented here).** This action writes
  `<slug>.schema.json` next to each post. A future `_includes/` partial in
  `corporate-website` would read the sidecar matching the current post's
  slug and emit it inside `<script type="application/ld+json">`. Chosen
  because every other action in this repo that produces structured output
  (`seo-analysis`, `internal-linking`, `keyword-suggestion`) writes to a
  dedicated output directory rather than mutating the source post, and a
  JSON string embedded into a `schema_jsonld:` frontmatter field is
  awkward to keep as valid YAML across re-runs.
- **B — Frontmatter field.** Write the JSON-LD (or a subset of fields)
  directly into the post's own frontmatter as `schema_jsonld:`, for a
  layout to read `page.schema_jsonld` directly with no sidecar-matching
  logic needed.

This session could not verify which of `corporate-website`'s existing
`_layouts` (if any) already emit partial schema.org markup, since reading
that repo was out of scope here. **Recommendation: read
`corporate-website`'s `_layouts/post.html` (or equivalent) before wiring
this into CI**, and switch to Option B only if a layout convention already
expects a frontmatter field rather than a sidecar file.

## Design notes

- **Docker base image.** Uses `python:3.12-slim` with `requirements.txt`
  installed at build time (the `semantic-keyword-clustering` action's
  pattern) — there is no existing `fullbright/schema-markup-generator`
  Docker Hub image to build from, unlike `seo-analysis`/`keyword-suggestion`.
- **Headline length.** Truncated to 110 characters (Google's guidance for
  the `headline` property) with a logged warning, rather than silently
  passing through an overlong title.
