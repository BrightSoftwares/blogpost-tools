"""Unit tests for src/migrator.py (Phase 5 — existing link migration)."""

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from migrator import migrate_existing_links, resolve_url_to_slug  # noqa: E402
from models import ExclusionReason, PostMetadata  # noqa: E402


def _make_post(slug: str, body: str, url_path: str | None = None, eligible: bool = True) -> PostMetadata:
    return PostMetadata(
        slug=slug,
        filepath=Path(f"/tmp/{slug}.md"),
        title="Post",
        date=date(2024, 1, 1),
        tags=[],
        categories=[],
        lang="en",
        body=body,
        body_word_count=len(body.split()),
        eligible_as_target=eligible,
        exclusion_reason=ExclusionReason.NONE if eligible else ExclusionReason.FUTURE_DATE,
        url_path=url_path or f"/{slug}/",
        frontmatter={},
    )


class TestResolveUrlToSlug(unittest.TestCase):
    def test_direct_slug_match(self):
        index = {"install-nginx": _make_post("install-nginx", "body")}
        self.assertEqual(resolve_url_to_slug("/tutorials/install-nginx/", index), "install-nginx")

    def test_full_path_match_against_url_path(self):
        # Slug and the URL's last path segment deliberately differ ("nginx-setup"
        # vs. "install-nginx") so this only resolves via the url_path match
        # (strategy 2), not the direct-slug match (strategy 1) tried first.
        index = {"nginx-setup": _make_post("nginx-setup", "body", url_path="/tutorials/install-nginx/")}
        self.assertEqual(resolve_url_to_slug("/tutorials/install-nginx/", index), "nginx-setup")

    def test_date_prefixed_filename_pattern(self):
        index = {"install-nginx": _make_post("install-nginx", "body")}
        self.assertEqual(resolve_url_to_slug("2024-01-01-install-nginx", index), "install-nginx")

    def test_strips_markdown_extension(self):
        index = {"install-nginx": _make_post("install-nginx", "body")}
        self.assertEqual(resolve_url_to_slug("/install-nginx.md", index), "install-nginx")

    def test_returns_none_when_unresolvable(self):
        index = {"install-nginx": _make_post("install-nginx", "body")}
        self.assertIsNone(resolve_url_to_slug("/some/other/post/", index))

    def test_direct_slug_match_is_case_insensitive(self):
        # indexer.py does not lowercase slugs, so a post filed as
        # "2024-01-01-Install-Nginx.md" is indexed under the literal
        # mixed-case key "Install-Nginx" — a lowercase URL must still resolve.
        index = {"Install-Nginx": _make_post("Install-Nginx", "body")}
        self.assertEqual(resolve_url_to_slug("/install-nginx/", index), "Install-Nginx")

    def test_date_prefixed_pattern_is_case_insensitive(self):
        index = {"Install-Nginx": _make_post("Install-Nginx", "body")}
        self.assertEqual(resolve_url_to_slug("2024-01-01-install-nginx", index), "Install-Nginx")

    def test_date_prefixed_pattern_requires_fixed_width_ymd(self):
        # "9-9-9-nginx-setup" has 3 all-digit dash-separated parts but is not
        # a real YYYY-MM-DD prefix (spec requires fixed 4-2-2 digit widths) —
        # must not be misread as a date-prefixed slug.
        index = {"nginx-setup": _make_post("nginx-setup", "body")}
        self.assertIsNone(resolve_url_to_slug("9-9-9-nginx-setup", index))

    def test_strips_url_fragment(self):
        index = {"other-post": _make_post("other-post", "body")}
        self.assertEqual(resolve_url_to_slug("/other-post/#some-heading", index), "other-post")

    def test_strips_query_string(self):
        index = {"other-post": _make_post("other-post", "body")}
        self.assertEqual(resolve_url_to_slug("/other-post/?utm_source=x", index), "other-post")


