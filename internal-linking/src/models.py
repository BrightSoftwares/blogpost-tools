"""Shared dataclasses for the Internal Linking v2 pipeline.

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md (Section 5).

Only ``ExclusionReason`` and ``PostMetadata`` are populated by the current
implementation (Phase 1 — indexer.py, Phase 2 — keywords.py). ``Section``,
``LinkOpportunity``, and ``ChangeLogEntry`` are defined here to match the
full spec so Phase 3-6 (scoring, insertion, migration, reporting) can be
added later without changing this module, but nothing in this repo
constructs them yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ExclusionReason(str, Enum):
    """Reason a post is not eligible as a link target.

    NONE means the post is eligible. MALFORMED is defined for completeness
    (matches the spec's enum) but is not actually assigned by the indexer:
    a post with unparsable frontmatter is skipped entirely (never added to
    the index), per the Phase 1 pseudocode.
    """

    NONE = "eligible"
    FUTURE_DATE = "future_date"
    UNPUBLISHED = "unpublished"
    REDIRECT = "redirect"
    LANG_MISMATCH = "lang_mismatch"
    MALFORMED = "malformed_frontmatter"
    NO_DATE = "no_date"


@dataclass
class PostMetadata:
    """Metadata and eligibility for a single blog post.

    Populated by ``indexer.build_post_index()`` (Phase 1). The ``keywords``
    field starts empty and is filled in by ``keywords.extract_keywords()``
    (Phase 2) for posts where ``eligible_as_target`` is True.
    """

    slug: str
    filepath: Path
    title: str
    date: Optional[date]
    tags: List[str]
    categories: List[str]
    lang: str
    body: str
    body_word_count: int
    eligible_as_target: bool
    exclusion_reason: ExclusionReason
    url_path: str
    frontmatter: Dict[str, Any]
    keywords: List[Tuple[str, float, str]] = field(default_factory=list)
    # keywords = [(keyword, specificity, source_tier), ...]


@dataclass(frozen=True)
class Section:
    """A heading-delimited section of a post body.

    Populated by ``text_utils.segment_into_sections()`` (Phase 3, not yet
    implemented). Defined here so Phase 3+ can import it from this module
    without a later breaking change.
    """

    index: int
    heading_level: int  # 0 for pre-first-heading "intro", else 1-6
    heading_text: str
    start_offset: int
    end_offset: int
    paragraph_offsets: List[Tuple[int, int]]  # list of (start, end) per paragraph


@dataclass(frozen=True)
class LinkOpportunity:
    """A candidate wikilink insertion.

    Populated by ``scoring.find_link_opportunities()`` (Phase 3, not yet
    implemented). Defined here so Phase 3+ can import it from this module
    without a later breaking change.
    """

    source_slug: str
    target_slug: str
    keyword: str
    anchor_text: str
    match_start: int
    match_end: int
    section_index: int
    paragraph_index: int
    relative_position: float
    score: float
    source_tier: str  # "title" | "tag" | "filename"


@dataclass
class ChangeLogEntry:
    """One row of the Phase 6 change report.

    Populated by Phase 4 (insertion) and Phase 5 (migration), not yet
    implemented. Defined here so Phase 4+ can import it from this module
    without a later breaking change.
    """

    source_file: str
    target_slug: str
    anchor_text: str
    position: int
    score: float
    link_type: str  # "new" | "migrated"
    source_tier: str
    timestamp: str  # ISO 8601 UTC
