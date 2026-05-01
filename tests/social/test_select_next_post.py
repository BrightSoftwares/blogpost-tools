"""Tests for select_next_post — T1, T2, T3."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "social"))

from select_next_post import select_next_post


def _write_post(tmp_path: Path, filename: str, frontmatter: dict) -> Path:
    import yaml
    p = tmp_path / filename
    fm = yaml.dump(frontmatter, allow_unicode=True)
    p.write_text(f"---\n{fm}---\n\nBody text here.\n", encoding="utf-8")
    return p


# T1 — 3 posts, 1 already published → returns oldest of remaining 2
def test_t1_skips_already_scheduled(tmp_path: Path) -> None:
    _write_post(tmp_path, "2024-01-01-alpha.md", {"title": "Alpha", "auto_social": True, "permalink": "/en/alpha/"})
    _write_post(tmp_path, "2024-01-02-beta.md", {"title": "Beta", "auto_social": True, "permalink": "/en/beta/"})
    _write_post(tmp_path, "2024-01-03-gamma.md", {"title": "Gamma", "auto_social": True, "permalink": "/en/gamma/"})

    # _slug_from_path strips YYYY-MM-DD- prefix: "2024-01-01-alpha.md" → "alpha"
    schedule = [{"slug": "alpha", "status": "published"}]
    result = select_next_post(tmp_path, schedule)

    assert result is not None
    assert result["slug"] == "beta"


# T2 — all posts have auto_social: false → returns None
def test_t2_all_disabled(tmp_path: Path) -> None:
    _write_post(tmp_path, "2024-01-01-no-social.md", {"title": "No Social", "auto_social": False})
    _write_post(tmp_path, "2024-01-02-also-no.md", {"title": "Also No", "auto_social": False})

    result = select_next_post(tmp_path, [])
    assert result is None


# T3 — target_slug given → returns that exact post
def test_t3_target_slug(tmp_path: Path) -> None:
    _write_post(tmp_path, "2024-01-01-first.md", {"title": "First", "auto_social": True, "permalink": "/en/first/"})
    _write_post(tmp_path, "2024-06-15-target.md", {"title": "Target Post", "auto_social": True, "permalink": "/en/target/"})

    # _slug_from_path strips YYYY-MM-DD- prefix: "2024-06-15-target.md" → "target"
    result = select_next_post(tmp_path, [], target_slug="target")
    assert result is not None
    assert result["slug"] == "target"


# Edge: target_slug not found → FileNotFoundError
def test_target_slug_not_found(tmp_path: Path) -> None:
    _write_post(tmp_path, "2024-01-01-some-post.md", {"title": "Some", "auto_social": True})
    with pytest.raises(FileNotFoundError):
        select_next_post(tmp_path, [], target_slug="nonexistent-slug")


# Edge: empty posts dir → returns None
def test_empty_dir(tmp_path: Path) -> None:
    result = select_next_post(tmp_path, [])
    assert result is None
