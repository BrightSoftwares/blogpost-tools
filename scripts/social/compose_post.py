"""Compose LinkedIn and Facebook post copy from blog post frontmatter."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_LINKEDIN_MAX = 3000
_MARKDOWN_STRIP = re.compile(r"[*_`#\[\]>]")


def _strip_markdown(text: str) -> str:
    """Remove common markdown symbols from a string."""
    return _MARKDOWN_STRIP.sub("", text).strip()


def _derive_excerpt(post: dict) -> str:
    """Return excerpt from frontmatter or first non-heading paragraph of body."""
    if post["frontmatter"].get("excerpt"):
        return post["frontmatter"]["excerpt"]
    paragraphs = post["body"].split("\n\n")
    for p in paragraphs:
        p = p.strip()
        if p.startswith("#"):
            continue
        stripped = _strip_markdown(p)
        if stripped:
            return stripped
    return ""


def _derive_permalink(post: dict, config: dict) -> str:
    """Return permalink from frontmatter or build from slug + site_url."""
    if post["frontmatter"].get("permalink"):
        return post["frontmatter"]["permalink"]
    site_url = config.get("brand", {}).get("site_url", "")
    return f"{site_url.rstrip('/')}/{post['slug']}/"


def _hashtags(post: dict) -> list[str]:
    """Return hashtags from frontmatter (hashtags or tags fields)."""
    raw = post["frontmatter"].get("hashtags") or post["frontmatter"].get("tags", [])
    return [str(t).lower().replace(" ", "") for t in raw]


def compose_post(
    post: dict,
    config: dict,
    brand_voice: dict | None = None,
) -> dict:
    """Render LinkedIn and Facebook copy from post + config + optional brand voice.

    Args:
        post: Dict with keys slug, frontmatter, body (from select_next_post).
        config: Loaded ``_data/social_config.yml``.
        brand_voice: Optional dict from brand_voice_fetcher.fetch_brand_voice.

    Returns:
        Dict with keys linkedin and facebook, each containing text and image_style.
    """
    bv = brand_voice or {}
    fm = post["frontmatter"]

    pain_point = (
        fm.get("pain_point")
        or bv.get("default_pain_point")
        or config.get("brand", {}).get("default_pain_point", "")
    )
    cta = (
        fm.get("cta")
        or config.get("defaults", {}).get("cta", "")
        or bv.get("tagline", "")
    )
    excerpt = _derive_excerpt(post)
    permalink = _derive_permalink(post, config)
    hashtags = _hashtags(post)
    brand_name = config.get("brand", {}).get("name", "")
    image_style = fm.get("social_image_style") or config.get("image", {}).get("default_style", "quote-card")

    li_hashtags = hashtags[: config.get("linkedin", {}).get("hashtag_count", 5)]
    fb_hashtags = hashtags[: config.get("facebook", {}).get("hashtag_count", 2)]

    env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=False)

    ctx_base = {
        "title": fm.get("title", ""),
        "excerpt": excerpt,
        "permalink": permalink,
        "pain_point": pain_point,
        "cta": cta,
        "social_stat": fm.get("social_stat", ""),
        "brand_name": brand_name,
    }

    li_text = env.get_template("linkedin.j2").render(**ctx_base, hashtags=li_hashtags)
    if len(li_text) > _LINKEDIN_MAX:
        # Truncate excerpt to fit within limit
        overflow = len(li_text) - _LINKEDIN_MAX + 1
        truncated_excerpt = excerpt[: max(0, len(excerpt) - overflow)] + "…"
        li_text = env.get_template("linkedin.j2").render(
            **{**ctx_base, "excerpt": truncated_excerpt}, hashtags=li_hashtags
        )

    fb_text = env.get_template("facebook.j2").render(**ctx_base, hashtags=fb_hashtags)

    return {
        "linkedin": {"text": li_text.strip(), "image_style": image_style},
        "facebook": {"text": fb_text.strip(), "image_style": image_style},
    }
