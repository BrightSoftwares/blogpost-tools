"""Unit tests for readability-checker/src/main.py.

Covers: syllable/sentence/word counting, the two scoring formulas, markdown
+ frontmatter stripping (so markup does not pollute the counts), and the
edge cases called out in the spec (empty posts, missing frontmatter,
non-UTF8 content, very short posts).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import main  # noqa: E402


# ---------------------------------------------------------------------------
# Syllable counting
# ---------------------------------------------------------------------------

def test_count_syllables_simple_words():
    assert main.count_syllables("cat") == 1
    assert main.count_syllables("banana") == 3
    assert main.count_syllables("readability") == 5


def test_count_syllables_silent_e():
    assert main.count_syllables("like") == 1
    assert main.count_syllables("time") == 1


def test_count_syllables_empty_or_non_alpha_returns_at_least_one():
    assert main.count_syllables("") == 0
    assert main.count_syllables("123") == 0


# ---------------------------------------------------------------------------
# Sentence / word counting
# ---------------------------------------------------------------------------

def test_count_sentences_basic():
    assert main.count_sentences("One. Two! Three?") == 3


def test_count_sentences_no_terminal_punctuation_counts_as_one():
    assert main.count_sentences("No punctuation here") == 1


def test_count_sentences_empty_text_is_zero():
    assert main.count_sentences("") == 0


def test_count_words_ignores_punctuation():
    words = main.count_words("Hello, world! It's fine.")
    assert words == ["Hello", "world", "It's", "fine"]


# ---------------------------------------------------------------------------
# Scoring formulas
# ---------------------------------------------------------------------------

def test_flesch_reading_ease_simple_text_scores_high():
    # Short words, short sentences -> easy to read -> high score.
    text = "The cat sat on the mat. The dog ran fast. I like cake."
    score = main.flesch_reading_ease(text)
    assert score is not None
    assert score > 80


def test_flesch_reading_ease_complex_text_scores_lower():
    complex_text = (
        "The implementation necessitates comprehensive consideration of "
        "multifaceted architectural interdependencies, particularly "
        "regarding asynchronous distributed transactional consistency "
        "guarantees across heterogeneous microservice infrastructures."
    )
    simple_text = "The cat sat on the mat. The dog ran fast. I like cake."
    complex_score = main.flesch_reading_ease(complex_text)
    simple_score = main.flesch_reading_ease(simple_text)
    assert complex_score < simple_score


def test_flesch_reading_ease_no_words_returns_none():
    assert main.flesch_reading_ease("") is None
    assert main.flesch_reading_ease("...") is None


def test_flesch_kincaid_grade_simple_text_low_grade():
    text = "The cat sat on the mat. The dog ran fast."
    grade = main.flesch_kincaid_grade(text)
    assert grade is not None
    assert grade < 6


def test_flesch_kincaid_grade_no_words_returns_none():
    assert main.flesch_kincaid_grade("") is None


# ---------------------------------------------------------------------------
# Frontmatter / markdown stripping
# ---------------------------------------------------------------------------

def test_strip_frontmatter_extracts_metadata_and_body():
    content = "---\ntitle: Hello World\nauthor: Jane\n---\nThis is the body.\n"
    fm, body = main.strip_frontmatter(content)
    assert fm["title"] == "Hello World"
    assert fm["author"] == "Jane"
    assert body.strip() == "This is the body."


def test_strip_frontmatter_no_delimiter_returns_full_content_as_body():
    content = "Just a plain markdown file, no frontmatter.\n"
    fm, body = main.strip_frontmatter(content)
    assert fm == {}
    assert body.strip() == content.strip()


def test_strip_markdown_removes_code_blocks_entirely():
    text = "Some prose.\n```python\ndef f(x_very_long_identifier_name): pass\n```\nMore prose."
    stripped = main.strip_markdown(text)
    assert "def" not in stripped
    assert "x_very_long_identifier_name" not in stripped
    assert "Some prose." in stripped
    assert "More prose." in stripped


def test_strip_markdown_removes_headings_and_list_markers():
    text = "# Heading One\n\n- item one\n- item two\n\nParagraph text here."
    stripped = main.strip_markdown(text)
    assert "#" not in stripped
    assert stripped.count("- ") == 0
    assert "Heading One" in stripped
    assert "item one" in stripped


def test_strip_markdown_keeps_link_text_drops_url():
    text = "Read the [documentation](https://example.com/very/long/path) for details."
    stripped = main.strip_markdown(text)
    assert "documentation" in stripped
    assert "https://example.com" not in stripped


def test_strip_markdown_removes_images_entirely():
    text = "Before image. ![alt text for a diagram](https://example.com/img.png) After image."
    stripped = main.strip_markdown(text)
    assert "example.com" not in stripped
    assert "Before image." in stripped
    assert "After image." in stripped


def test_strip_markdown_keeps_wikilink_display_text():
    text = "See [[some-file#Some Heading|the reference]] for context."
    stripped = main.strip_markdown(text)
    assert "the reference" in stripped
    assert "some-file" not in stripped


def test_strip_markdown_removes_bold_and_italic_markers():
    text = "This is **very important** and *also relevant*."
    stripped = main.strip_markdown(text)
    assert "*" not in stripped
    assert "very important" in stripped
    assert "also relevant" in stripped


# ---------------------------------------------------------------------------
# analyze_post edge cases (file-level)
# ---------------------------------------------------------------------------

def test_analyze_post_with_realistic_sample(tmp_path):
    post = tmp_path / "sample.md"
    post.write_text(
        "---\n"
        "title: A Simple Post\n"
        "date: 2026-01-01\n"
        "---\n"
        "# A Simple Post\n\n"
        "The cat sat on the mat. The dog ran fast. I like cake.\n\n"
        "```python\ndef unrelated_code_that_should_not_count(): pass\n```\n",
        encoding="utf-8",
    )
    result = main.analyze_post(post, min_score=60, target_grade_level=10)
    assert result is not None
    assert result["title"] == "A Simple Post"
    assert result["flesch_reading_ease"] is not None
    assert result["flesch_reading_ease"] > 60
    assert result["below_min_score"] is False
    # Code identifiers must not have been counted as prose words.
    assert result["word_count"] < 20


def test_analyze_post_empty_body_returns_none(tmp_path):
    post = tmp_path / "empty.md"
    post.write_text("---\ntitle: Empty\n---\n\n\n", encoding="utf-8")
    result = main.analyze_post(post, min_score=60, target_grade_level=10)
    assert result is None


def test_analyze_post_missing_frontmatter_still_scores(tmp_path):
    post = tmp_path / "no-frontmatter.md"
    post.write_text("The cat sat on the mat. The dog ran fast.\n", encoding="utf-8")
    result = main.analyze_post(post, min_score=60, target_grade_level=10)
    assert result is not None
    assert result["title"] == "no-frontmatter"  # falls back to filename stem


def test_analyze_post_non_utf8_file_is_skipped_not_crashed(tmp_path):
    post = tmp_path / "bad-encoding.md"
    post.write_bytes(b"\xff\xfe\x00\x01 not valid utf-8 \x80\x81")
    result = main.analyze_post(post, min_score=60, target_grade_level=10)
    assert result is None


def test_analyze_post_very_short_post_still_scores(tmp_path):
    post = tmp_path / "short.md"
    post.write_text("---\ntitle: Short\n---\nHi.\n", encoding="utf-8")
    result = main.analyze_post(post, min_score=60, target_grade_level=10)
    assert result is not None
    assert result["word_count"] == 1


def test_flesch_kincaid_grade_dense_text_scores_high_grade():
    dense_text = (
        "Notwithstanding the aforementioned methodological considerations, "
        "the epistemological ramifications of this multidisciplinary "
        "investigation necessitate substantial reconceptualization."
    )
    grade = main.flesch_kincaid_grade(dense_text)
    assert grade is not None
    assert grade > 12
