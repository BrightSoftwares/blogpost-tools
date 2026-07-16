"""Internal Linking v2 — main entry point.

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md.

Current scope: Phase 0 (bootstrap/config) + Phase 1 (post index building)
+ Phase 2 (keyword extraction) + Phase 3 (link opportunity scoring +
distribution constraints) + Phase 4 (wikilink insertion, in-memory only).
Phase 5 (existing link migration) and Phase 6 (output/reporting — writing
modified posts and CSV reports to disk) are NOT implemented here —
``ilv2k9a3-4`` and later. This entry point therefore builds the index,
extracts keywords, computes and inserts wikilinks *in memory* for every
eligible-length source post, logs a summary of what *would* change, and
exits without writing any files.

CLI flags below cover Phase 0-4 (config bootstrap, where to scan, which
language, the target-eligibility cutoff date, logging, and the Phase 3/4
constraint/strategy knobs). Flags tied exclusively to Phase 5/6 (e.g.
--mode, --dry-run, --report-only, --skip-migration) are intentionally
left out of this CLI for now; ``config.py``'s schema already defines them
(with defaults) so a future task can wire them in without changing the
config layer.

Usage:
    python internal_linking_v2.py --posts-dir _posts/en/ --lang en \\
        --seo-dir _seo/internal-linking/en/ --max-links-per-post 5
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict

import click
import spacy

from config import ConfigError, bootstrap
from indexer import build_post_index
from inserter import insert_wikilinks
from keywords import extract_keywords, get_spacy_model_for_lang
from scoring import apply_distribution_constraints, find_link_opportunities

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
@click.option("--max-links-per-post", default=None, type=int, help="Hard cap on links inserted per source post.")
@click.option(
    "--min-post-length-words", default=None, type=int, help="Skip source posts shorter than this word count."
)
@click.option(
    "--link-density-max", default=None, type=float, help="Max link density (links per word, e.g. 0.05 = 1/20 words)."
)
@click.option(
    "--min-paragraphs-between-links", default=None, type=int, help="Minimum paragraph spacing between links."
)
@click.option("--max-links-per-section", default=None, type=int, help="Maximum links per heading section.")
@click.option(
    "--distribution-strategy",
    default=None,
    type=click.Choice(["spread", "end-heavy", "uniform"], case_sensitive=False),
    help="Link position strategy.",
)
@click.option(
    "--anchor-text-strategy",
    default=None,
    type=click.Choice(["title-priority", "context", "filename"], case_sensitive=False),
    help="Anchor text selection strategy.",
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
    max_links_per_post: int,
    min_post_length_words: int,
    link_density_max: float,
    min_paragraphs_between_links: int,
    max_links_per_section: int,
    distribution_strategy: str,
    anchor_text_strategy: str,
    log_level: str,
    log_file: str,
) -> None:
    """Build the post index, extract keywords, and compute+insert wikilinks in memory.

    Phase 1-4 only: no files are written (Phase 5 migration and Phase 6
    reporting/output are not implemented yet).
    """
    cli_overrides: Dict[str, Any] = {
        "posts_dir": posts_dir,
        "seo_dir": seo_dir,
        "lang": lang,
        "future_cutoff_date": future_cutoff_date,
        "max_links_per_post": max_links_per_post,
        "min_post_length_words": min_post_length_words,
        "link_density_max": link_density_max,
        "min_paragraphs_between_links": min_paragraphs_between_links,
        "max_links_per_section": max_links_per_section,
        "distribution_strategy": distribution_strategy,
        "anchor_text_strategy": anchor_text_strategy,
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

    # Phase 3 + 4 (in-memory only — Phase 5 migration and Phase 6 output
    # are not implemented yet, so nothing is written to disk here).
    min_length = config["min_post_length_words"]
    posts_with_new_links = 0
    total_new_links = 0

    for slug, source_post in index.items():
        word_count = source_post.body_word_count
        if word_count < min_length:
            logger.debug(f"Skipping short source post {slug} ({word_count} words)")
            continue

        opportunities = find_link_opportunities(source_post, index, config)
        selected = apply_distribution_constraints(
            opportunities, config, source_word_count=word_count
        )
        if not selected:
            continue

        modified_body, insert_log = insert_wikilinks(source_post, selected)
        if modified_body != source_post.body:
            posts_with_new_links += 1
            total_new_links += len(insert_log)
            logger.debug(f"  {slug}: {len(insert_log)} new wikilink(s)")

    logger.info(
        f"Phase 3-4 complete (in-memory): {posts_with_new_links} post(s) would gain "
        f"{total_new_links} new wikilink(s). Phase 5 (migration) and Phase 6 (reporting/writing "
        "modified posts to disk) are not yet implemented; no files were written."
    )


if __name__ == "__main__":
    main()
