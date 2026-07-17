"""Shared text-manipulation helpers for Phase 3 (scoring) and Phase 4 (insertion).

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md
(Section 1 "Phase 3 — Link Opportunity Scoring", "Forbidden Regions
Implementation", and "Section Segmentation").

This module implements the body-parsing primitives that ``scoring.py``
needs: locating forbidden regions (code blocks, existing links, HTML,
Liquid tags) where a new link must never be inserted, splitting a post
body into heading-delimited sections, and splitting a body into
paragraphs (used to enforce the paragraph-spacing distribution
constraints in ``scoring.apply_distribution_constraints``).

Note on paragraph indexing: the spec's pseudocode calls
``section.find_paragraph_index(match.start)`` as if ``Section`` had a
method for it, but ``models.Section`` (Section 5) is a plain frozen
dataclass with no methods, and the distribution-constraint tests
(spec Test 2) compare ``paragraph_index`` values *across different
sections* (e.g. ``paragraph_index=i*5`` for ``section_index=i``),
which only makes sense if paragraph indices are global to the whole
post body, not local to a section. This module therefore computes one
global paragraph list per post (``compute_paragraphs``) and exposes
``find_paragraph_index`` to look up the global index for an offset;
``segment_into_sections`` reuses the same global list to fill each
``Section.paragraph_offsets`` (restricted to that section's range),
so there is a single source of truth for paragraph boundaries.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from models import Section

# --- Forbidden regions (Phase 3, "Forbidden Regions Implementation") ---

_FENCED_CODE_RE = re.compile(r"```[\s\S]*?```")
_INDENTED_CODE_RE = re.compile(r"(?:^|\n)((?:    [^\n]*\n?)+)")
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")  # public: reused by migrator.py (Phase 5)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_LIQUID_TAG_RE = re.compile(r"\{%[^%]*%\}|\{\{[^}]*\}\}")


def merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Merge overlapping/adjacent ``(start, end)`` intervals.

    Args:
        intervals: List of (start, end) offset tuples (need not be sorted).

    Returns:
        Sorted list of non-overlapping (start, end) tuples.
    """
    if not intervals:
        return []
    ordered = sorted(intervals)
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def compute_forbidden_regions(body: str) -> List[Tuple[int, int]]:
    """Return merged ``(start, end)`` offsets where links must NOT be inserted.

    Covers: fenced code blocks, indented code blocks, inline code,
    existing wikilinks, existing markdown links, HTML tags, and Liquid
    tags (``{% ... %}`` / ``{{ ... }}``).

    Args:
        body: Post body text (frontmatter already stripped).

    Returns:
        Sorted list of merged (start, end) offset tuples.
    """
    regions: List[Tuple[int, int]] = []

    for m in _FENCED_CODE_RE.finditer(body):
        regions.append((m.start(), m.end()))
    for m in _INDENTED_CODE_RE.finditer(body):
        regions.append((m.start(1), m.end(1)))
    for m in _INLINE_CODE_RE.finditer(body):
        regions.append((m.start(), m.end()))
    for m in _WIKILINK_RE.finditer(body):
        regions.append((m.start(), m.end()))
    for m in MARKDOWN_LINK_RE.finditer(body):
        regions.append((m.start(), m.end()))
    for m in _HTML_TAG_RE.finditer(body):
        regions.append((m.start(), m.end()))
    for m in _LIQUID_TAG_RE.finditer(body):
        regions.append((m.start(), m.end()))

    return merge_intervals(regions)


def compute_code_regions(body: str) -> List[Tuple[int, int]]:
    """Return merged ``(start, end)`` offsets covering only code (Phase 5).

    A narrower sibling of ``compute_forbidden_regions``: covers fenced,
    indented, and inline code only — NOT existing wikilinks/markdown
    links/HTML/Liquid tags. Phase 5 (``migrator.py``) needs this
    distinction because it operates directly on existing markdown-link
    matches (``[text](url)``); those matches are themselves markdown
    links, so checking them against the full forbidden-region list from
    ``compute_forbidden_regions`` (which includes every markdown link)
    would make every migration candidate trivially overlap its own
    region and never migrate. This function answers only "is this span
    inside a code block?", which is the one code-block check Phase 5's
    spec pseudocode (``is_inside_code_block``) actually needs.

    Args:
        body: Post body text (frontmatter already stripped).

    Returns:
        Sorted list of merged (start, end) offset tuples.
    """
    regions: List[Tuple[int, int]] = []

    for m in _FENCED_CODE_RE.finditer(body):
        regions.append((m.start(), m.end()))
    for m in _INDENTED_CODE_RE.finditer(body):
        regions.append((m.start(1), m.end(1)))
    for m in _INLINE_CODE_RE.finditer(body):
        regions.append((m.start(), m.end()))

    return merge_intervals(regions)


