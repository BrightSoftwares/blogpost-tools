#!/usr/bin/env python3
"""Helpers for the reusable Jekyll dependency-audit workflow (stdlib only).

    audit_report.py bundler --input bundle-audit.json [--fail-on high] [--unknown-as medium]
    audit_report.py pipfile-to-requirements Pipfile.lock > requirements-audit.txt
    audit_report.py pip --input pip-audit.json [--fail-on high] [--pip-severity high]

`bundler` reads `bundle-audit check --format json`; `pip` reads `pip-audit -f json`.
pip-audit reports no severity, so every pip finding gets --pip-severity.
Exit code 1 when a finding is at or above --fail-on (`none` never fails), else 0.
A Markdown summary goes to stdout, and is appended to $GITHUB_STEP_SUMMARY when set.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

RANK = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def parse_bundle_audit(text: str, unknown_as: str = "medium"):
    data = json.loads(text)
    findings = []
    for r in data.get("results", []):
        adv = r.get("advisory", {})
        gem = r.get("gem", {})
        sev = (adv.get("criticality") or "").lower()
        findings.append({
            "package": gem.get("name") or r.get("source", "?"),
            "version": gem.get("version", ""),
            "id": adv.get("id") or adv.get("cve") or adv.get("ghsa") or "?",
            "severity": sev if sev in RANK and sev != "none" else unknown_as,
            "title": adv.get("title", ""),
            "url": adv.get("url", ""),
            "kind": r.get("type", ""),
        })
    return findings


def parse_pip_audit(text: str, severity: str = "high"):
    data = json.loads(text)
    deps = data.get("dependencies", data) if isinstance(data, dict) else data
    findings = []
    for dep in deps:
        for v in dep.get("vulns", []):
            findings.append({"package": dep.get("name", "?"), "version": dep.get("version", ""),
                             "id": v.get("id", "?"), "severity": severity,
                             "title": ", ".join(v.get("aliases", [])) or v.get("description", "")[:80],
                             "url": "", "kind": "pip"})
    return findings


def pipfile_lock_to_requirements(text: str, include_dev: bool = True) -> str:
    """Pinned `name==version` lines from a Pipfile.lock (pip-audit cannot read it directly)."""
    data = json.loads(text)
    lines = []
    for section in ("default", "develop") if include_dev else ("default",):
        for name, meta in sorted(data.get(section, {}).items()):
            version = meta.get("version", "")
            if version.startswith("=="):
                lines.append(f"{name}{version}")
    return "\n".join(lines) + ("\n" if lines else "")


def dedupe(findings):
    seen, out = set(), []
    for f in findings:
        key = (f["package"], f["version"], f["id"])
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def evaluate(findings, fail_on: str):
    threshold = RANK[fail_on]
    return threshold > 0 and any(RANK[f["severity"]] >= threshold for f in findings)


def summary(title: str, findings, fail_on: str, failing: bool) -> str:
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in ("critical", "high", "medium", "low")}
    out = [f"### {title}", "",
           f"{len(findings)} finding(s): " + ", ".join(f"{n} {s}" for s, n in counts.items()) +
           f" (fail threshold: {fail_on}) -> **{'FAIL' if failing else 'pass'}**", ""]
    if findings:
        out += ["| Severity | Package | Version | Advisory | Title |", "|---|---|---|---|---|"]
        for f in sorted(findings, key=lambda f: -RANK[f["severity"]])[:50]:
            adv = f"[{f['id']}]({f['url']})" if f["url"] else f["id"]
            out.append(f"| {f['severity']} | {f['package']} | {f['version']} | {adv} | {f['title'][:90].replace('|', '/')} |")
        if len(findings) > 50:
            out.append(f"\n... and {len(findings) - 50} more")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("bundler", "pip"):
        p = sub.add_parser(name)
        p.add_argument("--input", required=True)
        p.add_argument("--fail-on", choices=sorted(RANK), default="high")
        p.add_argument("--unknown-as", choices=["low", "medium", "high", "critical"], default="medium")
        p.add_argument("--pip-severity", choices=["low", "medium", "high", "critical"], default="high")
    conv = sub.add_parser("pipfile-to-requirements")
    conv.add_argument("lockfile")
    args = ap.parse_args(argv)

    if args.cmd == "pipfile-to-requirements":
        with open(args.lockfile, encoding="utf-8") as fh:
            sys.stdout.write(pipfile_lock_to_requirements(fh.read()))
        return 0

    with open(args.input, encoding="utf-8") as fh:
        raw = fh.read()
    if args.cmd == "bundler":
        findings, title = dedupe(parse_bundle_audit(raw, args.unknown_as)), "bundler-audit (Gemfile.lock)"
    else:
        findings, title = dedupe(parse_pip_audit(raw, args.pip_severity)), "pip-audit (Pipfile.lock)"
    failing = evaluate(findings, args.fail_on)
    text = summary(title, findings, args.fail_on, failing)
    sys.stdout.write(text)
    step = os.environ.get("GITHUB_STEP_SUMMARY")
    if step:
        with open(step, "a", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
