"""Tests for render_calendar — T8."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "social"))

from render_calendar import render_calendar


def test_t8_renders_both_tables(tmp_path: Path) -> None:
    today = date.today().isoformat()
    recent_pub = (date.today() - timedelta(days=5)).isoformat()
    old_pub = (date.today() - timedelta(days=60)).isoformat()

    schedule = [
        {"slug": "draft-a", "scheduled_date": today, "status": "draft", "linkedin_post_id": None, "facebook_post_id": None},
        {"slug": "draft-b", "scheduled_date": today, "status": "approved", "linkedin_post_id": None, "facebook_post_id": None},
        {"slug": "draft-c", "scheduled_date": today, "status": "draft", "linkedin_post_id": None, "facebook_post_id": None},
        {"slug": "recent-pub", "published_at": recent_pub, "status": "published", "linkedin_post_id": "urn:li:share:111", "facebook_post_id": "999_888"},
        {"slug": "old-pub", "published_at": old_pub, "status": "published", "linkedin_post_id": "urn:li:share:000", "facebook_post_id": "000_111"},
    ]

    output = tmp_path / "social-calendar.md"
    render_calendar(schedule, output)

    content = output.read_text(encoding="utf-8")
    assert "## Upcoming" in content
    assert "draft-a" in content
    assert "draft-b" in content
    assert "draft-c" in content
    assert "## Last 30 days" in content
    assert "recent-pub" in content
    # old published (60 days ago) should not appear in last-30-days
    assert "old-pub" not in content


def test_empty_schedule_renders_placeholder(tmp_path: Path) -> None:
    output = tmp_path / "social-calendar.md"
    render_calendar([], output)
    content = output.read_text(encoding="utf-8")
    assert "— | —" in content
