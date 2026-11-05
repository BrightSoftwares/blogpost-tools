import os
import types

import pytest

import fleet_align_gems as al

MATRIX_TEXT = open(os.path.join(os.path.dirname(al.__file__), "versions.yml"), encoding="utf-8").read()
TOKEN = "ghp_SECRETTOKEN123"
LOCK = """GEM
  remote: https://rubygems.org/
  specs:
    i18n (1.14.7)
    ffi (1.16.3)
    jekyll (4.3.4)
    jekyll-timeago (0.13.1)
    rexml (3.4.5)

PLATFORMS
  ruby
"""
GEMFILE = """source 'https://rubygems.org'
gem 'jekyll', '~> 4.3.4'
gem 'jekyll-timeago', '~> 0.13.1', require: false
gem 'ffi', '= 1.16.3'
"""
M = al.load_matrix(MATRIX_TEXT)
LATEST = {"ffi": "1.18.0", "jekyll-timeago": "1.2.0"}


def test_matrix_parses_and_has_core_gems():
    assert M["gems"]["jekyll"] == "4.3.4" and M["gems"]["jekyll-timeago"] == "1.1.0"


def test_parse_lock_reads_specs_platforms_and_prereleases():
    assert al.parse_lock(LOCK)["ffi"] == "1.16.3"
    lock = "GEM\n  specs:\n    ffi (1.17.4-x86_64-linux)\n    foo (1.0.0.rc1)\n"
    assert al.parse_lock(lock) == {"ffi": "1.17.4", "foo": "1.0.0.rc1"}
    assert al.vkey("1.0.0.rc1") < al.vkey("1.0.0") < al.vkey("1.0.1")


def test_plan_updates_below_leaves_ahead_ignores_absent():
    p = al.plan(al.parse_lock(LOCK), M)
    assert sorted(p["update"]) == ["ffi", "jekyll-timeago"]
    assert p["ahead"] == {"rexml": "3.4.5"}
    assert "i18n" in p["ok"] and "webrick" not in p["ok"]


def test_numeric_not_lexicographic_compare():
    assert al.vkey("1.10.0") > al.vkey("1.9.9")


def test_pin_gemfile_rewrites_constraint_and_appends_transitive():
    out = al.pin_gemfile(GEMFILE, {"ffi": "1.17.4", "jekyll-timeago": "1.1.0", "rexml": "3.4.4"})
    assert "gem 'ffi', '= 1.17.4'" in out and "'= 1.16.3'" not in out
    assert "gem 'jekyll-timeago', '= 1.1.0', require: false" in out and "~> 0.13.1" not in out
    assert "gem 'rexml', '= 3.4.4'" in out and "gem 'jekyll', '~> 4.3.4'" in out


# ---------------------------------------------------------------- fake git/bundle
class FakeRunner:
    """Simulates git/bundle. `bundle update` honours `= x` pins in the Gemfile, otherwise installs LATEST."""

    def __init__(self, lock=LOCK, gemfile=GEMFILE, build_rc=0, update_rc=0, work_branch=False,
                 unreviewed="", merge_rc=0, extra_lock=None, raise_on_clone=False):
        self.lock, self.gemfile = lock, gemfile
        self.build_rc, self.update_rc, self.work_branch = build_rc, update_rc, work_branch
        self.unreviewed, self.merge_rc, self.extra_lock, self.raise_on_clone = unreviewed, merge_rc, extra_lock, raise_on_clone
        self.calls = []  # (argv, env)

    @property
    def cmds(self):
        return [c for c, _ in self.calls]

    def __call__(self, cmd, cwd=None, capture_output=True, text=True, env=None):
        self.calls.append((cmd, env))
        rc, out = 0, ""
        if cmd[:2] == ["git", "clone"]:
            if self.raise_on_clone:
                raise RuntimeError(f"boom https://x:{TOKEN}@github.com/a/b")
            os.makedirs(cmd[-1], exist_ok=True)
            open(os.path.join(cmd[-1], "Gemfile.lock"), "w").write(self.lock)
            open(os.path.join(cmd[-1], "Gemfile"), "w").write(self.gemfile)
        elif cmd[:2] == ["git", "fetch"]:
            rc = 0 if self.work_branch else 1
        elif cmd[:2] == ["git", "log"]:
            out = self.unreviewed
        elif "merge" in cmd and cmd[0] == "git" or cmd[:2] == ["git", "-c"] and "merge" in cmd:
            rc = self.merge_rc
        elif cmd[:2] == ["bundle", "update"]:
            rc = self.update_rc
            gf = open(os.path.join(cwd, "Gemfile")).read()
            lock = open(os.path.join(cwd, "Gemfile.lock")).read()
            for gem in cmd[2:]:
                if gem.startswith("--"):
                    continue
                pin = [l for l in gf.splitlines() if l.startswith(f"gem '{gem}', '= ")]
                ver = pin[-1].split("'= ")[1].split("'")[0] if pin else LATEST.get(gem, "9.9.9")
                lock = "\n".join(f"    {gem} ({ver})" if l.startswith(f"    {gem} (") else l for l in lock.split("\n"))
            if self.extra_lock:
                lock = self.extra_lock(lock)
            open(os.path.join(cwd, "Gemfile.lock"), "w").write(lock)
            out = f"fetching https://u:p@rubygems.org {TOKEN}" if rc else ""
        elif cmd[:3] == ["bundle", "exec", "jekyll"]:
            rc = self.build_rc
            out = f"error {TOKEN} https://u:p@x.org" if rc else ""
        return types.SimpleNamespace(returncode=rc, stdout=out, stderr="")

    def ran(self, *prefix):
        return any(c[:len(prefix)] == list(prefix) for c in self.cmds)

    def env_of(self, *prefix):
        return [e for c, e in self.calls if c[:len(prefix)] == list(prefix)]


