"""Render social-calendar.md from social_schedule.yml."""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

_PUBLISHED_WINDOW_DAYS = 30


def _li_url(entry: dict) -> str:
    pid = entry.get("linkedin_post_id")
    return f"[{pid}](https://www.linkedin.com/feed/update/{pid}/)" if pid else "—"


def _fb_url(entry: dict) -> str:
    pid = entry.get("facebook_post_id")
    return f"[{pid}](https://www.facebook.com/{pid})" if pid else "—"


def _table_rows(entries: list[dict]) -> str:
    rows = []
    for e in entries:
        rows.append(
            f"| {e.get('scheduled_date', '')} "
            f"| {e.get('slug', '')} "
            f"| {e.get('status', '')} "
            f"| {_li_url(e)} "
            f"| {_fb_url(e)} |"
        )
    return "\n".join(rows)


def render_calendar(schedule: list[dict], output_path: Path) -> None:
    """Render social-calendar.md from the social schedule list.

    Args:
        schedule: List of schedule entry dicts (from social_schedule.yml).
        output_path: Path to write the calendar markdown file.
    """
    now = datetime.now(tz=timezone.utc)
    today = now.date()
    cutoff = today - timedelta(days=_PUBLISHED_WINDOW_DAYS)

    upcoming = [
        e for e in schedule
        if e.get("status") in ("draft", "approved")
        and str(e.get("scheduled_date", "")) >= str(today)
    ]
    recent = [
        e for e in schedule
        if e.get("status") == "published"
        and str(e.get("published_at", "")) >= str(cutoff)
    ]

    header = "| Date | Slug | Status | LinkedIn | Facebook |"
    sep = "| ---- | ---- | ------ | -------- | -------- |"

    lines = [
        "# Social Publishing Calendar",
        f"_Last updated: {now.strftime('%Y-%m-%d %H:%M')} UTC_",
        "",
        "## Upcoming",
        header,
        sep,
        _table_rows(upcoming) if upcoming else "| — | — | — | — | — |",
        "",
        f"## Last {_PUBLISHED_WINDOW_DAYS} days",
        header,
        sep,
        _table_rows(recent) if recent else "| — | — | — | — | — |",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Calendar written to %s", output_path)
