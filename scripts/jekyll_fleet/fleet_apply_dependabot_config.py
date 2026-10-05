#!/usr/bin/env python3
"""Open/update one PR per repo that adds the canonical Dependabot config.

DRY-RUN BY DEFAULT: prints what would change. Pass --apply to write.
Only branch `claude/automated-work` is ever written (never the default branch);
the PR is opened against the repo's default branch. Merging is left to a human.

    GITHUB_TOKEN=... python3 fleet_apply_dependabot_config.py --repos fleet_repos.txt [--apply]
        [--enable-alerts]   # also PUT /vulnerability-alerts where alerts are disabled (needs admin)
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fleet_common import GitHub, default_branch, parse_repo_list  # noqa: E402

WORK_BRANCH = "claude/automated-work"
CONFIG_PATH = ".github/dependabot.yml"
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "dependabot.yml")
MARKER = re.compile(r"^# --- ecosystem: ([\w-]+) ---$", re.M)
PIP_MANIFESTS = ("Pipfile", "Pipfile.lock", "requirements.txt", "pyproject.toml", "setup.py")


EXCLUDED_DIRS = {"vendor", "node_modules", ".bundle", ".git", ".venv", "venv", "env", "site-packages", "__pycache__"}


def render_config(template: str, ecosystems) -> str:
    """Keep the header plus the blocks of the requested ecosystems (template order).

    `ecosystems` is either an iterable of names (directory "/") or a dict
    {name: [directories]}: one block is emitted per directory.
    """
    wanted = {e: ["/"] for e in ecosystems} if not isinstance(ecosystems, dict) else ecosystems
    parts = MARKER.split(template)  # [header, name1, body1, name2, body2, ...]
    out = parts[0]
    for name, body in zip(parts[1::2], parts[2::2]):
        for directory in wanted.get(name, []):
            out += body.replace('directory: "/"', f'directory: "{directory}"', 1)
    return out


def _pip_dirs(paths):
    dirs = set()
    for path in paths:
        if EXCLUDED_DIRS & set(path.split("/")[:-1]):
            continue
        name = path.rsplit("/", 1)[-1]
        if name in PIP_MANIFESTS:
            dirs.add("/" + path.rsplit("/", 1)[0] if "/" in path else "/")
    return sorted(dirs)


def detect_ecosystems(gh: GitHub, repo: str, branch: str, extra_pip_dirs=()):
    """Return ({ecosystem: [dirs]}, note). Nested pip manifests (e.g. _data/cleanup_scripts)
    are found via the git tree; vendor/ and node_modules/ are ignored. When GitHub truncates
    the tree only the repo root is inspected and `note` says so (use extra_pip_dirs)."""
    status, tree = gh.get(f"/repos/{repo}/git/trees/{branch}?recursive=1")
    if status != 200 or not isinstance(tree, dict):
        return {}, f"cannot read tree (HTTP {status})"
    entries = [t["path"] for t in tree.get("tree", []) if t.get("type") == "blob"]
    note = ""
    if tree.get("truncated"):
        note = "tree truncated: nested manifests may be missed (pass --pip-dir for known ones)"
    eco = {}
    if "Gemfile" in entries:
        eco["bundler"] = ["/"]
    if any(e.startswith(".github/workflows/") for e in entries):
        eco["github-actions"] = ["/"]
    pip = set(_pip_dirs(entries)) | {d if d.startswith("/") else "/" + d for d in extra_pip_dirs}
    if pip:
        eco["pip"] = sorted(pip)
    return eco, note


def _normalise(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def ensure_branch(gh: GitHub, repo: str, base: str, apply: bool):
    """Return a note. Creates the work branch from base, or fast-forwards it if it is
    not ahead of base (i.e. already merged). A branch with unmerged commits is kept."""
    st, ref = gh.get(f"/repos/{repo}/git/ref/heads/{WORK_BRANCH}")
    st_base, base_ref = gh.get(f"/repos/{repo}/git/ref/heads/{base}")
    if st_base != 200:
        raise RuntimeError(f"cannot read base branch {base}")
    base_sha = base_ref["object"]["sha"]
    if st == 404:
        if apply:
            s, _, _ = gh.request("POST", f"/repos/{repo}/git/refs",
                                 {"ref": f"refs/heads/{WORK_BRANCH}", "sha": base_sha})
            if s not in (200, 201):
                raise RuntimeError(f"could not create {WORK_BRANCH} (HTTP {s})")
        return f"create {WORK_BRANCH} from {base}"
    cmp_status, cmp = gh.get(f"/repos/{repo}/compare/{base}...{WORK_BRANCH}")
    if cmp_status == 200 and cmp.get("ahead_by", 1) == 0:
        if apply and cmp.get("behind_by", 0) > 0:
            s, _, _ = gh.request("PATCH", f"/repos/{repo}/git/refs/heads/{WORK_BRANCH}",
                                 {"sha": base_sha, "force": True})
            if s != 200:
                raise RuntimeError(f"could not reset {WORK_BRANCH} (HTTP {s})")
        return f"{WORK_BRANCH} already merged: fast-forward to {base}"
    return f"reuse existing {WORK_BRANCH} (has unmerged commits)"


def process_repo(gh: GitHub, repo: str, branch, template: str, apply: bool, enable_alerts: bool, pip_dirs=()):
    branch = branch or default_branch(gh, repo)
    if not branch:
        return f"{repo}: SKIP (repo not accessible)"
    eco, tree_note = detect_ecosystems(gh, repo, branch, pip_dirs)
    if not eco:
        return f"{repo}: SKIP (no Gemfile / workflows / pip manifest){'; ' + tree_note if tree_note else ''}"
    label = "+".join(f"{k}({','.join(v)})" if k == "pip" else k for k, v in eco.items())
    wanted = render_config(template, eco)
    _, current, _ = gh.file_text(repo, CONFIG_PATH, branch)
    notes = [tree_note] if tree_note else []
    if enable_alerts:
        s, _ = gh.get(f"/repos/{repo}/dependabot/alerts?per_page=1")
        if s == 403:
            if apply:
                es, _, _ = gh.request("PUT", f"/repos/{repo}/vulnerability-alerts")
                notes.append(f"enabled alerts (HTTP {es})")
            else:
                notes.append("would enable Dependabot alerts")
    if current is not None and _normalise(current) == _normalise(wanted):
        return f"{repo}: OK, config already canonical ({label})" + ("; " + "; ".join(notes) if notes else "")
    verb = "update" if current is not None else "add"
    plan = f"{repo}: WOULD {verb} {CONFIG_PATH} [{label}] on {WORK_BRANCH} and open PR -> {branch}"
    if not apply:
        return plan + ("; " + "; ".join(notes) if notes else "")
    notes.append(ensure_branch(gh, repo, branch, apply=True))
    _, _, file_sha = gh.file_text(repo, CONFIG_PATH, WORK_BRANCH)
    body = {"message": f"chore(deps): {verb} canonical Dependabot config\n\n"
                       "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n"
                       "Claude-Session: https://claude.ai/code/session_011jEKe7ZnVeN2ZXWexAJoAL",
            "content": base64.b64encode(wanted.encode()).decode(), "branch": WORK_BRANCH,
            "committer": {"name": "Claude", "email": "774136+fullbright@users.noreply.github.com"}}
    if file_sha:
        body["sha"] = file_sha
    s, _, _ = gh.request("PUT", f"/repos/{repo}/contents/{CONFIG_PATH}", body)
    if s not in (200, 201):
        return f"{repo}: ERROR writing config (HTTP {s})"
    s, prs = gh.get(f"/repos/{repo}/pulls?state=open&head={repo.split('/')[0]}:{WORK_BRANCH}")
    if s == 200 and prs:
        notes.append(f"PR already open: {prs[0]['html_url']}")
    else:
        s, pr, _ = gh.request("POST", f"/repos/{repo}/pulls", {
            "title": "chore(deps): canonical Dependabot config (Jekyll fleet)",
            "head": WORK_BRANCH, "base": branch,
            "body": "Adds `.github/dependabot.yml` from blogpost-tools `scripts/jekyll_fleet/templates/dependabot.yml`: "
                    "weekly, security updates grouped into one PR per ecosystem.\n\n"
                    "https://claude.ai/code/session_011jEKe7ZnVeN2ZXWexAJoAL"})
        notes.append(f"opened PR {pr.get('html_url')}" if s in (200, 201) and pr else f"PR creation failed (HTTP {s})")
    return f"{repo}: DONE " + "; ".join(notes)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repos", required=True)
    ap.add_argument("--apply", action="store_true", help="actually write (default: dry-run)")
    ap.add_argument("--enable-alerts", action="store_true")
    ap.add_argument("--pip-dir", action="append", default=[],
                    help="extra directory with a Python manifest (repeatable; for truncated trees)")
    args = ap.parse_args(argv)
    with open(args.repos, encoding="utf-8") as fh:
        entries = parse_repo_list(fh.read())
    with open(TEMPLATE, encoding="utf-8") as fh:
        template = fh.read()
    gh = GitHub.from_env()
    print(("APPLY" if args.apply else "DRY-RUN") + f" over {len(entries)} repos")
    for repo, branch in entries:
        print(process_repo(gh, repo, branch, template, args.apply, args.enable_alerts, args.pip_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
