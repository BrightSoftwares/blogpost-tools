"""
process_assets.py

Processes bsgen:asset blocks. When Smart Assets Manager (SAM) is live,
POSTs each block to the SAM API and replaces the block with a Markdown image tag.

Current mode (SAM not yet live): generates branded SVG placeholder images,
saves them to <output_dir>, and replaces blocks with local image references.
Set BSGEN_SAM_API_URL + BSGEN_SAM_API_KEY env vars to switch to live mode.

Each asset `type` gets its own visual composition (see `_render_*_fragment`
below) rather than one generic "centered text on a rectangle" template for
every type — a stat_card, a pullquote and a before/after comparison are
visually distinct, not just re-labeled copies of each other (2026-08-06,
human reviewer feedback: "the type of card changes, the rendered image is
of the same shape"). Output pixel dimensions (og_card 1200x630 etc.) still
come from the block's own `output_formats` — those are platform-required
sizes (Open Graph / LinkedIn card conventions), not a content-type concern,
so they intentionally stay the same across types.

Optional `palette` field on a bsgen:asset block picks between curated,
per-brand color variants (see BRAND_PALETTES) sourced from the real design
tokens (brightsoftwares/design-system tokens/brands/*.json) — never
hand-invented hex values. Defaults to DEFAULT_PALETTE if omitted or unknown.

Also updates the post frontmatter:
  - Sets `image: <hero_image_url>` if a hero_image or social_card asset is found
  - Sets `pipeline_state: visual_review_needed` after all assets are processed

Usage:
    python process_assets.py <post_file> <output_dir> [--site-url https://example.com]

Environment variables:
    BSGEN_SAM_API_URL   If set, use live SAM API (e.g. https://sam.bright-softwares.com)
    BSGEN_SAM_API_KEY   API key for SAM (required if BSGEN_SAM_API_URL is set)

Exit codes:
    0 = success
    1 = fatal error
    2 = some blocks failed (validation errors or API failures)
"""

import sys
import os
import re
import json
import html as html_module
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from parse_bsgen_blocks import parse_file, extract_frontmatter

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml

# Per-brand color variants, sourced from the real design tokens
# (brightsoftwares/design-system tokens/brands/*.json — fetched and verified
# 2026-08-06, not hand-invented). Each brand has at least a "hero" variant;
# bright-softwares and luminous (the two brands this content pipeline uses
# most) also have a "spotlight" variant for content that wants a warmer/more
# energetic treatment (announcements, wins) vs. hero's cooler/professional
# default (explainers, analysis) — pick per-post via the `palette` field on
# a bsgen:asset block, see resolve_palette().
#
# bright-softwares "hero": brand.color.navy.900 -> navy.700 bg, gold.300 accent
# bright-softwares "spotlight": brand.color.gold.900 -> gold.700 bg, gold.200 accent
# luminous "hero": brand.color.indigo.950 -> indigo.900 bg, coral.400 accent
# luminous "spotlight": brand.color.coral.900 -> coral.800 bg, indigo.300 accent
BRAND_PALETTES = {
    "bright-softwares": {
        "hero":      {"bg": "#081633", "bg2": "#0f2a5f", "accent": "#f1c459", "text": "#FFFFFF"},
        "spotlight": {"bg": "#432809", "bg2": "#855112", "accent": "#f7dc8e", "text": "#FFFFFF"},
    },
    "luminous": {
        "hero":      {"bg": "#15143f", "bg2": "#26246a", "accent": "#ff6b6b", "text": "#FFFFFF"},
        "spotlight": {"bg": "#561010", "bg2": "#811919", "accent": "#a9a9eb", "text": "#FFFFFF"},
    },
    # TODO: these 4 brands still carry their pre-2026-08-06 single-variant
    # hex values, not yet cross-checked against tokens/brands/*.json the way
    # bright-softwares/luminous were. Do not add a fabricated "spotlight" for
    # any of these without pulling real token values first (CLAUDE.md design
    # system rule — never hand-invent colors).
    "personal":        {"hero": {"bg": "#1A1A2E", "bg2": "#1A1A2E", "accent": "#E94560", "text": "#FFFFFF"}},
    "ieatmyhealth":    {"hero": {"bg": "#1E6B3C", "bg2": "#1E6B3C", "accent": "#6BCB77", "text": "#FFFFFF"}},
    "moda-by-flora":   {"hero": {"bg": "#4A154B", "bg2": "#4A154B", "accent": "#ECB5C9", "text": "#FFFFFF"}},
    "eagles-techs":    {"hero": {"bg": "#0D1117", "bg2": "#0D1117", "accent": "#58A6FF", "text": "#FFFFFF"}},
}
DEFAULT_BRAND = "bright-softwares"
DEFAULT_PALETTE = "hero"


