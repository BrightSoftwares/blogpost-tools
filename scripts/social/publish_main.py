"""Publish approved social drafts to LinkedIn and Facebook."""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
from datetime import date
from pathlib import Path

from yaml_io import load_yaml, save_yaml
from linkedin_publish import publish_to_linkedin
from facebook_publish import publish_to_facebook
from render_calendar import render_calendar

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _set_output(key: str, value: str) -> None:
    gh_output = os.environ.get("GITHUB_OUTPUT", "")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
    else:
        logger.info("GITHUB_OUTPUT not set; would emit: %s=%s", key, value[:120])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drafts-dir", default="_social_drafts/")
    parser.add_argument("--published-dir", default="_social_published/")
    parser.add_argument("--schedule-path", default="_data/social_schedule.yml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log", default="INFO")
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log.upper())

    repo_root = Path.cwd()
    drafts_dir = repo_root / args.drafts_dir
    published_dir = repo_root / args.published_dir
    schedule_path = repo_root / args.schedule_path

    li_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    li_urn = os.environ.get("LINKEDIN_ORG_URN", "")
    fb_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    fb_page = os.environ.get("FACEBOOK_PAGE_ID", "")

    if not args.dry_run:
        missing = [k for k, v in {
            "LINKEDIN_ACCESS_TOKEN": li_token,
            "LINKEDIN_ORG_URN": li_urn,
            "FACEBOOK_PAGE_ACCESS_TOKEN": fb_token,
            "FACEBOOK_PAGE_ID": fb_page,
        }.items() if not v]
        if missing:
            logger.error("Missing required env vars: %s", ", ".join(missing))
            sys.exit(1)

    approved = sorted(drafts_dir.glob("*.yml")) if drafts_dir.exists() else []
    approved = [p for p in approved if load_yaml(p).get("status") == "approved"]

    if not approved:
        logger.info("No approved drafts found. Exiting.")
        _set_output("published_count", "0")
        return

    schedule = load_yaml(schedule_path)
    if not isinstance(schedule, list):
        schedule = []

    published_dir.mkdir(parents=True, exist_ok=True)
    published_slugs = []
    errors = []

    for draft_path in approved:
        draft = load_yaml(draft_path)
        slug = draft.get("slug", draft_path.stem)
        logger.info("Publishing: %s", slug)

        try:
            li_post_id = publish_to_linkedin(
                access_token=li_token,
                org_urn=li_urn,
                text=draft["linkedin"]["text"],
                image_url=draft["linkedin"]["image_url"],
                dry_run=args.dry_run,
            )
        except Exception as exc:
            logger.error("LinkedIn publish failed for %s: %s", slug, exc)
            errors.append(f"{slug}: LinkedIn: {exc}")
            continue

        try:
            fb_post_id = publish_to_facebook(
                page_access_token=fb_token,
                page_id=fb_page,
                text=draft["facebook"]["text"],
                image_url=draft["facebook"]["image_url"],
                dry_run=args.dry_run,
            )
        except Exception as exc:
            logger.error("Facebook publish failed for %s: %s", slug, exc)
            errors.append(f"{slug}: Facebook: {exc}")
            continue

        today = date.today().isoformat()
        draft["status"] = "published"
        draft["linkedin_post_id"] = li_post_id
        draft["facebook_post_id"] = fb_post_id
        draft["published_at"] = today

        dest = published_dir / draft_path.name
        save_yaml(draft, dest)
        draft_path.unlink()

        for entry in schedule:
            if entry.get("slug") == slug:
                entry["status"] = "published"
                entry["linkedin_post_id"] = li_post_id
                entry["facebook_post_id"] = fb_post_id
                entry["published_at"] = today
                entry["draft_path"] = str(dest.relative_to(repo_root))
                entry["error"] = None
                break

        published_slugs.append(slug)
        logger.info("Published %s — LinkedIn: %s | Facebook: %s", slug, li_post_id, fb_post_id)

    save_yaml(schedule, schedule_path)
    render_calendar(schedule, repo_root / "social-calendar.md")

    _set_output("published_count", str(len(published_slugs)))
    _set_output("published_slugs", ",".join(published_slugs))
    if errors:
        _set_output("errors", "; ".join(errors))

    if errors:
        logger.error("Publish completed with %d error(s): %s", len(errors), errors)
        sys.exit(1)

    logger.info("Published %d post(s): %s", len(published_slugs), published_slugs)


if __name__ == "__main__":
    main()
