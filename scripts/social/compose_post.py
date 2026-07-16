"""Compose LinkedIn and Facebook post copy from blog post frontmatter."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_LINKEDIN_MAX = 3000
_MARKDOWN_STRIP = re.compile(r"[*_`#\[\]>]")

# UTM convention: 958.010.STANDARD.all.reference.revenue-engine-demand-side.md §7.4
# utm_source=<site/platform> · utm_medium=<organic|email|listing|community> ·
# utm_campaign=<exp-<product>-<nn>|evergreen> — lowercase, hyphens, no spaces.
_UTM_MEDIUM_SOCIAL = "organic"
_UTM_CAMPAIGN_DEFAULT = "evergreen"


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
    """Return the absolute, publishable URL for a post.

    Jekyll frontmatter `permalink` is always a site-relative path (e.g.
    ``/en/my-post/``) — it is never posted as-is to LinkedIn/Facebook, which
    need a full absolute URL to render a clickable link/preview. ``site_url``
    lives at the top level of ``_data/social_config.yml`` (``brand.site_url``
    is kept as a fallback for older configs).
    """
    site_url = config.get("site_url") or config.get("brand", {}).get("site_url", "")
    site_url = site_url.rstrip("/")

    raw_permalink = post["frontmatter"].get("permalink")
    if raw_permalink:
        path = raw_permalink if raw_permalink.startswith("/") else f"/{raw_permalink}"
        return f"{site_url}{path}" if site_url else raw_permalink

    return f"{site_url}/{post['slug']}/"


def _add_utm_params(url: str, *, utm_source: str, utm_medium: str, utm_campaign: str) -> str:
    """Append the vault UTM convention (958.010 §7.4) to a CTA URL.

    Existing query params are preserved; any pre-existing utm_* params on the
    URL are overridden by the ones computed here. No-op if ``url`` has no
    scheme (e.g. a bare relative path slipped through with no site_url set).
    """
    parts = urlsplit(url)
    if not parts.scheme:
        logger.warning("Cannot attach UTM params to non-absolute URL: %r", url)
        return url

    query_pairs = [(k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_")]
    query_pairs += [
        ("utm_source", utm_source),
        ("utm_medium", utm_medium),
        ("utm_campaign", utm_campaign),
    ]
    new_query = urlencode(query_pairs)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))


def _utm_campaign(post: dict, config: dict) -> str:
    """Resolve utm_campaign: frontmatter override > config default > 'evergreen'.

    Channel-experiment traffic (958.010 §7.2, ALGO 953.066) sets
    ``utm_campaign: exp-<product>-<nn>`` in the post frontmatter to carry its
    experiment id end to end; everything else falls back to 'evergreen'.
    """
    fm = post["frontmatter"]
    return (
        fm.get("utm_campaign")
        or config.get("defaults", {}).get("utm_campaign")
        or _UTM_CAMPAIGN_DEFAULT
    )


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
    utm_campaign = _utm_campaign(post, config)
    # Per-platform CTA links per 958.010 §7.4 — utm_source is the platform the
    # click originates FROM (linkedin/facebook), not the destination site.
    li_permalink = _add_utm_params(
        permalink, utm_source="linkedin", utm_medium=_UTM_MEDIUM_SOCIAL, utm_campaign=utm_campaign
    )
    fb_permalink = _add_utm_params(
        permalink, utm_source="facebook", utm_medium=_UTM_MEDIUM_SOCIAL, utm_campaign=utm_campaign
    )
    hashtags = _hashtags(post)
    brand_name = config.get("brand", {}).get("name", "")
    image_style = fm.get("social_image_style") or config.get("image", {}).get("default_style", "quote-card")

    li_hashtags = hashtags[: config.get("linkedin", {}).get("hashtag_count", 5)]
    fb_hashtags = hashtags[: config.get("facebook", {}).get("hashtag_count", 2)]

    env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=False)

    ctx_base = {
        "title": fm.get("title", ""),
        "excerpt": excerpt,
        "pain_point": pain_point,
        "cta": cta,
        "social_stat": fm.get("social_stat", ""),
        "brand_name": brand_name,
    }

    li_text = env.get_template("linkedin.j2").render(**ctx_base, permalink=li_permalink, hashtags=li_hashtags)
    if len(li_text) > _LINKEDIN_MAX:
        # Truncate excerpt to fit within limit
        overflow = len(li_text) - _LINKEDIN_MAX + 1
        truncated_excerpt = excerpt[: max(0, len(excerpt) - overflow)] + "…"
        li_text = env.get_template("linkedin.j2").render(
            **{**ctx_base, "excerpt": truncated_excerpt}, permalink=li_permalink, hashtags=li_hashtags
        )

    fb_text = env.get_template("facebook.j2").render(**ctx_base, permalink=fb_permalink, hashtags=fb_hashtags)

    return {
        "linkedin": {"text": li_text.strip(), "image_style": image_style},
        "facebook": {"text": fb_text.strip(), "image_style": image_style},
    }
