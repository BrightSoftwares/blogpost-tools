"""Phase 4 — Wikilink insertion.

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md
(Section 1 "Phase 4 — Link Insertion").

Takes the opportunities selected by
``scoring.apply_distribution_constraints`` and rewrites the source post
body, inserting ``[[target-filename-stem]]`` (when the anchor text
already equals the target's slug) or
``[[target-filename-stem|anchor text]]`` (otherwise). The bracket content
is the target's FILENAME STEM (``LinkOpportunity.target_filename_stem``,
e.g. ``2024-01-01-install-nginx``), not its date-stripped ``target_slug``
— verified live against ``jekyll-wikirefs`` (the renderer this repo's
wikilinks are meant for): it resolves ``[[...]]`` content against
``Jekyll::Document#basename`` minus extension, which still has the date
prefix, so a bare-slug bracket renders as ``invalid-wiki-link``. The
anchor-matches-slug comparison below still uses ``target_slug`` (a
human-typed anchor naturally reads like the slug, never like a
date-prefixed filename).
Matches are applied from the end of the body toward the start so that
earlier offsets are never invalidated by a later (leftward) insertion —
this is why ``scoring.find_link_opportunities`` and
``apply_distribution_constraints`` keep ``match_start``/``match_end`` on
each ``LinkOpportunity`` in terms of the *original* (unmodified) body.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from keywords import normalize
from models import LinkOpportunity, PostMetadata


def insert_wikilinks(
    source_post: PostMetadata, selected_opportunities: List[LinkOpportunity]
) -> Tuple[str, List[Dict[str, Any]]]:
    """Insert wikilinks for every selected opportunity into the post body.

    Args:
        source_post: The post whose ``body`` will be rewritten (read-only;
            the modified body is returned, not written back onto the
            dataclass instance).
        selected_opportunities: Opportunities to insert, as returned by
            ``scoring.apply_distribution_constraints`` (any order — this
            function re-sorts them end-to-start internally).

    Returns:
        Tuple of (modified_body, insertions_log). ``insertions_log`` is a
        list of dicts with keys ``source``, ``target``, ``anchor``,
        ``position``, ``score``, ``link_type`` (``"new"``) — matching the
        spec's Phase 4 pseudocode and the ``change_report.csv`` columns
        that Phase 6 (reporting, out of scope here) will eventually write.
    """
    body = source_post.body
    sorted_opps = sorted(selected_opportunities, key=lambda o: -o.match_start)

    insertions_log: List[Dict[str, Any]] = []
    for opp in sorted_opps:
        original_text = body[opp.match_start : opp.match_end]

        if normalize(original_text) == normalize(opp.target_slug.replace("-", " ")):
            wikilink = f"[[{opp.target_filename_stem}]]"
        else:
            wikilink = f"[[{opp.target_filename_stem}|{original_text}]]"

        body = body[: opp.match_start] + wikilink + body[opp.match_end :]

        insertions_log.append(
            {
                "source": opp.source_slug,
                "target": opp.target_slug,
                "anchor": original_text,
                "position": opp.match_start,
                "score": opp.score,
                "link_type": "new",
            }
        )

    return body, insertions_log
