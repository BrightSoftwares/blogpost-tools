"""Publish posts with photos to a Facebook Page via the Graph API."""

from __future__ import annotations

import logging
import time
import uuid

import requests

logger = logging.getLogger(__name__)

_FB_API = "https://graph.facebook.com/v19.0"


def publish_to_facebook(
    page_access_token: str,
    page_id: str,
    text: str,
    image_url: str,
    dry_run: bool = False,
) -> str:
    """Publish a post with photo to a Facebook Page.

    Args:
        page_access_token: Facebook Page long-lived access token.
        page_id: Facebook Page ID.
        text: Post message text.
        image_url: Publicly reachable image URL (must be accessible by Facebook).
        dry_run: If True, log payloads and return a fake post ID.

    Returns:
        The Facebook post ID string.
    """
    if dry_run:
        post_id = f"dry-run-{uuid.uuid4()}"
        logger.info("[DRY RUN] Facebook post payload: page=%s text_len=%d image=%s id=%s",
                    page_id, len(text), image_url, post_id)
        return post_id

    token = page_access_token

    # Step 1: Upload photo (unpublished)
    photo_resp = requests.post(
        f"{_FB_API}/{page_id}/photos",
        params={"url": image_url, "published": "false", "access_token": token},
        timeout=30,
    )
    _check_fb_error(photo_resp, image_url)
    photo_id = photo_resp.json()["id"]

    # Step 2: Publish feed post with attached photo
    feed_resp = requests.post(
        f"{_FB_API}/{page_id}/feed",
        params={
            "message": text,
            "attached_media[0]": f'{{"media_fbid":"{photo_id}"}}',
            "access_token": token,
        },
        timeout=30,
    )
    _check_fb_error(feed_resp, image_url)
    return feed_resp.json()["id"]


def _check_fb_error(resp: requests.Response, image_url: str = "") -> None:
    """Raise a descriptive RuntimeError on Facebook API error responses."""
    if resp.ok:
        return
    try:
        error = resp.json().get("error", {})
    except Exception:
        resp.raise_for_status()
        return

    code = error.get("code", 0)
    msg = error.get("message", resp.text)

    if code == 190:
        raise RuntimeError("FACEBOOK PAGE TOKEN EXPIRED — refresh via Graph API Explorer")
    if code == 100 and image_url:
        raise RuntimeError(
            f"Facebook error 100 — image URL may not be publicly reachable: {image_url}. "
            "Ensure Cloudinary visibility is 'public'."
        )
    if code == 17:
        # Rate limit — retry once after 60s
        logger.warning("Facebook rate limit hit (code 17), retrying after 60s")
        time.sleep(60)
        return  # caller retries
    raise RuntimeError(f"Facebook API error {code}: {msg}")
