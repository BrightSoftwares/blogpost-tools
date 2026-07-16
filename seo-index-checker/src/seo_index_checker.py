#!/usr/bin/env python3
"""
SEO Indexing Checker — detects why blog pages may not be indexed.

For each URL found in a site's sitemap.xml this script checks:
  1. HTTP status code (4xx/5xx -> inaccessible)
  2. <meta name="robots" content="noindex"> -> explicitly excluded
  3. <link rel="canonical"> mismatch -> Google prefers the canonical URL
  4. robots.txt disallow -> blocked from crawling
  5. Redirect chain -> if URL redirects elsewhere (not the canonical)

Output: a markdown report + JSON manifest so CI can track changes over time.

Usage:
  python3 seo_index_checker.py --site-url https://bright-softwares.com
  python3 seo_index_checker.py --site-url https://bright-softwares.com \\
      --sitemap-path /sitemap.xml --output _seo_reports/seo_index_2026-07-16.md

Ported from my-obsidian task_executor/tools/seo_index_checker.py (SP3.4 task 4) to run
as a reusable GitHub Actions workflow so every blog repo can schedule it.
"""

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    sys.exit("Missing dependency: pip install requests")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class UrlResult:
    url: str
    http_status: int | None
    final_url: str | None
    redirected: bool
    has_noindex: bool
    canonical: str | None
    canonical_mismatch: bool
    robots_blocked: bool
    likely_indexed: bool
    reasons: list[str]


# ---------------------------------------------------------------------------
# HTTP session with retry
# ---------------------------------------------------------------------------

def _make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers["User-Agent"] = (
        "Mozilla/5.0 (compatible; SEOIndexChecker/1.0; +https://bright-softwares.com)"
    )
    return session


# ---------------------------------------------------------------------------
# Sitemap parsing
# ---------------------------------------------------------------------------

def fetch_sitemap_urls(site_url: str, sitemap_path: str, session: requests.Session) -> list[str]:
    """Return all <loc> URLs from the sitemap (handles sitemap index recursively)."""
    sitemap_url = urljoin(site_url.rstrip("/") + "/", sitemap_path.lstrip("/"))
    urls: list[str] = []
    _collect_sitemap(sitemap_url, session, urls, depth=0)
    return urls


def _collect_sitemap(url: str, session: requests.Session, out: list[str], depth: int) -> None:
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

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    # Sitemap index -> recurse
    for sitemap in root.findall("sm:sitemap/sm:loc", ns):
        _collect_sitemap(sitemap.text.strip(), session, out, depth + 1)
    # URL set
    for loc in root.findall("sm:url/sm:loc", ns):
        out.append(loc.text.strip())


# ---------------------------------------------------------------------------
# robots.txt
# ---------------------------------------------------------------------------

def build_robots_parser(site_url: str, session: requests.Session) -> RobotFileParser:
    robots_url = urljoin(site_url.rstrip("/") + "/", "robots.txt")
    rp = RobotFileParser(robots_url)
    try:
        resp = session.get(robots_url, timeout=10)
        rp.parse(resp.text.splitlines())
    except Exception:
        pass
    return rp


# ---------------------------------------------------------------------------
# Per-URL analysis
# ---------------------------------------------------------------------------

