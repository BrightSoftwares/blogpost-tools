"""Publish posts to a LinkedIn company page via the LinkedIn REST API."""

from __future__ import annotations

import logging
import uuid

import requests

logger = logging.getLogger(__name__)

_LI_BASE = "https://api.linkedin.com/rest"
_LI_VERSION = "202404"


def _li_headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": _LI_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }


def publish_to_linkedin(
    access_token: str,
    org_urn: str,
    text: str,
    image_url: str,
    dry_run: bool = False,
) -> str:
    """Publish a post with image to a LinkedIn company page.

    Args:
        access_token: LinkedIn OAuth2 bearer token with w_organization_social scope.
        org_urn: Organization URN, e.g. 'urn:li:organization:12345678'.
        text: Post body (≤ 3000 chars).
        image_url: Publicly reachable image URL (1200x627 recommended).
        dry_run: If True, log payloads and return a fake URN.

    Returns:
        The LinkedIn post URN string.
    """
    if dry_run:
        urn = f"dry-run-{uuid.uuid4()}"
        logger.info("[DRY RUN] LinkedIn post payload: org=%s text_len=%d image=%s urn=%s",
                    org_urn, len(text), image_url, urn)
        return urn

    headers = _li_headers(access_token)

    # Step 1: Initialize image upload
    init_resp = requests.post(
        f"{_LI_BASE}/images?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": org_urn}},
        timeout=30,
    )
    if init_resp.status_code == 401:
        raise RuntimeError("ACCESS TOKEN EXPIRED — refresh LinkedIn access token via Developer Portal")
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
    if post_resp.status_code == 401:
        raise RuntimeError("ACCESS TOKEN EXPIRED — refresh LinkedIn access token via Developer Portal")
    if post_resp.status_code == 422:
        body = post_resp.json()
        if "DUPLICATE_POST" in str(body):
            logger.warning("LinkedIn DUPLICATE_POST: %s", body)
            existing = post_resp.headers.get("x-restli-id", "")
            if existing:
                return existing
            raise RuntimeError(f"LinkedIn duplicate post, no URN available: {body}")
    post_resp.raise_for_status()

    return post_resp.headers.get("x-restli-id", "unknown-urn")
