"""
render_type_gallery.py

QA tool: renders one sample SVG per (fragment type x brand/palette) combo
using generate_placeholder_svg(), so a human can review every visual
composition and every color variant in one pass before trusting the
pipeline against real content. Built 2026-08-06 after 3 rounds of bugs
were found only by actually looking at rendered images — this makes that
review systematic instead of ad-hoc.

Each output file is numbered (in the filename AND as a small corner badge
baked into JUST this QA render, never into generate_placeholder_svg's real
output) so a reviewer can say "fix #7" instead of describing an image.

Usage:
    python render_type_gallery.py <output_dir>

Produces <output_dir>/NN-<type>-<brand>-<palette>.svg for each combo, plus
a manifest.json describing what's what.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from process_assets import generate_placeholder_svg, BRAND_PALETTES  # noqa: E402

WIDTH, HEIGHT = 1200, 630

# One representative data payload per fragment type — realistic content,
# not lorem-ipsum, so wrapping/overflow behavior matches what real posts
# will actually produce.
SAMPLE_DATA_BY_TYPE = {
    "hero_image": {
        # generate_placeholder_svg() is called directly here, bypassing
        # parse_bsgen_blocks.py's normalize_asset_aliases() — so this MUST
        # use the canonical headline/subheadline keys, not the title/
        # subtitle aliases real content sometimes uses (see
        # test_parse_bsgen_blocks.py for the alias behavior itself).
        "type": "hero_image",
        "headline": "Legal Documents for Gmail Add-ons: What Google Actually Reviews",
        "subheadline": "A field guide to privacy policies, terms of service, and the 15-minute deploy",
    },
    "pullquote": {
        "type": "pullquote",
        "quote": "The difference between $50,000 and $1,800 isn't just a number — it's a hobbled product versus a complete one.",
        "attribution": "Full Bright, Bright Softwares (bright-softwares.com)",
    },
    "stat_card": {
        "type": "stat_card",
        "stat_value": "87%",
        "stat_label": "of enterprise engineering teams report improved review turnaround after adopting async tooling",
    },
    "comparison_table": {
        "type": "comparison_table",
        "table_title": "What Google Reviews in Your Gmail Add-on Privacy Policy",
        "columns": ["Section", "Generic (Fails)", "Specific (Passes)"],
        "rows": [
            ["Data access", "We access Gmail data", "We view specific labels only"],
            ["Data storage", "Data may be stored", "We store no email content"],
            ["Data deletion", "No deletion policy stated", "Auto-deleted after 30 days"],
            ["Liability (ToS)", "Vague liability language", "Explicit limitation clause"],
        ],
    },
    "before_after": {
        "type": "comparison_table",
        "table_title": "First Add-on vs. Second Add-on",
        "before_value": "2 hours: finding templates, adapting, deploying, verifying URLs",
        "before_label": "First add-on (Notiwise)",
        "after_value": "15 minutes: locate templates, substitute name + scopes, deploy",
        "after_label": "Second add-on (Pilotflow)",
        "delta": "87% time reduction on the second build",
    },
}

# (brand, palette) combos to render per type. Types are only rendered for
# brands where the combo is meaningful: every type gets both bright-softwares
# palettes (the only brand currently in live use) and both luminous palettes
# (the 2nd multi-variant brand) to exercise color variation; the 4
# single-palette brands get just the hero_image type as a brand-render
# smoke check (they have no "variation" to compare — see the TODO in
# BRAND_PALETTES about their un-audited placeholder hex values).
COMBOS = []
for brand in ("bright-softwares", "luminous"):
    for palette in BRAND_PALETTES[brand]:
        for type_key in SAMPLE_DATA_BY_TYPE:
            COMBOS.append((type_key, brand, palette))
for brand in ("personal", "ieatmyhealth", "moda-by-flora", "eagles-techs"):
    COMBOS.append(("hero_image", brand, "hero"))


def add_number_badge(svg: str, number: int) -> str:
    """QA-only: bake a small numbered badge into the top-right corner so a
    reviewer can reference '#7' without needing the filename. This is
    injected AFTER generate_placeholder_svg() runs — never part of the
    function itself, so production output never carries it (the whole
    point of fixing the debug-badge bug this gallery exists to re-verify)."""
    badge = (
        f'<circle cx="{WIDTH - 40}" cy="40" r="22" fill="#000000" opacity="0.55"/>'
        f'<text x="{WIDTH - 40}" y="40" font-family="system-ui, sans-serif" '
        f'font-size="20" font-weight="700" fill="#FFFFFF" text-anchor="middle" '
        f'dominant-baseline="middle">{number}</text>'
    )
    # Insert just before the closing </svg> tag.
    return svg.replace("</svg>", badge + "</svg>")


def main():
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "./gallery_output")
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for i, (type_key, brand, palette) in enumerate(COMBOS, 1):
        data = dict(SAMPLE_DATA_BY_TYPE[type_key])
        data["brand"] = brand
        data["palette"] = palette
        svg = generate_placeholder_svg(data, WIDTH, HEIGHT, f"gallery-{i}")
        svg = add_number_badge(svg, i)

        filename = f"{i:02d}-{type_key}-{brand}-{palette}.svg"
        (out_dir / filename).write_text(svg, encoding="utf-8")

        manifest.append({
            "number": i,
            "file": filename,
            "type": type_key,
            "brand": brand,
            "palette": palette,
        })
        print(f"OK: #{i:02d} {type_key} / {brand} / {palette} -> {filename}")

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n{len(manifest)} images written to {out_dir}")


if __name__ == "__main__":
    main()
