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

from process_assets import generate_placeholder_svg, wrap_label_to_width, process  # noqa: E402


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

    def test_extra_char_px_narrows_the_effective_line_budget(self):
        # A text that fits on one line at 0 extra px per char must wrap to
        # more lines once a per-character allowance (letter-spacing) is
        # added — same text, same width, different extra_char_px.
        text = "This is a moderately long line of sample text here"
        without_spacing = wrap_label_to_width(text, 16, 400, extra_char_px=0.0)
        with_spacing = wrap_label_to_width(text, 16, 400, extra_char_px=4.0)
        assert len(with_spacing) >= len(without_spacing)
        assert len(with_spacing) > 1


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

    def test_no_visible_placeholder_watermark_in_output(self):
        # Regression (found 2026-08-06, human reviewer feedback): a visible
        # "PLACEHOLDER — replace with SAM image" <text> watermark leaked
        # internal pipeline state into every customer-facing image. Same fix
        # pattern as the debug badge above — inspectable as a comment only.
        data = {"type": "hero_image", "brand": "luminous", "headline": "Notiwise launch"}
        svg = generate_placeholder_svg(data, 1200, 630, "asset-1")
        assert "PLACEHOLDER — replace with SAM image" not in svg
        assert "render_mode=placeholder" in svg

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

    def test_long_stat_label_wraps_instead_of_one_overflowing_line(self):
        # Regression (found 2026-08-06, code review): stat_label went into a
        # single unbounded <text> line — realistic long labels (a full
        # sentence, not a short caption) overflowed the card width.
        data = {
            "type": "stat_card",
            "brand": "bright-softwares",
            "stat_value": "87%",
            "stat_label": (
                "of enterprise engineering teams report improved code "
                "review turnaround time after adopting async review "
                "tooling across all squads"
            ),
        }
        svg = generate_placeholder_svg(data, 1200, 630, "asset-1")
        label_lines = re.findall(r'font-size="16"[^>]*>([^<]+)</text>', svg)
        assert len(label_lines) > 1
        # +2 accounts for the stat_label's letter-spacing="2px" widening
        # every character beyond the base per-char estimate (see the
        # letter-spacing-aware wrapping test below for the bug this guards).
        max_chars = int((1200 * 0.8) / (16 * 0.55 + 2))
        for line in label_lines:
            assert len(line) <= max_chars + 1

    def test_stat_label_wrapping_accounts_for_letter_spacing(self):
        # Regression (found 2026-08-06 via the screenshot loop, reviewing a
        # QA gallery render): wrap_label_to_width's width estimate didn't
        # add letter-spacing's per-character widening, so a label just
        # under the NAIVE (no-letter-spacing) character budget was judged
        # "fits on one line" and rendered as a single <text> overflowing
        # both edges of the card — never wrapped at all, unlike the
        # extreme-length label above which was long enough to trigger
        # wrapping regardless of the miscalculation.
        data = {
            "type": "stat_card",
            "brand": "bright-softwares",
            "stat_value": "87%",
            "stat_label": (
                "of enterprise engineering teams report improved review "
                "turnaround after adopting async tooling"
            ),
        }
        svg = generate_placeholder_svg(data, 1200, 630, "asset-1")
        label_lines = re.findall(r'font-size="16"[^>]*>([^<]+)</text>', svg)
        assert len(label_lines) > 1, (
            "94-char label with letter-spacing=2px must wrap onto 2+ lines, "
            "not render as one line overflowing the card"
        )


