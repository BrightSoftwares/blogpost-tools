#!/usr/bin/env python3
"""
Jekyll slug-conflict verifier.

Re-scans a `_posts` directory after `bulk_resolver.py` has run and confirms
no two posts still share the same `ref:` front-matter value. Exits non-zero
if conflicts remain, so it can be used as a CI gate (see the companion
`slug-conflict-audit.yml` idea in the README — not wired up automatically by
this script; add it to your own workflow if useful).

Usage:
    python3 verify_no_conflicts.py --posts-dir fr/_posts
"""

import argparse
import logging
import os
import re
import sys
from collections import defaultdict

log = logging.getLogger("verify_no_conflicts")

REF_PATTERN = re.compile(r"^ref:\s*(.+)$", re.MULTILINE)


def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


def find_remaining_conflicts(posts_dir: str) -> dict:
    by_ref = defaultdict(list)
    for filename in sorted(os.listdir(posts_dir)):
        if not filename.endswith((".md", ".markdown")):
            continue
        filepath = os.path.join(posts_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        match = REF_PATTERN.search(content)
        if match:
            by_ref[match.group(1).strip()].append(filename)
    return {ref: files for ref, files in by_ref.items() if len(files) > 1}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--posts-dir", required=True, help="Path to a Jekyll _posts directory")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    if not os.path.isdir(args.posts_dir):
        log.error("Posts directory not found: %s", args.posts_dir)
        return 1

    remaining = find_remaining_conflicts(args.posts_dir)

    if not remaining:
        log.info("No duplicate ref: values found in %s.", args.posts_dir)
        return 0

    log.error("Found %d ref: values with duplicate posts:", len(remaining))
    for ref, files in remaining.items():
        log.error("  ref '%s': %s", ref, ", ".join(files))
    return 1


if __name__ == "__main__":
    sys.exit(main())
