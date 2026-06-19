#!/usr/bin/env python3
"""
seo_links_populator.py — Populate seo.links frontmatter with relevant Wikidata entities.

Reads Jekyll blog posts, extracts key topics from title/tags/categories/silot_terms,
queries the Wikidata search API for matching entities, and writes 2+ relevant
Wikidata entity URLs into the post's `seo > links` frontmatter.

Usage:
    python seo_links_populator.py --dir en/_posts/
    python seo_links_populator.py --dir en/_drafts/400_refined_content/ --min-links 3
    python seo_links_populator.py --file en/_posts/2026-01-01-my-post.md --dry-run
    python seo_links_populator.py --dir en/_posts/ --force  # overwrite existing links
"""

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path


WIKIDATA_SEARCH_URL = "https://www.wikidata.org/w/api.php"
WIKIDATA_ENTITY_URL = "https://www.wikidata.org/wiki/{qid}"

FM_SEPARATOR = "---"

KEYWORD_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "through", "during",
    "before", "after", "above", "below", "between", "how", "what", "why",
    "when", "where", "which", "who", "whom", "this", "that", "these", "those",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "shall", "can", "it", "its", "i", "my", "your", "our", "we", "you",
    "they", "their", "them", "he", "she", "me", "us", "not", "no", "nor",
    "so", "if", "then", "than", "too", "very", "just", "also", "each",
    "every", "all", "both", "few", "more", "most", "other", "some", "such",
    "only", "own", "same", "here", "there", "once", "en", "de", "le", "la",
    "les", "un", "une", "des", "du", "et", "ou", "comment", "que", "qui",
    "ce", "est", "pour", "par", "sur", "dans", "avec", "sans", "plus",
    "use", "using", "used", "make", "get", "set",
}

COMPOUND_KEYWORDS = {
    "home assistant": "Q56283647",
    "docker compose": "Q108803380",
    "google workspace": "Q1540037",
    "machine learning": "Q2539",
    "deep learning": "Q197536",
    "artificial intelligence": "Q11660",
    "natural language processing": "Q30642",
    "cloud computing": "Q483639",
    "open source": "Q39162",
    "continuous integration": "Q965769",
    "continuous deployment": "Q126774744",
    "version control": "Q252303",
    "api gateway": "Q56401018",
    "load balancing": "Q1502954",
    "port forwarding": "Q278835",
    "system administration": "Q189062",
    "software development": "Q638608",
    "web application": "Q189210",
    "data analytics": "Q29661084",
    "image generation": "Q11060274",
}

SINGLE_KEYWORDS = {
    "docker": "Q15206305",
    "kubernetes": "Q22661306",
    "terraform": "Q60345827",
    "ansible": "Q2852503",
    "python": "Q28865",
    "javascript": "Q2005",
    "typescript": "Q978185",
    "nodejs": "Q756100",
    "react": "Q19399674",
    "postgresql": "Q192490",
    "mysql": "Q850",
    "redis": "Q2136322",
    "nginx": "Q306144",
    "linux": "Q388",
    "ubuntu": "Q381",
    "debian": "Q7715973",
    "git": "Q186055",
    "github": "Q364",
    "gitlab": "Q16639197",
    "jenkins": "Q7491312",
    "grafana": "Q22674461",
    "prometheus": "Q107917532",
    "elasticsearch": "Q3050461",
    "wordpress": "Q13166",
    "jekyll": "Q16143023",
    "gmail": "Q9334",
    "oauth": "Q384398",
    "rest": "Q749568",
    "graphql": "Q21081869",
    "json": "Q2063",
    "yaml": "Q281876",
    "markdown": "Q1193600",
    "css": "Q46441",
    "html": "Q8811",
    "wifi": "Q29642",
    "zigbee": "Q272443",
    "mqtt": "Q1163132",
    "bluetooth": "Q42490",
    "raspberry": "Q7295292",
    "arduino": "Q2225227",
    "openwrt": "Q1464818",
    "minecraft": "Q49740",
    "flutter": "Q56343037",
    "swift": "Q17118377",
    "ruby": "Q161053",
    "golang": "Q37227",
    "rust": "Q575650",
    "java": "Q251",
    "php": "Q59",
    "laravel": "Q6489078",
    "django": "Q185667",
    "flask": "Q3437977",
    "mongodb": "Q1165204",
    "cloudflare": "Q5134633",
    "stripe": "Q7624164",
    "aws": "Q456157",
    "azure": "Q725967",
    "gcp": "Q39801",
    "heroku": "Q1614215",
    "vercel": "Q109292685",
    "netlify": "Q110879059",
    "supabase": "Q98398498",
    "firebase": "Q5765488",
    "tailwind": "Q67828564",
    "bootstrap": "Q28706088",
    "fastapi": "Q113008953",
    "celery": "Q5058173",
    "cloudinary": "Q75419091",
    "minikube": "Q96445818",
    "helm": "Q56443371",
    "istio": "Q98381014",
    "vault": "Q69834939",
    "consul": "Q69834987",
    "apache": "Q11354",
    "tomcat": "Q507430",
    "maven": "Q139894",
    "gradle": "Q4039686",
    "npm": "Q7067518",
    "webpack": "Q56283539",
    "vite": "Q110878961",
    "drone": "Q230853",
    "dji": "Q1153603",
    "pilotflow": "Q1540037",
    "notiwise": "Q1540037",
    "seo": "Q180711",
    "devops": "Q17076988",
    "devsecops": "Q61793085",
    "microservices": "Q18344606",
    "serverless": "Q52638723",
    "chatgpt": "Q115317126",
    "openai": "Q21707860",
    "llm": "Q15711698",
    "blockchain": "Q20514253",
    "cryptocurrency": "Q13479982",
    "vpn": "Q160590",
    "dns": "Q8767",
    "ssl": "Q466704",
    "encryption": "Q141090",
    "authentication": "Q204756",
    "authorization": "Q4824619",
    "caching": "Q23762",
    "indexing": "Q1130645",
    "monitoring": "Q1137655",
    "logging": "Q1775371",
    "testing": "Q131252",
    "debugging": "Q189053",
    "refactoring": "Q1099908",
    "agile": "Q326116",
    "scrum": "Q724344",
    "kanban": "Q134861",
}


