#!/usr/bin/env python3
"""Align satellite gems of the Jekyll fleet to scripts/jekyll_fleet/versions.yml, in THREE phases that
never share a process or a directory (a Gemfile or plugin is arbitrary Ruby running as the same user,
so the process that runs it must hold nothing worth stealing, and the process that holds the token must
never run fleet code):

  --phase fetch   token phase. Clones each repo (hardened git, no hooks, no global config), removes .git,
                  writes <out>/<owner__repo>/tree + meta.json. Executes no fleet code.
  --phase build   NO token. Refuses to start if a secret is in its environment. Runs `bundle update` and a
                  real `bundle exec jekyll build` with an ALLOWLIST env (PATH, LANG, temp HOME, temp bundler
                  dirs) on the handed-over tree, and writes only a patch (Gemfile + Gemfile.lock text).
  --phase push    token phase. Validates each patch AS TEXT (rubygems.org only, GIT/PATH/PLATFORMS sections
                  unchanged, Gemfile edits only on matrix gems), applies it in a FRESH clone, pushes
                  `claude/automated-work` (never the default branch) with hooks disabled, opens/reuses the PR.
                  Dry-run unless --apply (dry-run needs no token and no network).

Residual risk: a malicious fleet repo can still run code in the build phase. That phase has no token, no
global git config and a throwaway HOME; run it in its own job/container (see
.github/workflows/fleet-align-gems.yml: build job has `contents: read`, no secrets).

    python3 fleet_align_gems.py --phase fetch --repos fleet_repos.txt --out work     # GITHUB_TOKEN set
    python3 fleet_align_gems.py --phase build --in work --patches patches           # no token
    python3 fleet_align_gems.py --phase push  --patches patches [--apply]            # GITHUB_TOKEN set
"""
from __future__ import annotations

import argparse
import base64
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fleet_common import GitHub, default_branch, parse_repo_list  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WORK_BRANCH = "claude/automated-work"
RUBYGEMS = "https://rubygems.org/"
LOCK_LINE = re.compile(r"^    ([A-Za-z0-9_.-]+) \((\d+(?:\.\d+)*(?:\.[A-Za-z][\w.]*)?)(?:-[^)]*)?\)$")
SECRET_ENV = ("GITHUB_TOKEN", "GH_TOKEN", "REPO_ACCESS_TOKEN", "FLEET_COMMIT_TRAILER")
NAME_OK = re.compile(r"[\w][\w./-]*", re.ASCII)  # no leading '-': a value can never look like a git option
GEM_NAME = re.compile(r"[\w.-]+", re.ASCII)
VERSION = re.compile(r"\d+(\.\w+)*")
URL_CRED = re.compile(r"://[^@/\s]+@")
PIN_COMMENT = "# Pinned by fleet_align_gems.py (scripts/jekyll_fleet/versions.yml)"
LOCK_VARIABLE_HEADERS = {"GEM", "DEPENDENCIES", "CHECKSUMS", "BUNDLED WITH"}


# --------------------------------------------------------------------------- matrix / names / output
def load_matrix(text: str) -> dict:
    """Parse versions.yml (flat: optional top-level keys, an `allow_sources` comma list and a `gems:` block)."""
    out = {"gems": {}, "allow_sources": set()}
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
        elif indent == 0 and key == "allow_sources":
            out["allow_sources"] = {v.strip() for v in val.split(",") if v.strip()}
            in_gems = False
        elif indent == 0:
            out[key] = val
            in_gems = False
        elif in_gems:
            if not GEM_NAME.fullmatch(key) or not VERSION.fullmatch(val):
                raise ValueError(f"bad gem entry in versions.yml: {raw!r}")
            out["gems"][key] = val
    if not out["gems"]:
        raise ValueError("versions.yml has no gems")
    return out


def valid_name(value: str) -> bool:
    return bool(NAME_OK.fullmatch(value)) and ".." not in value


def valid_repo(repo: str) -> bool:
    return bool(re.fullmatch(r"[\w.-]+/[\w.-]+", repo, re.ASCII)) and valid_name(repo.replace("/", "x", 1))


def redact(text: str, token: str = "") -> str:
    text = URL_CRED.sub("://<redacted>@", text)
    if token:
        text = text.replace(token, "<redacted>")
        text = text.replace(base64.b64encode(f"x-access-token:{token}".encode()).decode(), "<redacted>")
    return text


