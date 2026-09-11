#!/usr/bin/env python3
"""
seo_links_populator.py — Populate seo.links frontmatter with relevant Wikidata entities.

Reads Jekyll blog posts, extracts key topics from title/tags/categories/silot_terms,
queries the Wikidata search API for matching entities, and writes relevant
Wikidata entity URLs into the post's `seo > links` frontmatter.

Two modes:

    populate  (default)  — write seo.links into posts that don't have them
    audit     (--audit-csv) — resolve every QID already present in every post's
                              seo.links and flag the ones that look unrelated to
                              that post's own tags/categories/silot_terms/title

Usage:
    python seo_links_populator.py --dir en/_posts/
    python seo_links_populator.py --dir en/_drafts/400_refined_content/ --min-links 3
    python seo_links_populator.py --file en/_posts/2026-01-01-my-post.md --dry-run
    python seo_links_populator.py --dir en/_posts/ --force  # recompute existing links

    # standalone drift audit across a whole site (no writes):
    python seo_links_populator.py --audit-csv seo-links-audit.csv \
        --dir en/_posts --dir en/_drafts/400_refined_content

    # repair only the links the audit flags as irrelevant, keep the good ones:
    python seo_links_populator.py --dir en/_posts --replace-irrelevant

-------------------------------------------------------------------------------
2026-09-11 defect fixes (root cause of the garbage QIDs on
`2026-11-09-we-built-a-crm-feature-on-ourselves-first-...md`, written by the
scheduled `seo-links-populate.yml` run of 2026-09-07, commit 65b679a in
BrightSoftwares/corporate-website):

  D1  The "already has links, use --force" guard never fired. `seo.links` is a
      NESTED mapping, and `parse_frontmatter_yaml_lite()` is a flat parser: it
      returns `{"seo": [], "links": [...]}`, so `fm["seo"]` was an empty list,
      `existing_links` was always `[]`, and every weekly scheduled run silently
      recomputed (and overwrote) every post's links with force=false.
      Fixed by `extract_existing_seo_links()`, which reads the nested block out
      of the raw frontmatter text.

  D2  `extract_topics()` treated every non-stopword title word >2 chars as a
      topic, so "built", "ourselves", "found", "two", "demo", "first" became
      Wikidata queries. "ourselves" is how Q7478101 — the English pronoun
      "we" — ended up in an article about CRM dogfooding.
      Fixed by GENERIC_CONTENT_WORDS + by tracking each topic's provenance
      (curated frontmatter field vs. scraped from the title) and holding
      title-derived topics to a higher bar.

  D3  `find_best_entities()` appended EVERY search hit and scored it by the
      topic's *index in the list*, not by whether the entity had anything to do
      with the topic. Nothing was ever rejected for irrelevance; the only filter
      was four substrings in the description.
      Fixed by `label_match_kind()` (an entity is only accepted if its label
      actually matches the query — exact, all-words, or acronym-of-initials),
      `entity_is_non_topical()` (pronouns, given names, surnames, villages,
      films, songs, taxa, humans, ... are rejected outright) and MIN_ACCEPT_SCORE.

  D4  `update_seo_links()`'s regex replaced the whole `seo:` block, destroying
      any sibling key under it. Now only the `links:` list is rewritten.

  D5  The dictionary lookup matched on SUBSTRINGS (`kw_norm in topic_lower or
      topic_lower in kw_norm`), so the topic "java" resolved to JavaScript's
      QID and "rest" to anything containing "rest". Now exact-match only.

  D6  SINGLE_KEYWORDS mapped both "pilotflow" and "notiwise" to Q1540037
      (Google Workspace). Removed — no link beats a wrong link.

  D7  The min_links branch was a no-op that padded results with whatever scored
      highest, however bad. Now: write only what passes the gates; if that is
      fewer than min_links, log it and write the smaller set; if it is zero,
      leave the post alone.
-------------------------------------------------------------------------------
"""

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from frontmatter_utils import parse_frontmatter_yaml_lite as parse_frontmatter  # noqa: E402


WIKIDATA_SEARCH_URL = "https://www.wikidata.org/w/api.php"
WIKIDATA_ENTITY_URL = "https://www.wikidata.org/wiki/{qid}"
USER_AGENT = "BlogSEOLinksBot/2.0 (https://bright-softwares.com; blogpost-tools)"

FM_SEPARATOR = "---"

# An entity has to clear this to be written into a post at all (D3/D7).
MIN_ACCEPT_SCORE = 3.0

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

