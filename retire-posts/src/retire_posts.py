#!/usr/bin/env python3
"""
retire_posts.py — SEO-safe blog post retirement.

Reads _data/retire_posts.yml, then for every entry:
  1. Adds redirect_from: [source_url] to the destination post's frontmatter.
  2. Appends a "See also" mention at the end of the destination post body.
  3. Deletes the source post file.

Run with --dry-run to preview changes without writing any files.
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Optional

import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_POST_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-(.+)$")
_SKIP_DIRS = {"_layouts", "_includes", "_sass", ".git", ".github", "node_modules", ".jekyll-cache"}


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) from a Jekyll file's content."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}, content
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        # Frontmatter contains unparseable content (e.g. wikilinks [[...]] or bare ? chars)
        fm = {}
    if not isinstance(fm, dict):
        fm = {}
    body = content[m.end():]
    return fm, body


def write_frontmatter(fm: dict, body: str) -> str:
    """Serialize frontmatter dict + body back to a Jekyll file string."""
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return f"---\n{fm_str}---\n{body}"


def _derive_post_url(md_file: Path, fm: dict) -> Optional[str]:
    """
    Derive the Jekyll URL for a post using the /blog/:categories/:slug pattern.
    Falls back gracefully when categories or slug cannot be determined.
    """
    stem = md_file.stem
    slug_match = _POST_DATE_RE.match(stem)
    slug = slug_match.group(1) if slug_match else stem

    raw_cats = fm.get("categories") or fm.get("category") or []
    if isinstance(raw_cats, str):
        raw_cats = [raw_cats]
    categories = [str(c).strip() for c in raw_cats if str(c).strip()]
    if not categories:
        return f"/blog/{slug}"
    return f"/blog/{categories[0]}/{slug}"


def build_url_index(root: Path) -> dict[str, Path]:
    """
    Walk all markdown files under root and map their Jekyll URL(s) to the file path.

    Indexed keys per file:
      - permalink (if set in frontmatter)
      - redirect_from entries (old URLs that already point here)
      - derived /blog/:category/:slug URL (for posts in */_posts/ directories)
      - __slug__{slug} key for slug-based fallback lookup
    """
    index: dict[str, Path] = {}

    for md_file in root.rglob("*.md"):
        rel_parts = set(md_file.relative_to(root).parts)
        if rel_parts & _SKIP_DIRS:
            continue

        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        fm, _ = parse_frontmatter(text)
        if not fm:
            continue

        def _idx(url: str) -> None:
            key = url.rstrip("/")
            if key:
                index.setdefault(key, md_file)

        # 1. Explicit permalink / url frontmatter
        if fm.get("permalink"):
            _idx(str(fm["permalink"]))
        if fm.get("url"):
            _idx(str(fm["url"]))

        # 2. redirect_from entries (old URLs already pointing here)
        redirects = fm.get("redirect_from") or []
        if isinstance(redirects, str):
            redirects = [redirects]
        for r in redirects:
            _idx(str(r))

        # 3. Derived URL for posts (Jekyll /blog/:categories/:slug pattern)
        if "_posts" in md_file.parts:
            derived = _derive_post_url(md_file, fm)
            if derived:
                _idx(derived)

        # 4. Slug-only fallback key
        stem = md_file.stem
        slug_match = _POST_DATE_RE.match(stem)
        slug = slug_match.group(1) if slug_match else stem
        index.setdefault(f"__slug__{slug}", md_file)

    return index


def find_file_for_url(url: str, index: dict[str, Path]) -> Optional[Path]:
    """Look up a Jekyll URL in the index (normalises trailing slash).
    Falls back to matching by the last path segment (slug)."""
    normalised = url.rstrip("/")
    if normalised in index:
        return index[normalised]
    # Slug-based fallback: match on the last URL segment
    slug = normalised.rsplit("/", 1)[-1]
    return index.get(f"__slug__{slug}")


def retire_post(
    source_url: str,
    dest_url: str,
    reason: str,
    root: Path,
    dry_run: bool,
) -> bool:
    """
    Perform the full retirement of source_url → dest_url.
    Returns True on success, False on any error.
    """
    index = build_url_index(root)

    source_path = find_file_for_url(source_url, index)
    dest_path = find_file_for_url(dest_url, index)

    if source_path is None:
        log.error("Cannot find source file for URL: %s", source_url)
        log.error("Indexed URLs (sample): %s", list(index.keys())[:20])
        return False

    if dest_path is None:
        log.error("Cannot find destination file for URL: %s", dest_url)
        return False

    log.info("Retiring  %s  (%s)", source_url, source_path)
    log.info("       →  %s  (%s)", dest_url, dest_path)

    # --- 1. Update destination: add redirect_from, append See also ---
    dest_content = dest_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(dest_content)

    existing_redirects: list = fm.get("redirect_from") or []
    if isinstance(existing_redirects, str):
        existing_redirects = [existing_redirects]
    if source_url not in existing_redirects:
        existing_redirects.append(source_url)
    fm["redirect_from"] = existing_redirects

    see_also_line = f"\n> **See also:** This page was previously available at `{source_url}` ({reason}). It has been consolidated here.\n"
    if see_also_line.strip() not in body:
        body = body.rstrip("\n") + "\n" + see_also_line

    new_dest_content = write_frontmatter(fm, body)

    if dry_run:
        log.info("[DRY-RUN] Would update: %s", dest_path)
        log.info("[DRY-RUN] New redirect_from: %s", existing_redirects)
    else:
        dest_path.write_text(new_dest_content, encoding="utf-8")
        log.info("Updated destination: %s", dest_path)

    # --- 2. Delete source ---
    if dry_run:
        log.info("[DRY-RUN] Would delete: %s", source_path)
    else:
        source_path.unlink()
        log.info("Deleted source: %s", source_path)

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Retire Jekyll blog posts with SEO redirects.")
    parser.add_argument("--vault-root", default=".", help="Path to the Jekyll site root.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files.")
    args = parser.parse_args()

    root = Path(args.vault_root).resolve()
    queue_file = root / "_data" / "retire_posts.yml"

    if not queue_file.exists():
        log.error("Queue file not found: %s", queue_file)
        sys.exit(1)

    queue_data = yaml.safe_load(queue_file.read_text(encoding="utf-8")) or {}
    entries = queue_data.get("retire_posts") or []

    if not entries:
        log.info("Nothing to retire. retire_posts list is empty.")
        return

    errors = 0
    for entry in entries:
        source_url = entry.get("url", "").strip()
        dest_url = entry.get("redirect_to", "").strip()
        reason = entry.get("reason", "consolidated").strip()

        if not source_url or not dest_url:
            log.warning("Skipping incomplete entry: %s", entry)
            errors += 1
            continue

        ok = retire_post(source_url, dest_url, reason, root, dry_run=args.dry_run)
        if not ok:
            errors += 1

    if errors:
        log.error("%d error(s) encountered.", errors)
        sys.exit(1)
    else:
        log.info("All retirements completed successfully.")


if __name__ == "__main__":
    main()