def safe_line(text: str, token: str = "") -> str:
    """Printable, single-line, CI-safe: redacted, control characters escaped, leading `::` neutralised
    (a line starting with `::` is a GitHub Actions workflow command)."""
    text = redact(str(text), token)
    text = "".join(c if c.isprintable() else f"\\x{ord(c):02x}" for c in text)
    return ("\\" + text) if text.startswith("::") else text


def say(text: str, token: str = "") -> None:
    print(safe_line(text, token))


# --------------------------------------------------------------------------- lock parsing and checks
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
    """{"update": [gems below target], "ahead": {gem: ver above target}, "ok": [...]}; absent gems ignored."""
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


def lock_blocks(text: str):
    """[(header, block_text)] : the lock is blank-line separated blocks, header = first (unindented) line."""
    blocks = []
    for chunk in re.split(r"\n\s*\n", text.strip("\n")):
        if chunk.strip():
            blocks.append((chunk.split("\n", 1)[0].strip(), chunk))
    return blocks


def _remotes(block: str):
    return [l.split("remote:", 1)[1].strip() for l in block.splitlines() if l.strip().startswith("remote:")]


def sources_problems(lock_text: str, matrix: dict):
    """GEM remote must be exactly rubygems.org; any GIT/PATH remote must be allowlisted in versions.yml."""
    problems = []
    for header, block in lock_blocks(lock_text):
        for remote in _remotes(block):
            if header == "GEM" and remote != RUBYGEMS:
                problems.append(f"GEM remote not {RUBYGEMS}: {remote}")
            if header in ("GIT", "PATH") and remote not in matrix["allow_sources"]:
                problems.append(f"{header} source not allowlisted in versions.yml: {remote}")
    return problems


def lock_problems(before_text: str, after_text: str, matrix: dict, allow_transitive=False):
    """Pure text validation of a lock change. Returns (problems, transitive_changes)."""
    problems = sources_problems(after_text, matrix)
    b, a = lock_blocks(before_text), lock_blocks(after_text)
    for header in {h for h, _ in b} | {h for h, _ in a}:
        if header in LOCK_VARIABLE_HEADERS:
            continue
        if [t for h, t in b if h == header] != [t for h, t in a if h == header]:
            problems.append(f"{header} section changed (compared whole, revisions included)")
    bd = "\n".join(t for h, t in b if h == "DEPENDENCIES")
    ad = "\n".join(t for h, t in a if h == "DEPENDENCIES")
    bl = {l.strip() for l in bd.splitlines() if l.strip() and l.strip() != "DEPENDENCIES"}
    al_ = {l.strip() for l in ad.splitlines() if l.strip() and l.strip() != "DEPENDENCIES"}
    stray = sorted({l.split(" ", 1)[0].rstrip("!") for l in bl ^ al_} - set(matrix["gems"]))
    if stray:
        problems.append("DEPENDENCIES changed outside the matrix: " + ", ".join(stray))
    bp, ap = parse_lock(before_text), parse_lock(after_text)
    for gem, ver in ap.items():
        if not GEM_NAME.fullmatch(gem) or not VERSION.fullmatch(ver):
            if not re.fullmatch(r"\d+(\.\d+)*(\.[A-Za-z][\w.]*)?", ver):
                problems.append(f"odd gem or version in lock: {gem} {ver}")
    changed = sorted(g for g in set(bp) | set(ap) if bp.get(g) != ap.get(g))
    transitive = [f"{g} {bp.get(g)}->{ap.get(g)}" for g in changed if g not in matrix["gems"]]
    if transitive and not allow_transitive:
        problems.append("changes outside the matrix: " + ", ".join(transitive))
    return problems, transitive


def verify_after(new_lock: dict, matrix: dict, wanted: list) -> list:
    return [f"{g}: {new_lock.get(g)} != {matrix['gems'][g]}" for g in wanted if new_lock.get(g) != matrix["gems"][g]]


