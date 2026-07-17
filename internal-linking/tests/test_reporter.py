"""Unit tests for src/reporter.py (Phase 6 — output & reporting)."""

import csv
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import ExclusionReason, PostMetadata  # noqa: E402
from reporter import (  # noqa: E402
    write_aliases_csv,
    write_change_report,
    write_modified_posts,
    write_outputs,
)


def _make_post(slug: str, body: str, keywords=None) -> PostMetadata:
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
        eligible_as_target=True,
        exclusion_reason=ExclusionReason.NONE,
        url_path=f"/{slug}/",
        frontmatter={},
        keywords=keywords or [],
    )


class TestWriteModifiedPosts(unittest.TestCase):
    def test_preserves_original_frontmatter_verbatim(self):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "post.md"
            original = (
                "---\n"
                "title: My Post\n"
                "date: 2024-01-01\n"
                "tags: [a, b]\n"
                "---\n"
                "Original body with [old link](/other-post/).\n"
            )
            filepath.write_text(original, encoding="utf-8")

            new_body = "Original body with [[other-post]].\n"
            write_modified_posts([(filepath, new_body)])

            result = filepath.read_text(encoding="utf-8")
            self.assertIn("title: My Post\ndate: 2024-01-01\ntags: [a, b]\n", result)
            self.assertIn("[[other-post]]", result)
            self.assertNotIn("[old link](/other-post/)", result)

    def test_handles_yaml_end_delimiter_variant(self):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "post.md"
            original = "---\ntitle: X\n...\nBody here.\n"
            filepath.write_text(original, encoding="utf-8")

            write_modified_posts([(filepath, "New body.\n")])

            result = filepath.read_text(encoding="utf-8")
            self.assertTrue(result.startswith("---\ntitle: X\n...\n"))
            self.assertIn("New body.", result)

    def test_ensures_exactly_one_trailing_newline_regardless_of_input(self):
        # python-frontmatter's Post.content strips the trailing newline at
        # parse time, so every real in-memory body this pipeline works
        # with has none — the writer must restore exactly one, and must
        # not double it up if a body somehow already has one (or several).
        with tempfile.TemporaryDirectory() as tmp:
            no_trailing = Path(tmp) / "no_trailing.md"
            has_trailing = Path(tmp) / "has_trailing.md"
            extra_trailing = Path(tmp) / "extra_trailing.md"
            for f in (no_trailing, has_trailing, extra_trailing):
                f.write_text("---\ntitle: X\n---\nOriginal\n", encoding="utf-8")

            write_modified_posts(
                [
                    (no_trailing, "Body with no trailing newline"),
                    (has_trailing, "Body with one trailing newline\n"),
                    (extra_trailing, "Body with extra trailing newlines\n\n\n"),
                ]
            )

            self.assertTrue(no_trailing.read_text(encoding="utf-8").endswith("newline\n"))
            self.assertFalse(no_trailing.read_text(encoding="utf-8").endswith("newline\n\n"))
            self.assertTrue(has_trailing.read_text(encoding="utf-8").endswith("newline\n"))
            self.assertFalse(has_trailing.read_text(encoding="utf-8").endswith("newline\n\n"))
            self.assertTrue(extra_trailing.read_text(encoding="utf-8").endswith("newlines\n"))
            self.assertFalse(extra_trailing.read_text(encoding="utf-8").endswith("newlines\n\n"))

    def test_multiple_files_each_written_independently(self):
        with tempfile.TemporaryDirectory() as tmp:
            f1 = Path(tmp) / "a.md"
            f2 = Path(tmp) / "b.md"
            f1.write_text("---\ntitle: A\n---\nBody A\n", encoding="utf-8")
            f2.write_text("---\ntitle: B\n---\nBody B\n", encoding="utf-8")

            write_modified_posts([(f1, "New A\n"), (f2, "New B\n")])

            self.assertIn("New A", f1.read_text(encoding="utf-8"))
            self.assertIn("title: A", f1.read_text(encoding="utf-8"))
            self.assertIn("New B", f2.read_text(encoding="utf-8"))
            self.assertIn("title: B", f2.read_text(encoding="utf-8"))


