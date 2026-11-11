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
.github/workflows/fleet-align-gems.yml: build job has `contents: read`, no secrets). Inside the build job,
code from a fleet repo could also start a background process that outlives the step and reads the job's
ACTIONS_RUNTIME_TOKEN (artifact upload scope); that is inside the accepted threat model of this design.

Lock validation compares locks STRUCTURALLY with Bundler's own parser (lock_structure.rb, pure parser, no fleet
code) plus a strict line grammar; a Python text split on blank lines is not how Bundler reads a lock. It fails
closed when ruby is unavailable.

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
LOCK_LINE = re.compile(r"^    ([A-Za-z0-9_.-]+) \((\d+(?:\.\d+)*(?:\.[A-Za-z][\w.]*)?)(?:-[^)]*)?\)$", re.ASCII)
# Spec line as Bundler reads it: 4 spaces, name, parenthesised version (digits, letters, dots; optional -platform).
SPEC_LINE = re.compile(r"^    ([A-Za-z0-9_.-]+) \(([0-9][A-Za-z0-9.]*)(-[A-Za-z0-9_.-]+)?\)$", re.ASCII)
SECRET_ENV = ("GITHUB_TOKEN", "GH_TOKEN", "REPO_ACCESS_TOKEN", "FLEET_COMMIT_TRAILER")
NAME_OK = re.compile(r"[\w][\w./-]*", re.ASCII)  # no leading '-': a value can never look like a git option
GEM_NAME = re.compile(r"[\w.-]+", re.ASCII)
VERSION = re.compile(r"\d+(\.\w+)*", re.ASCII)
URL_CRED = re.compile(r"://[^@/\s]+@")
PIN_COMMENT = "# Pinned by fleet_align_gems.py (scripts/jekyll_fleet/versions.yml)"


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
        m = SPEC_LINE.match(line) if in_specs else None
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


_NAME = r"[A-Za-z0-9_.-]+"
_SOURCE_LINES = (r"  remote: \S+", r"  revision: [0-9a-f]+", r"  (?:tag|branch|ref|glob|submodules): \S+", r"  specs:",
                 rf"    {_NAME} \([0-9][A-Za-z0-9.]*(?:-[A-Za-z0-9_.-]+)?\)", rf"      {_NAME}(?: \([^()\n]*\))?")
LOCK_GRAMMAR = {
    "GEM": _SOURCE_LINES, "GIT": _SOURCE_LINES, "PATH": _SOURCE_LINES,
    "PLATFORMS": (r"  [A-Za-z0-9_.-]+",),
    "DEPENDENCIES": (rf"  {_NAME}(?: \([^()\n]*\))?!?",),
    "CHECKSUMS": (rf"  {_NAME} \([^()\s]+\)(?: [A-Za-z0-9]+=[0-9a-f]+)?",),
    "BUNDLED WITH": (r"  {1,3}[0-9][A-Za-z0-9.]*",),  # Bundler 2 writes 3 spaces, Bundler 4 writes 2
    "RUBY VERSION": (r"  {1,3}ruby [0-9][A-Za-z0-9.]*",),
}
_GRAMMAR_RE = {h: [re.compile(p, re.ASCII) for p in pats] for h, pats in LOCK_GRAMMAR.items()}


def lock_lines(text: str):
    """Yield (section, line) for every line, split on "\\n" ONLY (the one separator Bundler uses), so lines Python's
    splitlines()/\\s treat as separators (\\r \\x0b \\x0c \\x1c-\\x1e \\x85 U+2028/9) stay inside a line and fail the grammar."""
    section = ""
    for line in text.split("\n"):
        if line and not line[0].isspace():
            section = line
        yield section, line


def grammar_problems(text: str) -> list:
    """Strict line grammar of a Gemfile.lock: known section headers, known 2/3/4/6-space forms, no blank-ish lines."""
    problems, prev = [], None
    for n, (section, line) in enumerate(lock_lines(text), 1):
        if line == "":
            prev = line
            continue
        shown = _clip(line, 60)
        if not line[0].isspace() and prev is not None and prev != "":
            problems.append(f"lock line {n}: section header {shown} is not preceded by an empty line")
        prev = line
        if not line.isascii() or not line.isprintable() or line != line.rstrip(" "):
            problems.append(f"lock line {n}: control, non-ASCII or trailing-space characters: {shown}")
        elif not line.startswith(" "):
            if line not in LOCK_GRAMMAR:
                problems.append(f"lock line {n}: unknown section header: {shown}")
        elif not any(r.fullmatch(line) for r in _GRAMMAR_RE.get(section, ())):
            problems.append(f"lock line {n}: not allowed in {section or 'no section'}: {shown}")
    return problems