# D2. Words that are perfectly ordinary English but are never a *topic*.
# Blog titles are full of them, and Wikidata happily returns an item for each
# one (pronouns, numbers, dictionary entries), which is exactly how
# "ourselves" became a link to the pronoun "we" (Q7478101).
GENERIC_CONTENT_WORDS = {
    # pronouns / self-reference that survive the stopword list
    "ourselves", "myself", "yourself", "yourselves", "himself", "herself",
    "itself", "themselves", "everyone", "everybody", "someone", "somebody",
    "anyone", "anybody", "nobody", "everything", "something", "anything",
    "nothing",
    # generic verbs
    "built", "build", "building", "rebuilt", "found", "finding", "made",
    "making", "shipped", "shipping", "ship", "wrote", "writing", "written",
    "ran", "running", "run", "took", "taken", "taking", "gave", "given",
    "giving", "went", "going", "came", "coming", "said", "says", "saying",
    "told", "telling", "knew", "know", "known", "knowing", "thought",
    "think", "thinking", "want", "wanted", "need", "needed", "needs",
    "look", "looks", "looked", "looking", "keep", "keeps", "kept", "let",
    "lets", "put", "puts", "turn", "turns", "turned", "start", "starts",
    "started", "stop", "stops", "stopped", "try", "tried", "tries",
    "trying", "work", "works", "worked", "working", "add", "adds", "added",
    "adding", "fix", "fixes", "fixed", "fixing", "call", "calls", "called",
    "show", "shows", "showed", "shown", "become", "became", "becomes",
    # generic nouns that are *about* writing, not about a subject
    "post", "posts", "blog", "blogs", "article", "articles", "guide",
    "guides", "tutorial", "tutorials", "lesson", "lessons", "story",
    "stories", "note", "notes", "example", "examples", "demo", "demos",
    "tip", "tips", "trick", "tricks", "part", "parts", "step", "steps",
    "thing", "things", "stuff", "way", "ways", "time", "times", "day",
    "days", "week", "weeks", "month", "months", "year", "years", "hour",
    "hours", "minute", "minutes", "case", "cases", "reason", "reasons",
    "problem", "problems", "question", "questions", "answer", "answers",
    "idea", "ideas", "point", "points", "fact", "facts", "result",
    "results", "feature", "features", "version", "versions", "update",
    "updates", "change", "changes", "issue", "issues", "list", "lists",
    "number", "numbers", "name", "names", "kind", "kinds", "sort", "sorts",
    "type", "types", "end", "ends", "start", "beginning", "middle",
    # numbers and ordinals
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "hundred", "thousand", "million", "billion",
    "first", "second", "third", "fourth", "fifth", "last", "next",
    "another", "many", "several", "various",
    # generic adjectives / adverbs
    "new", "old", "good", "bad", "best", "worst", "better", "worse", "big",
    "small", "large", "little", "long", "short", "hard", "easy", "simple",
    "complex", "quick", "slow", "fast", "real", "true", "false", "right",
    "wrong", "sure", "maybe", "actually", "really", "finally", "already",
    "still", "never", "always", "ever", "often", "sometimes", "usually",
    "almost", "enough", "again", "back", "away", "over", "under", "why",
    "instead", "because", "while", "since", "until", "though", "although",
    "however", "therefore", "anyway", "rather", "quite", "pretty", "much",
    "less", "least", "own", "whole", "full", "empty", "free", "own",
}

# D3. Wikidata descriptions that mean "this item is not a subject you would
# ever want to cite from a technical blog post". Matched as substrings against
# the lowercased English description.
NON_TOPICAL_DESCRIPTION_PATTERNS = (
    # Wikimedia plumbing (was the only filter before this fix)
    "wikimedia", "wikipedia", "disambiguation", "category", "template",
    "list of", "wikinews", "wiktionary",
    # grammar / lexicography — this is the "ourselves" → pronoun "we" class
    "pronoun", "preposition", "conjunction", "interjection", "determiner",
    "grammatical", "part of speech", "letter of the", "digraph",
    "english word", "word in", "lexeme",
    # people and name items
    "given name", "family name", "surname", "male given", "female given",
    "unisex given", "human settlement in", "human biblical",
    "human who", "person who", "fictional character", "fictional human",
    # geography
    "commune in", "village in", "town in", "city in", "municipality in",
    "hamlet in", "civil parish", "census-designated", "locality in",
    "river in", "mountain in", "island in", "neighborhood", "neighbourhood",
    # media / art works
    "film", "movie", "album", "song", "single by", "studio album",
    "television series", "tv series", "episode of", "video game",
    "novel by", "book by", "poem", "painting", "sculpture", "band",
    "musical group", "manga", "anime",
    # science-article noise
    "scientific article", "scholarly article", "research article",
    "doctoral thesis", "preprint",
    # taxonomy
    "species of", "genus of", "family of moths", "taxon", "subspecies",
    "moth of the family", "beetle", "plant", "fungus",
    # sport / org noise
    "football club", "footballer", "association football",
)

