"""
process_callouts.py

Replaces bsgen:callout blocks in a Markdown post with HTML <div> elements.
Modifies the file in-place.

Usage:
    python process_callouts.py <post_file>

Exit codes:
    0 = success
    1 = file not found or fatal error
    2 = validation errors in blocks (blocks with errors are skipped, not replaced)

Reversibility: the original ```bsgen:callout fence is kept as a dormant,
HTML-commented copy immediately before the rendered <div> (see
parse_bsgen_blocks.wrap_dormant_source). To revert: delete the rendered
<div> and un-wrap the comment around the dormant fence.
"""

import sys
import json
import html
from pathlib import Path

# Allow running standalone or as part of the package
sys.path.insert(0, str(Path(__file__).parent))
from parse_bsgen_blocks import parse_file, wrap_dormant_source


def render_callout(data: dict) -> str:
    """Render a bsgen:callout dict to the bs-callout HTML div."""
    ctype = data.get("type", "TIP").upper()
    css_type = ctype.lower()

    if ctype == "STAT":
        # A STAT block is valid (per validate_callout) with either a
        # stat_value+stat_label pair or a content-only fallback — only emit
        # the stat spans when both values are actually present, otherwise
        # degrade to a plain content paragraph rather than two empty <span>s.
        has_stat_pair = "stat_value" in data and "stat_label" in data
        content = html.escape(str(data.get("content", "")))
        if has_stat_pair:
            stat_value = html.escape(str(data["stat_value"]))
            stat_label = html.escape(str(data["stat_label"]))
            inner = (
                f'<span class="bs-callout__stat-value">{stat_value}</span>'
                f'<span class="bs-callout__stat-label">{stat_label}</span>'
            )
            if content:
                inner += f'\n<p class="bs-callout__content">{content}</p>'
        else:
            inner = f'<p class="bs-callout__content">{content}</p>'

    elif ctype == "QUOTE":
        quote_text = html.escape(str(data.get("quote_text", "")))
        attribution = html.escape(str(data.get("attribution", "")))
        inner = (
            f'<blockquote class="bs-callout__quote">{quote_text}</blockquote>'
            f'<cite class="bs-callout__attribution">— {attribution}</cite>'
        )

    else:
        # TIP, WARNING, SHORTCUT
        content = html.escape(str(data.get("content", "")))
        inner = f'<p class="bs-callout__content">{content}</p>'

    return (
        f'<div class="bs-callout bs-callout--{css_type}">\n'
        f'  {inner}\n'
        f'</div>'
    )


def process(post_path: Path) -> int:
    """Process all bsgen:callout blocks. Returns number of replacements made."""
    parsed = parse_file(post_path, filter_type="callout")

    callout_blocks = parsed["blocks"]["callout"]
    if not callout_blocks:
        print(f"INFO: no bsgen:callout blocks found in {post_path}", file=sys.stderr)
        return 0

    content = post_path.read_text(encoding="utf-8")
    replacements = 0
    errors_found = False

    for block in callout_blocks:
        if block["validation_errors"]:
            for err in block["validation_errors"]:
                print(f"SKIP callout #{block['index']}: {err}", file=sys.stderr)
            errors_found = True
            continue

        html_div = render_callout(block["data"])
        if block["raw"] not in content:
            print(f"WARNING: callout #{block['index']} raw text not found in file — may have been modified", file=sys.stderr)
            continue

        replacement = f"{wrap_dormant_source(block['raw'])}\n{html_div}"
        content = content.replace(block["raw"], replacement, 1)
        replacements += 1
        print(f"OK: replaced callout #{block['index']} (type={block['data'].get('type')})", file=sys.stderr)

    post_path.write_text(content, encoding="utf-8")
    print(f"INFO: {replacements} callout(s) replaced in {post_path}", file=sys.stderr)

    return 2 if errors_found else 0


def main():
    if len(sys.argv) < 2:
        print("Usage: process_callouts.py <post_file>", file=sys.stderr)
        sys.exit(1)

    post_path = Path(sys.argv[1])
    if not post_path.exists():
        print(f"ERROR: file not found: {post_path}", file=sys.stderr)
        sys.exit(1)

    exit_code = process(post_path)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
