"""Tests for migrate_jekyll_repo.py's `_data` stub generator.

Regression (found 2026-08-26 migrating beaconharbor.afanou.com,
`sp14-5-navigation-stub-collision-20260826`): `ensure_data_stub("_data/navigation.yml", ...)`
only checked `path.exists()` for the exact file `_data/navigation.yml`. When a repo already
used the directory form (`_data/navigation/en.yml` + `_data/navigation/fr.yml`), that check
was False (the *file* doesn't exist) so the script happily created an empty
`_data/navigation.yml` stub sitting next to the real `_data/navigation/` directory. Jekyll
populates `site.data.navigation` from either form — having both is undefined/collision-prone
and the empty stub could silently shadow the real per-language data depending on file-walk
order.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "jekyll-multi-language-tools"))

import migrate_jekyll_repo  # noqa: E402
from migrate_jekyll_repo import ensure_data_stub  # noqa: E402


class TestEnsureDataStub:
    def test_creates_stub_when_nothing_exists(self, tmp_path):
        created = ensure_data_stub(tmp_path, "_data/translations.yml", "items: []\n", dry_run=False)

        assert created is True
        assert (tmp_path / "_data" / "translations.yml").read_text(encoding="utf-8") == "items: []\n"

    def test_skips_when_exact_file_already_exists(self, tmp_path):
        data_dir = tmp_path / "_data"
        data_dir.mkdir()
        (data_dir / "translations.yml").write_text("real: content\n", encoding="utf-8")

        created = ensure_data_stub(tmp_path, "_data/translations.yml", "items: []\n", dry_run=False)

        assert created is False
        assert (data_dir / "translations.yml").read_text(encoding="utf-8") == "real: content\n"

    def test_skips_when_sibling_directory_form_already_exists(self, tmp_path):
        nav_dir = tmp_path / "_data" / "navigation"
        nav_dir.mkdir(parents=True)
        (nav_dir / "en.yml").write_text("items: [home]\n", encoding="utf-8")
        (nav_dir / "fr.yml").write_text("items: [accueil]\n", encoding="utf-8")

        created = ensure_data_stub(tmp_path, "_data/navigation.yml", "items: []\n", dry_run=False)

        assert created is False
        assert not (tmp_path / "_data" / "navigation.yml").exists()
        # real per-language files must survive untouched
        assert (nav_dir / "en.yml").read_text(encoding="utf-8") == "items: [home]\n"
        assert (nav_dir / "fr.yml").read_text(encoding="utf-8") == "items: [accueil]\n"

    def test_dry_run_never_writes_even_when_creating(self, tmp_path):
        created = ensure_data_stub(tmp_path, "_data/translations.yml", "items: []\n", dry_run=True)

        assert created is True
        assert not (tmp_path / "_data" / "translations.yml").exists()
