"""Unit tests for scripts/seo_autofix.py.

All tests are hermetic (no network, no live Jekyll build, no GSC/Docker
dependency) — they build small synthetic build_dir/content_dir trees under
pytest's tmp_path and assert on the pure functions plus the run_autofix()
orchestrator. This is deliberate: the actual GitHub Actions run and any live
GSC API call cannot be exercised from this sandbox (see the task report).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "seo_autofix",
    Path(__file__).resolve().parent.parent.parent / "scripts" / "seo_autofix.py",
)
autofix = importlib.util.module_from_spec(_SPEC)
sys.modules["seo_autofix"] = autofix
_SPEC.loader.exec_module(autofix)


# ---------------------------------------------------------------------------
# derive_alt_text
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "img_src,expected",
    [
        ("/assets/img/sunset-over-the-mountains.jpg", "Sunset Over The Mountains"),
        ("/assets/2026-09-26-team-offsite-cover.png", "Team Offsite Cover"),
        ("/assets/img/dashboard-screenshot-1200x630.png", "Dashboard Screenshot"),
        ("/assets/img/logo@2x.png", "Logo"),
        ("photo_of_a_cat.jpeg", "Photo Of A Cat"),
    ],
)
def test_derive_alt_text_reasonable_filenames(img_src, expected):
    assert autofix.derive_alt_text(img_src) == expected


@pytest.mark.parametrize(
    "img_src",
    [
        "/assets/img/a3f9c21b.png",       # hash-like
        "/assets/img/123456.jpg",         # purely numeric
        "",                                # empty
        "/assets/img/.png",               # empty stem
    ],
)
def test_derive_alt_text_returns_none_when_unconfident(img_src):
    assert autofix.derive_alt_text(img_src) is None


# ---------------------------------------------------------------------------
# find_missing_alt_images — only a TRULY ABSENT alt attribute counts
# ---------------------------------------------------------------------------

def test_find_missing_alt_images_flags_absent_alt_only():
    html = """
    <html><body>
      <img src="/assets/a.jpg">
      <img src="/assets/b.jpg" alt="">
      <img src="/assets/c.jpg" alt="A cat">
      <img src="/assets/d.jpg" />
    </body></html>
    """
    missing = autofix.find_missing_alt_images(html)
    assert missing == ["/assets/a.jpg", "/assets/d.jpg"]


def test_find_missing_alt_images_empty_alt_is_never_flagged():
    """Empty alt="" is a deliberate a11y marker for decorative images — never a fix target."""
    html = '<img src="/assets/decorative.png" alt="">'
    assert autofix.find_missing_alt_images(html) == []


# ---------------------------------------------------------------------------
# slug_from_build_path / find_source_file_for_slug / map_build_to_source
# ---------------------------------------------------------------------------

def test_slug_from_build_path_index_html():
    build_dir = Path("/build")
    p = build_dir / "2026" / "09" / "26" / "my-post" / "index.html"
    assert autofix.slug_from_build_path(p, build_dir) == "my-post"


def test_slug_from_build_path_bare_html():
    build_dir = Path("/build")
    p = build_dir / "about.html"
    assert autofix.slug_from_build_path(p, build_dir) == "about"


def test_find_source_file_for_slug_single_match(tmp_path):
    posts = tmp_path / "_posts"
    posts.mkdir()
    (posts / "2026-09-26-my-post.md").write_text("---\ntitle: hi\n---\nbody")
    found = autofix.find_source_file_for_slug("my-post", [posts])
    assert found == posts / "2026-09-26-my-post.md"


def test_find_source_file_for_slug_ambiguous_returns_none(tmp_path):
    posts = tmp_path / "_posts"
    posts.mkdir()
    (posts / "2026-09-26-my-post.md").write_text("a")
    (posts / "2020-01-01-my-post.md").write_text("b")
    assert autofix.find_source_file_for_slug("my-post", [posts]) is None


def test_find_source_file_for_slug_zero_matches_returns_none(tmp_path):
    posts = tmp_path / "_posts"
    posts.mkdir()
    (posts / "2026-09-26-something-else.md").write_text("a")
    assert autofix.find_source_file_for_slug("my-post", [posts]) is None


def test_map_build_to_source_page(tmp_path):
    build_dir = tmp_path / "build"
    pages = tmp_path / "_pages"
    pages.mkdir(parents=True)
    (pages / "about.md").write_text("---\ntitle: About\n---\nhello")
    built = build_dir / "about" / "index.html"
    assert autofix.map_build_to_source(built, build_dir, [pages]) == pages / "about.md"


# ---------------------------------------------------------------------------
# apply_alt_fix
# ---------------------------------------------------------------------------

def test_apply_alt_fix_raw_img_tag(tmp_path):
    f = tmp_path / "post.md"
    f.write_text('Intro\n\n<img src="/assets/sunset.jpg">\n\nMore text.')
    ok = autofix.apply_alt_fix(f, "/assets/sunset.jpg", "Sunset")
    assert ok is True
    assert '<img alt="Sunset" src="/assets/sunset.jpg">' in f.read_text()


def test_apply_alt_fix_markdown_syntax(tmp_path):
    f = tmp_path / "post.md"
    f.write_text("Intro\n\n![](/assets/sunset.jpg)\n\nMore text.")
    ok = autofix.apply_alt_fix(f, "/assets/sunset.jpg", "Sunset")
    assert ok is True
    assert "![Sunset](/assets/sunset.jpg)" in f.read_text()


def test_apply_alt_fix_ambiguous_multiple_matches_skips(tmp_path):
    f = tmp_path / "post.md"
    f.write_text(
        '<img src="/assets/sunset.jpg">\n'
        '<img src="/assets/sunset.jpg">\n'
    )
    original = f.read_text()
    ok = autofix.apply_alt_fix(f, "/assets/sunset.jpg", "Sunset")
    assert ok is False
    assert f.read_text() == original  # untouched


def test_apply_alt_fix_no_match_skips(tmp_path):
    f = tmp_path / "post.md"
    f.write_text("no images here")
    assert autofix.apply_alt_fix(f, "/assets/sunset.jpg", "Sunset") is False


def test_apply_alt_fix_already_has_alt_is_not_matched(tmp_path):
    f = tmp_path / "post.md"
    f.write_text('<img src="/assets/sunset.jpg" alt="already set">')
    original = f.read_text()
    ok = autofix.apply_alt_fix(f, "/assets/sunset.jpg", "Sunset")
    assert ok is False
    assert f.read_text() == original


# ---------------------------------------------------------------------------
# Internal link detection + fuzzy match + apply
# ---------------------------------------------------------------------------

def test_find_internal_hrefs_skips_external_and_fragments():
    html = (
        '<a href="/about/">About</a>'
        '<a href="https://example.com/other">External</a>'
        '<a href="#section">Fragment</a>'
        '<a href="mailto:a@b.com">Mail</a>'
    )
    hrefs = autofix.find_internal_hrefs(html, site_url="https://mysite.com")
    assert hrefs == ["/about/"]


def test_find_internal_hrefs_same_domain_absolute_is_internal():
    html = '<a href="https://mysite.com/about/">About</a>'
    hrefs = autofix.find_internal_hrefs(html, site_url="https://mysite.com")
    assert hrefs == ["https://mysite.com/about/"]


def test_target_exists_in_build(tmp_path):
    build_dir = tmp_path / "build"
    (build_dir / "about").mkdir(parents=True)
    (build_dir / "about" / "index.html").write_text("hi")
    assert autofix.target_exists_in_build("/about/", build_dir) is True
    assert autofix.target_exists_in_build("/missing-page/", build_dir) is False
    assert autofix.target_exists_in_build("/", build_dir) is True


def test_all_page_urls(tmp_path):
    build_dir = tmp_path / "build"
    (build_dir / "about").mkdir(parents=True)
    (build_dir / "about" / "index.html").write_text("hi")
    (build_dir / "index.html").write_text("home")
    urls = autofix.all_page_urls(build_dir)
    assert "/about/" in urls
    assert "/" in urls


def test_fuzzy_match_internal_link_finds_close_rename():
    candidates = ["/about-us/", "/contact/", "/pricing/"]
    assert autofix.fuzzy_match_internal_link("/about-me/", candidates) == "/about-us/"


def test_fuzzy_match_internal_link_no_confident_match_returns_none():
    candidates = ["/completely/unrelated/", "/other-page/"]
    assert autofix.fuzzy_match_internal_link("/xyz-nothing-like-it/", candidates) is None


def test_apply_link_fix_single_occurrence(tmp_path):
    f = tmp_path / "post.md"
    f.write_text("See [our about page](/about-me/) for more.")
    ok = autofix.apply_link_fix(f, "/about-me/", "/about-us/")
    assert ok is True
    assert "/about-us/" in f.read_text()


def test_apply_link_fix_multiple_occurrences_skips(tmp_path):
    f = tmp_path / "post.md"
    f.write_text("[a](/about-me/) and [b](/about-me/)")
    original = f.read_text()
    ok = autofix.apply_link_fix(f, "/about-me/", "/about-us/")
    assert ok is False
    assert f.read_text() == original


# ---------------------------------------------------------------------------
# run_autofix — end-to-end over a synthetic build tree
# ---------------------------------------------------------------------------

def test_run_autofix_fixes_alt_and_reports_unfixable(tmp_path):
    build_dir = tmp_path / "build"
    posts = tmp_path / "_posts"
    (build_dir / "2026" / "09" / "26" / "my-post").mkdir(parents=True)
    posts.mkdir()

    (build_dir / "2026" / "09" / "26" / "my-post" / "index.html").write_text(
        '<html><body><img src="/assets/team-offsite-cover.jpg"></body></html>'
    )
    (posts / "2026-09-26-my-post.md").write_text(
        '---\ntitle: hi\n---\n<img src="/assets/team-offsite-cover.jpg">\n'
    )

    result = autofix.run_autofix(build_dir, [posts])

    assert len(result.alt_fixed) == 1
    assert result.alt_fixed[0]["alt_text"] == "Team Offsite Cover"
    assert result.changed_files == [str(posts / "2026-09-26-my-post.md")]
    assert 'alt="Team Offsite Cover"' in (posts / "2026-09-26-my-post.md").read_text()


def test_run_autofix_reports_unresolvable_alt_without_crashing(tmp_path):
    build_dir = tmp_path / "build"
    posts = tmp_path / "_posts"
    (build_dir / "page").mkdir(parents=True)
    posts.mkdir()
    # Hash-like filename -> derive_alt_text returns None -> must be skipped, not fixed.
    (build_dir / "page" / "index.html").write_text('<img src="/assets/a3f9c21b.png">')

    result = autofix.run_autofix(build_dir, [posts])

    assert result.alt_fixed == []
    assert len(result.alt_skipped) == 1
    assert "confident alt text" in result.alt_skipped[0]["reason"]


def test_run_autofix_fixes_broken_internal_link(tmp_path):
    build_dir = tmp_path / "build"
    posts = tmp_path / "_posts"
    posts.mkdir()
    (build_dir / "about-us").mkdir(parents=True)
    (build_dir / "about-us" / "index.html").write_text("<html><body>About us</body></html>")
    (build_dir / "2026" / "01" / "01" / "post-a").mkdir(parents=True)
    (build_dir / "2026" / "01" / "01" / "post-a" / "index.html").write_text(
        '<a href="/about-me/">About</a>'
    )
    (posts / "2026-01-01-post-a.md").write_text("See our [about page](/about-me/) for info.")

    result = autofix.run_autofix(build_dir, [posts], site_url="https://example.com")

    assert len(result.link_fixed) == 1
    assert result.link_fixed[0]["suggested_href"] == "/about-us/"
    assert "/about-us/" in (posts / "2026-01-01-post-a.md").read_text()


def test_run_autofix_never_touches_working_alt_or_valid_links(tmp_path):
    build_dir = tmp_path / "build"
    posts = tmp_path / "_posts"
    posts.mkdir()
    (build_dir / "page").mkdir(parents=True)
    (build_dir / "page" / "index.html").write_text(
        '<img src="/assets/logo.png" alt="Logo"><a href="/page/">self</a>'
    )
    (posts / "2026-01-01-page.md").write_text("nothing to change here")

    result = autofix.run_autofix(build_dir, [posts])

    assert result.alt_fixed == result.alt_skipped == []
    assert result.link_fixed == result.link_skipped == []
    assert result.changed_files == []
