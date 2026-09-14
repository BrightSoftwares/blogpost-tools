"""Unit tests for schema-markup-generator/src/main.py.

Covers: valid JSON-LD generation for a well-formed post, graceful skipping
of posts missing an unavoidable required field (title/date), best-effort
handling of missing-but-not-unavoidable fields (author/image/description),
date normalization, headline truncation, and slug derivation.
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import main  # noqa: E402


# ---------------------------------------------------------------------------
# slugify_from_path
# ---------------------------------------------------------------------------

def test_slugify_strips_jekyll_date_prefix():
    assert main.slugify_from_path(Path("_posts/2026-01-01-my-post.md")) == "my-post"


def test_slugify_keeps_stem_without_date_prefix():
    assert main.slugify_from_path(Path("_posts/my-post.md")) == "my-post"


# ---------------------------------------------------------------------------
# _to_iso_date
# ---------------------------------------------------------------------------

def test_to_iso_date_from_date_object():
    assert main._to_iso_date(date(2026, 1, 1)) == "2026-01-01"


def test_to_iso_date_from_string():
    assert main._to_iso_date("2026-01-01") == "2026-01-01"


def test_to_iso_date_from_none_returns_none():
    assert main._to_iso_date(None) is None


def test_to_iso_date_from_unparseable_string_returns_none():
    assert main._to_iso_date("not a date") is None


def test_to_iso_date_from_empty_string_returns_none():
    assert main._to_iso_date("") is None


# ---------------------------------------------------------------------------
# build_jsonld — full happy path
# ---------------------------------------------------------------------------

def test_build_jsonld_well_formed_post_generates_valid_output():
    fm = {
        "title": "A Well Formed Post",
        "date": date(2026, 1, 1),
        "author": "Jane Doe",
        "description": "A short meta description.",
        "image": "assets/images/post/hero.png",
        "categories": ["engineering"],
    }
    jsonld, warnings, skip_reason = main.build_jsonld(
        fm, Path("_posts/2026-01-01-a-well-formed-post.md"), "https://example.com", "Example Inc"
    )
    assert skip_reason is None
    assert jsonld["@context"] == "https://schema.org"
    assert jsonld["@type"] == "BlogPosting"
    assert jsonld["headline"] == "A Well Formed Post"
    assert jsonld["datePublished"] == "2026-01-01"
    assert jsonld["author"] == {"@type": "Person", "name": "Jane Doe"}
    assert jsonld["description"] == "A short meta description."
    assert jsonld["image"] == "https://example.com/assets/images/post/hero.png"
    assert jsonld["url"] == "https://example.com/a-well-formed-post/"
    assert jsonld["mainEntityOfPage"] == {"@type": "WebPage", "@id": "https://example.com/a-well-formed-post/"}
    assert jsonld["publisher"] == {"@type": "Organization", "name": "Example Inc"}
    assert warnings == []


def test_build_jsonld_absolute_image_url_kept_as_is():
    fm = {"title": "T", "date": "2026-01-01", "image": "https://cdn.example.com/img.png"}
    jsonld, _, skip_reason = main.build_jsonld(fm, Path("_posts/2026-01-01-t.md"), None, None)
    assert skip_reason is None
    assert jsonld["image"] == "https://cdn.example.com/img.png"


def test_build_jsonld_alternate_image_field_names_checked_in_order():
    fm = {"title": "T", "date": "2026-01-01", "og_image": "og.png"}
    jsonld, _, _ = main.build_jsonld(fm, Path("_posts/2026-01-01-t.md"), None, None)
    assert jsonld["image"] == "og.png"


def test_build_jsonld_relative_image_without_site_url_warns():
    fm = {"title": "T", "date": "2026-01-01", "image": "hero.png"}
    jsonld, warnings, _ = main.build_jsonld(fm, Path("_posts/2026-01-01-t.md"), None, None)
    assert jsonld["image"] == "hero.png"
    assert any("not an absolute URL" in w for w in warnings)


def test_build_jsonld_relative_image_with_site_url_no_warning():
    fm = {"title": "T", "date": "2026-01-01", "image": "hero.png"}
    jsonld, warnings, _ = main.build_jsonld(fm, Path("_posts/2026-01-01-t.md"), "https://example.com", None)
    assert jsonld["image"] == "https://example.com/hero.png"
    assert not any("not an absolute URL" in w for w in warnings)


# ---------------------------------------------------------------------------
# build_jsonld — unavoidable required fields missing -> skip, not crash
# ---------------------------------------------------------------------------

def test_build_jsonld_missing_title_is_skipped():
    fm = {"date": "2026-01-01"}
    jsonld, _, skip_reason = main.build_jsonld(fm, Path("_posts/2026-01-01-x.md"), None, None)
    assert jsonld is None
    assert "title" in skip_reason


def test_build_jsonld_missing_date_is_skipped():
    fm = {"title": "T"}
    jsonld, _, skip_reason = main.build_jsonld(fm, Path("_posts/x.md"), None, None)
    assert jsonld is None
    assert "date" in skip_reason


def test_build_jsonld_empty_title_is_skipped():
    fm = {"title": "   ", "date": "2026-01-01"}
    jsonld, _, skip_reason = main.build_jsonld(fm, Path("_posts/2026-01-01-x.md"), None, None)
    assert jsonld is None


# ---------------------------------------------------------------------------
# build_jsonld — best-effort fields, warned but not fatal
# ---------------------------------------------------------------------------

def test_build_jsonld_missing_author_and_no_publisher_omits_with_warning():
    fm = {"title": "T", "date": "2026-01-01"}
    jsonld, warnings, skip_reason = main.build_jsonld(fm, Path("_posts/2026-01-01-t.md"), None, None)
    assert skip_reason is None
    assert "author" not in jsonld
    assert any("author" in w for w in warnings)


def test_build_jsonld_missing_author_falls_back_to_publisher_organization():
    fm = {"title": "T", "date": "2026-01-01"}
    jsonld, warnings, skip_reason = main.build_jsonld(fm, Path("_posts/2026-01-01-t.md"), None, "Example Inc")
    assert skip_reason is None
    assert jsonld["author"] == {"@type": "Organization", "name": "Example Inc"}


def test_build_jsonld_missing_image_omits_with_warning():
    fm = {"title": "T", "date": "2026-01-01"}
    jsonld, warnings, _ = main.build_jsonld(fm, Path("_posts/2026-01-01-t.md"), None, None)
    assert "image" not in jsonld
    assert any("image" in w for w in warnings)


def test_build_jsonld_missing_description_omits_with_warning():
    fm = {"title": "T", "date": "2026-01-01"}
    jsonld, warnings, _ = main.build_jsonld(fm, Path("_posts/2026-01-01-t.md"), None, None)
    assert "description" not in jsonld
    assert any("description" in w for w in warnings)


def test_build_jsonld_no_site_url_omits_url_fields_with_warning():
    fm = {"title": "T", "date": "2026-01-01"}
    jsonld, warnings, _ = main.build_jsonld(fm, Path("_posts/2026-01-01-t.md"), None, None)
    assert "url" not in jsonld
    assert "mainEntityOfPage" not in jsonld
    assert "publisher" not in jsonld
    assert any("site_url" in w for w in warnings)


def test_build_jsonld_date_modified_included_when_present():
    fm = {"title": "T", "date": "2026-01-01", "last_modified_at": "2026-02-01"}
    jsonld, _, _ = main.build_jsonld(fm, Path("_posts/2026-01-01-t.md"), None, None)
    assert jsonld["dateModified"] == "2026-02-01"


def test_build_jsonld_headline_truncated_when_too_long():
    long_title = "A" * 150
    fm = {"title": long_title, "date": "2026-01-01"}
    jsonld, warnings, _ = main.build_jsonld(fm, Path("_posts/2026-01-01-t.md"), None, None)
    assert len(jsonld["headline"]) == main.MAX_HEADLINE_LENGTH
    assert any("truncated" in w for w in warnings)


# ---------------------------------------------------------------------------
# process_post — file-level integration, edge cases from the spec
# ---------------------------------------------------------------------------

def test_process_post_well_formed(tmp_path):
    post = tmp_path / "2026-01-01-my-post.md"
    post.write_text(
        "---\ntitle: My Post\ndate: 2026-01-01\nauthor: Jane\ndescription: desc\nimage: hero.png\n---\nBody.\n",
        encoding="utf-8",
    )
    result = main.process_post(post, "https://example.com", "Example Inc")
    assert result["status"] == "generated"
    assert result["jsonld"]["headline"] == "My Post"


def test_process_post_missing_frontmatter_entirely_is_skipped(tmp_path):
    post = tmp_path / "no-frontmatter.md"
    post.write_text("Just a body, no frontmatter at all.\n", encoding="utf-8")
    result = main.process_post(post, None, None)
    assert result["status"] == "skipped"


def test_process_post_non_utf8_file_is_skipped_not_crashed(tmp_path):
    post = tmp_path / "bad-encoding.md"
    post.write_bytes(b"\xff\xfe\x00\x01 not valid utf-8 \x80\x81")
    result = main.process_post(post, None, None)
    assert result["status"] == "skipped"
    assert "utf-8" in result["reason"].lower() or "utf8" in result["reason"].lower()


def test_process_post_empty_file_is_skipped_not_crashed(tmp_path):
    post = tmp_path / "empty.md"
    post.write_text("", encoding="utf-8")
    result = main.process_post(post, None, None)
    assert result["status"] == "skipped"


def test_find_posts_matches_glob(tmp_path, monkeypatch):
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir()
    (posts_dir / "2026-01-01-a.md").write_text("---\ntitle: A\ndate: 2026-01-01\n---\nBody\n")
    (posts_dir / "2026-01-02-b.md").write_text("---\ntitle: B\ndate: 2026-01-02\n---\nBody\n")
    (posts_dir / "not-a-post.txt").write_text("ignore me")

    found = main.find_posts(str(posts_dir / "**" / "*.md"))
    assert len(found) == 2
    assert all(p.suffix == ".md" for p in found)
