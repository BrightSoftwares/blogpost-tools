"""Internal Linking v2 — main entry point.

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md.

Current scope: Phase 0 (bootstrap/config) + Phase 1 (post index building)
+ Phase 2 (keyword extraction). Phase 3 (link opportunity scoring),
Phase 4 (link insertion), Phase 5 (existing link migration), and Phase 6
(output/reporting) are NOT implemented here — this entry point builds the
index, extracts keywords for every eligible post, logs a summary, and
exits. It does not write any files (no reports, no modified posts).

CLI flags below cover only what Phase 0-2 need (config bootstrap, where
to scan, which language, the target-eligibility cutoff date, and
logging). Flags tied exclusively to Phase 3-6 (e.g. --mode,
--max-links-per-post, --distribution-strategy) are intentionally left out
of this CLI for now; ``config.py``'s schema already defines them (with
defaults) so a future task can wire them in without changing the config
layer.

Usage:
    python internal_linking_v2.py --posts-dir _posts/en/ --lang en \\
        --seo-dir _seo/internal-linking/en/
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict

import click
import spacy

from config import ConfigError, bootstrap
from indexer import build_post_index
from keywords import extract_keywords, get_spacy_model_for_lang

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--config",
    "config_path",
    default="./internal-linking-config.yml",
    show_default=True,
    help="Path to the YAML config file.",
)
@click.option("--posts-dir", default=None, help="Directory containing post markdown files.")
@click.option("--seo-dir", default=None, help="Output directory for reports (required by config, unused until Phase 6).")
@click.option("--lang", default=None, help="Post language: en, fr, es, de, it, pt.")
@click.option(
    "--future-cutoff-date",
    default=None,
    help='Cutoff date for target eligibility ("auto" = today UTC, or YYYY-MM-DD).',
)
@click.option(
    "--log-level",
    default=None,
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    help="Logging level.",
)
@click.option("--log-file", default=None, help="Optional path to a rotating log file.")
def main(
    config_path: str,
    posts_dir: str,
    seo_dir: str,
    lang: str,
    future_cutoff_date: str,
    log_level: str,
    log_file: str,
) -> None:
    """Build the post index (Phase 1) and extract keywords (Phase 2)."""
    cli_overrides: Dict[str, Any] = {
        "posts_dir": posts_dir,
        "seo_dir": seo_dir,
        "lang": lang,
        "future_cutoff_date": future_cutoff_date,
        "log_level": log_level,
        "log_file": log_file,
    }

    try:
        config = bootstrap(config_path, cli_overrides)
    except ConfigError as e:
        # setup_logging() hasn't necessarily run yet if bootstrap failed
        # before reaching it, so fall back to a basic handler here.
        logging.basicConfig(level=logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s")
        logging.error(f"Configuration error: {e}")
        sys.exit(1)

    model_name = get_spacy_model_for_lang(config["lang"])
    logger.info(f"Loading spaCy model: {model_name}")
    nlp = spacy.load(model_name)

    logger.info(f"Building post index from {config['posts_dir']} (cutoff: {config['future_cutoff_date']})")
    index = build_post_index(config["posts_dir"], config["lang"], config["future_cutoff_date"])

    eligible_count = 0
    for post in index.values():
        if post.eligible_as_target:
            post.keywords = extract_keywords(post, nlp)
            eligible_count += 1

    total = len(index)
    excluded = total - eligible_count
    logger.info(f"Indexed {total} posts; {eligible_count} eligible as link targets, {excluded} excluded")

    reason_counts: Dict[str, int] = {}
    for post in index.values():
        if not post.eligible_as_target:
            reason_counts[post.exclusion_reason.value] = reason_counts.get(post.exclusion_reason.value, 0) + 1
    for reason, count in sorted(reason_counts.items()):
        logger.info(f"  excluded ({reason}): {count}")

    shown = 0
    for slug, post in index.items():
        if post.eligible_as_target and post.keywords:
            top_keywords = ", ".join(kw for kw, _score, _source in post.keywords[:5])
            logger.debug(f"  {slug}: {top_keywords}")
            shown += 1
        if shown >= 5:
            break

    logger.info(
        "Phase 1-2 complete. Phase 3-6 (link scoring/insertion/migration/reporting) not yet implemented; "
        "no files were written."
    )


if __name__ == "__main__":
    main()
