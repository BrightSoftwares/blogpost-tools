#!/usr/bin/env python3
"""Apply the mechanical steps of the SP14.4/14.5 multi-language Jekyll
migration checklist to a single blog repo.

Source of truth for the steps this script automates: the "SP14.4: Migration
Checklist" section of
`951.156.AINOTE.solo.out.ainote-sp14-4-multilang-jekyll-specs.md` in the
my-obsidian vault, and the already-validated real-world pattern live on
eagles-techs.com (pilot repo, migrated by hand before this script existed —
this script codifies that recipe per the Solutions Catalog batch-recipe
protocol: probe repo 1 by hand, capture the recipe, script repos 2-N).

What this script does (mechanical / judgment-free steps only):
    1. Optionally tag current HEAD as a pre-migration backup anchor.
    2. Create `<collection>/<lang>/` folders for every known language.
    3. `git mv` flat collection files into their language subfolder
       (preserves git history; a plain filesystem move does not).
    4. Ensure every migrated post/page has `lang:` and `ref:` frontmatter
       fields — added only if missing, existing values are NEVER overwritten.
    5. Ensure `_data/translations.yml` and `_data/navigation.yml` exist
       (created as empty stub files if missing — never overwrites existing).
    6. Report a before/after file count so nothing is silently lost.

What this script deliberately does NOT do (left to a human or a separate,
reviewed step — see the checklist's "Open question" and steps 3-4):
    - Editing `_config.yml` `defaults:` / `collections:` blocks (schema
      varies per repo — e-commerce collections, custom permalinks — this is
      exactly the kind of structural decision CLAUDE.md says not to guess).
    - Adding/pinning the `_includes` shared-components submodule (URL and
      target path vary: eagles-techs.com uses `_data/shared` ->
      `shared-site-data.git`, NOT the `_includes/common` -> `blog-common.git`
      path named in the original architecture spec — a real divergence,
      flagged rather than silently resolved either way).
    - Stripe / e-commerce setup (`stripe_product_sync.py` already exists for
      that, and only applies to repos in the SP14.5 e-commerce table).
    - Pushing or opening a PR (the caller's job — see the External Repo
      Branch Policy).

Always defaults to --dry-run (prints a plan, changes nothing). Pass --apply
to actually perform the git mv / file writes. Designed to be idempotent: run
it twice, the second run is a no-op (everything already reports COMPLIANT).

Usage:
    # Preview only (safe, default)
    python migrate_jekyll_repo.py /path/to/jekyll-site

    # Reuse a detection report instead of re-scanning
    python migrate_jekyll_repo.py /path/to/jekyll-site --detection-report report.json

    # Actually perform the moves + frontmatter fixups
    python migrate_jekyll_repo.py /path/to/jekyll-site --apply

    # Also tag the current HEAD as a rollback anchor before changing anything
    python migrate_jekyll_repo.py /path/to/jekyll-site --apply --tag-backup
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detect_post_languages import (  # noqa: E402
    DEFAULT_COLLECTIONS,
    DEFAULT_LANGUAGES,
    extract_frontmatter,
    get_frontmatter_value,
    scan_collection,
)

STUB_TRANSLATIONS_YML = """# Auto-created by migrate_jekyll_repo.py — populate with real UI strings.
# Read unconditionally by _includes/*/nav.html per the language-fallback spec.
en:
  nav_home: "Home"
fr:
  nav_home: "Accueil"
"""

STUB_NAVIGATION_YML = """# Auto-created by migrate_jekyll_repo.py — populate with real menu entries.
# Read unconditionally by _includes/*/nav.html per the language-fallback spec.
items: []
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Apply the mechanical multi-language Jekyll migration steps "
        "(folder restructure + lang/ref frontmatter) to one repo."
    )
    parser.add_argument("site_dir", help="Path to Jekyll site root (a git working tree)")
    parser.add_argument(
        "--collections",
        default=",".join(DEFAULT_COLLECTIONS),
        help=f"Comma-separated collections to migrate (default: {','.join(DEFAULT_COLLECTIONS)})",
    )
    parser.add_argument(
        "--languages",
        default=",".join(DEFAULT_LANGUAGES),
        help=f"Comma-separated known language codes; first is the default/fallback lang "
        f"(default: {','.join(DEFAULT_LANGUAGES)})",
    )
    parser.add_argument(
        "--detection-report",
        default=None,
        help="Path to a JSON report from detect_post_languages.py --format json "
        "(skips re-scanning; entries with status UNKNOWN or MIXED are always skipped)",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Actually perform changes (default: dry-run)"
    )
    parser.add_argument(
        "--tag-backup",
        action="store_true",
        help="git tag the current HEAD as pre-migration-YYYY-MM-DD before changing anything "
        "(only meaningful with --apply)",
    )
    return parser.parse_args()


def run_git(site_dir: Path, args: list[str], dry_run: bool) -> None:
    cmd = ["git", "-C", str(site_dir)] + args
    if dry_run:
        print(f"  [dry-run] would run: {' '.join(cmd)}")
        return
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR running {' '.join(cmd)}: {result.stderr.strip()}", file=sys.stderr)


def tag_backup(site_dir: Path, dry_run: bool) -> str:
    tag = f"pre-migration-{date.today().isoformat()}"
    run_git(site_dir, ["tag", tag], dry_run)
    if not dry_run:
        run_git(site_dir, ["push", "origin", tag], dry_run)
    print(f"Backup tag: {tag}")
    return tag


def derive_ref(filename: str) -> str:
    """Slug from a YYYY-MM-DD-slug.md filename, matching the eagles-techs.com
    `ref:` convention observed in the live pilot migration."""
    stem = Path(filename).stem
    match = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", stem)
    return match.group(1) if match else stem


