"""Phase 1 — Post index building.

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md
(Section 1 "Phase 1 — Index Building" and Section 2 "Frontmatter
Considerations").

Scans a single Jekyll ``posts_dir`` (e.g. ``_posts/en/``) for ``*.md`` /
``*.markdown`` files and builds a ``{slug: PostMetadata}`` index, flagging
each post as eligible or ineligible as a link *target* (Phase 3+ concern;
posts are never excluded here as link *sources*).

Two points where this module resolves a gap left open by the spec's
pseudocode (documented inline at the point of decision):

1. The pseudocode's ``eligible_as_target`` formula only accounts for
   ``is_future``, ``is_unpublished``, ``is_redirect``, and
   ``lang_mismatch`` — it never guards against a post with no resolvable
   date at all, even though ``ExclusionReason.NO_DATE`` exists and
   Section 2's eligibility table lists "Date present" as a check. Without
   a guard, comparing ``None > cutoff_date`` would raise. This
   implementation adds a ``no_date`` flag to the eligibility formula and
   to ``compute_exclusion_reason()``.
2. The spec's ``build_post_index(posts_dir, lang, cutoff_date)`` signature
   (also used verbatim in the spec's mandatory Test 1) takes no config
   object, so ``config.include_unpublished`` is intentionally NOT wired
   in here — an unpublished post is always excluded as a target
   regardless of that config flag. This mirrors the given function
   signature; wiring ``include_unpublished`` through would require
   widening the signature, which is left for a future task if wanted.
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import frontmatter
import yaml

from models import ExclusionReason, PostMetadata

logger = logging.getLogger(__name__)

_FILENAME_DATE_SLUG_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)$")


def extract_slug_from_filename(filepath: Path) -> str:
    """Extract the slug from a Jekyll post filename.

    Filename format: ``YYYY-MM-DD-slug.md`` -> ``"slug"``. If the
    filename has no date prefix, the stem itself (minus extension) is
    used as the slug.

    Args:
        filepath: Path to the post file.

    Returns:
        The slug string.
    """
    stem = Path(filepath).stem
    match = _FILENAME_DATE_SLUG_RE.match(stem)
    if match:
        return match.group(2)
    return stem


def extract_date_from_filename(filepath: Path) -> Optional[date]:
    """Extract the ``YYYY-MM-DD`` date prefix from a Jekyll post filename.

    Args:
        filepath: Path to the post file.

    Returns:
        Parsed date, or None if the filename has no date prefix.
    """
    stem = Path(filepath).stem
    match = _FILENAME_DATE_SLUG_RE.match(stem)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None


def _coerce_to_date(value: Any) -> Optional[date]:
    """Normalize a frontmatter date value (date/datetime/str) to a date."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"Could not parse frontmatter date string: {value!r}")
            return None
    logger.warning(f"Unrecognized frontmatter date type: {type(value)!r}")
    return None


