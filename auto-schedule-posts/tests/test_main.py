import datetime
import os
import sys

import frontmatter
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import main  # noqa: E402  (safe: the CLI entrypoint is behind __main__)


def _post(**meta):
    return frontmatter.loads("---\n" + "\n".join(f"{k}: {v}" for k, v in meta.items()) + "\n---\nbody")


def test_date_only_post_keeps_its_date():
    # Regression: the old else-branch wiped `date` when post_date was absent.
    d, src = main.pick_post_date(_post(date="2026-01-02"))
    assert str(d) == "2026-01-02" and src == "date"


def test_post_date_wins_over_date():
    d, src = main.pick_post_date(_post(date="2026-01-02", post_date="2025-05-05"))
    assert str(d) == "2025-05-05" and src == "post_date"


def test_no_dates_returns_none():
    assert main.pick_post_date(_post(title="x")) == (None, "date")


def test_cap_horizon_disabled_is_identity():
    dates = pd.bdate_range("2026-10-06", periods=5)
    assert list(main.cap_horizon(dates, 0)) == list(dates)


def test_cap_horizon_clamps_far_dates():
    today = datetime.date(2026, 10, 6)
    dates = pd.bdate_range("2026-10-06", periods=60, freq="C", weekmask="Mon")
    out = main.cap_horizon(dates, 90, today=today)
    assert max(out) == pd.Timestamp("2027-01-04")
    assert len(out) == 60 and min(out) == dates[0]


def test_end_to_end_dated_posts_are_scheduled_in_order(tmp_path):
    src, dst = tmp_path / "s", tmp_path / "d"
    src.mkdir(); dst.mkdir()
    (src / "a.md").write_text("---\ndate: 2026-03-01\n---\n" + "x" * 600)
    (src / "b.md").write_text("---\ndate: 2026-01-01\n---\n" + "x" * 600)
    main.auto_schedule_posts(str(src), str(dst), "Mon", "2026-10-06", "false")
    a = frontmatter.load(str(dst / "a.md"))["date"]
    b = frontmatter.load(str(dst / "b.md"))["date"]
    assert b < a  # earlier original date is scheduled first (needs date to survive)
