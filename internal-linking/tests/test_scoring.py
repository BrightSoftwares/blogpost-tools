"""Unit tests for src/scoring.py (Phase 3 — link opportunity scoring +
distribution constraints).

Includes the spec's mandatory Test 2 (link distribution constraints)
(951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md, Section 5),
adapted from the spec's literal pseudocode: the spec's ``MockConfig`` is
undefined pseudocode shorthand (not real Python), and this repo's real
config (``config.bootstrap()``) is always a plain dict — so ``MockConfig``
here is a thin ``dict`` subclass carrying the same field names, and
``apply_distribution_constraints`` reads config via dict subscription
(``config["key"]``) to match ``indexer.py``/``config.py`` convention. The
test's own assertions are unchanged from the spec.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import ExclusionReason, LinkOpportunity, PostMetadata  # noqa: E402
from scoring import (  # noqa: E402
    apply_distribution_constraints,
    compute_position_score,
    find_link_opportunities,
    find_whole_word_matches,
    select_anchor_text,
    semantic_overlap,
)


class MockConfig(dict):
    """Dict-based stand-in for the spec's pseudocode ``MockConfig`` (see
    module docstring — this repo's real config is always a plain dict)."""


def _make_post(slug: str, title: str, body: str, keywords=None, eligible: bool = True) -> PostMetadata:
    return PostMetadata(
        slug=slug,
        filepath=Path(f"/tmp/{slug}.md"),
        title=title,
        date=None,
        tags=[],
        categories=[],
        lang="en",
        body=body,
        body_word_count=len(body.split()),
        eligible_as_target=eligible,
        exclusion_reason=ExclusionReason.NONE if eligible else ExclusionReason.FUTURE_DATE,
        url_path=f"/{slug}/",
        frontmatter={},
        keywords=keywords or [],
    )


class TestDistributionConstraints(unittest.TestCase):
    """Spec Test 2 (Section 5), verbatim assertions."""

    def test_distribution_constraints_enforced(self):
        opps = [
            LinkOpportunity(
                source_slug="src",
                target_slug=f"tgt-{i}",
                keyword=f"kw{i}",
                anchor_text=f"anchor {i}",
                match_start=i * 100,
                match_end=i * 100 + 10,
                section_index=0,
                paragraph_index=i,
                relative_position=i / 10,
                score=1.0 - i * 0.01,
                source_tier="title",
            )
            for i in range(10)
        ]

        config = MockConfig(
            max_links_per_post=8,
            max_links_per_section=1,
            min_paragraphs_between_links=3,
            link_density_max=1.0,  # disable density
        )

        selected = apply_distribution_constraints(opps, config, source_word_count=1000)

        # Only 1 link allowed (all opportunities share section_index=0).
        self.assertEqual(len(selected), 1)

        opps2 = [
            LinkOpportunity(
                source_slug="src",
                target_slug=f"tgt-{i}",
                keyword=f"kw{i}",
                anchor_text=f"anchor {i}",
                match_start=i * 100,
                match_end=i * 100 + 10,
                section_index=i,
                paragraph_index=i * 5,  # paragraphs far apart
                relative_position=i / 10,
                score=1.0 - i * 0.01,
                source_tier="title",
            )
            for i in range(10)
        ]
        selected2 = apply_distribution_constraints(opps2, config, source_word_count=1000)

        self.assertEqual(len(selected2), 8)
        paras = sorted(o.paragraph_index for o in selected2)
        for i in range(len(paras) - 1):
            self.assertGreaterEqual(paras[i + 1] - paras[i], 3)

    def test_max_links_per_post_cap(self):
        opps = [
            LinkOpportunity(
                source_slug="src",
                target_slug=f"tgt-{i}",
                keyword=f"kw{i}",
                anchor_text=f"anchor {i}",
                match_start=i * 1000,
                match_end=i * 1000 + 10,
                section_index=i,
                paragraph_index=i * 10,
                relative_position=i / 20,
                score=1.0 - i * 0.01,
                source_tier="title",
            )
            for i in range(20)
        ]
        config = MockConfig(
            max_links_per_post=3, max_links_per_section=1, min_paragraphs_between_links=3, link_density_max=1.0
        )
        selected = apply_distribution_constraints(opps, config, source_word_count=10000)
        self.assertEqual(len(selected), 3)

    def test_never_links_same_target_twice(self):
        opps = [
            LinkOpportunity(
                source_slug="src",
                target_slug="same-target",
                keyword=f"kw{i}",
                anchor_text=f"anchor {i}",
                match_start=i * 1000,
                match_end=i * 1000 + 10,
                section_index=i,
                paragraph_index=i * 10,
                relative_position=i / 5,
                score=1.0 - i * 0.01,
                source_tier="title",
            )
            for i in range(5)
        ]
        config = MockConfig(
            max_links_per_post=8, max_links_per_section=1, min_paragraphs_between_links=3, link_density_max=1.0
        )
        selected = apply_distribution_constraints(opps, config, source_word_count=10000)
        self.assertEqual(len(selected), 1)

    def test_link_density_cap_enforced(self):
        opps = [
            LinkOpportunity(
                source_slug="src",
                target_slug=f"tgt-{i}",
                keyword=f"kw{i}",
                anchor_text=f"anchor {i}",
                match_start=i * 1000,
                match_end=i * 1000 + 10,
                section_index=i,
                paragraph_index=i * 10,
                relative_position=i / 20,
                score=1.0 - i * 0.01,
                source_tier="title",
            )
            for i in range(20)
        ]
        # word_count=800, density_max=0.05 -> n/(800/20)=n/40 <= 0.05 -> n <= 2.
        config = MockConfig(
            max_links_per_post=20, max_links_per_section=1, min_paragraphs_between_links=1, link_density_max=0.05
        )
        selected = apply_distribution_constraints(opps, config, source_word_count=800)
        self.assertEqual(len(selected), 2)


