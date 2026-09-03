"""Client for Smart Assets Manager deterministic image generation.

Root cause (2026-09-02, found while debugging "never posted to LinkedIn"):
this client was written against a payload shape the live SAM API
(`BrightSoftwares/smart-assets-manager`, `backend/app/schemas/deterministic.py`
+ `backend/app/api/deterministic.py`, SP5.2/SP5.3) never actually implements.
Every live call failed with HTTP 422 ("Field required: type") — confirmed via
GitHub Actions job logs, run 33414570733, step "Generate next post". Fixed to
match the real contract:

  - Top-level ``type`` is required (``"svg"`` for the built-in social card
    templates in ``SOCIAL_TEMPLATES`` — NOT ``"social_card"``, which is a
    different, simpler generator with its own field set).
  - Template selection + variables live under ``data.template_id`` /
    ``data.variables`` (an ``SVGTemplateData`` object), not top-level
    ``template_id``/``params``.
  - ``generate_sizes`` is a bool switch, not the list of size strings this
    client used to send.
  - The ``social_media`` preset generates profile/cover-photo sizes (e.g.
    1640x624 Facebook Cover, 400x400 profile pics) — NOT the 1200x627 /
    1200x1200 blog card sizes this pipeline needs. Use ``custom_sizes``
    instead; leaving a size's ``name`` unset makes the API default it to
    ``f"{width}x{height}"``, which is what this client keys its response
    parsing on.
  - The response is ``DeterministicGenerationResponse``: ``assets`` (each
    with ``width``/``height``/``name``/``url``), not a flat ``urls`` list;
    credits are ``credits_charged``, not ``credits_used``.
  - The three built-in templates (``SOCIAL_TEMPLATES`` in
    ``smart-assets-manager/backend/app/social_templates_registry.py``) take
    pre-wrapped per-line variables (``title_line1..3``, ``excerpt_line1..2``,
    etc.), not a single raw string — this client now wraps text client-side.
"""

from __future__ import annotations

import logging
import os
import textwrap
import time

import requests

logger = logging.getLogger(__name__)

_RETRY_DELAYS = [1, 2, 4]

# The `smart-assets.bright-softwares.com` custom domain has no DNS record
# (confirmed 2026-08-22 CI scan: NameResolutionError on every call). Default
# to the known-working Render URL instead; SAM_API_URL still overrides it if
# the custom domain is ever provisioned.
_DEFAULT_SAM_API_BASE = os.environ.get("SAM_API_URL", "https://smart-assets-manager.onrender.com")

# Blog social cards need a landscape (LinkedIn/OG feed) and a square
# (Facebook/Instagram) rendition. The API's built-in "social_media" preset is
# for profile/cover photos and does not include these sizes — request them
# explicitly instead. Leaving "name" unset makes the API default it to
# "{width}x{height}", which _generate_social_card_variables()/the caller key
# their result lookup on.
_CARD_SIZES = [
    {"width": 1200, "height": 627},
    {"width": 1200, "height": 1200},
]
_LANDSCAPE_SIZE_NAME = "1200x627"
_SQUARE_SIZE_NAME = "1200x1200"

_LINE_WRAP_CHARS = 50


def _wrap_lines(text: str, max_lines: int, max_chars: int = _LINE_WRAP_CHARS) -> list[str]:
    """Wrap ``text`` into at most ``max_lines`` lines of ``max_chars`` each.

    Returns a list padded to exactly ``max_lines`` entries (empty strings for
    unused lines) so callers can always unpack ``title_line1``, ``_line2``, …
    positionally without an IndexError.
    """
    text = (text or "").strip()
    if not text:
        return [""] * max_lines
    wrapped = textwrap.wrap(
        text, width=max_chars, max_lines=max_lines, placeholder="…"
    )
    wrapped += [""] * (max_lines - len(wrapped))
    return wrapped[:max_lines]


def _build_svg_variables(
    template_id: str,
    title: str,
    excerpt: str | None,
    social_stat: str | None,
    cta: str | None,
    brand_name: str,
    brand_colors: dict,
) -> dict:
    """Build the ``data.variables`` payload for one of the SOCIAL_TEMPLATES.

    ``template_id`` is the short id (``quote-card``/``stat-card``/
    ``question-hook``), matching ``image_style`` — the registry's
    ``social-<template_id>`` prefix is applied by the caller.
    """
    variables = {
        "brand_name": brand_name,
        "primary_color": brand_colors.get("primary", "#0066CC"),
        "secondary_color": brand_colors.get("secondary", "#00CC66"),
        "accent_color": brand_colors.get("accent", "#FF6600"),
    }

    if template_id == "stat-card":
        title_lines = _wrap_lines(title, 2)
        variables["stat"] = (social_stat or "").strip()
        # No dedicated "stat label" input exists upstream yet — fall back to
        # the post title's first line so the card isn't blank. Best-guess;
        # revisit if stat-card posts need a distinct caption field.
        variables["stat_label"] = title_lines[0]
        variables["title_line1"], variables["title_line2"] = title_lines
    elif template_id == "question-hook":
        title_lines = _wrap_lines(title, 3)
        cta_lines = _wrap_lines(cta, 2)
        variables["title_line1"], variables["title_line2"], variables["title_line3"] = title_lines
        variables["cta_line1"], variables["cta_line2"] = cta_lines
    else:
        # "quote-card" is the config default (_data/social_config.yml
        # image.default_style) and the fallback for any unrecognized style.
        title_lines = _wrap_lines(title, 3)
        excerpt_lines = _wrap_lines(excerpt, 2)
        variables["title_line1"], variables["title_line2"], variables["title_line3"] = title_lines
        variables["excerpt_line1"], variables["excerpt_line2"] = excerpt_lines

    return variables


