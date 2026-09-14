#!/usr/bin/env python3
"""
Schema Markup Generator - GitHub Actions Ready

Parses Jekyll frontmatter from blog posts and generates schema.org
Article/BlogPosting JSON-LD blocks. Never edits the source post — writes one
sidecar `<slug>.schema.json` file per post into `output_dir`, plus a combined
`schema_markup_latest.json`, following this repo's `seo-analysis` output
convention (a dedicated output directory that a separate integration step
consumes, rather than mutating the post in place).

Design decision (documented for the PR, since it is a genuine open question
this session cannot fully resolve without reading corporate-website's Jekyll
`_layouts`): sidecar files were chosen over writing a `schema_jsonld:`
frontmatter field because every other action in this repo that produces
structured output (seo-analysis, internal-linking, keyword-suggestion)
writes to a dedicated `_seo/<tool>/output/` directory rather than rewriting
the source post's frontmatter in place, and frontmatter-field JSON strings
are awkward to keep valid YAML across re-runs. A future Jekyll `_includes/`
partial can read `<slug>.schema.json` (matched by post basename) and emit
it inside a `<script type="application/ld+json">` tag — that wiring is a
corporate-website change, out of scope here.

Required fields per the schema.org Article/BlogPosting spec: `@context`,
`@type`, `headline`, `datePublished`, (`dateModified` if available),
`author`, `image`, `description`. Only `headline` (post title) and
`datePublished` (post date) are treated as UNAVOIDABLE — a post missing
either is skipped with a clear warning, never crashing the batch. Every
other field is generated best-effort and simply omitted (with a warning)
when the source data isn't available, since schema.org itself does not
require every property to be present to be valid JSON-LD.
"""

import glob as globmod
import json
import logging
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import frontmatter as fm_lib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

MAX_HEADLINE_LENGTH = 110  # Google's guidance for schema.org `headline`.

# Frontmatter keys checked, in priority order, for the post's image.
_IMAGE_FIELD_CANDIDATES = ["image", "og_image", "header_image", "hero_image", "cover_image", "thumbnail"]
# Frontmatter keys checked, in priority order, for dateModified.
_MODIFIED_FIELD_CANDIDATES = ["date_modified", "last_modified_at", "updated"]

_SLUG_DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def slugify_from_path(path: Path) -> str:
    """Jekyll convention: `_posts/2026-01-01-my-post.md` -> `my-post`."""
    stem = path.stem
    return _SLUG_DATE_PREFIX_RE.sub("", stem)


def _to_iso_date(value: Any) -> Optional[str]:
    """Normalize a frontmatter date value (date/datetime/str) to an ISO 8601
    string. Returns None if the value can't be interpreted as a date.
    """
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        # Accept "YYYY-MM-DD" or a full ISO datetime string as-is; anything
        # else is passed through rather than guessed at (schema.org expects
        # a valid ISO 8601 string, and inventing a format here could
        # silently produce an invalid one).
        if re.match(r"^\d{4}-\d{2}-\d{2}(T.*)?$", text):
            return text
        try:
            return datetime.fromisoformat(text).isoformat()
        except ValueError:
            return None
    return None


def _first_present(fm: Dict[str, Any], keys: List[str]) -> Optional[Any]:
    for key in keys:
        val = fm.get(key)
        if val:
            return val
    return None


def _resolve_url(value: str, site_url: Optional[str]) -> str:
    if value.startswith("http://") or value.startswith("https://"):
        return value
    if not site_url:
        return value
    return site_url.rstrip("/") + "/" + value.lstrip("/")


def _build_author(fm: Dict[str, Any], publisher_name: Optional[str]) -> Optional[Dict[str, str]]:
    author = fm.get("author")
    if isinstance(author, str) and author.strip():
        return {"@type": "Person", "name": author.strip()}
    if isinstance(author, dict) and author.get("name"):
        return {"@type": "Person", "name": str(author["name"])}
    if publisher_name:
        # Best-effort fallback: attribute to the publishing organization
        # rather than omit authorship entirely.
        return {"@type": "Organization", "name": publisher_name}
    return None


def build_jsonld(
    fm: Dict[str, Any],
    post_path: Path,
    site_url: Optional[str],
    publisher_name: Optional[str],
) -> "tuple[Optional[Dict[str, Any]], List[str], Optional[str]]":
    """Return (jsonld_or_None, warnings, skip_reason).

    `skip_reason` is set (and jsonld is None) only when an unavoidable
    required field (headline or datePublished) is missing.
    """
    warnings: List[str] = []

    headline = fm.get("title")
    if not headline or not str(headline).strip():
        return None, warnings, "missing required field: title (headline)"
    headline = str(headline).strip()
    if len(headline) > MAX_HEADLINE_LENGTH:
        warnings.append(f"headline truncated from {len(headline)} to {MAX_HEADLINE_LENGTH} chars")
        headline = headline[:MAX_HEADLINE_LENGTH].rstrip()

    date_published = _to_iso_date(fm.get("date"))
    if not date_published:
        return None, warnings, "missing required field: date (datePublished)"

    slug = slugify_from_path(post_path)

    jsonld: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": headline,
        "datePublished": date_published,
    }

    date_modified = _to_iso_date(_first_present(fm, _MODIFIED_FIELD_CANDIDATES))
    if date_modified:
        jsonld["dateModified"] = date_modified

    author = _build_author(fm, publisher_name)
    if author:
        jsonld["author"] = author
    else:
        warnings.append("no author found in frontmatter and no publisher_name fallback given; omitted")

    description = fm.get("description")
    if description and str(description).strip():
        jsonld["description"] = str(description).strip()
    else:
        warnings.append("no description found in frontmatter; omitted")

    image = _first_present(fm, _IMAGE_FIELD_CANDIDATES)
    if image and isinstance(image, str):
        resolved_image = _resolve_url(image, site_url)
        jsonld["image"] = resolved_image
        if not resolved_image.startswith(("http://", "https://")):
            warnings.append(
                f"image '{image}' is relative and no site_url was given; "
                "resulting JSON-LD 'image' is not an absolute URL"
            )
    else:
        warnings.append("no image found in frontmatter; omitted")

    if site_url:
        post_url = _resolve_url(f"{slug}/", site_url)
        jsonld["url"] = post_url
        jsonld["mainEntityOfPage"] = {"@type": "WebPage", "@id": post_url}
        if publisher_name:
            jsonld["publisher"] = {"@type": "Organization", "name": publisher_name}
    else:
        warnings.append("no site_url given; url/mainEntityOfPage/publisher omitted")

    return jsonld, warnings, None


