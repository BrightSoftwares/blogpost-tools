"""Phase 6 — Output & Reporting.

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md
(Section 1 "Phase 6 — Output & Reporting").

Writes migrated/inserted post bodies back to their source files (unless
running in dry-run or report-only mode) and produces two CSV reports:
``change_report.csv`` (every Phase 4/5 change made this run) and
``aliases.csv`` (every keyword -> target mapping, v1-compatible columns
for downstream consumers per the spec).

Deviation from the spec's literal ``serialize_frontmatter(fm)``
pseudocode: ``PostMetadata.frontmatter`` is a plain dict parsed once at
Phase 1 indexing, and round-tripping it back through a YAML dumper would
reorder keys and normalize quoting/formatting — a noisy, unreviewable
diff across many posts for content that only actually changed in the
body. Instead, ``write_modified_posts`` re-reads each file's ORIGINAL
frontmatter block verbatim (byte-for-byte, via the same ``---`` delimiter
Jekyll/python-frontmatter use) and only replaces the body, so the diff a
human reviews is exactly the link changes and nothing else.
"""

from __future__ import annotations

import csv
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from models import PostMetadata

logger = logging.getLogger(__name__)

_FRONTMATTER_BLOCK_RE = re.compile(r"\A---\r?\n.*?\r?\n(?:---|\.\.\.)\r?\n?", re.DOTALL)


def _read_raw_frontmatter_block(filepath: Path) -> str:
    """Return the original file's frontmatter block, byte-for-byte.

    Returns an empty string if the file has no ``---``-delimited
    frontmatter block at all (shouldn't happen for a real Jekyll post,
    but fail safe rather than crash a whole run over one file) or if it
    can no longer be read.

    Args:
        filepath: Path to the original post file (re-read fresh — the
            in-memory ``PostMetadata`` never stores the raw frontmatter
            text, only the parsed dict).

    Returns:
        The frontmatter block including both ``---`` delimiters and the
        trailing newline, or ``""``.
    """
    try:
        raw = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        logger.warning(f"Could not re-read {filepath} for frontmatter preservation: {e}")
        return ""
    match = _FRONTMATTER_BLOCK_RE.match(raw)
    return match.group(0) if match else ""


def write_modified_posts(modified_posts: List[Tuple[Path, str]]) -> None:
    """Write each modified post's body back to its source file.

    Args:
        modified_posts: ``(filepath, modified_body)`` pairs for every
            source post whose body changed this run.
    """
    for filepath, modified_body in modified_posts:
        frontmatter_block = _read_raw_frontmatter_block(filepath)
        # python-frontmatter's Post.content strips the trailing newline at
        # parse time (indexer.py's `body = parsed.content`), so every
        # in-memory body this pipeline works with is already missing it —
        # verified live: `frontmatter.loads("---\ntitle: T\n---\nLine one.\n").content`
        # returns "Line one." with no trailing \n. That's invisible until
        # something actually writes the file back to disk, which only
        # happens here — restore exactly one trailing newline so files
        # keep ending the way a normal editor / git / Jekyll expects.
        new_content = frontmatter_block + modified_body.rstrip("\n") + "\n"
        filepath.write_text(new_content, encoding="utf-8")
        logger.info(f"Wrote {filepath}")


def write_change_report(entries: List[Dict[str, Any]], output_path: str) -> None:
    """Write the Phase 4/5 change report CSV.

    Columns match the spec: source_file, target_slug, anchor_text,
    position, score, link_type, source_tier, timestamp. Phase 4 (new
    insertions, ``inserter.insert_wikilinks``) and Phase 5 (migrations,
    ``migrator.migrate_existing_links``) log entries use different key
    names and shapes — normalized here into the report's column set
    rather than forcing both phases onto one dict shape upstream (Phase
    5 has no position/score/source_tier concept; Phase 4 has no
    original_url). Missing fields are written as empty cells.

    Args:
        entries: Raw log-entry dicts from Phase 4 and/or Phase 5.
        output_path: File path to write the CSV to.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()

    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source_file",
                "target_slug",
                "anchor_text",
                "position",
                "score",
                "link_type",
                "source_tier",
                "timestamp",
            ],
        )
        writer.writeheader()
        for entry in entries:
            writer.writerow(
                {
                    "source_file": entry.get("source", ""),
                    "target_slug": entry.get("target", ""),
                    "anchor_text": entry.get("anchor", ""),
                    "position": entry.get("position", ""),
                    "score": entry.get("score", ""),
                    "link_type": entry.get("link_type", ""),
                    "source_tier": entry.get("source_tier", ""),
                    "timestamp": timestamp,
                }
            )
    logger.info(f"Wrote change report ({len(entries)} entries) to {out}")


def write_aliases_csv(target_index: Dict[str, PostMetadata], output_path: str) -> None:
    """Write the v1-compatible aliases.csv: keyword,target_slug,target_url,specificity.

    One row per (post, keyword) pair for every keyword any eligible post
    carries — regardless of whether it was actually used as a link this
    run — matching v1's downstream-consumer contract (spec: "aliases.csv
    MUST be written with the same columns as v1").

    Args:
        target_index: Full post index (``indexer.build_post_index()``
            output, with ``keywords`` populated by Phase 2).
        output_path: File path to write the CSV to.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "target_slug", "target_url", "specificity"])
        for slug, post in target_index.items():
            for keyword, specificity, _source_tier in post.keywords:
                writer.writerow([keyword, slug, post.url_path, specificity])
    logger.info(f"Wrote aliases.csv to {out}")


def write_outputs(
    modified_posts: List[Tuple[Path, str]],
    all_log_entries: List[Dict[str, Any]],
    target_index: Dict[str, PostMetadata],
    config: Dict[str, Any],
) -> None:
    """Phase 6 orchestrator — dry-run / report-only / live-write modes.

    Args:
        modified_posts: ``(filepath, modified_body)`` pairs for every
            source post whose body changed this run (Phase 4 insertions
            and/or Phase 5 migrations already applied in memory).
        all_log_entries: Combined Phase 4 + Phase 5 log entries.
        target_index: Full post index (for aliases.csv).
        config: Bootstrapped config dict — reads ``dry_run``,
            ``report_only``, ``write_aliases_csv``, ``seo_dir``.
    """
    if config.get("dry_run"):
        for filepath, _modified_body in modified_posts:
            logger.info(f"DRY RUN: would modify {filepath}")
        logger.info(f"DRY RUN: would modify {len(modified_posts)} post(s); no files written.")
        return

    if config.get("report_only"):
        write_change_report(all_log_entries, str(Path(config["seo_dir"]) / "audit_report.csv"))
        logger.info("REPORT ONLY: wrote audit_report.csv; no post files modified.")
        return

    write_modified_posts(modified_posts)

    if config.get("write_aliases_csv", True):
        write_aliases_csv(target_index, str(Path(config["seo_dir"]) / "aliases.csv"))

    write_change_report(all_log_entries, str(Path(config["seo_dir"]) / "change_report.csv"))

    logger.info(f"Modified {len(modified_posts)} post(s); wrote reports to {config['seo_dir']}")
