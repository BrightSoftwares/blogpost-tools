#!/usr/bin/env python3
"""Align satellite gems of the Jekyll fleet to scripts/jekyll_fleet/versions.yml.

One PR per repo on `claude/automated-work` (never the default branch). Per repo:
clone, read Gemfile.lock, `bundle update <gems> --conservative` for gems below the matrix,
require the lock to land EXACTLY on the matrix (never a downgrade, never beyond), run a real
`bundle exec jekyll build`, then commit + push + open the PR. A repo whose update or build
fails is reported and never opened. A repo without a committed Gemfile.lock is skipped.

DRY-RUN BY DEFAULT: clones, updates and builds locally, prints the plan, pushes nothing.
    GITHUB_TOKEN=... python3 fleet_align_gems.py --repos fleet_repos.txt [--apply] [--only owner/repo]
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fleet_common import GitHub, default_branch, parse_repo_list  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WORK_BRANCH = "claude/automated-work"
LOCK_LINE = re.compile(r"^    ([A-Za-z0-9_.-]+) \((\d+(?:\.\d+)*)[^)]*\)$")


def load_matrix(text: str) -> dict:
    """Parse versions.yml (flat: `ruby: "x"` and a `gems:` block of `name: "ver"`)."""
    out = {"ruby": None, "gems": {}}
    in_gems = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        m = re.fullmatch(r'(\s*)([\w.-]+):\s*"?([^"]*)"?', line)
        if not m:
            raise ValueError(f"bad line in versions.yml: {raw!r}")
        indent, key, val = len(m.group(1)), m.group(2), m.group(3)
        if indent == 0 and key == "gems":
            in_gems = True
        elif indent == 0:
            out[key] = val
            in_gems = False
        elif in_gems:
            out["gems"][key] = val
    if not out["gems"]:
        raise ValueError("versions.yml has no gems")
    return out


def parse_lock(text: str) -> dict:
    """{gem: version} from the `specs:` sections of a Gemfile.lock."""
    gems, in_specs = {}, False
    for line in text.splitlines():
        if line.strip() == "specs:":
            in_specs = True
            continue
        if in_specs and not line.startswith("    "):
            in_specs = False
        m = LOCK_LINE.match(line) if in_specs else None
        if m:
            gems[m.group(1)] = m.group(2)
    return gems


def vkey(v: str):
    return tuple(int(p) for p in v.split("."))


def plan(lock: dict, matrix: dict) -> dict:
    """Return {"update": [gems below target], "ahead": {gem: ver above target}, "ok": [...]}.
    Gems absent from the lock are ignored (the site does not use them)."""
    res = {"update": [], "ahead": {}, "ok": []}
    for gem, target in matrix["gems"].items():
        cur = lock.get(gem)
        if cur is None:
            continue
        if vkey(cur) < vkey(target):
            res["update"].append(gem)
        elif vkey(cur) > vkey(target):
            res["ahead"][gem] = cur
        else:
            res["ok"].append(gem)
    return res


def verify_after(new_lock: dict, matrix: dict, wanted: list) -> list:
    """Problems after the update: every updated gem must sit exactly on the matrix."""
    return [f"{g}: {new_lock.get(g)} != {matrix['gems'][g]}" for g in wanted
            if new_lock.get(g) != matrix["gems"][g]]


def run(cmd, cwd, runner=subprocess.run):
    p = runner(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def align_repo(repo, branch, matrix, workdir, apply, token, runner=subprocess.run, gh=None):
    """Return a one-line result. All git/bundle calls go through `runner` (injectable)."""
    url = f"https://x-access-token:{token}@github.com/{repo}.git"
    dest = os.path.join(workdir, repo.replace("/", "__"))
    rc, out = run(["git", "clone", "-q", "--depth", "50", "--branch", branch, url, dest], workdir, runner)
    if rc:
        return f"{repo}: ERROR clone failed"
    # Start from the work branch if it exists (keeps earlier unmerged work), else from the default branch.
    rc, _ = run(["git", "fetch", "-q", "origin", WORK_BRANCH], dest, runner)
    run(["git", "checkout", "-q", "-B", WORK_BRANCH, f"origin/{WORK_BRANCH}" if rc == 0 else branch], dest, runner)
    lock_path = os.path.join(dest, "Gemfile.lock")
    if not os.path.exists(lock_path):
        return f"{repo}: SKIP (no committed Gemfile.lock)"
    with open(lock_path, encoding="utf-8") as fh:
        before = parse_lock(fh.read())
    pl = plan(before, matrix)
    if not pl["update"]:
        note = f"; ahead of matrix (left alone): {pl['ahead']}" if pl["ahead"] else ""
        return f"{repo}: OK, lock already on matrix{note}"
    rc, out = run(["bundle", "update", *pl["update"], "--conservative"], dest, runner)
    if rc:
        return f"{repo}: FAIL bundle update ({out.strip().splitlines()[-1:]}) - no PR"
    with open(lock_path, encoding="utf-8") as fh:
        after = parse_lock(fh.read())
    problems = verify_after(after, matrix, pl["update"])
    if problems:
        return f"{repo}: FAIL lock not on matrix after update ({'; '.join(problems)}) - no PR"
    rc, out = run(["bundle", "exec", "jekyll", "build"], dest, runner)
    if rc:
        return f"{repo}: FAIL jekyll build ({out.strip().splitlines()[-1:]}) - no PR"
    summary = ", ".join(f"{g} {before[g]}->{after[g]}" for g in pl["update"])
    if not apply:
        return f"{repo}: WOULD open PR on {WORK_BRANCH}: {summary} (build green)"
    trailer = os.environ.get("FLEET_COMMIT_TRAILER", "")
    msg = f"chore(deps): align Jekyll fleet gems to versions.yml ({summary})" + (f"\n\n{trailer}" if trailer else "")
    run(["git", "add", "Gemfile.lock"], dest, runner)
    rc, out = run(["git", "-c", "user.name=Claude", "-c", "user.email=774136+fullbright@users.noreply.github.com",
                   "commit", "-q", "-m", msg], dest, runner)
    if rc:
        return f"{repo}: FAIL commit"
    rc, out = run(["git", "push", "-q", "origin", f"HEAD:{WORK_BRANCH}"], dest, runner)
    if rc:
        return f"{repo}: FAIL push (not forced)"
    note = "pushed"
    if gh is not None:
        s, prs = gh.get(f"/repos/{repo}/pulls?state=open&head={repo.split('/')[0]}:{WORK_BRANCH}")
        if s == 200 and prs:
            note += f"; PR already open: {prs[0]['html_url']}"
        else:
            s, pr, _ = gh.request("POST", f"/repos/{repo}/pulls", {
                "title": "chore(deps): align Jekyll fleet gems to versions.yml", "head": WORK_BRANCH, "base": branch,
                "body": f"Aligned by `fleet_align_gems.py`: {summary}. Real `jekyll build` passed before this PR."})
            note += f"; opened PR {pr.get('html_url')}" if s in (200, 201) and pr else f"; PR creation failed (HTTP {s})"
    return f"{repo}: DONE {summary}; {note}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repos", default=os.path.join(HERE, "fleet_repos.txt"))
    ap.add_argument("--matrix", default=os.path.join(HERE, "versions.yml"))
    ap.add_argument("--apply", action="store_true", help="push + open PRs (default: dry-run)")
    ap.add_argument("--only", action="append", default=[], help="restrict to owner/repo (repeatable)")
    args = ap.parse_args(argv)
    with open(args.matrix, encoding="utf-8") as fh:
        matrix = load_matrix(fh.read())
    with open(args.repos, encoding="utf-8") as fh:
        entries = [e for e in parse_repo_list(fh.read()) if not args.only or e[0] in args.only]
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    gh = GitHub.from_env()
    print(("APPLY" if args.apply else "DRY-RUN") + f" over {len(entries)} repos")
    with tempfile.TemporaryDirectory() as wd:
        for repo, branch in entries:
            br = branch or default_branch(gh, repo)
            print(align_repo(repo, br, matrix, wd, args.apply, token, gh=gh) if br else f"{repo}: SKIP (not accessible)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
