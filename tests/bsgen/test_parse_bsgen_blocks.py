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

from parse_bsgen_blocks import normalize_asset_aliases, validate_asset, parse_file  # noqa: E402


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
