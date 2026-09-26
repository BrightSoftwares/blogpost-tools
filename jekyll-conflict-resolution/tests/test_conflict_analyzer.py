import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

import conflict_analyzer  # noqa: E402


def write_post(dirpath, filename, ref, body):
    with open(os.path.join(dirpath, filename), "w", encoding="utf-8") as f:
        f.write(f"---\nref: {ref}\n---\n{body}\n")


class TestFindConflicts(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.posts_dir = self.tmpdir.name

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_no_conflicts(self):
        write_post(self.posts_dir, "2020-01-01-a.md", "post-a", "Content A")
        write_post(self.posts_dir, "2020-01-02-b.md", "post-b", "Content B")
        conflicts = conflict_analyzer.find_conflicts(self.posts_dir)
        self.assertEqual(conflicts, {})

    def test_detects_duplicate_ref(self):
        write_post(self.posts_dir, "2020-01-01-a.md", "shared-slug", "Same content here")
        write_post(self.posts_dir, "2020-01-02-b.md", "shared-slug", "Same content here")
        conflicts = conflict_analyzer.find_conflicts(self.posts_dir)
        self.assertIn("shared-slug", conflicts)
        self.assertEqual(len(conflicts["shared-slug"]), 2)

    def test_ignores_non_markdown_files(self):
        write_post(self.posts_dir, "2020-01-01-a.md", "shared-slug", "Content")
        with open(os.path.join(self.posts_dir, "notes.txt"), "w", encoding="utf-8") as f:
            f.write("ref: shared-slug\n")
        conflicts = conflict_analyzer.find_conflicts(self.posts_dir)
        self.assertEqual(conflicts, {})


class TestClassifyPair(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.posts_dir = self.tmpdir.name

    def tearDown(self):
        self.tmpdir.cleanup()

    def _post(self, filename, ref, body):
        write_post(self.posts_dir, filename, ref, body)
        return {
            "filename": filename,
            "date": filename[:10],
            "filepath": os.path.join(self.posts_dir, filename),
        }

    def test_identical_content_classified_identical(self):
        a = self._post("2020-01-01-a.md", "slug", "Exactly the same paragraph of content, word for word.")
        b = self._post("2020-01-02-b.md", "slug", "Exactly the same paragraph of content, word for word.")
        result = conflict_analyzer.classify_pair(a, b, identical_threshold=0.95, minor_threshold=0.70)
        self.assertEqual(result["decision"], "IDENTICAL")

    def test_very_different_content_classified_different(self):
        a = self._post("2020-01-01-a.md", "slug", "A tutorial about configuring nginx reverse proxies on Ubuntu.")
        b = self._post("2020-01-02-b.md", "slug", "Recipe for baking sourdough bread with a poolish starter.")
        result = conflict_analyzer.classify_pair(a, b, identical_threshold=0.95, minor_threshold=0.70)
        self.assertEqual(result["decision"], "DIFFERENT")

    def test_body_containing_horizontal_rule_not_truncated(self):
        # 2026-09-19 fix: unbounded split("---") truncated everything after a body's own
        # '---' horizontal rule. Both posts share the identical full body (rule included),
        # so they must still classify as IDENTICAL, not DIFFERENT from a truncated compare.
        body = "Intro paragraph text here.\n\n---\n\nMore content after the horizontal rule that must survive extraction."
        a = self._post("2020-01-01-a.md", "hr-slug", body)
        b = self._post("2020-01-02-b.md", "hr-slug", body)
        content = conflict_analyzer.extract_content(a["filepath"])
        self.assertIn("More content after the horizontal rule", content)
        result = conflict_analyzer.classify_pair(a, b, identical_threshold=0.95, minor_threshold=0.70)
        self.assertEqual(result["decision"], "IDENTICAL")


class TestCLI(unittest.TestCase):
    def test_cli_runs_and_reports_conflicts(self):
        with tempfile.TemporaryDirectory() as posts_dir:
            write_post(posts_dir, "2020-01-01-a.md", "dup", "Same body text repeated here for the test.")
            write_post(posts_dir, "2020-01-02-b.md", "dup", "Same body text repeated here for the test.")

            result = subprocess.run(
                [sys.executable, os.path.join(SCRIPT_DIR, "conflict_analyzer.py"), "--posts-dir", posts_dir],
                capture_output=True,
                text=True,
                check=True,
            )
            report = json.loads(result.stdout)
            self.assertEqual(report["total_conflicts"], 1)
            self.assertEqual(report["conflicts"][0]["decision"], "IDENTICAL")


if __name__ == "__main__":
    unittest.main()
