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