def is_inside_any_region(start: int, end: int, regions: List[Tuple[int, int]]) -> bool:
    """Return True if the ``[start, end)`` span overlaps any forbidden region.

    Args:
        start: Span start offset.
        end: Span end offset.
        regions: Sorted, merged (start, end) forbidden-region tuples.

    Returns:
        True if the span overlaps at least one region.
    """
    for r_start, r_end in regions:
        if not (end <= r_start or start >= r_end):
            return True
    return False


# --- Paragraph splitting (global, shared by sections + scoring) ---


def compute_paragraphs(body: str) -> List[Tuple[int, int]]:
    """Split ``body`` into paragraphs separated by one or more blank lines.

    A paragraph is any maximal run of text between blank-line separators
    (``\\n`` + optional whitespace + ``\\n``). Purely-whitespace segments
    (e.g. leading/trailing blank runs) are not counted as paragraphs.

    Args:
        body: Full post body text.

    Returns:
        List of (start, end) offsets, one per paragraph, in document order.
    """
    paragraphs: List[Tuple[int, int]] = []
    pos = 0
    for m in re.finditer(r"\n[ \t]*\n", body):
        end = m.start()
        if body[pos:end].strip():
            paragraphs.append((pos, end))
        pos = m.end()
    if body[pos:].strip():
        paragraphs.append((pos, len(body)))
    return paragraphs


def find_paragraph_index(offset: int, paragraphs: List[Tuple[int, int]]) -> int:
    """Return the index of the paragraph containing ``offset``.

    Args:
        offset: Absolute offset into the body the paragraphs were computed from.
        paragraphs: Paragraph (start, end) list from ``compute_paragraphs``.

    Returns:
        The paragraph index, or the index of the nearest preceding
        paragraph if ``offset`` falls in an inter-paragraph gap (e.g.
        blank lines). Returns 0 if ``paragraphs`` is empty or ``offset``
        precedes the first paragraph.
    """
    if not paragraphs:
        return 0
    best = 0
    for i, (start, end) in enumerate(paragraphs):
        if start <= offset < end:
            return i
        if start <= offset:
            best = i
    return best


# --- Section segmentation (Phase 3, "Section Segmentation") ---

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


def segment_into_sections(body: str) -> List[Section]:
    """Split ``body`` into sections delimited by ATX headings (``#`` .. ``######``).

    Args:
        body: Full post body text.

    Returns:
        List of Section objects covering the entire body (the region
        before the first heading, if any, is section 0 with
        ``heading_level=0`` and ``heading_text="(intro)"``).
    """
    paragraphs = compute_paragraphs(body)
    lines = body.split("\n")
    sections: List[Section] = []

    current_heading_level = 0
    current_heading_text = "(intro)"
    section_idx = 0
    offset = 0
    section_start_offset = 0

    for line in lines:
        m = _HEADING_RE.match(line)
        if m:
            section_end_offset = offset
            sections.append(
                Section(
                    index=section_idx,
                    heading_level=current_heading_level,
                    heading_text=current_heading_text,
                    start_offset=section_start_offset,
                    end_offset=section_end_offset,
                    paragraph_offsets=[
                        p for p in paragraphs if section_start_offset <= p[0] < section_end_offset
                    ],
                )
            )
            section_idx += 1
            current_heading_level = len(m.group(1))
            current_heading_text = m.group(2).strip()
            section_start_offset = offset
        offset += len(line) + 1  # +1 for the newline split() consumed

    sections.append(
        Section(
            index=section_idx,
            heading_level=current_heading_level,
            heading_text=current_heading_text,
            start_offset=section_start_offset,
            end_offset=len(body),
            paragraph_offsets=[p for p in paragraphs if section_start_offset <= p[0] < len(body)],
        )
    )
    return sections


def find_section_containing(offset: int, sections: List[Section]) -> Optional[Section]:
    """Return the Section whose range contains ``offset``.

    Args:
        offset: Absolute offset into the body ``sections`` was built from.
        sections: Sections from ``segment_into_sections`` (contiguous, in order).

    Returns:
        The containing Section, or None if ``offset`` is out of range
        (should not happen for a genuine in-body match).
    """
    for section in sections:
        if section.start_offset <= offset < section.end_offset:
            return section
    # Edge case: a match starting exactly at end-of-body (empty tail) falls
    # just outside every half-open [start, end) range above.
    if sections and offset == sections[-1].end_offset:
        return sections[-1]
    return None