class TestMigrateExistingLinks(unittest.TestCase):
    def test_migrates_markdown_link_with_matching_anchor_to_short_form(self):
        target = _make_post("install-nginx", "target body")
        body = "See [install nginx](/install-nginx/) for details."
        source = _make_post("src", body)
        index = {"install-nginx": target}

        modified_body, modified, log = migrate_existing_links(source, index)

        self.assertTrue(modified)
        self.assertIn("[[install-nginx]]", modified_body)
        self.assertNotIn("[install nginx](/install-nginx/)", modified_body)
        self.assertEqual(log[0]["target"], "install-nginx")
        self.assertEqual(log[0]["link_type"], "migrated")
        self.assertEqual(log[0]["original_url"], "/install-nginx/")

    def test_migrates_markdown_link_with_different_anchor_to_long_form(self):
        target = _make_post("install-nginx", "target body")
        body = "Read [how to set up nginx](/install-nginx/) here."
        source = _make_post("src", body)
        index = {"install-nginx": target}

        modified_body, modified, _log = migrate_existing_links(source, index)

        self.assertTrue(modified)
        self.assertIn("[[install-nginx|how to set up nginx]]", modified_body)

    def test_skips_external_links(self):
        body = "See [external](https://example.com/foo) for details."
        source = _make_post("src", body)
        modified_body, modified, log = migrate_existing_links(source, {})
        self.assertFalse(modified)
        self.assertEqual(modified_body, body)
        self.assertEqual(log, [])

    def test_skips_mailto_and_anchor_links(self):
        body = "Email [me](mailto:x@example.com) or jump to [section](#section)."
        source = _make_post("src", body)
        modified_body, modified, _log = migrate_existing_links(source, {})
        self.assertFalse(modified)
        self.assertEqual(modified_body, body)

    def test_skips_image_links(self):
        body = "![alt text](/install-nginx/)"
        target = _make_post("install-nginx", "target body")
        modified_body, modified, log = migrate_existing_links(_make_post("src", body), {"install-nginx": target})
        self.assertFalse(modified)
        self.assertEqual(log, [])
        self.assertEqual(modified_body, body)

    def test_skips_links_inside_fenced_code_blocks(self):
        body = "```\n[install-nginx](/install-nginx/)\n```"
        target = _make_post("install-nginx", "target body")
        modified_body, modified, log = migrate_existing_links(_make_post("src", body), {"install-nginx": target})
        self.assertFalse(modified)
        self.assertEqual(log, [])
        self.assertEqual(modified_body, body)

    def test_skips_links_inside_indented_code_blocks(self):
        body = "Intro text.\n\n    [install-nginx](/install-nginx/)\n\nMore text."
        target = _make_post("install-nginx", "target body")
        modified_body, modified, log = migrate_existing_links(_make_post("src", body), {"install-nginx": target})
        self.assertFalse(modified)
        self.assertEqual(log, [])
        self.assertEqual(modified_body, body)

    def test_skips_links_inside_inline_code_spans(self):
        body = "See `[install-nginx](/install-nginx/)` in the source."
        target = _make_post("install-nginx", "target body")
        modified_body, modified, log = migrate_existing_links(_make_post("src", body), {"install-nginx": target})
        self.assertFalse(modified)
        self.assertEqual(log, [])
        self.assertEqual(modified_body, body)

    def test_migrates_with_case_insensitive_anchor_slug_match(self):
        target = _make_post("install-nginx", "target body")
        body = "See [Install Nginx](/install-nginx/) for details."
        modified_body, modified, log = migrate_existing_links(_make_post("src", body), {"install-nginx": target})
        self.assertTrue(modified)
        self.assertIn("[[install-nginx]]", modified_body)
        self.assertEqual(log[0]["target"], "install-nginx")

    def test_skips_unresolvable_links(self):
        body = "See [somewhere](/does-not-exist/) for details."
        source = _make_post("src", body)
        modified_body, modified, log = migrate_existing_links(source, {})
        self.assertFalse(modified)
        self.assertEqual(log, [])
        self.assertEqual(modified_body, body)

    def test_skips_links_to_ineligible_targets(self):
        target = _make_post("future-post", "target body", eligible=False)
        body = "See [upcoming](/future-post/) soon."
        source = _make_post("src", body)
        modified_body, modified, log = migrate_existing_links(source, {"future-post": target})
        self.assertFalse(modified)
        self.assertEqual(log, [])
        self.assertEqual(modified_body, body)

    def test_multiple_links_processed_end_to_start_preserve_offsets(self):
        alpha = _make_post("alpha-post", "body")
        beta = _make_post("beta-post", "body")
        body = "First [alpha](/alpha-post/) then [beta](/beta-post/) done."
        source = _make_post("src", body)
        index = {"alpha-post": alpha, "beta-post": beta}

        modified_body, modified, log = migrate_existing_links(source, index)

        self.assertTrue(modified)
        self.assertIn("[[alpha-post|alpha]]", modified_body)
        self.assertIn("[[beta-post|beta]]", modified_body)
        self.assertEqual(len(log), 2)
        self.assertEqual({entry["target"] for entry in log}, {"alpha-post", "beta-post"})

    def test_empty_body_returns_unchanged(self):
        source = _make_post("src", "")
        modified_body, modified, log = migrate_existing_links(source, {})
        self.assertEqual(modified_body, "")
        self.assertFalse(modified)
        self.assertEqual(log, [])

    def test_no_links_in_body_returns_unchanged(self):
        body = "Nothing to migrate here."
        source = _make_post("src", body)
        modified_body, modified, log = migrate_existing_links(source, {})
        self.assertEqual(modified_body, body)
        self.assertFalse(modified)
        self.assertEqual(log, [])


if __name__ == "__main__":
    unittest.main()
