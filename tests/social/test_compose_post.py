"""Tests for compose_post — T4, T5, T6, T7."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "social"))

from compose_post import _add_utm_params, _derive_permalink, compose_post

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


# T8 — UTM convention (958.010 §7.4): every published CTA link carries
# utm_source/utm_medium/utm_campaign automatically, per platform.
def test_t8_linkedin_and_facebook_links_carry_utm_params() -> None:
    post = _make_post({
        "title": "UTM Post",
        "excerpt": "Excerpt.",
        "permalink": "/en/utm-post/",
        "tags": ["automation"],
    })
    result = compose_post(post, _BASE_CONFIG, {})

    li = result["linkedin"]["text"]
    fb = result["facebook"]["text"]

    assert "https://bright-softwares.com/en/utm-post/?" in li
    assert "utm_source=linkedin" in li
    assert "utm_medium=organic" in li
    assert "utm_campaign=evergreen" in li

    assert "https://bright-softwares.com/en/utm-post/?" in fb
    assert "utm_source=facebook" in fb
    assert "utm_medium=organic" in fb
    assert "utm_campaign=evergreen" in fb


# T9 — frontmatter utm_campaign overrides the 'evergreen' default (channel
# experiment traffic per 958.010 §7.2 / ALGO 953.066).
def test_t9_frontmatter_utm_campaign_override() -> None:
    post = _make_post({
        "title": "Experiment Post",
        "excerpt": "Excerpt.",
        "permalink": "/en/experiment-post/",
        "tags": ["automation"],
        "utm_campaign": "exp-notiwise-01",
    })
    result = compose_post(post, _BASE_CONFIG, {})

    assert "utm_campaign=exp-notiwise-01" in result["linkedin"]["text"]
    assert "utm_campaign=exp-notiwise-01" in result["facebook"]["text"]


# T10 — _derive_permalink always returns an absolute URL when site_url is set,
# even though Jekyll frontmatter permalinks are site-relative.
def test_t10_derive_permalink_is_absolute() -> None:
    post = _make_post({"title": "X", "permalink": "/en/some-post/"})
    assert _derive_permalink(post, _BASE_CONFIG) == "https://bright-softwares.com/en/some-post/"

    post_no_permalink = _make_post({"title": "X"})
    post_no_permalink["slug"] = "some-slug"
    assert _derive_permalink(post_no_permalink, _BASE_CONFIG) == "https://bright-softwares.com/some-slug/"


# T11 — _add_utm_params overrides any pre-existing utm_* params and preserves
# other query params; no-ops on non-absolute URLs instead of corrupting them.
def test_t11_add_utm_params_overrides_existing_and_preserves_other_query() -> None:
    url = "https://bright-softwares.com/en/post/?ref=abc&utm_source=old"
    result = _add_utm_params(url, utm_source="linkedin", utm_medium="organic", utm_campaign="evergreen")

    assert "ref=abc" in result
    assert "utm_source=linkedin" in result
    assert "utm_source=old" not in result

    relative = "/en/post/"
    assert _add_utm_params(relative, utm_source="linkedin", utm_medium="organic", utm_campaign="evergreen") == relative
