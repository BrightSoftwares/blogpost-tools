"""
process_assets.py

Processes bsgen:asset blocks. When Smart Assets Manager (SAM) is live,
POSTs each block to the SAM API and replaces the block with a Markdown image tag.

Current mode (SAM not yet live): generates branded SVG placeholder images,
saves them to <output_dir>, and replaces blocks with local image references.
Set BSGEN_SAM_API_URL + BSGEN_SAM_API_KEY env vars to switch to live mode.

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

# Brand color map (from design system; used for placeholder backgrounds)
BRAND_COLORS = {
    "luminous":        {"bg": "#1A2980", "accent": "#26D0CE", "text": "#FFFFFF"},
    "bright-softwares": {"bg": "#0F1B44", "accent": "#4A90D9", "text": "#FFFFFF"},
    "personal":        {"bg": "#1A1A2E", "accent": "#E94560", "text": "#FFFFFF"},
    "ieatmyhealth":   {"bg": "#1E6B3C", "accent": "#6BCB77", "text": "#FFFFFF"},
    "moda-by-flora":   {"bg": "#4A154B", "accent": "#ECB5C9", "text": "#FFFFFF"},
    "eagles-techs":    {"bg": "#0D1117", "accent": "#58A6FF", "text": "#FFFFFF"},
}

PLACEHOLDER_NOTE = "<!-- bsgen placeholder — replace with SAM-generated image when live -->"


def slug_from_filename(post_path: Path) -> str:
    name = post_path.stem
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", name)
    return m.group(1) if m else name


def date_from_filename(post_path: Path) -> str:
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-", post_path.stem)
    return m.group(1) if m else datetime.now().strftime("%Y-%m-%d")


def generate_placeholder_svg(data: dict, width: int, height: int, asset_id: str) -> str:
    """Generate a branded SVG placeholder image for a bsgen:asset block."""
    brand = data.get("brand", "bright-softwares")
    colors = BRAND_COLORS.get(brand, BRAND_COLORS["bright-softwares"])
    bg = colors["bg"]
    accent = colors["accent"]
    text_color = colors["text"]

    asset_type = data.get("type", "asset")
    label_lines = []

    if asset_type == "pullquote":
        quote = str(data.get("quote", ""))[:80]
        attribution = str(data.get("attribution", ""))
        label_lines = [f'"{quote}"', f"— {attribution}"]
    elif asset_type == "stat_card":
        label_lines = [
            str(data.get("stat_value", "")),
            str(data.get("stat_label", "")),
        ]
    elif asset_type == "comparison_table":
        label_lines = [str(data.get("table_title", "Comparison Table"))]
    elif asset_type == "before_after":
        label_lines = [
            f"{data.get('before_value', 'Before')} → {data.get('after_value', 'After')}",
            str(data.get("delta", "")),
        ]
    elif asset_type in ("social_card", "hero_image"):
        label_lines = [str(data.get("headline", ""))]
        if data.get("subheadline"):
            label_lines.append(str(data["subheadline"])[:60])

    # Build SVG text elements
    text_y_start = height // 2 - (len(label_lines) - 1) * 22
    text_elements = ""
    for i, line in enumerate(label_lines):
        y = text_y_start + i * 44
        escaped = html_module.escape(line[:70])
        font_size = 32 if i == 0 else 20
        text_elements += (
            f'<text x="{width//2}" y="{y}" '
            f'font-family="system-ui, sans-serif" '
            f'font-size="{font_size}" '
            f'font-weight="{"700" if i == 0 else "400"}" '
            f'fill="{text_color}" '
            f'text-anchor="middle" '
            f'dominant-baseline="middle">{escaped}</text>\n'
        )

    # Type badge in corner
    type_badge = (
        f'<rect x="16" y="16" width="160" height="32" rx="8" fill="{accent}" opacity="0.9"/>'
        f'<text x="96" y="32" font-family="system-ui" font-size="13" '
        f'font-weight="600" fill="{bg}" text-anchor="middle" dominant-baseline="middle">'
        f'bsgen:{asset_type}</text>'
    )

    # Placeholder label
    placeholder_label = (
        f'<text x="{width//2}" y="{height - 20}" '
        f'font-family="system-ui" font-size="11" fill="{accent}" '
        f'text-anchor="middle" opacity="0.7">PLACEHOLDER — replace with SAM image</text>'
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <!-- bsgen:asset placeholder | id={html_module.escape(asset_id)} | brand={html_module.escape(brand)} -->
  <rect width="{width}" height="{height}" fill="{bg}"/>
  <!-- diagonal stripe pattern for placeholder visual -->
  <defs>
    <pattern id="stripes" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="20" height="40" fill="{accent}" opacity="0.06"/>
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#stripes)"/>
  <!-- border -->
  <rect x="2" y="2" width="{width-4}" height="{height-4}" rx="4" fill="none" stroke="{accent}" stroke-width="2" opacity="0.3"/>
  {type_badge}
  {text_elements}
  {placeholder_label}
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
        asset_id = data.get("id", f"asset-{block['index']}")
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

        # Build replacement figure tag
        figure_tag = render_figure_tag(asset_id, in_post_url, post_path, content, data)

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
