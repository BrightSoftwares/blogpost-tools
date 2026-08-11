"""
check_post_integrity.py

Final integrity sweep before a post can be trusted to advance to
pipeline_state: visual_review_ok (i.e. "ready to go live"). Catches two
classes of bug the per-block bsgen processors can silently let through
(2026-08-06, human reviewer feedback on a live draft):

1. Raw, un-processed bsgen blocks/comments still present in the post body.
   A block that fails validate_* (e.g. a STAT callout missing required
   fields) is skipped with exit code 2 ("non-fatal, continue") — nothing
   stops the post from reaching visual_review_needed with literal internal
   markup like ```bsgen:callout``` still exposed to readers. This is a
   defense-in-depth check: even after a specific validation bug is fixed
   (see parse_bsgen_blocks.py's STAT handling), THIS check is what actually
   catches the next one before it ships, instead of relying on a human to
   spot raw markup while reviewing generated images.

2. Internal links that don't resolve to a real published post. A
   content-drafting session can hand-write a markdown link or <a href> with
   a guessed future publish date/slug (bypassing both the wikilinks plugin
   and process_related.py's own resolver, which only sees bsgen:related
   blocks, not prose links) — if the guess is wrong, it's a 404 once live.

This does NOT replace process_related.py — it complements it by sweeping the
WHOLE post body (any link in prose, not just bsgen:related block anchors).

Usage:
    python check_post_integrity.py <post_file> <posts_dir> <site_url> \\
        [--language en] [--strict]

    --strict   Exit 1 (fatal) if any issue is found — use this to gate a
               post's pipeline_state transition. Without --strict, issues
               are reported but the script exits 2 (non-fatal), matching
               the other bsgen processors' convention.

Exit codes:
    0 = clean, no issues found
    1 = issues found AND --strict was passed
    2 = issues found, --strict not passed (report only)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
from process_related import load_posts_index, STOP_WORDS  # noqa: E402
from parse_bsgen_blocks import extract_frontmatter  # noqa: E402

# A raw ```bsgen:<type>``` fence that survived processing — the block was
# either never run, or was skipped due to a validation error.
RAW_BSGEN_FENCE_RE = re.compile(r"```bsgen:\w+")

# Raw bsgen:* HTML comments that AREN'T the expected post-processing markers.
# Of these four, only `urls {...}` (written by process_assets.py's process())
# actually lands in a post's markdown content today — `type=`/`placeholder |`/
# `render_mode=` are written by generate_placeholder_svg() into the generated
# .svg FILE, never into the post body (code review finding, 2026-08-06: this
# allowlist previously claimed all four are post-content markers, which
# wasn't true). The SVG-only three stay allow-listed defensively — if a
# future change ever inlines placeholder markup into post content, it
# shouldn't retroactively start failing this check.
_EXPECTED_ASSET_COMMENT_RE = re.compile(r"<!--\s*bsgen:asset\s+(type=|placeholder\s*\||render_mode=|urls\s)")


def find_raw_bsgen_leaks(content: str) -> list[str]:
    """Anything that still looks like un-processed bsgen source markup."""
    issues = []
    for m in RAW_BSGEN_FENCE_RE.finditer(content):
        line_no = content.count("\n", 0, m.start()) + 1
        issues.append(f"line {line_no}: unprocessed bsgen fence left in content: {m.group(0)!r}")

    for m in re.finditer(r"<!--\s*bsgen:[\w-]+[^>]*-->", content):
        if _EXPECTED_ASSET_COMMENT_RE.match(m.group(0)):
            continue
        line_no = content.count("\n", 0, m.start()) + 1
        issues.append(f"line {line_no}: unexpected raw bsgen comment: {m.group(0)!r}")

    return issues


# Markdown [text](url) and raw <a href="url"> — only ones that look like an
# internal Jekyll dated-post URL are checked (external links, anchors, and
# non-post internal paths like /assets/... or /feed.xml are out of scope).
# The optional `(?:\s+"[^"]*")?` tail handles CommonMark's link-title syntax
# ([text](url "title")) — without it, a titled link with a bad guessed date
# was silently invisible to this scanner (code review finding, 2026-08-06).
_MARKDOWN_LINK_RE = re.compile(
    r'\[([^\]]*)\]\((/[^)\s]+|https?://[^)\s]+)(?:\s+"[^"]*")?\)'
)
_HTML_HREF_RE = re.compile(r'href="(/[^"]+|https?://[^"]+)"')
_DATED_POST_PATH_RE = re.compile(r"/\d{4}/\d{2}/\d{2}/")


def _same_origin(url: str, site_url: str) -> bool:
    """True for origin-relative paths ('/x') or an exact scheme+host match
    with site_url. A naive `str.startswith(site_root)` (the original check
    here) would misclassify a lookalike host like
    'https://bright-softwares.com.evil.com/...' or a protocol-relative
    '//evil.com/...' as internal (security review finding, 2026-08-06 — not
    exploitable as-is since such URLs still fail to resolve to a known post
    and get reported anyway, but worth being precise about "internal").
    """
    parsed = urlparse(url)
    if not parsed.netloc:
        return url.startswith("/") and not url.startswith("//")
    site_parsed = urlparse(site_url)
    return (parsed.scheme, parsed.netloc) == (site_parsed.scheme, site_parsed.netloc)


def extract_internal_links(content: str, site_url: str) -> list[tuple[str, str]]:
    """Return [(anchor_text, url), ...] for links pointing at this same site."""
    links = []
    for m in _MARKDOWN_LINK_RE.finditer(content):
        text, url = m.group(1), m.group(2)
        if _same_origin(url, site_url):
            links.append((text, url))
    for m in _HTML_HREF_RE.finditer(content):
        url = m.group(1)
        if _same_origin(url, site_url):
            links.append(("", url))
    return links


def normalize_path(url: str, site_url: str) -> str:
    """Reduce a same-origin URL to just its path, so '/en/...' and
    'https://site/en/...' compare equal regardless of how it was written."""
    parsed = urlparse(url)
    path = parsed.path if parsed.netloc else url
    if not path.startswith("/"):
        path = "/" + path
    return path if path.endswith("/") else path + "/"


def check_internal_links(content: str, posts_index: list[dict], site_url: str) -> list[str]:
    known_paths = {normalize_path(p["url"], site_url) for p in posts_index}

    issues = []
    for text, url in extract_internal_links(content, site_url):
        if not _DATED_POST_PATH_RE.search(url):
            continue  # not a dated post URL — out of scope for this check
        norm = normalize_path(url, site_url)
        if norm not in known_paths:
            issues.append(
                f"internal link does not resolve to any published post: "
                f"{url!r} (anchor text: {text!r})"
            )
    return issues


def check_duplicate_topic(current_fm: dict, current_slug: str, posts_index: list[dict]) -> list[str]:
    """Flag (never auto-fix) when a very-similar post already exists.

    Heuristic only: exact tag-set match + a title sharing 3+ significant
    words. This is a content-editorial signal for a human, not something
    this script decides — see check_post_integrity's own docstring.
    """
    current_tags = set(t.lower() for t in (current_fm.get("tags", []) or []))
    if not current_tags:
        return []

    def _title_words(title: str) -> set[str]:
        # Filter common words the same way process_related.py's own
        # title/keyword overlap scorer does — without this, two unrelated
        # posts sharing only "with"/"your"/"this" register a false overlap
        # (code review finding, 2026-08-06).
        return set(
            w for w in re.findall(r"[a-z0-9]+", title.lower())
            if len(w) > 3 and w not in STOP_WORDS
        )

    current_title_words = _title_words(str(current_fm.get("title", "")))
    issues = []
    for post in posts_index:
        if post["slug"] == current_slug:
            continue
        cand_tags = set(t.lower() for t in (post.get("tags", []) or []))
        if not cand_tags or cand_tags != current_tags:
            continue
        cand_title_words = _title_words(str(post.get("title", "")))
        overlap = current_title_words & cand_title_words
        if len(overlap) >= 3:
            issues.append(
                f"possible duplicate topic: identical tag set + title overlap "
                f"({sorted(overlap)}) with already-published {post['url']!r} "
                f"({post['title']!r}) — human editorial call, not auto-fixed"
            )
    return issues


def process(post_path: Path, posts_dir: Path, site_url: str, language: str = "en") -> tuple[int, list[str]]:
    content = post_path.read_text(encoding="utf-8")
    current_fm = extract_frontmatter(content)
    current_slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", post_path.stem)

    posts_index = load_posts_index(posts_dir, site_url, language) if posts_dir.exists() else []

    issues = []
    issues += find_raw_bsgen_leaks(content)
    issues += check_internal_links(content, posts_index, site_url)
    issues += check_duplicate_topic(current_fm, current_slug, posts_index)

    return (0 if not issues else 1), issues


def main():
    parser = argparse.ArgumentParser(description="Final integrity sweep for a bsgen-processed post")
    parser.add_argument("post_file")
    parser.add_argument("posts_dir", help="Path to en/_posts/ (or matching language dir)")
    parser.add_argument("site_url", help="e.g. https://bright-softwares.com")
    parser.add_argument("--language", default="en")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 (fatal) on any issue instead of 2 (report-only)")
    args = parser.parse_args()

    post_path = Path(args.post_file)
    if not post_path.exists():
        print(f"ERROR: post file not found: {post_path}", file=sys.stderr)
        sys.exit(1)

    found_any, issues = process(post_path, Path(args.posts_dir), args.site_url, args.language)

    if not found_any:
        print(f"OK: no integrity issues found in {post_path}", file=sys.stderr)
        sys.exit(0)

    print(f"ISSUES found in {post_path}:", file=sys.stderr)
    for issue in issues:
        print(f"  - {issue}", file=sys.stderr)

    sys.exit(1 if args.strict else 2)


if __name__ == "__main__":
    main()
