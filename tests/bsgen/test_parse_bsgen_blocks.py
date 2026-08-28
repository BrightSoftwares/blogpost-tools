"""Tests for parse_bsgen_blocks.py's asset field-name alias normalization.

Regression (found 2026-08-06 while building a sample-render QA gallery):
real content across this repo is inconsistent about hero_image/social_card
field names — some drafts use `headline:`/`subheadline:` (what the
validator/renderer originally required), others use `title:`/`subtitle:`
for the exact same shape. The latter silently failed validation ("missing
'headline'") and the block was skipped entirely — no image ever generated,
raw fence left in the post.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "bsgen"))

from parse_bsgen_blocks import (  # noqa: E402
    normalize_asset_aliases,
    validate_asset,
    validate_social,
    parse_file,
    wrap_dormant_source,
)


class TestNormalizeAssetAliases:
    def test_title_becomes_headline_when_headline_missing(self):
        data = {"type": "social_card", "title": "The CASA Certification Myth"}
        normalized = normalize_asset_aliases(data)
        assert normalized["headline"] == "The CASA Certification Myth"

    def test_subtitle_becomes_subheadline_when_subheadline_missing(self):
        data = {"type": "hero_image", "subtitle": "A shorter supporting line"}
        normalized = normalize_asset_aliases(data)
        assert normalized["subheadline"] == "A shorter supporting line"

    def test_headline_wins_when_both_present(self):
        data = {"type": "social_card", "headline": "Real headline", "title": "Ignored"}
        normalized = normalize_asset_aliases(data)
        assert normalized["headline"] == "Real headline"

    def test_non_headline_types_are_untouched(self):
        # pullquote/stat_card/comparison_table don't use headline/title at
        # all — normalization must not invent fields for them.
        data = {"type": "stat_card", "title": "Should not become a headline"}
        normalized = normalize_asset_aliases(data)
        assert "headline" not in normalized

    def test_title_only_block_now_passes_validation(self):
        data = {
            "id": "x", "type": "social_card", "brand": "bright-softwares",
            "output_formats": [{"og_card": "1200x630"}],
            "title": "The CASA Certification Myth",
        }
        normalized = normalize_asset_aliases(data)
        assert validate_asset(normalized, 1) == []


class TestParseFileAppliesAliasNormalization:
    def test_title_subtitle_block_is_parsed_without_validation_errors(self, tmp_path: Path):
        post = tmp_path / "post.md"
        post.write_text(
            "---\ntitle: Test\n---\n\n"
            "```bsgen:asset\n"
            "id: card-1\n"
            "type: social_card\n"
            "brand: bright-softwares\n"
            "title: \"The CASA Certification Myth\"\n"
            "subtitle: \"$50K is the ceiling.\"\n"
            "output_formats:\n"
            "  - og_card: \"1200x630\"\n"
            "```\n",
            encoding="utf-8",
        )
        result = parse_file(post, filter_type="asset")
        assert result["validation_errors"] == []
        block = result["blocks"]["asset"][0]
        assert block["data"]["headline"] == "The CASA Certification Myth"
        assert block["data"]["subheadline"] == "$50K is the ceiling."


class TestBlogHeroValidationExemption:
    """blog-hero real content never sets id/output_formats (see
    process_assets.py's DEFAULT_BLOG_HERO_OUTPUT_FORMATS + slug-based id
    fallback) — validate_asset must not hard-require them for this type."""

    def test_blog_hero_without_id_or_output_formats_is_valid(self):
        data = {"type": "blog-hero", "brand": "bright-softwares", "title": "X"}
        assert validate_asset(data, 1) == []

    def test_blog_hero_still_requires_title_or_headline(self):
        data = {"type": "blog-hero", "brand": "bright-softwares"}
        errors = validate_asset(data, 1)
        assert any("title" in e for e in errors)

    def test_other_types_still_require_id_and_output_formats(self):
        data = {"type": "hero_image", "brand": "bright-softwares", "headline": "X"}
        errors = validate_asset(data, 1)
        assert any("'id'" in e for e in errors)
        assert any("'output_formats'" in e for e in errors)


class TestFrameworkMatrixValidation:
    """SP-P5: framework_matrix (Smart Assets Manager template_id=framework-matrix)."""

    VALID_QUADRANTS = [
        {"label": "a", "title": "a", "body": "a", "tone": "positive"},
        {"label": "b", "title": "b", "body": "b", "tone": "neutral"},
        {"label": "c", "title": "c", "body": "c", "tone": "neutral"},
        {"label": "d", "title": "d", "body": "d", "tone": "negative"},
    ]

    def _base(self, **overrides):
        data = {
            "id": "x", "type": "framework_matrix", "brand": "bright-softwares",
            "output_formats": [{"og_card": "1200x630"}],
            "title": "Where to spend the next quarter.",
            "lede": "A simple 2x2 to triage feature ideas.",
            "quadrants": list(self.VALID_QUADRANTS),
        }
        data.update(overrides)
        return data

    def test_valid_block_passes(self):
        assert validate_asset(self._base(), 1) == []

    def test_missing_title_fails(self):
        data = self._base()
        del data["title"]
        errors = validate_asset(data, 1)
        assert any("framework_matrix" in e and "title" in e for e in errors)

    def test_missing_lede_fails(self):
        data = self._base()
        del data["lede"]
        errors = validate_asset(data, 1)
        assert any("framework_matrix" in e and "lede" in e for e in errors)

    def test_missing_quadrants_fails(self):
        data = self._base()
        del data["quadrants"]
        errors = validate_asset(data, 1)
        assert any("framework_matrix" in e and "quadrants" in e for e in errors)

    def test_wrong_quadrant_count_fails(self):
        data = self._base(quadrants=self.VALID_QUADRANTS[:3])
        errors = validate_asset(data, 1)
        assert any("exactly 4 entries" in e for e in errors)

    def test_five_quadrants_also_fails(self):
        data = self._base(quadrants=self.VALID_QUADRANTS + [self.VALID_QUADRANTS[0]])
        errors = validate_asset(data, 1)
        assert any("exactly 4 entries" in e for e in errors)


class TestPrinciplesListValidation:
    """SP-P5: principles_list (Smart Assets Manager template_id=numbered-list-editorial)."""

    VALID_ITEMS = [
        {"number": "01", "title": "Signal over noise.", "body": "x"},
        {"number": "02", "title": "Clarity at scale.", "body": "x"},
        {"number": "03", "title": "Light, not heat.", "body": "x"},
    ]

    def _base(self, **overrides):
        data = {
            "id": "x", "type": "principles_list", "brand": "bright-softwares",
            "output_formats": [{"og_card": "1200x630"}],
            "kicker": "A field guide",
            "title": "Three principles for shipping intelligent software.",
            "items": list(self.VALID_ITEMS),
        }
        data.update(overrides)
        return data

    def test_valid_block_passes(self):
        assert validate_asset(self._base(), 1) == []

    def test_two_items_is_valid(self):
        assert validate_asset(self._base(items=self.VALID_ITEMS[:2]), 1) == []

    def test_missing_kicker_fails(self):
        data = self._base()
        del data["kicker"]
        errors = validate_asset(data, 1)
        assert any("principles_list" in e and "kicker" in e for e in errors)

    def test_missing_items_fails(self):
        data = self._base()
        del data["items"]
        errors = validate_asset(data, 1)
        assert any("principles_list" in e and "items" in e for e in errors)

    def test_one_item_fails(self):
        data = self._base(items=self.VALID_ITEMS[:1])
        errors = validate_asset(data, 1)
        assert any("2-3 entries" in e for e in errors)

    def test_four_items_fails(self):
        data = self._base(items=self.VALID_ITEMS + [self.VALID_ITEMS[0]])
        errors = validate_asset(data, 1)
        assert any("2-3 entries" in e for e in errors)


class TestDormantSourceReversibility:
    """A render must be reversible by comment/uncomment, not git archaeology.

    All four bsgen processors preserve the original ```bsgen:TYPE fence as a
    dormant copy wrapped in an HTML comment (wrap_dormant_source), placed
    ahead of the rendered output, instead of discarding it. parse_file()
    must treat anything inside an HTML comment as inert so the dormant copy
    is never re-processed — and un-wrapping it (deleting the comment
    markers) must restore a live, parseable block with zero retyping.
    """

    RAW_BLOCK = (
        '```bsgen:callout\ntype: TIP\ncontent: "hello world"\n```'
    )

    def _post(self, body: str) -> str:
        return f"---\ntitle: t\n---\n\nIntro.\n\n{body}\n\nOutro.\n"

    def test_live_block_is_parsed(self, tmp_path):
        post = tmp_path / "post.md"
        post.write_text(self._post(self.RAW_BLOCK), encoding="utf-8")
        result = parse_file(post, filter_type="callout")
        assert len(result["blocks"]["callout"]) == 1

    def test_dormant_wrapped_block_is_not_reparsed_as_live(self, tmp_path):
        rendered = '<div class="bs-callout bs-callout--tip">rendered</div>'
        replacement = f"{wrap_dormant_source(self.RAW_BLOCK)}\n{rendered}"
        post = tmp_path / "post.md"
        post.write_text(self._post(replacement), encoding="utf-8")
        result = parse_file(post, filter_type="callout")
        assert result["blocks"]["callout"] == []
        # The literal fence text is still present (that's the point — it's
        # recoverable), just inert while wrapped.
        assert "bsgen:callout" in post.read_text(encoding="utf-8")

    def test_unwrapping_the_comment_restores_a_live_block(self, tmp_path):
        rendered = '<div class="bs-callout bs-callout--tip">rendered</div>'
        replacement = f"{wrap_dormant_source(self.RAW_BLOCK)}\n{rendered}"
        post = tmp_path / "post.md"
        post.write_text(self._post(replacement), encoding="utf-8")

        # Simulate a human undo: delete the rendered line and the comment
        # wrapper lines around the dormant fence, leaving the bare fence.
        lines = post.read_text(encoding="utf-8").split("\n")
        undone = [
            line for line in lines
            if not line.startswith("<!-- bsgen source")
            and line.strip() != "-->"
            and line != rendered
        ]
        post.write_text("\n".join(undone), encoding="utf-8")

        result = parse_file(post, filter_type="callout")
        assert len(result["blocks"]["callout"]) == 1


class TestValidateSocialCarouselCrash:
    """Regression: found 2026-08-26 drafting a new SLA-monitoring post.

    validate_social() did `slides[0].get("type")` unconditionally for
    `post_type: carousel`, raising AttributeError('str' object has no
    attribute 'get') when `slides` is a flat list of strings instead of a
    list of {slide, type, headline, subtext} dicts. process_social.py has
    no try/except around parse_file(), so this uncaught exception crashed
    the whole script (exit code 1 = FATAL to bsgen-pipeline.yml), not just
    the one carousel block — even though every other malformed-block case
    is designed to degrade to a skip-with-error (validation_errors),
    never a crash.
    """

    def _base(self, **overrides):
        data = {
            "platform": "linkedin",
            "post_type": "carousel",
            "source_section": "intro",
            "brand": "bright-softwares",
            "total_slides": 3,
        }
        data.update(overrides)
        return data

    def test_flat_string_slides_does_not_crash(self):
        # This is the exact shape that crashed in production: slides is a
        # plain list of strings, not a list of dicts.
        data = self._base(slides=["Hook text", "Middle text", "CTA text"])
        errors = validate_social(data, 1)
        assert any("must be an object" in e for e in errors)

    def test_valid_dict_slides_still_passes(self):
        data = self._base(
            slides=[
                {"slide": 1, "type": "hook_slide", "headline": "h", "subtext": "s"},
                {"slide": 2, "type": "cta_slide", "headline": "h2", "subtext": "s2"},
            ]
        )
        errors = validate_social(data, 1)
        assert errors == []

    def test_mixed_dict_and_string_slides_does_not_crash(self):
        data = self._base(
            slides=[
                {"slide": 1, "type": "hook_slide", "headline": "h", "subtext": "s"},
                "a stray string slide",
            ]
        )
        errors = validate_social(data, 1)
        assert any("must be an object" in e for e in errors)

    def test_wrong_first_slide_type_still_reported_when_slides_are_dicts(self):
        data = self._base(
            slides=[
                {"slide": 1, "type": "not_hook", "headline": "h", "subtext": "s"},
                {"slide": 2, "type": "cta_slide", "headline": "h2", "subtext": "s2"},
            ]
        )
        errors = validate_social(data, 1)
        assert any("slide 1 must be hook_slide" in e for e in errors)

    def test_empty_slides_does_not_crash(self):
        data = self._base(slides=[])
        errors = validate_social(data, 1)
        assert isinstance(errors, list)
