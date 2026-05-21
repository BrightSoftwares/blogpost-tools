"""Publish posts to a LinkedIn company page via the LinkedIn REST API.

Supports two post types:
- Single image: publish_to_linkedin()
- PDF carousel: publish_carousel_to_linkedin()
"""

from __future__ import annotations

import logging
import time
import urllib.parse
import uuid

import requests

logger = logging.getLogger(__name__)

_LI_BASE = "https://api.linkedin.com/rest"
_LI_VERSION = "202404"

_DOCUMENT_POLL_INTERVAL_S = 2
_DOCUMENT_POLL_MAX_S = 60


def _li_headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": _LI_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }


def _raise_on_token_expiry(resp: requests.Response) -> None:
    if resp.status_code == 401:
        raise RuntimeError(
            "ACCESS TOKEN EXPIRED — refresh LinkedIn access token via Developer Portal"
        )


def _raise_on_duplicate(resp: requests.Response) -> str | None:
    """If the response is a duplicate-post 422, return the existing URN or raise."""
    if resp.status_code == 422:
        body = resp.json()
        if "DUPLICATE_POST" in str(body):
            logger.warning("LinkedIn DUPLICATE_POST: %s", body)
            existing = resp.headers.get("x-restli-id", "")
            if existing:
                return existing
            raise RuntimeError(f"LinkedIn duplicate post, no URN available: {body}")
    return None


def publish_to_linkedin(
    access_token: str,
    org_urn: str,
    text: str,
    image_url: str,
    dry_run: bool = False,
) -> str:
    """Publish a post with a single image to a LinkedIn company page.

    Args:
        access_token: LinkedIn OAuth2 bearer token with w_organization_social scope.
        org_urn: Organization URN, e.g. 'urn:li:organization:12345678'.
        text: Post body (≤ 3000 chars).
        image_url: Publicly reachable image URL (1200x627 recommended).
        dry_run: If True, log payloads and return a fake URN without making API calls.

    Returns:
        The LinkedIn post URN string.
    """
    if dry_run:
        urn = f"dry-run-{uuid.uuid4()}"
        logger.info(
            "[DRY RUN] LinkedIn post payload: org=%s text_len=%d image=%s urn=%s",
            org_urn, len(text), image_url, urn,
        )
        return urn

    headers = _li_headers(access_token)

    # Step 1: Initialize image upload
    init_resp = requests.post(
        f"{_LI_BASE}/images?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": org_urn}},
        timeout=30,
    )
    _raise_on_token_expiry(init_resp)
    init_resp.raise_for_status()
    upload_data = init_resp.json()["value"]
    upload_url: str = upload_data["uploadUrl"]
    image_urn: str = upload_data["image"]

    # Step 2: Fetch image bytes and upload
    try:
        img_resp = requests.get(image_url, timeout=30)
        img_resp.raise_for_status()
    except Exception as exc:
        raise RuntimeError(f"Could not fetch image from {image_url}: {exc}") from exc

    put_resp = requests.put(
        upload_url,
        data=img_resp.content,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=60,
    )
    put_resp.raise_for_status()

    # Step 3: Create the post
    post_payload = {
        "author": org_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED"},
        "content": {"media": {"id": image_urn}},
        "lifecycleState": "PUBLISHED",
    }
    post_resp = requests.post(
        f"{_LI_BASE}/posts",
        headers=headers,
        json=post_payload,
        timeout=30,
    )
    _raise_on_token_expiry(post_resp)
    existing_urn = _raise_on_duplicate(post_resp)
    if existing_urn:
        return existing_urn
    post_resp.raise_for_status()

    return post_resp.headers.get("x-restli-id", "unknown-urn")