def go(tmp_path, runner, apply=False, **kw):
    return al.align_repo("a/site", "main", M, str(tmp_path), apply, TOKEN, runner=runner, trailer="T-trailer", **kw)


def test_dry_run_pins_builds_and_never_commits_or_pushes(tmp_path):
    r = FakeRunner()
    out = go(tmp_path, r)
    assert "WOULD open PR" in out and "ffi 1.16.3->1.17.4" in out and "ahead of matrix" in out
    assert ["bundle", "update", "ffi", "jekyll-timeago", "--conservative"] in r.cmds
    assert r.ran("bundle", "exec", "jekyll", "build")
    assert not r.ran("git", "push") and not any("commit" in c for c in r.cmds)


def test_overshoot_without_pin_would_fail_but_pinning_lands_exactly(tmp_path):
    # LATEST is above the matrix: only the Gemfile pin makes the lock land on the target.
    r = FakeRunner()
    assert "WOULD open PR" in go(tmp_path, r)
    r2 = FakeRunner()
    r2.gemfile = "source 'https://rubygems.org'\n"  # transitive only: pin line appended
    assert "WOULD open PR" in go(tmp_path / "t", r2)


def test_apply_commits_gemfile_and_lock_pushes_only_work_branch(tmp_path):
    r = FakeRunner()
    out = go(tmp_path, r, apply=True)
    assert out.startswith("a/site: DONE")
    assert ["git", "add", "--", "Gemfile", "Gemfile.lock"] in r.cmds
    assert [c for c in r.cmds if c[:2] == ["git", "push"]] == [["git", "push", "-q", "origin", "HEAD:claude/automated-work"]]
    assert not any("--force" in c or "-f" in c for c in r.cmds)


# ---------------------------------------------------------------- major 1 (security): token handling
def test_token_never_in_argv_and_only_git_network_calls_get_auth(tmp_path):
    r = FakeRunner(work_branch=True)
    go(tmp_path, r, apply=True)
    assert not any(TOKEN in a for c in r.cmds for a in c)
    assert ["git", "clone", "-q", "--depth", "50", "--branch", "main", "--", "https://github.com/a/site.git",
            os.path.join(str(tmp_path), "a__site")] in r.cmds
    for prefix in (("git", "clone"), ("git", "fetch"), ("git", "push")):
        env = r.env_of(*prefix)[0]
        assert "Authorization: basic" in env["GIT_CONFIG_VALUE_0"] and env["GIT_CONFIG_KEY_0"] == "http.extraheader"
    assert ["git", "remote", "set-url", "origin", "https://github.com/a/site.git"] in r.cmds


def test_env_for_bundle_and_jekyll_has_no_secrets(tmp_path, monkeypatch):
    for k in ("GITHUB_TOKEN", "GH_TOKEN", "FLEET_COMMIT_TRAILER", "REPO_ACCESS_TOKEN"):
        monkeypatch.setenv(k, TOKEN)
    r = FakeRunner()
    go(tmp_path, r)
    for prefix in (("bundle", "update"), ("bundle", "exec")):
        env = r.env_of(*prefix)[0]
        assert env is not None
        assert not any(k in env for k in ("GITHUB_TOKEN", "GH_TOKEN", "FLEET_COMMIT_TRAILER", "REPO_ACCESS_TOKEN"))
        assert not any(k.startswith("GIT_CONFIG_") for k in env)
        assert TOKEN not in "".join(env.values()) and env["BUNDLE_APP_CONFIG"].startswith(str(tmp_path))


def test_echoed_failure_output_is_redacted(tmp_path):
    out = go(tmp_path, FakeRunner(build_rc=1))
    assert TOKEN not in out and "u:p@" not in out
    out2 = go(tmp_path / "b", FakeRunner(update_rc=1))
    assert TOKEN not in out2 and "u:p@" not in out2