def _extract_meta_robots(html: str) -> str:
    """Return content of <meta name="robots"> (lowercased) or empty string."""
    pattern = r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)["\']'
    m = re.search(pattern, html, re.IGNORECASE)
    if m:
        return m.group(1).lower()
    # Also try reversed attribute order
    pattern2 = r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']robots["\']'
    m2 = re.search(pattern2, html, re.IGNORECASE)
    return m2.group(1).lower() if m2 else ""


def _extract_canonical(html: str) -> str | None:
    """Return href of <link rel="canonical"> or None."""
    pattern = r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']'
    m = re.search(pattern, html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    pattern2 = r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']'
    m2 = re.search(pattern2, html, re.IGNORECASE)
    return m2.group(1).strip() if m2 else None


def analyze_url(
    url: str,
    session: requests.Session,
    robots_parser: RobotFileParser,
    delay: float = 0.5,
) -> UrlResult:
    time.sleep(delay)

    reasons: list[str] = []
    http_status = None
    final_url = None
    redirected = False
    has_noindex = False
    canonical = None
    canonical_mismatch = False
    robots_blocked = False

    # 1. robots.txt
    if not robots_parser.can_fetch("*", url):
        robots_blocked = True
        reasons.append("robots.txt disallows this URL")

    # 2. HTTP fetch
    try:
        resp = session.get(url, timeout=15, allow_redirects=True)
        http_status = resp.status_code
        final_url = resp.url
        redirected = final_url.rstrip("/") != url.rstrip("/")

        if http_status >= 400:
            reasons.append(f"HTTP {http_status} — page not accessible")
        elif redirected:
            reasons.append(f"Redirects to {final_url} — Google indexes the destination, not this URL")

        # 3. Parse HTML for noindex and canonical
        if http_status and http_status < 400:
            html = resp.text
            meta_robots = _extract_meta_robots(html)
            if "noindex" in meta_robots:
                has_noindex = True
                reasons.append(f"<meta name='robots' content='{meta_robots}'> — noindex directive")

            canonical = _extract_canonical(html)
            if canonical:
                norm_url = url.rstrip("/")
                norm_canon = canonical.rstrip("/")
                if norm_url != norm_canon and not canonical.startswith(url):
                    canonical_mismatch = True
                    reasons.append(
                        f"Canonical points to {canonical} — Google will index canonical, not this URL"
                    )

    except requests.exceptions.ConnectionError:
        reasons.append("Connection error — domain/host unreachable")
    except requests.exceptions.Timeout:
        reasons.append("Request timed out")
    except Exception as exc:
        reasons.append(f"Fetch error: {exc}")

    likely_indexed = (
        not robots_blocked
        and (http_status is not None and http_status < 300)
        and not has_noindex
        and not canonical_mismatch
        and not redirected
    )

    return UrlResult(
        url=url,
        http_status=http_status,
        final_url=final_url,
        redirected=redirected,
        has_noindex=has_noindex,
        canonical=canonical,
        canonical_mismatch=canonical_mismatch,
        robots_blocked=robots_blocked,
        likely_indexed=likely_indexed,
        reasons=reasons,
    )


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    site_url: str,
    results: list[UrlResult],
    report_date: str,
) -> str:
    indexed = [r for r in results if r.likely_indexed]
    issues = [r for r in results if not r.likely_indexed]

    lines = [
        f"# SEO Indexing Checker Report — {report_date}",
        "",
        f"**Site:** {site_url}",
        f"**Generated:** {report_date}",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total URLs in sitemap | {len(results)} |",
        f"| Likely indexed | {len(indexed)} |",
        f"| Likely NOT indexed (issues found) | {len(issues)} |",
        "",
        "## URLs with Indexing Issues",
        "",
    ]

    if not issues:
        lines.append("No issues found — all URLs appear likely to be indexed.")
    else:
        for r in issues:
            lines.append(f"### `{r.url}`")
            lines.append("")
            lines.append(f"- **HTTP status:** {r.http_status}")
            if r.final_url and r.redirected:
                lines.append(f"- **Redirects to:** {r.final_url}")
            if r.canonical:
                lines.append(f"- **Canonical:** {r.canonical}")
            lines.append("- **Issues:**")
            for reason in r.reasons:
                lines.append(f"  - {reason}")
            lines.append("")

    lines += [
        "## Likely Indexed URLs (first 30)",
        "",
    ]
    for r in indexed[:30]:
        lines.append(f"- {r.url}")

    lines += [
        "",
        "## Next Steps",
        "",
        "For each issue above, consider:",
        "- **HTTP 4xx**: Fix the broken page or add a redirect",
        "- **noindex**: Remove the directive if the page should be indexed",
        "- **Canonical mismatch**: Update the canonical tag or consolidate to one URL",
        "- **robots.txt block**: Update robots.txt to allow the URL",
        "- **Redirect**: Update internal links to point to the final URL directly",
        "",
        "> Auto-fix is out of scope for this checker (requires human judgment per issue).",
    ]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="SEO Indexing Checker")
    parser.add_argument("--site-url", required=True, help="Base URL of the site")
    parser.add_argument("--sitemap-path", default="/sitemap.xml", help="Sitemap path (default: /sitemap.xml)")
    parser.add_argument("--output-dir", default="_seo_reports", help="Directory to write the report + manifest (default: _seo_reports)")
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds to wait between requests (default: 0.5)")
    parser.add_argument("--limit", type=int, default=None, help="Process at most N URLs (for testing)")
    args = parser.parse_args()

    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_dir = Path(args.output_dir)
    output_path = output_dir / f"seo_index_{report_date}.md"
    manifest_path = output_dir / "seo_index_manifest.json"

    session = _make_session()
    robots_parser = build_robots_parser(args.site_url, session)

    print(f"Fetching sitemap: {args.site_url}{args.sitemap_path}")
    urls = fetch_sitemap_urls(args.site_url, args.sitemap_path, session)
    if args.limit:
        urls = urls[:args.limit]
    print(f"Found {len(urls)} URLs. Analyzing…")

    results: list[UrlResult] = []
    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] {url}", end="\r")
        results.append(analyze_url(url, session, robots_parser, delay=args.delay))

    print()
    indexed_count = sum(1 for r in results if r.likely_indexed)
    issues_count = len(results) - indexed_count
    print(f"Done. Likely indexed: {indexed_count} | Issues: {issues_count}")

    report = generate_report(args.site_url, results, report_date)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Report: {output_path}")

    manifest = {"runs": []}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    manifest["runs"].append({
        "date": report_date,
        "site_url": args.site_url,
        "total": len(results),
        "likely_indexed": indexed_count,
        "issues": issues_count,
        "report": str(output_path),
    })
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
