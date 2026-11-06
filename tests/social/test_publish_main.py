"""publish_main: LinkedIn-only drafts, and no duplicate LinkedIn post when Facebook fails."""
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "social"))
import publish_main  # noqa: E402


def _setup(tmp_path, draft, monkeypatch):
    (tmp_path / "_social_drafts").mkdir()
    (tmp_path / "_social_drafts" / "d.yml").write_text(yaml.safe_dump(draft))
    (tmp_path / "_data").mkdir()
    (tmp_path / "_data" / "social_schedule.yml").write_text(yaml.safe_dump([{"slug": "s", "status": "approved"}]))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "t")
    monkeypatch.setenv("LINKEDIN_ORG_URN", "u")
    monkeypatch.delenv("FACEBOOK_PAGE_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("FACEBOOK_PAGE_ID", raising=False)
    monkeypatch.setattr(sys, "argv", ["publish_main"])


def _draft(with_fb):
    d = {"slug": "s", "status": "approved", "linkedin": {"text": "x", "image_url": "i"}}
    if with_fb:
        d["facebook"] = {"text": "y", "image_url": "i"}
    return d


def test_linkedin_only_needs_no_facebook_credentials(tmp_path, monkeypatch):
    _setup(tmp_path, _draft(False), monkeypatch)
    calls = []
    monkeypatch.setattr(publish_main, "publish_to_linkedin", lambda **k: calls.append("li") or "urn:li:1")
    monkeypatch.setattr(publish_main, "publish_to_facebook", lambda **k: pytest.fail("facebook must not be called"))
    publish_main.main()
    assert calls == ["li"]
    assert not (tmp_path / "_social_drafts" / "d.yml").exists()
    assert (tmp_path / "_social_published" / "d.yml").exists()


def test_facebook_failure_does_not_leave_draft_to_be_reposted(tmp_path, monkeypatch):
    _setup(tmp_path, _draft(True), monkeypatch)
    monkeypatch.setenv("FACEBOOK_PAGE_ACCESS_TOKEN", "f")
    monkeypatch.setenv("FACEBOOK_PAGE_ID", "p")
    monkeypatch.setattr(publish_main, "publish_to_linkedin", lambda **k: "urn:li:1")

    def boom(**k):
        raise RuntimeError("token expired")

    monkeypatch.setattr(publish_main, "publish_to_facebook", boom)
    with pytest.raises(SystemExit):  # the job still goes red so the Facebook problem is seen
        publish_main.main()
    assert not (tmp_path / "_social_drafts" / "d.yml").exists(), "draft must be closed out once LinkedIn is live"
    done = yaml.safe_load((tmp_path / "_social_published" / "d.yml").read_text())
    assert done["linkedin_post_id"] == "urn:li:1" and done["facebook_post_id"] is None


def test_dry_run_changes_nothing(tmp_path, monkeypatch):
    """Regression: a dry run used to move the draft, flip it to published and edit the schedule,
    and the workflow then pushed that to master without any post having been sent."""
    _setup(tmp_path, _draft(False), monkeypatch)
    monkeypatch.setattr(sys, "argv", ["publish_main", "--dry-run"])
    seen = {}
    monkeypatch.setattr(publish_main, "publish_to_linkedin", lambda **k: seen.update(k) or "dry-run-id")
    before_sched = (tmp_path / "_data" / "social_schedule.yml").read_text()
    publish_main.main()
    assert seen["dry_run"] is True
    assert (tmp_path / "_social_drafts" / "d.yml").exists()
    assert not (tmp_path / "_social_published").exists()
    assert (tmp_path / "_data" / "social_schedule.yml").read_text() == before_sched
    assert not (tmp_path / "social-calendar.md").exists()


def test_already_published_draft_is_not_posted_again(tmp_path, monkeypatch):
    """Regression: the workflow never committed the draft deletion, so 2 approved drafts of 2026-10-30
    sat next to their _social_published copies and every later run would re-post them."""
    _setup(tmp_path, _draft(False), monkeypatch)
    (tmp_path / "_social_published").mkdir()
    (tmp_path / "_social_published" / "d.yml").write_text("slug: s\nstatus: published\n")
    monkeypatch.setattr(publish_main, "publish_to_linkedin", lambda **k: pytest.fail("must not post twice"))
    publish_main.main()
    assert not (tmp_path / "_social_drafts" / "d.yml").exists()
    assert "published" in (tmp_path / "_social_published" / "d.yml").read_text()