def parse_frontmatter(content: str) -> tuple[dict | None, str, str]:
    """Return (frontmatter_dict, raw_frontmatter, body) or (None, '', content)."""
    if not content.startswith("---"):
        return None, "", content

    second = content.index("---", 3)
    raw_fm = content[3:second].strip()
    body = content[second + 3:]

    fm: dict = {}
    current_key = ""
    current_list: list | None = None

    for line in raw_fm.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("- ") and current_list is not None:
            current_list.append(stripped[2:].strip())
            continue

        if current_list is not None:
            fm[current_key] = current_list
            current_list = None

        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            current_key = key
            if val == "":
                current_list = []
            elif val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
            else:
                fm[key] = val.strip("'\"")

    if current_list is not None:
        fm[current_key] = current_list

    return fm, raw_fm, body


def extract_topics(fm: dict, body: str) -> list[str]:
    """Extract candidate topic keywords from frontmatter and body."""
    topics: list[str] = []

    title = fm.get("title", "")
    if title:
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]+", title.lower())
        topics.extend(w for w in words if w not in KEYWORD_STOPWORDS and len(w) > 2)

    for field in ("tags", "categories"):
        vals = fm.get(field, [])
        if isinstance(vals, str):
            vals = [v.strip() for v in vals.split(",")]
        for v in vals:
            clean = v.strip().lower().replace("-", " ")
            if clean and clean not in KEYWORD_STOPWORDS:
                topics.append(clean)

    silot = fm.get("silot_terms", "")
    if isinstance(silot, str) and silot:
        for term in silot.split():
            t = term.strip().lower()
            if t not in KEYWORD_STOPWORDS and len(t) > 2:
                topics.append(t)

    seen = set()
    unique = []
    for t in topics:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


def search_wikidata(query: str, limit: int = 3) -> list[dict]:
    """Search Wikidata for entities matching query. Returns list of {qid, label, description}."""
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "format": "json",
        "limit": str(limit),
        "type": "item",
    }
    url = WIKIDATA_SEARCH_URL + "?" + "&".join(f"{k}={urllib.request.quote(v)}" for k, v in params.items())

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BlogSEOLinksBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        results = []
        for item in data.get("search", []):
            results.append({
                "qid": item["id"],
                "label": item.get("label", ""),
                "description": item.get("description", ""),
            })
        return results
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return []


