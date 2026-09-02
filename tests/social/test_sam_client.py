"""Tests for sam_client.generate_social_card.

Regression coverage for the 2026-09-02 fix: the client used to send a
payload shape ({"template_id":..., "params": {...}, "generate_sizes": [...]})
that the live SAM API's DeterministicGenerationRequest schema has never
accepted, failing every call with HTTP 422 ("Field required: type") — see
sam_client.py's module docstring for the full root-cause writeup.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "social"))

from sam_client import _build_svg_variables, _wrap_lines, generate_social_card


def _mock_resp(status: int, body: dict | None = None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = body or {}
    resp.text = str(body or {})
    return resp


_BRAND_COLORS = {"primary": "#0066CC", "secondary": "#00CC66", "accent": "#FF6600"}


def test_wrap_lines_pads_to_max_lines() -> None:
    assert _wrap_lines("short", 3) == ["short", "", ""]


def test_wrap_lines_empty_text() -> None:
    assert _wrap_lines(None, 2) == ["", ""]


def test_wrap_lines_truncates_overflow_with_ellipsis() -> None:
    long_text = " ".join(["word"] * 40)
    lines = _wrap_lines(long_text, 2, max_chars=20)
    assert len(lines) == 2
    assert lines[-1].endswith("…") or lines[-1] != ""


def test_build_svg_variables_quote_card_shape() -> None:
    variables = _build_svg_variables(
        "quote-card", "A Title", "An excerpt", None, None, "Bright Softwares", _BRAND_COLORS
    )
    assert set(variables) == {
        "brand_name", "primary_color", "secondary_color", "accent_color",
        "title_line1", "title_line2", "title_line3",
        "excerpt_line1", "excerpt_line2",
    }
    assert variables["title_line1"] == "A Title"
    assert variables["brand_name"] == "Bright Softwares"


def test_build_svg_variables_stat_card_shape() -> None:
    variables = _build_svg_variables(
        "stat-card", "A Title", None, "74%", None, "Bright Softwares", _BRAND_COLORS
    )
    assert set(variables) == {
        "brand_name", "primary_color", "secondary_color", "accent_color",
        "stat", "stat_label", "title_line1", "title_line2",
    }
    assert variables["stat"] == "74%"


def test_build_svg_variables_question_hook_shape() -> None:
    variables = _build_svg_variables(
        "question-hook", "A Title", None, None, "Read more", "Bright Softwares", _BRAND_COLORS
    )
    assert set(variables) == {
        "brand_name", "primary_color", "secondary_color", "accent_color",
        "title_line1", "title_line2", "title_line3",
        "cta_line1", "cta_line2",
    }
    assert variables["cta_line1"] == "Read more"


# Regression: payload envelope must match DeterministicGenerationRequest
# (smart-assets-manager backend/app/schemas/deterministic.py) — top-level
# "type", data.template_id/data.variables, bool generate_sizes, custom_sizes.
def test_generate_social_card_sends_correct_payload_envelope() -> None:
    with patch("sam_client.requests.post") as mock_post:
        mock_post.return_value = _mock_resp(200, {
            "success": True,
            "assets": [
                {"width": 1200, "height": 627, "name": "1200x627", "url": "https://cdn/landscape.png"},
                {"width": 1200, "height": 1200, "name": "1200x1200", "url": "https://cdn/square.png"},
            ],
            "credits_charged": 0.25,
        })

        result = generate_social_card(
            api_key="k",
            template_id="quote-card",
            title="A Title",
            excerpt="An excerpt",
            social_stat=None,
            brand_colors=_BRAND_COLORS,
            brand_name="Bright Softwares",
        )

        sent = mock_post.call_args.kwargs["json"]
        assert sent["type"] == "svg"
        assert sent["data"]["template_id"] == "social-quote-card"
        assert isinstance(sent["data"]["variables"], dict)
        assert sent["generate_sizes"] is True
        assert "preset_name" not in sent  # would collide with custom_sizes (422 upstream)
        assert sent["custom_sizes"] == [
            {"width": 1200, "height": 627},
            {"width": 1200, "height": 1200},
        ]

        assert result["landscape_url"] == "https://cdn/landscape.png"
        assert result["square_url"] == "https://cdn/square.png"
        assert result["credits_used"] == 0.25


def test_generate_social_card_raises_on_422() -> None:
    with patch("sam_client.requests.post") as mock_post:
        mock_post.return_value = _mock_resp(422, {"detail": "Field required: type"})
        try:
            generate_social_card(
                api_key="k",
                template_id="quote-card",
                title="T",
                excerpt="E",
                social_stat=None,
                brand_colors=_BRAND_COLORS,
            )
            assert False, "expected RuntimeError"
        except RuntimeError as exc:
            assert "422" in str(exc)
