# Readability Checker

A GitHub Action that scores Jekyll blog posts for readability using the
**Flesch Reading Ease** and **Flesch-Kincaid Grade Level** formulas. Never
modifies the posts it scans — it only reports.

Fills a confirmed gap in `blogpost-tools`: no readability-scoring script
existed anywhere in this repo before this action (verified by grepping the
full repo for "readab" — see `blog-post-writer` skill's SP14.5 addendum in
`sergioafanou/my-obsidian`).

## What it does

1. Expands `posts_glob` to a list of markdown files.
2. For each post: strips Jekyll frontmatter (`python-frontmatter`), then
   strips Markdown syntax (headings, lists, links, images, wikilinks,
   bold/italic, fenced code blocks — code is removed entirely, not scored
   as prose) so word/sentence/syllable counts reflect the actual prose.
3. Computes:
   - **Flesch Reading Ease** (0-100, higher = easier to read)
   - **Flesch-Kincaid Grade Level** (approximate US school grade required)
4. Writes a JSON report, a CSV, and a human-readable summary — mirroring
   the `seo-analysis` action's output convention — plus GitHub Actions
   outputs for downstream steps.

A post scoring below `min_score` is flagged in the report but **does not
fail the build** unless `fail_on_below_min` is set to `"true"` — matching
this repo's existing convention (see `seo-analysis`) of not failing builds
for non-critical findings.

## Inputs

| Input | Default | Description |
|---|---|---|
| `posts_glob` | `_posts/**/*.md` | Glob pattern (relative to the workspace root) matching the posts to check. |
| `min_score` | `60` | Minimum acceptable Flesch Reading Ease score. 60 is the conventional "Plain English / general audience" threshold. |
| `target_grade_level` | `10` | Target Flesch-Kincaid Grade Level. 8-10 is the commonly recommended range for general web content. |
| `fail_on_below_min` | `false` | If `"true"`, exit non-zero when any post is below `min_score`. |
| `output_dir` | `_seo/readability-checker/output` | Where JSON/CSV/summary reports are written. |

## Outputs

| Output | Description |
|---|---|
| `report_file` | Path to `readability_latest.json`. |
| `posts_analyzed` | Number of posts successfully scored. |
| `posts_below_threshold` | Number of posts scoring below `min_score`. |
| `average_score` | Average Flesch Reading Ease across all analyzed posts. |

## Usage

```yaml
name: Readability Check

on:
  pull_request:
    paths:
      - '_posts/**/*.md'

jobs:
  readability:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: BrightSoftwares/blogpost-tools/readability-checker@main
        with:
          posts_glob: '_posts/**/*.md'
          min_score: '60'
```

## Development

```bash
pip install -r requirements-test.txt
pytest tests/ -v --tb=short
```

Run against a single post locally:

```bash
INPUT_POSTS_GLOB="_posts/2026-01-01-example.md" INPUT_OUTPUT_DIR=/tmp/rc-output \
  python3 src/main.py
```

## Design notes

- **No new external dependency for scoring.** The syllable-counting
  heuristic (vowel-group counting, standard technique used by
  textstat-style tools) and both formulas are implemented directly in
  `src/main.py` — the repo already depends on `python-frontmatter`
  (reused here for frontmatter parsing), and neither formula needs
  anything beyond it.
- **Docker base image.** Uses `python:3.12-slim` with `requirements.txt`
  installed at build time (the `semantic-keyword-clustering` action's
  pattern), rather than a pre-built `fullbright/*` Docker Hub image like
  `seo-analysis`/`keyword-suggestion` — there is no existing
  `fullbright/readability-checker` image to build from, and this repo
  already has a working precedent for a plain `python:3` base.
