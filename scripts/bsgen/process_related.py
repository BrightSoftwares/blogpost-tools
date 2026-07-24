"""
process_related.py

Resolves bsgen:related blocks: for each anchor wikilink, searches the live posts
directory for a matching published post. Falls back to automatic tag/category
discovery if wikilinks don't resolve. Replaces the block with a "Related reading"
HTML module or inline links.

Discovery order:
  1. Explicit wikilinks in the block's anchors list (resolve [[slug]] to URL)
  2. Tag/category overlap with current post's frontmatter (score-based)
  3. Title + frontmatter keyword similarity (TF-IDF-lite)
  4. Generic "Explore more" link (site root) if nothing found

Usage:
    python process_related.py <post_file> <posts_dir> <site_url> [--language en]

    <posts_dir>  Path to en/_posts/ (published posts to search against)
    <site_url>   e.g. https://bright-softwares.com

Exit codes:
    0 = success
    1 = fatal error
    2 = some wikilinks dangled (resolved with fallback, not a hard failure)
"""

import sys
import re
import json
import html as html_module
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from parse_bsgen_blocks import parse_file, extract_frontmatter

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml

MAX_RELATED = 3

GENERIC_EXPLORE_MORE = {
    "url": "/",
    "title": "Explore more posts",
    "anchor_text": "Explore more on our blog",
}


def slug_from_filepath(post_path: Path) -> str:
    """Derive slug from filename: strip date prefix and .md extension."""
    name = post_path.stem
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", name)
    return m.group(1) if m else name


def url_from_filepath(post_path: Path, site_url: str, language: str) -> str:
    """Build a canonical URL for a post file."""
    slug = slug_from_filepath(post_path)
    # Try to read permalink from frontmatter first
    try:
        content = post_path.read_text(encoding="utf-8")
        fm = extract_frontmatter(content)
        if "permalink" in fm:
            return site_url.rstrip("/") + "/" + fm["permalink"].lstrip("/")
    except Exception:
        pass
    # Default Jekyll URL pattern: /lang/YYYY/MM/DD/slug/
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-", post_path.stem)
    if m:
        y, mo, d = m.group(1), m.group(2), m.group(3)
        return f"{site_url.rstrip('/')}/{language}/{y}/{mo}/{d}/{slug}/"
    return f"{site_url.rstrip('/')}/{language}/{slug}/"


def load_posts_index(posts_dir: Path, site_url: str, language: str) -> list[dict]:
    """Load frontmatter + URL for all posts in the directory."""
    index = []
    for post_file in sorted(posts_dir.glob("*.md")):
        try:
            content = post_file.read_text(encoding="utf-8")
            fm = extract_frontmatter(content)
            slug = slug_from_filepath(post_file)
            url = url_from_filepath(post_file, site_url, language)
            index.append({
                "path": post_file,
                "slug": slug,
                "url": url,
                "title": fm.get("title", slug),
                "tags": fm.get("tags", []) or [],
                "categories": fm.get("categories", []) or [],
                "description": fm.get("description", ""),
            })
        except Exception as e:
            print(f"WARNING: could not read {post_file}: {e}", file=sys.stderr)
    return index


def resolve_wikilink(wikilink: str, posts_index: list[dict]) -> dict | None:
    """Resolve [[slug]] to a post entry. Returns None if not found."""
    # Strip [[ and ]]
    slug_raw = re.sub(r"^\[\[|\]\]$", "", wikilink.strip())
    slug_norm = slug_raw.lower().strip()

    for post in posts_index:
        if post["slug"].lower() == slug_norm:
            return post
        # Also try partial match (post slug contains the wikilink slug)
        if slug_norm in post["slug"].lower():
            return post

    return None


def score_by_tags(current_fm: dict, candidate: dict) -> int:
    """Score a candidate post by tag + category overlap with current post."""
    current_tags = set(t.lower() for t in (current_fm.get("tags", []) or []))
    current_cats = set(c.lower() for c in (current_fm.get("categories", []) or []))
    cand_tags = set(t.lower() for t in (candidate.get("tags", []) or []))
    cand_cats = set(c.lower() for c in (candidate.get("categories", []) or []))

    return len(current_tags & cand_tags) * 2 + len(current_cats & cand_cats) * 3


def score_by_keywords(current_fm: dict, candidate: dict) -> float:
    """Score by title + description keyword overlap (TF-IDF-lite)."""
    STOP_WORDS = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "it", "as", "be", "was",
        "are", "were", "this", "that", "i", "you", "we", "they", "my", "your"
    }

    def tokenize(text: str) -> Counter:
        words = re.findall(r"[a-z0-9]+", text.lower())
        return Counter(w for w in words if w not in STOP_WORDS and len(w) > 2)

    current_text = " ".join([
        str(current_fm.get("title", "") or ""),
        str(current_fm.get("description", "") or ""),
        " ".join(current_fm.get("tags", []) or []),
    ])
    cand_text = " ".join([
        str(candidate.get("title", "") or ""),
        str(candidate.get("description", "") or ""),
        " ".join(candidate.get("tags", []) or []),
    ])

    current_tokens = tokenize(current_text)
    cand_tokens = tokenize(cand_text)

    if not current_tokens or not cand_tokens:
        return 0.0

    overlap = sum((current_tokens & cand_tokens).values())
    return overlap / (len(current_tokens) ** 0.5 * len(cand_tokens) ** 0.5 + 1)