def resolve_palette(brand: str, palette: str | None) -> dict:
    """Resolve (brand, palette) to a color dict, falling back gracefully.

    Unknown brand -> DEFAULT_BRAND. Unknown/missing palette name -> the
    brand's DEFAULT_PALETTE if present, else whichever variant the brand
    does have. Never raises — a bad `palette` value in a bsgen block should
    degrade to a sane default, not fail the whole asset block.
    """
    brand_palettes = BRAND_PALETTES.get(brand, BRAND_PALETTES[DEFAULT_BRAND])
    if palette and palette in brand_palettes:
        return brand_palettes[palette]
    return brand_palettes.get(DEFAULT_PALETTE) or next(iter(brand_palettes.values()))


PLACEHOLDER_NOTE = "<!-- bsgen placeholder — replace with SAM-generated image when live -->"


def slug_from_filename(post_path: Path) -> str:
    name = post_path.stem
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", name)
    return m.group(1) if m else name


def date_from_filename(post_path: Path) -> str:
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-", post_path.stem)
    return m.group(1) if m else datetime.now().strftime("%Y-%m-%d")


def wrap_label_to_width(text: str, font_size: int, max_width: int, max_lines: int = 3) -> list[str]:
    """Word-wrap text into lines that fit max_width at font_size, capped at max_lines.

    SVG has no layout engine, so this uses a standard average-character-width
    heuristic for a system-ui/sans-serif font (~0.55 * font_size per char,
    the same ratio commonly used for canvas/SVG text-fitting since real glyph
    metrics aren't available at generation time). The last line is
    ellipsis-truncated if content still doesn't fit within max_lines — this
    is a placeholder, not final art, so a hard cap is the right tradeoff over
    unbounded overflow.
    """
    if not text:
        return []
    avg_char_width = font_size * 0.55
    max_chars = max(1, int(max_width / avg_char_width))

    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)

    if len(lines) == max_lines:
        last = lines[-1]
        if len(last) > max_chars:
            lines[-1] = last[: max(0, max_chars - 1)].rstrip() + "…"
        # Also true if wrapping simply ran out of lines before consuming all words.
        consumed = sum(len(l) + 1 for l in lines) - 1
        if consumed < len(text) and not lines[-1].endswith("…"):
            lines[-1] = lines[-1].rstrip() + "…"

    return lines


def _text_el(x, y, text, font_size, weight="400", fill="#FFFFFF", anchor="middle",
             style="normal", opacity=1, letter_spacing=None) -> str:
    """Build one <text> element. Shared by every per-type fragment renderer below."""
    extra = ""
    if style != "normal":
        extra += f' font-style="{style}"'
    if opacity != 1:
        extra += f' opacity="{opacity}"'
    if letter_spacing:
        extra += f' letter-spacing="{letter_spacing}"'
    return (
        f'<text x="{x}" y="{y}" font-family="system-ui, sans-serif" '
        f'font-size="{font_size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}" dominant-baseline="middle"{extra}>'
        f'{html_module.escape(text)}</text>'
    )