class TestTypeAwareComposition:
    """Regression (found 2026-08-06, human reviewer feedback): every asset
    type rendered as the exact same "centered text on a striped rectangle"
    composition — only the text content varied. Each type must now produce
    a visibly distinct SVG structure, not just different words."""

    def _render(self, asset_type: str, **extra) -> str:
        data = {"type": asset_type, "brand": "bright-softwares", **extra}
        return generate_placeholder_svg(data, 1200, 630, f"asset-{asset_type}")

    def test_pullquote_has_a_quote_glyph_and_left_rule(self):
        svg = self._render("pullquote", quote="Ship it", attribution="Someone")
        assert "“</text>" in svg  # the oversized decorative quote mark (U+201C)
        assert 'width="6"' in svg  # the left-edge accent rule

    def test_stat_card_has_a_decorative_ring_and_no_quote_glyph(self):
        svg = self._render("stat_card", stat_value="3x", stat_label="faster")
        assert "<circle" in svg
        assert "“</text>" not in svg

    def test_comparison_with_before_after_values_has_a_center_divider(self):
        svg = self._render("comparison_table", table_title="Before vs after",
                            before_value="2 hours", after_value="15 minutes")
        assert "<line " in svg  # the vertical divider between columns

    def test_comparison_table_with_real_rows_shows_row_labels_not_before_after(self):
        # Regression (found 2026-08-06 via the screenshot loop, human-reviewed
        # example post): a comparison_table block with real columns+rows data
        # (not a simple before/after pair) fell through to the placeholder
        # "Before" / "After" labels — an empty-looking, uninformative card.
        svg = self._render(
            "comparison_table",
            table_title="What Google reviews",
            columns=["Section", "Generic (Fails)", "Specific (Passes)"],
            rows=[
                ["Data access", "We access Gmail data", "We view specific labels"],
                ["Data storage", "Data may be stored", "We store no email content"],
            ],
        )
        assert ">Before<" not in svg
        assert ">After<" not in svg
        assert "Data access" in svg
        assert "Data storage" in svg
        assert "Generic (Fails)" in svg
        assert "Specific (Passes)" in svg

    def test_comparison_table_renders_the_actual_cell_content_not_just_labels(self):
        # Regression (found 2026-08-06, human reviewer feedback on the
        # rendered image): the previous fix above only showed the row
        # SUBJECT ("Data access") and silently dropped both actual cell
        # values ("We access Gmail data" / "We view specific labels") — a
        # comparison table with no comparison in it doesn't communicate
        # anything ("I don't understand the message this image brings").
        svg = self._render(
            "comparison_table",
            table_title="What Google reviews",
            columns=["Section", "Generic (Fails)", "Specific (Passes)"],
            rows=[
                ["Data access", "We access Gmail data", "We view specific labels"],
            ],
        )
        assert "We access Gmail data" in svg
        assert "We view specific labels" in svg

    def test_comparison_table_caps_at_four_rows(self):
        rows = [[f"Row {i}", "a", "b"] for i in range(10)]
        svg = self._render("comparison_table", table_title="Many rows",
                            columns=["X", "Y", "Z"], rows=rows)
        for i in range(4):
            assert f"Row {i}" in svg
        for i in range(4, 10):
            assert f"Row {i}" not in svg

    def test_comparison_table_with_dict_rows_does_not_crash(self):
        # Regression (found 2026-08-06, code review): validate_asset only
        # checks row LENGTH matches column count, never row SHAPE — a content
        # author writing `rows:` as a list of mappings (easy YAML mistake,
        # visually similar to a list-of-lists) crashed the whole post's
        # processing with an uncaught KeyError instead of just this block.
        svg = self._render(
            "comparison_table", table_title="Dict rows",
            columns=["Section", "A", "B"],
            rows=[{"Section": "Data access", "A": "x", "B": "y"}],
        )
        assert "Data access" in svg

    def test_before_after_renders_the_required_labels(self):
        # Regression (found 2026-08-06, code review): before_label/
        # after_label are required by validate_asset for this shape but were
        # never actually rendered — the caption above each value silently
        # vanished.
        svg = self._render(
            "comparison_table",
            before_value="2 hours", before_label="Manual review",
            after_value="15 minutes", after_label="Automated scan",
        )
        assert "Manual review" in svg
        assert "Automated scan" in svg

    def test_headline_type_has_none_of_the_type_specific_markup(self):
        svg = self._render("hero_image", headline="Plain headline")
        assert "<circle" not in svg
        assert "<line " not in svg
        assert 'width="6"' not in svg

    def test_four_types_produce_four_different_fragments(self):
        svgs = {
            t: self._render(t, headline="X", quote="X", attribution="X",
                             stat_value="X", stat_label="X", table_title="X",
                             before_value="A", after_value="B")
            for t in ("hero_image", "pullquote", "stat_card", "comparison_table")
        }
        # Strip the shared wrapper bits (id/brand comments, gradient defs,
        # border) so this compares only the per-type fragment, not boilerplate.
        def fragment_only(svg: str) -> str:
            start = svg.index("-->", svg.index("bsgen:asset type=")) + 3
            end = svg.index("<!-- bsgen:asset render_mode=placeholder")
            return svg[start:end]
        fragments = {t: fragment_only(s) for t, s in svgs.items()}
        assert len(set(fragments.values())) == len(fragments), (
            "expected 4 visually distinct fragments, got duplicates"
        )


