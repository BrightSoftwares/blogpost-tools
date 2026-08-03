"""Tests for bsgen placeholder-SVG generation.

Regression (found 2026-08-01, corporate-website + Notiwise + Pilotflow posts):
generate_placeholder_svg() truncated headline/subheadline text at a fixed
CHARACTER count (70) instead of measuring/wrapping to the actual card WIDTH,
so long headlines rendered past the card edges. It also always drew a visible
corner badge with the literal internal string "bsgen:<type>" — flagged by the
human reviewer as unwanted debug noise on a customer-facing placeholder image.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "bsgen"))

from process_assets import generate_placeholder_svg, wrap_label_to_width  # noqa: E402


class TestWrapLabelToWidth:
    def test_short_text_is_a_single_line(self):
        lines = wrap_label_to_width("Short headline", 32, 1000)
        assert lines == ["Short headline"]

    def test_long_text_wraps_into_multiple_lines(self):
        text = "This is a very long headline that should not fit on one single line at this font size"
        lines = wrap_label_to_width(text, 32, 400)
        assert len(lines) > 1
        max_chars = int(400 / (32 * 0.55))
        for line in lines[:-1]:
            assert len(line) <= max_chars

    def test_respects_max_lines_cap_with_ellipsis(self):
        text = " ".join(["word"] * 60)
        lines = wrap_label_to_width(text, 32, 300, max_lines=3)
        assert len(lines) == 3
        assert lines[-1].endswith("…")

    def test_empty_text_returns_no_lines(self):
        assert wrap_label_to_width("", 32, 1000) == []


class TestGeneratePlaceholderSvg:
    def _svg_text_lines(self, svg: str) -> list[str]:
        return re.findall(r"<text[^>]*>([^<]*)</text>", svg)

    def test_long_headline_does_not_produce_one_unwrapped_line(self):
        data = {
            "type": "social_card",
            "brand": "bright-softwares",
            "headline": (
                "This Is An Extremely Long Headline That Would Previously "
                "Overflow The Card Edges Because It Was Only Truncated By "
                "Character Count Not Actual Rendered Width"
            ),
        }
        svg = generate_placeholder_svg(data, 1200, 630, "asset-1")
        text_lines = self._svg_text_lines(svg)
        # Every wrapped headline line should be short enough to plausibly
        # fit inside 1200px at font-size 32 (the bug produced one ~140-char
        # line at font-size 32, which is what this guards against).
        max_chars = int((1200 * 0.86) / (32 * 0.55))
        headline_lines = [
            l for l in text_lines if l and "PLACEHOLDER" not in l
        ]
        assert len(headline_lines) > 1
        for line in headline_lines:
            assert len(line) <= max_chars + 1  # +1 for the ellipsis char

    def test_short_headline_still_renders_as_single_line(self):
        data = {"type": "social_card", "brand": "bright-softwares", "headline": "Short"}
        svg = generate_placeholder_svg(data, 1200, 630, "asset-1")
        text_lines = [l for l in self._svg_text_lines(svg) if l and "PLACEHOLDER" not in l]
        assert text_lines == ["Short"]

    def test_no_visible_debug_badge_in_output(self):
        data = {"type": "social_card", "brand": "bright-softwares", "headline": "Hello"}
        svg = generate_placeholder_svg(data, 1200, 630, "asset-1")
        # The old bug: a visible <rect> + <text>bsgen:social_card</text> badge.
        assert "bsgen:social_card</text>" not in svg
        assert "<!-- bsgen:asset type=social_card -->" in svg

    def test_placeholder_footer_label_still_present(self):
        data = {"type": "hero_image", "brand": "luminous", "headline": "Notiwise launch"}
        svg = generate_placeholder_svg(data, 1200, 630, "asset-1")
        assert "PLACEHOLDER — replace with SAM image" in svg

    def test_pullquote_and_stat_card_still_render(self):
        pullquote_svg = generate_placeholder_svg(
            {"type": "pullquote", "quote": "A short quote", "attribution": "Someone"},
            800, 400, "asset-2",
        )
        assert "A short quote" in pullquote_svg

        stat_svg = generate_placeholder_svg(
            {"type": "stat_card", "stat_value": "42%", "stat_label": "improvement"},
            800, 400, "asset-3",
        )
        assert "42%" in stat_svg
