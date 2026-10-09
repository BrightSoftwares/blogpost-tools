"""Guard: a fully-dry run of reusable-automoveandpublish-posts.yml must not mutate or commit.

Regression for 2026-10-08: a push-triggered "dry" publish-on-approval run still ran the
Unsplash/Cloudinary step (no dry_run input), a hardcoded dry_run:false move, and the
unconditional commit step, pushing bot edits to 29 approved drafts on master.
"""
from pathlib import Path

import yaml

WF = Path(__file__).resolve().parents[2] / ".github/workflows/reusable-automoveandpublish-posts.yml"


def _steps():
    wf = yaml.safe_load(WF.read_text())
    return [s for job in wf["jobs"].values() for s in job.get("steps", [])]


def _find(prefix):
    matches = [s for s in _steps() if str(s.get("name", "")).startswith(prefix)]
    assert len(matches) == 1, prefix
    return matches[0]


def test_unsplash_step_skipped_when_dry():
    assert "featuredimagefinder_dryrun" in _find("(4) Unsplash").get("if", "")


def test_commit_step_skipped_when_all_dry():
    cond = _find("(9) Commit").get("if", "")
    for name in ("featuredimagefinder", "autoschedule", "pretifier", "manualpublication"):
        assert f"inputs.{name}_dryrun" in cond


def test_no_hardcoded_false_dry_run_on_moves():
    for s in _steps():
        w = s.get("with") or {}
        if "function_to_run" in w:
            assert str(w.get("dry_run")).strip().lower() != "false", s.get("name")


def test_social_generate_does_not_open_pr_on_dry_run():
    wf = yaml.safe_load((WF.parent / "reusable_social-generate.yml").read_text())
    steps = [s for job in wf["jobs"].values() for s in job.get("steps", [])]
    open_pr = [s for s in steps if s.get("name") == "Open PR"][0]
    assert "inputs.dry_run" in open_pr["if"]


def test_indexation_cleanup_never_deletes_tracked_credentials():
    text = (WF.parent / "reusable_indexation-issues.yml").read_text()
    assert "rm -f *.secret.*" not in text
    assert "git ls-files --error-unmatch" in text
    assert 'rm -f ${{ inputs.service_account_file_path }}\n' not in text


def test_numpy_pinned_below_2_4():
    root = WF.parents[2]
    for rel in ("internal-linking/requirements.txt", "indexation-issues/requirements.txt",
                "seo-analysis/requirements-minimal.txt", "keyword-suggestion/requirements.txt"):
        lines = [l for l in (root / rel).read_text().splitlines() if l.strip().startswith("numpy")]
        assert lines and all("<2.4" in l for l in lines), rel
