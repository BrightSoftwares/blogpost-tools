"""Tests for brand_voice_fetcher."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "social"))

from brand_voice_fetcher import fetch_brand_voice

_SAMPLE_DOC = """
## brandname_tagline
Ship faster.

## ai_brand_voice
Direct. Pragmatic. Developer-first.

## ai_brand_tagline
Automate the boring parts.

## other_section
Not extracted.
"""


def _mock_resp(text: str, status: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.ok = status < 400
    resp.text = text
    resp.raise_for_status = MagicMock(side_effect=None if status < 400 else Exception(f"HTTP {status}"))
    return resp


def test_parses_all_sections() -> None:
    with patch("brand_voice_fetcher.requests.get") as mock_get:
        mock_get.return_value = _mock_resp(_SAMPLE_DOC)
        result = fetch_brand_voice("https://example.com/brand.md")

    assert result["tagline"] == "Ship faster."
    assert "Direct" in result["voice"]


def test_returns_empty_on_network_error() -> None:
    with patch("brand_voice_fetcher.requests.get") as mock_get:
        mock_get.side_effect = Exception("connection refused")
        result = fetch_brand_voice("https://error-test.example.com/brand.md")

    # On error, all sections are empty strings (graceful fallback)
    assert result["tagline"] == ""
    assert result["voice"] == ""


def test_caches_second_call() -> None:
    with patch("brand_voice_fetcher.requests.get") as mock_get:
        mock_get.return_value = _mock_resp(_SAMPLE_DOC)
        fetch_brand_voice("https://unique-url-for-cache-test.example.com/brand.md")
        fetch_brand_voice("https://unique-url-for-cache-test.example.com/brand.md")

    assert mock_get.call_count == 1


def test_empty_voice_url_not_called() -> None:
    with patch("brand_voice_fetcher.requests.get") as mock_get:
        result = fetch_brand_voice("")

    mock_get.assert_not_called()
    assert result == {}