# D3. Wikidata "instance of" / description heads that mark a *good* topical
# entity. Used as a positive signal, not a hard requirement.
TOPICAL_DESCRIPTION_HINTS = (
    "software", "programming", "computer", "computing", "technology",
    "protocol", "framework", "library", "language", "database", "operating",
    "algorithm", "practice", "methodology", "method", "process", "concept",
    "discipline", "field of", "branch of", "system", "service", "platform",
    "standard", "format", "technique", "strategy", "business", "management",
    "marketing", "engineering", "science", "security", "network", "web",
    "application", "tool", "company", "organization", "organisation",
)

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
    # Verified 2026-09-11 against the live Wikidata pages.
    "customer relationship management": "Q485643",
    "code review": "Q1342704",
    "software as a service": "Q1254596",
    "eating your own dog food": "Q3033752",
    # NOTE: do not hand-add entries here without checking the QID against the
    # live item first, and run `--audit-dictionary` afterwards. While writing
    # this fix a plausible-looking "dogfooding": "Q1226025" was nearly added —
    # the real QID for "eating your own dog food" is Q3033752. That is exactly
    # the class of error that put Q1540037 (Google Workspace) behind the
    # keywords "pilotflow" and "notiwise" in the first place.
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
    "arduino": "Q2225227",
    "openwrt": "Q1464818",
    "minecraft": "Q49740",
    "flutter": "Q56343037",
    "ruby": "Q161053",
    "golang": "Q37227",
    "java": "Q251",
    "php": "Q59",
    "laravel": "Q6489078",
    "django": "Q185667",
    "flask": "Q3437977",
    "mongodb": "Q1165204",
    "cloudflare": "Q5134633",
    "stripe": "Q7624164",
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
    "apache": "Q11354",
    "tomcat": "Q507430",
    "maven": "Q139894",
    "gradle": "Q4039686",
    "npm": "Q7067518",
    "webpack": "Q56283539",
    "vite": "Q110878961",
    # Verified 2026-09-11 against the live Wikidata pages.
    "crm": "Q485643",
    "saas": "Q1254596",
    "dogfooding": "Q3033752",
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
    "encryption": "Q141090",
    "authentication": "Q204756",
    "authorization": "Q4824619",
    "caching": "Q23762",
    "indexing": "Q1130645",
    "monitoring": "Q1137655",
    "logging": "Q1775371",
    "debugging": "Q189053",
    "refactoring": "Q1099908",
    "agile": "Q326116",
    "scrum": "Q724344",
    "kanban": "Q134861",
    # D5/D6 removed: "pilotflow"/"notiwise" both pointed at Q1540037 (Google
    # Workspace) — product names with no Wikidata item get NO link, not a
    # wrong one. "rest"/"vault"/"swift"/"rust"/"drone"/"dji"/"raspberry"/
    # "aws"/"azure"/"gcp"/"testing" removed too: under the old substring
    # matcher they hijacked unrelated topics, and several are ambiguous
    # dictionary words that the search path now handles with a relevance gate.
}

# Topic provenance. Curated fields are hand-written by the author and are
# trusted; the title is prose and is not (D2).
SOURCE_CURATED = "curated"
SOURCE_TITLE = "title"


# ---------------------------------------------------------------------------
# Matching helpers
# ---------------------------------------------------------------------------

def normalize_token(value: str) -> str:
    """Lowercase and strip everything that isn't a letter or digit."""
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def _words(value: str) -> list[str]:
    return [w for w in re.split(r"[^a-z0-9]+", (value or "").lower()) if w]


def _singular(word: str) -> str:
    """Crude singulariser so the tag "webhooks" still matches the label "webhook"."""
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("ses"):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def label_match_kind(topic: str, label: str) -> str | None:
    """How well does a Wikidata entity's label match the topic we searched for?

    Returns "exact", "all_words", "acronym" or None. None means reject — this
    is the gate that was entirely missing before (D3), and it is what stops
    a search for "ourselves" from being accepted as the pronoun "we".
    """
    t_norm, l_norm = normalize_token(topic), normalize_token(label)
    if not t_norm or not l_norm:
        return None
    if t_norm == l_norm or _singular(t_norm) == _singular(l_norm):
        return "exact"

    topic_words = [_singular(w) for w in _words(topic)]
    label_words = [_singular(w) for w in _words(label)]
    # "all words present" is only allowed for multi-word topics. For a single
    # word it is far too loose: the topic "built" is "all the words" of the
    # band "Built to Spill", and the topic "review" of "review of a film".
    if len(topic_words) >= 2 and all(w in label_words for w in topic_words):
        return "all_words"

    # "crm" → "customer relationship management": a short all-letters topic
    # whose characters are the initials of the label's words.
    if 2 <= len(t_norm) <= 6 and t_norm.isalpha() and len(label_words) >= 2:
        initials = "".join(w[0] for w in _words(label))
        if initials == t_norm:
            return "acronym"

    return None


