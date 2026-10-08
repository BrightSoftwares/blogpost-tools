#!/usr/bin/env python3
"""Markdown table of open Dependabot alerts (by severity) + hygiene signals per repo.

Read-only. Usage:
    GITHUB_TOKEN=... python3 fleet_dependabot_report.py --repos fleet_repos.txt [--output report.md]

Columns: alerts by severity, whether .github/dependabot.yml exists, age of
Gemfile.lock's last commit, and how the repo consumes the shared wikilinks plugin
(`gem` = shared gem, `local-copy` = _plugins/wikilinks.rb, `none`).
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fleet_common import SEVERITIES, GitHub, GitHubError, default_branch, parse_repo_list  # noqa: E402


def alert_counts(gh: GitHub, repo: str):
    """Return (counts dict, note). note is '' on success, else why alerts are unavailable."""
    status, data, _ = gh.request("GET", f"/repos/{repo}/dependabot/alerts?state=open&per_page=1")
    if status != 200:
        msg = (data or {}).get("message", "") if isinstance(data, dict) else ""
        if "disabled" in msg.lower():
            return None, "alerts disabled"
        return None, f"HTTP {status}"
    counts = {s: 0 for s in SEVERITIES}
    try:
        for alert in gh.paginate(f"/repos/{repo}/dependabot/alerts?state=open"):
            sev = ((alert.get("security_advisory") or {}).get("severity") or "").lower()
            if sev in counts:
                counts[sev] += 1
    except GitHubError as err:
        return None, f"HTTP {err.status} while paging"
    return counts, ""


def wikilinks_mode(gh: GitHub, repo: str, branch: str) -> str:
    _, gemfile, _ = gh.file_text(repo, "Gemfile", branch)
    if gemfile and "jekyll-obsidian-wikilinks" in gemfile:
        return "gem"
    status, _, _ = gh.file_text(repo, "_plugins/wikilinks.rb", branch)
    return "local-copy" if status == 200 else "none"


def lock_age_days(gh: GitHub, repo: str, branch: str, today: "dt.date | None" = None):
    status, data = gh.get(f"/repos/{repo}/commits?path=Gemfile.lock&per_page=1&sha={branch}")
    if status != 200 or not data:
        return None
    day = dt.date.fromisoformat(data[0]["commit"]["committer"]["date"][:10])
    return ((today or dt.date.today()) - day).days


def collect(gh: GitHub, entries, today=None):
    rows = []
    for repo, branch in entries:
        branch = branch or default_branch(gh, repo)
        if not branch:
            rows.append({"repo": repo, "error": "repo not accessible"})
            continue
        counts, note = alert_counts(gh, repo)
        status, _, _ = gh.file_text(repo, ".github/dependabot.yml", branch)
        rows.append({
            "repo": repo, "branch": branch, "counts": counts, "note": note,
            "dependabot_yml": status == 200,
            "lock_age": lock_age_days(gh, repo, branch, today),
            "wikilinks": wikilinks_mode(gh, repo, branch),
        })
    return rows


def render(rows) -> str:
    head = ("| Repo | Branch | Crit | High | Med | Low | Total | dependabot.yml | Gemfile.lock age | wikilinks |\n"
            "|---|---|--:|--:|--:|--:|--:|:-:|--:|:-:|\n")
    lines = []
    totals = {s: 0 for s in SEVERITIES}
    for r in rows:
        if "error" in r:
            lines.append(f"| {r['repo']} | - | - | - | - | - | - | - | - | {r['error']} |")
            continue
        c = r["counts"]
        if c is None:
            cells = [f"n/a ({r['note']})", "", "", "", ""]
            total = "n/a"
        else:
            for s in SEVERITIES:
                totals[s] += c[s]
            cells = [str(c[s]) for s in SEVERITIES]
            total = str(sum(c.values()))
        age = "?" if r["lock_age"] is None else f"{r['lock_age']}d"
        lines.append(f"| {r['repo']} | {r['branch']} | {' | '.join(cells[:4])} | {total} | "
                     f"{'yes' if r['dependabot_yml'] else 'NO'} | {age} | {r['wikilinks']} |")
    lines.append(f"| **Fleet total** | | {totals['critical']} | {totals['high']} | {totals['medium']} | "
                 f"{totals['low']} | {sum(totals.values())} | | | |")
    unknown = sum(1 for r in rows if "error" in r or r["counts"] is None)
    foot = f"\n_Totals exclude {unknown} repo(s) whose alerts could not be read (n/a)._\n" if unknown else ""
    return head + "\n".join(lines) + "\n" + foot


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repos", required=True, help="file with `owner/repo [branch]` lines")
    ap.add_argument("--output", help="write markdown here instead of stdout")
    args = ap.parse_args(argv)
    with open(args.repos, encoding="utf-8") as fh:
        entries = parse_repo_list(fh.read())
    table = render(collect(GitHub.from_env(), entries))
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(table)
    else:
        sys.stdout.write(table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
