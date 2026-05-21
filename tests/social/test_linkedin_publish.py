"""Tests for LinkedIn publish functions — T9-T11 (image) + T12-T20 (carousel)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "social"))

from linkedin_publish import publish_carousel_to_linkedin, publish_to_linkedin


def _mock_resp(status: int, body: dict | None = None, headers: dict | None = None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.ok = status < 400
    resp.json.return_value = body or {}
    resp.headers = headers or {}
    resp.raise_for_status = MagicMock(
        side_effect=None if status < 400 else Exception(f"HTTP {status}")
    )
    resp.content = b""
    return resp


# ---------------------------------------------------------------------------
# T9-T11: publish_to_linkedin (single image) — existing behaviour preserved
# ---------------------------------------------------------------------------

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
        get_resp = _mock_resp(200)
        get_resp.content = img_bytes
        get_resp.raise_for_status = MagicMock()
        mock_get.return_value = get_resp
        mock_put.return_value = _mock_resp(201)

        urn = publish_to_linkedin(
            access_token="token123",
            org_urn="urn:li:organization:12345",
            text="Hello LinkedIn!",
            image_url="https://example.com/image.jpg",
        )

    assert urn == "urn:li:share:999"


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
        get_resp = _mock_resp(200)
        get_resp.content = img_bytes
        get_resp.raise_for_status = MagicMock()
        mock_get.return_value = get_resp
        mock_put.return_value = _mock_resp(201)

        with pytest.raises(RuntimeError, match="ACCESS TOKEN EXPIRED"):
            publish_to_linkedin(
                access_token="expired",
                org_urn="urn:li:organization:12345",
                text="Hello!",
                image_url="https://example.com/image.jpg",
            )


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


# ---------------------------------------------------------------------------
# T12-T20: publish_carousel_to_linkedin (PDF document carousel)
# ---------------------------------------------------------------------------

_ORG_URN = "urn:li:organization:12345"
_DOC_URN = "urn:li:document:D560abc123"
_POST_URN = "urn:li:share:777"
_INIT_BODY = {
    "value": {
        "uploadUrl": "https://upload.li.example.com/doc/presigned",
        "document": _DOC_URN,
    }
}
_PDF_BYTES = b"%PDF-1.4 fakepdfbytes"


def _make_carousel_mocks(
    *,
    init_status: int = 200,
    put_status: int = 201,
    poll_statuses: list[dict] | None = None,
    post_status: int = 201,
    post_body: dict | None = None,
    post_headers: dict | None = None,
) -> tuple[MagicMock, MagicMock, MagicMock]:
    """Return (mock_post, mock_get, mock_put) configured for carousel flow."""
    if poll_statuses is None:
        poll_statuses = [{"status": "AVAILABLE"}]

    mock_post = MagicMock()
    mock_get = MagicMock()
    mock_put = MagicMock()

    # POST calls: initializeUpload + final post creation
    post_side_effects = [
        _mock_resp(init_status, _INIT_BODY),
        _mock_resp(post_status, post_body or {}, post_headers or {"x-restli-id": _POST_URN}),
    ]
    mock_post.side_effect = post_side_effects

    # GET calls: PDF fetch + poll(s)
    pdf_get = _mock_resp(200)
    pdf_get.content = _PDF_BYTES
    pdf_get.raise_for_status = MagicMock()

    poll_resps = [_mock_resp(200, body) for body in poll_statuses]
    mock_get.side_effect = [pdf_get] + poll_resps

    mock_put.return_value = _mock_resp(put_status)

    return mock_post, mock_get, mock_put


# T12 — happy path: all steps succeed, document becomes AVAILABLE on first poll
def test_t12_carousel_happy_path() -> None:
    mock_post, mock_get, mock_put = _make_carousel_mocks()

    with patch("linkedin_publish.requests.post", mock_post), \
         patch("linkedin_publish.requests.get", mock_get), \
         patch("linkedin_publish.requests.put", mock_put), \
         patch("linkedin_publish.time.sleep"):

        result = publish_carousel_to_linkedin(
            access_token="token",
            org_urn=_ORG_URN,
            text="Check out my carousel!",
            pdf_url="https://cloudinary.example.com/deck.pdf",
            document_title="My Carousel",
        )

    assert result["post_urn"] == _POST_URN
    assert result["document_urn"] == _DOC_URN
    assert mock_put.call_count == 1
    assert mock_post.call_count == 2


# T13 — dry_run: no network calls, returns fake URNs
def test_t13_carousel_dry_run() -> None:
    with patch("linkedin_publish.requests.post") as mock_post, \
         patch("linkedin_publish.requests.get") as mock_get, \
         patch("linkedin_publish.requests.put") as mock_put:

        result = publish_carousel_to_linkedin(
            access_token="token",
            org_urn=_ORG_URN,
            text="post text",
            pdf_url="https://example.com/deck.pdf",
            document_title="Dry Run Deck",
            dry_run=True,
        )

    assert result["post_urn"].startswith("urn:li:share:dry-run-")
    assert result["document_urn"].startswith("urn:li:document:dry-run-")
    mock_post.assert_not_called()
    mock_get.assert_not_called()
    mock_put.assert_not_called()


# T14 — 401 on initializeUpload → ACCESS TOKEN EXPIRED
def test_t14_carousel_expired_token_on_init() -> None:
    mock_post = MagicMock()
    mock_post.return_value = _mock_resp(401, {})

    with patch("linkedin_publish.requests.post", mock_post), \
         patch("linkedin_publish.requests.get"), \
         patch("linkedin_publish.requests.put"):

        with pytest.raises(RuntimeError, match="ACCESS TOKEN EXPIRED"):
            publish_carousel_to_linkedin(
                access_token="expired",
                org_urn=_ORG_URN,
                text="text",
                pdf_url="https://example.com/deck.pdf",
                document_title="Deck",
            )


# T15 — 401 on POST /rest/posts → ACCESS TOKEN EXPIRED
def test_t15_carousel_expired_token_on_post() -> None:
    mock_post, mock_get, mock_put = _make_carousel_mocks(
        post_status=401, post_headers={}
    )

    with patch("linkedin_publish.requests.post", mock_post), \
         patch("linkedin_publish.requests.get", mock_get), \
         patch("linkedin_publish.requests.put", mock_put), \
         patch("linkedin_publish.time.sleep"):

        with pytest.raises(RuntimeError, match="ACCESS TOKEN EXPIRED"):
            publish_carousel_to_linkedin(
                access_token="expired",
                org_urn=_ORG_URN,
                text="text",
                pdf_url="https://example.com/deck.pdf",
                document_title="Deck",
            )


# T16 — DUPLICATE_POST 422 → returns existing URN, no re-raise
def test_t16_carousel_duplicate_post() -> None:
    existing_urn = "urn:li:share:existing-456"
    dup_body = {"status": 422, "message": "DUPLICATE_POST detected"}
    mock_post, mock_get, mock_put = _make_carousel_mocks(
        post_status=422,
        post_body=dup_body,
        post_headers={"x-restli-id": existing_urn},
    )

    with patch("linkedin_publish.requests.post", mock_post), \
         patch("linkedin_publish.requests.get", mock_get), \
         patch("linkedin_publish.requests.put", mock_put), \
         patch("linkedin_publish.time.sleep"):

        result = publish_carousel_to_linkedin(
            access_token="token",
            org_urn=_ORG_URN,
            text="text",
            pdf_url="https://example.com/deck.pdf",
            document_title="Deck",
        )

    assert result["post_urn"] == existing_urn
    assert result["document_urn"] == _DOC_URN


# T17 — rate limit 429 → raises with retryAfter info and preserves document URN
def test_t17_carousel_rate_limit() -> None:
    rate_limit_resp = _mock_resp(429, {}, {"Retry-After": "86400"})
    rate_limit_resp.raise_for_status = MagicMock()

    mock_post = MagicMock()
    mock_get = MagicMock()
    mock_put = MagicMock()

    pdf_get = _mock_resp(200)
    pdf_get.content = _PDF_BYTES
    pdf_get.raise_for_status = MagicMock()
    poll_get = _mock_resp(200, {"status": "AVAILABLE"})
    mock_get.side_effect = [pdf_get, poll_get]

    mock_post.side_effect = [_mock_resp(200, _INIT_BODY), rate_limit_resp]
    mock_put.return_value = _mock_resp(201)

    with patch("linkedin_publish.requests.post", mock_post), \
         patch("linkedin_publish.requests.get", mock_get), \
         patch("linkedin_publish.requests.put", mock_put), \
         patch("linkedin_publish.time.sleep"):

        with pytest.raises(RuntimeError, match="rate limit"):
            publish_carousel_to_linkedin(
                access_token="token",
                org_urn=_ORG_URN,
                text="text",
                pdf_url="https://example.com/deck.pdf",
                document_title="Deck",
            )


# T18 — document processing takes multiple polls before AVAILABLE
def test_t18_carousel_polls_until_available() -> None:
    poll_statuses = [
        {"status": "PROCESSING"},
        {"status": "PROCESSING"},
        {"status": "AVAILABLE"},
    ]
    mock_post, mock_get, mock_put = _make_carousel_mocks(poll_statuses=poll_statuses)

    with patch("linkedin_publish.requests.post", mock_post), \
         patch("linkedin_publish.requests.get", mock_get), \
         patch("linkedin_publish.requests.put", mock_put), \
         patch("linkedin_publish.time.sleep") as mock_sleep:

        result = publish_carousel_to_linkedin(
            access_token="token",
            org_urn=_ORG_URN,
            text="text",
            pdf_url="https://example.com/deck.pdf",
            document_title="Deck",
        )

    # 1 PDF fetch + 3 polls = 4 GET calls
    assert mock_get.call_count == 4
    # sleep called twice (between PROCESSING polls)
    assert mock_sleep.call_count == 2
    assert result["post_urn"] == _POST_URN


# T19 — document never reaches AVAILABLE → timeout raises RuntimeError
def test_t19_carousel_document_poll_timeout() -> None:
    # Return PROCESSING indefinitely; _wait_for_document_available times out
    processing_resp = _mock_resp(200, {"status": "PROCESSING"})

    mock_post = MagicMock()
    mock_get = MagicMock()
    mock_put = MagicMock()

    pdf_get = _mock_resp(200)
    pdf_get.content = _PDF_BYTES
    pdf_get.raise_for_status = MagicMock()
    mock_get.side_effect = [pdf_get] + [processing_resp] * 50
    mock_post.return_value = _mock_resp(200, _INIT_BODY)
    mock_put.return_value = _mock_resp(201)

    with patch("linkedin_publish.requests.post", mock_post), \
         patch("linkedin_publish.requests.get", mock_get), \
         patch("linkedin_publish.requests.put", mock_put), \
         patch("linkedin_publish.time.sleep"), \
         patch("linkedin_publish.time.monotonic", side_effect=[0.0] + [9999.0] * 100):

        with pytest.raises(RuntimeError, match="not AVAILABLE"):
            publish_carousel_to_linkedin(
                access_token="token",
                org_urn=_ORG_URN,
                text="text",
                pdf_url="https://example.com/deck.pdf",
                document_title="Deck",
            )


# T20 — PDF fetch fails → RuntimeError with URL in message
def test_t20_carousel_pdf_fetch_failure() -> None:
    mock_post = MagicMock()
    mock_get = MagicMock()
    mock_put = MagicMock()

    mock_post.return_value = _mock_resp(200, _INIT_BODY)
    pdf_get = _mock_resp(404)
    pdf_get.raise_for_status = MagicMock(side_effect=Exception("404 Not Found"))
    mock_get.return_value = pdf_get

    with patch("linkedin_publish.requests.post", mock_post), \
         patch("linkedin_publish.requests.get", mock_get), \
         patch("linkedin_publish.requests.put", mock_put):

        with pytest.raises(RuntimeError, match="Could not fetch PDF"):
            publish_carousel_to_linkedin(
                access_token="token",
                org_urn=_ORG_URN,
                text="text",
                pdf_url="https://example.com/missing.pdf",
                document_title="Deck",
            )

    mock_put.assert_not_called()