def entity_is_non_topical(description: str) -> bool:
    """True if the entity's description marks it as a non-subject (D3)."""
    desc = (description or "").lower()
    if not desc:
        # No description at all is a weak signal of a thin/ambiguous item.
        return False
    return any(p in desc for p in NON_TOPICAL_DESCRIPTION_PATTERNS)


def entity_is_topical(description: str) -> bool:
    """True if the description looks like a real subject (positive signal)."""
    desc = (description or "").lower()
    return any(h in desc for h in TOPICAL_DESCRIPTION_HINTS)


def is_relevant_to_post(
    label: str,
    description: str,
    post_terms: set[str],
    post_phrases: list[str] | None = None,
) -> bool:
    """Audit-mode relevance test: does this entity relate to the post?

    `post_terms` is the set of normalized words from the post's own tags,
    categories, silot_terms and title; `post_phrases` are the curated terms
    kept whole (so the tag "crm" can still match the label "customer
    relationship management" through the acronym rule).
    """
    if entity_is_non_topical(description):
        return False
    for phrase in post_phrases or []:
        if label_match_kind(phrase, label) is not None:
            return True
    entity_words = set(_words(label)) | set(_words(description))
    entity_words = {w for w in entity_words if len(w) > 2 and w not in KEYWORD_STOPWORDS}
    return bool(entity_words & post_terms)


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

# Only indented, non-blank lines belong to the `seo:` block. A blank line ends
# it — deliberately conservative, so a wrapped scalar further down the
# frontmatter can never be swallowed and relocated by update_seo_links().
_SEO_BLOCK_RE = re.compile(
    r"^seo:[ \t]*\n((?:[ \t]+\S.*\n?)*)", re.MULTILINE
)
_LINKS_LIST_RE = re.compile(
    r"^([ \t]+)links:[ \t]*\n((?:[ \t]+-[ \t]+\S.*\n?)*)", re.MULTILINE
)


def extract_existing_seo_links(raw_fm: str) -> list[str]:
    """Read the NESTED seo.links list out of raw frontmatter text (D1).

    `parse_frontmatter_yaml_lite()` is a flat parser: given

        seo:
          links:
          - https://www.wikidata.org/wiki/Q1

    it returns {"seo": [], "links": [...]}. Callers reading `fm["seo"]["links"]`
    therefore always saw nothing, and the "skip files that already have links"
    guard never fired — which is how a force=false scheduled run overwrote a
    post that already had a hand-picked link.
    """
    if not raw_fm:
        return []
    block = _SEO_BLOCK_RE.search(raw_fm)
    if not block:
        return []
    links_match = _LINKS_LIST_RE.search(block.group(1))
    if not links_match:
        # inline form: `  links: [a, b]`
        inline = re.search(r"^[ \t]+links:[ \t]*\[(.*)\]", block.group(1), re.MULTILINE)
        if inline:
            return [v.strip().strip("'\"") for v in inline.group(1).split(",") if v.strip()]
        return []
    return [
        line.strip()[2:].strip().strip("'\"")
        for line in links_match.group(2).splitlines()
        if line.strip().startswith("- ")
    ]


def post_vocabulary(fm: dict) -> set[str]:
    """Normalized word set from the post's own curated fields + title."""
    terms: set[str] = set()
    for field in ("tags", "categories"):
        vals = fm.get(field, [])
        if isinstance(vals, str):
            vals = [v.strip() for v in vals.split(",")]
        for v in vals:
            terms.update(_words(str(v)))
    for field in ("silot_terms", "title", "description"):
        val = fm.get(field, "")
        if isinstance(val, str):
            terms.update(_words(val))
    return {t for t in terms if len(t) > 2 and t not in KEYWORD_STOPWORDS}


def post_phrases(fm: dict) -> list[str]:
    """Curated terms kept whole (tags, categories, silot_terms tokens)."""
    out: list[str] = []
    for field in ("tags", "categories"):
        vals = fm.get(field, [])
        if isinstance(vals, str):
            vals = [v.strip() for v in vals.split(",")]
        for v in vals:
            clean = str(v).strip().lower().replace("-", " ")
            if clean:
                out.append(clean)
    silot = fm.get("silot_terms", "")
    if isinstance(silot, str):
        out.extend(t for t in silot.split() if len(t) > 2)
    return list(dict.fromkeys(out))


