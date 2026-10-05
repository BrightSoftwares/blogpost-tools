#!/usr/bin/env python3
"""
seo_report_builder.py — assembles the single unified markdown report for
`reusable_seo-pipeline.yml` (see `231.004.PRJ...` "Unified SEO Pipeline Spec").

Each mode step in the pipeline writes its own small JSON fragment to a shared
state directory (`<mode>.json`); this script reads whichever fragments exist
(a mode that did not run this cycle simply has no fragment) plus an optional
`autofix.json`, and renders the one committed report:

    <report_dir>/seo-report-YYYY-MM-DD.md

Per-mode JSON fragment schema (`<state_dir>/<mode>.json`):
    {
      "status": "ok" | "issues" | "error",
      "key_metric": "<short human string for the summary table>",
      "critical_count": <int>,
      "body_markdown": "<markdown body for this mode's Details section>",
      "followups": ["<bullet text>", ...]   # optional, goes in the
                                             # "Needs Human/AI Follow-Up" section
    }

autofix.json schema: the JSON written by `seo_autofix.py` (see that module's
`AutofixResult.to_dict()`).

This module is pure (no network, no subprocess) so it is fully unit-testable.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

MODE_ORDER = ["html-analysis", "diagnostics", "index-check", "gsc-index-coverage"]

MODE_TITLES = {
    "html-analysis": "HTML Analysis",
    "diagnostics": "Search Console Diagnostics",
    "index-check": "Index / Crawlability Check",
    "gsc-index-coverage": "GSC Index Coverage",
}


@dataclass
class ModeResult:
    ran: bool = False
    status: str = "not run"
    key_metric: str = "—"
    critical_count: int = 0
    body_markdown: str = ""
    followups: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "ModeResult":
        return cls(
            ran=True,
            status=str(data.get("status", "ok")),
            key_metric=str(data.get("key_metric", "—")),
            critical_count=int(data.get("critical_count", 0) or 0),
            body_markdown=str(data.get("body_markdown", "")),
            followups=list(data.get("followups", []) or []),
        )


def load_mode_results(state_dir: Path) -> dict[str, ModeResult]:
    results: dict[str, ModeResult] = {}
    for mode in MODE_ORDER:
        frag = state_dir / f"{mode}.json"
        if frag.exists():
            try:
                data = json.loads(frag.read_text(encoding="utf-8"))
                results[mode] = ModeResult.from_dict(data)
                continue
            except (json.JSONDecodeError, OSError):
                results[mode] = ModeResult(
                    ran=True, status="error", key_metric="could not read state file",
                    critical_count=0,
                    body_markdown=f"Could not parse `{frag.name}` — treated as an error, not silently skipped.",
                )
                continue
        results[mode] = ModeResult()
    return results


def load_autofix(state_dir: Path) -> Optional[dict]:
    frag = state_dir / "autofix.json"
    if not frag.exists():
        return None
    try:
        return json.loads(frag.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _autofix_table(entries: list[dict], columns: list[tuple[str, str]]) -> list[str]:
    """Render a markdown table. columns: list of (header, dict_key)."""
    if not entries:
        return []
    lines = ["| " + " | ".join(h for h, _ in columns) + " |",
             "|" + "|".join("---" for _ in columns) + "|"]
    for e in entries:
        row = [str(e.get(key, "")) for _, key in columns]
        lines.append("| " + " | ".join(row) + " |")
    return lines


def build_report(
    site_url: str,
    run_date: str,
    results: dict[str, ModeResult],
    autofix: Optional[dict] = None,
    autofix_pr_url: str = "",
    keep_legacy_html_analysis: bool = True,
) -> str:
    lines: list[str] = [f"# SEO Report — {site_url}", "", f"**Run date:** {run_date}", ""]

    # --- Summary table --------------------------------------------------
    lines += ["## Summary", "", "| Mode | Status | Key metric | Critical issues |", "|---|---|---|---|"]
    total_critical = 0
    for mode in MODE_ORDER:
        r = results.get(mode, ModeResult())
        status = r.status if r.ran else "not run this cycle"
        metric = r.key_metric if r.ran else "—"
        critical = r.critical_count if r.ran else 0
        total_critical += critical
        lines.append(f"| {MODE_TITLES[mode]} | {status} | {metric} | {critical} |")
    lines.append("")

    # --- Details ---------------------------------------------------------
    lines.append("## Details")
    lines.append("")
    for mode in MODE_ORDER:
        r = results.get(mode, ModeResult())
        lines.append(f"### {MODE_TITLES[mode]}")
        lines.append("")
        if not r.ran:
            lines.append("Not run this cycle.")
        else:
            lines.append(r.body_markdown.strip() or "_No details reported._")
        lines.append("")

    # --- Auto-fixes applied ----------------------------------------------
    lines.append("## Auto-Fixes Applied")
    lines.append("")
    lines.append(
        "> Scope: only missing `alt` text (derived from filename) and broken *internal* "
        "links (fuzzy-matched against this run's own pages) are auto-fixed, and only when "
        "an unambiguous single match exists. Everything else is reported below, never fixed automatically."
    )
    lines.append("")
    alt_fixed = (autofix or {}).get("alt_fixed", [])
    link_fixed = (autofix or {}).get("link_fixed", [])
    if not alt_fixed and not link_fixed:
        lines.append("No auto-fixes were applied this run.")
    else:
        if alt_fixed:
            lines.append(f"**Missing alt text fixed ({len(alt_fixed)}):**")
            lines.append("")
            lines += _autofix_table(
                alt_fixed,
                [("Page", "page"), ("Image", "img_src"), ("Alt text added", "alt_text"), ("Source file", "source")],
            )
            lines.append("")
        if link_fixed:
            lines.append(f"**Broken internal links fixed ({len(link_fixed)}):**")
            lines.append("")
            lines += _autofix_table(
                link_fixed,
                [("Page", "page"), ("Old href", "href"), ("New href", "suggested_href"), ("Source file", "source")],
            )
            lines.append("")
        if autofix_pr_url:
            lines.append(f"Changes are on a PR, not committed directly to the default branch: {autofix_pr_url}")
            lines.append("")

    # --- Needs human/AI follow-up ----------------------------------------
    lines.append("## Needs Human/AI Follow-Up")
    lines.append("")
    followup_lines: list[str] = []
    for mode in MODE_ORDER:
        r = results.get(mode, ModeResult())
        if r.ran:
            for item in r.followups:
                followup_lines.append(f"- **{MODE_TITLES[mode]}:** {item}")
    if autofix:
        for e in autofix.get("alt_skipped", []):
            followup_lines.append(
                f"- **HTML Analysis (alt text, not auto-fixed):** `{e.get('page')}` — "
                f"`{e.get('img_src')}` — {e.get('reason', 'skipped')}"
            )
        for e in autofix.get("link_skipped", []):
            followup_lines.append(
                f"- **HTML Analysis (internal link, not auto-fixed):** `{e.get('page')}` — "
                f"`{e.get('href')}` — {e.get('reason', 'skipped')}"
            )
    if followup_lines:
        lines += followup_lines
    else:
        lines.append("Nothing pending this run.")
    lines.append("")

    # --- Critical issues checklist -----------------------------------------
    lines.append("## Critical Issues Checklist")
    lines.append("")
    if total_critical == 0:
        lines.append("- [x] No critical issues found this run.")
    else:
        lines.append(f"- [ ] {total_critical} critical issue(s) found this run — see per-mode Details sections above.")
    lines.append("")

    if keep_legacy_html_analysis:
        lines.append(
            "> Raw HTMLProofer output is also committed at `_drafts/html_analysis.txt` "
            "(kept for 2 migration cycles per the 2026-07-04 spec's Open Question 5, answered 2026-09-26; "
            "drop once the unified report above is trusted)."
        )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def total_critical_count(results: dict[str, ModeResult]) -> int:
    return sum(r.critical_count for r in results.values() if r.ran)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-url", required=True)
    parser.add_argument("--run-date", required=True)
    parser.add_argument("--state-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--autofix-pr-url", default="")
    parser.add_argument("--keep-legacy-html-analysis", default="true")
    parser.add_argument("--github-output", type=Path, default=None,
                         help="If given, append total_critical=<n> to this GitHub Actions output file.")
    args = parser.parse_args()

    results = load_mode_results(args.state_dir)
    autofix = load_autofix(args.state_dir)
    keep_legacy = str(args.keep_legacy_html_analysis).lower() in ("1", "true", "yes")

    report = build_report(
        site_url=args.site_url,
        run_date=args.run_date,
        results=results,
        autofix=autofix,
        autofix_pr_url=args.autofix_pr_url,
        keep_legacy_html_analysis=keep_legacy,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")

    total = total_critical_count(results)
    print(f"Wrote {args.out} ({len(report)} bytes). Total critical issues: {total}")

    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as fh:
            fh.write(f"total_critical={total}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
