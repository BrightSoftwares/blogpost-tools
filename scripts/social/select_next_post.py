"""Select the next blog post to schedule for social publishing."""

from __future__ import annotations

import logging
import re
from pathlib import Path

import frontmatter

logger = logging.getLogger(__name__)

_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")
_SCHEDULED_STATUSES = {"draft", "approved", "published"}


def _slug_from_path(path: Path) -> str:
    """Derive slug from filename: strip YYYY-MM-DD- prefix and extension."""
    stem = path.stem
    return _DATE_PREFIX.sub("", stem)


def select_next_post(
    posts_dir: Path,
    schedule: list[dict],
    target_slug: str | None = None,
) -> dict | None:
    """Pick the next blog post to schedule.

    If target_slug is given, return that post regardless of schedule status.
    Otherwise return the oldest eligible post (by mtime then filename) where:
      - frontmatter has ``auto_social: true``
      - slug not already in schedule with status in (draft, approved, published)

    Returns a dict with keys: slug, blog_path, frontmatter, body.
    Returns None if no eligible post found.
    """
    if not posts_dir.is_dir():
        logger.info("No posts found in %s", posts_dir)
        return None

    md_files = sorted(posts_dir.rglob("*.md"), key=lambda p: (p.stat().st_mtime, p.name))

    if not md_files:
        logger.info("No posts found in %s", posts_dir)
        return None

    scheduled_slugs = {
        entry["slug"]
        for entry in schedule
        if entry.get("status") in _SCHEDULED_STATUSES
    }

    for path in md_files:
        post = frontmatter.load(str(path))
        slug = post.metadata.get("slug") or _slug_from_path(path)

        if target_slug is not None:
            if slug == target_slug:
                return {
                    "slug": slug,
                    "blog_path": str(path),
                    "frontmatter": post.metadata,
                    "body": post.content,
                }
            continue

        if not post.metadata.get("auto_social", False):
            continue
        if slug in scheduled_slugs:
            continue

        logger.info("Selected post: %s (%s)", slug, path)
        return {
            "slug": slug,
            "blog_path": str(path),
            "frontmatter": post.metadata,
            "body": post.content,
        }

    if target_slug is not None:
        raise FileNotFoundError(f"No post with slug={target_slug}")

    logger.info("No eligible post found in %s", posts_dir)
    return None
