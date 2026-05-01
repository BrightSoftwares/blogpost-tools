"""Tests for publish_to_facebook — T12, T13, T14."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "social"))

from facebook_publish import publish_to_facebook


def _mock_resp(status: int, body: dict | None = None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.ok = status < 400
    resp.json.return_value = body or {}
    resp.text = str(body or {})
    resp.raise_for_status = MagicMock(side_effect=None if status < 400 else Exception(f"HTTP {status}"))
    return resp


# T12 — happy path: photo upload + feed post succeed
def test_t12_happy_path() -> None:
    with patch("facebook_publish.requests.post") as mock_post:
        mock_post.side_effect = [
            _mock_resp(200, {"id": "photo_abc"}),
            _mock_resp(200, {"id": "page_123_post_456"}),
        ]

        post_id = publish_to_facebook(
            page_access_token="token",
            page_id="page_123",
            text="Hello Facebook!",
            image_url="https://example.com/image.jpg",
        )

    assert post_id == "page_123_post_456"
    assert mock_post.call_count == 2


# T13 — error code 190 on photo upload → raises FACEBOOK PAGE TOKEN EXPIRED
def test_t13_expired_token() -> None:
    with patch("facebook_publish.requests.post") as mock_post:
        mock_post.return_value = _mock_resp(400, {"error": {"code": 190, "message": "Invalid OAuth access token"}})

        with pytest.raises(RuntimeError, match="FACEBOOK PAGE TOKEN EXPIRED"):
            publish_to_facebook(
                page_access_token="expired",
                page_id="page_123",
                text="Hello!",
                image_url="https://example.com/image.jpg",
            )


# T14 — dry_run=True → no network calls; returns dry-run-<uuid>
def test_t14_dry_run() -> None:
    with patch("facebook_publish.requests.post") as mock_post:
        post_id = publish_to_facebook(
            page_access_token="token",
            page_id="page_123",
            text="Hello!",
            image_url="https://example.com/image.jpg",
            dry_run=True,
        )

    assert post_id.startswith("dry-run-")
    mock_post.assert_not_called()