def extract_topics(fm: dict, body: str = "") -> list[tuple[str, str]]:
    """Extract (topic, source) pairs from frontmatter.

    Curated fields (tags/categories/silot_terms) are trusted topics. Title
    words are candidates only, and generic prose words are dropped outright
    (D2) — before this fix, "built", "ourselves", "found", "two", "demo" and
    "first" were all sent to the Wikidata search API as if they were subjects.
    """
    topics: list[tuple[str, str]] = []

    for field in ("tags", "categories"):
        vals = fm.get(field, [])
        if isinstance(vals, str):
            vals = [v.strip() for v in vals.split(",")]
        for v in vals:
            clean = str(v).strip().lower().replace("-", " ")
            if clean and clean not in KEYWORD_STOPWORDS and clean not in GENERIC_CONTENT_WORDS:
                topics.append((clean, SOURCE_CURATED))

    silot = fm.get("silot_terms", "")
    if isinstance(silot, str) and silot:
        for term in silot.split():
            t = term.strip().lower()
            if len(t) > 2 and t not in KEYWORD_STOPWORDS and t not in GENERIC_CONTENT_WORDS:
                topics.append((t, SOURCE_CURATED))

    title = fm.get("title", "")
    if title:
        for w in re.findall(r"[a-zA-Z][a-zA-Z0-9\-]+", str(title).lower()):
            if len(w) <= 2:
                continue
            if w in KEYWORD_STOPWORDS or w in GENERIC_CONTENT_WORDS:
                continue
            topics.append((w, SOURCE_TITLE))

    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for topic, source in topics:
        if topic in seen:
            continue
        seen.add(topic)
        unique.append((topic, source))
    return unique


# ---------------------------------------------------------------------------
# Wikidata access
# ---------------------------------------------------------------------------

def _api_get(params: dict) -> dict | None:
    url = WIKIDATA_SEARCH_URL + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError) as exc:
        print(f"WARN: Wikidata request failed ({exc})", file=sys.stderr)
        return None


def search_wikidata(query: str, limit: int = 3) -> list[dict]:
    """Search Wikidata. Returns [{qid, label, description, match_type}]."""
    data = _api_get({
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "uselang": "en",
        "format": "json",
        "limit": str(limit),
        "type": "item",
    })
    if not data:
        return []
    results = []
    for item in data.get("search", []):
        results.append({
            "qid": item["id"],
            "label": item.get("label", ""),
            "description": item.get("description", ""),
            "match_type": (item.get("match") or {}).get("type", ""),
        })
    return results


def resolve_entities(qids: list[str]) -> dict[str, dict]:
    """Resolve QIDs to {qid: {label, description}} via wbgetentities (batched)."""
    out: dict[str, dict] = {}
    unique = [q for q in dict.fromkeys(qids) if re.fullmatch(r"Q\d+", q)]
    for i in range(0, len(unique), 50):
        batch = unique[i:i + 50]
        data = _api_get({
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "props": "labels|descriptions",
            "languages": "en",
            "format": "json",
        })
        if not data:
            continue
        for qid, entity in (data.get("entities") or {}).items():
            if "missing" in entity:
                out[qid] = {"label": "", "description": "", "missing": True}
                continue
            out[qid] = {
                "label": (entity.get("labels", {}).get("en") or {}).get("value", ""),
                "description": (entity.get("descriptions", {}).get("en") or {}).get("value", ""),
                "missing": False,
            }
        time.sleep(0.2)
    return out


# ---------------------------------------------------------------------------
# Entity selection
# ---------------------------------------------------------------------------

