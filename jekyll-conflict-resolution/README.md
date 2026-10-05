# Jekyll Slug-Conflict Resolution

Three small CLI scripts for finding and resolving duplicate `ref:`
front-matter slugs in a Jekyll `_posts` directory. Jekyll doesn't error on a
duplicate slug by default — it silently picks one post and the other simply
never gets a URL. These scripts make that failure mode visible and fixable.

Originally written to resolve 48 duplicate-slug conflicts (26 unique slugs)
across `BrightSoftwares/corporate-website`'s `fr/_posts` directory in
January 2026. Generalized here so they work on any Jekyll `_posts`
directory and language, not just French posts.

## Scripts

| Script | Purpose |
|---|---|
| `conflict_analyzer.py` | Scans a `_posts` dir, groups posts by `ref:`, and classifies each conflicting pair as `IDENTICAL` / `MINOR_UPDATE` / `DIFFERENT` by content similarity. Outputs a JSON report. |
| `bulk_resolver.py` | Applies a resolutions file (deletes + renames) to the posts directory. Always supports `--dry-run`. |
| `verify_no_conflicts.py` | Re-scans after resolution and exits non-zero if any duplicate `ref:` remains — usable as a CI gate. |

## Usage

### 1. Analyze

```bash
python3 conflict_analyzer.py --posts-dir fr/_posts --output conflict_report.json
```

This does **not** decide what to do about a conflict — it classifies it and
proposes an action in plain English. A human (or an AI session with the
report in context) reads the report and decides:

- `IDENTICAL` conflicts: almost certainly safe to auto-resolve (keep the
  newest, delete the older duplicate).
- `MINOR_UPDATE` / `DIFFERENT` conflicts: need a human or editorial judgment
  call on the new slug/filename — these are not mechanical decisions.

### 2. Write a resolutions file

```json
{
  "deletes": ["2020-04-03-old-duplicate-post.md"],
  "renames": {
    "2020-07-05-how-to-configure-jenkins-fr.md": {
      "new_filename": "2020-07-05-jenkins-ssl-nginx-reverse-proxy.md",
      "new_ref": "jenkins-ssl-nginx-reverse-proxy"
    }
  }
}
```

### 3. Dry-run, then apply

```bash
python3 bulk_resolver.py --posts-dir fr/_posts --resolutions resolutions.json --dry-run
python3 bulk_resolver.py --posts-dir fr/_posts --resolutions resolutions.json --apply
```

### 4. Verify

```bash
python3 verify_no_conflicts.py --posts-dir fr/_posts
```

## Preventing future conflicts

The scripts here fix *existing* conflicts. To stop new ones from
accumulating, two cheap additions pay for themselves:

1. **Pre-commit hook** — block a commit that introduces a duplicate
   `ref:`/language combination:
   ```bash
   #!/bin/bash
   # .git/hooks/pre-commit
   python3 jekyll-conflict-resolution/verify_no_conflicts.py --posts-dir fr/_posts || exit 1
   ```
2. **Scheduled CI check** — run `verify_no_conflicts.py` on a schedule (e.g.
   monthly) across every `_posts` directory in the site and fail the job (or
   open an issue) if it finds anything. Not wired up as a reusable workflow
   here — add a caller workflow in the consuming site's own
   `.github/workflows/` if you want it scheduled.

## Tests

```bash
cd jekyll-conflict-resolution
python3 -m unittest discover -s tests -v
```

## Background

Companion blog post: *When Content Management Goes Wrong: Lessons from
Deduplicating 50 Blog Posts* (`corporate-website`
`en/_drafts/300_generated_raw_content/`), which links here for the
technical implementation detail.
