import os
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

import bulk_resolver  # noqa: E402
import verify_no_conflicts  # noqa: E402


def write_post(dirpath, filename, ref, body):
    with open(os.path.join(dirpath, filename), "w", encoding="utf-8") as f:
        f.write(f"---\nref: {ref}\n---\n{body}\n")


class TestApplyDeletes(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.posts_dir = self.tmpdir.name

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_dry_run_does_not_delete(self):
        write_post(self.posts_dir, "old.md", "slug", "content")
        count = bulk_resolver.apply_deletes(self.posts_dir, ["old.md"], dry_run=True)
        self.assertEqual(count, 1)
        self.assertTrue(os.path.exists(os.path.join(self.posts_dir, "old.md")))

    def test_apply_deletes_file(self):
        write_post(self.posts_dir, "old.md", "slug", "content")
        count = bulk_resolver.apply_deletes(self.posts_dir, ["old.md"], dry_run=False)
        self.assertEqual(count, 1)
        self.assertFalse(os.path.exists(os.path.join(self.posts_dir, "old.md")))

    def test_missing_file_is_skipped_not_errored(self):
        count = bulk_resolver.apply_deletes(self.posts_dir, ["does-not-exist.md"], dry_run=False)
        self.assertEqual(count, 0)


class TestApplyRenames(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.posts_dir = self.tmpdir.name

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_apply_rename_updates_ref_and_filename(self):
        write_post(self.posts_dir, "old.md", "old-slug", "body text")
        renames = {"old.md": {"new_filename": "new.md", "new_ref": "new-slug"}}

        bulk_resolver.apply_renames(self.posts_dir, renames, dry_run=False)

        self.assertFalse(os.path.exists(os.path.join(self.posts_dir, "old.md")))
        new_path = os.path.join(self.posts_dir, "new.md")
        self.assertTrue(os.path.exists(new_path))
        with open(new_path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("ref: new-slug", content)
        self.assertIn("body text", content)

    def test_dry_run_leaves_files_untouched(self):
        write_post(self.posts_dir, "old.md", "old-slug", "body text")
        renames = {"old.md": {"new_filename": "new.md", "new_ref": "new-slug"}}

        bulk_resolver.apply_renames(self.posts_dir, renames, dry_run=True)

        self.assertTrue(os.path.exists(os.path.join(self.posts_dir, "old.md")))
        self.assertFalse(os.path.exists(os.path.join(self.posts_dir, "new.md")))


class TestVerifyNoConflicts(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.posts_dir = self.tmpdir.name

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_no_conflicts_returns_empty(self):
        write_post(self.posts_dir, "a.md", "slug-a", "content")
        write_post(self.posts_dir, "b.md", "slug-b", "content")
        remaining = verify_no_conflicts.find_remaining_conflicts(self.posts_dir)
        self.assertEqual(remaining, {})

    def test_conflict_detected(self):
        write_post(self.posts_dir, "a.md", "shared", "content")
        write_post(self.posts_dir, "b.md", "shared", "content")
        remaining = verify_no_conflicts.find_remaining_conflicts(self.posts_dir)
        self.assertIn("shared", remaining)
        self.assertEqual(sorted(remaining["shared"]), ["a.md", "b.md"])


if __name__ == "__main__":
    unittest.main()
