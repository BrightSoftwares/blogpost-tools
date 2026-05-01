"""Fetch and parse brand voice from a remote markdown file."""

from __future__ import annotations

import logging
import re

import requests

logger = logging.getLogger(__name__)

_cache: dict[str, dict] = {}
_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


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
