"""Regression tests for the seo-analysis action.yml <-> src/main.py contract.

Bug (found 2026-09-08): corporate-website's and ieatmyhealth.com's
`seo_diagnotics.yml` called `BrightSoftwares/blogpost-tools/seo-analysis@main`
with `dry_run: false`, expecting the fixer to actually apply fixes. Instead
the job logged "Dry run: False" immediately followed by "NO FIXING MODE: No
fixing will be performed" (contradiction), then failed because nothing got
fixed and `critical_issues > 0`.

Root cause: `seo-analysis/src/main.py` gates fixing behind a SEPARATE
env var, `INPUT_FIX_ISSUES` (see `should_fix_issues` a few lines below the
`dry_run` parsing) -- completely independent of `dry_run`. But
`seo-analysis/action.yml` never declared `fix_issues` (nor `fix_severity`,
`content_dirs`, `no_backup`, `max_pages`, `output_dir`, all of which
main.py also reads via `INPUT_*`) as an `inputs:` entry. GitHub Actions
silently drops any `with:` key a caller passes that isn't declared in the
action's `inputs:` block, so `INPUT_FIX_ISSUES` was always unset ->
defaulted to `"false"` -> fixing could never engage, no matter what
`dry_run` was set to. The Readme.md even documents
`INPUT_FIX_ISSUES=true` as the way to enable fixing when running the
script directly -- but that path was never wired into the action.yml
consumed by real workflows.

Confirmed failing runs (both show the same "NO FIXING MODE" contradiction):
- BrightSoftwares/corporate-website run 34263961294 / job 102188558501
- BrightSoftwares/ieatmyhealth.com run 34264563988 / job 102190589396

These tests pin down two things so this class of bug can't silently
reappear:
1. Every `INPUT_<NAME>` environment variable `main.py` reads has a matching
   entry in `action.yml`'s `inputs:` block (so it is actually reachable via
   a caller's `with:` block, instead of being silently dropped).
2. `should_fix_issues` and `dry_run` are independent gates -- setting
   `dry_run: false` alone must never enable fixing, and `fix_issues: true`
   must enable it regardless of `dry_run`.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from unittest import mock

import pytest
import yaml

SEO_ANALYSIS_DIR = Path(__file__).resolve().parent.parent.parent / "seo-analysis"
ACTION_YML = SEO_ANALYSIS_DIR / "action.yml"
MAIN_PY = SEO_ANALYSIS_DIR / "src" / "main.py"


def _declared_inputs() -> set[str]:
    spec = yaml.safe_load(ACTION_YML.read_text())
    return set(spec.get("inputs", {}).keys())


def _env_vars_read_by_main() -> set[str]:
    """Every INPUT_<NAME> main.py reads via os.getenv(...)."""
    text = MAIN_PY.read_text()
    names = re.findall(r'os\.getenv\(\s*["\']INPUT_([A-Z0-9_]+)["\']', text)
    return {n.lower() for n in names}


def test_every_env_var_main_reads_is_declared_in_action_yml():
    declared = _declared_inputs()
    read = _env_vars_read_by_main()
    undeclared = read - declared
    assert not undeclared, (
        f"src/main.py reads INPUT_<X> for {sorted(undeclared)} but action.yml "
        f"does not declare a matching input under `inputs:` -- GitHub Actions "
        f"silently drops any `with:` value a caller sets for an undeclared "
        f"input, so it can never reach the script. Declared inputs: "
        f"{sorted(declared)}."
    )


def test_fix_issues_input_is_declared_and_defaults_to_false():
    spec = yaml.safe_load(ACTION_YML.read_text())
    assert "fix_issues" in spec["inputs"], (
        "action.yml must expose `fix_issues` so callers can opt into the "
        "fixer -- this is the input whose absence caused the 2026-09-08 bug."
    )
    # Default False preserves existing behavior for any caller that doesn't
    # explicitly opt in (matches main.py's own os.getenv(..., "false") default).
    assert spec["inputs"]["fix_issues"]["default"] is False


@pytest.fixture
def main_module(monkeypatch, tmp_path):
    """Import seo-analysis/src/main.py in isolation.

    Runs with cwd redirected to a tmp dir so the module's incidental file
    writes (seo_analysis.log, the default _seo/... output dir) never touch
    the real working tree.
    """
    monkeypatch.chdir(tmp_path)
    src_dir = SEO_ANALYSIS_DIR / "src"
    monkeypatch.syspath_prepend(str(src_dir))

    spec = importlib.util.spec_from_file_location("seo_analysis_main", MAIN_PY)
    module = importlib.util.module_from_spec(spec)
    sys.modules["seo_analysis_main"] = module
    spec.loader.exec_module(module)
    try:
        yield module
    finally:
        sys.modules.pop("seo_analysis_main", None)
        sys.modules.pop("seo_analysis_fixer", None)


def _set_base_env(monkeypatch, output_dir, **overrides):
    env = {
        "INPUT_SITE_URL": "https://example.com",
        "INPUT_SITEMAP_URL": "https://example.com/sitemap.xml",
        "INPUT_OUTPUT_DIR": str(output_dir),
        "GITHUB_OUTPUT": str(output_dir / "gh_output"),
    }
    env.update(overrides)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return env


def _fake_stats():
    return {
        "total_issues": 5,
        "issues_by_severity": {"critical": 1, "high": 0, "medium": 0, "low": 0},
        "pages_with_issues": 1,
        "pages_without_issues": 0,
    }


def test_dry_run_false_alone_does_not_enable_fixing(main_module, monkeypatch, tmp_path):
    """The historical bug: dry_run=false must NOT be sufficient by itself."""
    _set_base_env(monkeypatch, tmp_path, INPUT_DRY_RUN="false")

    monkeypatch.setattr(
        main_module.SEOAnalyzer,
        "run_analysis",
        lambda self, max_pages=None: {"statistics": _fake_stats()},
    )
    fixer_cls = mock.Mock()
    monkeypatch.setattr(main_module, "SEOIssueFixer", fixer_cls)

    main_module.main()

    fixer_cls.assert_not_called()


def test_fix_issues_true_enables_fixing_independent_of_dry_run(main_module, monkeypatch, tmp_path):
    """fix_issues=true must enable fixing, with dry_run still controlling
    whether the fixer applies real writes."""
    _set_base_env(monkeypatch, tmp_path, INPUT_DRY_RUN="false", INPUT_FIX_ISSUES="true")

    monkeypatch.setattr(
        main_module.SEOAnalyzer,
        "run_analysis",
        lambda self, max_pages=None: {"statistics": _fake_stats()},
    )

    fake_fixer_instance = mock.Mock()
    fake_fixer_instance.process_issues.return_value = {
        "summary": {"total_fixes_attempted": 1, "fixes_successful": 1, "fixes_failed": 0},
    }
    fixer_cls = mock.Mock(return_value=fake_fixer_instance)
    monkeypatch.setattr(main_module, "SEOIssueFixer", fixer_cls)

    main_module.main()

    fixer_cls.assert_called_once()
    _, kwargs = fixer_cls.call_args
    assert kwargs["dry_run"] is False
    fake_fixer_instance.process_issues.assert_called_once()


def test_fix_issues_false_with_dry_run_true_still_skips_fixing(main_module, monkeypatch, tmp_path):
    """Sanity check on the other corner: both flags off -> no fixing."""
    _set_base_env(monkeypatch, tmp_path, INPUT_DRY_RUN="true", INPUT_FIX_ISSUES="false")

    monkeypatch.setattr(
        main_module.SEOAnalyzer,
        "run_analysis",
        lambda self, max_pages=None: {"statistics": _fake_stats()},
    )
    fixer_cls = mock.Mock()
    monkeypatch.setattr(main_module, "SEOIssueFixer", fixer_cls)

    main_module.main()

    fixer_cls.assert_not_called()