def find_best_entities(
    topics: list[tuple[str, str]],
    min_links: int = 2,
    max_links: int = 5,
    verbose: bool = True,
) -> list[str]:
    """Pick Wikidata entities for the given (topic, source) pairs.

    Every candidate must clear four gates (D3):
      A. the topic itself is not a generic prose word (handled in extract_topics)
      B. the entity's label actually matches the topic (label_match_kind)
      C. the entity's description is not a non-subject (entity_is_non_topical)
      D. the resulting score >= MIN_ACCEPT_SCORE
    Nothing is ever padded in to reach min_links (D7).
    """
    # Back-compat: accept a plain list of strings.
    norm_topics: list[tuple[str, str]] = [
        t if isinstance(t, tuple) else (t, SOURCE_CURATED) for t in topics
    ]

    entities: list[tuple[str, str, float, str]] = []  # (qid, label, score, why)
    seen_qids: set[str] = set()

    curated_terms = [t for t, s in norm_topics if s == SOURCE_CURATED]
    haystack = " ".join(curated_terms + [t for t, _ in norm_topics]).lower()

    # 1. Curated compound dictionary — highest confidence, no network.
    for compound, qid in COMPOUND_KEYWORDS.items():
        if compound in haystack and qid not in seen_qids:
            entities.append((qid, compound, 10.0, "dict:compound"))
            seen_qids.add(qid)

    # 2. Curated single-word dictionary — EXACT match only (D5).
    for i, (topic, _source) in enumerate(norm_topics):
        qid = SINGLE_KEYWORDS.get(normalize_token(topic))
        if qid and qid not in seen_qids:
            entities.append((qid, topic, 8.0 - (i * 0.1), "dict:single"))
            seen_qids.add(qid)

    # 3. Live search, gated.
    for i, (topic, source) in enumerate(norm_topics):
        if len(entities) >= max_links:
            break
        # Title-derived single words only get a search if they survived the
        # generic-word filter AND are long enough to be a real subject.
        if source == SOURCE_TITLE and len(normalize_token(topic)) < 4:
            continue

        results = search_wikidata(topic, limit=3)
        time.sleep(0.2)

        for result in results:
            qid = result["qid"]
            if qid in seen_qids:
                continue

            kind = label_match_kind(topic, result["label"])
            if kind is None:
                if verbose:
                    print(f"    reject {qid} ({result['label']!r}) — label does not match topic {topic!r}")
                continue
            if entity_is_non_topical(result["description"]):
                if verbose:
                    print(f"    reject {qid} ({result['label']!r}) — non-topical: {result['description']!r}")
                continue

            base = 5.5 if source == SOURCE_CURATED else 3.5
            bonus = {"exact": 1.5, "acronym": 1.0, "all_words": 0.5}[kind]
            penalty = i * 0.1
            score = base + bonus - penalty
            if entity_is_topical(result["description"]):
                score += 0.5

            if score < MIN_ACCEPT_SCORE:
                if verbose:
                    print(f"    reject {qid} ({result['label']!r}) — score {score:.1f} < {MIN_ACCEPT_SCORE}")
                continue

            seen_qids.add(qid)
            entities.append((qid, result["label"], score, f"search:{source}:{kind}"))
            break  # one entity per topic

    entities.sort(key=lambda x: -x[2])
    selected = entities[:max_links]

    if verbose:
        for qid, label, score, why in selected:
            print(f"    accept {qid} ({label}) score={score:.1f} via {why}")
        if len(selected) < min_links:
            print(f"    NOTE: only {len(selected)} entity/entities cleared the "
                  f"relevance gates (min_links={min_links}); writing what passed "
                  f"rather than padding with irrelevant items")

    return [WIKIDATA_ENTITY_URL.format(qid=qid) for qid, _, _, _ in selected]


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def update_seo_links(content: str, links: list[str]) -> str:
    """Replace (or insert) ONLY the seo.links list, preserving sibling keys (D4)."""
    links_yaml = "\n".join(f"    - {link}" for link in links)

    if not content.startswith("---"):
        return f"---\nseo:\n  links:\n{links_yaml.replace('    - ', '  - ')}\n---\n\n{content}"

    second = content.index("---", 3)
    # `content[3:second]` keeps the newline that follows the opening `---`;
    # re-emitting it produced the stray blank line at the top of every
    # frontmatter block the old populator ever touched (visible in commit
    # 65b679a's diff as a lone `+` on line 2 of each post).
    fm_text = content[3:second].lstrip("\n")
    body = content[second + 3:]

    block = _SEO_BLOCK_RE.search(fm_text)
    if block:
        inner = block.group(1)
        links_match = _LINKS_LIST_RE.search(inner)
        if links_match:
            indent = links_match.group(1)
            new_list = f"{indent}links:\n" + "\n".join(f"{indent}- {link}" for link in links) + "\n"
            new_inner = inner[:links_match.start()] + new_list + inner[links_match.end():]
        else:
            new_list = "  links:\n" + "\n".join(f"  - {link}" for link in links) + "\n"
            new_inner = inner.rstrip("\n") + "\n" + new_list if inner.strip() else new_list
        fm_text = fm_text[:block.start()] + "seo:\n" + new_inner + fm_text[block.end():]
    else:
        new_block = "seo:\n  links:\n" + "\n".join(f"  - {link}" for link in links) + "\n"
        fm_text = fm_text.rstrip("\n") + "\n" + new_block

    return f"---\n{fm_text}---{body}"