def find_best_entities(topics: list[str], min_links: int = 2, max_links: int = 5) -> list[str]:
    """Find the best Wikidata entities for the given topics."""
    entities: list[tuple[str, str, float]] = []
    seen_qids: set[str] = set()

    title_lower = " ".join(topics[:6]).lower()
    for compound, qid in COMPOUND_KEYWORDS.items():
        if compound in title_lower:
            if qid not in seen_qids:
                entities.append((qid, compound, 10.0))
                seen_qids.add(qid)

    for i, topic in enumerate(topics):
        topic_lower = topic.lower().replace("-", "").replace(" ", "")
        for kw, qid in SINGLE_KEYWORDS.items():
            if qid in seen_qids:
                continue
            kw_norm = kw.lower().replace("-", "").replace(" ", "")
            if topic_lower == kw_norm or kw_norm in topic_lower or topic_lower in kw_norm:
                score = 8.0 - (i * 0.3)
                entities.append((qid, kw, score))
                seen_qids.add(qid)
                break

    for i, topic in enumerate(topics):
        if len(entities) >= max_links:
            break

        results = search_wikidata(topic, limit=2)
        time.sleep(0.2)

        for result in results:
            qid = result["qid"]
            if qid in seen_qids:
                continue
            seen_qids.add(qid)

            score = 5.0 - (i * 0.5)
            label = result["label"].lower()
            desc = (result.get("description") or "").lower()

            if topic.lower() == label:
                score += 3.0
            elif topic.lower() in label:
                score += 1.5

            skip_descriptions = ["wikimedia", "disambiguation", "category", "template"]
            if any(s in desc for s in skip_descriptions):
                continue

            entities.append((qid, result["label"], score))

    entities.sort(key=lambda x: -x[2])
    selected = entities[:max_links]

    if len(selected) < min_links:
        return [WIKIDATA_ENTITY_URL.format(qid=qid) for qid, _, _ in selected]

    return [WIKIDATA_ENTITY_URL.format(qid=qid) for qid, _, _ in selected[:max(min_links, len(selected))]]


def update_seo_links(content: str, links: list[str]) -> str:
    """Update or insert seo.links in the post's frontmatter."""
    if not content.startswith("---"):
        links_yaml = "\n".join(f"  - {link}" for link in links)
        return f"---\nseo:\n  links:\n{links_yaml}\n---\n\n{content}"

    second = content.index("---", 3)
    fm_text = content[3:second]
    body = content[second + 3:]

    links_yaml = "\n".join(f"  - {link}" for link in links)

    seo_pattern = re.compile(
        r"^seo:\s*\n(?:\s+links:\s*\n(?:\s+-\s+.*\n)*|\s+.*\n)*",
        re.MULTILINE,
    )
    match = seo_pattern.search(fm_text)
    if match:
        new_seo = f"seo:\n  links:\n{links_yaml}\n"
        fm_text = fm_text[:match.start()] + new_seo + fm_text[match.end():]
    else:
        fm_text = fm_text.rstrip("\n") + f"\nseo:\n  links:\n{links_yaml}\n"

    return f"---\n{fm_text}---{body}"


def process_file(
    file_path: Path,
    min_links: int = 2,
    max_links: int = 5,
    force: bool = False,
    dry_run: bool = False,
) -> bool:
    """Process a single file. Returns True if changes were made."""
    content = file_path.read_text(encoding="utf-8")
    fm, raw_fm, body = parse_frontmatter(content)

    if fm is None:
        print(f"SKIP {file_path}: no frontmatter")
        return False

    existing_seo = fm.get("seo", {})
    if isinstance(existing_seo, dict):
        existing_links = existing_seo.get("links", [])
    else:
        existing_links = []

    if existing_links and not force:
        print(f"SKIP {file_path}: already has {len(existing_links)} seo links (use --force to overwrite)")
        return False

    topics = extract_topics(fm, body)
    if not topics:
        print(f"SKIP {file_path}: no topics extracted")
        return False

    print(f"SCAN {file_path}: topics={topics[:8]}")
    links = find_best_entities(topics, min_links=min_links, max_links=max_links)

    if not links:
        print(f"SKIP {file_path}: no Wikidata entities found")
        return False

    if dry_run:
        print(f"[DRY RUN] {file_path}: would set seo.links to:")
        for link in links:
            print(f"  - {link}")
        return True

    updated = update_seo_links(content, links)
    file_path.write_text(updated, encoding="utf-8")
    print(f"UPDATED {file_path}: {len(links)} seo links")
    for link in links:
        print(f"  - {link}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Populate seo.links with relevant Wikidata entities.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dir", help="Directory of Jekyll posts to process")
    group.add_argument("--file", help="Single file to process")
    parser.add_argument("--min-links", type=int, default=2, help="Minimum links per post (default: 2)")
    parser.add_argument("--max-links", type=int, default=4, help="Maximum links per post (default: 4)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing seo.links")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    parser.add_argument("--glob", default="*.md", help="File glob pattern (default: *.md)")
    args = parser.parse_args()

    changed = 0
    total = 0

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            return 2
        total = 1
        if process_file(path, args.min_links, args.max_links, args.force, args.dry_run):
            changed = 1
    else:
        dir_path = Path(args.dir)
        if not dir_path.is_dir():
            print(f"ERROR: Directory not found: {dir_path}", file=sys.stderr)
            return 2
        files = sorted(dir_path.glob(args.glob))
        total = len(files)
        for f in files:
            if process_file(f, args.min_links, args.max_links, args.force, args.dry_run):
                changed += 1

    print(f"\nDone: {changed}/{total} files updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
