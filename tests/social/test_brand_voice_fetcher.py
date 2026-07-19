"""Tests for brand_voice_fetcher."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "social"))

from brand_voice_fetcher import fetch_brand_voice, load_brand_voice_from_submodule

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


def test_load_from_submodule_maps_fields(tmp_path: Path) -> None:
    voice_dir = tmp_path / "_design-system" / "brand-voice"
    voice_dir.mkdir(parents=True)
    (voice_dir / "bright-softwares.json").write_text(
        json.dumps(
            {
                "tagline": "We turn your processes into machines",
                "voice_adjectives": ["Intelligent", "Trustworthy"],
                "pain_points": ["Too many manual processes eating time", "Other pain"],
            }
        ),
        encoding="utf-8",
    )

    result = load_brand_voice_from_submodule(tmp_path, "bright-softwares")

    assert result["tagline"] == "We turn your processes into machines"
    assert result["voice"] == "Intelligent, Trustworthy"
    assert result["default_pain_point"] == "Too many manual processes eating time"


def test_load_from_submodule_missing_file_returns_none(tmp_path: Path) -> None:
    assert load_brand_voice_from_submodule(tmp_path, "no-such-brand") is None


def test_load_from_submodule_empty_slug_returns_none(tmp_path: Path) -> None:
    assert load_brand_voice_from_submodule(tmp_path, "") is None


def test_load_from_submodule_malformed_json_returns_none(tmp_path: Path) -> None:
    voice_dir = tmp_path / "_design-system" / "brand-voice"
    voice_dir.mkdir(parents=True)
    (voice_dir / "broken.json").write_text("{not valid json", encoding="utf-8")

    assert load_brand_voice_from_submodule(tmp_path, "broken") is None


def test_load_from_submodule_non_dict_json_returns_none(tmp_path: Path) -> None:
    """Valid JSON but wrong shape (e.g. an array) must degrade gracefully, not crash."""
    voice_dir = tmp_path / "_design-system" / "brand-voice"
    voice_dir.mkdir(parents=True)
    (voice_dir / "wrong-shape.json").write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")

    assert load_brand_voice_from_submodule(tmp_path, "wrong-shape") is None


def test_load_from_submodule_rejects_path_traversal(tmp_path: Path) -> None:
    """A malicious/malformed slug (e.g. from a compromised caller-repo config)
    must never escape _design-system/brand-voice/."""
    secret = tmp_path / "outside-secret.json"
    secret.write_text(json.dumps({"tagline": "leaked"}), encoding="utf-8")

    for bad_slug in ("../outside-secret", "../../outside-secret", "/etc/passwd", "a/b", "a\\b"):
        assert load_brand_voice_from_submodule(tmp_path, bad_slug) is None
