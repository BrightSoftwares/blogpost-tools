"""Tests for common/frontmatter_utils.py — the shared frontmatter parsing library.

Extracted 2026-08-28 (wave-6, 231.004 blog-automation campaign) from 7
independent reimplementations across retire-posts, jekyll-multi-language-tools,
scripts, scripts/bsgen and seo-links-enricher. These tests pin down the exact
behavior each call site depended on, so a future edit to this shared module
can't silently change one caller's output without a red test.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))

import frontmatter_utils as frontmatter  # noqa: E402


# --- parse_frontmatter (dict, body) ----------------------------------------

def test_parse_frontmatter_basic():
    content = "---\ntitle: Hello\nlang: en\n---\nBody text here.\n"
    fm, body = frontmatter.parse_frontmatter(content)
    assert fm == {"title": "Hello", "lang": "en"}
    assert body == "Body text here.\n"


def test_parse_frontmatter_no_delimiter_returns_empty_dict():
    content = "Just a plain markdown file, no frontmatter.\n"
    fm, body = frontmatter.parse_frontmatter(content)
    assert fm == {}
    assert body == content


def test_parse_frontmatter_malformed_yaml_does_not_raise():
    # Obsidian-style wikilink inside a value breaks yaml.safe_load.
    content = "---\ntitle: [[broken wikilink\n---\nBody\n"
    fm, body = frontmatter.parse_frontmatter(content)
    assert fm == {}
    assert body == "Body\n"


def test_parse_frontmatter_non_dict_yaml_returns_empty_dict():
    content = "---\n- just\n- a\n- list\n---\nBody\n"
    fm, body = frontmatter.parse_frontmatter(content)
    assert fm == {}
    assert body == "Body\n"


def test_parse_frontmatter_tolerates_trailing_whitespace_after_delimiter():
    content = "---   \ntitle: Hello\n---  \nBody\n"
    fm, body = frontmatter.parse_frontmatter(content)
    assert fm == {"title": "Hello"}
    assert body == "Body\n"


# --- parse_frontmatter_dict (dict only) ------------------------------------

def test_parse_frontmatter_dict():
    content = "---\ntitle: Hello\n---\nBody\n"
    assert frontmatter.parse_frontmatter_dict(content) == {"title": "Hello"}


def test_parse_frontmatter_dict_no_match():
    assert frontmatter.parse_frontmatter_dict("no frontmatter here") == {}


# --- parse_frontmatter_with_offsets (dict, body, start, end) ---------------

def test_parse_frontmatter_with_offsets_basic():
    content = "---\ntitle: Hello\n---\nBody\n"
    fm, body, start, end = frontmatter.parse_frontmatter_with_offsets(content)
    assert fm == {"title": "Hello"}
    assert body == "Body\n"
    assert start == 0
    assert content[end:] == body


def test_parse_frontmatter_with_offsets_no_match():
    fm, body, start, end = frontmatter.parse_frontmatter_with_offsets("no fm")
    assert fm == {}
    assert body == "no fm"
    assert start == -1
    assert end == -1


def test_parse_frontmatter_with_offsets_malformed_yaml_does_not_raise():
    # Regression: the original enrich_seo_links.py::extract_frontmatter had
    # no try/except around yaml.safe_load and would crash the whole run.
    content = "---\ntitle: [[broken\n---\nBody\n"
    fm, body, start, end = frontmatter.parse_frontmatter_with_offsets(content)
    assert fm == {}
    assert body == "Body\n"


# --- write_frontmatter (round-trip) ----------------------------------------

def test_write_frontmatter_round_trips():
    fm = {"title": "Hello", "tags": ["a", "b"]}
    body = "Body text.\n"
    out = frontmatter.write_frontmatter(fm, body)
    fm2, body2 = frontmatter.parse_frontmatter(out)
    assert fm2 == fm
    assert body2 == body


def test_write_frontmatter_preserves_key_order():
    fm = {"z": 1, "a": 2}
    out = frontmatter.write_frontmatter(fm, "body\n")
    z_idx = out.index("z:")
    a_idx = out.index("a:")
    assert z_idx < a_idx  # sort_keys=False


# --- parse_frontmatter_flat (flat dict, manual line-split) -----------------

def test_parse_frontmatter_flat_basic():
    content = '---\ntitle: "Hello"\nPriority: P1\n---\nrest of file'
    fm = frontmatter.parse_frontmatter_flat(content)
    assert fm == {"title": "Hello", "Priority": "P1"}


def test_parse_frontmatter_flat_tolerates_wikilinks():
    # This is exactly why scan_completed_subprojects.py avoids yaml.safe_load.
    content = '---\nProject: "[[203.PRJ.blog-automation]]"\nStatus: "In Progress"\n---\nrest'
    fm = frontmatter.parse_frontmatter_flat(content)
    assert fm["Status"] == "In Progress"
    assert "[[203.PRJ.blog-automation]]" in fm["Project"]


def test_parse_frontmatter_flat_no_match():
    assert frontmatter.parse_frontmatter_flat("plain text") == {}


# --- parse_frontmatter_flat_with_body (dict, raw_str, remaining) -----------

def test_parse_frontmatter_flat_with_body_basic():
    content = "---\nlang: en\nredirect_from: '/old/path/'\n---\nBody here"
    fm, raw, remaining = frontmatter.parse_frontmatter_flat_with_body(content)
    assert fm == {"lang": "en", "redirect_from": "/old/path/"}
    assert "lang: en" in raw
    assert remaining == "Body here"


def test_parse_frontmatter_flat_with_body_no_match():
    fm, raw, remaining = frontmatter.parse_frontmatter_flat_with_body("no fm")
    assert fm == {}
    assert raw == ""
    assert remaining == "no fm"


def test_parse_frontmatter_flat_with_body_strips_both_quote_styles():
    content = "---\na: \"double\"\nb: 'single'\n---\nbody"
    fm, _, _ = frontmatter.parse_frontmatter_flat_with_body(content)
    assert fm == {"a": "double", "b": "single"}


# --- parse_frontmatter_yaml_lite (dict|None, raw_str, body; list support) --

def test_parse_frontmatter_yaml_lite_scalars():
    content = "---\ntitle: Hello\nauthor: Kekeli\n---\nBody"
    fm, raw, body = frontmatter.parse_frontmatter_yaml_lite(content)
    assert fm == {"title": "Hello", "author": "Kekeli"}
    assert body == "\nBody"  # leading \n preserved, matches original slice semantics


def test_parse_frontmatter_yaml_lite_block_list():
    content = "---\ntags:\n  - python\n  - jekyll\ntitle: Post\n---\nBody"
    fm, raw, body = frontmatter.parse_frontmatter_yaml_lite(content)
    assert fm["tags"] == ["python", "jekyll"]
    assert fm["title"] == "Post"


def test_parse_frontmatter_yaml_lite_inline_list():
    content = "---\ntags: [python, jekyll]\n---\nBody"
    fm, raw, body = frontmatter.parse_frontmatter_yaml_lite(content)
    assert fm["tags"] == ["python", "jekyll"]


def test_parse_frontmatter_yaml_lite_no_delimiter_returns_none():
    fm, raw, body = frontmatter.parse_frontmatter_yaml_lite("no frontmatter")
    assert fm is None
    assert raw == ""
    assert body == "no frontmatter"


# --- extract_frontmatter_text / get_frontmatter_value ----------------------

def test_extract_frontmatter_text_basic():
    content = "---\nlang: en\nref: my-post\n---\nBody content"
    fm_text, body = frontmatter.extract_frontmatter_text(content)
    assert "lang: en" in fm_text
    assert body == "\nBody content"  # leading \n preserved, matches original split(2) semantics


def test_extract_frontmatter_text_no_delimiter():
    fm_text, body = frontmatter.extract_frontmatter_text("no frontmatter")
    assert fm_text == ""
    assert body == "no frontmatter"


def test_extract_frontmatter_text_malformed_returns_body_unchanged():
    content = "---\nonly one delimiter\nBody"
    fm_text, body = frontmatter.extract_frontmatter_text(content)
    assert fm_text == ""
    assert body == content


def test_get_frontmatter_value_found():
    fm_text = "\nlang: en\nref: my-post\n"
    assert frontmatter.get_frontmatter_value(fm_text, "lang") == "en"
    assert frontmatter.get_frontmatter_value(fm_text, "ref") == "my-post"


def test_get_frontmatter_value_quoted():
    fm_text = '\ntitle: "Hello World"\n'
    assert frontmatter.get_frontmatter_value(fm_text, "title") == "Hello World"


def test_get_frontmatter_value_missing_field():
    fm_text = "\nlang: en\n"
    assert frontmatter.get_frontmatter_value(fm_text, "missing") == ""
