"""Phase 3 — Link opportunity scoring and distribution constraints.

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md
(Section 1 "Phase 3 — Link Opportunity Scoring", "Distribution constraint
application", "Anchor text selection", and "Position Score Function").

Given a source post and the (already keyword-extracted, Phase 2) target
index, ``find_link_opportunities`` finds every candidate wikilink
insertion point, scores it, and ``apply_distribution_constraints``
greedily selects a subset that respects spacing/density rules.

Several design decisions were required beyond the literal pseudocode
(documented at the point of decision, and repeated in the
``ilv2k9a3-3 notes`` section of the PRJ file for visibility):

1. ``select_anchor_text`` returns ``(anchor_text, start, end)`` instead of
   just ``anchor_text``. The spec's ``insert_wikilinks`` (Phase 4) slices
   ``body[opp.match_start:opp.match_end]`` and expects that slice to equal
   the anchor text used for scoring — but the anchor-text strategies
   (``context``, ``title-priority``) *extend* the match beyond the raw
   keyword hit. Returning only text (as the spec's pseudocode literally
   does) would silently desync ``anchor_text`` from ``match_start``/
   ``match_end``, so any extension found here is folded back into the
   opportunity's offsets before it is returned.
2. ``extend_to_noun_phrase`` and ``semantic_overlap`` (title-priority
   strategy) and ``extend_with_context`` (context strategy) have no
   pseudocode bodies in the spec at all — Phase 3's own function
   signatures (``find_link_opportunities(source_post, target_index,
   config)``, no ``nlp_model`` parameter) mean POS-tagged noun-phrase
   extension isn't available here, unlike Phase 2. These are implemented
   as simple whitespace/punctuation-based word-boundary extension and a
   token-Jaccard overlap heuristic instead of spaCy-based NLP. See the
   docstrings below.
3. ``config`` is accessed as a dict (``config["key"]``) rather than via
   the spec pseudocode's dot-notation (``config.distribution_strategy``),
   matching the dict-based config produced by ``config.bootstrap()``
   (config.py) and used throughout ``indexer.py``/``keywords.py``.
4. ``max_links_per_section`` (Constraint 1) is read from config instead
   of hardcoded to 1: the spec's own pseudocode comment says "max 1 link
   per section" literally, but the documented config schema (Section 3)
   defines ``max_links_per_section`` as a configurable 1-10 field for
   exactly this constraint. Honoring the config value generalizes the
   constraint while preserving the spec's literal behavior at the
   documented default of 1.
5. Constraint 6 (``section_already_links_to`` — don't insert if the
   section already links to the same target via an existing markdown
   link) is only partially implemented: the wikilink-form check works,
   but the markdown-link branch needs Phase 5's ``resolve_url_to_slug``,
   which does not exist yet (Phase 5 is explicitly out of scope for this
   task — ``ilv2k9a3-4``). ``apply_distribution_constraints`` accepts
   optional ``sections``/``source_body``/``target_index`` parameters so
   the check can run once Phase 5 lands (this also keeps the mandatory
   spec Test 2 call signature, which passes none of these, working as
   the check is simply skipped when they aren't supplied).
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from models import LinkOpportunity, PostMetadata, Section
from text_utils import (
    compute_forbidden_regions,
    compute_paragraphs,
    find_paragraph_index,
    find_section_containing,
    is_inside_any_region,
    segment_into_sections,
)

_WORD_BOUNDARY_STOP = ".!?\n"


def find_whole_word_matches(body: str, keyword: str) -> List["re.Match[str]"]:
    """Find all case-insensitive, whole-word matches of ``keyword`` in ``body``.

    Multi-word keywords tolerate any run of whitespace between their
    tokens (the keyword text was normalized/tokenized by spaCy in Phase 2
    and may not have the exact single-space formatting of the source
    post's prose).

    Args:
        body: Post body text to search.
        keyword: Lowercased keyword/phrase from Phase 2 keyword extraction.

    Returns:
        List of ``re.Match`` objects, in document order.
    """
    tokens = keyword.split()
    if not tokens:
        return []
    pattern = r"\b" + r"\s+".join(re.escape(tok) for tok in tokens) + r"\b"
    return list(re.finditer(pattern, body, flags=re.IGNORECASE))


def compute_position_score(relative_position: float, strategy: str) -> float:
    """Return a 0.0-1.0 score based on where a match falls within the post.

    Args:
        relative_position: Match start offset divided by body length (0.0-1.0).
        strategy: One of "spread" (peak 0.4-0.8), "end-heavy" (linear
            increase), or "uniform" (constant 1.0).

    Returns:
        Position score in [0.0, 1.0] (approximately; "spread" is
        piecewise-linear per the spec and does not overshoot).

    Raises:
        ValueError: If ``strategy`` is not a recognized distribution strategy.
    """
    if strategy == "spread":
        if relative_position < 0.2:
            return 0.1 + (relative_position / 0.2) * 0.4
        elif relative_position < 0.6:
            return 0.5 + ((relative_position - 0.2) / 0.4) * 0.5
        elif relative_position < 0.9:
            return 1.0 - ((relative_position - 0.6) / 0.3) * 0.3
        else:
            return 0.7 - ((relative_position - 0.9) / 0.1) * 0.4
    elif strategy == "end-heavy":
        return relative_position
    elif strategy == "uniform":
        return 1.0
    raise ValueError(f"Unknown distribution_strategy: {strategy}")


def _extend_left(body: str, start: int, max_words: int) -> int:
    """Walk left from ``start`` by up to ``max_words`` words.

    Stops at a sentence-ending punctuation mark, a newline, or the start
    of the body — i.e. never extends across a sentence/paragraph boundary.
    """
    i = start
    words_added = 0
    while words_added < max_words and i > 0:
        j = i
        while j > 0 and body[j - 1] in " \t":
            j -= 1
        if j == 0 or body[j - 1] in _WORD_BOUNDARY_STOP:
            return j
        k = j
        while k > 0 and body[k - 1] not in " \t" + _WORD_BOUNDARY_STOP:
            k -= 1
        if k == j:
            return j
        i = k
        words_added += 1
    return i


def _extend_right(body: str, end: int, max_words: int) -> int:
    """Walk right from ``end`` by up to ``max_words`` words (mirror of ``_extend_left``)."""
    i = end
    n = len(body)
    words_added = 0
    while words_added < max_words and i < n:
        j = i
        while j < n and body[j] in " \t":
            j += 1
        if j >= n or body[j] in _WORD_BOUNDARY_STOP:
            return j
        k = j
        while k < n and body[k] not in " \t" + _WORD_BOUNDARY_STOP:
            k += 1
        if k == j:
            return j
        i = k
        words_added += 1
    return i


def extend_with_context(body: str, start: int, end: int, max_words: int = 5) -> Tuple[str, int, int]:
    """Extend a match with up to ``max_words`` surrounding words (context strategy).

    Args:
        body: Full source post body.
        start: Match start offset.
        end: Match end offset.
        max_words: Total extra words to add, split between left and right.

    Returns:
        (extended_text, new_start, new_end).
    """
    left_budget = max_words // 2
    right_budget = max_words - left_budget
    new_start = _extend_left(body, start, left_budget)
    new_end = _extend_right(body, end, right_budget)
    return body[new_start:new_end], new_start, new_end


def extend_to_noun_phrase(body: str, start: int, end: int) -> Tuple[str, int, int]:
    """Extend a match to an approximate surrounding noun phrase (title-priority strategy).

    No POS tagger is available in Phase 3 (``find_link_opportunities``
    receives no ``nlp_model``, unlike Phase 2's ``extract_keywords``), so
    this approximates "extend to noun phrase" as a tighter word-boundary
    extension (up to 2 words each side, vs. the ``context`` strategy's up
    to 5) — enough to often capture an adjacent modifier/head noun
    without a real dependency parse.

    Args:
        body: Full source post body.
        start: Match start offset.
        end: Match end offset.

    Returns:
        (extended_text, new_start, new_end).
    """
    new_start = _extend_left(body, start, 2)
    new_end = _extend_right(body, end, 2)
    return body[new_start:new_end], new_start, new_end


def semantic_overlap(text: str, title: str) -> float:
    """Approximate semantic overlap between ``text`` and a target's title.

    No embeddings/NLP model is available at this phase, so this uses
    token-level Jaccard similarity over lowercased alphanumeric words as
    a cheap, deterministic stand-in for the spec's unspecified
    ``semantic_overlap`` — good enough to gate whether a noun-phrase
    extension "meaningfully" overlaps the target title.

    Args:
        text: Candidate (possibly extended) anchor text.
        title: Target post's title.

    Returns:
        Jaccard similarity in [0.0, 1.0]; 0.0 if either side has no tokens.
    """

    def _tokens(s: str) -> set:
        return set(re.findall(r"[a-z0-9]+", s.lower()))

    t1, t2 = _tokens(text), _tokens(title)
    if not t1 or not t2:
        return 0.0
    return len(t1 & t2) / len(t1 | t2)


def select_anchor_text(
    match: "re.Match[str]", target_post: PostMetadata, source_body: str, strategy: str
) -> Tuple[str, int, int]:
    """Select the anchor text (and its span) for a matched keyword.

    Args:
        match: The raw keyword match (from ``find_whole_word_matches``).
        target_post: The link target's metadata (title used by title-priority).
        source_body: Full source post body.
        strategy: One of "title-priority", "context", "filename".

    Returns:
        (anchor_text, start, end) — start/end may differ from
        ``match.start()``/``match.end()`` if the anchor was extended.

    Raises:
        ValueError: If ``strategy`` is not recognized.
    """
    start, end = match.start(), match.end()

    if strategy == "filename":
        return source_body[start:end], start, end

    if strategy == "context":
        return extend_with_context(source_body, start, end, max_words=5)

    if strategy == "title-priority":
        extended_text, ext_start, ext_end = extend_to_noun_phrase(source_body, start, end)
        if semantic_overlap(extended_text, target_post.title) > 0.5:
            return extended_text, ext_start, ext_end
        return source_body[start:end], start, end

    raise ValueError(f"Unknown anchor_text_strategy: {strategy}")


def find_link_opportunities(
    source_post: PostMetadata, target_index: Dict[str, PostMetadata], config: Dict[str, Any]
) -> List[LinkOpportunity]:
    """Find and score every candidate wikilink insertion in ``source_post`` (Phase 3).

    Args:
        source_post: The post links will potentially be inserted into.
        target_index: Full post index (``indexer.build_post_index()`` output,
            with ``keywords`` populated by ``keywords.extract_keywords()``).
        config: Bootstrapped config dict (``config.bootstrap()`` output);
            reads ``distribution_strategy`` and ``anchor_text_strategy``.

    Returns:
        List of LinkOpportunity, sorted by ``score`` descending.
    """
    source_body = source_post.body
    if not source_body:
        return []

    sections = segment_into_sections(source_body)
    paragraphs = compute_paragraphs(source_body)
    forbidden_regions = compute_forbidden_regions(source_body)
    body_len = len(source_body)

    distribution_strategy = config["distribution_strategy"]
    anchor_text_strategy = config["anchor_text_strategy"]

    opportunities: List[LinkOpportunity] = []

    for target_slug, target_post in target_index.items():
        if target_slug == source_post.slug:
            continue
        if not target_post.eligible_as_target:
            continue

        for keyword, specificity, source_tier in target_post.keywords:
            for match in find_whole_word_matches(source_body, keyword):
                if is_inside_any_region(match.start(), match.end(), forbidden_regions):
                    continue

                section = find_section_containing(match.start(), sections)
                if section is None:
                    continue

                anchor_text, a_start, a_end = select_anchor_text(
                    match, target_post, source_body, anchor_text_strategy
                )
                # An extension strategy could push the span into a forbidden
                # region (e.g. across a code fence boundary) — fall back to
                # the raw, already-validated match in that case.
                if (a_start, a_end) != (match.start(), match.end()) and is_inside_any_region(
                    a_start, a_end, forbidden_regions
                ):
                    anchor_text, a_start, a_end = (
                        source_body[match.start() : match.end()],
                        match.start(),
                        match.end(),
                    )

                relative_position = a_start / body_len
                position_score = compute_position_score(relative_position, distribution_strategy)
                anchor_quality_score = min(len(anchor_text.split()) / 10.0, 1.0)

                total_score = (
                    specificity * 0.4
                    + position_score * 0.3
                    + anchor_quality_score * 0.2
                    + (1.0 if source_tier == "title" else 0.5) * 0.1
                )

                opportunities.append(
                    LinkOpportunity(
                        source_slug=source_post.slug,
                        target_slug=target_slug,
                        target_filename_stem=target_post.filepath.stem,
                        keyword=keyword,
                        anchor_text=anchor_text,
                        match_start=a_start,
                        match_end=a_end,
                        section_index=section.index,
                        paragraph_index=find_paragraph_index(a_start, paragraphs),
                        relative_position=relative_position,
                        score=total_score,
                        source_tier=source_tier,
                    )
                )

    opportunities.sort(key=lambda o: -o.score)
    return opportunities


def _section_already_links_to(section_text: str, target_slug: str, target_index: Dict[str, PostMetadata]) -> bool:
    """Best-effort duplicate-link check within a section body (Section 2).

    Only checks for an existing wikilink to ``target_slug``. The spec's
    markdown-link branch (resolving ``[text](url)`` via
    ``resolve_url_to_slug``) needs Phase 5 (migration), which is out of
    scope here — ``target_index`` is accepted (currently unused) so this
    signature will not need to change when that branch is added.

    Args:
        section_text: The section's body slice.
        target_slug: Slug to check for.
        target_index: Full post index (unused today; see above).

    Returns:
        True if the section already contains ``[[target_slug]]`` or
        ``[[target_slug|...]]``.
    """
    del target_index  # not used until Phase 5's resolve_url_to_slug exists
    return bool(re.search(rf"\[\[{re.escape(target_slug)}(\||\]\])", section_text))


def apply_distribution_constraints(
    opportunities: List[LinkOpportunity],
    config: Dict[str, Any],
    source_word_count: int,
    sections: Optional[List[Section]] = None,
    source_body: Optional[str] = None,
    target_index: Optional[Dict[str, PostMetadata]] = None,
) -> List[LinkOpportunity]:
    """Greedily select opportunities respecting distribution constraints (Phase 3).

    Assumes ``opportunities`` is already sorted by score descending (as
    returned by ``find_link_opportunities``).

    Args:
        opportunities: Candidate opportunities, score-descending.
        config: Config dict; reads ``max_links_per_post``,
            ``max_links_per_section`` (default 1), ``min_paragraphs_between_links``
            (default 3), and ``link_density_max``.
        source_word_count: Word count of the source post (density constraint).
        sections: Optional section list, needed only for Constraint 6
            (same-target-already-linked-in-section). If omitted (as in the
            spec's mandatory Test 2), Constraint 6 is skipped.
        source_body: Optional source post body, needed only for Constraint 6.
        target_index: Optional post index, needed only for Constraint 6.

    Returns:
        Selected opportunities, in the order they were accepted (score descending).
    """
    selected: List[LinkOpportunity] = []
    section_counts: Counter = Counter()
    used_paragraphs: set = set()
    used_target_slugs: set = set()

    max_links_per_post = config["max_links_per_post"]
    max_links_per_section = config.get("max_links_per_section", 1)
    min_paragraphs_between_links = config.get("min_paragraphs_between_links", 3)
    link_density_max = config["link_density_max"]

    check_section_dupes = sections is not None and source_body is not None and target_index is not None
    sections_by_index = {s.index: s for s in sections} if sections is not None else {}

    for opp in opportunities:
        if len(selected) >= max_links_per_post:
            break

        # Constraint 1: max N links per section (N configurable, spec default 1)
        if section_counts[opp.section_index] >= max_links_per_section:
            continue

        # Constraint 2: no 2 consecutive paragraphs with links
        if (opp.paragraph_index - 1) in used_paragraphs or (opp.paragraph_index + 1) in used_paragraphs:
            continue

        # Constraint 3: min N paragraphs between any two links
        if any(abs(opp.paragraph_index - p) < min_paragraphs_between_links for p in used_paragraphs):
            continue

        # Constraint 4: never link the same target twice from one post
        if opp.target_slug in used_target_slugs:
            continue

        # Constraint 5: link density cap (links per word)
        projected_density = (len(selected) + 1) / (source_word_count / 20) if source_word_count else 0.0
        if projected_density > link_density_max:
            continue

        # Constraint 6 (best-effort — see _section_already_links_to docstring)
        if check_section_dupes:
            section = sections_by_index.get(opp.section_index)
            if section is not None:
                section_text = source_body[section.start_offset : section.end_offset]
                if _section_already_links_to(section_text, opp.target_slug, target_index):
                    continue

        selected.append(opp)
        section_counts[opp.section_index] += 1
        used_paragraphs.add(opp.paragraph_index)
        used_target_slugs.add(opp.target_slug)

    return selected
