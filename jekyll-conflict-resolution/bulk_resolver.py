#!/usr/bin/env python3
"""
Jekyll slug-conflict bulk resolver.

Applies resolutions produced by `conflict_analyzer.py` (or a hand-written
resolutions file in the same shape) to a Jekyll `_posts` directory:

  - "delete": removes the file (used for IDENTICAL conflicts — keep newest).
  - "rename": renames the file and rewrites its `ref:` front-matter to a new,
    unique slug (used for MINOR_UPDATE / DIFFERENT conflicts).

Always run with --dry-run first. This script does not decide *which*
resolution to apply — that is an editorial judgment call a human or an AI
session makes by reading `conflict_analyzer.py`'s report; this script only
executes a decision that has already been made.

Resolutions file format (JSON):
{
  "deletes": ["2020-01-01-old-post.md", "..."],
  "renames": {
    "2020-01-01-old-slug.md": {
      "new_filename": "2020-01-01-new-descriptive-slug.md",
      "new_ref": "new-descriptive-slug"
    }
  }
}

Usage:
    python3 bulk_resolver.py --posts-dir fr/_posts --resolutions resolutions.json --dry-run
    python3 bulk_resolver.py --posts-dir fr/_posts --resolutions resolutions.json --apply
"""

import argparse
import json
import logging
import os
import re
import sys

log = logging.getLogger("bulk_resolver")

REF_PATTERN = re.compile(r"^ref:\s*(.+)$", re.MULTILINE)


def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


def apply_deletes(posts_dir: str, deletes: list, dry_run: bool) -> int:
    count = 0
    for filename in deletes:
        filepath = os.path.join(posts_dir, filename)
        if not os.path.exists(filepath):
            log.warning("Skip delete (not found): %s", filepath)
            continue
        if dry_run:
            log.info("[dry-run] Would delete: %s", filepath)
        else:
            os.remove(filepath)
            log.info("Deleted: %s", filepath)
        count += 1
    return count


def _resolve_within(posts_dir: str, filename: str) -> str:
    """Join posts_dir + filename and reject the result if it escapes posts_dir (2026-09-19
    fix). A resolutions file is caller-supplied JSON; an unvalidated os.path.join lets a
    '../'-style or absolute filename write/delete outside the intended directory entirely
    (an absolute filename silently discards posts_dir in os.path.join outright)."""
    base = os.path.abspath(posts_dir)
    resolved = os.path.abspath(os.path.join(base, filename))
    if os.path.commonpath([base, resolved]) != base:
        raise ValueError(f"{filename!r} resolves outside posts_dir ({posts_dir!r}) — refusing")
    return resolved


def apply_renames(posts_dir: str, renames: dict, dry_run: bool) -> int:
    # Pre-validate every entry (path traversal, cross-entry target collisions) before any
    # write happens (2026-09-19 fix) — a bad entry must never leave a partial rename applied.
    resolved = {}
    targets_seen = {}
    for old_filename, spec in renames.items():
        new_filename = spec["new_filename"]
        old_path = _resolve_within(posts_dir, old_filename)
        new_path = _resolve_within(posts_dir, new_filename)
        if new_path in targets_seen:
            raise ValueError(
                f"Resolutions file has two renames targeting the same file "
                f"({new_filename!r}): {targets_seen[new_path]!r} and {old_filename!r}"
            )
        targets_seen[new_path] = old_filename
        resolved[old_filename] = (old_path, new_path, new_filename, spec["new_ref"])

    count = 0
    for old_filename, (old_path, new_path, new_filename, new_ref) in resolved.items():
        if not os.path.exists(old_path):
            log.warning("Skip rename (source not found): %s", old_path)
            continue

        same_path = os.path.normpath(old_path) == os.path.normpath(new_path)
        if not same_path and os.path.exists(new_path):
            log.warning("Skip rename (target already exists): %s -> %s", old_filename, new_filename)
            continue

        with open(old_path, "r", encoding="utf-8") as f:
            content = f.read()

        old_ref_match = REF_PATTERN.search(content)
        old_ref = old_ref_match.group(1).strip() if old_ref_match else None

        if old_ref:
            content = REF_PATTERN.sub(f"ref: {new_ref}", content, count=1)
        else:
            log.warning("%s has no ref: field to update", old_filename)

        if dry_run:
            log.info("[dry-run] Would rename: %s -> %s (ref: %s -> %s)", old_filename, new_filename, old_ref, new_ref)
        else:
            with open(new_path, "w", encoding="utf-8") as f:
                f.write(content)
            # 2026-09-19 fix: new_filename == old_filename used to write then immediately
            # os.remove the same path it just wrote, deleting the file entirely.
            if not same_path:
                os.remove(old_path)
            log.info("Renamed: %s -> %s (ref: %s -> %s)", old_filename, new_filename, old_ref, new_ref)
        count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--posts-dir", required=True, help="Path to a Jekyll _posts directory")
    parser.add_argument("--resolutions", required=True, help="Path to a resolutions JSON file (see module docstring)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Print what would happen without changing files")
    mode.add_argument("--apply", action="store_true", help="Actually delete/rename files")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    if not os.path.isdir(args.posts_dir):
        log.error("Posts directory not found: %s", args.posts_dir)
        return 1
    if not os.path.isfile(args.resolutions):
        log.error("Resolutions file not found: %s", args.resolutions)
        return 1

    with open(args.resolutions, "r", encoding="utf-8") as f:
        resolutions = json.load(f)

    dry_run = args.dry_run
    deleted = apply_deletes(args.posts_dir, resolutions.get("deletes", []), dry_run)
    renamed = apply_renames(args.posts_dir, resolutions.get("renames", {}), dry_run)

    log.info(
        "%s: %d deleted, %d renamed",
        "Dry-run complete" if dry_run else "Done",
        deleted,
        renamed,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
