"""Unit tests for src/inserter.py (Phase 4 — wikilink insertion).

Includes the spec's mandatory Test 3 (wikilink format output)
(951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md, Section 5),
adapted only to construct ``PostMetadata``/``LinkOpportunity`` with this
repo's actual dataclass fields (the spec's pseudocode omits a couple of
required fields, e.g. ``frontmatter``) — assertions are unchanged except
where noted.

``target_filename_stem`` is deliberately set to a DATE-PREFIXED value
(e.g. ``2024-01-01-install-nginx``) distinct from ``target_slug``
(``install-nginx``) in every test here — this is the exact shape real
Jekyll posts have, and is what caught the original bug where the
inserted bracket content used ``target_slug`` instead of the filename
stem, which ``jekyll-wikirefs`` (the actual renderer) cannot resolve.
"""

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from inserter import insert_wikilinks  # noqa: E402
from models import ExclusionReason, LinkOpportunity, PostMetadata  # noqa: E402


def _make_post(slug: str, body: str) -> PostMetadata:
    return PostMetadata(
        slug=slug,
        filepath=Path(f"/tmp/{slug}.md"),
        title="Source",
        date=date(2024, 1, 1),
        tags=[],
        categories=[],
        lang="en",
        body=body,
        body_word_count=len(body.split()),
        eligible_as_target=True,
        exclusion_reason=ExclusionReason.NONE,
        url_path=f"/{slug}/",
        frontmatter={},
    )


class TestWikilinkFormatOutput(unittest.TestCase):
    """Spec Test 3 (Section 5), adapted for the filename-stem bracket format."""

    def test_wikilink_format_with_anchor(self):
        body = "This post mentions how to install nginx in detail."
        post = _make_post("src-post", body)

        # Anchor text "install nginx" normalized matches slug "install-nginx" -> short form.
        anchor = "install nginx"
        start = body.index(anchor)
        opp = LinkOpportunity(
            source_slug="src-post",
            target_slug="install-nginx",
            target_filename_stem="2024-01-01-install-nginx",
            keyword="install nginx",
            anchor_text=anchor,
            match_start=start,
            match_end=start + len(anchor),
            section_index=0,
            paragraph_index=0,
            relative_position=0.5,
            score=0.9,
            source_tier="title",
        )

        modified_body, log = insert_wikilinks(post, [opp])
        self.assertIn("[[2024-01-01-install-nginx]]", modified_body)
        self.assertNotIn("[[install-nginx]]", modified_body)
        self.assertNotIn("[[2024-01-01-install-nginx|install nginx]]", modified_body)
        self.assertEqual(log[0]["target"], "install-nginx")
        self.assertEqual(log[0]["link_type"], "new")

        # Non-matching anchor -> long form [[filename-stem|anchor]].
        body2 = "This post: how to install nginx in detail."
        anchor2 = "how to install nginx"
        start2 = body2.index(anchor2)
        post2 = _make_post("src-post", body2)
        opp2 = LinkOpportunity(
            source_slug="src-post",
            target_slug="install-nginx",
            target_filename_stem="2024-01-01-install-nginx",
            keyword="install nginx",
            anchor_text=anchor2,
            match_start=start2,
            match_end=start2 + len(anchor2),
            section_index=0,
            paragraph_index=0,
            relative_position=0.5,
            score=0.9,
            source_tier="title",
        )
        modified_body2, _log2 = insert_wikilinks(post2, [opp2])
        self.assertIn("[[2024-01-01-install-nginx|how to install nginx]]", modified_body2)
        self.assertNotIn("[[install-nginx|", modified_body2)


class TestInsertionMechanics(unittest.TestCase):
    def test_multiple_links_processed_end_to_start_preserve_offsets(self):
        body = "First mention of alpha here, then beta later, then gamma at the end."
        post = _make_post("multi", body)

        def _opp(target_slug, filename_stem, text):
            start = body.index(text)
            return LinkOpportunity(
                source_slug="multi",
                target_slug=target_slug,
                target_filename_stem=filename_stem,
                keyword=text,
                anchor_text=text,
                match_start=start,
                match_end=start + len(text),
                section_index=0,
                paragraph_index=0,
                relative_position=start / len(body),
                score=0.5,
                source_tier="title",
            )

        opps = [
            _opp("alpha-post", "2024-01-01-alpha-post", "alpha"),
            _opp("beta-post", "2024-01-02-beta-post", "beta"),
            _opp("gamma-post", "2024-01-03-gamma-post", "gamma"),
        ]

        modified_body, log = insert_wikilinks(post, opps)

        self.assertIn("[[2024-01-01-alpha-post|alpha]]", modified_body)
        self.assertIn("[[2024-01-02-beta-post|beta]]", modified_body)
        self.assertIn("[[2024-01-03-gamma-post|gamma]]", modified_body)
        self.assertEqual(len(log), 3)
        self.assertEqual({entry["target"] for entry in log}, {"alpha-post", "beta-post", "gamma-post"})

    def test_no_opportunities_returns_body_unchanged(self):
        body = "Nothing to link here."
        post = _make_post("plain", body)
        modified_body, log = insert_wikilinks(post, [])
        self.assertEqual(modified_body, body)
        self.assertEqual(log, [])

    def test_log_entry_fields(self):
        body = "Mentions nginx once."
        post = _make_post("src", body)
        start = body.index("nginx")
        opp = LinkOpportunity(
            source_slug="src",
            target_slug="install-nginx",
            target_filename_stem="2024-01-01-install-nginx",
            keyword="nginx",
            anchor_text="nginx",
            match_start=start,
            match_end=start + len("nginx"),
            section_index=0,
            paragraph_index=0,
            relative_position=start / len(body),
            score=0.75,
            source_tier="tag",
        )
        _modified, log = insert_wikilinks(post, [opp])
        entry = log[0]
        self.assertEqual(entry["source"], "src")
        self.assertEqual(entry["target"], "install-nginx")  # log stays slug-keyed
        self.assertEqual(entry["anchor"], "nginx")
        self.assertEqual(entry["position"], start)
        self.assertEqual(entry["score"], 0.75)
        self.assertEqual(entry["link_type"], "new")


if __name__ == "__main__":
    unittest.main()
