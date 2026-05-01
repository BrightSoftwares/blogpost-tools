"""Tests for publish_to_linkedin — T9, T10, T11."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "social"))

from linkedin_publish import publish_to_linkedin


def _mock_resp(status: int, body: dict | None = None, headers: dict | None = None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.ok = status < 400
    resp.json.return_value = body or {}
    resp.headers = headers or {}
    resp.raise_for_status = MagicMock(side_effect=None if status < 400 else Exception(f"HTTP {status}"))
    return resp


# T9 — happy path: initializeUpload + PUT + POST all succeed
def test_t9_happy_path() -> None:
    init_body = {"value": {"uploadUrl": "https://upload.example.com/img", "image": "urn:li:image:abc123"}}
    img_bytes = b"fakeimagebytes"
    post_headers = {"x-restli-id": "urn:li:share:999"}

    with patch("linkedin_publish.requests.post") as mock_post, \
         patch("linkedin_publish.requests.get") as mock_get, \
         patch("linkedin_publish.requests.put") as mock_put:

        mock_post.side_effect = [
            _mock_resp(200, init_body),
            _mock_resp(201, {}, post_headers),
        ]
        mock_get.return_value = _mock_resp(200)
        mock_get.return_value.content = img_bytes
        mock_get.return_value.raise_for_status = MagicMock()
        mock_put.return_value = _mock_resp(201)

        urn = publish_to_linkedin(
            access_token="token123",
            org_urn="urn:li:organization:12345",
            text="Hello LinkedIn!",
            image_url="https://example.com/image.jpg",
        )

    assert urn == "urn:li:share:999"


# T10 — 401 on /rest/posts → raises with ACCESS TOKEN EXPIRED
def test_t10_expired_token_on_post() -> None:
    init_body = {"value": {"uploadUrl": "https://upload.example.com/img", "image": "urn:li:image:abc123"}}
    img_bytes = b"fakeimagebytes"

    with patch("linkedin_publish.requests.post") as mock_post, \
         patch("linkedin_publish.requests.get") as mock_get, \
         patch("linkedin_publish.requests.put") as mock_put:

        mock_post.side_effect = [
            _mock_resp(200, init_body),
            _mock_resp(401, {}),
        ]
        mock_get.return_value = _mock_resp(200)
        mock_get.return_value.content = img_bytes
        mock_get.return_value.raise_for_status = MagicMock()
        mock_put.return_value = _mock_resp(201)

        with pytest.raises(RuntimeError, match="ACCESS TOKEN EXPIRED"):
            publish_to_linkedin(
                access_token="expired",
                org_urn="urn:li:organization:12345",
                text="Hello!",
                image_url="https://example.com/image.jpg",
            )


# T11 — dry_run=True → no network calls; returns dry-run-<uuid>
def test_t11_dry_run() -> None:
    with patch("linkedin_publish.requests.post") as mock_post, \
         patch("linkedin_publish.requests.get") as mock_get, \
         patch("linkedin_publish.requests.put") as mock_put:

        urn = publish_to_linkedin(
            access_token="token",
            org_urn="urn:li:organization:12345",
            text="Hello!",
            image_url="https://example.com/image.jpg",
            dry_run=True,
        )

    assert urn.startswith("dry-run-")
    mock_post.assert_not_called()
    mock_get.assert_not_called()
    mock_put.assert_not_called()
