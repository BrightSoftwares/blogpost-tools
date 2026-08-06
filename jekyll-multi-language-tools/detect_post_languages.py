#!/usr/bin/env python3
"""Detect the language of every post/page/product in a Jekyll site and report
whether it already complies with the multi-language folder architecture
(`_posts/<lang>/`, `_pages/<lang>/`, `_products/<lang>/`).

Read-only / non-destructive: this script never writes to the site directory.
It is the Phase 1 preparation step for `migrate_jekyll_repo.py` (SP14.5) and
is safe to run repeatedly, including against an already-migrated repo, as an
audit / idempotency check.

Detection order per file:
    1. Already under a known `<collection>/<lang>/` folder -> COMPLIANT (lang
       taken from the folder name, frontmatter is cross-checked and flagged
       as an ANOMALY if it disagrees).
    2. Flat file (not yet split by language) with a `lang:` frontmatter field
       -> NEEDS_MOVE (target = `<collection>/<lang>/<filename>`).
    3. Flat file with no `lang:` field -> best-effort content detection via
       the optional `langdetect` package. Falls back to `UNKNOWN` (flagged
       for manual review) if `langdetect` is not installed or confidence is
       too low to trust.
    4. Mixed-language heuristic: the first half and second half of the body
       are detected separately; if they disagree with high confidence the
       post is flagged as a MIXED anomaly regardless of source.

Usage:
    # Human-readable markdown report to stdout
    python detect_post_languages.py /path/to/jekyll-site

    # Write a markdown report to a file
    python detect_post_languages.py /path/to/jekyll-site --output report.md

    # Machine-readable JSON (for migrate_jekyll_repo.py --detection-report)
    python detect_post_languages.py /path/to/jekyll-site --format json --output report.json

    # Only scan posts, custom known languages
    python detect_post_languages.py /path/to/jekyll-site --collections _posts --languages en,fr,de
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

try:
    from langdetect import DetectorFactory, detect_langs

    DetectorFactory.seed = 0  # deterministic results across runs
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

DEFAULT_COLLECTIONS = ["_posts", "_pages", "_products"]
DEFAULT_LANGUAGES = ["en", "fr"]
MIN_CONFIDENCE = 0.70  # below this, content-detected lang is UNKNOWN not a guess


@dataclass
class PostEntry:
    collection: str
    current_path: str
    filename: str
    frontmatter_lang: str = ""
    detected_lang: str = ""
    detected_confidence: float = 0.0
    target_lang: str = ""
    target_path: str = ""
    status: str = ""  # COMPLIANT | NEEDS_MOVE | NEEDS_FRONTMATTER | MIXED | UNKNOWN
    notes: list = field(default_factory=list)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Detect post/page/product language and migration readiness "
        "for the multi-language Jekyll architecture (read-only)."
    )
    parser.add_argument("site_dir", help="Path to Jekyll site root")
    parser.add_argument(
        "--collections",
        default=",".join(DEFAULT_COLLECTIONS),
        help=f"Comma-separated collections to scan (default: {','.join(DEFAULT_COLLECTIONS)})",
    )
    parser.add_argument(
        "--languages",
        default=",".join(DEFAULT_LANGUAGES),
        help=f"Comma-separated known language codes (default: {','.join(DEFAULT_LANGUAGES)})",
    )
    parser.add_argument(
        "--output", default=None, help="Write report to this file (default: stdout)"
    )
    parser.add_argument(
        "--format", choices=["md", "json"], default="md", help="Report format (default: md)"
    )
    return parser.parse_args()


def extract_frontmatter(content: str) -> tuple[str, str]:
    """Split content into frontmatter text and body (mirrors translate_posts.py)."""
    if not content.startswith("---"):
        return "", content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return "", content
    return parts[1], parts[2]


def get_frontmatter_value(fm_text: str, field_name: str) -> str:
    match = re.search(
        rf"^{re.escape(field_name)}:\s*[\"']?(.+?)[\"']?\s*$", fm_text, re.MULTILINE
    )
    return match.group(1) if match else ""


def strip_liquid_and_markdown(body: str) -> str:
    """Rough cleanup so langdetect sees prose, not markup noise."""
    text = re.sub(r"\{%.*?%\}", " ", body, flags=re.DOTALL)
    text = re.sub(r"\{\{.*?\}\}", " ", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"[#*_`>\[\]()!-]", " ", text)
    return text.strip()


def detect_language_content(text: str) -> tuple[str, float]:
    """Return (lang_code, confidence). ('', 0.0) if undetectable."""
    if not HAS_LANGDETECT or not text.strip():
        return "", 0.0
    try:
        candidates = detect_langs(text)
    except Exception:
        return "", 0.0
    if not candidates:
        return "", 0.0
    top = candidates[0]
    return top.lang, round(top.prob, 3)


def check_mixed_language(body: str) -> bool:
    """Best-effort: split body in half, detect each half, flag disagreement."""
    if not HAS_LANGDETECT:
        return False
    clean = strip_liquid_and_markdown(body)
    if len(clean) < 400:
        return False  # too short to split reliably
    mid = len(clean) // 2
    first_half, second_half = clean[:mid], clean[mid:]
    lang1, conf1 = detect_language_content(first_half)
    lang2, conf2 = detect_language_content(second_half)
    if not lang1 or not lang2:
        return False
    return lang1 != lang2 and conf1 >= MIN_CONFIDENCE and conf2 >= MIN_CONFIDENCE


def scan_collection(site_dir: Path, collection: str, languages: list[str]) -> list[PostEntry]:
    collection_dir = site_dir / collection
    if not collection_dir.exists():
        return []

    entries: list[PostEntry] = []

    # 1) Files already inside a <collection>/<lang>/ subfolder.
    for lang in languages:
        lang_dir = collection_dir / lang
        if not lang_dir.is_dir():
            continue
        for post_path in sorted(lang_dir.glob("*.md")):
            entry = _build_entry(site_dir, collection, post_path, languages)
            entry.detected_lang = lang
            if entry.frontmatter_lang and entry.frontmatter_lang != lang:
                entry.status = "MIXED"
                entry.notes.append(
                    f"folder says lang={lang} but frontmatter says lang={entry.frontmatter_lang}"
                )
            else:
                entry.status = "COMPLIANT"
            entry.target_lang = lang
            entry.target_path = entry.current_path
            entries.append(entry)

    # 2) Flat files directly under the collection (not yet split by language).
    for post_path in sorted(collection_dir.glob("*.md")):
        entry = _build_entry(site_dir, collection, post_path, languages)

        if entry.frontmatter_lang and entry.frontmatter_lang in languages:
            entry.status = "NEEDS_MOVE"
            entry.target_lang = entry.frontmatter_lang
        elif entry.frontmatter_lang:
            entry.status = "NEEDS_MOVE"
            entry.target_lang = entry.frontmatter_lang
            entry.notes.append(
                f"lang '{entry.frontmatter_lang}' not in known --languages list, verify manually"
            )
        else:
            content = post_path.read_text(encoding="utf-8", errors="replace")
            _, body = extract_frontmatter(content)
            clean_body = strip_liquid_and_markdown(body)
            lang, confidence = detect_language_content(clean_body[:3000])
            entry.detected_lang = lang
            entry.detected_confidence = confidence
            if check_mixed_language(body):
                entry.status = "MIXED"
                entry.notes.append("first-half/second-half language detection disagree")
            elif lang and confidence >= MIN_CONFIDENCE:
                entry.status = "NEEDS_FRONTMATTER"
                entry.target_lang = lang
                entry.notes.append(
                    f"no 'lang:' field; content-detected '{lang}' (confidence {confidence})"
                )
                if lang not in languages:
                    entry.notes.append(
                        f"detected lang '{lang}' not in known --languages list, verify manually"
                    )
            else:
                entry.status = "UNKNOWN"
                if not HAS_LANGDETECT:
                    entry.notes.append(
                        "langdetect not installed (pip install langdetect) — cannot auto-detect"
                    )
                else:
                    entry.notes.append("no 'lang:' field and detection confidence too low")

        if entry.target_lang:
            entry.target_path = str(
                (collection_dir / entry.target_lang / post_path.name).relative_to(site_dir)
            )
        entries.append(entry)

    return entries


def _build_entry(site_dir: Path, collection: str, post_path: Path, languages: list[str]) -> PostEntry:
    content = post_path.read_text(encoding="utf-8", errors="replace")
    fm_text, _ = extract_frontmatter(content)
    fm_lang = get_frontmatter_value(fm_text, "lang")
    return PostEntry(
        collection=collection,
        current_path=str(post_path.relative_to(site_dir)),
        filename=post_path.name,
        frontmatter_lang=fm_lang,
    )


def render_markdown(all_entries: list[PostEntry], site_dir: Path) -> str:
    lines = [f"# Language Detection Report — `{site_dir.name}`", ""]
    lines.append(
        f"Generated by `detect_post_languages.py` "
        f"(langdetect {'available' if HAS_LANGDETECT else 'NOT installed — content detection skipped'})."
    )
    lines.append("")

    counts: dict[str, int] = {}
    for e in all_entries:
        counts[e.status] = counts.get(e.status, 0) + 1

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total files scanned: **{len(all_entries)}**")
    for status in ["COMPLIANT", "NEEDS_MOVE", "NEEDS_FRONTMATTER", "MIXED", "UNKNOWN"]:
        if status in counts:
            lines.append(f"- `{status}`: {counts[status]}")
    lines.append("")

    if not all_entries:
        lines.append("No matching collection files found.")
        return "\n".join(lines)

    non_compliant = [e for e in all_entries if e.status != "COMPLIANT"]
    if non_compliant:
        lines.append("## Action Required")
        lines.append("")
        lines.append("| Collection | File | Status | Frontmatter lang | Detected lang | Target path | Notes |")
        lines.append("|---|---|---|---|---|---|---|")
        for e in non_compliant:
            conf = f" ({e.detected_confidence})" if e.detected_confidence else ""
            lines.append(
                f"| {e.collection} | {e.filename} | {e.status} | {e.frontmatter_lang or '-'} "
                f"| {e.detected_lang or '-'}{conf} | {e.target_path or '-'} | {'; '.join(e.notes) or '-'} |"
            )
        lines.append("")

    compliant = [e for e in all_entries if e.status == "COMPLIANT"]
    if compliant:
        lines.append(f"## Already Compliant ({len(compliant)})")
        lines.append("")
        lines.append("<details><summary>Expand</summary>")
        lines.append("")
        for e in compliant:
            lines.append(f"- `{e.current_path}` (lang={e.detected_lang})")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    return "\n".join(lines)


def main():
    args = parse_args()
    site_dir = Path(args.site_dir).resolve()
    if not site_dir.exists():
        print(f"ERROR: Site directory not found: {site_dir}", file=sys.stderr)
        sys.exit(1)

    collections = [c.strip() for c in args.collections.split(",") if c.strip()]
    languages = [l.strip() for l in args.languages.split(",") if l.strip()]

    all_entries: list[PostEntry] = []
    for collection in collections:
        all_entries.extend(scan_collection(site_dir, collection, languages))

    if args.format == "json":
        payload = {
            "site": site_dir.name,
            "collections": collections,
            "languages": languages,
            "langdetect_available": HAS_LANGDETECT,
            "entries": [asdict(e) for e in all_entries],
        }
        output = json.dumps(payload, indent=2)
    else:
        output = render_markdown(all_entries, site_dir)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(output)

    # Exit non-zero if anything needs attention, so this can gate CI if desired.
    non_compliant = [e for e in all_entries if e.status != "COMPLIANT"]
    sys.exit(1 if non_compliant else 0)


if __name__ == "__main__":
    main()