def process_file(
    file_path: Path,
    min_links: int = 2,
    max_links: int = 5,
    force: bool = False,
    dry_run: bool = False,
    replace_irrelevant: bool = False,
) -> bool:
    """Process a single file. Returns True if changes were made."""
    content = file_path.read_text(encoding="utf-8")
    fm, raw_fm, body = parse_frontmatter(content)

    if fm is None:
        print(f"SKIP {file_path}: no frontmatter")
        return False

    # D1: read the nested block, not fm["seo"].
    existing_links = extract_existing_seo_links(raw_fm)

    keep_links: list[str] = []
    if existing_links and not force and not replace_irrelevant:
        print(f"SKIP {file_path}: already has {len(existing_links)} seo links "
              f"(use --force to recompute, --replace-irrelevant to repair)")
        return False

    if existing_links and replace_irrelevant:
        vocab, phrases = post_vocabulary(fm), post_phrases(fm)
        resolved = resolve_entities([m.group() for link in existing_links
                                     if (m := re.search(r"Q\d+", link))])
        for link in existing_links:
            m = re.search(r"Q\d+", link)
            if not m:
                continue
            info = resolved.get(m.group())
            if info and not info.get("missing") and is_relevant_to_post(
                info["label"], info["description"], vocab, phrases
            ):
                keep_links.append(link)
            else:
                label = (info or {}).get("label", "?")
                print(f"    dropping irrelevant existing link {m.group()} ({label!r})")
        if len(keep_links) == len(existing_links):
            print(f"SKIP {file_path}: all {len(existing_links)} existing links look relevant")
            return False

    topics = extract_topics(fm, body)
    if not topics:
        print(f"SKIP {file_path}: no topics extracted")
        return False

    print(f"SCAN {file_path}: topics={[t for t, _ in topics][:8]}")
    room = max(0, max_links - len(keep_links))
    new_links = find_best_entities(topics, min_links=min_links, max_links=room) if room else []

    seen = set(keep_links)
    links = list(keep_links) + [ln for ln in new_links if ln not in seen]

    if not links:
        print(f"SKIP {file_path}: no Wikidata entity cleared the relevance gates")
        return False
    if links == existing_links:
        print(f"SKIP {file_path}: computed links identical to existing")
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


# ---------------------------------------------------------------------------
# Audit mode
# ---------------------------------------------------------------------------

AUDIT_COLUMNS = [
    "post_path", "post_title", "qid", "wikidata_url", "label", "description",
    "relevance", "reason", "post_terms",
]


def audit_files(files: list[Path], csv_path: Path, offline: bool = False) -> dict:
    """Resolve every QID in every post's seo.links and flag irrelevant ones.

    Writes one CSV row per (post, QID). `relevance` is one of:
      ok          — the entity shares vocabulary with the post's own terms
      suspect     — resolvable, but nothing in its label/description relates
                    to the post's tags/categories/silot_terms/title
      non-topical — its description marks it as a pronoun / given name /
                    village / film / taxon / Wikimedia page etc.
      missing     — the QID does not exist on Wikidata
      unresolved  — Wikidata was unreachable (no verdict possible)
      malformed   — the link is not a Wikidata entity URL
    """
    rows: list[dict] = []
    all_qids: list[str] = []
    per_file: list[tuple[Path, dict, str, list[str]]] = []

    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"WARN: cannot read {f}: {exc}", file=sys.stderr)
            continue
        fm, raw_fm, _ = parse_frontmatter(content)
        if fm is None:
            continue
        links = extract_existing_seo_links(raw_fm)
        if not links:
            continue
        per_file.append((f, fm, raw_fm, links))
        for link in links:
            m = re.search(r"Q\d+", link)
            if m:
                all_qids.append(m.group())

    resolved = {} if offline else resolve_entities(all_qids)

    counts = {"ok": 0, "suspect": 0, "non-topical": 0, "missing": 0,
              "unresolved": 0, "malformed": 0}

    for f, fm, _raw, links in per_file:
        vocab, phrases = post_vocabulary(fm), post_phrases(fm)
        title = str(fm.get("title", ""))
        for link in links:
            m = re.search(r"Q\d+", link)
            if not m or "wikidata.org" not in link:
                verdict, reason, qid, label, desc = "malformed", "not a Wikidata entity URL", "", "", ""
            else:
                qid = m.group()
                info = resolved.get(qid)
                if info is None:
                    verdict, reason, label, desc = "unresolved", "Wikidata unreachable", "", ""
                elif info.get("missing"):
                    verdict, reason, label, desc = "missing", "QID does not exist", "", ""
                else:
                    label, desc = info["label"], info["description"]
                    if entity_is_non_topical(desc):
                        verdict = "non-topical"
                        reason = f"description matches a non-subject pattern: {desc!r}"
                    elif is_relevant_to_post(label, desc, vocab, phrases):
                        verdict, reason = "ok", "shares vocabulary with the post's own terms"
                    else:
                        verdict = "suspect"
                        reason = "no overlap with the post's tags/categories/silot_terms/title"
            counts[verdict] = counts.get(verdict, 0) + 1
            rows.append({
                "post_path": str(f),
                "post_title": title,
                "qid": qid,
                "wikidata_url": link,
                "label": label,
                "description": desc,
                "relevance": verdict,
                "reason": reason,
                "post_terms": " ".join(sorted(vocab)[:25]),
            })

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nAudit written to {csv_path}")
    print(f"  posts with seo.links : {len(per_file)}")
    print(f"  links audited        : {len(rows)}")
    for k in ("ok", "suspect", "non-topical", "missing", "unresolved", "malformed"):
        if counts.get(k):
            print(f"  {k:<20}: {counts[k]}")
    return counts


