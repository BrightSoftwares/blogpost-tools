"""Fetch and parse brand voice from a local design-system submodule file or a remote markdown file."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

_cache: dict[str, dict] = {}
_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_SLUG_RE = re.compile(r"^[a-z0-9-]+$")


def load_brand_voice_from_submodule(repo_root: Path, slug: str) -> dict | None:
    """Load brand voice from the design-system submodule's structured JSON.

    Expects the caller repo to have `brightsoftwares/design-system` checked out
    as a submodule at `_design-system/` (requires `submodules: true` on the
    checkout step). Returns None if the slug or the file is not present, so
    callers can fall back to `fetch_brand_voice` (remote markdown URL).

    Maps the richer JSON schema (tagline, pain_points, ...) onto the same
    {tagline, voice, default_pain_point} shape `compose_post` already consumes.
    """
    if not slug or not _SLUG_RE.match(slug):
        # `slug` comes from `_data/social_config.yml` in the *calling* repo —
        # reject anything but a bare identifier to prevent path traversal
        # (e.g. slug="../../../../etc/passwd") reading files outside
        # _design-system/brand-voice/.
        if slug:
            logger.warning("Rejecting invalid brand voice slug: %r", slug)
        return None
    voice_path = repo_root / "_design-system" / "brand-voice" / f"{slug}.json"
    if not voice_path.exists():
        return None
    try:
        data = json.loads(voice_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"expected a JSON object, got {type(data).__name__}")
    except Exception as exc:
        logger.warning("Could not parse brand voice JSON at %s: %s", voice_path, exc)
        return None

    pain_points = data.get("pain_points") or []
    return {
        "tagline": data.get("tagline", ""),
        "voice": ", ".join(data.get("voice_adjectives", [])),
        "default_pain_point": pain_points[0] if pain_points else "",
    }


def _extract_section(text: str, heading: str) -> str:
    """Return content between ``## heading`` and the next ``##`` heading (or EOF)."""
    matches = list(_HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        if m.group(1).strip().lower() == heading.lower():
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            return text[start:end].strip()
    return ""


def fetch_brand_voice(voice_url: str, timeout: int = 10) -> dict:
    """Download a brand voice markdown file and extract key sections.

    Returns:
        dict with keys: tagline, voice, default_pain_point.
        Falls back to empty strings if URL unreachable.
    """
    if not voice_url:
        return {}

    if voice_url in _cache:
        return _cache[voice_url]

    result: dict = {"tagline": "", "voice": "", "default_pain_point": ""}
    try:
        resp = requests.get(voice_url, timeout=timeout)
        resp.raise_for_status()
        text = resp.text
        result["tagline"] = (
            _extract_section(text, "brandname_tagline")
            or _extract_section(text, "ai_brand_tagline")
        )
        result["voice"] = _extract_section(text, "ai_brand_voice")
        # First sentence of voice as default pain point
        voice = result["voice"]
        if voice:
            first_sentence = re.split(r"(?<=[.!?])\s", voice)[0]
            result["default_pain_point"] = first_sentence
    except Exception as exc:
        logger.warning("Could not fetch brand voice from %s: %s", voice_url, exc)

    _cache[voice_url] = result
    return result