def find_posts(posts_glob: str) -> List[Path]:
    matches = globmod.glob(posts_glob, recursive=True)
    paths = sorted({Path(m).resolve() for m in matches if Path(m).is_file()})
    return paths


def process_post(path: Path, site_url: Optional[str], publisher_name: Optional[str]) -> Dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"file": str(path), "status": "skipped", "reason": "non-UTF8 file content"}
    except OSError as e:
        return {"file": str(path), "status": "skipped", "reason": f"could not read file: {e}"}

    try:
        post = fm_lib.loads(raw)
        fm = dict(post.metadata)
    except Exception as e:  # noqa: BLE001 - malformed frontmatter must not crash the batch
        return {"file": str(path), "status": "skipped", "reason": f"could not parse frontmatter: {e}"}

    jsonld, warnings, skip_reason = build_jsonld(fm, path, site_url, publisher_name)

    if skip_reason:
        logger.warning("Skipping %s: %s", path, skip_reason)
        return {"file": str(path), "status": "skipped", "reason": skip_reason}

    for w in warnings:
        logger.warning("%s: %s", path, w)

    return {
        "file": str(path),
        "status": "generated",
        "slug": slugify_from_path(path),
        "jsonld": jsonld,
        "warnings": warnings,
    }


def save_results(
    results: List[Dict[str, Any]],
    output_dir: Path,
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    generated = [r for r in results if r["status"] == "generated"]
    skipped = [r for r in results if r["status"] == "skipped"]

    # One sidecar file per successfully-generated post.
    for r in generated:
        sidecar_path = Path(r["file"]).with_suffix(".schema.json")
        with open(sidecar_path, "w", encoding="utf-8") as f:
            json.dump(r["jsonld"], f, indent=2, ensure_ascii=False)
        r["sidecar_file"] = str(sidecar_path)

    payload = {
        "metadata": {
            "generation_timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "posts_processed": len(generated),
            "posts_skipped": len(skipped),
        },
        "generated": generated,
        "skipped": skipped,
    }

    json_file = output_dir / f"schema_markup_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    latest_json = output_dir / "schema_markup_latest.json"
    with open(latest_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    summary_file = output_dir / f"summary_report_{timestamp}.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("SCHEMA MARKUP GENERATOR SUMMARY\n")
        f.write("=" * 70 + "\n")
        f.write(f"Posts processed: {len(generated)}\n")
        f.write(f"Posts skipped: {len(skipped)}\n\n")
        for r in generated:
            warn_note = f" ({len(r['warnings'])} warning(s))" if r["warnings"] else ""
            f.write(f"- {r['file']} -> {r['sidecar_file']}{warn_note}\n")
        if skipped:
            f.write("\nSkipped:\n")
            for r in skipped:
                f.write(f"- {r['file']}: {r['reason']}\n")
    logger.info("Saved summary report: %s", summary_file)

    return {"latest_json": latest_json, "generated": len(generated), "skipped": len(skipped)}


def main() -> int:
    posts_glob = os.getenv("INPUT_POSTS_GLOB", "_posts/**/*.md")
    site_url = os.getenv("INPUT_SITE_URL") or None
    publisher_name = os.getenv("INPUT_PUBLISHER_NAME") or None
    output_dir = Path(os.getenv("INPUT_OUTPUT_DIR", "_seo/schema-markup-generator/output"))

    logger.info("=" * 70)
    logger.info("SCHEMA MARKUP GENERATOR CONFIGURATION")
    logger.info("=" * 70)
    logger.info("Posts glob: %s", posts_glob)
    logger.info("Site URL: %s", site_url or "(not set)")
    logger.info("Publisher name: %s", publisher_name or "(not set)")
    logger.info("Output dir: %s", output_dir)
    logger.info("=" * 70)

    posts = find_posts(posts_glob)
    if not posts:
        logger.warning("No posts matched glob %s — nothing to process.", posts_glob)

    results = [process_post(p, site_url, publisher_name) for p in posts]
    stats = save_results(results, output_dir)

    print("\n" + "=" * 70)
    print("SCHEMA MARKUP GENERATION COMPLETE")
    print("=" * 70)
    print(f"Posts processed: {stats['generated']}")
    print(f"Posts skipped: {stats['skipped']}")
    print("=" * 70)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as fh:
            print(f"report_file={stats['latest_json']}", file=fh)
            print(f"posts_processed={stats['generated']}", file=fh)
            print(f"posts_skipped={stats['skipped']}", file=fh)

    return 0


if __name__ == "__main__":
    sys.exit(main())
