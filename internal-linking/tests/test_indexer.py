"""Unit tests for src/indexer.py (Phase 1 — post index building).

Includes the spec's mandatory Test 1 (future-post exclusion) verbatim
(951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md, Section 5),
plus supplementary tests for the other eligibility rules from Section 2.
"""

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from indexer import (  # noqa: E402
    build_post_index,
    compute_exclusion_reason,
    compute_jekyll_permalink,
    count_words,
    extract_date_from_filename,
    extract_slug_from_filename,
)
from models import ExclusionReason  # noqa: E402


def _write_post(posts_dir: Path, filename: str, frontmatter_lines: str, body: str = "Content.") -> Path:
    path = posts_dir / filename
    path.write_text(f"---\n{frontmatter_lines}\n---\n{body}\n", encoding="utf-8")
    return path


class TestFuturePostExclusion(unittest.TestCase):
    """Spec Test 1 (Section 5): a post with date > today must have
    eligible_as_target=False, exclusion_reason=FUTURE_DATE."""

    def test_future_post_excluded_from_targets(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            posts_dir = Path(tmp) / "_posts"
            posts_dir.mkdir()

            _write_post(
                posts_dir,
                "2099-01-01-future-thing.md",
                "title: 'Future Thing'\ndate: 2099-01-01\nlang: en",
            )
            _write_post(
                posts_dir,
                "2024-01-01-live-thing.md",
                "title: 'Live Thing'\ndate: 2024-01-01\nlang: en",
            )

            index = build_post_index(str(posts_dir), lang="en", cutoff_date=date(2026, 1, 1))

            self.assertIn("future-thing", index)
            self.assertFalse(index["future-thing"].eligible_as_target)
            self.assertEqual(index["future-thing"].exclusion_reason, ExclusionReason.FUTURE_DATE)

            self.assertIn("live-thing", index)
            self.assertTrue(index["live-thing"].eligible_as_target)
            self.assertEqual(index["live-thing"].exclusion_reason, ExclusionReason.NONE)


class TestEligibilityRules(unittest.TestCase):
    """Supplementary coverage for Section 2's other eligibility rules."""

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.posts_dir = Path(self._tmp.name) / "_posts"
        self.posts_dir.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_unpublished_post_excluded(self):
        _write_post(
            self.posts_dir,
            "2024-01-01-draft-thing.md",
            "title: 'Draft Thing'\ndate: 2024-01-01\nlang: en\npublished: false",
        )
        index = build_post_index(str(self.posts_dir), lang="en", cutoff_date=date(2026, 1, 1))
        self.assertFalse(index["draft-thing"].eligible_as_target)
        self.assertEqual(index["draft-thing"].exclusion_reason, ExclusionReason.UNPUBLISHED)

    def test_redirect_post_excluded(self):
        _write_post(
            self.posts_dir,
            "2024-01-01-old-thing.md",
            "title: 'Old Thing'\ndate: 2024-01-01\nlang: en\nredirect_to: /new-thing/",
        )
        index = build_post_index(str(self.posts_dir), lang="en", cutoff_date=date(2026, 1, 1))
        self.assertFalse(index["old-thing"].eligible_as_target)
        self.assertEqual(index["old-thing"].exclusion_reason, ExclusionReason.REDIRECT)

    def test_lang_mismatch_excluded(self):
        _write_post(
            self.posts_dir,
            "2024-01-01-chose-truc.md",
            "title: 'Chose Truc'\ndate: 2024-01-01\nlang: fr",
        )
        index = build_post_index(str(self.posts_dir), lang="en", cutoff_date=date(2026, 1, 1))
        self.assertFalse(index["chose-truc"].eligible_as_target)
        self.assertEqual(index["chose-truc"].exclusion_reason, ExclusionReason.LANG_MISMATCH)

    def test_no_date_excluded(self):
        # No frontmatter date AND no YYYY-MM-DD filename prefix.
        _write_post(self.posts_dir, "no-date-thing.md", "title: 'No Date Thing'\nlang: en")
        index = build_post_index(str(self.posts_dir), lang="en", cutoff_date=date(2026, 1, 1))
        self.assertFalse(index["no-date-thing"].eligible_as_target)
        self.assertEqual(index["no-date-thing"].exclusion_reason, ExclusionReason.NO_DATE)
        self.assertIsNone(index["no-date-thing"].date)

    def test_date_falls_back_to_filename_when_frontmatter_missing(self):
        _write_post(self.posts_dir, "2024-01-01-filename-date.md", "title: 'Filename Date'\nlang: en")
        index = build_post_index(str(self.posts_dir), lang="en", cutoff_date=date(2026, 1, 1))
        self.assertTrue(index["filename-date"].eligible_as_target)
        self.assertEqual(index["filename-date"].date, date(2024, 1, 1))

    def test_malformed_frontmatter_skipped_entirely(self):
        path = self.posts_dir / "2024-01-01-broken.md"
        path.write_text("---\ntitle: 'Broken'\ntags: [a, b\ndate: 2024-01-01\n---\nContent.\n", encoding="utf-8")
        _write_post(self.posts_dir, "2024-01-01-fine.md", "title: 'Fine'\ndate: 2024-01-01\nlang: en")

        index = build_post_index(str(self.posts_dir), lang="en", cutoff_date=date(2026, 1, 1))

        self.assertNotIn("broken", index)
        self.assertIn("fine", index)

    def test_lang_absent_in_frontmatter_assumes_match(self):
        _write_post(self.posts_dir, "2024-01-01-no-lang-field.md", "title: 'No Lang Field'\ndate: 2024-01-01")
        index = build_post_index(str(self.posts_dir), lang="en", cutoff_date=date(2026, 1, 1))
        self.assertTrue(index["no-lang-field"].eligible_as_target)


class TestHelperFunctions(unittest.TestCase):
    """Unit tests for indexer.py's small helper functions."""

    def test_extract_slug_from_filename_with_date_prefix(self):
        self.assertEqual(
            extract_slug_from_filename(Path("2024-05-01-how-to-install-nginx.md")),
            "how-to-install-nginx",
        )

    def test_extract_slug_from_filename_without_date_prefix(self):
        self.assertEqual(extract_slug_from_filename(Path("standalone-page.md")), "standalone-page")

    def test_extract_date_from_filename_valid(self):
        self.assertEqual(
            extract_date_from_filename(Path("2024-05-01-how-to-install-nginx.md")),
            date(2024, 5, 1),
        )

    def test_extract_date_from_filename_missing(self):
        self.assertIsNone(extract_date_from_filename(Path("standalone-page.md")))

    def test_count_words(self):
        self.assertEqual(count_words("one two three"), 3)
        self.assertEqual(count_words(""), 0)

    def test_compute_jekyll_permalink_default(self):
        permalink = compute_jekyll_permalink({}, date(2024, 5, 1), "my-slug")
        self.assertEqual(permalink, "/2024/05/01/my-slug/")

    def test_compute_jekyll_permalink_explicit_override(self):
        permalink = compute_jekyll_permalink({"permalink": "/custom/path/"}, date(2024, 5, 1), "my-slug")
        self.assertEqual(permalink, "/custom/path/")

    def test_compute_jekyll_permalink_no_date(self):
        self.assertEqual(compute_jekyll_permalink({}, None, "my-slug"), "/my-slug/")

    def test_compute_exclusion_reason_precedence(self):
        # no_date takes precedence over everything else.
        self.assertEqual(
            compute_exclusion_reason(
                is_future=True, is_unpublished=True, is_redirect=True, lang_mismatch=True, no_date=True
            ),
            ExclusionReason.NO_DATE,
        )
        self.assertEqual(
            compute_exclusion_reason(
                is_future=True, is_unpublished=True, is_redirect=True, lang_mismatch=True, no_date=False
            ),
            ExclusionReason.FUTURE_DATE,
        )
        self.assertEqual(
            compute_exclusion_reason(
                is_future=False, is_unpublished=False, is_redirect=False, lang_mismatch=False, no_date=False
            ),
            ExclusionReason.NONE,
        )


if __name__ == "__main__":
    unittest.main()
