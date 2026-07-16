"""Unit tests for src/keywords.py (Phase 2 — keyword extraction).

Requires the en_core_web_sm spaCy model to be installed
(``python -m spacy download en_core_web_sm``, or built into the
Dockerfile.internal-linking image). Tests are skipped gracefully if the
model isn't available in the current environment.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import ExclusionReason, PostMetadata  # noqa: E402

try:
    import spacy

    _NLP = spacy.load("en_core_web_sm")
except Exception:  # noqa: BLE001 - broad on purpose: missing module or missing model both skip
    _NLP = None

from keywords import (  # noqa: E402
    extract_keywords,
    extract_meaningful_ngrams,
    get_spacy_model_for_lang,
    is_proper_noun,
    is_pure_stopword,
    normalize,
)


def _make_post(title: str, slug: str, tags=None, categories=None) -> PostMetadata:
    return PostMetadata(
        slug=slug,
        filepath=Path(f"/tmp/{slug}.md"),
        title=title,
        date=None,
        tags=tags or [],
        categories=categories or [],
        lang="en",
        body="",
        body_word_count=0,
        eligible_as_target=True,
        exclusion_reason=ExclusionReason.NONE,
        url_path=f"/{slug}/",
        frontmatter={},
    )


@unittest.skipIf(_NLP is None, "en_core_web_sm spaCy model not installed in this environment")
class TestExtractKeywords(unittest.TestCase):
    def test_title_tags_and_filename_tiers_present(self):
        post = _make_post(
            title="How to Install Nginx on Ubuntu",
            slug="how-to-install-nginx-on-ubuntu",
            tags=["nginx", "ubuntu"],
            categories=["devops"],
        )
        keywords = extract_keywords(post, _NLP)
        sources = {source for _kw, _score, source in keywords}

        self.assertIn("tag", sources)
        self.assertTrue(any(kw == "nginx" for kw, _score, source in keywords if source == "tag"))
        # Full-title candidate should survive filtering (long, multi-word).
        self.assertTrue(any(source == "title-full" for _kw, _score, source in keywords))

    def test_dedup_keeps_highest_specificity(self):
        # "nginx" appears both as a tag (0.8) and would also appear via
        # filename n-grams (0.5) if the slug contained it; the tag score
        # should win once deduplicated.
        post = _make_post(title="Nginx Guide", slug="nginx-guide", tags=["nginx"])
        keywords = extract_keywords(post, _NLP)
        nginx_entries = [(kw, score, source) for kw, score, source in keywords if kw == "nginx"]
        self.assertEqual(len(nginx_entries), 1)
        _kw, score, _source = nginx_entries[0]
        self.assertEqual(score, 0.8)

    def test_short_common_word_filtered_out(self):
        post = _make_post(title="The Big One", slug="the-big-one", tags=["it"])
        keywords = extract_keywords(post, _NLP)
        kws = [kw for kw, _score, _source in keywords]
        self.assertNotIn("it", kws)  # 2 chars, not proper noun -> filtered

    def test_sort_order_longer_keywords_first(self):
        post = _make_post(
            title="Complete Guide to Kubernetes Cluster Management",
            slug="complete-guide-to-kubernetes-cluster-management",
            tags=["kubernetes"],
        )
        keywords = extract_keywords(post, _NLP)
        if len(keywords) > 1:
            word_counts = [len(kw.split()) for kw, _s, _src in keywords]
            self.assertEqual(word_counts, sorted(word_counts, reverse=True))

    def test_empty_tags_and_categories_do_not_crash(self):
        post = _make_post(title="Just A Title Here", slug="just-a-title-here")
        keywords = extract_keywords(post, _NLP)
        self.assertIsInstance(keywords, list)


@unittest.skipIf(_NLP is None, "en_core_web_sm spaCy model not installed in this environment")
class TestHelperFunctions(unittest.TestCase):
    def test_is_pure_stopword_true(self):
        self.assertTrue(is_pure_stopword("the and", _NLP))

    def test_is_pure_stopword_false(self):
        self.assertFalse(is_pure_stopword("nginx server", _NLP))

    def test_is_proper_noun_true(self):
        # en_core_web_sm's statistical tagger needs a token it reliably
        # tags PROPN in isolation; "Docker" is stable, some other
        # capitalized tech nouns (e.g. "Kubernetes") get tagged NOUN
        # out of context by this small model.
        self.assertTrue(is_proper_noun("Docker", _NLP))

    def test_is_proper_noun_false(self):
        self.assertFalse(is_proper_noun("server", _NLP))

    def test_extract_meaningful_ngrams_rejects_stopword_edges(self):
        doc = _NLP("the install of nginx")
        ngrams = extract_meaningful_ngrams(doc, min_n=2, max_n=2)
        self.assertNotIn("the install", ngrams)


class TestNormalizeAndModelMapping(unittest.TestCase):
    """These don't need the spaCy model, so they always run."""

    def test_normalize_strips_trailing_punctuation_and_lowercases(self):
        self.assertEqual(normalize("How To Install Nginx?"), "how to install nginx")

    def test_normalize_collapses_whitespace(self):
        self.assertEqual(normalize("  multiple   spaces here  "), "multiple spaces here")

    def test_get_spacy_model_for_lang_known(self):
        self.assertEqual(get_spacy_model_for_lang("en"), "en_core_web_sm")
        self.assertEqual(get_spacy_model_for_lang("fr"), "fr_core_news_sm")

    def test_get_spacy_model_for_lang_unknown_raises(self):
        with self.assertRaises(ValueError):
            get_spacy_model_for_lang("xx")


if __name__ == "__main__":
    unittest.main()
