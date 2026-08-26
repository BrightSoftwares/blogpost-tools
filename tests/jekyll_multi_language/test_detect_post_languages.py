"""Tests for detect_post_languages.py's markdown file discovery.

Regression (found 2026-08-24 migrating keke.li, `sp14-5-10-markdown-glob-gap`):
`scan_collection` globbed `*.md` only, so Jekyll's default `.markdown`-extension
scaffold posts (e.g. the `jekyll new` starter post) were silently invisible to
both this detector and `migrate_jekyll_repo.py` (which reuses `scan_collection`)
— not COMPLIANT, not flagged, not counted at all. A repo could be under-reported
as fully migrated when a `.markdown` file inside it still needed attention.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "jekyll-multi-language-tools"))

import detect_post_languages  # noqa: E402
from detect_post_languages import _md_files, scan_collection  # noqa: E402


POST_BODY = """---
title: "Welcome"
lang: en
---
This is a short English welcome post used only to exercise the file-discovery
glob, not the language detector itself.
"""


class TestMdFilesHelper:
    def test_finds_both_md_and_markdown_extensions(self, tmp_path):
        (tmp_path / "a.md").write_text("md file", encoding="utf-8")
        (tmp_path / "b.markdown").write_text("markdown file", encoding="utf-8")
        (tmp_path / "c.txt").write_text("not markdown", encoding="utf-8")

        found = _md_files(tmp_path)

        assert [p.name for p in found] == ["a.md", "b.markdown"]

    def test_empty_directory_returns_empty_list(self, tmp_path):
        assert _md_files(tmp_path) == []


class TestScanCollectionMarkdownExtension:
    def test_flat_markdown_extension_file_is_detected_not_silently_skipped(self, tmp_path):
        site_dir = tmp_path
        posts_dir = site_dir / "_posts"
        posts_dir.mkdir()
        # Jekyll's default `jekyll new` scaffold extension — the exact case
        # that was previously invisible to scan_collection entirely.
        (posts_dir / "2022-05-16-welcome-to-jekyll.markdown").write_text(
            POST_BODY, encoding="utf-8"
        )

        entries = scan_collection(site_dir, "_posts", ["en", "fr"])

        assert len(entries) == 1
        entry = entries[0]
        assert entry.filename == "2022-05-16-welcome-to-jekyll.markdown"
        # Has `lang: en` frontmatter and isn't yet in an `en/` subfolder ->
        # NEEDS_MOVE, not silently absent from the report.
        assert entry.status == "NEEDS_MOVE"
        assert entry.target_lang == "en"

    def test_already_migrated_markdown_extension_file_is_compliant(self, tmp_path):
        site_dir = tmp_path
        lang_dir = site_dir / "_posts" / "en"
        lang_dir.mkdir(parents=True)
        (lang_dir / "2022-05-16-welcome-to-jekyll.markdown").write_text(
            POST_BODY, encoding="utf-8"
        )

        entries = scan_collection(site_dir, "_posts", ["en", "fr"])

        assert len(entries) == 1
        assert entries[0].status == "COMPLIANT"

    def test_mixed_md_and_markdown_files_both_counted(self, tmp_path):
        site_dir = tmp_path
        posts_dir = site_dir / "_posts"
        posts_dir.mkdir()
        (posts_dir / "2026-01-01-post-one.md").write_text(POST_BODY, encoding="utf-8")
        (posts_dir / "2026-01-02-post-two.markdown").write_text(POST_BODY, encoding="utf-8")

        entries = scan_collection(site_dir, "_posts", ["en", "fr"])

        assert {e.filename for e in entries} == {
            "2026-01-01-post-one.md",
            "2026-01-02-post-two.markdown",
        }


NO_FRONTMATTER_BODY = """---
categories: [Something]
---
Some short product blurb with no lang field at all.
"""


class TestOutOfScopeLanguageIsNeverAutoMigrated:
    """Regression (found 2026-08-26 migrating modabyflora-corporate and
    joyousbyflora-posts, 6 instances across 2 repos): a confident langdetect
    result outside the declared --languages list (e.g. 'it'/'de'/'no' from a
    short French product blurb) used to be reported NEEDS_FRONTMATTER, which
    migrate_jekyll_repo.py auto-applies — silently creating an out-of-scope
    <collection>/<lang>/ folder for content that was actually French. Any
    detected language not in the declared list must downgrade to UNKNOWN,
    which migrate_jekyll_repo.py always skips.
    """

    def test_confident_out_of_scope_language_becomes_unknown(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            detect_post_languages,
            "detect_language_content",
            lambda text: ("it", 0.95),
        )
        site_dir = tmp_path
        posts_dir = site_dir / "_products"
        posts_dir.mkdir()
        (posts_dir / "short-french-product.md").write_text(
            NO_FRONTMATTER_BODY, encoding="utf-8"
        )

        entries = scan_collection(site_dir, "_products", ["en", "fr"])

        assert len(entries) == 1
        entry = entries[0]
        assert entry.status == "UNKNOWN"
        assert entry.detected_lang == "it"
        assert any("outside the declared" in n for n in entry.notes)

    def test_confident_in_scope_language_still_needs_frontmatter(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            detect_post_languages,
            "detect_language_content",
            lambda text: ("fr", 0.95),
        )
        site_dir = tmp_path
        posts_dir = site_dir / "_products"
        posts_dir.mkdir()
        (posts_dir / "clear-french-product.md").write_text(
            NO_FRONTMATTER_BODY, encoding="utf-8"
        )

        entries = scan_collection(site_dir, "_products", ["en", "fr"])

        assert len(entries) == 1
        assert entries[0].status == "NEEDS_FRONTMATTER"
        assert entries[0].target_lang == "fr"
