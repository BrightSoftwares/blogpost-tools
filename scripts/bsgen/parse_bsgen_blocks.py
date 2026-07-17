"""
parse_bsgen_blocks.py

Extracts and validates all bsgen:* fenced code blocks from a Markdown post.
Outputs JSON to stdout. Used by all four bsgen processor scripts.

Usage:
    python parse_bsgen_blocks.py <post_file> [--type asset|callout|social|related]

Exit codes:
    0 = success (even if no blocks found)
    1 = file not found
    2 = validation error (with --strict flag)
"""

import sys
import re
import json
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml


# Brevity guideline for callout `content`. Callouts render as a flowing HTML
# <p class="bs-callout__content"> that wraps naturally (see process_callouts.py) —
# unlike pullquotes / social cards, which render into fixed-dimension images where
# over-length text genuinely overflows the canvas. Over-length callout content is
# therefore a *soft* nudge toward brevity, not a rendering failure: the block is
# still rendered and a warning is logged. (Fix: over-length callouts used to raise a
# fatal validation error that halted the whole bsgen pipeline with exit code 2.)
CALLOUT_CONTENT_SOFT_LIMIT = 120

VALID_BLOCK_TYPES = {"asset", "callout", "social", "related"}
VALID_BRANDS = {
    "luminous", "bright-softwares", "personal",
    "ieatmyhealth", "moda-by-flora", "eagles-techs"
}

# Matches ```bsgen:TYPE ... ``` fences (non-greedy, handles any content inside)
BSGEN_FENCE_RE = re.compile(
    r"```bsgen:(\w+)\s*\n(.*?)```",
    re.DOTALL
)


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from a Jekyll post."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def parse_block_body(raw_yaml: str, block_type: str, index: int) -> dict | None:
    """Parse YAML body of a bsgen block. Returns None on parse failure."""
    try:
        data = yaml.safe_load(raw_yaml)
        if data is None:
            data = {}
        if not isinstance(data, dict):
            print(f"WARNING: bsgen:{block_type} block #{index} body is not a YAML mapping — skipped", file=sys.stderr)
            return None
        return data
    except yaml.YAMLError as e:
        print(f"WARNING: bsgen:{block_type} block #{index} has invalid YAML — skipped: {e}", file=sys.stderr)
        return None


def validate_asset(data: dict, index: int) -> list[str]:
    """Return list of validation error messages for a bsgen:asset block."""
    errors = []
    for field in ("id", "type", "brand", "output_formats"):
        if field not in data:
            errors.append(f"asset #{index}: missing required field '{field}'")

    if "brand" in data and data["brand"] not in VALID_BRANDS:
        errors.append(f"asset #{index}: unknown brand '{data['brand']}' (must be one of {sorted(VALID_BRANDS)})")

    asset_type = data.get("type")
    if asset_type == "pullquote":
        if "quote" not in data:
            errors.append(f"asset #{index} (pullquote): missing 'quote'")
        elif len(str(data["quote"])) > 160:
            errors.append(f"asset #{index} (pullquote): 'quote' exceeds 160 chars")
        if "attribution" not in data:
            errors.append(f"asset #{index} (pullquote): missing 'attribution'")
    elif asset_type == "stat_card":
        for f in ("stat_value", "stat_label"):
            if f not in data:
                errors.append(f"asset #{index} (stat_card): missing '{f}'")
    elif asset_type == "comparison_table":
        for f in ("table_title", "columns", "rows"):
            if f not in data:
                errors.append(f"asset #{index} (comparison_table): missing '{f}'")
        if "columns" in data and "rows" in data:
            col_len = len(data["columns"])
            for ri, row in enumerate(data.get("rows", [])):
                if len(row) != col_len:
                    errors.append(f"asset #{index} (comparison_table): row {ri} has {len(row)} cells, expected {col_len}")
    elif asset_type == "before_after":
        for f in ("before_label", "before_value", "after_label", "after_value"):
            if f not in data:
                errors.append(f"asset #{index} (before_after): missing '{f}'")
    elif asset_type in ("social_card", "hero_image"):
        if "headline" not in data:
            errors.append(f"asset #{index} ({asset_type}): missing 'headline'")

    return errors


def validate_callout(data: dict, index: int) -> list[str]:
    errors = []
    ctype = data.get("type")
    if not ctype:
        errors.append(f"callout #{index}: missing 'type'")
        return errors
    if ctype not in ("TIP", "WARNING", "SHORTCUT", "STAT", "QUOTE"):
        errors.append(f"callout #{index}: unknown type '{ctype}'")
    if ctype in ("TIP", "WARNING", "SHORTCUT", "STAT"):
        if "content" not in data:
            errors.append(f"callout #{index} ({ctype}): missing 'content'")
        elif len(str(data["content"])) > CALLOUT_CONTENT_SOFT_LIMIT:
            # Soft guideline only — do NOT append to `errors` (that would skip the
            # block and fail the pipeline). The callout still renders; HTML wraps it.
            print(
                f"WARNING: callout #{index} ({ctype}): 'content' is "
                f"{len(str(data['content']))} chars (soft guideline: "
                f"{CALLOUT_CONTENT_SOFT_LIMIT}); rendering anyway",
                file=sys.stderr,
            )
    if ctype == "STAT":
        for f in ("stat_value", "stat_label"):
            if f not in data:
                errors.append(f"callout #{index} (STAT): missing '{f}'")
    if ctype == "QUOTE":
        for f in ("quote_text", "attribution"):
            if f not in data:
                errors.append(f"callout #{index} (QUOTE): missing '{f}'")
    return errors