def pin_gemfile(text: str, targets: dict) -> str:
    """Make bundler land on the EXACT matrix version: rewrite the version constraint of each `gem 'name'`
    line to `'= target'` (other options kept), or append a pinned line for gems that are only transitive.
    A multi-line declaration is not rewritten (a duplicate line is appended, which bundler rejects)."""
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
        out = out.rstrip("\n") + "\n\n" + PIN_COMMENT + "\n" + "\n".join(extra) + "\n"
    return out


def gemfile_problems(before: str, after: str, matrix: dict):
    """Only `gem` lines of matrix gems (pinned to the matrix version) and the pin comment may change."""
    problems = []
    for line in difflib.unified_diff(before.split("\n"), after.split("\n"), lineterm="", n=0):
        if line.startswith(("---", "+++", "@@")):
            continue
        body = line[1:]
        if not body.strip() or body.strip() == PIN_COMMENT:
            continue
        m = re.match(r"^\s*gem\s+['\"]([\w.-]+)['\"]", body)
        if not m or m.group(1) not in matrix["gems"]:
            problems.append(f"Gemfile change outside the matrix: {body.strip()[:80]!r}")
        elif line.startswith("+"):
            pin = re.search(r",\s*'= (\d+(?:\.\w+)*)'", body)
            if not pin or pin.group(1) != matrix["gems"][m.group(1)]:
                problems.append(f"Gemfile line for {m.group(1)} not pinned to the matrix version")
    return problems


# --------------------------------------------------------------------------- files, envs, subprocess
def read_regular(path: str, root: str) -> str:
    """Read a regular file inside root: refuse symlinks (lstat + realpath containment + O_NOFOLLOW)."""
    if os.path.islink(path):
        raise ValueError(f"{os.path.basename(path)} is a symlink")
    if not os.path.realpath(path).startswith(os.path.realpath(root) + os.sep):
        raise ValueError(f"{os.path.basename(path)} resolves outside the repository")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, encoding="utf-8") as fh:
        return fh.read()


def write_regular(path: str, root: str, text: str) -> None:
    if os.path.islink(path):
        raise ValueError(f"{os.path.basename(path)} is a symlink")
    if not os.path.realpath(os.path.dirname(path)).startswith(os.path.realpath(root)):
        raise ValueError("path resolves outside the repository")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)


PASS_NET = ("HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "https_proxy", "http_proxy", "no_proxy", "SSL_CERT_FILE", "GIT_SSL_CAINFO")


def git_env(home: str, token: str = "") -> dict:
    """Env for the token phases' git calls: no global/system config; auth, if any, scoped to github.com
    via an http.<url>.extraheader (never in argv, never on disk) and redirects disabled."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": home, "LANG": "C.UTF-8",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"}
    if token:
        cred = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        env.update({k: os.environ[k] for k in PASS_NET if k in os.environ})
        env.update({"GIT_CONFIG_COUNT": "2",
                    "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
                    "GIT_CONFIG_VALUE_0": f"Authorization: basic {cred}",
                    "GIT_CONFIG_KEY_1": "http.followRedirects", "GIT_CONFIG_VALUE_1": "false"})
    return env


def build_env(tmp: str, passthrough=()) -> dict:
    """Allowlist env for code the fleet controls. Nothing else is inherited."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8", "HOME": tmp, "TMPDIR": tmp,
           "BUNDLE_APP_CONFIG": os.path.join(tmp, "bundle-app"), "BUNDLE_USER_HOME": os.path.join(tmp, "bundle-user")}
    for name in passthrough:  # explicit, non-secret opt-ins only (e.g. SSL_CERT_FILE)
        if name in SECRET_ENV:
            raise ValueError(f"refusing to pass {name} to the build phase")
        if name in os.environ:
            env[name] = os.environ[name]
    return env