def discover_related(current_fm: dict, posts_index: list[dict], current_slug: str, count: int = 3) -> list[dict]:
    """Auto-discover related posts. Returns up to `count` entries."""
    scored = []
    for post in posts_index:
        if post["slug"] == current_slug:
            continue  # Skip self
        tag_score = score_by_tags(current_fm, post)
        kw_score = score_by_keywords(current_fm, post)
        total = tag_score * 10 + kw_score  # Tag overlap weighted higher
        scored.append((total, post))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for total, p in scored[:count] if total > 0]


def render_related_module(links: list[dict]) -> str:
    """Render a 'Related reading' HTML module from a list of {url, title, anchor_text} dicts."""
    items = ""
    for link in links:
        title = html_module.escape(link.get("title", ""))
        anchor = html_module.escape(link.get("anchor_text", title))
        url = link.get("url", "#")
        items += f'  <li><a href="{url}" class="bs-related__link">{anchor}</a></li>\n'

    return (
        '<div class="bs-related-reading">\n'
        '  <h4 class="bs-related__heading">Related reading</h4>\n'
        '  <ul class="bs-related__list">\n'
        f"{items}"
        '  </ul>\n'
        '</div>'
    )


def process(post_path: Path, posts_dir: Path, site_url: str, language: str = "en") -> int:
    parsed = parse_file(post_path, filter_type="related")
    related_blocks = parsed["blocks"]["related"]

    if not related_blocks:
        print(f"INFO: no bsgen:related blocks found in {post_path}", file=sys.stderr)
        return 0

    current_fm = parsed["frontmatter"]
    current_slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", post_path.stem)

    posts_index = load_posts_index(posts_dir, site_url, language)
    print(f"INFO: loaded {len(posts_index)} published posts from {posts_dir}", file=sys.stderr)

    content = post_path.read_text(encoding="utf-8")
    had_dangling = False

    for block in related_blocks:
        if block["validation_errors"]:
            for err in block["validation_errors"]:
                print(f"SKIP related #{block['index']}: {err}", file=sys.stderr)
            continue

        data = block["data"]
        anchors = data.get("anchors", [])
        placement = data.get("placement", "related_reading_module")
        resolved_links = []

        # Step 1: resolve explicit wikilinks
        for anchor in anchors:
            wikilink = anchor.get("wikilink", "")
            anchor_text = anchor.get("anchor_text", "")

            resolved = resolve_wikilink(wikilink, posts_index)
            if resolved:
                resolved_links.append({
                    "url": resolved["url"],
                    "title": resolved["title"],
                    "anchor_text": anchor_text or resolved["title"],
                })
                print(f"OK: resolved {wikilink} → {resolved['url']}", file=sys.stderr)
            else:
                print(f"WARNING: dangling wikilink {wikilink} — will use auto-discovery to fill gap", file=sys.stderr)
                had_dangling = True

        # Step 2: auto-discover to fill up to MAX_RELATED
        needed = MAX_RELATED - len(resolved_links)
        if needed > 0:
            # Exclude already-resolved URLs from auto-discovery results
            resolved_urls = {l["url"] for l in resolved_links}
            discovered = discover_related(current_fm, posts_index, current_slug, count=needed * 2)
            for post in discovered:
                if post["url"] not in resolved_urls and len(resolved_links) < MAX_RELATED:
                    resolved_links.append({
                        "url": post["url"],
                        "title": post["title"],
                        "anchor_text": post["title"],
                    })

        # Step 3: fallback to generic if still empty
        if not resolved_links:
            site_root = site_url.rstrip("/")
            resolved_links.append({
                "url": f"{site_root}/{language}/",
                "title": "Explore more posts",
                "anchor_text": "Explore more on our blog",
            })
            print(f"INFO: no matches found, using generic explore-more link", file=sys.stderr)

        # Step 4: render and replace
        html_module_str = render_related_module(resolved_links)

        if block["raw"] in content:
            content = content.replace(block["raw"], html_module_str, 1)
            print(f"OK: replaced related #{block['index']} with {len(resolved_links)} link(s)", file=sys.stderr)
        else:
            print(f"WARNING: related #{block['index']} raw text not found in file", file=sys.stderr)

    post_path.write_text(content, encoding="utf-8")
    return 2 if had_dangling else 0


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Process bsgen:related blocks")
    parser.add_argument("post_file")
    parser.add_argument("posts_dir", help="Path to en/_posts/ directory")
    parser.add_argument("site_url", help="e.g. https://bright-softwares.com")
    parser.add_argument("--language", default="en")
    args = parser.parse_args()

    post_path = Path(args.post_file)
    posts_dir = Path(args.posts_dir)

    if not post_path.exists():
        print(f"ERROR: post file not found: {post_path}", file=sys.stderr)
        sys.exit(1)
    if not posts_dir.exists():
        print(f"WARNING: posts_dir not found: {posts_dir} — auto-discovery disabled", file=sys.stderr)
        posts_dir.mkdir(parents=True, exist_ok=True)

    exit_code = process(post_path, posts_dir, args.site_url, args.language)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