def validate_social(data: dict, index: int) -> list[str]:
    errors = []
    for f in ("platform", "post_type", "source_section", "brand"):
        if f not in data:
            errors.append(f"social #{index}: missing required field '{f}'")
    if "brand" in data and data["brand"] not in VALID_BRANDS:
        errors.append(f"social #{index}: unknown brand '{data['brand']}'")

    post_type = data.get("post_type")
    platform = data.get("platform")

    if platform == "linkedin" and post_type == "single_post":
        for f in ("hook", "body", "cta"):
            if f not in data:
                errors.append(f"social #{index} (linkedin single_post): missing '{f}'")
        if "hook" in data and len(str(data["hook"])) > 200:
            errors.append(f"social #{index}: linkedin hook exceeds 200 chars")

    elif post_type == "carousel":
        for f in ("slides", "total_slides"):
            if f not in data:
                errors.append(f"social #{index} (carousel): missing '{f}'")
        slides = data.get("slides", [])
        if len(slides) > 6:
            errors.append(f"social #{index} (carousel): too many slides ({len(slides)}, max 6)")
        if slides and slides[0].get("type") != "hook_slide":
            errors.append(f"social #{index} (carousel): slide 1 must be hook_slide")
        if slides and slides[-1].get("type") != "cta_slide":
            errors.append(f"social #{index} (carousel): last slide must be cta_slide")

    elif post_type == "thread":
        tweets = data.get("tweets", [])
        if not tweets:
            errors.append(f"social #{index} (thread): missing 'tweets'")
        if len(tweets) < 5 or len(tweets) > 8:
            errors.append(f"social #{index} (thread): thread must have 5-8 tweets, got {len(tweets)}")
        for ti, tweet in enumerate(tweets):
            if len(str(tweet)) > 250:
                errors.append(f"social #{index} (thread): tweet {ti+1} exceeds 250 chars")

    elif post_type == "single_tweet":
        if "tweet" not in data:
            errors.append(f"social #{index} (single_tweet): missing 'tweet'")

    return errors


def validate_related(data: dict, index: int) -> list[str]:
    errors = []
    if "anchors" not in data:
        errors.append(f"related #{index}: missing 'anchors'")
        return errors
    for ai, anchor in enumerate(data.get("anchors", [])):
        if "wikilink" not in anchor:
            errors.append(f"related #{index} anchor {ai}: missing 'wikilink'")
        if "anchor_text" not in anchor:
            errors.append(f"related #{index} anchor {ai}: missing 'anchor_text'")
    return errors


VALIDATORS = {
    "asset": validate_asset,
    "callout": validate_callout,
    "social": validate_social,
    "related": validate_related,
}


def parse_file(post_path: Path, filter_type: str | None = None) -> dict:
    content = post_path.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter(content)

    result = {
        "file": str(post_path),
        "frontmatter": frontmatter,
        "blocks": {t: [] for t in VALID_BLOCK_TYPES},
        "validation_errors": [],
        "warnings": [],
    }

    counts = {t: 0 for t in VALID_BLOCK_TYPES}

    for match in BSGEN_FENCE_RE.finditer(content):
        raw_type = match.group(1).lower()
        raw_body = match.group(2)
        raw_full = match.group(0)

        if raw_type not in VALID_BLOCK_TYPES:
            result["warnings"].append(f"Unknown bsgen type '{raw_type}' — skipped (unknown types are ignored)")
            continue

        if filter_type and raw_type != filter_type:
            continue

        counts[raw_type] += 1
        index = counts[raw_type]

        data = parse_block_body(raw_body, raw_type, index)
        if data is None:
            continue

        errors = VALIDATORS[raw_type](data, index)
        result["validation_errors"].extend(errors)

        # Store the raw fence text so processors can do find-and-replace
        entry = {
            "index": index,
            "raw": raw_full,
            "data": data,
            "validation_errors": errors,
        }
        result["blocks"][raw_type].append(entry)

    return result


def main():
    parser = argparse.ArgumentParser(description="Parse bsgen blocks from a Markdown post")
    parser.add_argument("post_file", help="Path to the Markdown post file")
    parser.add_argument("--type", dest="block_type", choices=list(VALID_BLOCK_TYPES),
                        help="Only extract blocks of this type")
    parser.add_argument("--strict", action="store_true",
                        help="Exit with code 2 if any validation errors are found")
    args = parser.parse_args()

    post_path = Path(args.post_file)
    if not post_path.exists():
        print(f"ERROR: file not found: {post_path}", file=sys.stderr)
        sys.exit(1)

    result = parse_file(post_path, filter_type=args.block_type)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.strict and result["validation_errors"]:
        for err in result["validation_errors"]:
            print(f"VALIDATION ERROR: {err}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
