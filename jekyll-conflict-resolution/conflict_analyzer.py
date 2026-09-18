#!/usr/bin/env python3
"""
Jekyll slug-conflict analyzer.

Scans a Jekyll `_posts` directory for duplicate `ref:` values (the same
front-matter slug used by more than one post) and classifies each conflict
as IDENTICAL (near-duplicate content, keep the newest), MINOR_UPDATE (same
topic, meaningfully revised), or DIFFERENT (unrelated posts that happened to
share a slug).

Originally written to resolve 48 duplicate-slug conflicts across ~26 French
posts in BrightSoftwares/corporate-website (see the companion blog post,
"When Content Management Goes Wrong"). Generalized here to work on any
Jekyll `_posts` directory, not just `fr/_posts`.

Usage:
    python3 conflict_analyzer.py --posts-dir fr/_posts
    python3 conflict_analyzer.py --posts-dir en/_posts --identical-threshold 0.97
"""

import argparse
import difflib
import json
import logging
import os
import re
import sys
from collections import defaultdict

log = logging.getLogger("conflict_analyzer")

REF_PATTERN = re.compile(r"^ref:\s*(.+)$", re.MULTILINE)


def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


def extract_content(filepath: str) -> str:
    """Return the post body (everything after the second '---' front-matter delimiter)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("---")
    if len(parts) >= 3:
        return parts[2].strip()
    return content.strip()


def extract_ref(filepath: str) -> str | None:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    match = REF_PATTERN.search(content)
    return match.group(1).strip() if match else None


def find_conflicts(posts_dir: str) -> dict:
    """Group posts in posts_dir by their `ref:` front-matter value."""
    by_ref = defaultdict(list)
    for filename in sorted(os.listdir(posts_dir)):
        if not filename.endswith((".md", ".markdown")):
            continue
        filepath = os.path.join(posts_dir, filename)
        ref = extract_ref(filepath)
        if ref is None:
            continue
        by_ref[ref].append(
            {
                "filename": filename,
                "date": filename[:10],
                "filepath": filepath,
                "size": os.path.getsize(filepath),
            }
        )
    return {ref: posts for ref, posts in by_ref.items() if len(posts) > 1}


def classify_pair(post_a: dict, post_b: dict, identical_threshold: float, minor_threshold: float) -> dict:
    content_a = extract_content(post_a["filepath"])
    content_b = extract_content(post_b["filepath"])
    similarity = difflib.SequenceMatcher(None, content_a, content_b).ratio()

    if similarity >= identical_threshold:
        decision = "IDENTICAL"
        action = f"Keep newest ({post_b['date']}), redirect/delete old ({post_a['date']})"
    elif similarity >= minor_threshold:
        decision = "MINOR_UPDATE"
        action = f"Keep both — rename {post_b['date']} with a descriptive suffix"
    else:
        decision = "DIFFERENT"
        action = f"Keep both — rename {post_b['date']} with a unique slug"

    return {"decision": decision, "action": action, "similarity": similarity}


def analyze(posts_dir: str, identical_threshold: float, minor_threshold: float) -> dict:
    conflicts = find_conflicts(posts_dir)
    report = {"posts_dir": posts_dir, "conflicts": [], "summary": defaultdict(int)}

    for ref, posts in sorted(conflicts.items()):
        sorted_posts = sorted(posts, key=lambda p: p["date"])
        if len(sorted_posts) != 2:
            # More than 2 posts sharing a ref — flag for manual triage rather than
            # guessing which pair to compare.
            report["conflicts"].append(
                {
                    "ref": ref,
                    "decision": "MANUAL_REVIEW_NEEDED",
                    "action": f"{len(sorted_posts)} posts share this ref — needs manual triage",
                    "posts": [p["filename"] for p in sorted_posts],
                }
            )
            report["summary"]["MANUAL_REVIEW_NEEDED"] += 1
            continue

        result = classify_pair(sorted_posts[0], sorted_posts[1], identical_threshold, minor_threshold)
        report["conflicts"].append(
            {
                "ref": ref,
                "decision": result["decision"],
                "action": result["action"],
                "similarity": round(result["similarity"], 4),
                "posts": [p["filename"] for p in sorted_posts],
            }
        )
        report["summary"][result["decision"]] += 1

    report["summary"] = dict(report["summary"])
    report["total_conflicts"] = len(report["conflicts"])
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--posts-dir", required=True, help="Path to a Jekyll _posts directory to scan")
    parser.add_argument(
        "--identical-threshold",
        type=float,
        default=0.95,
        help="Similarity ratio (0-1) above which two posts are considered identical (default: 0.95)",
    )
    parser.add_argument(
        "--minor-threshold",
        type=float,
        default=0.70,
        help="Similarity ratio (0-1) above which two posts are considered a minor update (default: 0.70)",
    )
    parser.add_argument("--output", help="Write the JSON report to this path instead of stdout")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    if not os.path.isdir(args.posts_dir):
        log.error("Posts directory not found: %s", args.posts_dir)
        return 1

    report = analyze(args.posts_dir, args.identical_threshold, args.minor_threshold)
    output_json = json.dumps(report, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        log.info("Wrote report to %s (%d conflicts)", args.output, report["total_conflicts"])
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