def _clip(text, n=80):
    return repr(str(text)[:n]) + ("..." if len(str(text)) > n else "")


def sources_problems(lock_text: str, matrix: dict):
    """EVERY `remote:` line of the lock (no matter which block Python thinks it is in), exactly one per source
    section: a GEM remote must be exactly rubygems.org; a GIT/PATH remote must be allowlisted in versions.yml."""
    problems, per_section = [], {}
    for n, (section, line) in enumerate(lock_lines(lock_text), 1):
        if section.split(" ")[0] in ("GEM", "GIT", "PATH") and line == section:
            per_section[n] = [section, 0]
        if "remote:" not in line:
            continue
        m = re.fullmatch(r"  remote: (\S+)", line)
        if not m:
            problems.append(f"malformed remote line in {section or 'no section'}: {_clip(line.strip())}")
        elif section == "GEM" and m.group(1) != RUBYGEMS:
            problems.append(f"GEM remote not {RUBYGEMS}: {_clip(m.group(1))}")
        elif section in ("GIT", "PATH") and m.group(1) not in matrix["allow_sources"]:
            problems.append(f"{section} source not allowlisted in versions.yml: {_clip(m.group(1))}")
        elif section not in ("GEM", "GIT", "PATH"):
            problems.append(f"remote line outside a source section ({section or 'none'}): {_clip(m.group(1))}")
        elif per_section:
            per_section[max(per_section)][1] += 1
    for section, count in per_section.values():
        if count != 1:
            problems.append(f"{section} source section has {count} remote lines (exactly one required)")
    return problems


def source_spec_lists(text: str) -> list:
    """Per source section (GEM/GIT/PATH, in file order): the ordered [(spec line, [dependency lines])]. Text level on
    purpose: Bundler's parser keeps ONE of two identical name/version specs and hides the other."""
    out = []
    for section, line in lock_lines(text):
        if section.split(" ")[0] in ("GEM", "GIT", "PATH") and line == section:
            out.append([])
        elif out and SPEC_LINE.match(line):
            out[-1].append((line, []))
        elif out and out[-1] and line.startswith("      "):
            out[-1][-1][1].append(line)
    return out


def section_headers(text: str) -> list:
    return [line for line in text.split("\n") if line and not line[0].isspace()]


class LockStructureError(Exception):
    pass


_STRUCTURE_CACHE: dict = {}


def bundler_structure(text: str, runner=subprocess.run) -> dict:
    if runner is subprocess.run and text in _STRUCTURE_CACHE:  # same lock text, same answer (one ruby start is ~0.4 s)
        return _STRUCTURE_CACHE[text]
    result = _bundler_structure(text, runner)
    if runner is subprocess.run:
        _STRUCTURE_CACHE[text] = result
    return result


def _bundler_structure(text: str, runner=subprocess.run) -> dict:
    """Parse a lock with Bundler's own LockfileParser (lock_structure.rb). Fails CLOSED: no ruby, a timeout or any
    parse error raises LockStructureError, which callers turn into a rejection."""
    script = os.path.join(HERE, "lock_structure.rb")
    home = tempfile.mkdtemp(prefix="lockstruct-")
    try:
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": home, "LANG": "C.UTF-8"}
        try:
            res = runner(["ruby", script], input=text, capture_output=True, text=True, timeout=10, env=env)
        except FileNotFoundError:
            raise LockStructureError("ruby is not available: cannot validate the lock structure (failing closed)") from None
        except subprocess.TimeoutExpired:
            raise LockStructureError("lock structure parser timed out (failing closed)") from None
        if res.returncode:
            raise LockStructureError("Bundler could not parse the lock: " + _clip((res.stderr or "").strip().splitlines()[-1:] or ""))
        try:
            return json.loads(res.stdout)
        except ValueError:
            raise LockStructureError("lock structure parser returned invalid output") from None
    finally:
        shutil.rmtree(home, ignore_errors=True)


