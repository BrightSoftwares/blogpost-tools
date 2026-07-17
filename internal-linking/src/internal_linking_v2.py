"""Internal Linking v2 — main entry point.

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md.

Current scope: Phase 0 (bootstrap/config) + Phase 1 (post index building)
+ Phase 2 (keyword extraction) + Phase 3 (link opportunity scoring +
distribution constraints) + Phase 4 (wikilink insertion) + Phase 5
(existing link migration) — all in-memory only. Phase 6 (output/reporting
— writing modified posts and CSV reports to disk) is NOT implemented here
— a later task. This entry point therefore builds the index, extracts
keywords, migrates existing internal markdown links, computes and inserts
new wikilinks *in memory* for every eligible-length source post, logs a
summary of what *would* change, and exits without writing any files.

Per the spec, Phase 5 (migration) runs before Phase 3 (new-link scoring)
for each source post, so newly-migrated wikilinks are already present in
the body Phase 3 scans — a link the migration just converted must not
also be treated as a fresh insertion opportunity.

CLI flags below cover Phase 0-5 (config bootstrap, where to scan, which
language, the target-eligibility cutoff date, logging, the Phase 3/4
constraint/strategy knobs, and ``--migrate/--no-migrate`` for Phase 5).
Flags tied exclusively to Phase 6 (e.g. --dry-run, --report-only) are
intentionally left out of this CLI for now; ``config.py``'s schema
already defines them (with defaults) so a future task can wire them in
without changing the config layer. ``--mode`` (full/migrate-only/audit)
is likewise deferred — ``--migrate/--no-migrate`` covers this task's
actual need (an on/off switch for Phase 5) without committing to the
full mode semantics before Phase 6 exists to make "migrate-only"/"audit"
meaningful.

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
from indexer import build_post_index, count_words
from inserter import insert_wikilinks
from keywords import extract_keywords, get_spacy_model_for_lang
from migrator import migrate_existing_links
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
    "--migrate/--no-migrate",
    "migrate",
    default=None,
    help="Migrate existing internal markdown links to wikilinks (Phase 5). Defaults to config's `skip_migration` setting (migration ON) when not passed.",
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
    migrate: bool,
    log_level: str,
    log_file: str,
) -> None:
    """Build the post index, extract keywords, migrate existing links, and compute+insert new wikilinks in memory.

    Phase 1-5 only: no files are written (Phase 6 reporting/output is not
    implemented yet).
    """
    cli_overrides: Dict[str, Any] = {
        "posts_dir": posts_dir,
        "seo_dir": seo_dir,
        "lang": lang,
        "future_cutoff_date": future_cutoff_date,
        "max_links_per_post": max_links_per_post,
        "min_post_length_words": min_post_length_words,
        "skip_migration": (not migrate) if migrate is not None else None,
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

    # Phase 5 + Phase 3 + 4 (in-memory only — Phase 6 output/reporting is
    # not implemented yet, so nothing is written to disk here). Phase 5
    # runs first per the spec, so any link it migrates is already a
    # wikilink by the time Phase 3 scans the body for new opportunities.
    min_length = config["min_post_length_words"]
    posts_migrated = 0
    total_migrated_links = 0
    posts_with_new_links = 0
    total_new_links = 0

    for slug, source_post in index.items():
        if not config["skip_migration"]:
            migrated_body, was_migrated, migration_log = migrate_existing_links(source_post, index)
            if was_migrated:
                source_post.body = migrated_body
                # Recompute word count: Phase 3's link-density constraint
                # (scoring.apply_distribution_constraints) and the
                # min-length skip below both key off body_word_count, which
                # was only ever set once at Phase 1 indexing — leaving it
                # stale here would score Phase 3 against a word count that
                # no longer matches the (now-migrated) body.
                source_post.body_word_count = count_words(migrated_body)
                posts_migrated += 1
                total_migrated_links += len(migration_log)
                logger.debug(f"  {slug}: {len(migration_log)} link(s) would migrate")

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
        f"Phase 5 complete (in-memory): {posts_migrated} post(s) would have "
        f"{total_migrated_links} existing link(s) migrated to wikilinks."
    )
    logger.info(
        f"Phase 3-4 complete (in-memory): {posts_with_new_links} post(s) would gain "
        f"{total_new_links} new wikilink(s). Phase 6 (reporting/writing modified posts to "
        "disk) is not yet implemented; no files were written."
    )


if __name__ == "__main__":
    main()
