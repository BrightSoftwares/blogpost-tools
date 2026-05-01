"""Client for Smart Assets Manager deterministic image generation."""

from __future__ import annotations

import logging
import time

import requests

logger = logging.getLogger(__name__)

_RETRY_DELAYS = [1, 2, 4]


def generate_social_card(
    api_key: str,
    template_id: str,
    title: str,
    excerpt: str | None,
    social_stat: str | None,
    brand_colors: dict,
    api_base: str = "https://smart-assets.bright-softwares.com",
) -> dict:
    """Call Smart Assets Manager deterministic generation endpoint.

    Args:
        api_key: Bearer token for the SAM API.
        template_id: One of 'quote-card', 'stat-card', 'question-hook'.
        title: Blog post title.
        excerpt: Optional excerpt for the card body.
        social_stat: Optional stat string (e.g. '74% fewer rules').
        brand_colors: Dict with keys primary, secondary, accent.
        api_base: Base URL for the SAM instance.

    Returns:
        Dict with landscape_url (1200x627), square_url (1200x1200), credits_used.
    """
    url = f"{api_base.rstrip('/')}/api/v1/deterministic/generate"
    payload = {
        "template_id": f"social-{template_id}",
        "preset_name": "social_media",
        "storage": "cloudinary",
        "visibility": "public",
        "generate_sizes": ["1200x627", "1200x1200"],
        "params": {
            "title": title,
            "excerpt": excerpt or "",
            "stat": social_stat or "",
            "primary_color": brand_colors.get("primary", "#0066CC"),
            "secondary_color": brand_colors.get("secondary", "#00CC66"),
            "accent_color": brand_colors.get("accent", "#FF6600"),
        },
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    last_exc: Exception | None = None
    for attempt, delay in enumerate([0] + _RETRY_DELAYS):
        if delay:
            time.sleep(delay)
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            if resp.status_code >= 500:
                logger.warning("SAM 5xx on attempt %d: %s", attempt + 1, resp.text[:200])
                last_exc = RuntimeError(f"SAM server error {resp.status_code}")
                continue
            if resp.status_code >= 400:
                raise RuntimeError(
                    f"SAM client error {resp.status_code}: {resp.text[:400]}"
                )
            data = resp.json()
            sizes = {item["size"]: item["url"] for item in data.get("urls", [])}
            return {
                "landscape_url": sizes.get("1200x627", ""),
                "square_url": sizes.get("1200x1200", ""),
                "credits_used": data.get("credits_used", 0.0),
            }
        except RuntimeError:
            raise
        except Exception as exc:
            logger.warning("SAM request error on attempt %d: %s", attempt + 1, exc)
            last_exc = exc

    raise RuntimeError(f"SAM failed after retries: {last_exc}")