# ---------------------------------------------------------------- major 3 (security): lock diff
def test_lock_diff_refuses_foreign_remote_new_git_section_and_transitive(tmp_path):
    def foreign(lock):
        return lock.replace("https://rubygems.org/", "https://evil.example/")

    def git_section(lock):
        return lock + "\nGIT\n  remote: https://github.com/x/y.git\n  revision: abc\n  specs:\n    y (1.0.0)\n"

    def transitive(lock):
        return lock.replace("    i18n (1.14.7)", "    i18n (1.15.0)\n    newdep (1.0.0)")

    r = FakeRunner(extra_lock=foreign)
    assert "GEM remote not https://rubygems.org/" in go(tmp_path / "a", r, apply=True) and not r.ran("git", "push")
    r = FakeRunner(extra_lock=git_section)
    assert "GIT sources changed" in go(tmp_path / "b", r, apply=True) and not r.ran("git", "push")
    r = FakeRunner(extra_lock=transitive)
    assert "changes outside the matrix" in go(tmp_path / "c", r, apply=True) and not r.ran("git", "push")
    # explicit opt-in lists them instead
    r = FakeRunner(extra_lock=transitive)
    out = go(tmp_path / "d", r, apply=True, allow_transitive=True)
    assert out.startswith("a/site: DONE")


def test_lock_problems_pure():
    b = LOCK
    assert al.lock_problems(b, b, M)[0] == []
    assert al.lock_problems(b, b.replace("PLATFORMS", "PATH\n  remote: .\n  specs:\n    z (1)\n\nPLATFORMS"), M)[0]


# ---------------------------------------------------------------- code review majors
def test_existing_work_branch_is_merged_with_default_when_it_has_commits(tmp_path):
    r = FakeRunner(work_branch=True, unreviewed="abc123 earlier work\n")
    out = go(tmp_path, r, apply=True)
    assert out.startswith("a/site: DONE")
    assert any(c[0] == "git" and "merge" in c and "origin/main" in c for c in r.cmds)


def test_existing_work_branch_without_unreviewed_commits_is_reset_to_default(tmp_path):
    r = FakeRunner(work_branch=True, unreviewed="")
    go(tmp_path, r)
    assert ["git", "checkout", "-q", "-B", "claude/automated-work", "origin/main", "--"] in r.cmds
    assert not any("merge" in c for c in r.cmds)


def test_merge_conflict_stops_without_push(tmp_path):
    r = FakeRunner(work_branch=True, unreviewed="abc x\n", merge_rc=1)
    out = go(tmp_path, r, apply=True)
    assert "cannot merge" in out and r.ran("git", "merge", "--abort") and not r.ran("git", "push")


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
    out = go(tmp_path, FakeRunner(work_branch=True, unreviewed="abc123 earlier work\n"), apply=True, gh=gh)
    assert "opened PR https://x/pr/1" in out and "abc123 earlier work" in gh.posted["body"]
    gh2 = GH([{"html_url": "https://x/pr/9"}])
    out2 = go(tmp_path / "z", FakeRunner(), apply=True, gh=gh2)
    assert "PR already open: https://x/pr/9" in out2 and gh2.posted is None


def test_one_repo_raising_does_not_stop_the_next(tmp_path):
    bad = al.safe_align("a/bad", "main", M, str(tmp_path), False, TOKEN, runner=FakeRunner(raise_on_clone=True))
    assert bad.startswith("a/bad: ERROR RuntimeError") and TOKEN not in bad and "x:" not in bad
    good = al.safe_align("a/ok", "main", M, str(tmp_path), False, TOKEN, runner=FakeRunner())
    assert "WOULD open PR" in good


def test_no_lock_and_already_aligned_skip_without_building(tmp_path):
    aligned = LOCK.replace("ffi (1.16.3)", "ffi (1.17.4)").replace("jekyll-timeago (0.13.1)", "jekyll-timeago (1.1.0)")
    r2 = FakeRunner(lock=aligned)
    assert "OK, lock already on matrix" in go(tmp_path, r2) and not r2.ran("bundle", "update")


# ---------------------------------------------------------------- minors: validation + main()
def test_names_are_validated():
    assert al.valid_name("main") and al.valid_name("release/1.x")
    assert not al.valid_name("-rf") and not al.valid_name("a b") and not al.valid_name("a/../b")
    assert "invalid" in al.align_repo("a/site", "--upload-pack=x", M, "/tmp", False, TOKEN, runner=FakeRunner())


def test_main_rejects_bad_only_and_bad_branch(tmp_path, capsys):
    repos = tmp_path / "r.txt"
    repos.write_text("a/site -evil\n")
    with pytest.raises(SystemExit):
        al.main(["--repos", str(repos), "--only", "-x"])
    with pytest.raises(SystemExit):
        al.main(["--repos", str(repos)])