def run(cmd, cwd, runner=subprocess.run, env=None):
    p = runner(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def git(args, cwd, runner, env):
    """Every git call of the token phases: hooks disabled."""
    return run(["git", "-c", "core.hooksPath=/dev/null", *args], cwd, runner, env)


# --------------------------------------------------------------------------- phase: fetch
def fetch_repo(repo, branch, outdir, token, runner=subprocess.run):
    if not valid_repo(repo) or not valid_name(branch or ""):
        return f"{repo}: SKIP (invalid repo or branch name)"
    base = os.path.join(outdir, repo.replace("/", "__"))
    shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base)
    home = tempfile.mkdtemp(prefix="fetchhome-")
    try:
        tree = os.path.join(base, "tree")
        rc, _ = git(["clone", "-q", "--depth", "1", "--branch", branch, "--", f"https://github.com/{repo}.git", tree],
                    base, runner, git_env(home, token))
        if rc:
            return f"{repo}: ERROR clone failed"
        shutil.rmtree(os.path.join(tree, ".git"), ignore_errors=True)  # hand over a plain directory
        with open(os.path.join(base, "meta.json"), "w", encoding="utf-8") as fh:
            json.dump({"repo": repo, "branch": branch}, fh)
        return f"{repo}: fetched {branch}"
    finally:
        shutil.rmtree(home, ignore_errors=True)


# --------------------------------------------------------------------------- phase: build (NO token)
def build_repo(repo, branch, tree, matrix, runner=subprocess.run, passthrough=()):
    """Return ("PATCH", dict) or ("MSG", text). Runs fleet code, so it must hold no secret."""
    leaked = [k for k in SECRET_ENV if os.environ.get(k)]
    if leaked:
        raise RuntimeError(f"build phase refuses to run with secrets in the environment: {leaked}")
    tmp = tempfile.mkdtemp(prefix="buildhome-")
    try:
        env = build_env(tmp, passthrough)
        lock_path, gemfile_path = os.path.join(tree, "Gemfile.lock"), os.path.join(tree, "Gemfile")
        if not (os.path.lexists(lock_path) and os.path.lexists(gemfile_path)):
            return "MSG", f"{repo}: SKIP (no committed Gemfile and Gemfile.lock)"
        try:
            before_text, gemfile_before = read_regular(lock_path, tree), read_regular(gemfile_path, tree)
        except (ValueError, OSError) as exc:
            return "MSG", f"{repo}: FAIL {exc} - refused"
        problems = sources_problems(before_text, matrix)
        if problems:
            return "MSG", f"{repo}: FAIL {'; '.join(problems)} - no patch"
        before = parse_lock(before_text)
        pl = plan(before, matrix)
        ahead = f"; ahead of matrix (left alone): {pl['ahead']}" if pl["ahead"] else ""
        if not pl["update"]:
            return "MSG", f"{repo}: OK, lock already on matrix{ahead}"
        write_regular(gemfile_path, tree, pin_gemfile(gemfile_before, {g: matrix["gems"][g] for g in pl["update"]}))
        rc, out = run(["bundle", "update", *pl["update"], "--conservative"], tree, runner, env)
        if rc:
            return "MSG", f"{repo}: FAIL bundle update ({redact(out).strip().splitlines()[-1:]}) - no patch"
        try:
            after_text, gemfile_after = read_regular(lock_path, tree), read_regular(gemfile_path, tree)
        except (ValueError, OSError) as exc:
            return "MSG", f"{repo}: FAIL {exc} after update - refused"
        after = parse_lock(after_text)
        problems = verify_after(after, matrix, pl["update"])
        lp, transitive = lock_problems(before_text, after_text, matrix, allow_transitive=False)
        problems += lp + gemfile_problems(gemfile_before, gemfile_after, matrix)
        if problems:
            return "MSG", f"{repo}: FAIL checks ({'; '.join(problems)}) - no patch"
        rc, out = run(["bundle", "exec", "jekyll", "build"], tree, runner, env)
        if rc:
            return "MSG", f"{repo}: FAIL jekyll build ({redact(out).strip().splitlines()[-1:]}) - no patch"
        summary = ", ".join(f"{g} {before[g]}->{after[g]}" for g in pl["update"])
        return "PATCH", {"repo": repo, "branch": branch, "summary": summary, "ahead": ahead,
                         "before_gemfile": gemfile_before, "before_lock": before_text,
                         "after_gemfile": gemfile_after, "after_lock": after_text, "transitive": transitive}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------- phase: push (token, no fleet code)
SUMMARY_ITEM = r"[\w.-]+ [\w.+~-]+->[\w.+~-]+"
SUMMARY_RE = re.compile(rf"{SUMMARY_ITEM}(?:, {SUMMARY_ITEM})*")
AHEAD_PREFIX = "; ahead of matrix (left alone): "
CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def fleet_repo_set(text: str) -> set:
    """Lower-cased owner/repo names of the fleet list (GitHub names are case-insensitive)."""
    return {repo.lower() for repo, _ in parse_repo_list(text)}


