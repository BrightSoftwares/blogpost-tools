"""Unit tests for scripts/seo_report_builder.py — pure markdown assembly, no
network, no live workflow run."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "seo_report_builder",
    Path(__file__).resolve().parent.parent.parent / "scripts" / "seo_report_builder.py",
)
builder = importlib.util.module_from_spec(_SPEC)
sys.modules["seo_report_builder"] = builder
_SPEC.loader.exec_module(builder)


def test_load_mode_results_missing_fragment_means_not_run(tmp_path):
    results = builder.load_mode_results(tmp_path)
    for mode in builder.MODE_ORDER:
        assert results[mode].ran is False


def test_load_mode_results_reads_existing_fragment(tmp_path):
    (tmp_path / "html-analysis.json").write_text(json.dumps({
        "status": "issues",
        "key_metric": "3 broken links",
        "critical_count": 1,
        "body_markdown": "Some details.",
        "followups": ["1 broken external link — see raw log"],
    }))
    results = builder.load_mode_results(tmp_path)
    r = results["html-analysis"]
    assert r.ran is True
    assert r.status == "issues"
    assert r.critical_count == 1
    assert r.followups == ["1 broken external link — see raw log"]


def test_load_mode_results_corrupt_fragment_reported_as_error_not_silently_skipped(tmp_path):
    (tmp_path / "diagnostics.json").write_text("{not valid json")
    results = builder.load_mode_results(tmp_path)
    r = results["diagnostics"]
    assert r.ran is True
    assert r.status == "error"


def test_load_autofix_missing_returns_none(tmp_path):
    assert builder.load_autofix(tmp_path) is None


def test_build_report_all_modes_not_run(tmp_path):
    results = builder.load_mode_results(tmp_path)
    report = builder.build_report("https://example.com", "2026-09-26", results)
    assert "# SEO Report" in report
    assert "not run this cycle" in report
    assert "No auto-fixes were applied this run." in report
    assert "Nothing pending this run." in report
    assert "No critical issues found this run." in report


def test_build_report_critical_count_rolls_up_across_modes(tmp_path):
    (tmp_path / "html-analysis.json").write_text(json.dumps({
        "status": "issues", "key_metric": "x", "critical_count": 2, "body_markdown": "a",
    }))
    (tmp_path / "diagnostics.json").write_text(json.dumps({
        "status": "issues", "key_metric": "y", "critical_count": 3, "body_markdown": "b",
    }))
    results = builder.load_mode_results(tmp_path)
    assert builder.total_critical_count(results) == 5
    report = builder.build_report("https://example.com", "2026-09-26", results)
    assert "5 critical issue(s) found this run" in report


def test_build_report_includes_autofix_tables_and_pr_link():
    results = {mode: builder.ModeResult() for mode in builder.MODE_ORDER}
    autofix = {
        "alt_fixed": [{"page": "about/index.html", "img_src": "/a.jpg", "alt_text": "A", "source": "_pages/about.md"}],
        "alt_skipped": [{"page": "x/index.html", "img_src": "/b.jpg", "reason": "ambiguous"}],
        "link_fixed": [],
        "link_skipped": [{"page": "y/index.html", "href": "/old/", "reason": "no fuzzy match"}],
    }
    report = builder.build_report(
        "https://example.com", "2026-09-26", results, autofix=autofix,
        autofix_pr_url="https://github.com/org/repo/pull/1",
    )
    assert "Missing alt text fixed (1)" in report
    assert "https://github.com/org/repo/pull/1" in report
    assert "ambiguous" in report
    assert "no fuzzy match" in report


def test_build_report_keep_legacy_html_analysis_flag_toggles_footnote():
    results = {mode: builder.ModeResult() for mode in builder.MODE_ORDER}
    with_legacy = builder.build_report("https://x.com", "2026-09-26", results, keep_legacy_html_analysis=True)
    without_legacy = builder.build_report("https://x.com", "2026-09-26", results, keep_legacy_html_analysis=False)
    assert "html_analysis.txt" in with_legacy
    assert "html_analysis.txt" not in without_legacy


def test_mode_followups_surface_in_needs_followup_section():
    results = {mode: builder.ModeResult() for mode in builder.MODE_ORDER}
    results["diagnostics"] = builder.ModeResult(
        ran=True, status="issues", key_metric="12 declining queries", critical_count=0,
        body_markdown="See CSV artifact.",
        followups=["4 pages losing clicks month-over-month — see uploaded CSV artifact"],
    )
    report = builder.build_report("https://x.com", "2026-09-26", results)
    assert "4 pages losing clicks month-over-month" in report
    assert "Search Console Diagnostics" in report
