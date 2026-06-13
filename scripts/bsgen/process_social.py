"""
process_social.py

Extracts bsgen:social blocks from a Markdown post to JSON files,
then removes the blocks from the post (they live inside <!-- SOCIAL --> comments).

Output files: <output_dir>/YYYY-MM-DD-{slug}-{platform}-{post_type}.json
The bsgen:social fence (and the enclosing <!-- SOCIAL --> section if empty) is
removed from the post file.

Usage:
    python process_social.py <post_file> <output_dir>

Exit codes:
    0 = success
    1 = fatal error
    2 = validation errors (blocks with errors are skipped)
"""

import sys
import re
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from parse_bsgen_blocks import parse_file


def slug_from_filename(post_path: Path) -> str:
    """Derive post slug from filename (strip date prefix YYYY-MM-DD- and .md)."""
    name = post_path.stem  # e.g. 2026-06-01-my-post-title
    date_prefix = re.match(r"^\d{4}-\d{2}-\d{2}-", name)
    if date_prefix:
        return name[date_prefix.end():]
    return name


def date_from_filename(post_path: Path) -> str:
    """Extract YYYY-MM-DD date from filename, or use today."""
    match = re.match(r"^(\d{4}-\d{2}-\d{2})-", post_path.stem)
    if match:
        return match.group(1)
    return datetime.now().strftime("%Y-%m-%d")


def process(post_path: Path, output_dir: Path) -> int:
    """Extract social blocks. Returns exit code."""
    parsed = parse_file(post_path, filter_type="social")

    social_blocks = parsed["blocks"]["social"]
    if not social_blocks:
        print(f"INFO: no bsgen:social blocks found in {post_path}", file=sys.stderr)
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    content = post_path.read_text(encoding="utf-8")

    slug = slug_from_filename(post_path)
    date_str = date_from_filename(post_path)
    errors_found = False
    extracted = 0

    for block in social_blocks:
        if block["validation_errors"]:
            for err in block["validation_errors"]:
                print(f"SKIP social #{block['index']}: {err}", file=sys.stderr)
            errors_found = True
            continue

        data = block["data"]
        platform = data.get("platform", "unknown")
        post_type = data.get("post_type", "unknown").replace("_", "-")

        out_file = output_dir / f"{date_str}-{slug}-{platform}-{post_type}.json"

        payload = {
            "source_post": str(post_path),
            "slug": slug,
            "date": date_str,
            "platform": platform,
            "post_type": data.get("post_type"),
            "source_section": data.get("source_section"),
            "brand": data.get("brand"),
            "content": data,
        }

        out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"OK: extracted social #{block['index']} → {out_file}", file=sys.stderr)
        extracted += 1

        # Remove block from content
        if block["raw"] in content:
            content = content.replace(block["raw"], "", 1)

    # Clean up empty <!-- SOCIAL --> ... <!-- /SOCIAL --> sections
    content = re.sub(
        r"<!--\s*SOCIAL\s*-->\s*<!--\s*/SOCIAL\s*-->",
        "",
        content,
        flags=re.DOTALL
    )
    # Clean up <!-- SOCIAL --> sections that now only have whitespace
    content = re.sub(
        r"<!--\s*SOCIAL\s*-->\s*(<!--\s*/SOCIAL\s*-->)?",
        lambda m: "" if not m.group(1) or m.group(0).strip() == m.group(0).strip() else m.group(0),
        content
    )

    post_path.write_text(content, encoding="utf-8")
    print(f"INFO: {extracted} social block(s) extracted from {post_path}", file=sys.stderr)

    return 2 if errors_found else 0


def main():
    if len(sys.argv) < 3:
        print("Usage: process_social.py <post_file> <output_dir>", file=sys.stderr)
        sys.exit(1)

    post_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not post_path.exists():
        print(f"ERROR: file not found: {post_path}", file=sys.stderr)
        sys.exit(1)

    exit_code = process(post_path, output_dir)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