def regenerated_problems(patch: dict, matrix: dict) -> list:
    """Do not trust the patch's Gemfile or summary: rebuild both from the two locks and require equality.
    The gems that changed between before_lock and after_lock must be exactly the matrix gems that were below
    target; the Gemfile must equal pin_gemfile(before_gemfile, those gems at matrix versions) byte for byte."""
    before, after = parse_lock(patch["before_lock"]), parse_lock(patch["after_lock"])
    update = plan(before, matrix)["update"]
    changed = sorted(g for g in set(before) | set(after) if before.get(g) != after.get(g))
    if changed != update:
        return [f"lock changes {changed} differ from the gems below the matrix {update}"]
    expected = pin_gemfile(patch["before_gemfile"], {g: matrix["gems"][g] for g in update})
    problems = []
    if patch["after_gemfile"] != expected:
        problems.append("Gemfile differs from the regenerated pin (not byte-identical)")
    derived = ", ".join(f"{g} {before[g]}->{after[g]}" for g in update)
    if patch["summary"] != derived:
        problems.append("summary does not match the lock diff")
    return problems


def patch_problems(patch: dict, matrix: dict, allowed):
    """Validate a patch purely as text (the patch file is untrusted: it came out of the build phase).

    `allowed`: set of lower-cased owner/repo names from fleet_repos.txt; a patch for any other repo is rejected.
    """
    keys = ("repo", "branch", "summary", "before_gemfile", "before_lock", "after_gemfile", "after_lock")
    if not isinstance(patch, dict) or not all(isinstance(patch.get(k), str) for k in keys):
        return ["malformed patch"]
    ahead = patch.get("ahead", "")
    if not isinstance(ahead, str):
        return ["malformed patch"]
    if not valid_repo(patch["repo"]) or not valid_name(patch["branch"]):
        return ["invalid repo or branch in patch"]
    if patch["repo"].lower() not in allowed:
        return ["repo not in fleet_repos.txt"]
    if len(patch["summary"]) > 500 or not SUMMARY_RE.fullmatch(patch["summary"]):
        return ["invalid summary in patch"]
    if ahead and (len(ahead) > 1000 or not ahead.startswith(AHEAD_PREFIX) or CONTROL_CHARS.search(ahead)):
        return ["invalid ahead note in patch"]
    problems = sources_problems(patch["before_lock"], matrix)
    lp, _ = lock_problems(patch["before_lock"], patch["after_lock"], matrix, allow_transitive=False)
    problems = problems + lp + gemfile_problems(patch["before_gemfile"], patch["after_gemfile"], matrix)
    return problems + regenerated_problems(patch, matrix)