def structure_problems(before_text: str, after_text: str, matrix: dict, runner=subprocess.run) -> list:
    """Structural comparison of two locks as Bundler reads them. Only the matrix gems below target may change, and
    only to the matrix version; sources, platforms, Ruby/Bundler versions, dependencies and checksums are otherwise
    byte-for-byte what they were."""
    try:
        b, a = bundler_structure(before_text, runner), bundler_structure(after_text, runner)
    except LockStructureError as exc:
        return [str(exc)]
    problems = []
    if b["sources"] != a["sources"]:
        problems.append("ordered source list (class, uri, revision, ref, branch, glob) changed")
    for key in ("platforms", "ruby_version"):
        if b[key] != a[key]:
            problems.append(f"{key} changed")
    allowed_bundler = {v.strip() for v in str(matrix.get("allow_bundler", "")).split(",") if v.strip()}
    if b["bundler_version"] != a["bundler_version"] and a["bundler_version"] not in allowed_bundler:
        problems.append(f"BUNDLED WITH changed {b['bundler_version']} -> {a['bundler_version']} (not in allow_bundler)")
    key = lambda sp: (sp["name"], sp["platform"], sp["source"])  # noqa: E731
    seen = set()
    for sp in a["specs"]:
        if key(sp) in seen:
            problems.append(f"duplicate spec {sp['name']} ({sp['platform']}) in one source")
        seen.add(key(sp))
    bmap, amap = {key(sp): sp for sp in b["specs"]}, {key(sp): sp for sp in a["specs"]}
    if set(bmap) != set(amap):
        added = sorted({k[0] for k in set(amap) - set(bmap)})
        removed = sorted({k[0] for k in set(bmap) - set(amap)})
        problems.append(f"spec set changed: added {added}, removed {removed}")
    # which matrix gems were below target (by the versions Bundler read, not by a text regex)
    bver = {sp["name"]: sp["version"] for sp in b["specs"]}
    update = plan(bver, matrix)["update"]
    names = {sp["name"] for sp in a["specs"]}
    for k in sorted(set(bmap) & set(amap)):
        bs, as_ = bmap[k], amap[k]
        if k[0] in update:
            if as_["version"] != matrix["gems"][k[0]]:
                problems.append(f"{k[0]} is {as_['version']}, matrix says {matrix['gems'][k[0]]}")
            stray = sorted({d.split(" ")[0] for d in as_["deps"]} - names)
            if stray:
                problems.append(f"{k[0]} gained dependencies on gems that are not in the lock: {stray}")
        elif bs != as_:
            problems.append(f"spec changed outside the matrix update: {k[0]} ({k[1]})")
    bd, ad = {d["name"]: d for d in b["dependencies"]}, {d["name"]: d for d in a["dependencies"]}
    for name in sorted(set(bd) | set(ad)):
        if bd.get(name) == ad.get(name):
            continue
        want = f"= {matrix['gems'].get(name)}"
        if name in update and ad.get(name) and ad[name]["req"] == want and ad[name]["source"] == (bd.get(name) or ad[name])["source"]:
            continue
        problems.append(f"DEPENDENCIES entry changed outside the matrix update: {name}")
    bl, al_ = source_spec_lists(before_text), source_spec_lists(after_text)
    if len(bl) != len(al_):
        problems.append("number of source sections changed")
    for n, (bs, as_) in enumerate(zip(bl, al_), 1):
        if len(bs) != len(as_):
            problems.append(f"source section {n}: spec list length {len(bs)} -> {len(as_)} (added, removed or hidden duplicate)")
            continue
        for (bline, bdeps), (aline, adeps) in zip(bs, as_):
            bm, am = SPEC_LINE.match(bline), SPEC_LINE.match(aline)
            if bm.group(1) in update and am and am.group(1) == bm.group(1) and am.group(3) == bm.group(3):
                continue  # the updated gem's own line (version and dependencies are checked structurally above)
            if (bline, bdeps) != (aline, adeps):
                problems.append(f"source section {n}: spec line changed outside the matrix update: {_clip(aline.strip())}")
    problems += checksum_problems(before_text, after_text, update)
    return problems