def publish_carousel_to_linkedin(
    access_token: str,
    org_urn: str,
    text: str,
    pdf_url: str,
    document_title: str,
    visibility: str = "PUBLIC",
    dry_run: bool = False,
) -> dict[str, str]:
    """Publish a PDF document as a LinkedIn carousel post.

    Carousels are rendered as swipeable slide decks by LinkedIn when posted as
    PDF documents via the Documents API. The PDF must have 3–300 pages.

    Upload sequence:
      1. POST /rest/documents?action=initializeUpload  → uploadUrl + documentUrn
      2. PUT uploadUrl  (binary PDF bytes, no auth header — pre-signed URL)
      3. Poll GET /rest/documents/{urn}  until status = AVAILABLE
      4. POST /rest/posts  with content.media.id = documentUrn

    Args:
        access_token: LinkedIn OAuth2 bearer token with w_organization_social scope.
        org_urn: Organization URN, e.g. 'urn:li:organization:12345678'.
        text: Post body (≤ 3000 chars). Appears above the carousel.
        pdf_url: Publicly reachable URL to the PDF file (≤ 100 MB, 3–300 pages).
        document_title: Title shown in the carousel header on LinkedIn (≤ 400 chars).
        visibility: "PUBLIC" or "CONNECTIONS" (default "PUBLIC").
        dry_run: If True, log payloads and return fake URNs without making API calls.

    Returns:
        Dict with keys:
            post_urn     — urn:li:share:… (the created post)
            document_urn — urn:li:document:… (the uploaded PDF asset)
    """
    if dry_run:
        doc_urn = f"urn:li:document:dry-run-{uuid.uuid4()}"
        post_urn = f"urn:li:share:dry-run-{uuid.uuid4()}"
        logger.info(
            "[DRY RUN] LinkedIn carousel: org=%s text_len=%d pdf=%s title=%r doc=%s post=%s",
            org_urn, len(text), pdf_url, document_title, doc_urn, post_urn,
        )
        return {"post_urn": post_urn, "document_urn": doc_urn}

    headers = _li_headers(access_token)

    # Step 1: Initialize document upload
    logger.info("Initializing LinkedIn document upload for %r", document_title)
    init_resp = requests.post(
        f"{_LI_BASE}/documents?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": org_urn}},
        timeout=30,
    )
    _raise_on_token_expiry(init_resp)
    init_resp.raise_for_status()
    upload_data = init_resp.json()["value"]
    upload_url: str = upload_data["uploadUrl"]
    document_urn: str = upload_data["document"]
    logger.info("Document URN assigned: %s", document_urn)

    # Step 2: Fetch PDF bytes from source URL
    logger.info("Fetching PDF from %s", pdf_url)
    try:
        pdf_resp = requests.get(pdf_url, timeout=60)
        pdf_resp.raise_for_status()
    except Exception as exc:
        raise RuntimeError(f"Could not fetch PDF from {pdf_url}: {exc}") from exc

    pdf_bytes = pdf_resp.content
    logger.info("PDF fetched: %d bytes", len(pdf_bytes))

    # Step 3: Upload PDF bytes to the pre-signed URL
    # Note: pre-signed upload URLs do NOT require Authorization header.
    logger.info("Uploading PDF to LinkedIn pre-signed URL")
    put_resp = requests.put(
        upload_url,
        data=pdf_bytes,
        headers={"Content-Type": "application/octet-stream"},
        timeout=120,
    )
    put_resp.raise_for_status()
    logger.info("PDF upload complete (HTTP %d)", put_resp.status_code)

    # Step 4: Poll until document is processed and AVAILABLE
    _wait_for_document_available(document_urn, headers)

    # Step 5: Create the carousel post
    logger.info("Creating LinkedIn post with carousel document")
    post_payload = {
        "author": org_urn,
        "commentary": text,
        "visibility": visibility,
        "distribution": {"feedDistribution": "MAIN_FEED"},
        "content": {
            "media": {
                "id": document_urn,
                "title": document_title,
            }
        },
        "lifecycleState": "PUBLISHED",
    }
    post_resp = requests.post(
        f"{_LI_BASE}/posts",
        headers=headers,
        json=post_payload,
        timeout=30,
    )
    _raise_on_token_expiry(post_resp)
    existing_urn = _raise_on_duplicate(post_resp)
    if existing_urn:
        logger.info("Carousel already posted (duplicate): %s", existing_urn)
        return {"post_urn": existing_urn, "document_urn": document_urn}
    if post_resp.status_code == 429:
        retry_after = post_resp.headers.get("Retry-After", "unknown")
        raise RuntimeError(
            f"LinkedIn rate limit reached (3 posts/day/org). "
            f"Retry after {retry_after} seconds. "
            f"Document URN preserved: {document_urn}"
        )
    post_resp.raise_for_status()

    post_urn = post_resp.headers.get("x-restli-id", "unknown-urn")
    logger.info("Carousel post created: %s", post_urn)
    return {"post_urn": post_urn, "document_urn": document_urn}


def _wait_for_document_available(
    document_urn: str,
    headers: dict,
    poll_interval_s: float = _DOCUMENT_POLL_INTERVAL_S,
    max_wait_s: float = _DOCUMENT_POLL_MAX_S,
) -> None:
    """Poll LinkedIn until the document finishes processing.

    LinkedIn processes uploaded PDFs asynchronously. Posting before the document
    reaches AVAILABLE status results in a 422. This function blocks until ready
    or raises on timeout.

    Args:
        document_urn: The document URN returned by initializeUpload.
        headers: Authenticated LinkedIn REST headers (without Content-Type for GET).
        poll_interval_s: Seconds between polls (default 2).
        max_wait_s: Maximum total wait in seconds (default 60).

    Raises:
        RuntimeError: If the document does not reach AVAILABLE within max_wait_s.
    """
    encoded_urn = urllib.parse.quote(document_urn, safe="")
    poll_url = f"{_LI_BASE}/documents/{encoded_urn}"
    get_headers = {k: v for k, v in headers.items() if k != "Content-Type"}

    deadline = time.monotonic() + max_wait_s
    attempt = 0
    while time.monotonic() < deadline:
        attempt += 1
        poll_resp = requests.get(poll_url, headers=get_headers, timeout=15)
        _raise_on_token_expiry(poll_resp)
        poll_resp.raise_for_status()

        status = poll_resp.json().get("status", "")
        logger.debug("Document poll attempt %d: status=%s", attempt, status)

        if status == "AVAILABLE":
            logger.info("Document AVAILABLE after %d poll(s)", attempt)
            return
        if status in ("FAILED", "PROCESSING_FAILED"):
            raise RuntimeError(
                f"LinkedIn document processing failed (status={status}): {document_urn}"
            )

        time.sleep(poll_interval_s)

    raise RuntimeError(
        f"LinkedIn document not AVAILABLE after {max_wait_s}s "
        f"(last status unknown, {attempt} polls). URN: {document_urn}"
    )