class TestWriteChangeReport(unittest.TestCase):
    def test_normalizes_phase4_and_phase5_entry_shapes(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = str(Path(tmp) / "change_report.csv")
            entries = [
                {  # Phase 4 shape (inserter.py)
                    "source": "src-post",
                    "target": "install-nginx",
                    "anchor": "nginx",
                    "position": 42,
                    "score": 0.9,
                    "link_type": "new",
                },
                {  # Phase 5 shape (migrator.py) — no position/score/source_tier
                    "source": "src-post",
                    "target": "other-post",
                    "anchor": "other post",
                    "original_url": "/other-post/",
                    "link_type": "migrated",
                },
            ]
            write_change_report(entries, output_path)

            with open(output_path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["source_file"], "src-post")
            self.assertEqual(rows[0]["target_slug"], "install-nginx")
            self.assertEqual(rows[0]["position"], "42")
            self.assertEqual(rows[0]["link_type"], "new")
            self.assertEqual(rows[1]["target_slug"], "other-post")
            self.assertEqual(rows[1]["link_type"], "migrated")
            self.assertEqual(rows[1]["position"], "")  # missing field -> empty cell
            self.assertTrue(rows[0]["timestamp"])  # non-empty ISO timestamp

    def test_empty_entries_writes_header_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = str(Path(tmp) / "change_report.csv")
            write_change_report([], output_path)
            with open(output_path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows, [])

    def test_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = str(Path(tmp) / "nested" / "dir" / "change_report.csv")
            write_change_report([], output_path)
            self.assertTrue(Path(output_path).exists())


class TestWriteAliasesCsv(unittest.TestCase):
    def test_v1_compatible_columns_one_row_per_keyword(self):
        index = {
            "install-nginx": _make_post(
                "install-nginx",
                "body",
                keywords=[("install nginx", 1.0, "title"), ("nginx", 0.8, "tag")],
            ),
        }
        with tempfile.TemporaryDirectory() as tmp:
            output_path = str(Path(tmp) / "aliases.csv")
            write_aliases_csv(index, output_path)
            with open(output_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                rows = list(reader)

            self.assertEqual(header, ["keyword", "target_slug", "target_url", "specificity"])
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0], ["install nginx", "install-nginx", "/install-nginx/", "1.0"])
            self.assertEqual(rows[1], ["nginx", "install-nginx", "/install-nginx/", "0.8"])

    def test_post_with_no_keywords_contributes_no_rows(self):
        index = {"empty-post": _make_post("empty-post", "body", keywords=[])}
        with tempfile.TemporaryDirectory() as tmp:
            output_path = str(Path(tmp) / "aliases.csv")
            write_aliases_csv(index, output_path)
            with open(output_path, newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
            self.assertEqual(len(rows), 1)  # header only


class TestWriteOutputs(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "post.md"
            filepath.write_text("---\ntitle: X\n---\nOriginal\n", encoding="utf-8")
            config = {"dry_run": True, "report_only": False, "seo_dir": tmp, "write_aliases_csv": True}

            write_outputs([(filepath, "Modified\n")], [{"source": "a", "target": "b", "link_type": "new"}], {}, config)

            self.assertIn("Original", filepath.read_text(encoding="utf-8"))
            self.assertFalse((Path(tmp) / "change_report.csv").exists())
            self.assertFalse((Path(tmp) / "aliases.csv").exists())

    def test_report_only_writes_audit_report_but_not_posts(self):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "post.md"
            filepath.write_text("---\ntitle: X\n---\nOriginal\n", encoding="utf-8")
            config = {"dry_run": False, "report_only": True, "seo_dir": tmp, "write_aliases_csv": True}

            write_outputs([(filepath, "Modified\n")], [{"source": "a", "target": "b", "link_type": "new"}], {}, config)

            self.assertIn("Original", filepath.read_text(encoding="utf-8"))
            self.assertTrue((Path(tmp) / "audit_report.csv").exists())
            self.assertFalse((Path(tmp) / "aliases.csv").exists())
            self.assertFalse((Path(tmp) / "change_report.csv").exists())

    def test_live_mode_writes_posts_and_both_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "post.md"
            filepath.write_text("---\ntitle: X\n---\nOriginal\n", encoding="utf-8")
            index = {"install-nginx": _make_post("install-nginx", "body", keywords=[("nginx", 0.8, "tag")])}
            config = {"dry_run": False, "report_only": False, "seo_dir": tmp, "write_aliases_csv": True}

            write_outputs(
                [(filepath, "Modified\n")],
                [{"source": "a", "target": "b", "link_type": "new"}],
                index,
                config,
            )

            self.assertIn("Modified", filepath.read_text(encoding="utf-8"))
            self.assertIn("title: X", filepath.read_text(encoding="utf-8"))
            self.assertTrue((Path(tmp) / "change_report.csv").exists())
            self.assertTrue((Path(tmp) / "aliases.csv").exists())

    def test_live_mode_respects_write_aliases_csv_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            filepath = Path(tmp) / "post.md"
            filepath.write_text("---\ntitle: X\n---\nOriginal\n", encoding="utf-8")
            config = {"dry_run": False, "report_only": False, "seo_dir": tmp, "write_aliases_csv": False}

            write_outputs([(filepath, "Modified\n")], [], {}, config)

            self.assertFalse((Path(tmp) / "aliases.csv").exists())
            self.assertTrue((Path(tmp) / "change_report.csv").exists())


if __name__ == "__main__":
    unittest.main()