class TestPositionScore(unittest.TestCase):
    def test_spread_peaks_in_middle(self):
        low_start = compute_position_score(0.0, "spread")
        mid = compute_position_score(0.5, "spread")
        low_end = compute_position_score(0.99, "spread")
        self.assertGreater(mid, low_start)
        self.assertGreater(mid, low_end)

    def test_end_heavy_is_monotonic(self):
        self.assertLess(compute_position_score(0.1, "end-heavy"), compute_position_score(0.9, "end-heavy"))

    def test_uniform_always_one(self):
        self.assertEqual(compute_position_score(0.0, "uniform"), 1.0)
        self.assertEqual(compute_position_score(0.99, "uniform"), 1.0)

    def test_unknown_strategy_raises(self):
        with self.assertRaises(ValueError):
            compute_position_score(0.5, "bogus")


class TestFindWholeWordMatches(unittest.TestCase):
    def test_case_insensitive_single_word(self):
        matches = find_whole_word_matches("Install NGINX today.", "nginx")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].group(0), "NGINX")

    def test_multi_word_keyword_tolerates_whitespace(self):
        matches = find_whole_word_matches("Please install  nginx  server now.", "install nginx server")
        self.assertEqual(len(matches), 1)

    def test_no_partial_word_match(self):
        matches = find_whole_word_matches("nginxproxy is different from nginx.", "nginx")
        self.assertEqual(len(matches), 1)  # only the standalone "nginx", not "nginxproxy"

    def test_empty_keyword_returns_no_matches(self):
        self.assertEqual(find_whole_word_matches("some body text", ""), [])


