"""Orchestrator for social post generation: select → compose → generate image → write draft."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import date
from pathlib import Path

from yaml_io import load_yaml, save_yaml
from select_next_post import select_next_post
from compose_post import compose_post
from brand_voice_fetcher import fetch_brand_voice
from sam_client import generate_social_card
from render_calendar import render_calendar

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _set_output(key: str, value: str) -> None:
    """Write a key=value pair to $GITHUB_OUTPUT."""
    gh_output = os.environ.get("GITHUB_OUTPUT", "")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
    else:
        logger.info("GITHUB_OUTPUT not set; would emit: %s=%s", key, value[:120])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--posts-dir", default="_posts/en/")
    parser.add_argument("--drafts-dir", default="_social_drafts/")
    parser.add_argument("--schedule-path", default="_data/social_schedule.yml")
    parser.add_argument("--config-path", default="_data/social_config.yml")
    parser.add_argument("--target-slug", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log", default="INFO")
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log.upper())

    repo_root = Path.cwd()
    posts_dir = repo_root / args.posts_dir
    drafts_dir = repo_root / args.drafts_dir
    schedule_path = repo_root / args.schedule_path
    config_path = repo_root / args.config_path

    config = load_yaml(config_path)
    if isinstance(config, list):
        logger.error("social_config.yml must be a mapping, not a list")
        sys.exit(1)

    schedule = load_yaml(schedule_path)
    if not isinstance(schedule, list):
        schedule = []

    post = select_next_post(posts_dir, schedule, target_slug=args.target_slug)
    if post is None:
        logger.info("No eligible post found. Exiting.")
        _set_output("has_changes", "false")
        return

    voice_url = config.get("brand", {}).get("voice_url", "")
    brand_voice = fetch_brand_voice(voice_url) if voice_url else {}

    composed = compose_post(post, config, brand_voice)

    # Generate social card image
    api_key = os.environ.get("SMART_ASSETS_API_KEY", "")
    image_style = composed["linkedin"]["image_style"]
    brand_colors = {
        "primary": config.get("brand", {}).get("primary_color", "#0066CC"),
        "secondary": config.get("brand", {}).get("secondary_color", "#00CC66"),
        "accent": config.get("brand", {}).get("accent_color", "#FF6600"),
    }

    if api_key and not args.dry_run:
        card = generate_social_card(
            api_key=api_key,
            template_id=image_style,
            title=post["frontmatter"].get("title", ""),
            excerpt=post["frontmatter"].get("excerpt"),
            social_stat=post["frontmatter"].get("social_stat"),
            brand_colors=brand_colors,
        )
    else:
        card = {"landscape_url": "dry-run-placeholder-1200x627", "square_url": "dry-run-placeholder-1200x1200", "credits_used": 0}
        if not api_key:
            logger.warning("SMART_ASSETS_API_KEY not set — using placeholder image")

    today = date.today().isoformat()
    slug = post["slug"]
    draft_filename = f"{today}-{slug}.yml"
    draft_path = drafts_dir / draft_filename

    permalink = post["frontmatter"].get("permalink", f"/{slug}/")

    draft = {
        "slug": slug,
        "blog_path": post["blog_path"],
        "permalink": permalink,
        "scheduled_date": today,
        "status": "draft",
        "image": {"landscape_url": card["landscape_url"], "square_url": card["square_url"]},
        "linkedin": {"text": composed["linkedin"]["text"], "image_url": card["landscape_url"]},
        "facebook": {"text": composed["facebook"]["text"], "image_url": card["square_url"]},
    }

    drafts_dir.mkdir(parents=True, exist_ok=True)
    save_yaml(draft, draft_path)

    # Update schedule
    schedule.append({
        "slug": slug,
        "blog_path": post["blog_path"],
        "permalink": permalink,
        "scheduled_date": today,
        "status": "draft",
        "draft_path": str(draft_path.relative_to(repo_root)),
        "linkedin_post_id": None,
        "facebook_post_id": None,
        "published_at": None,
        "error": None,
    })
    save_yaml(schedule, schedule_path)

    render_calendar(schedule, repo_root / "social-calendar.md")

    _set_output("has_changes", "true")
    _set_output("slug", slug)
    _set_output("scheduled_date", today)
    _set_output("linkedin_preview", composed["linkedin"]["text"][:200].replace("\n", " "))
    _set_output("facebook_preview", composed["facebook"]["text"][:200].replace("\n", " "))
    _set_output("image_url", card["landscape_url"])

    logger.info("Draft written: %s", draft_path)


if __name__ == "__main__":
    main()
