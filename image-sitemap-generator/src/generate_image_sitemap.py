#!/usr/bin/env python3
"""
generate_image_sitemap.py — builds a Google Image Sitemap for a Jekyll site.

jekyll-sitemap (already in use on all 9 BrightSoftwares/personal blogs, see
_config.yml) generates a standard sitemap.xml — page URLs only, no image
extension. This script crawls the LIVE site's own sitemap.xml (no local
Jekyll build needed — same live-HTTP-fetch approach as
seo-index-checker/src/seo_index_checker.py, so it works identically in CI
and locally against any of the 9 repos) and produces a companion
image-sitemap.xml per Google's image sitemap extension:
https://developers.google.com/search/docs/crawling-indexing/sitemaps/image-sitemaps

For each URL in the page sitemap:
  1. Fetch the rendered HTML.
  2. Extract every <img src="..."> inside <body> (skips <head>, so favicons
     and meta preview tags are naturally excluded).
  3. Resolve relative src to absolute URLs.
  4. Skip data: URIs (inline base64 — not indexable "images" in Google's
     sense) and common non-content assets (nav/footer icon paths — see
     NON_CONTENT_PATH_HINTS) so the sitemap isn't polluted with UI chrome.
  5. Use the <img alt="..."> attribute as <image:title> when present (best
     available proxy for a caption — this script does not attempt to infer
     captions from surrounding <figcaption> markup).
  6. Emit one <url><image:image>... block per page, capped at
     MAX_IMAGES_PER_URL (Google's documented per-URL limit is 1,000).

Caps MAX_URLS_PER_SITEMAP (Google's documented limit is 50,000 <url> entries
per sitemap file) by truncating and printing a warning — none of the 9 sites
are anywhere near this today, but the check exists so an operator sees a
warning instead of silently uploading a truncated sitemap to Search Console.

Usage:
  python3 generate_image_sitemap.py --site-url https://bright-softwares.com
  python3 generate_image_sitemap.py --site-url https://bright-softwares.com \\
      --sitemap-path /sitemap.xml --output image-sitemap.xml --limit 50

Output: an XML file at --output (default: image-sitemap.xml) plus a summary
line on stderr. Does NOT modify robots.txt or _config.yml — submitting the
generated file to Search Console / referencing it from robots.txt is a
one-time manual step (see the reusable workflow's PR description).
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree
from xml.sax.saxutils import escape as xml_escape

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    sys.exit("Missing dependency: pip install requests")

MAX_IMAGES_PER_URL = 1000
MAX_URLS_PER_SITEMAP = 50000

# Path fragments that identify UI chrome rather than content images. Matched
# case-insensitively against the resolved image URL's path. Deliberately
# narrow (a false-negative just means one extra harmless <image:image>
# entry; a false-positive would silently drop a real content image).
NON_CONTENT_PATH_HINTS = (
    "/favicon",
    "/apple-touch-icon",
    "/assets/icons/",
    "/assets/images/logo",
    "/assets/images/nav",
)

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
SRC_ATTR_RE = re.compile(r'src=["\']([^"\']+)["\']', re.IGNORECASE)
ALT_ATTR_RE = re.compile(r'alt=["\']([^"\']*)["\']', re.IGNORECASE)
BODY_RE = re.compile(r"<body\b[^>]*>(.*)</body>", re.IGNORECASE | re.DOTALL)


@dataclass
class PageImages:
    url: str
    images: list[tuple[str, str]] = field(default_factory=list)  # (abs_url, title)


def _make_session(user_agent: str) -> "requests.Session":
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers["User-Agent"] = user_agent
    return session


def _collect_sitemap(url: str, session: "requests.Session", out: list[str], depth: int) -> None:
    if depth > 3:
        return
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as exc:
        print(f"  [WARN] Cannot fetch sitemap {url}: {exc}", file=sys.stderr)
        return

    try:
        root = ElementTree.fromstring(resp.content)
    except ElementTree.ParseError as exc:
        print(f"  [WARN] Cannot parse sitemap XML at {url}: {exc}", file=sys.stderr)
        return

    for sitemap in root.findall("sm:sitemap/sm:loc", SITEMAP_NS):
        _collect_sitemap(sitemap.text.strip(), session, out, depth + 1)
    for loc in root.findall("sm:url/sm:loc", SITEMAP_NS):
        out.append(loc.text.strip())


def fetch_sitemap_urls(site_url: str, sitemap_path: str, session: "requests.Session") -> list[str]:
    """Return all <loc> URLs from the page sitemap (handles sitemap index recursively)."""
    sitemap_url = urljoin(site_url.rstrip("/") + "/", sitemap_path.lstrip("/"))
    urls: list[str] = []
    _collect_sitemap(sitemap_url, session, urls, depth=0)
    return urls


def is_content_image(abs_url: str) -> bool:
    """Filter out data: URIs and known UI-chrome paths (see NON_CONTENT_PATH_HINTS)."""
    if abs_url.startswith("data:"):
        return False
    path = urlparse(abs_url).path.lower()
    return not any(hint in path for hint in NON_CONTENT_PATH_HINTS)


def extract_images(html: str, page_url: str) -> list[tuple[str, str]]:
    """Return deduped (absolute_url, title) pairs for every content <img> in <body>."""
    body_match = BODY_RE.search(html)
    body_html = body_match.group(1) if body_match else html

    seen: dict[str, str] = {}
    for tag in IMG_TAG_RE.findall(body_html):
        src_match = SRC_ATTR_RE.search(tag)
        if not src_match:
            continue
        raw_src = src_match.group(1).strip()
        if not raw_src:
            continue
        abs_url = urljoin(page_url, raw_src)
        if not is_content_image(abs_url):
            continue
        if abs_url in seen:
            continue
        alt_match = ALT_ATTR_RE.search(tag)
        title = alt_match.group(1).strip() if alt_match else ""
        seen[abs_url] = title

    return list(seen.items())[:MAX_IMAGES_PER_URL]


def crawl(
    site_url: str,
    sitemap_path: str,
    session: "requests.Session",
    limit: int,
    delay: float,
) -> list[PageImages]:
    urls = fetch_sitemap_urls(site_url, sitemap_path, session)
    if not urls:
        print(f"[WARN] No URLs found in {sitemap_path} at {site_url}", file=sys.stderr)
        return []

    if len(urls) > MAX_URLS_PER_SITEMAP:
        print(
            f"[WARN] Sitemap has {len(urls)} URLs, exceeding Google's "
            f"{MAX_URLS_PER_SITEMAP}-URL-per-sitemap limit — truncating. "
            "Split into multiple image sitemaps + a sitemap index if this "
            "site grows past this size.",
            file=sys.stderr,
        )
        urls = urls[:MAX_URLS_PER_SITEMAP]

    if limit:
        urls = urls[:limit]

    pages: list[PageImages] = []
    for i, url in enumerate(urls, 1):
        time.sleep(delay)
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as exc:
            print(f"  [WARN] Skipping {url}: {exc}", file=sys.stderr)
            continue

        images = extract_images(resp.text, url)
        if images:
            pages.append(PageImages(url=url, images=images))
        print(f"  [{i}/{len(urls)}] {url} -> {len(images)} image(s)", file=sys.stderr)

    return pages


def render_image_sitemap_xml(pages: list[PageImages]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    for page in pages:
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(page.url)}</loc>")
        for img_url, title in page.images:
            lines.append("    <image:image>")
            lines.append(f"      <image:loc>{xml_escape(img_url)}</image:loc>")
            if title:
                lines.append(f"      <image:title>{xml_escape(title)}</image:title>")
            lines.append("    </image:image>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--site-url", required=True, help="Base URL, e.g. https://bright-softwares.com")
    parser.add_argument("--sitemap-path", default="/sitemap.xml")
    parser.add_argument("--output", default="image-sitemap.xml")
    parser.add_argument("--limit", type=int, default=0, help="Process at most N sitemap URLs (0 = no limit)")
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds between page fetches")
    parser.add_argument(
        "--user-agent",
        default="Mozilla/5.0 (compatible; ImageSitemapGenerator/1.0; +https://bright-softwares.com)",
    )
    args = parser.parse_args()

    session = _make_session(args.user_agent)
    pages = crawl(args.site_url, args.sitemap_path, session, args.limit, args.delay)

    total_images = sum(len(p.images) for p in pages)
    print(
        f"Found {total_images} content image(s) across {len(pages)} page(s) "
        f"with at least one image.",
        file=sys.stderr,
    )

    xml_content = render_image_sitemap_xml(pages)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(xml_content, encoding="utf-8")
    print(f"Wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
