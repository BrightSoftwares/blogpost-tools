"""Static guards on reusable_social-publish.yml (the dry run and the commit step)."""
from pathlib import Path

import yaml

WF = Path(__file__).resolve().parents[2] / ".github/workflows/reusable_social-publish.yml"


def _commit_step():
    wf = yaml.safe_load(WF.read_text())
    steps = wf["jobs"]["publish"]["steps"]
    return next(s for s in steps if s.get("name") == "Commit results")


def test_commit_step_skipped_in_dry_run():
    assert "inputs.dry_run" in _commit_step().get("if", "")


def test_commit_step_is_race_and_missing_path_safe():
    run = _commit_step()["run"]
    assert "pull --rebase" in run, "push must rebase first (non-fast-forward failure 2026-10-30)"
    assert "-e \"$p\"" in run, "git add aborts on a missing pathspec such as _social_published/"
    assert "git diff --staged --quiet" in run


def test_commit_step_stages_draft_removals():
    assert "git add -A" in _commit_step()["run"] and "drafts_dir" in _commit_step()["run"]