def _coerce_to_list(value: Any) -> List[str]:
    """Normalize a frontmatter tags/categories value to a list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return [str(value)]


def compute_exclusion_reason(
    is_future: bool,
    is_unpublished: bool,
    is_redirect: bool,
    lang_mismatch: bool,
    no_date: bool = False,
) -> ExclusionReason:
    """Determine the single exclusion reason to report for a post.

    Precedence (first match wins) when multiple flags are true:
    no_date > future_date > unpublished > redirect > lang_mismatch > none.
    ``no_date`` is checked first because ``is_future`` cannot be reliably
    computed without a date. This precedence order is not specified by
    the spec verbatim and is a reasonable resolution chosen here.

    Args:
        is_future: True if the post's date is after the cutoff date.
        is_unpublished: True if ``published: false`` in frontmatter.
        is_redirect: True if the post has ``redirect_to``/``redirect_from_only``.
        lang_mismatch: True if the post's ``lang`` differs from the configured lang.
        no_date: True if no date could be resolved from frontmatter or filename.

    Returns:
        The applicable ExclusionReason (NONE if none apply).
    """
    if no_date:
        return ExclusionReason.NO_DATE
    if is_future:
        return ExclusionReason.FUTURE_DATE
    if is_unpublished:
        return ExclusionReason.UNPUBLISHED
    if is_redirect:
        return ExclusionReason.REDIRECT
    if lang_mismatch:
        return ExclusionReason.LANG_MISMATCH
    return ExclusionReason.NONE


def compute_jekyll_permalink(fm: Dict[str, Any], post_date: Optional[date], slug: str) -> str:
    """Compute the Jekyll URL path for a post.

    Uses an explicit ``permalink:`` frontmatter field if present;
    otherwise falls back to the default Jekyll date-based pattern
    ``/YYYY/MM/DD/slug/``, or ``/slug/`` if no date is available.

    Args:
        fm: Post frontmatter dict.
        post_date: Resolved post date (may be None).
        slug: Post slug.

    Returns:
        URL path string.
    """
    explicit = fm.get("permalink")
    if explicit:
        return str(explicit)

    if post_date is not None:
        return f"/{post_date.year:04d}/{post_date.month:02d}/{post_date.day:02d}/{slug}/"

    return f"/{slug}/"


def count_words(body: str) -> int:
    """Count whitespace-delimited words in a post body.

    Args:
        body: Post body text (frontmatter already stripped).

    Returns:
        Word count.
    """
    return len(body.split())


def build_post_index(posts_dir: str, lang: str, cutoff_date: date) -> Dict[str, PostMetadata]:
    """Build the post index for a single ``posts_dir`` (Phase 1).

    Scans ``posts_dir`` for ``*.md`` and ``*.markdown`` files (no
    recursion into subdirectories, matching the spec's pseudocode, which
    globs only the given directory). Posts with malformed YAML
    frontmatter are logged and skipped (never added to the index).

    Args:
        posts_dir: Directory containing Jekyll post markdown files.
        lang: Configured site/section language (e.g. "en"). Used to flag
            ``lang_mismatch`` against each post's own ``lang:`` field.
        cutoff_date: Posts dated after this date are flagged as
            ``future_date`` (not eligible as link targets).

    Returns:
        Dict mapping slug -> PostMetadata for every successfully parsed
        post (including ineligible ones — callers filter on
        ``eligible_as_target``).
    """
    index: Dict[str, PostMetadata] = {}
    posts_path = Path(posts_dir)

    all_posts = sorted(posts_path.glob("*.md")) + sorted(posts_path.glob("*.markdown"))

    for filepath in all_posts:
        try:
            raw = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            logger.warning(f"Skipping unreadable file (bad encoding): {filepath} — {e}")
            continue

        try:
            parsed = frontmatter.loads(raw)
        except yaml.YAMLError as e:
            logger.warning(f"Skipping malformed frontmatter: {filepath} — {e}")
            continue

        fm = parsed.metadata
        body = parsed.content

        slug = extract_slug_from_filename(filepath)

        post_date = _coerce_to_date(fm.get("date"))
        if post_date is None:
            post_date = extract_date_from_filename(filepath)

        no_date = post_date is None
        is_future = (not no_date) and post_date > cutoff_date
        is_unpublished = fm.get("published", True) is False
        is_redirect = bool(fm.get("redirect_to")) or bool(fm.get("redirect_from_only"))
        post_lang = fm.get("lang", lang)
        lang_mismatch = lang is not None and post_lang != lang

        eligible_as_target = not (is_future or is_unpublished or is_redirect or lang_mismatch or no_date)

        index[slug] = PostMetadata(
            slug=slug,
            filepath=filepath,
            title=fm.get("title", slug.replace("-", " ").title()),
            date=post_date,
            tags=_coerce_to_list(fm.get("tags")),
            categories=_coerce_to_list(fm.get("categories")),
            lang=post_lang,
            body=body,
            body_word_count=count_words(body),
            eligible_as_target=eligible_as_target,
            exclusion_reason=compute_exclusion_reason(
                is_future, is_unpublished, is_redirect, lang_mismatch, no_date
            ),
            url_path=compute_jekyll_permalink(fm, post_date, slug),
            frontmatter=fm,
        )

    eligible_count = sum(1 for post in index.values() if post.eligible_as_target)
    logger.info(f"Indexed {len(index)} posts; {eligible_count} eligible as link targets")

    return index
