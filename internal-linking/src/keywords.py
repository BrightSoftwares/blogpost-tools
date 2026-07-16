"""Phase 2 — Keyword extraction.

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md
(Section 1 "Phase 2 — Keyword Extraction" and its
``extract_meaningful_ngrams`` helper).

Extracts a ranked list of ``(keyword, specificity_score, source_tier)``
candidates per post, in priority order: title (tier "title" /
"title-full", specificity 1.0) > tags/categories (tier "tag", 0.8) >
filename n-grams (tier "filename", 0.5, backward-compat with v1).

Note on config wiring: the spec's ``extract_keywords(post, nlp_model)``
signature (Section 1) takes no config argument, and its pseudocode
hardcodes the n-gram window per tier (title: 2-5, filename: 2-4) and the
minimum keyword length (3) directly rather than reading them from
``config.keyword_min_ngram`` / ``keyword_max_ngram`` / ``keyword_min_length``
(defined in config.py / Section 3). This module follows the spec's
pseudocode literally. If per-tier n-gram bounds should be configurable,
that requires widening this function's signature — left for a follow-up.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Tuple

from models import PostMetadata

logger = logging.getLogger(__name__)

# en -> en_core_web_sm, fr -> fr_core_news_sm, etc. (spec Section 1, Main Orchestrator)
_SPACY_MODEL_BY_LANG = {
    "en": "en_core_web_sm",
    "fr": "fr_core_news_sm",
    "es": "es_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm",
    "pt": "pt_core_news_sm",
}


def get_spacy_model_for_lang(lang: str) -> str:
    """Return the spaCy model name to load for a given language.

    Args:
        lang: One of the supported languages (en, fr, es, de, it, pt).

    Returns:
        spaCy model name (e.g. "en_core_web_sm").

    Raises:
        ValueError: If the language has no known spaCy model mapping.
    """
    try:
        return _SPACY_MODEL_BY_LANG[lang]
    except KeyError as exc:
        raise ValueError(f"No spaCy model mapping for lang: {lang}") from exc


def normalize(text: str) -> str:
    """Normalize text for comparison: lowercase, trim, collapse whitespace,
    strip trailing punctuation.

    Args:
        text: Raw text (e.g. a post title or anchor text).

    Returns:
        Normalized text.
    """
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]+$", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_pure_stopword(kw: str, nlp_model) -> bool:
    """Return True if every token in ``kw`` is a stopword (or there are no
    meaningful tokens at all).

    Args:
        kw: Candidate keyword/phrase.
        nlp_model: Loaded spaCy language pipeline.

    Returns:
        True if ``kw`` carries no non-stopword content.
    """
    doc = nlp_model(kw)
    tokens = [t for t in doc if not t.is_space and not t.is_punct]
    if not tokens:
        return True
    return all(t.is_stop for t in tokens)


def is_proper_noun(kw: str, nlp_model) -> bool:
    """Return True if ``kw`` contains at least one proper-noun token.

    Args:
        kw: Candidate keyword (typically a single word here).
        nlp_model: Loaded spaCy language pipeline.

    Returns:
        True if any token is tagged PROPN.
    """
    doc = nlp_model(kw)
    tokens = [t for t in doc if not t.is_space and not t.is_punct]
    return any(t.pos_ == "PROPN" for t in tokens)


def extract_meaningful_ngrams(doc, min_n: int, max_n: int) -> List[str]:
    """Extract meaningful n-grams from a spaCy doc.

    "Meaningful" = the window is not all stopwords (contains at least one
    NOUN or PROPN) and neither the first nor last token is a stopword.

    Args:
        doc: spaCy Doc.
        min_n: Minimum n-gram length (inclusive).
        max_n: Maximum n-gram length (inclusive).

    Returns:
        List of n-gram strings (original casing preserved; callers
        lowercase as needed).
    """
    tokens = [t for t in doc if not t.is_punct and not t.is_space]
    ngrams: List[str] = []

    for n in range(min_n, max_n + 1):
        for i in range(len(tokens) - n + 1):
            window = tokens[i : i + n]
            if not any(t.pos_ in ("NOUN", "PROPN") for t in window):
                continue
            if window[0].is_stop or window[-1].is_stop:
                continue
            ngrams.append(" ".join(t.text for t in window))

    return ngrams


def extract_keywords(post: PostMetadata, nlp_model) -> List[Tuple[str, float, str]]:
    """Extract a ranked list of keyword candidates for a post (Phase 2).

    Priority order: title > tags/categories > filename n-grams.

    Args:
        post: Post to extract keywords from (title/tags/categories/slug used).
        nlp_model: Loaded spaCy language pipeline matching the post's language.

    Returns:
        List of (keyword, specificity_score, source_tier) tuples, sorted
        with longer (more specific) keywords first, then by score
        descending, then by length descending.
    """
    candidates: List[Tuple[str, float, str]] = []

    # Tier A — Title (specificity 1.0)
    title_doc = nlp_model(post.title)
    for ngram in extract_meaningful_ngrams(title_doc, min_n=2, max_n=5):
        candidates.append((ngram.lower(), 1.0, "title"))
    candidates.append((normalize(post.title), 1.0, "title-full"))

    # Tier B — Tags & categories (specificity 0.8)
    for tag in list(post.tags) + list(post.categories):
        candidates.append((tag.lower(), 0.8, "tag"))

    # Tier C — Filename-derived n-grams (specificity 0.5, backward-compat)
    filename_slug = post.slug.replace("-", " ")
    slug_doc = nlp_model(filename_slug)
    for ngram in extract_meaningful_ngrams(slug_doc, min_n=2, max_n=4):
        candidates.append((ngram.lower(), 0.5, "filename"))

    # Deduplicate: keep highest specificity per keyword
    deduplicated: Dict[str, Tuple[float, str]] = {}
    for kw, score, source in candidates:
        if kw not in deduplicated or deduplicated[kw][0] < score:
            deduplicated[kw] = (score, source)

    # Filter: drop too-short/stopword-only/short-common-word keywords
    filtered: List[Tuple[str, float, str]] = []
    for kw, (score, source) in deduplicated.items():
        if len(kw) < 3:
            continue
        if is_pure_stopword(kw, nlp_model):
            continue
        if len(kw.split()) == 1 and len(kw) < 4 and not is_proper_noun(kw, nlp_model):
            continue
        filtered.append((kw, score, source))

    # Sort: longer keywords first (more specific), then by score, then by length
    filtered.sort(key=lambda x: (-len(x[0].split()), -x[1], -len(x[0])))

    return filtered
