#!/usr/bin/env python3
"""
SEO Links Enricher — DEPRECATED SHIM around scripts/seo_links_populator.py.

This file used to contain a second, independent implementation of
"populate `seo.links` with Wikidata entities". It was never once successful in
production: the only caller (`corporate-website/.github/workflows/seo-links-enricher.yml`)
has exactly one run in its history — 2026-06-22, `startup_failure` — and it
pointed at `./_posts`, a directory that does not exist in that repo (its posts
live under `en/_posts`).

Meanwhile it carried the same family of defects as the live populator, plus
worse ones of its own:

  * `extract_topics()` scraped capitalised runs out of the title with
    `re.findall(r"[A-Z][a-z]+(?:\\s[A-Z][a-z]+)*|[A-Z]{2,}", title)` and had no
    stopword list at all, so "We Built", "Ourselves First" and "It Found Two
    Bugs No Demo Would Have" were all sent to Wikidata as search queries.
  * `search_wikidata()` requested `limit=1` and returned `results[0]["id"]`
    unconditionally — no label check, no entity-type check, nothing.
  * `process_file()` treated any post whose links were all
    `Q29581045`/`Q1662689` as "generic" and re-enriched it; every other post
    with 2+ links was skipped regardless of whether those links were correct.

Two implementations of one job is how the two drifted apart in the first place
(doctrine: fix the script, never fork it). Rather than fixing the same bugs
twice, this module now delegates to the single maintained implementation in
`scripts/seo_links_populator.py`, which has the relevance gates, the
`--replace-irrelevant` repair path, and the `--audit-csv` drift report.

The CLI is kept backward compatible (`--posts-dir`, `--file`, `--apply`,
`--dry-run`) so the existing reusable workflow keeps working, and the new audit
flags are exposed here too.

Prefer calling `scripts/seo_links_populator.py` directly in new workflows.
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))

import seo_links_populator as populator  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

MIN_LINKS = 2
MAX_LINKS = 4


def main():
    parser = argparse.ArgumentParser(
        description="Enrich blog post seo.links with Wikidata entities "
                    "(deprecated shim for scripts/seo_links_populator.py)"
    )
    parser.add_argument("--posts-dir", type=str, help="Directory containing blog posts")
    parser.add_argument("--file", type=str, help="Single file to process")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without modifying files")
    parser.add_argument("--force", action="store_true", help="Recompute seo.links even if present")
    parser.add_argument("--replace-irrelevant", action="store_true",
                        help="Keep existing links that pass the audit, replace the rest")
    parser.add_argument("--min-links", type=int, default=MIN_LINKS)
    parser.add_argument("--max-links", type=int, default=MAX_LINKS)
    parser.add_argument("--audit-csv", metavar="PATH",
                        help="Audit mode: write a seo.links relevance report to PATH")
    parser.add_argument("--audit-offline", action="store_true",
                        help="Audit mode: skip Wikidata resolution")
    args = parser.parse_args()

    logger.warning(
        "enrich_seo_links.py is deprecated — it now delegates to "
        "scripts/seo_links_populator.py. Point new workflows at that script."
    )

    if not args.file and not args.posts_dir:
        parser.print_help()
        return 1

    files = populator.collect_files(
        [args.posts_dir] if args.posts_dir else [],
        [args.file] if args.file else [],
        "*.md",
    )
    if not files:
        logger.error("No markdown files found")
        return 1

    if args.audit_csv:
        populator.audit_files(files, Path(args.audit_csv), offline=args.audit_offline)
        return 0

    dry_run = not args.apply
    updated = 0
    for f in files:
        if populator.process_file(
            f,
            min_links=args.min_links,
            max_links=args.max_links,
            force=args.force,
            dry_run=dry_run,
            replace_irrelevant=args.replace_irrelevant,
        ):
            updated += 1

    logger.info("Processed %d files, %d %s", len(files), updated,
                "would be updated" if dry_run else "updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