DICT_AUDIT_COLUMNS = ["table", "keyword", "qid", "wikidata_url", "label",
                      "description", "verdict", "reason"]


def audit_dictionary(csv_path: Path) -> dict:
    """Validate the hand-curated keyword→QID tables against live Wikidata.

    The hard-coded tables are the highest-confidence path in this script, which
    makes a wrong entry there the most damaging kind of defect: it silently
    stamps the same wrong QID onto every post that mentions the keyword (see
    "pilotflow"/"notiwise" → Q1540037 "Google Workspace", removed 2026-09-11).
    Re-run this after every edit to COMPOUND_KEYWORDS / SINGLE_KEYWORDS.
    """
    pairs = ([("COMPOUND_KEYWORDS", k, v) for k, v in COMPOUND_KEYWORDS.items()] +
             [("SINGLE_KEYWORDS", k, v) for k, v in SINGLE_KEYWORDS.items()])
    resolved = resolve_entities([qid for _, _, qid in pairs])

    rows, counts = [], {}
    for table, keyword, qid in pairs:
        info = resolved.get(qid)
        if info is None:
            verdict, reason, label, desc = "unresolved", "Wikidata unreachable", "", ""
        elif info.get("missing"):
            verdict, reason, label, desc = "missing", "QID does not exist", "", ""
        else:
            label, desc = info["label"], info["description"]
            if entity_is_non_topical(desc):
                verdict, reason = "non-topical", f"description: {desc!r}"
            elif label_match_kind(keyword, label) is None:
                verdict = "mismatch"
                reason = f"label {label!r} does not match keyword {keyword!r}"
            else:
                verdict, reason = "ok", f"label matches ({label_match_kind(keyword, label)})"
        counts[verdict] = counts.get(verdict, 0) + 1
        rows.append({
            "table": table, "keyword": keyword, "qid": qid,
            "wikidata_url": WIKIDATA_ENTITY_URL.format(qid=qid),
            "label": label, "description": desc,
            "verdict": verdict, "reason": reason,
        })

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=DICT_AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDictionary audit written to {csv_path}  ({len(rows)} keywords)")
    for k, v in sorted(counts.items()):
        print(f"  {k:<12}: {v}")
    return counts


def collect_files(dirs: list[str], files: list[str], glob: str) -> list[Path]:
    out: list[Path] = []
    for f in files:
        p = Path(f)
        if p.exists():
            out.append(p)
        else:
            print(f"WARN: file not found: {p}", file=sys.stderr)
    for d in dirs:
        p = Path(d)
        if not p.is_dir():
            print(f"WARN: directory not found: {p}", file=sys.stderr)
            continue
        out.extend(sorted(p.glob(glob)))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Populate (or audit) seo.links with relevant Wikidata entities."
    )
    parser.add_argument("--dir", action="append", default=[],
                        help="Directory of Jekyll posts (repeatable)")
    parser.add_argument("--file", action="append", default=[],
                        help="Single file to process (repeatable)")
    parser.add_argument("--min-links", type=int, default=2, help="Minimum links per post (default: 2)")
    parser.add_argument("--max-links", type=int, default=4, help="Maximum links per post (default: 4)")
    parser.add_argument("--force", action="store_true", help="Recompute seo.links even if present")
    parser.add_argument("--replace-irrelevant", action="store_true",
                        help="Keep existing links that pass the audit, replace the rest")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    parser.add_argument("--glob", default="*.md", help="File glob pattern (default: *.md)")
    parser.add_argument("--audit-csv", metavar="PATH",
                        help="Audit mode: write a seo.links relevance report to PATH (no writes to posts)")
    parser.add_argument("--audit-offline", action="store_true",
                        help="Audit mode: skip Wikidata resolution (structure-only report)")
    parser.add_argument("--audit-dictionary", metavar="PATH",
                        help="Validate the hard-coded keyword→QID tables against "
                             "live Wikidata and write the report to PATH")
    args = parser.parse_args()

    if args.audit_dictionary:
        audit_dictionary(Path(args.audit_dictionary))
        if not args.dir and not args.file:
            return 0

    if not args.dir and not args.file:
        parser.error("at least one --dir or --file is required")

    files = collect_files(args.dir, args.file, args.glob)

    if args.audit_csv:
        audit_files(files, Path(args.audit_csv), offline=args.audit_offline)
        return 0

    changed = 0
    for f in files:
        if process_file(f, args.min_links, args.max_links, args.force,
                        args.dry_run, args.replace_irrelevant):
            changed += 1

    print(f"\nDone: {changed}/{len(files)} files updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
