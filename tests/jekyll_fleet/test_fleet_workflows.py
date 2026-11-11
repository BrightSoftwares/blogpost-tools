import os

import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def load(name):
    with open(os.path.join(ROOT, ".github", "workflows", name), encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    doc["on"] = doc.pop(True, doc.get("on"))  # PyYAML parses the bare key `on` as True
    return doc


def test_sweeper_is_weekly_tuesday_on_hosted_runner_with_apply():
    wf = load("fleet-dependabot-sweeper.yml")
    assert wf["on"]["schedule"] == [{"cron": "0 6 * * 2"}]
    assert "workflow_dispatch" in wf["on"]
    job = wf["jobs"]["sweep"]
    assert job["runs-on"] == "ubuntu-latest"
    assert job["env"]["GITHUB_TOKEN"] == "${{ secrets.REPO_ACCESS_TOKEN }}"
    steps = "\n".join(str(s.get("run", "")) for s in job["steps"])
    assert "fleet_close_superseded_dependabot.py" in steps and "--apply" in steps
    assert "fleet_dependabot_report.py" in steps and "GITHUB_STEP_SUMMARY" in steps
    assert wf["permissions"] == {"contents": "read"}


def test_sweeper_fails_fast_with_a_clear_message_when_token_secret_is_missing():
    steps = load("fleet-dependabot-sweeper.yml")["jobs"]["sweep"]["steps"]
    names = [s.get("name", "") for s in steps]
    guard = next(i for i, n in enumerate(names) if "token secret" in n)
    close = next(i for i, n in enumerate(names) if n.startswith("Close superseded"))
    assert guard < close
    assert "REPO_ACCESS_TOKEN" in steps[guard]["run"] and "exit 1" in steps[guard]["run"]


def test_drift_check_targets_current_jekyll_and_hosted_runner():
    wf = load("jekyll-version-drift-check.yml")
    assert wf["env"]["TARGET_JEKYLL_VERSION"] == "4.3.4"
    for job in wf["jobs"].values():
        assert "self-hosted" not in job["runs-on"]
        assert "ubuntu-latest" in job["runs-on"]


def test_fleet_tests_workflow_watches_the_sweeper_and_drift_check():
    wf = load("jekyll-fleet-tests.yml")
    for trigger in ("pull_request", "push"):
        paths = wf["on"][trigger]["paths"]
        assert ".github/workflows/fleet-dependabot-sweeper.yml" in paths
        assert ".github/workflows/jekyll-version-drift-check.yml" in paths


def test_align_workflow_separates_token_and_fleet_code():
    wf = load("fleet-align-gems.yml")
    jobs = wf["jobs"]
    assert wf["permissions"] == {"contents": "read"}
    assert "secrets." not in str(jobs["build"]) and "GITHUB_TOKEN" not in str(jobs["build"])
    assert jobs["build"]["permissions"] == {"contents": "read"}
    assert "--phase build" in str(jobs["build"]["steps"]) and "--phase push" not in str(jobs["build"]["steps"])
    assert "--phase build" not in str(jobs["push"]["steps"]) and "--phase fetch" not in str(jobs["push"]["steps"])
    for name in ("fetch", "build", "push"):
        assert all(s.get("with", {}).get("persist-credentials") is False for s in jobs[name]["steps"]
                   if str(s.get("uses", "")).startswith("actions/checkout"))
    assert jobs["push"]["needs"] == "build" and jobs["build"]["needs"] == "fetch"


def test_align_workflow_ships_the_trees_as_one_archive_so_hidden_files_survive():
    # upload-artifact failed with "Maximum call stack size exceeded" on the fleet's file count (run 43045847997):
    # the trees travel as ONE tar (dotfiles included), packed in fetch and unpacked in build.
    jobs = load("fleet-align-gems.yml")["jobs"]
    steps = jobs["fetch"]["steps"]
    pack = next(s for s in steps if "tar -czf fleet-trees.tgz -C work ." in str(s.get("run", "")))
    up = next(s for s in steps if str(s.get("uses", "")).startswith("actions/upload-artifact"))
    assert up["with"]["name"] == "fleet-trees" and up["with"]["path"] == "fleet-trees.tgz"
    assert steps.index(pack) < steps.index(up)
    bsteps = jobs["build"]["steps"]
    dl = next(s for s in bsteps if str(s.get("uses", "")).startswith("actions/download-artifact"))
    unpack = next(s for s in bsteps if "tar -xzf archive/fleet-trees.tgz -C work" in str(s.get("run", "")))
    assert dl["with"]["name"] == "fleet-trees" and dl["with"]["path"] == "archive"
    assert bsteps.index(dl) < bsteps.index(unpack)


GUARD = "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)"


def test_align_workflow_only_runs_from_the_default_branch():
    wf = load("fleet-align-gems.yml")
    assert wf["jobs"]["fetch"]["if"] == GUARD
    for name in ("fetch", "build", "push"):
        assert GUARD in wf["jobs"][name]["if"], name


def test_align_workflow_one_bad_repo_does_not_block_the_others():
    jobs = load("fleet-align-gems.yml")["jobs"]
    assert jobs["build"]["if"] == "${{ !cancelled() && needs.fetch.result != 'skipped' && " + GUARD + " }}"
    assert jobs["push"]["if"] == "${{ !cancelled() && needs.build.result != 'skipped' && " + GUARD + " }}"
    for job, step_id in (("fetch", "fetch"), ("build", "build")):
        steps = jobs[job]["steps"]
        phase = next(s for s in steps if s.get("id") == step_id)
        assert phase["continue-on-error"] is True
        up = next(s for s in steps if str(s.get("uses", "")).startswith("actions/upload-artifact"))
        assert up["with"]["if-no-files-found"] == "ignore"
        fail = next(s for s in steps if s.get("if") == f"steps.{step_id}.outcome == 'failure'")
        assert "::error::" in fail["run"] and "exit 1" in fail["run"]
        assert steps.index(phase) < steps.index(up) < steps.index(fail)  # failure is reported after the hand-over
    for job in ("build", "push"):
        dl = next(s for s in jobs[job]["steps"] if str(s.get("uses", "")).startswith("actions/download-artifact"))
        # fetch/build always write a manifest, so the artifact exists; a failed download is a real failure, not "nothing to do"
        assert "continue-on-error" not in dl, job
    assert "mkdir -p patches" in str(jobs["push"]["steps"]) and "mkdir -p work patches" in str(jobs["build"]["steps"])


def test_align_token_jobs_pin_actions_by_commit_sha_and_dry_run_holds_no_secret():
    import re

    jobs = load("fleet-align-gems.yml")["jobs"]
    # `uses` carries the pin; the trailing `# v4` comment is dropped by the YAML parser
    for name in ("fetch", "push"):
        for step in jobs[name]["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"(?:actions/[\w-]+|ruby/setup-ruby)@[0-9a-f]{40}", step["uses"]), step["uses"]
    run = next(s for s in jobs["push"]["steps"] if "--phase push" in str(s.get("run", "")))
    assert "${{" not in run["run"], "expression injected into the shell script"
    assert run["env"]["APPLY"] == "${{ inputs.apply }}"
    assert run["env"]["GITHUB_TOKEN"] == "${{ inputs.apply && secrets.REPO_ACCESS_TOKEN || '' }}"


def test_align_push_job_runs_lock_structure_on_the_pinned_ruby_of_the_build_job():
    jobs = load("fleet-align-gems.yml")["jobs"]
    ruby = {n: next(s for s in jobs[n]["steps"] if str(s.get("uses", "")).startswith("ruby/setup-ruby@")) for n in ("build", "push")}
    assert ruby["push"]["with"]["ruby-version"] == ruby["build"]["with"]["ruby-version"]
    assert ruby["push"]["uses"] == ruby["build"]["uses"], "push must use the same pinned ruby/setup-ruby SHA as build"
    steps = jobs["push"]["steps"]
    order = [i for i, s in enumerate(steps) if "ruby/setup-ruby" in str(s.get("uses", "")) or "--phase push" in str(s.get("run", ""))]
    assert "ruby/setup-ruby" in steps[order[0]].get("uses", ""), "setup-ruby must run before the push phase"