def _wrap_and_stack(lines_specs: list[tuple[str, int, str]], width: int, center_x: int,
                    center_y: int, max_width_ratio: float = 0.86, line_height: int = 40,
                    text_color: str = "#FFFFFF", anchor: str = "middle",
                    letter_spacing: str | None = None) -> str:
    """Word-wrap a list of (text, font_size, weight) logical lines to fit `width`,
    then stack the resulting physical lines centered on (center_x, center_y).

    Shared wrapping logic used by every fragment below — this is what fixes the
    original bug (fixed-character truncation instead of width-aware wrapping).
    """
    text_max_width = int(width * max_width_ratio)
    physical = []
    for i, (line, font_size, weight) in enumerate(lines_specs):
        max_lines = 3 if i == 0 else 2
        for wrapped in wrap_label_to_width(line, font_size, text_max_width, max_lines=max_lines):
            physical.append((wrapped, font_size, weight))

    y_start = center_y - (len(physical) - 1) * (line_height // 2)
    out = ""
    for i, (line, font_size, weight) in enumerate(physical):
        y = y_start + i * line_height
        out += _text_el(center_x, y, line, font_size, weight, text_color, anchor=anchor,
                        letter_spacing=letter_spacing) + "\n"
    return out


def _render_headline_fragment(data: dict, width: int, height: int, colors: dict) -> str:
    """hero_image / social_card (and the generic fallback): centered headline
    + optional subheadline. This is the card type most posts use."""
    lines = [(str(data.get("headline", "")), 32, "700")]
    if data.get("subheadline"):
        lines.append((str(data["subheadline"]), 20, "400"))
    return _wrap_and_stack(lines, width, width // 2, height // 2, text_color=colors["text"])


def _render_pullquote_fragment(data: dict, width: int, height: int, colors: dict) -> str:
    """pullquote: a big decorative quotation mark + italic quote + attribution
    — a blockquote-style composition, not a plain centered headline."""
    quote = str(data.get("quote", ""))
    attribution = str(data.get("attribution", ""))

    # Oversized opening-quote glyph, top-left, in the accent color — the
    # single biggest visual differentiator vs. a headline card. Uses the
    # proper typographic left-double-quotation-mark (U+201C), not a straight
    # ASCII '"' — at this size a straight quote renders as two flat
    # rectangles in most sans-serif fonts, not a recognizable quote mark.
    glyph = _text_el(int(width * 0.06), int(height * 0.32), "“", int(height * 0.42),
                     "700", colors["accent"], anchor="start", opacity=0.9)
    # Thin accent-colored rule down the left edge, blockquote-style.
    rule = f'<rect x="0" y="0" width="6" height="{height}" fill="{colors["accent"]}" opacity="0.8"/>'

    body = _wrap_and_stack(
        [(quote, 30, "700")], width, width // 2, int(height * 0.48),
        max_width_ratio=0.78, text_color=colors["text"],
    )
    body += _wrap_and_stack(
        [(f"— {attribution}", 18, "400")] if attribution else [],
        width, width // 2, int(height * 0.48) + 70,
        max_width_ratio=0.78, text_color=colors["accent"],
    )
    # Quote text is italicized by re-emitting with font-style; _wrap_and_stack
    # doesn't take a style param (shared by non-italic fragments too), so
    # patch it in on the elements this fragment just built.
    body = body.replace('font-weight="700" fill', 'font-weight="700" font-style="italic" fill')
    return rule + glyph + body


def _render_stat_fragment(data: dict, width: int, height: int, colors: dict) -> str:
    """stat_card: one big number, not a headline — the number is the whole point."""
    stat_value = str(data.get("stat_value", ""))
    stat_label = str(data.get("stat_label", "")).upper()

    number_size = max(56, min(int(height * 0.32), 140))
    number_y = height // 2 - 20
    number = _wrap_and_stack(
        [(stat_value, number_size, "800")], width, width // 2, number_y,
        max_width_ratio=0.9, text_color=colors["accent"], line_height=int(number_size * 1.05),
    )
    # stat_label can be a full sentence, not just a short caption (e.g. "of
    # enterprise engineering teams report improved code review turnaround
    # time…") — wrap it the same width-aware way as every other text field
    # here instead of emitting one unbounded <text> line that overflows the
    # card (2026-08-06, code review finding).
    label = _wrap_and_stack(
        [(stat_label, 16, "600")], width, width // 2,
        number_y + int(number_size * 0.75) + 30,
        max_width_ratio=0.8, text_color=colors["text"], line_height=24,
        letter_spacing="2px",
    )
    # A subtle ring behind the number, purely decorative — visually marks
    # this as a "stat" composition even before reading the number.
    ring = (
        f'<circle cx="{width//2}" cy="{number_y - int(number_size*0.15)}" '
        f'r="{int(min(width, height) * 0.32)}" fill="none" stroke="{colors["accent"]}" '
        f'stroke-width="2" opacity="0.18"/>'
    )
    return ring + number + label


def _render_before_after_fragment(data: dict, width: int, height: int, colors: dict) -> str:
    """before_after: a real two-column split with a center divider, not a
    single centered line of "A → B" text."""
    before_value = str(data.get("before_value") or "Before")
    after_value = str(data.get("after_value") or "After")
    # before_label/after_label are required by validate_asset for this type
    # (parse_bsgen_blocks.py) but were never actually rendered — the caption
    # above each value silently vanished (code review finding, 2026-08-06).
    before_label = data.get("before_label")
    after_label = data.get("after_label")
    delta = str(data.get("delta", ""))
    title = str(data.get("table_title", ""))

    left_x = width // 4
    right_x = (width * 3) // 4
    has_captions = bool(before_label or after_label)
    # Captions sit at a FIXED row near the top of the columns, and the value
    # block's own center is pushed down to compensate — independent of how
    # many lines the value text wraps to (up to 3 at this font size). Deriving
    # the caption position from the value's own center (the original
    # approach) collided whenever a long value wrapped to multiple lines,
    # since _wrap_and_stack's vertical spread pushed the top line up past a
    # caption placed a fixed offset above the center (found via the
    # screenshot loop, 2026-08-06, while verifying the code-review fix above).
    caption_y = int(height * 0.30)
    col_y = int(height * 0.58) if has_captions else height // 2
    col_y -= 10 if delta or title else 0

    divider = (
        f'<line x1="{width//2}" y1="{int(height*0.18)}" x2="{width//2}" '
        f'y2="{int(height*0.82)}" stroke="{colors["accent"]}" stroke-width="2" opacity="0.5"/>'
    )
    captions = ""
    if before_label:
        captions += _text_el(left_x, caption_y, str(before_label), 14, "600",
                             colors["text"], opacity=0.7, letter_spacing="1px")
    if after_label:
        captions += _text_el(right_x, caption_y, str(after_label), 14, "600",
                             colors["accent"], opacity=0.85, letter_spacing="1px")
    left = _wrap_and_stack([(before_value, 26, "700")], width // 2, left_x, col_y,
                           max_width_ratio=0.8, text_color=colors["text"])
    right = _wrap_and_stack([(after_value, 26, "700")], width // 2, right_x, col_y,
                            max_width_ratio=0.8, text_color=colors["accent"])
    arrow = _text_el(width // 2, col_y, "→", 22, "700", colors["accent"], opacity=0.9)

    footer = ""
    if title:
        footer += _text_el(width // 2, int(height * 0.16), title, 18, "600",
                           colors["text"], opacity=0.85)
    if delta:
        footer += _text_el(width // 2, int(height * 0.86), delta, 18, "600", colors["accent"])

    return divider + captions + left + right + arrow + footer


def _render_table_fragment(data: dict, width: int, height: int, colors: dict) -> str:
    """comparison_table: a real N-row table (title + 2 column headers + up
    to 4 row labels), not a placeholder "Before"/"After" split. A full data
    table (long cell text in 3 columns) doesn't fit legibly on a card this
    size, so this shows the actual column headers plus the row subjects
    (column 1 of each row) as a scannable checklist — honest about what a
    social-card-sized image can convey, rather than cramming unreadable text."""
    title = str(data.get("table_title", "Comparison"))
    columns = data.get("columns") or []
    rows = [r for r in (data.get("rows") or []) if r]

    left_header = str(columns[1]) if len(columns) > 1 else "Before"
    right_header = str(columns[2]) if len(columns) > 2 else "After"
    # A row is expected to be a list/tuple (validate_asset only checks
    # length, not shape) — a content author writing `rows:` as a list of
    # mappings instead would otherwise raise an uncaught KeyError here and
    # crash the whole post's processing, not just this one block (code
    # review finding, 2026-08-06).
    row_labels = [
        str(r[0]) if isinstance(r, (list, tuple)) and r
        else str(next(iter(r.values()), "")) if isinstance(r, dict)
        else str(r)
        for r in rows[:4]
    ]

    heading = _wrap_and_stack(
        [(title, 20, "700")], width, width // 2, int(height * 0.14),
        max_width_ratio=0.86, text_color=colors["text"],
    )
    divider = (
        f'<line x1="{width//2}" y1="{int(height*0.22)}" x2="{width//2}" '
        f'y2="{int(height*0.30)}" stroke="{colors["accent"]}" stroke-width="1.5" opacity="0.5"/>'
    )
    left_h = _text_el(width // 4, int(height * 0.28), left_header, 16, "600",
                      colors["text"], opacity=0.75)
    right_h = _text_el((width * 3) // 4, int(height * 0.28), right_header, 16, "600",
                       colors["accent"], opacity=0.95)

    row_y_start = int(height * 0.44)
    row_gap = max(32, int((height * 0.42) / max(1, len(row_labels))))
    rows_svg = ""
    for i, label in enumerate(row_labels):
        y = row_y_start + i * row_gap
        rows_svg += _wrap_and_stack(
            [(f"• {label}", 18, "500")], width, width // 2, y,
            max_width_ratio=0.8, text_color=colors["text"], line_height=24,
        )

    return heading + divider + left_h + right_h + rows_svg


def _render_comparison_fragment(data: dict, width: int, height: int, colors: dict) -> str:
    """comparison_table / before_after share a `type`-dispatch entry, but
    carry genuinely different data shapes (a real table with columns+rows,
    vs. a single before/after value pair) — route to whichever fragment
    actually matches the fields present, defaulting to the table view when
    a bsgen:asset block sets `type: comparison_table` explicitly."""
    if data.get("rows") and data.get("columns"):
        return _render_table_fragment(data, width, height, colors)
    if data.get("before_value") or data.get("after_value"):
        return _render_before_after_fragment(data, width, height, colors)
    # Neither shape present — degrade to the table view (title-only is safer
    # than a placeholder "Before"/"After" that implies data that isn't there).
    return _render_table_fragment(data, width, height, colors)


# asset `type` -> fragment renderer. Anything not listed falls back to the
# headline treatment (the safest default: just centered text, no assumptions
# about fields that type doesn't provide).
_FRAGMENT_RENDERERS = {
    "pullquote": _render_pullquote_fragment,
    "stat_card": _render_stat_fragment,
    "comparison_table": _render_comparison_fragment,
    "before_after": _render_comparison_fragment,
    "social_card": _render_headline_fragment,
    "hero_image": _render_headline_fragment,
}


def generate_placeholder_svg(data: dict, width: int, height: int, asset_id: str) -> str:
    """Generate a branded SVG placeholder image for a bsgen:asset block.

    Dispatches to a type-specific composition (see _FRAGMENT_RENDERERS) so
    different asset types actually look different, not just differently
    labeled. Colors come from resolve_palette(brand, palette) — real design
    tokens, with an optional per-post palette variant.
    """
    brand = data.get("brand", DEFAULT_BRAND)
    colors = resolve_palette(brand, data.get("palette"))
    bg, bg2, accent = colors["bg"], colors.get("bg2", colors["bg"]), colors["accent"]

    asset_type = data.get("type", "asset")
    renderer = _FRAGMENT_RENDERERS.get(asset_type, _render_headline_fragment)
    fragment = renderer(data, width, height, colors)

    # Asset type is recorded as an XML comment for debugging, not a visible
    # on-image badge — the visible corner badge (rendering literal internal
    # strings like "bsgen:social_card" on every placeholder) was flagged as
    # unwanted noise by the human reviewer; the type is still inspectable in
    # the SVG source when needed.
    type_badge = f'<!-- bsgen:asset type={html_module.escape(asset_type)} -->'

    # 2026-08-06: the visible "PLACEHOLDER — replace with SAM image" watermark
    # was also flagged by the human reviewer (leaks internal pipeline state
    # into a customer-facing image, and reads as broken/unfinished). Same fix
    # pattern as the type badge above: keep it inspectable as a comment, not
    # rendered. The generated `<!-- bsgen:asset urls {...} -->` manifest
    # comment already written into the post body is the real "this is a
    # placeholder" signal for anyone editing the source.
    placeholder_marker = (
        f'<!-- bsgen:asset render_mode=placeholder id={html_module.escape(asset_id)} -->'
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <!-- bsgen:asset placeholder | id={html_module.escape(asset_id)} | brand={html_module.escape(brand)} -->
  <defs>
    <linearGradient id="bggrad-{html_module.escape(asset_id)}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg}"/>
      <stop offset="100%" stop-color="{bg2}"/>
    </linearGradient>
    <pattern id="stripes-{html_module.escape(asset_id)}" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="20" height="40" fill="{accent}" opacity="0.05"/>
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#bggrad-{html_module.escape(asset_id)})"/>
  <rect width="{width}" height="{height}" fill="url(#stripes-{html_module.escape(asset_id)})"/>
  <rect x="2" y="2" width="{width-4}" height="{height-4}" rx="4" fill="none" stroke="{accent}" stroke-width="2" opacity="0.3"/>
  {type_badge}
  {fragment}
  {placeholder_marker}
</svg>"""


def process_with_sam_api(data: dict, asset_id: str, api_url: str, api_key: str) -> dict | None:
    """POST block to SAM API. Returns {format_name: url} dict or None on failure."""
    try:
        import urllib.request
        payload = json.dumps({"block": data, "asset_id": asset_id}).encode()
        req = urllib.request.Request(
            f"{api_url.rstrip('/')}/api/v1/generate",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result.get("urls", {})
    except Exception as e:
        print(f"ERROR: SAM API call failed for {asset_id}: {e}", file=sys.stderr)
        return None


def parse_size(size_str: str) -> tuple[int, int]:
    """Parse 'WxH' string to (width, height) ints."""
    m = re.match(r"(\d+)[x×](\d+)", size_str)
    if m:
        return int(m.group(1)), int(m.group(2))
    return 1200, 630


_UNSAFE_ID_CHARS_RE = re.compile(r"[^A-Za-z0-9_-]")


def sanitize_asset_id(asset_id: str) -> str:
    """Make an asset id safe to use as a filesystem path component.

    `id:` is a field inside a bsgen:asset block — content, not code — so it
    must be treated as untrusted input. Before this, `asset_id` went straight
    into an f-string filename joined onto `output_dir` (see `process()`
    below); a crafted id like `../../../.github/workflows/ci` would escape
    `output_dir` entirely and let a post write/overwrite an arbitrary file in
    the repo checkout. Strip everything but the filename-safe charset.
    """
    safe = _UNSAFE_ID_CHARS_RE.sub("-", asset_id).strip("-")
    return safe or "asset"


def render_figure_tag(asset_id: str, img_url: str, post_path: Path, content: str, data: dict) -> str:
    """Build the Markdown/HTML image replacement for an asset block."""
    alt = ""
    # Look for the [Figure N: ...] line immediately before the block
    idx = content.find(f"```bsgen:asset\nid: {asset_id}")
    if idx > 0:
        preceding = content[:idx].rstrip()
        last_line = preceding.split("\n")[-1].strip()
        figure_match = re.match(r"\[Figure \d+:(.+)\]", last_line)
        if figure_match:
            alt = figure_match.group(1).strip()

    if not alt:
        asset_type = data.get("type", "asset")
        alt = f"{asset_type} for {post_path.stem}"

    escaped_alt = html_module.escape(alt)
    return f"![{escaped_alt}]({img_url})"


def update_frontmatter_field(content: str, key: str, value: str) -> str:
    """Update or add a field in the YAML frontmatter."""
    fm_match = re.match(r"^(---\s*\n)(.*?)(---\s*\n)", content, re.DOTALL)
    if not fm_match:
        return content

    prefix = fm_match.group(1)
    fm_body = fm_match.group(2)
    suffix = fm_match.group(3)
    rest = content[fm_match.end():]

    # Replace existing key or append
    key_pattern = re.compile(rf"^{re.escape(key)}\s*:.*$", re.MULTILINE)
    new_line = f"{key}: {value}"
    if key_pattern.search(fm_body):
        fm_body = key_pattern.sub(new_line, fm_body)
    else:
        fm_body = fm_body.rstrip("\n") + f"\n{new_line}\n"

    return prefix + fm_body + suffix + rest


def process(post_path: Path, output_dir: Path, site_url: str = "") -> int:
    parsed = parse_file(post_path, filter_type="asset")
    asset_blocks = parsed["blocks"]["asset"]

    if not asset_blocks:
        print(f"INFO: no bsgen:asset blocks found in {post_path}", file=sys.stderr)
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)

    sam_api_url = os.environ.get("BSGEN_SAM_API_URL", "")
    sam_api_key = os.environ.get("BSGEN_SAM_API_KEY", "")
    use_sam = bool(sam_api_url and sam_api_key)

    slug = slug_from_filename(post_path)
    date_str = date_from_filename(post_path)

    content = post_path.read_text(encoding="utf-8")
    errors_found = False
    hero_url = None  # Track the first og_card/hero image for frontmatter

    for block in asset_blocks:
        if block["validation_errors"]:
            for err in block["validation_errors"]:
                print(f"SKIP asset #{block['index']}: {err}", file=sys.stderr)
            errors_found = True
            continue

        data = block["data"]
        raw_asset_id = data.get("id", f"asset-{block['index']}")
        asset_id = sanitize_asset_id(raw_asset_id)
        output_formats = data.get("output_formats", [])

        if use_sam:
            urls = process_with_sam_api(data, asset_id, sam_api_url, sam_api_key)
            if not urls:
                print(f"ERROR: SAM API failed for asset '{asset_id}' — aborting", file=sys.stderr)
                sys.exit(1)  # Per answer 4: fail hard, keep post in 400
        else:
            # Placeholder mode: generate one SVG per output_format
            urls = {}
            for fmt_entry in output_formats:
                if isinstance(fmt_entry, dict):
                    for fmt_name, size_str in fmt_entry.items():
                        w, h = parse_size(size_str)
                        svg_content = generate_placeholder_svg(data, w, h, asset_id)
                        svg_filename = f"{date_str}-{slug}-{asset_id}-{fmt_name}.svg"
                        svg_path = output_dir / svg_filename
                        svg_path.write_text(svg_content, encoding="utf-8")
                        rel_url = f"/assets/images/bsgen/{svg_filename}"
                        urls[fmt_name] = rel_url
                        print(f"OK: placeholder SVG → {svg_path}", file=sys.stderr)

        if not urls:
            print(f"WARNING: no URLs generated for asset '{asset_id}'", file=sys.stderr)
            errors_found = True
            continue

        # Pick the in-post image (prefer og_card, then first available)
        in_post_url = urls.get("og_card") or urls.get("linkedin_post") or next(iter(urls.values()))

        # Track hero URL for frontmatter (first hero_image or social_card)
        if data.get("type") in ("hero_image", "social_card") and hero_url is None:
            hero_url = in_post_url

        # Build replacement figure tag — uses the RAW id to locate the
        # original ```bsgen:asset block text, which still contains whatever
        # the author literally typed (sanitize_asset_id() only applies to
        # the on-disk filename, not to matching against post content).
        figure_tag = render_figure_tag(raw_asset_id, in_post_url, post_path, content, data)

        # Add placeholder note + JSON manifest of all URLs as HTML comment
        urls_comment = f"\n<!-- bsgen:asset urls {json.dumps(urls)} -->"
        replacement = f"{PLACEHOLDER_NOTE}\n{figure_tag}{urls_comment}"

        if block["raw"] in content:
            content = content.replace(block["raw"], replacement, 1)
            print(f"OK: replaced asset '{asset_id}' with image tag → {in_post_url}", file=sys.stderr)
        else:
            print(f"WARNING: asset '{asset_id}' raw block not found in file", file=sys.stderr)

    # Update frontmatter: set image (for Jekyll) and pipeline_state
    if hero_url:
        content = update_frontmatter_field(content, "image", hero_url)

    # pipeline_state possible values:
    # - visual_review_needed : bsgen processing complete; human must review generated assets
    # - visual_review_ok     : human approved the visuals; ready for automoveandpublish pipeline
    # - bsgen_processing     : bsgen workflow is currently running (set at job start)
    # - bsgen_error          : processing failed; see bsgen_error_message frontmatter field
    content = update_frontmatter_field(content, "pipeline_state", "visual_review_needed")

    post_path.write_text(content, encoding="utf-8")
    print(f"INFO: asset processing complete for {post_path} (SAM={'live' if use_sam else 'placeholder'})", file=sys.stderr)

    return 2 if errors_found else 0


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Process bsgen:asset blocks")
    parser.add_argument("post_file")
    parser.add_argument("output_dir", help="Where to save generated assets")
    parser.add_argument("--site-url", default="", help="Site base URL for asset paths")
    args = parser.parse_args()

    post_path = Path(args.post_file)
    output_dir = Path(args.output_dir)

    if not post_path.exists():
        print(f"ERROR: file not found: {post_path}", file=sys.stderr)
        sys.exit(1)

    exit_code = process(post_path, output_dir, args.site_url)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