class TestResolvePalette:
    def test_known_brand_and_palette_resolves_exact_match(self):
        from process_assets import resolve_palette, BRAND_PALETTES
        result = resolve_palette("bright-softwares", "spotlight")
        assert result == BRAND_PALETTES["bright-softwares"]["spotlight"]

    def test_unknown_palette_falls_back_to_brand_default(self):
        from process_assets import resolve_palette, BRAND_PALETTES
        result = resolve_palette("luminous", "nonexistent-palette-name")
        assert result == BRAND_PALETTES["luminous"]["hero"]

    def test_missing_palette_falls_back_to_brand_default(self):
        from process_assets import resolve_palette, BRAND_PALETTES
        result = resolve_palette("bright-softwares", None)
        assert result == BRAND_PALETTES["bright-softwares"]["hero"]

    def test_unknown_brand_falls_back_to_default_brand(self):
        from process_assets import resolve_palette, BRAND_PALETTES
        result = resolve_palette("not-a-real-brand", "hero")
        assert result == BRAND_PALETTES["bright-softwares"]["hero"]

    def test_brand_with_only_one_variant_never_raises_on_other_names(self):
        from process_assets import resolve_palette, BRAND_PALETTES
        result = resolve_palette("eagles-techs", "spotlight")
        assert result == BRAND_PALETTES["eagles-techs"]["hero"]


class TestSanitizeAssetId:
    """Regression (found 2026-08-06, security review of these bsgen fixes):
    `id:` is a field inside a bsgen:asset block — author-controlled post
    content — and was going straight into an f-string filename joined onto
    output_dir. A crafted id like '../../../.github/workflows/ci' escaped
    output_dir entirely, letting a post overwrite arbitrary repo files."""

    def test_path_traversal_sequences_are_stripped(self):
        from process_assets import sanitize_asset_id
        assert ".." not in sanitize_asset_id("../../../etc/passwd")
        assert "/" not in sanitize_asset_id("../../../etc/passwd")

    def test_normal_id_is_unchanged(self):
        from process_assets import sanitize_asset_id
        assert sanitize_asset_id("legal-docs-hero") == "legal-docs-hero"

    def test_empty_or_all_unsafe_id_falls_back_to_a_safe_default(self):
        from process_assets import sanitize_asset_id
        assert sanitize_asset_id("../../..") == "asset"
        assert sanitize_asset_id("") == "asset"


class TestProcessPathTraversal:
    """Integration-level proof that process() cannot be made to write a file
    outside the given output_dir via a malicious bsgen:asset `id:` field."""

    def _make_post(self, tmp_path: Path, asset_id: str) -> Path:
        posts_dir = tmp_path / "en" / "_posts"
        posts_dir.mkdir(parents=True)
        post = posts_dir / "2026-08-06-test-post.md"
        post.write_text(
            "---\n"
            "title: Test post\n"
            "tags: [test]\n"
            "pipeline_state: bsgen_processing\n"
            "---\n\n"
            "Intro text.\n\n"
            "```bsgen:asset\n"
            f"id: \"{asset_id}\"\n"
            "type: hero_image\n"
            "brand: bright-softwares\n"
            "headline: \"hello\"\n"
            "output_formats:\n"
            "  - og_card: \"1200x630\"\n"
            "```\n",
            encoding="utf-8",
        )
        return post

    def test_malicious_id_does_not_escape_output_dir(self, tmp_path: Path):
        post = self._make_post(tmp_path, "../../../.github/workflows/ci")
        output_dir = tmp_path / "assets" / "images" / "bsgen"
        (tmp_path / ".github" / "workflows").mkdir(parents=True)

        process(post, output_dir)

        written = list(output_dir.glob("*.svg"))
        assert len(written) == 1
        assert output_dir in written[0].parents
        # Nothing was written into (or under) the traversal target.
        assert not any((tmp_path / ".github" / "workflows").glob("*.svg"))