def checksum_problems(before_text: str, after_text: str, update: list) -> list:
    """CHECKSUMS must exist iff it did, and every line that does not name an updated gem must be byte-identical."""
    def lines(text):
        sec, out = None, []
        for section, line in lock_lines(text):
            if line == "CHECKSUMS":
                sec = []
                continue
            if section == "CHECKSUMS" and line.startswith("  "):
                sec.append(line)
        return sec
    b, a = lines(before_text), lines(after_text)
    if (b is None) != (a is None):
        return ["CHECKSUMS section added or removed"]
    if b is None:
        return []
    def keep(ls):
        return [l for l in ls if l.strip().split(" ", 1)[0] not in update]
    return [] if keep(b) == keep(a) else ["CHECKSUMS lines outside the matrix update changed"]


def lock_problems(before_text: str, after_text: str, matrix: dict, allow_transitive=False):
    """Validate a lock change: strict line grammar + one remote per source + identical ordered section headers +
    the STRUCTURAL comparison through Bundler's parser. Returns (problems, transitive_changes)."""
    problems = grammar_problems(after_text) + sources_problems(after_text, matrix)
    if section_headers(before_text) != section_headers(after_text):
        problems.append("ordered list of section headers changed")
    problems += structure_problems(before_text, after_text, matrix)
    bp, ap = parse_lock(before_text), parse_lock(after_text)
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
SUMMARY_RE = re.compile(rf"{SUMMARY_ITEM}(?:, {SUMMARY_ITEM})*", re.ASCII)
AHEAD_PREFIX = "; ahead of matrix (left alone): "
CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def fleet_branches(text: str) -> dict:
    """{lower-cased owner/repo: declared branch or None} from fleet_repos.txt."""
    return {repo.lower(): branch for repo, branch in parse_repo_list(text)}


def patch_filename(repo: str) -> str:
    return repo.replace("/", "__") + ".json"


def binding_problem(name, patch, branches, gh=None):
    """A patch is bound to ITS repo: the file name must be that repo's, and the branch must be the fleet-list branch
    (or the repo's default branch), never whatever the untrusted patch says. None when fine or not checkable."""
    if not isinstance(patch, dict) or not isinstance(patch.get("repo"), str) or not isinstance(patch.get("branch"), str):
        return None  # push_patch reports it as malformed
    if not valid_repo(patch["repo"]):
        return None
    if name != patch_filename(patch["repo"]):
        return f"{name}: FAIL patch file name does not match its repo {patch['repo']} (expected {patch_filename(patch['repo'])})"
    expected = branches.get(patch["repo"].lower())
    if expected is None and gh is not None:
        expected = default_branch(gh, patch["repo"])
    if expected is not None and patch["branch"] != expected:
        return f"{patch['repo']}: FAIL patch branch {patch['branch']!r} is not the fleet branch {expected!r}"
    return None


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
    # the push phase re-checks what the build phase promised: every updated gem sits EXACTLY on the matrix version
    # and no matrix gem vanished from the lock (a missing entry is a validation message, never a KeyError)
    gone = sorted(g for g in matrix["gems"] if g in before and g not in after)
    if gone:
        return [f"matrix gem removed from the lock: {', '.join(gone)}"]
    wrong = verify_after(after, matrix, update)
    if wrong:
        return [f"after_lock not on the matrix version ({'; '.join(wrong)})"]
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
        os.makedirs(args.out, exist_ok=True)
        # always hand over a file, so the artifact exists even when every repo failed (a missing artifact is then a
        # real download failure, not "nothing to do")
        with open(os.path.join(args.out, "MANIFEST.txt"), "w", encoding="utf-8") as fh:
            fh.write("".join(f"{r}\n" for r, _ in entries))
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
        with open(os.path.join(args.patches, "MANIFEST.txt"), "w", encoding="utf-8") as fh:
            fh.write("build phase ran\n")
        for name in sorted(os.listdir(args.indir)):
            base = os.path.join(args.indir, name)
            if not os.path.isdir(base):
                continue  # e.g. MANIFEST.txt
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
                with open(os.path.join(args.patches, patch_filename(repo)), "w", encoding="utf-8") as fh:
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
        branches = fleet_branches(fh.read())
    allowed = set(branches)
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
            bad = binding_problem(name, patch, branches, gh)
            if bad:
                report(bad)
                continue
            report(safe_call(name, push_patch, patch, matrix, wd, args.apply, token, gh=gh, allowed=allowed), token)
    return finish(failures)


if __name__ == "__main__":
    sys.exit(main())