def push_patch(patch, matrix, workdir, apply, token, runner=subprocess.run, gh=None, trailer=None, *, allowed):
    repo = str(patch.get("repo", "?")) if isinstance(patch, dict) else "?"
    problems = patch_problems(patch, matrix, allowed)
    if problems:
        return f"{repo}: FAIL patch rejected ({'; '.join(problems)})"
    branch = patch["branch"]
    if not apply:
        return f"{repo}: WOULD push to {WORK_BRANCH}: {patch['summary']}{patch.get('ahead', '')} (patch valid)"
    trailer = os.environ.get("FLEET_COMMIT_TRAILER", "") if trailer is None else trailer
    os.makedirs(workdir, exist_ok=True)
    home = tempfile.mkdtemp(prefix="pushhome-", dir=workdir)
    local, net = git_env(home), git_env(home, token)
    url = f"https://github.com/{repo}.git"
    dest = os.path.join(workdir, repo.replace("/", "__") + "-push")
    shutil.rmtree(dest, ignore_errors=True)
    rc, _ = git(["clone", "-q", "--depth", "50", "--branch", branch, "--", url, dest], workdir, runner, net)
    if rc:
        return f"{repo}: ERROR clone failed"
    ident = ["-c", "user.name=Claude", "-c", "user.email=774136+fullbright@users.noreply.github.com"]
    rc, _ = git(["fetch", "-q", "--depth", "50", "origin", WORK_BRANCH], dest, runner, net)
    unreviewed = ""
    if rc == 0:
        git(["checkout", "-q", "-B", WORK_BRANCH, f"origin/{WORK_BRANCH}", "--"], dest, runner, local)
        _, unreviewed = git(["log", "--format=%h %s", f"origin/{branch}..HEAD", "--"], dest, runner, local)
        if unreviewed.strip():
            rc, _ = git([*ident, "merge", "-q", "--no-edit", f"origin/{branch}"], dest, runner, local)
            if rc:
                git(["merge", "--abort"], dest, runner, local)
                return f"{repo}: FAIL cannot merge origin/{branch} into {WORK_BRANCH}"
        else:
            git(["checkout", "-q", "-B", WORK_BRANCH, f"origin/{branch}", "--"], dest, runner, local)
    else:
        git(["checkout", "-q", "-B", WORK_BRANCH, f"origin/{branch}", "--"], dest, runner, local)
    gf, lk = os.path.join(dest, "Gemfile"), os.path.join(dest, "Gemfile.lock")
    try:
        current_gf, current_lk = read_regular(gf, dest), read_regular(lk, dest)
        if current_gf != patch["before_gemfile"] or current_lk != patch["before_lock"]:
            return f"{repo}: FAIL stale patch (Gemfile or lock changed since the build) - rebuild"
        write_regular(gf, dest, patch["after_gemfile"])
        write_regular(lk, dest, patch["after_lock"])
    except (ValueError, OSError) as exc:
        return f"{repo}: FAIL {exc} - refused"
    msg = f"chore(deps): align Jekyll fleet gems to versions.yml ({patch['summary']})" + (f"\n\n{trailer}" if trailer else "")
    git(["add", "--", "Gemfile", "Gemfile.lock"], dest, runner, local)
    rc, _ = git([*ident, "commit", "-q", "-m", msg], dest, runner, local)
    if rc:
        return f"{repo}: FAIL commit"
    rc, _ = git(["push", "-q", "origin", f"HEAD:{WORK_BRANCH}"], dest, runner, net)
    if rc:
        return f"{repo}: FAIL push (not forced)"
    note = "pushed"
    if gh is not None:
        s, prs = gh.get(f"/repos/{repo}/pulls?state=open&head={repo.split('/')[0]}:{WORK_BRANCH}")
        if s == 200 and prs:
            note += f"; PR already open: {prs[0]['html_url']}"
        else:
            body = f"Aligned by `fleet_align_gems.py`: {patch['summary']}. Real `jekyll build` passed (token-free build phase)."
            if unreviewed.strip():
                body += "\n\nUnreviewed commits already on `claude/automated-work`:\n" + unreviewed.strip()
            s, pr, _ = gh.request("POST", f"/repos/{repo}/pulls", {
                "title": "chore(deps): align Jekyll fleet gems to versions.yml", "head": WORK_BRANCH, "base": branch, "body": body})
            if s in (200, 201) and pr:
                note += f"; opened PR {pr.get('html_url')}"
            else:
                shutil.rmtree(home, ignore_errors=True)
                return f"{repo}: FAIL pushed {WORK_BRANCH} but PR creation failed (HTTP {s}); {patch['summary']}"
    shutil.rmtree(home, ignore_errors=True)
    return f"{repo}: DONE {patch['summary']}; {note}{patch.get('ahead', '')}"


# --------------------------------------------------------------------------- CLI
def safe_call(label, fn, *args, **kwargs):
    """One repo failing (even with an exception) never stops the others."""
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - isolation is the point
        return f"{label}: ERROR {type(exc).__name__}: {exc}"


FAILURE_LINE = re.compile(r": (?:ERROR|FAIL)\b")


def is_failure(text: str) -> bool:
    """True for a per-repo report line that says ERROR or FAIL (SKIP / OK / WOULD / DONE are not failures)."""
    return bool(FAILURE_LINE.search(text))