class TestBlogHeroFragment:
    """Regression (found 2026-08-06): `type: blog-hero` appears in 14 real
    bsgen:asset blocks on corporate-website (per the SAM spec's
    template_id=blog-hero: title/author/date/category/background_image) but
    had no renderer at all — silently fell through to the plain
    centered-headline default, and its actual field name (`title`, not
    `headline`) meant even that produced blank text. Also had no background
    treatment of its own despite being spec'd to sit on a real photo."""

    def _render(self, **extra) -> str:
        data = {"type": "blog-hero", "brand": "bright-softwares", **extra}
        return generate_placeholder_svg(data, 1200, 630, "asset-blog-hero")

    def test_title_field_renders(self):
        svg = self._render(title="The $50,000 Lie That Almost Killed My Gmail Addon")
        assert "The $50,000 Lie That Almost Killed My Gmail Addon" in svg

    def test_theme_field_renders_as_category_badge(self):
        # Real content uses `theme`, the SAM spec calls the field
        # `category` — both must work.
        svg = self._render(title="X", theme="technical")
        assert "TECHNICAL" in svg

    def test_category_field_also_works(self):
        svg = self._render(title="X", category="Engineering")
        assert "ENGINEERING" in svg

    def test_no_badge_when_no_category_or_theme(self):
        svg = self._render(title="X")
        # No stray empty pill rect group for the badge.
        assert svg.count("<rect") < self._render(title="X", theme="technical").count("<rect")

    def test_author_and_date_render_as_byline(self):
        svg = self._render(title="X", author="Full Bright", date="August 6, 2026")
        assert "Full Bright" in svg
        assert "August 6, 2026" in svg
        assert "·" in svg

    def test_no_byline_when_author_and_date_absent(self):
        svg = self._render(title="X")
        assert "·" not in svg

    def test_has_a_distinct_photo_style_background_not_the_flat_stripe_pattern(self):
        # The whole point of this type: it should NOT look like every other
        # flat-gradient-plus-diagonal-stripe placeholder card.
        blog_hero_svg = self._render(title="X")
        headline_svg = generate_placeholder_svg(
            {"type": "hero_image", "brand": "bright-softwares", "headline": "X"},
            1200, 630, "asset-headline",
        )
        assert "radialGradient" in blog_hero_svg
        assert "stripes-" not in blog_hero_svg
        assert "stripes-" in headline_svg

    def test_long_title_wraps_within_three_lines(self):
        svg = self._render(
            title=(
                "Reading Before Writing: What a Pre-Development Codebase "
                "Review Actually Found in the Pilotflow Codebase"
            ),
        )
        title_lines = re.findall(r'font-size="34"[^>]*>([^<]+)</text>', svg)
        assert 1 < len(title_lines) <= 3

    def test_missing_output_formats_and_id_do_not_crash_process(self, tmp_path: Path):
        # Real content never sets id/output_formats for this type (see
        # parse_bsgen_blocks.validate_asset's blog-hero exemption) — must
        # still process end to end, defaulting both.
        post = tmp_path / "post.md"
        post.write_text(
            "---\ntitle: Test\ntags: [test]\npipeline_state: bsgen_processing\n---\n\n"
            "```bsgen:asset\n"
            "type: blog-hero\n"
            "slug: test-post\n"
            "brand: bright-softwares\n"
            "title: \"Test Title\"\n"
            "theme: technical\n"
            "```\n",
            encoding="utf-8",
        )
        output_dir = tmp_path / "assets"
        exit_code = process(post, output_dir)
        assert exit_code == 0
        written = list(output_dir.glob("*.svg"))
        assert len(written) == 1
        assert "test-post" in written[0].name
