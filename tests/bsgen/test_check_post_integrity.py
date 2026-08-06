"""Tests for check_post_integrity.py — the final sweep before a post can be
trusted as publish-ready.

Regression (found 2026-08-06, human reviewer feedback on a live draft): a
STAT callout that failed validation was left as a raw ```bsgen:callout```
fence, and hand-written links with a guessed publish date pointed at posts
that didn't exist at that URL. Neither issue stopped the pipeline or was
otherwise surfaced anywhere a human would see it before images were reviewed.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "bsgen"))

from check_post_integrity import (  # noqa: E402
    check_duplicate_topic,
    check_internal_links,
    find_raw_bsgen_leaks,
    normalize_path,
    process,
)

SITE_URL = "https://bright-softwares.com"


class TestFindRawBsgenLeaks:
    def test_clean_post_has_no_leaks(self):
        content = "---\ntitle: x\n---\n\nJust prose. No fences.\n"
        assert find_raw_bsgen_leaks(content) == []

    def test_unprocessed_fence_is_flagged(self):
        content = "---\ntitle: x\n---\n\n```bsgen:callout\ntype: STAT\ncontent: \"x\"\n```\n"
        issues = find_raw_bsgen_leaks(content)
        assert len(issues) == 1
        assert "bsgen:callout" in issues[0]

    def test_expected_asset_comments_are_not_flagged(self):
        # These are the comments process_assets.py itself intentionally
        # writes (type badge, placeholder note, render_mode marker) — never
        # a leak.
        content = (
            "<!-- bsgen:asset placeholder | id=x | brand=bright-softwares -->\n"
            "<!-- bsgen:asset type=social_card -->\n"
            "<!-- bsgen:asset render_mode=placeholder id=x -->\n"
            '<!-- bsgen:asset urls {"og_card": "/x.svg"} -->\n'
        )
        assert find_raw_bsgen_leaks(content) == []

    def test_unexpected_bsgen_comment_is_flagged(self):
        content = "<!-- bsgen:related unresolved -->\n"
        issues = find_raw_bsgen_leaks(content)
        assert len(issues) == 1
        assert "bsgen:related" in issues[0]


class TestNormalizePath:
    def test_absolute_url_is_stripped_to_path(self):
        assert normalize_path(f"{SITE_URL}/en/2026/03/11/foo/", SITE_URL) == "/en/2026/03/11/foo/"

    def test_relative_url_passes_through(self):
        assert normalize_path("/en/2026/03/11/foo/", SITE_URL) == "/en/2026/03/11/foo/"

    def test_missing_trailing_slash_is_added(self):
        assert normalize_path("/en/2026/03/11/foo", SITE_URL) == "/en/2026/03/11/foo/"


class TestSameOriginLookalikes:
    """Regression (found 2026-08-06, security review): a naive
    `url.startswith(site_root)` check misclassifies a lookalike host as
    internal. Not exploitable as a false-safe (the URL still fails to
    resolve and gets reported), but the origin check should be exact."""

    def test_lookalike_subdomain_suffix_is_not_same_origin(self):
        content = "See [this](https://bright-softwares.com.evil.com/en/2026/03/11/x/) here."
        issues = check_internal_links(content, TestCheckInternalLinks.POSTS_INDEX, SITE_URL)
        assert issues == []  # out of scope: not actually this site

    def test_protocol_relative_lookalike_is_not_same_origin(self):
        content = "See [this](//evil.com/en/2026/03/11/x/) here."
        issues = check_internal_links(content, TestCheckInternalLinks.POSTS_INDEX, SITE_URL)
        assert issues == []


class TestCheckInternalLinks:
    POSTS_INDEX = [
        {"path": None, "slug": "real-post", "url": f"{SITE_URL}/en/2026/06/22/real-post/",
         "title": "Real Post", "tags": [], "categories": [], "description": ""},
    ]

    def test_link_to_real_post_is_not_flagged(self):
        content = f"See [this]({SITE_URL}/en/2026/06/22/real-post/) for more."
        assert check_internal_links(content, self.POSTS_INDEX, SITE_URL) == []

    def test_link_to_guessed_wrong_date_is_flagged(self):
        # Same slug, wrong date — exactly the bug class this regresses against:
        # a hand-written link guessing a future publish date that didn't happen.
        content = f"See [this]({SITE_URL}/en/2026/03/11/real-post/) for more."
        issues = check_internal_links(content, self.POSTS_INDEX, SITE_URL)
        assert len(issues) == 1
        assert "2026/03/11" in issues[0]

    def test_non_dated_internal_link_is_out_of_scope(self):
        content = "See [assets](/assets/images/hero.svg) for the image."
        assert check_internal_links(content, self.POSTS_INDEX, SITE_URL) == []

    def test_external_link_is_out_of_scope(self):
        content = "See [wikipedia](https://en.wikipedia.org/2026/03/11/foo/) for more."
        assert check_internal_links(content, self.POSTS_INDEX, SITE_URL) == []

    def test_html_href_is_also_checked(self):
        content = f'<a href="{SITE_URL}/en/2026/01/01/nonexistent/">link</a>'
        issues = check_internal_links(content, self.POSTS_INDEX, SITE_URL)
        assert len(issues) == 1

    def test_markdown_link_with_title_attribute_is_still_checked(self):
        # Regression (found 2026-08-06, code review): CommonMark's
        # [text](url "title") syntax made the whole link invisible to the
        # old regex — a titled link with a bad guessed date shipped silently.
        content = f'See [this post]({SITE_URL}/en/2026/03/11/real-post/ "Real Post") for more.'
        issues = check_internal_links(content, self.POSTS_INDEX, SITE_URL)
        assert len(issues) == 1
        assert "2026/03/11" in issues[0]


class TestCheckDuplicateTopic:
    def test_no_flag_when_no_tag_overlap(self):
        current_fm = {"title": "A New Post About Widgets", "tags": ["widgets"]}
        posts_index = [
            {"slug": "other", "tags": ["gadgets"], "title": "A New Post About Widgets"},
        ]
        assert check_duplicate_topic(current_fm, "current", posts_index) == []

    def test_flags_same_tags_and_overlapping_title(self):
        current_fm = {
            "title": "Legal Documents for Gmail Add-ons: What Google Reviews",
            "tags": ["gmail", "legal", "saas"],
        }
        posts_index = [
            {
                "slug": "legal-documents-for-gmail-add-ons-what-google-reviews",
                "tags": ["gmail", "legal", "saas"],
                "title": "Legal Documents for Gmail Add-ons: What Google Reviews and How to Deploy",
                "url": f"{SITE_URL}/en/2026/06/22/legal-documents-for-gmail-add-ons/",
            },
        ]
        issues = check_duplicate_topic(current_fm, "current-slug", posts_index)
        assert len(issues) == 1
        assert "possible duplicate topic" in issues[0]

    def test_skips_self_by_slug(self):
        current_fm = {"title": "Same Title Here", "tags": ["x"]}
        posts_index = [{"slug": "current-slug", "tags": ["x"], "title": "Same Title Here"}]
        assert check_duplicate_topic(current_fm, "current-slug", posts_index) == []

    def test_stopwords_alone_do_not_count_as_title_overlap(self):
        # Regression (found 2026-08-06, code review): the old word filter
        # was just len(w) > 3, so two UNRELATED posts sharing only common
        # words like "with"/"your"/"this" (all 4+ chars) falsely flagged as
        # duplicates. Real content words still overlapping should still flag.
        current_fm = {
            "title": "Async Code Review With Your Distributed Team",
            "tags": ["engineering", "process"],
        }
        posts_index = [
            {
                "slug": "other-post",
                "tags": ["engineering", "process"],
                "title": "Documenting Decisions With Your Distributed Stakeholders",
                "url": f"{SITE_URL}/en/2026/01/01/other-post/",
            },
        ]
        # Only "distributed" is real overlap once stopwords are filtered —
        # below the 3-word threshold, so this must NOT flag.
        assert check_duplicate_topic(current_fm, "current-slug", posts_index) == []


class TestProcessIntegration:
    def test_clean_post_exits_zero(self, tmp_path: Path):
        post = tmp_path / "post.md"
        post.write_text("---\ntitle: Clean\ntags: []\n---\n\nJust prose.\n", encoding="utf-8")
        posts_dir = tmp_path / "_posts"
        posts_dir.mkdir()
        code, issues = process(post, posts_dir, SITE_URL)
        assert code == 0
        assert issues == []

    def test_post_with_raw_leak_exits_nonzero(self, tmp_path: Path):
        post = tmp_path / "post.md"
        post.write_text(
            "---\ntitle: Leaky\ntags: []\n---\n\n```bsgen:callout\ntype: STAT\n```\n",
            encoding="utf-8",
        )
        posts_dir = tmp_path / "_posts"
        posts_dir.mkdir()
        code, issues = process(post, posts_dir, SITE_URL)
        assert code == 1
        assert any("bsgen:callout" in i for i in issues)
