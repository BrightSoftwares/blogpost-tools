#!/usr/bin/env python3
"""Align satellite gems of the Jekyll fleet to scripts/jekyll_fleet/versions.yml.

One PR per repo on `claude/automated-work` (never the default branch). Per repo:
clone, merge the default branch into the work branch, read Gemfile.lock, pin the Gemfile
constraint of each gem below the matrix to `= <target>` and run `bundle update <gems> --conservative`,
require the lock to land EXACTLY on the matrix (never a downgrade) with only rubygems.org sources and no
changes to gems outside the matrix, run a real
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
LOCK_LINE = re.compile(r"^    ([A-Za-z0-9_.-]+) \((\d+(?:\.\d+)*(?:\.[A-Za-z][\w.]*)?)(?:-[^)]*)?\)$")


def load_matrix(text: str) -> dict:
    """Parse versions.yml (flat: optional top-level keys and a `gems:` block of `name: "ver"`)."""
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
    """Sortable key: numeric parts, then 0 for a pre-release (1.0.0.rc1 < 1.0.0) or 1 for a release."""
    nums = [int(p) for p in v.split(".") if p.isdigit()]
    pre = any(not p.isdigit() for p in v.split("."))
    return tuple(nums) + (0 if pre else 1,)


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
    res["update"].sort()
    return res


def verify_after(new_lock: dict, matrix: dict, wanted: list) -> list:
    """Problems after the update: every updated gem must sit exactly on the matrix."""
    return [f"{g}: {new_lock.get(g)} != {matrix['gems'][g]}" for g in wanted
            if new_lock.get(g) != matrix["gems"][g]]


SECRET_ENV = ("GITHUB_TOKEN", "GH_TOKEN", "REPO_ACCESS_TOKEN", "FLEET_COMMIT_TRAILER")
NAME_OK = re.compile(r"[\w][\w./-]*")  # no leading '-', so a value can never look like a git option
URL_CRED = re.compile(r"://[^@/\s]+@")


def valid_name(value: str) -> bool:
    return bool(NAME_OK.fullmatch(value)) and ".." not in value


def git_env(token: str, base=None) -> dict:
    """Env for git network calls only: auth via http.extraheader, never in argv or .git/config."""
    import base64
    env = dict(os.environ if base is None else base)
    cred = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    env.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "http.extraheader",
                "GIT_CONFIG_VALUE_0": f"Authorization: basic {cred}", "GIT_TERMINAL_PROMPT": "0"})
    return env


def clean_env(cfg_dir: str, base=None) -> dict:
    """Env for code the fleet controls (bundle, jekyll plugins, git hooks): no secrets."""
    env = {k: v for k, v in (os.environ if base is None else base).items()
           if k not in SECRET_ENV and not k.startswith("GIT_CONFIG_")}
    env["BUNDLE_APP_CONFIG"] = cfg_dir
    return env


def redact(text: str, token: str = "") -> str:
    text = URL_CRED.sub("://<redacted>@", text)
    if token:
        import base64
        text = text.replace(token, "<redacted>").replace(base64.b64encode(f"x-access-token:{token}".encode()).decode(), "<redacted>")
    return text


def pin_gemfile(text: str, targets: dict) -> str:
    """Make bundler land on the EXACT matrix version: rewrite the version constraint of each
    `gem 'name'` line to `'= target'` (other options kept), or append a pinned line for gems that
    are only transitive. A multi-line declaration is not rewritten (a duplicate line is appended,
    which bundler rejects, so the repo fails loudly instead of being half-edited)."""
    lines = text.split("\n")
    done = set()
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*gem\s+['\"]([^'\"]+)['\"])(.*)$", line)
        if m and m.group(2) in targets and m.group(2) not in done:
            rest = m.group(3)
            if rest.rstrip().endswith((",", "\\")):
                continue
            rest = re.sub(r",\s*['\"][~><=! ]*\d[^'\"]*['\"]", "", rest)
            lines[i] = f"{m.group(1)}, '= {targets[m.group(2)]}'{rest}"
            done.add(m.group(2))
    out = "\n".join(lines)
    extra = [f"gem '{g}', '= {v}'" for g, v in targets.items() if g not in done]
    if extra:
        out = out.rstrip("\n") + "\n\n# Pinned by fleet_align_gems.py (scripts/jekyll_fleet/versions.yml)\n" + "\n".join(extra) + "\n"
    return out


def run(cmd, cwd, runner=subprocess.run, env=None):
    p = runner(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def lock_sections(text: str) -> dict:
    """{'GEM': [remote, ...], 'GIT': [...], 'PATH': [...]} from `remote:` lines of each source section."""
    out, cur = {}, None
    for line in text.splitlines():
        if line in ("GEM", "GIT", "PATH"):
            cur = line
            out.setdefault(cur, [])
        elif line and not line.startswith(" "):
            cur = None
        elif cur and line.strip().startswith("remote:"):
            out[cur].append(line.split("remote:", 1)[1].strip())
    return out


def lock_problems(before_text: str, after_text: str, matrix: dict, allow_transitive=False):
    """Return (problems, transitive_changes). Refuses non-rubygems sources, new GIT/PATH sections
    and (unless allowed) any changed gem outside the matrix."""
    problems = []
    b, a = lock_sections(before_text), lock_sections(after_text)
    if any(r != "https://rubygems.org/" for r in a.get("GEM", [])):
        problems.append(f"GEM remote not https://rubygems.org/: {a.get('GEM')}")
    for kind in ("GIT", "PATH"):
        if sorted(a.get(kind, [])) != sorted(b.get(kind, [])):
            problems.append(f"{kind} sources changed: {b.get(kind, [])} -> {a.get(kind, [])}")
    bl, al_ = parse_lock(before_text), parse_lock(after_text)
    changed = sorted(g for g in set(bl) | set(al_) if bl.get(g) != al_.get(g))
    transitive = [f"{g} {bl.get(g)}->{al_.get(g)}" for g in changed if g not in matrix["gems"]]
    if transitive and not allow_transitive:
        problems.append("changes outside the matrix: " + ", ".join(transitive))
    return problems, transitive


def align_repo(repo, branch, matrix, workdir, apply, token, runner=subprocess.run, gh=None, allow_transitive=False,
               trailer=None):
    """Return a one-line result. All git/bundle calls go through `runner` (injectable)."""
    if not valid_name(repo.replace("/", "x", 1)) or not valid_name(branch or ""):
        return f"{repo}: SKIP (invalid repo or branch name)"
    trailer = os.environ.get("FLEET_COMMIT_TRAILER", "") if trailer is None else trailer
    genv = git_env(token)
    os.makedirs(workdir, exist_ok=True)
    cfg = tempfile.mkdtemp(prefix="bundlecfg-", dir=workdir)
    cenv = clean_env(cfg)
    url = f"https://github.com/{repo}.git"  # clean URL: no credentials anywhere on disk or in argv
    dest = os.path.join(workdir, repo.replace("/", "__"))
    rc, out = run(["git", "clone", "-q", "--depth", "50", "--branch", branch, "--", url, dest], workdir, runner, genv)
    if rc:
        return f"{repo}: ERROR clone failed"
    run(["git", "remote", "set-url", "origin", url], dest, runner, cenv)
    # Start from the work branch if it exists (keeps earlier unmerged work), else from the default branch.
    rc, _ = run(["git", "fetch", "-q", "--depth", "50", "origin", WORK_BRANCH], dest, runner, genv)
    unreviewed = ""
    if rc == 0:
        run(["git", "checkout", "-q", "-B", WORK_BRANCH, f"origin/{WORK_BRANCH}", "--"], dest, runner, cenv)
        _, unreviewed = run(["git", "log", "--format=%h %s", f"origin/{branch}..HEAD", "--"], dest, runner, cenv)
        if unreviewed.strip():
            # Never push a branch that is behind the default branch (it could revert newer changes).
            rc, out = run(["git", "-c", "user.name=Claude", "-c", "user.email=774136+fullbright@users.noreply.github.com",
                           "merge", "-q", "--no-edit", f"origin/{branch}"], dest, runner, cenv)
            if rc:
                run(["git", "merge", "--abort"], dest, runner, cenv)
                return f"{repo}: FAIL cannot merge origin/{branch} into {WORK_BRANCH} - no PR"
        else:
            run(["git", "checkout", "-q", "-B", WORK_BRANCH, f"origin/{branch}", "--"], dest, runner, cenv)
    else:
        run(["git", "checkout", "-q", "-B", WORK_BRANCH, f"origin/{branch}", "--"], dest, runner, cenv)
    lock_path = os.path.join(dest, "Gemfile.lock")
    gemfile_path = os.path.join(dest, "Gemfile")
    if not os.path.exists(lock_path) or not os.path.exists(gemfile_path):
        return f"{repo}: SKIP (no committed Gemfile and Gemfile.lock)"
    with open(lock_path, encoding="utf-8") as fh:
        before_text = fh.read()
    before = parse_lock(before_text)
    pl = plan(before, matrix)
    ahead = f"; ahead of matrix (left alone): {pl['ahead']}" if pl["ahead"] else ""
    if not pl["update"]:
        return f"{repo}: OK, lock already on matrix{ahead}"
    with open(gemfile_path, encoding="utf-8") as fh:
        gemfile_before = fh.read()
    targets = {g: matrix["gems"][g] for g in pl["update"]}
    with open(gemfile_path, "w", encoding="utf-8") as fh:
        fh.write(pin_gemfile(gemfile_before, targets))
    rc, out = run(["bundle", "update", *pl["update"], "--conservative"], dest, runner, cenv)
    if rc:
        return f"{repo}: FAIL bundle update ({redact(out, token).strip().splitlines()[-1:]}) - no PR"
    with open(lock_path, encoding="utf-8") as fh:
        after_text = fh.read()
    after = parse_lock(after_text)
    problems = verify_after(after, matrix, pl["update"])
    lp, transitive = lock_problems(before_text, after_text, matrix, allow_transitive)
    problems += lp
    if problems:
        return f"{repo}: FAIL lock check ({'; '.join(problems)}) - no PR"
    rc, out = run(["bundle", "exec", "jekyll", "build"], dest, runner, cenv)
    if rc:
        return f"{repo}: FAIL jekyll build ({redact(out, token).strip().splitlines()[-1:]}) - no PR"
    summary = ", ".join(f"{g} {before[g]}->{after[g]}" for g in pl["update"])
    if not apply:
        return f"{repo}: WOULD open PR on {WORK_BRANCH}: {summary} (build green){ahead}"
    msg = f"chore(deps): align Jekyll fleet gems to versions.yml ({summary})" + (f"\n\n{trailer}" if trailer else "")
    run(["git", "add", "--", "Gemfile", "Gemfile.lock"], dest, runner, cenv)
    rc, out = run(["git", "-c", "user.name=Claude", "-c", "user.email=774136+fullbright@users.noreply.github.com",
                   "commit", "-q", "-m", msg], dest, runner, cenv)
    if rc:
        return f"{repo}: FAIL commit"
    rc, out = run(["git", "push", "-q", "origin", f"HEAD:{WORK_BRANCH}"], dest, runner, genv)
    if rc:
        return f"{repo}: FAIL push (not forced)"
    note = "pushed"
    if gh is not None:
        s, prs = gh.get(f"/repos/{repo}/pulls?state=open&head={repo.split('/')[0]}:{WORK_BRANCH}")
        if s == 200 and prs:
            note += f"; PR already open: {prs[0]['html_url']}"
        else:
            body = f"Aligned by `fleet_align_gems.py`: {summary}. Real `jekyll build` passed before this PR."
            if transitive:
                body += "\n\nTransitive gem changes: " + ", ".join(transitive)
            if unreviewed.strip():
                body += "\n\nUnreviewed commits already on `claude/automated-work`:\n" + unreviewed.strip()
            s, pr, _ = gh.request("POST", f"/repos/{repo}/pulls", {
                "title": "chore(deps): align Jekyll fleet gems to versions.yml", "head": WORK_BRANCH, "base": branch,
                "body": body})
            note += f"; opened PR {pr.get('html_url')}" if s in (200, 201) and pr else f"; PR creation failed (HTTP {s})"
    return f"{repo}: DONE {summary}; {note}{ahead}"


def safe_align(repo, *args, **kwargs):
    """One repo failing (even with an exception) never stops the others."""
    try:
        return align_repo(repo, *args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - isolation is the point
        return f"{repo}: ERROR {type(exc).__name__}: {redact(str(exc), args[4] if len(args) > 4 else '')}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repos", default=os.path.join(HERE, "fleet_repos.txt"))
    ap.add_argument("--matrix", default=os.path.join(HERE, "versions.yml"))
    ap.add_argument("--apply", action="store_true", help="push + open PRs (default: dry-run)")
    ap.add_argument("--only", action="append", default=[], help="restrict to owner/repo (repeatable)")
    ap.add_argument("--allow-transitive", action="store_true",
                    help="accept changes to gems outside the matrix (they are listed in the PR body)")
    args = ap.parse_args(argv)
    if any(not valid_name(o.replace("/", "x", 1)) for o in args.only):
        ap.error("--only values must match [\\w./-]+ with no leading '-'")
    with open(args.matrix, encoding="utf-8") as fh:
        matrix = load_matrix(fh.read())
    with open(args.repos, encoding="utf-8") as fh:
        entries = [e for e in parse_repo_list(fh.read()) if not args.only or e[0] in args.only]
    bad = [e for e in entries if e[1] is not None and not valid_name(e[1])]
    if bad:
        ap.error(f"invalid branch in repo list: {bad}")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    gh = GitHub.from_env()
    print(("APPLY" if args.apply else "DRY-RUN") + f" over {len(entries)} repos")
    with tempfile.TemporaryDirectory() as wd:
        for repo, branch in entries:
            br = branch or default_branch(gh, repo)
            print(safe_align(repo, br, matrix, wd, args.apply, token, gh=gh, allow_transitive=args.allow_transitive) if br else f"{repo}: SKIP (not accessible)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
