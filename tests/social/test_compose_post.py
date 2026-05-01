"""Tests for compose_post — T4, T5, T6, T7."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "social"))

from compose_post import compose_post

_BASE_CONFIG = {
    "site_url": "https://bright-softwares.com",
    "defaults": {
        "pain_point": "Struggling with manual work?",
        "cta": "Read more →",
        "hashtags": ["automation", "productivity", "devtools", "saas", "brightsoftwares"],
    },
}
_BASE_BRAND_VOICE = {
    "tagline": "Ship faster.",
    "voice": "Direct and pragmatic.",
    "default_pain_point": "Wasting time on repetitive tasks?",
}


def _make_post(frontmatter: dict, body: str = "## Heading\n\nParagraph text here.\n") -> dict:
    return {
        "slug": "test-slug",
        "blog_path": "_posts/en/2024-01-01-test-slug.md",
        "frontmatter": frontmatter,
        "body": body,
    }


# T4 — all frontmatter fields present
def test_t4_full_frontmatter() -> None:
    post = _make_post({
        "title": "My Great Post",
        "excerpt": "A short excerpt about automation.",
        "permalink": "/en/my-great-post/",
        "tags": ["gmail", "automation", "productivity", "devtools", "saas"],
        "pain_point": "Too many manual steps?",
        "cta": "Try it free →",
        "social_stat": "74% fewer rules",
    })
    result = compose_post(post, _BASE_CONFIG, _BASE_BRAND_VOICE)

    li = result["linkedin"]["text"]
    assert "Too many manual steps?" in li
    assert "A short excerpt" in li
    assert "Try it free →" in li
    assert "/en/my-great-post/" in li
    # 5 hashtags from post tags
    assert li.count("#") == 5


# T5 — missing pain_point and cta → falls back to brand_voice then config
def test_t5_fallback_pain_point_cta() -> None:
    post = _make_post({
        "title": "No Extras",
        "excerpt": "Simple excerpt.",
        "permalink": "/en/no-extras/",
        "tags": ["automation"],
    })
    result = compose_post(post, _BASE_CONFIG, _BASE_BRAND_VOICE)

    li = result["linkedin"]["text"]
    # Should use brand voice default_pain_point
    assert "Wasting time on repetitive tasks?" in li
    # CTA falls back to config default
    assert "Read more →" in li


# T6 — excerpt > 3000 chars → LinkedIn body truncated
def test_t6_long_excerpt_truncated() -> None:
    long_excerpt = "word " * 700  # ~3500 chars
    post = _make_post({
        "title": "Long Post",
        "excerpt": long_excerpt,
        "permalink": "/en/long-post/",
        "tags": ["automation"],
    })
    result = compose_post(post, _BASE_CONFIG, {})

    li = result["linkedin"]["text"]
    assert len(li) <= 3000
    assert "…" in li


# T7 — no excerpt frontmatter → first paragraph of body used
def test_t7_no_excerpt_uses_body() -> None:
    post = _make_post(
        {"title": "No Excerpt", "permalink": "/en/no-excerpt/", "tags": ["automation"]},
        body="## Heading\n\nThis is the first real paragraph.\n\nSecond paragraph ignored.\n",
    )
    result = compose_post(post, _BASE_CONFIG, {})

    li = result["linkedin"]["text"]
    assert "This is the first real paragraph." in li
