import os
import types

import fleet_align_gems as al

MATRIX_TEXT = open(os.path.join(os.path.dirname(al.__file__), "versions.yml"), encoding="utf-8").read()
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
M = al.load_matrix(MATRIX_TEXT)
GOOD_AFTER = LOCK.replace("ffi (1.16.3)", "ffi (1.17.4)").replace("jekyll-timeago (0.13.1)", "jekyll-timeago (1.1.0)")


def test_matrix_parses_and_has_core_gems():
    assert M["gems"]["jekyll"] == "4.3.4" and M["gems"]["jekyll-timeago"] == "1.1.0" and M["ruby"] == "3.4"


def test_parse_lock_reads_specs_only():
    assert al.parse_lock(LOCK) == {"i18n": "1.14.7", "ffi": "1.16.3", "jekyll": "4.3.4",
                                   "jekyll-timeago": "0.13.1", "rexml": "3.4.5"}


def test_plan_updates_below_leaves_ahead_ignores_absent():
    p = al.plan(al.parse_lock(LOCK), M)
    assert sorted(p["update"]) == ["ffi", "jekyll-timeago"]
    assert p["ahead"] == {"rexml": "3.4.5"}
    assert "i18n" in p["ok"] and "webrick" not in p["ok"]


def test_numeric_not_lexicographic_compare():
    assert al.vkey("1.10.0") > al.vkey("1.9.9")


def test_verify_after_flags_overshoot_and_miss():
    assert al.verify_after({"ffi": "1.17.4"}, M, ["ffi"]) == []
    assert al.verify_after({"ffi": "1.18.0"}, M, ["ffi"])
    assert al.verify_after({}, M, ["ffi"])


class FakeRunner:
    def __init__(self, lock_before, lock_after=None, build_rc=0, update_rc=0):
        self.lock_before, self.lock_after = lock_before, lock_after
        self.build_rc, self.update_rc = build_rc, update_rc
        self.cmds = []

    def __call__(self, cmd, cwd=None, capture_output=True, text=True):
        self.cmds.append(cmd)
        rc = 0
        if cmd[:2] == ["git", "clone"]:
            os.makedirs(cmd[-1], exist_ok=True)
            if self.lock_before is not None:
                open(os.path.join(cmd[-1], "Gemfile.lock"), "w").write(self.lock_before)
        elif cmd[:2] == ["git", "fetch"]:
            rc = 1
        elif cmd[:2] == ["bundle", "update"]:
            rc = self.update_rc
            if self.lock_after:
                open(os.path.join(cwd, "Gemfile.lock"), "w").write(self.lock_after)
        elif cmd[:3] == ["bundle", "exec", "jekyll"]:
            rc = self.build_rc
        return types.SimpleNamespace(returncode=rc, stdout="", stderr="boom" if rc else "")

    def ran(self, *prefix):
        return any(c[:len(prefix)] == list(prefix) for c in self.cmds)


def go(tmp_path, runner, apply=False):
    return al.align_repo("a/site", "main", M, str(tmp_path), apply, "tok", runner=runner)


def test_dry_run_builds_but_never_pushes(tmp_path):
    r = FakeRunner(LOCK, GOOD_AFTER)
    out = go(tmp_path, r)
    assert "WOULD open PR" in out and "ffi 1.16.3->1.17.4" in out
    assert r.ran("bundle", "exec", "jekyll", "build") and not r.ran("git", "push")


def test_apply_pushes_only_work_branch(tmp_path):
    r = FakeRunner(LOCK, GOOD_AFTER)
    out = go(tmp_path, r, apply=True)
    assert out.startswith("a/site: DONE")
    pushes = [c for c in r.cmds if c[:2] == ["git", "push"]]
    assert pushes == [["git", "push", "-q", "origin", "HEAD:claude/automated-work"]]
    assert not any("--force" in c or "-f" in c for c in r.cmds)


def test_build_failure_means_no_pr_no_push(tmp_path):
    r = FakeRunner(LOCK, GOOD_AFTER, build_rc=1)
    out = go(tmp_path, r, apply=True)
    assert "FAIL jekyll build" in out and not r.ran("git", "push")


def test_update_failure_and_overshoot_block_pr(tmp_path):
    assert "FAIL bundle update" in go(tmp_path, FakeRunner(LOCK, update_rc=1), apply=True)
    over = LOCK.replace("ffi (1.16.3)", "ffi (1.18.0)").replace("jekyll-timeago (0.13.1)", "jekyll-timeago (1.1.0)")
    r = FakeRunner(LOCK, over)
    assert "FAIL lock not on matrix" in go(tmp_path, r, apply=True) and not r.ran("git", "push")


def test_no_lock_and_already_aligned_skip_without_building(tmp_path):
    r = FakeRunner(None)
    assert "SKIP" in go(tmp_path, r) and not r.ran("bundle", "update")
    r2 = FakeRunner(GOOD_AFTER)
    assert "OK, lock already on matrix" in go(tmp_path / "x", r2) and not r2.ran("bundle", "update")
