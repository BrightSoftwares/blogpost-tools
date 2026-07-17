"""Phase 5 — Existing Link Migration.

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md
(Section 1 "Phase 5 — Existing Link Migration").

Rewrites existing markdown links (``[text](url)``) that point at another
post in the index into wikilinks (``[[slug]]`` or ``[[slug|text]]``),
matching the same anchor-equals-slug convention ``inserter.py`` (Phase 4)
already uses for newly-inserted links. External links, image links
(``![...](...)``), and links inside code blocks are left untouched;
links that cannot be resolved to a post in the index, or that resolve to
an ineligible target (future/unpublished/redirect), are also left as-is
(logged, not migrated).

Deliberately out of scope here, matching the same "compute in memory,
change nothing on disk" pattern ``internal_linking_v2.py`` already uses
for Phase 3/4: writing the migrated body back to the post file and
producing the ``change_report.csv``/``aliases.csv`` outputs are Phase 6
(not yet implemented — a later task).
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from keywords import normalize
from models import PostMetadata
from text_utils import MARKDOWN_LINK_RE, compute_code_regions, is_inside_any_region

logger = logging.getLogger(__name__)

_EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "ftp://", "#")
_EXTENSION_SUFFIX = (".md", ".markdown", ".html")
_DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-(.+)$")


def _find_case_insensitive(candidate: str, target_index: Dict[str, PostMetadata]) -> str | None:
    """Return the index key matching ``candidate`` case-insensitively, or None.

    ``indexer.py``'s slug extraction does not lowercase filenames (a post
    filed as ``2024-01-01-Install-Nginx.md`` is indexed under the literal
    key ``"Install-Nginx"``), so a direct-key lookup on a lowercased URL
    candidate can miss a real match. Callers try the exact-case lookup
    first (cheap dict hit for the common all-lowercase case) and fall back
    to this linear case-insensitive scan only when that misses.
    """
    lower_candidate = candidate.lower()
    for slug in target_index:
        if slug.lower() == lower_candidate:
            return slug
    return None


def resolve_url_to_slug(url: str, target_index: Dict[str, PostMetadata]) -> str | None:
    """Resolve an existing link's URL to a slug already present in the index.

    Tries, in order: (1) the last path segment as a direct slug match,
    (2) a full-path match against any indexed post's ``url_path``, (3) a
    ``YYYY-MM-DD-slug`` filename-style prefix stripped down to its slug.
    Each strategy tries an exact-case match first, then falls back to a
    case-insensitive match (slugs are not guaranteed lowercase — see
    ``_find_case_insensitive``). URL fragments (``#section``) and query
    strings (``?x=y``) are stripped before segmenting, so an anchor link
    into another post (``/other-post/#section``) still resolves to that
    post's slug.

    Args:
        url: The raw URL/path from an existing markdown link.
        target_index: Full post index (``indexer.build_post_index()`` output).

    Returns:
        The matching slug, or None if no post in the index resolves to this URL.
    """
    cleaned = url.strip().split("#", 1)[0].split("?", 1)[0].strip("/")
    for suffix in _EXTENSION_SUFFIX:
        if cleaned.lower().endswith(suffix):
            cleaned = cleaned[: -len(suffix)]
            break

    segments = [s for s in cleaned.split("/") if s]
    candidate = segments[-1] if segments else ""

    if candidate in target_index:
        return candidate
    match = _find_case_insensitive(candidate, target_index)
    if match is not None:
        return match

    normalized_url = "/" + cleaned.lower() + "/" if cleaned else "/"
    for slug, post in target_index.items():
        if post.url_path.strip("/").lower() == normalized_url.strip("/").lower():
            return slug

    date_match = _DATE_PREFIX_RE.match(candidate)
    if date_match:
        date_slug = date_match.group(1)
        if date_slug in target_index:
            return date_slug
        match = _find_case_insensitive(date_slug, target_index)
        if match is not None:
            return match

    return None


def migrate_existing_links(
    source_post: PostMetadata, target_index: Dict[str, PostMetadata]
) -> Tuple[str, bool, List[Dict[str, Any]]]:
    """Migrate a post's existing internal markdown links to wikilinks (Phase 5).

    Args:
        source_post: The post whose ``body`` will be scanned (read-only;
            the modified body is returned, not written back onto the
            dataclass instance).
        target_index: Full post index, used to resolve link URLs to slugs
            and to check target eligibility.

    Returns:
        Tuple of (modified_body, modified, migration_log). ``migration_log``
        entries match the same dict shape ``inserter.insert_wikilinks``
        produces, plus ``original_url`` and ``link_type`` set to
        ``"migrated"`` (vs. ``"new"`` for Phase 4 insertions), matching the
        spec's Phase 5 pseudocode and the ``ChangeLogEntry`` fields Phase 6
        will eventually read.
    """
    body = source_post.body
    if not body:
        return body, False, []

    code_regions = compute_code_regions(body)
    modified = False
    migration_log: List[Dict[str, Any]] = []

    matches = list(MARKDOWN_LINK_RE.finditer(body))
    for match in reversed(matches):
        anchor_text = match.group(1)
        url = match.group(2)

        if urlparse(url).scheme or url.startswith(_EXTERNAL_PREFIXES):
            continue
        if match.start() > 0 and body[match.start() - 1] == "!":
            continue
        if is_inside_any_region(match.start(), match.end(), code_regions):
            continue

        resolved_slug = resolve_url_to_slug(url, target_index)
        if resolved_slug is None:
            logger.debug(f"Could not resolve internal link {url} in {source_post.slug}")
            continue

        target = target_index.get(resolved_slug)
        if target is not None and not target.eligible_as_target:
            logger.warning(
                f"Post {source_post.slug} links to ineligible post "
                f"{resolved_slug} ({target.exclusion_reason.value})"
            )
            continue

        if normalize(anchor_text) == normalize(resolved_slug.replace("-", " ")):
            replacement = f"[[{resolved_slug}]]"
        else:
            replacement = f"[[{resolved_slug}|{anchor_text}]]"

        body = body[: match.start()] + replacement + body[match.end() :]
        modified = True
        migration_log.append(
            {
                "source": source_post.slug,
                "target": resolved_slug,
                "anchor": anchor_text,
                "original_url": url,
                "link_type": "migrated",
            }
        )

    return body, modified, migration_log
