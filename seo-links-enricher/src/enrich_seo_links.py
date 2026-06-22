#!/usr/bin/env python3
"""
SEO Links Enricher — Populates frontmatter seo.links with relevant Wikidata entities.

Reads Jekyll blog post markdown files, extracts key topics from title, tags,
categories, and silot_terms, queries the Wikidata API for relevant entities,
and updates the seo > links frontmatter field.

Usage:
    python enrich_seo_links.py --posts-dir ./_posts --dry-run
    python enrich_seo_links.py --posts-dir ./_posts --apply
    python enrich_seo_links.py --file ./_posts/2026-01-01-my-post.md --apply
"""

import argparse
import logging
import re
import sys
import time
from pathlib import Path
from typing import Optional

import requests
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
MIN_LINKS = 2
MAX_LINKS = 5
REQUEST_DELAY = 0.5


def extract_frontmatter(content: str) -> tuple[dict, str, int, int]:
    match = re.match(r"^---\n(.*?\n)---\n", content, re.DOTALL)
    if not match:
        return {}, content, -1, -1
    fm_text = match.group(1)
    fm = yaml.safe_load(fm_text) or {}
    start = 0
    end = match.end()
    return fm, content[end:], start, end


def rebuild_frontmatter(fm: dict, body: str) -> str:
    fm_text = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return f"---\n{fm_text}---\n{body}"


def extract_topics(fm: dict, body: str) -> list[str]:
    topics = []
    title = fm.get("title", "")
    if title:
        words = re.findall(r"[A-Z][a-z]+(?:\s[A-Z][a-z]+)*|[A-Z]{2,}", title)
        topics.extend(words)
        topics.append(title)

    for key in ("tags", "categories"):
        val = fm.get(key, [])
        if isinstance(val, list):
            topics.extend(val)
        elif isinstance(val, str):
            topics.extend(val.split())

    silot = fm.get("silot_terms", "")
    if isinstance(silot, str) and silot:
        topics.extend(silot.split())

    seen = set()
    unique = []
    for t in topics:
        t_clean = t.strip().lower().replace("-", " ")
        if len(t_clean) >= 3 and t_clean not in seen:
            seen.add(t_clean)
            unique.append(t_clean)
    return unique


def search_wikidata(query: str) -> Optional[str]:
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "limit": 1,
        "format": "json",
    }
    try:
        resp = requests.get(WIKIDATA_API, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("search", [])
        if results:
            qid = results[0]["id"]
            return f"https://www.wikidata.org/wiki/{qid}"
    except Exception as e:
        logger.warning("Wikidata search failed for %r: %s", query, e)
    return None


def find_relevant_links(topics: list[str], existing_links: list[str]) -> list[str]:
    existing_qids = set()
    for link in existing_links:
        m = re.search(r"Q\d+", link)
        if m:
            existing_qids.add(m.group())

    priority_queries = []
    compound_terms = [t for t in topics if " " in t or len(t) > 8]
    single_terms = [t for t in topics if t not in compound_terms]
    priority_queries = compound_terms[:10] + single_terms[:10]

    new_links = []
    for query in priority_queries:
        if len(new_links) + len(existing_links) >= MAX_LINKS:
            break
        url = search_wikidata(query)
        if url:
            m = re.search(r"Q\d+", url)
            if m and m.group() not in existing_qids:
                existing_qids.add(m.group())
                new_links.append(url)
                logger.info("  Found: %s → %s", query, url)
        time.sleep(REQUEST_DELAY)

    return new_links


def process_file(filepath: Path, dry_run: bool = True) -> bool:
    content = filepath.read_text(encoding="utf-8")
    fm, body, _, _ = extract_frontmatter(content)
    if not fm:
        logger.warning("No frontmatter in %s, skipping", filepath)
        return False

    topics = extract_topics(fm, body)
    if not topics:
        logger.info("No topics extracted from %s, skipping", filepath)
        return False

    seo = fm.get("seo", {})
    if not isinstance(seo, dict):
        seo = {}
    existing_links = seo.get("links", [])
    if not isinstance(existing_links, list):
        existing_links = [existing_links] if existing_links else []

    if len(existing_links) >= MIN_LINKS:
        all_generic = all(
            re.search(r"Q29581045|Q1662689", link) for link in existing_links
        )
        if not all_generic:
            logger.info("Already has %d relevant links: %s", len(existing_links), filepath.name)
            return False

    logger.info("Processing %s (topics: %s)", filepath.name, topics[:5])
    new_links = find_relevant_links(topics, existing_links)

    if not new_links:
        logger.info("  No new links found for %s", filepath.name)
        return False

    all_links = list(existing_links) + new_links
    all_links = all_links[:MAX_LINKS]

    if dry_run:
        logger.info("  [DRY RUN] Would set seo.links to: %s", all_links)
        return True

    seo["links"] = all_links
    fm["seo"] = seo
    new_content = rebuild_frontmatter(fm, body)
    filepath.write_text(new_content, encoding="utf-8")
    logger.info("  Updated seo.links: %s", all_links)
    return True


def main():
    parser = argparse.ArgumentParser(description="Enrich blog post seo.links with Wikidata entities")
    parser.add_argument("--posts-dir", type=str, help="Directory containing blog posts")
    parser.add_argument("--file", type=str, help="Single file to process")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without modifying files")
    args = parser.parse_args()

    dry_run = not args.apply

    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            logger.error("File not found: %s", filepath)
            sys.exit(1)
        updated = process_file(filepath, dry_run=dry_run)
        logger.info("Result: %s", "updated" if updated else "no changes")
    elif args.posts_dir:
        posts_dir = Path(args.posts_dir)
        if not posts_dir.exists():
            logger.error("Directory not found: %s", posts_dir)
            sys.exit(1)
        files = sorted(posts_dir.rglob("*.md"))
        updated_count = 0
        for f in files:
            if process_file(f, dry_run=dry_run):
                updated_count += 1
        logger.info("Processed %d files, %d %s", len(files), updated_count,
                     "would be updated" if dry_run else "updated")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