def generate_social_card(
    api_key: str,
    template_id: str,
    title: str,
    excerpt: str | None,
    social_stat: str | None,
    brand_colors: dict,
    cta: str | None = None,
    brand_name: str = "",
    api_base: str = _DEFAULT_SAM_API_BASE,
) -> dict:
    """Call Smart Assets Manager deterministic generation endpoint.

    Args:
        api_key: Bearer token for the SAM API.
        template_id: One of 'quote-card', 'stat-card', 'question-hook'.
        title: Blog post title.
        excerpt: Optional excerpt for the card body (quote-card only).
        social_stat: Optional stat string (e.g. '74% fewer rules') (stat-card only).
        brand_colors: Dict with keys primary, secondary, accent.
        cta: Optional call-to-action text (question-hook only).
        brand_name: Brand name shown on the card.
        api_base: Base URL for the SAM instance.

    Returns:
        Dict with landscape_url (1200x627), square_url (1200x1200), credits_used.
    """
    url = f"{api_base.rstrip('/')}/api/v1/deterministic/generate"
    payload = {
        "type": "svg",
        "storage": "cloudinary",
        "visibility": "public",
        "generate_sizes": True,
        "custom_sizes": _CARD_SIZES,
        "data": {
            "template_id": f"social-{template_id}",
            "variables": _build_svg_variables(
                template_id, title, excerpt, social_stat, cta, brand_name, brand_colors
            ),
        },
        "output_format": "PNG",
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
            sizes = {
                asset["name"]: asset.get("secure_url") or asset.get("url")
                for asset in data.get("assets", [])
            }
            logger.debug("SAM API response = %s", data)
            logger.debug("Parsed sizes = %s", sizes)

            # SAM's top-level "success" flag only means the request was
            # accepted and processed -- it does NOT mean assets were
            # actually generated and stored. A Cloudinary storage failure
            # (e.g. missing/misconfigured API key on the SAM side) comes
            # back as HTTP 200 with `success: true`, `total_generated: 0`,
            # `assets: []`, and the real failure buried in a per-size
            # `errors` list. Root cause (2026-09-03, run 33623967098, job
            # 100227254579): every request hit
            # "Failed to store in Cloudinary: Failed to upload to
            # Cloudinary: Must supply api_key" here, `sizes` ended up `{}`,
            # and this function silently returned empty landscape_url /
            # square_url -- the caller had no signal anything went wrong
            # and wrote a social draft with blank image URLs. Treat a
            # non-empty `errors` list, or zero assets on a non-zero
            # request, as a hard failure instead of degrading silently.
            errors = data.get("errors") or []
            total_requested = data.get("total_requested", len(_CARD_SIZES))
            total_generated = data.get("total_generated", len(data.get("assets", [])))
            if errors or (total_requested and not total_generated):
                logger.error(
                    "SAM reported success=%s but generated 0 usable assets "
                    "(requested=%s, generated=%s). generation_id=%s errors=%s",
                    data.get("success"),
                    total_requested,
                    total_generated,
                    data.get("generation_id"),
                    errors,
                )
                raise RuntimeError(
                    f"SAM returned HTTP {resp.status_code} but generated 0/"
                    f"{total_requested} assets (generation_id="
                    f"{data.get('generation_id')!r}). Per-size errors: {errors}"
                )

            landscape_url = sizes.get(_LANDSCAPE_SIZE_NAME, "")
            square_url = sizes.get(_SQUARE_SIZE_NAME, "")
            if not landscape_url or not square_url:
                # Belt-and-braces: even if SAM reports success/generated
                # counts that look fine, refuse to hand back a partial
                # result silently -- an empty URL here is exactly what
                # produced empty social images before this fix.
                logger.error(
                    "SAM response had no per-size error but is still missing "
                    "an expected size. landscape_url=%r square_url=%r "
                    "expected=%s got_keys=%s",
                    landscape_url,
                    square_url,
                    (_LANDSCAPE_SIZE_NAME, _SQUARE_SIZE_NAME),
                    list(sizes.keys()),
                )
                raise RuntimeError(
                    f"SAM response missing expected sizes: "
                    f"landscape={landscape_url!r} square={square_url!r} "
                    f"(got keys {list(sizes.keys())})"
                )

            return {
                "landscape_url": landscape_url,
                "square_url": square_url,
                "credits_used": data.get("credits_charged", 0.0),
            }
        except RuntimeError:
            raise
        except Exception as exc:
            logger.warning("SAM request error on attempt %d: %s", attempt + 1, exc)
            last_exc = exc

    raise RuntimeError(f"SAM failed after retries: {last_exc}")
