#!/usr/bin/env python3
"""Close Dependabot PRs that are superseded, obsolete or out of scope across the Jekyll fleet.

DRY-RUN BY DEFAULT: prints what would be closed and why. Pass --apply to close.
Closing is reversible (reopen the PR); nothing is deleted, branches are never touched.
Only PRs authored by `dependabot[bot]` are considered. Each close posts a one-line
comment naming the rule.

Rules, evaluated in this order (first match wins):

  A  wrong-direction        every update in the PR moves a version/tag DOWN (target < the PR's
                            own "from"). Known case: jekyll-obsidian-wikilinks-v2.1.1 -> v2.1.0.
  C  out-of-scope           ecosystem not in templates/dependabot.yml (e.g. npm), or a pip
                            directory outside PIP_SCOPE_DIRS (tooling, not the Jekyll build).
  B  obsolete               every update targets a version <= the one already on the default
                            branch (Gemfile.lock, else Gemfile) and the PR is >= STALE_DAYS old;
                            OR the PR is >= CONFLICT_STALE_DAYS old and GitHub reports it
                            unmergeable (a base from years ago; Dependabot re-opens a fresh PR
                            if the bump is still wanted).
  D  lock-already-satisfies same version test as B for a younger PR (the lock moved after the PR
                            was opened, e.g. after a fleet alignment).

    GITHUB_TOKEN=... python3 fleet_close_superseded_dependabot.py [--repos fleet_repos.txt] [--apply]
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fleet_common import PIP_SCOPE_DIRS, GitHub, GitHubError, default_branch, parse_repo_list  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "templates", "dependabot.yml")
DEFAULT_REPOS = os.path.join(HERE, "fleet_repos.txt")
ECO_MARKER = re.compile(r"^# --- ecosystem: ([\w-]+) ---$", re.M)

DEPENDABOT = "dependabot[bot]"
STALE_DAYS = 30
CONFLICT_STALE_DAYS = 180
MERGEABLE_RETRIES = 3
MERGEABLE_WAIT = 2

# branch segment -> ecosystem name used in the template
ECO_ALIASES = {"npm_and_yarn": "npm", "github_actions": "github-actions"}


# ---------------------------------------------------------------- parsing helpers

def parse_version(text: "str | None"):
    """First dotted number sequence in `text` as a tuple of ints, or None.
    'jekyll-obsidian-wikilinks-v2.1.1' -> (2,1,1); '~> 2.9.1' -> (2,9,1); '1.17.4-x86_64-linux' -> (1,17,4)."""
    m = re.search(r"\d+(?:\.\d+)*", text or "")
    return tuple(int(p) for p in m.group(0).split(".")) if m else None


def cmp_versions(a, b) -> int:
    n = max(len(a), len(b))
    a, b = a + (0,) * (n - len(a)), b + (0,) * (n - len(b))
    return (a > b) - (a < b)


def template_ecosystems(template: str):
    return set(ECO_MARKER.findall(template))


def pr_ecosystem(branch: str) -> "str | None":
    m = re.match(r"dependabot/([^/]+)/", branch or "")
    if not m:
        return None
    return ECO_ALIASES.get(m.group(1), m.group(1))


_BODY_UPDATE = re.compile(r"Updates `([^`]+)`(?: from (\S+))? to (\S+)")
_BODY_BUMPS = re.compile(r"Bumps \[([^\]]+)\]\([^)]*\) from (\S+) to (\S+?)\.?(?:\s|$)")
_TITLE_UPDATE = re.compile(
    r"(?:[Bb]ump|[Uu]pdate)s?\s+(\S+)\s+(?:requirement\s+)?from\s+(.+?)\s+to\s+(.+?)(?:\s+in\s+/\S*)?\s*$")
_TITLE_DIR = re.compile(r"\sin\s+(/\S*)\s*$")


def parse_updates(title: str, body: str):
    """Return [(name, from_text|None, to_text)]. Body is authoritative (group PRs), title is the fallback."""
    found = [(n, f or None, t.rstrip(".")) for n, f, t in _BODY_UPDATE.findall(body or "")]
    if not found:
        found = [(n, f, t) for n, f, t in _BODY_BUMPS.findall(body or "")]
    if not found:
        m = _TITLE_UPDATE.search(title or "")
        if m:
            found = [(m.group(1), m.group(2), m.group(3))]
    return found


def pr_directory(gh: GitHub, repo: str, pr: dict) -> str:
    m = _TITLE_DIR.search(pr.get("title") or "")
    if m:
        return m.group(1)
    eco = pr_ecosystem(pr["head"]["ref"])
    if eco in ("bundler", "github-actions"):
        return "/"
    status, files = gh.get(f"/repos/{repo}/pulls/{pr['number']}/files?per_page=100")
    if status == 200 and files:
        dirs = {("/" + f["filename"].rsplit("/", 1)[0]) if "/" in f["filename"] else "/" for f in files}
        return sorted(dirs)[0]
    return "/"


# ---------------------------------------------------------------- default-branch versions

def lock_version(lock: "str | None", name: str):
    if not lock:
        return None
    best = None
    for m in re.finditer(rf"^    {re.escape(name)} \(([^)]+)\)", lock, re.M):
        v = parse_version(m.group(1))
        if v and (best is None or cmp_versions(v, best) > 0):
            best = v
    return best


def gemfile_version(gemfile: "str | None", name: str):
    """Version declared in the Gemfile for `name`: git `tag:` if present, else the first constraint."""
    if not gemfile:
        return None
    lines = gemfile.splitlines()
    for i, line in enumerate(lines):
        if re.match(rf"\s*gem\s+['\"]{re.escape(name)}['\"]", line) and not line.lstrip().startswith("#"):
            stmt = [line]  # the statement continues while a line ends with a comma
            while stmt[-1].rstrip().endswith(",") and i + len(stmt) < len(lines):
                stmt.append(lines[i + len(stmt)])
            window = "\n".join(stmt)
            tag = re.search(r"tag:\s*['\"]([^'\"]+)['\"]", window)
            if tag:
                return parse_version(tag.group(1))
            req = re.match(rf"\s*gem\s+['\"]{re.escape(name)}['\"]\s*,\s*['\"]([^'\"]+)['\"]", line)
            return parse_version(req.group(1)) if req else None
    return None


def current_version(lock, gemfile, name):
    return lock_version(lock, name) or gemfile_version(gemfile, name)


# ---------------------------------------------------------------- classification

class Verdict:
    def __init__(self, rule: str, reason: str):
        self.rule, self.reason = rule, reason

    def __repr__(self):
        return f"Verdict({self.rule!r}, {self.reason!r})"


def age_days(pr: dict, today: dt.date) -> int:
    created = dt.date.fromisoformat(pr["created_at"][:10])
    return (today - created).days


def classify(gh: GitHub, repo: str, pr: dict, ctx: dict, today: dt.date, sleep=time.sleep) -> "Verdict | None":
    """Return a Verdict if the PR should be closed, else None. `ctx` carries per-repo
    {'ecosystems', 'pip_dirs', 'lock', 'gemfile'}."""
    if (pr.get("user") or {}).get("login") != DEPENDABOT:
        return None
    eco = pr_ecosystem(pr["head"]["ref"])
    if eco is None:
        return None
    updates = parse_updates(pr.get("title", ""), pr.get("body", ""))
    parsed = [(n, parse_version(f), parse_version(t)) for n, f, t in updates]
    lock, gemfile = ctx.get("lock"), ctx.get("gemfile")

    # Rule A: wrong direction
    if eco in ("bundler", "pip") and parsed and all(t is not None for _, _, t in parsed):
        def is_down(name, frm, to):
            return frm is not None and cmp_versions(to, frm) < 0
        if all(is_down(*u) for u in parsed):
            names = ", ".join(n for n, _, _ in parsed)
            return Verdict("A wrong-direction", f"downgrades {names}")

    # Rule C: out of scope
    if eco not in ctx["ecosystems"]:
        return Verdict("C out-of-scope", f"ecosystem {eco} is not in the canonical Dependabot template")
    if eco == "pip":
        directory = pr_directory(gh, repo, pr)
        if directory not in ctx["pip_dirs"]:
            return Verdict("C out-of-scope", f"pip directory {directory} is tooling, not the Jekyll build")

    # Rule B / D: version already satisfied on the default branch (bundler only)
    if eco == "bundler" and parsed and all(t is not None for _, _, t in parsed):
        curs = [(n, t, current_version(lock, gemfile, n)) for n, _, t in parsed]
        if all(cur is not None and cmp_versions(t, cur) <= 0 for _, t, cur in curs):
            detail = ", ".join(f"{n} {'.'.join(map(str, t))} <= {'.'.join(map(str, cur))}" for n, t, cur in curs)
            if age_days(pr, today) >= STALE_DAYS:
                return Verdict("B obsolete", f"default branch already has it ({detail})")
            return Verdict("D lock-already-satisfies", f"default branch already has it ({detail})")

    # Rule B (stale + conflicting): a base so old that GitHub cannot merge it any more
    if age_days(pr, today) >= CONFLICT_STALE_DAYS:
        full = None
        for attempt in range(MERGEABLE_RETRIES):  # GitHub computes `mergeable` lazily: null on first read
            status, full = gh.get(f"/repos/{repo}/pulls/{pr['number']}")
            if status != 200 or not full or full.get("mergeable") is not None:
                break
            sleep(MERGEABLE_WAIT)
        if full and full.get("mergeable") is False:
            return Verdict("B obsolete", f"open {age_days(pr, today)} days and no longer mergeable (conflicting base)")
    return None


def repo_context(gh: GitHub, repo: str, branch: str, template_eco, pip_dirs, cache=None):
    _, lock, _ = gh.file_text(repo, "Gemfile.lock", branch)
    _, gemfile, _ = gh.file_text(repo, "Gemfile", branch)
    return {"ecosystems": template_eco, "pip_dirs": set(pip_dirs), "lock": lock, "gemfile": gemfile}


def close_pr(gh: GitHub, repo: str, number: int, verdict: Verdict) -> bool:
    comment = (f"Closed by blogpost-tools fleet_close_superseded_dependabot (rule {verdict.rule}): "
               f"{verdict.reason}. Reopen this PR if that was wrong.")
    s1, _, _ = gh.request("POST", f"/repos/{repo}/issues/{number}/comments", {"body": comment})
    s2, _, _ = gh.request("PATCH", f"/repos/{repo}/pulls/{number}", {"state": "closed"})
    return s1 in (200, 201) and s2 == 200


def scan(gh: GitHub, entries, template: str, pip_dirs=PIP_SCOPE_DIRS, today=None, sleep=time.sleep):
    """Return (results, kept, errors). results = [(repo, number, title, Verdict)]."""
    today = today or dt.date.today()
    template_eco = template_ecosystems(template)
    results, kept, errors = [], [], []
    for repo, branch in entries:
        branch = branch or default_branch(gh, repo)
        if not branch:
            errors.append(f"{repo}: repo not accessible")
            continue
        try:
            prs = list(gh.paginate(f"/repos/{repo}/pulls?state=open"))
        except GitHubError as err:
            errors.append(f"{repo}: {err}")
            continue
        dep = [p for p in prs if (p.get("user") or {}).get("login") == DEPENDABOT]
        if not dep:
            continue
        ctx = repo_context(gh, repo, branch, template_eco, pip_dirs)
        for pr in dep:
            verdict = classify(gh, repo, pr, ctx, today, sleep)
            if verdict:
                results.append((repo, pr["number"], pr["title"], verdict))
            else:
                kept.append((repo, pr["number"], pr["title"]))
    return results, kept, errors


def render(results, kept, errors, apply: bool, outcomes=None) -> str:
    outcomes = outcomes or {}
    out = [("APPLY" if apply else "DRY-RUN") + f": {len(results)} PR(s) to close, {len(kept)} kept"]
    by_rule: dict = {}
    for repo, number, title, v in results:
        by_rule.setdefault(v.rule, []).append((repo, number, title, v))
    for rule in sorted(by_rule):
        out.append(f"\n## Rule {rule} ({len(by_rule[rule])})")
        for repo, number, title, v in by_rule[rule]:
            status = outcomes.get((repo, number))
            mark = "" if status is None else (" [closed]" if status else " [FAILED to close]")
            out.append(f"- {repo}#{number}: {title} -- {v.reason}{mark}")
    if kept:
        out.append(f"\n## Kept open ({len(kept)})")
        for repo, number, title in kept:
            out.append(f"- {repo}#{number}: {title}")
    for e in errors:
        out.append(f"\nERROR {e}")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repos", default=DEFAULT_REPOS)
    ap.add_argument("--apply", action="store_true", help="actually close PRs (default: dry-run)")
    ap.add_argument("--pip-scope-dir", action="append", default=None,
                    help=f"pip directory that is in scope (repeatable; default {', '.join(PIP_SCOPE_DIRS)})")
    ap.add_argument("--output", help="also write the report here")
    args = ap.parse_args(argv)
    with open(args.repos, encoding="utf-8") as fh:
        entries = parse_repo_list(fh.read())
    with open(TEMPLATE, encoding="utf-8") as fh:
        template = fh.read()
    gh = GitHub.from_env()
    results, kept, errors = scan(gh, entries, template, args.pip_scope_dir or PIP_SCOPE_DIRS)
    outcomes = {}
    if args.apply:
        for repo, number, _, verdict in results:
            outcomes[(repo, number)] = close_pr(gh, repo, number, verdict)
    report = render(results, kept, errors, args.apply, outcomes)
    sys.stdout.write(report)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
    failed = any(v is False for v in outcomes.values())
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