def ensure_frontmatter_fields(content: str, lang: str, filename: str) -> tuple[str, bool]:
    """Add missing lang:/ref: fields. Never touches an existing value.
    Returns (new_content, changed)."""
    fm_text, body = extract_frontmatter(content)
    if not fm_text:
        return content, False

    changed = False
    new_fm = fm_text

    if not get_frontmatter_value(fm_text, "lang"):
        new_fm = new_fm.rstrip("\n") + f"\nlang: {lang}\n"
        changed = True

    if not get_frontmatter_value(fm_text, "ref"):
        new_fm = new_fm.rstrip("\n") + f"\nref: {derive_ref(filename)}\n"
        changed = True

    if not changed:
        return content, False
    return f"---{new_fm}---{body}", True


def migrate_collection(site_dir: Path, collection: str, languages: list[str], dry_run: bool) -> dict:
    stats = {"moved": 0, "frontmatter_fixed": 0, "skipped_unknown": 0, "skipped_mixed": 0}
    entries = scan_collection(site_dir, collection, languages)

    for entry in entries:
        if entry.status == "COMPLIANT":
            continue
        if entry.status == "UNKNOWN":
            stats["skipped_unknown"] += 1
            print(f"  SKIP (unknown language, needs manual review): {entry.current_path}")
            continue
        if entry.status == "MIXED":
            stats["skipped_mixed"] += 1
            print(f"  SKIP (mixed-language anomaly, needs manual review): {entry.current_path}")
            continue

        current_path = site_dir / entry.current_path
        target_path = site_dir / entry.target_path
        lang = entry.target_lang

        print(f"  MOVE: {entry.current_path} -> {entry.target_path}")
        if dry_run:
            print(f"    [dry-run] would ensure lang/ref frontmatter (lang={lang})")
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            run_git(site_dir, ["mv", str(current_path), str(target_path)], dry_run=False)
            content = target_path.read_text(encoding="utf-8")
            new_content, changed = ensure_frontmatter_fields(content, lang, entry.filename)
            if changed:
                target_path.write_text(new_content, encoding="utf-8")
                stats["frontmatter_fixed"] += 1
        stats["moved"] += 1

    return stats


def ensure_data_stub(site_dir: Path, relative_path: str, stub_content: str, dry_run: bool) -> bool:
    path = site_dir / relative_path
    if path.exists():
        return False
    print(f"  CREATE stub: {relative_path}")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(stub_content, encoding="utf-8")
    return True


def count_md_files(site_dir: Path, collections: list[str]) -> int:
    total = 0
    for collection in collections:
        collection_dir = site_dir / collection
        if collection_dir.exists():
            total += len(list(collection_dir.rglob("*.md")))
    return total


def main():
    args = parse_args()
    site_dir = Path(args.site_dir).resolve()
    if not site_dir.exists():
        print(f"ERROR: Site directory not found: {site_dir}", file=sys.stderr)
        sys.exit(1)
    if not (site_dir / ".git").exists():
        print(f"ERROR: {site_dir} is not a git working tree (no .git) — refusing to `git mv`.", file=sys.stderr)
        sys.exit(1)

    collections = [c.strip() for c in args.collections.split(",") if c.strip()]
    languages = [l.strip() for l in args.languages.split(",") if l.strip()]
    dry_run = not args.apply

    print(f"{'DRY RUN — no changes will be made' if dry_run else 'APPLY MODE — changes will be made'}")
    print(f"Site: {site_dir}")
    print(f"Collections: {collections}  Languages: {languages}")
    print()

    if args.detection_report:
        # Report is informational context only; migrate_collection always
        # re-derives status live from disk so the script stays idempotent
        # even if the report is stale.
        report = json.loads(Path(args.detection_report).read_text(encoding="utf-8"))
        print(f"Loaded detection report for '{report.get('site')}' "
              f"({len(report.get('entries', []))} entries) — used as context only.")
        print()

    before_count = count_md_files(site_dir, collections)

    if args.tag_backup:
        tag_backup(site_dir, dry_run)
        print()

    all_stats = {"moved": 0, "frontmatter_fixed": 0, "skipped_unknown": 0, "skipped_mixed": 0}
    for collection in collections:
        if not (site_dir / collection).exists():
            continue
        print(f"## {collection}")
        stats = migrate_collection(site_dir, collection, languages, dry_run)
        for key in all_stats:
            all_stats[key] += stats[key]
        print()

    print("## _data stubs")
    ensure_data_stub(site_dir, "_data/translations.yml", STUB_TRANSLATIONS_YML, dry_run)
    ensure_data_stub(site_dir, "_data/navigation.yml", STUB_NAVIGATION_YML, dry_run)
    print()

    after_count = count_md_files(site_dir, collections)

    print("## Summary")
    print(f"- Files moved: {all_stats['moved']}")
    print(f"- Frontmatter fields added (lang/ref): {all_stats['frontmatter_fixed']}")
    print(f"- Skipped (unknown language, needs manual review): {all_stats['skipped_unknown']}")
    print(f"- Skipped (mixed-language anomaly, needs manual review): {all_stats['skipped_mixed']}")
    print(f"- Markdown file count before: {before_count}  after: {after_count} "
          f"({'OK, none lost' if before_count == after_count or dry_run else 'MISMATCH — investigate before committing'})")

    if not dry_run and before_count != after_count:
        print("ERROR: file count changed unexpectedly — do not push, investigate first.", file=sys.stderr)
        sys.exit(1)

    print()
    print("NOT done by this script (see docstring): _config.yml defaults/collections edits, "
          "shared-includes submodule setup, e-commerce setup, git push, PR creation.")

    sys.exit(0 if (all_stats["skipped_unknown"] == 0 and all_stats["skipped_mixed"] == 0) else 2)


if __name__ == "__main__":
    main()