def finish(failures) -> int:
    """Exit status: non-zero when any repo reported ERROR or FAIL, so the job (and the workflow run) goes red."""
    if failures:
        say(f"SUMMARY: {len(failures)} repo(s) reported ERROR/FAIL - exiting non-zero")
        return 1
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", required=True, choices=("fetch", "build", "push"))
    ap.add_argument("--repos", default=os.path.join(HERE, "fleet_repos.txt"))
    ap.add_argument("--matrix", default=os.path.join(HERE, "versions.yml"))
    ap.add_argument("--out", help="fetch: directory for the plain trees")
    ap.add_argument("--in", dest="indir", help="build: directory written by the fetch phase")
    ap.add_argument("--patches", help="build: output dir for patches; push: dir to read them from")
    ap.add_argument("--apply", action="store_true", help="push: really push + open PRs (default: dry-run)")
    ap.add_argument("--only", action="append", default=[], help="restrict to owner/repo (repeatable)")
    ap.add_argument("--build-env-pass", action="append", default=[], help="build: non-secret env var name to pass through")
    args = ap.parse_args(argv)
    if any(not valid_repo(o) for o in args.only):
        ap.error("--only values must be owner/repo matching [\\w.-]+ with no leading '-'")
    with open(args.matrix, encoding="utf-8") as fh:
        matrix = load_matrix(fh.read())
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    failures = []

    def report(text, tok=""):
        if is_failure(text):
            failures.append(text)
        say(text, tok)

    if args.phase == "fetch":
        if not args.out or not token:
            ap.error("fetch needs --out and GITHUB_TOKEN")
        with open(args.repos, encoding="utf-8") as fh:
            entries = [e for e in parse_repo_list(fh.read()) if not args.only or e[0] in args.only]
        bad = [e for e in entries if e[1] is not None and not valid_name(e[1])]
        if bad:
            ap.error(f"invalid branch in repo list: {bad}")
        gh = GitHub.from_env()
        for repo, branch in entries:
            br = branch or default_branch(gh, repo)
            report(safe_call(repo, fetch_repo, repo, br, args.out, token) if br else f"{repo}: ERROR not accessible (listed in fleet_repos.txt)", token)
        return finish(failures)
    if args.phase == "build":
        if not args.indir or not args.patches:
            ap.error("build needs --in and --patches")
        if any(os.environ.get(k) for k in SECRET_ENV):
            ap.error("build phase refuses to run with a token in the environment")
        os.makedirs(args.patches, exist_ok=True)
        for name in sorted(os.listdir(args.indir)):
            base = os.path.join(args.indir, name)
            try:
                with open(os.path.join(base, "meta.json"), encoding="utf-8") as fh:
                    meta = json.load(fh)
                repo, branch = meta["repo"], meta["branch"]
                if not valid_repo(repo) or not valid_name(branch):
                    report(f"{name}: ERROR invalid repo or branch in meta.json")
                    continue
                if args.only and repo not in args.only:
                    continue
            except (OSError, ValueError, KeyError, TypeError):
                report(f"{name}: ERROR unreadable or invalid meta.json")
                continue
            try:
                kind, res = build_repo(repo, branch, os.path.join(base, "tree"), matrix, passthrough=args.build_env_pass)
            except Exception as exc:  # noqa: BLE001
                kind, res = "MSG", f"{repo}: ERROR {type(exc).__name__}: {exc}"
            if kind == "PATCH":
                with open(os.path.join(args.patches, name + ".json"), "w", encoding="utf-8") as fh:
                    json.dump(res, fh)
                report(f"{repo}: patch ready: {res['summary']}{res['ahead']}")
            else:
                report(res)
        return finish(failures)
    if not args.patches:
        ap.error("push needs --patches")
    if args.apply and not token:
        ap.error("push --apply needs GITHUB_TOKEN")
    gh = GitHub.from_env() if args.apply else None
    with open(args.repos, encoding="utf-8") as fh:
        allowed = fleet_repo_set(fh.read())
    with tempfile.TemporaryDirectory() as wd:
        for name in sorted(os.listdir(args.patches)):
            if not name.endswith(".json"):
                continue
            try:
                with open(os.path.join(args.patches, name), encoding="utf-8") as fh:
                    patch = json.load(fh)
            except (OSError, ValueError):
                report(f"{name}: ERROR unreadable patch")
                continue
            if args.only and (not isinstance(patch, dict) or patch.get("repo") not in args.only):
                continue
            report(safe_call(name, push_patch, patch, matrix, wd, args.apply, token, gh=gh, allowed=allowed), token)
    return finish(failures)


if __name__ == "__main__":
    sys.exit(main())