class TestSelectAnchorText(unittest.TestCase):
    def test_filename_strategy_returns_raw_match(self):
        body = "This post mentions how to install nginx in detail."
        matches = find_whole_word_matches(body, "install nginx")
        target = _make_post("install-nginx", "Install Nginx", "")
        text, start, end = select_anchor_text(matches[0], target, body, "filename")
        self.assertEqual(text, "install nginx")
        self.assertEqual(body[start:end], text)

    def test_context_strategy_extends_span(self):
        body = "This post mentions how to install nginx in great detail today."
        matches = find_whole_word_matches(body, "install nginx")
        target = _make_post("install-nginx", "Install Nginx", "")
        text, start, end = select_anchor_text(matches[0], target, body, "context")
        self.assertGreaterEqual(len(text.split()), len("install nginx".split()))
        self.assertEqual(body[start:end], text)

    def test_title_priority_falls_back_when_no_overlap(self):
        body = "This sentence has nothing to do with the target at all really."
        matches = find_whole_word_matches(body, "nothing")
        target = _make_post("completely-unrelated", "Completely Unrelated Topic", "")
        text, start, end = select_anchor_text(matches[0], target, body, "title-priority")
        # No semantic overlap with the target title -> raw match returned.
        self.assertEqual(text, "nothing")
        self.assertEqual((start, end), (matches[0].start(), matches[0].end()))

    def test_unknown_strategy_raises(self):
        body = "some text"
        matches = find_whole_word_matches(body, "some")
        target = _make_post("t", "T", "")
        with self.assertRaises(ValueError):
            select_anchor_text(matches[0], target, body, "bogus-strategy")


class TestSemanticOverlap(unittest.TestCase):
    def test_identical_text_high_overlap(self):
        self.assertGreater(semantic_overlap("install nginx", "Install Nginx"), 0.9)

    def test_unrelated_text_low_overlap(self):
        self.assertEqual(semantic_overlap("banana bread recipe", "install nginx server"), 0.0)

    def test_empty_inputs_return_zero(self):
        self.assertEqual(semantic_overlap("", "Install Nginx"), 0.0)
        self.assertEqual(semantic_overlap("install nginx", ""), 0.0)


class TestFindLinkOpportunities(unittest.TestCase):
    def _config(self, **overrides):
        base = {
            "distribution_strategy": "spread",
            "anchor_text_strategy": "filename",
            "max_links_per_post": 8,
            "max_links_per_section": 1,
            "min_paragraphs_between_links": 3,
            "link_density_max": 0.5,
        }
        base.update(overrides)
        return base

    def test_finds_opportunity_for_eligible_target_keyword(self):
        source = _make_post(
            "how-to-deploy",
            "How to Deploy",
            "This guide explains how to install nginx before deploying your app.",
        )
        target = _make_post(
            "install-nginx",
            "Install Nginx",
            "Body of the nginx post.",
            keywords=[("install nginx", 1.0, "title")],
        )
        index = {source.slug: source, target.slug: target}

        opportunities = find_link_opportunities(source, index, self._config())

        self.assertEqual(len(opportunities), 1)
        self.assertEqual(opportunities[0].target_slug, "install-nginx")

    def test_skips_self_link(self):
        source = _make_post(
            "install-nginx", "Install Nginx", "This is about install nginx.", keywords=[("install nginx", 1.0, "title")]
        )
        index = {source.slug: source}
        opportunities = find_link_opportunities(source, index, self._config())
        self.assertEqual(opportunities, [])

    def test_skips_ineligible_target(self):
        source = _make_post("post-a", "Post A", "Mentions install nginx here.")
        target = _make_post(
            "install-nginx",
            "Install Nginx",
            "Body.",
            keywords=[("install nginx", 1.0, "title")],
            eligible=False,
        )
        index = {source.slug: source, target.slug: target}
        opportunities = find_link_opportunities(source, index, self._config())
        self.assertEqual(opportunities, [])

    def test_skips_match_inside_forbidden_region(self):
        source = _make_post(
            "post-a",
            "Post A",
            "See `install nginx` as inline code, not prose.",
        )
        target = _make_post(
            "install-nginx", "Install Nginx", "Body.", keywords=[("install nginx", 1.0, "title")]
        )
        index = {source.slug: source, target.slug: target}
        opportunities = find_link_opportunities(source, index, self._config())
        self.assertEqual(opportunities, [])

    def test_empty_body_returns_no_opportunities(self):
        source = _make_post("post-a", "Post A", "")
        index = {source.slug: source}
        self.assertEqual(find_link_opportunities(source, index, self._config()), [])


if __name__ == "__main__":
    unittest.main()
