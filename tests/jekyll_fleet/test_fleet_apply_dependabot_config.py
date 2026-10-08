import os

import yaml
from fleet_helpers import file_payload, make_gh
import fleet_apply_dependabot_config as apply_mod

TEMPLATE = open(apply_mod.TEMPLATE, encoding="utf-8").read()
REPO = "a/site"


def base_routes(root=("Gemfile",), workflows=True, existing=None, branch="main", truncated=False):
    paths = list(root) + ([".github/workflows/ci.yml"] if workflows else [])
    r = {
        ("GET", f"/repos/{REPO}"): (200, {"default_branch": branch}),
        ("GET", f"/repos/{REPO}/git/trees/{branch}?recursive=1"):
            (200, {"truncated": truncated, "tree": [{"path": p, "type": "blob"} for p in paths]}),
        ("GET", f"/repos/{REPO}/git/ref/heads/{branch}"): (200, {"object": {"sha": "base111"}}),
    }
    if existing is not None:
        r[("GET", f"/repos/{REPO}/contents/.github/dependabot.yml?ref={branch}")] = (200, file_payload(existing))
    return r


def test_template_is_valid_yaml_for_every_subset():
    for eco in (["bundler"], ["bundler", "github-actions"], ["bundler", "github-actions", "pip"], ["pip"]):
        doc = yaml.safe_load(apply_mod.render_config(TEMPLATE, eco))
        assert doc["version"] == 2
        assert [u["package-ecosystem"] for u in doc["updates"]] == eco


def test_template_security_updates_are_grouped_and_weekly():
    doc = yaml.safe_load(TEMPLATE)
    for upd in doc["updates"]:
        assert upd["schedule"]["interval"] == "weekly"
    bundler = doc["updates"][0]
    assert bundler["groups"]["bundler-security"]["applies-to"] == "security-updates"


def test_bundler_block_ignores_wikilinks_gem_and_jekyll_majors():
    bundler = yaml.safe_load(TEMPLATE)["updates"][0]
    assert bundler["package-ecosystem"] == "bundler"
    ignore = {i["dependency-name"]: i.get("update-types") for i in bundler["ignore"]}
    # no update-types == ignore all versions
    assert ignore == {"jekyll-obsidian-wikilinks": None, "jekyll": ["version-update:semver-major"]}
    # the other ecosystems must not inherit the bundler-specific ignores
    for upd in yaml.safe_load(TEMPLATE)["updates"][1:]:
        assert "ignore" not in upd


def test_rendered_config_keeps_ignore_only_for_bundler():
    doc = yaml.safe_load(apply_mod.render_config(TEMPLATE, ["bundler", "github-actions", "pip"]))
    assert [bool(u.get("ignore")) for u in doc["updates"]] == [True, False, False]
    doc = yaml.safe_load(apply_mod.render_config(TEMPLATE, ["github-actions"]))
    assert "ignore" not in doc["updates"][0]


def test_detect_ecosystems():
    gh, _ = make_gh(base_routes(root=("Gemfile", "Pipfile.lock")))
    assert apply_mod.detect_ecosystems(gh, REPO, "main") == (
        {"bundler": ["/"], "github-actions": ["/"], "pip": ["/"]}, "")
    gh, _ = make_gh(base_routes(root=("Gemfile",), workflows=False))
    assert apply_mod.detect_ecosystems(gh, REPO, "main")[0] == {"bundler": ["/"]}


def test_nested_pip_manifests_get_their_own_block_and_vendor_is_ignored():
    gh, _ = make_gh(base_routes(root=("Gemfile", "_data/cleanup_scripts/Pipfile.lock", "scripts/requirements.txt",
                                      "vendor/bundle/x/requirements.txt", "node_modules/y/requirements.txt",
                                      ".venv/Lib/site-packages/numpy/requirements.txt", "venv/z/Pipfile")))
    eco, note = apply_mod.detect_ecosystems(gh, REPO, "main")
    assert eco["pip"] == ["/_data/cleanup_scripts", "/scripts"] and note == ""
    doc = yaml.safe_load(apply_mod.render_config(TEMPLATE, eco))
    pip_dirs = [u["directory"] for u in doc["updates"] if u["package-ecosystem"] == "pip"]
    assert pip_dirs == ["/_data/cleanup_scripts", "/scripts"]


def test_truncated_tree_is_flagged_and_extra_dirs_are_honoured():
    gh, _ = make_gh(base_routes(truncated=True))
    eco, note = apply_mod.detect_ecosystems(gh, REPO, "main", extra_pip_dirs=["_data/x"])
    assert "truncated" in note and eco["pip"] == ["/_data/x"]


def test_dry_run_never_writes():
    gh, api = make_gh(base_routes())
    msg = apply_mod.process_repo(gh, REPO, None, TEMPLATE, apply=False, enable_alerts=False)
    assert "WOULD add" in msg and "[bundler+github-actions]" in msg
    assert api.writes() == []


def test_already_canonical_is_skipped_even_with_trailing_whitespace():
    wanted = apply_mod.render_config(TEMPLATE, ["bundler", "github-actions"]).replace("\n", "  \n")
    gh, api = make_gh(base_routes(existing=wanted))
    msg = apply_mod.process_repo(gh, REPO, None, TEMPLATE, apply=True, enable_alerts=False)
    assert "already canonical" in msg
    assert api.writes() == []


def test_skip_repo_without_manifests():
    gh, _ = make_gh(base_routes(root=("README.md",), workflows=False))
    assert "SKIP" in apply_mod.process_repo(gh, REPO, None, TEMPLATE, False, False)


def test_apply_creates_branch_writes_file_and_opens_pr_against_default_branch():
    routes = base_routes(branch="master")
    routes[("GET", f"/repos/{REPO}/git/ref/heads/claude/automated-work")] = (404, {})
    routes[("POST", f"/repos/{REPO}/git/refs")] = (201, {})
    routes[("PUT", f"/repos/{REPO}/contents/.github/dependabot.yml")] = (201, {})
    routes[("GET", f"/repos/{REPO}/pulls?state=open&head=a:claude/automated-work")] = (200, [])
    routes[("POST", f"/repos/{REPO}/pulls")] = (201, {"html_url": "https://github.com/a/site/pull/1"})
    gh, api = make_gh(routes)
    msg = apply_mod.process_repo(gh, REPO, None, TEMPLATE, apply=True, enable_alerts=False)
    assert "opened PR https://github.com/a/site/pull/1" in msg
    method_paths = [(m, p) for m, p, _ in api.writes()]
    assert method_paths == [("POST", f"/repos/{REPO}/git/refs"),
                            ("PUT", f"/repos/{REPO}/contents/.github/dependabot.yml"),
                            ("POST", f"/repos/{REPO}/pulls")]
    put_body = api.writes()[1][2]
    assert put_body["branch"] == "claude/automated-work"
    assert put_body["message"] == "chore(deps): add canonical Dependabot config"
    assert api.writes()[2][2]["base"] == "master"
    # never writes to the default branch
    assert all(b is None or b.get("branch") != "master" for _, _, b in api.writes())


def test_existing_open_pr_is_reused_and_unmerged_branch_kept():
    routes = base_routes()
    routes[("GET", f"/repos/{REPO}/git/ref/heads/claude/automated-work")] = (200, {"object": {"sha": "w1"}})
    routes[("GET", f"/repos/{REPO}/compare/main...claude/automated-work")] = (200, {"ahead_by": 2, "behind_by": 0})
    routes[("PUT", f"/repos/{REPO}/contents/.github/dependabot.yml")] = (200, {})
    routes[("GET", f"/repos/{REPO}/contents/.github/dependabot.yml?ref=claude/automated-work")] = (200, file_payload("old"))
    routes[("GET", f"/repos/{REPO}/pulls?state=open&head=a:claude/automated-work")] = (200, [{"html_url": "https://x/pr/9"}])
    gh, api = make_gh(routes)
    msg = apply_mod.process_repo(gh, REPO, None, TEMPLATE, True, False)
    assert "PR already open: https://x/pr/9" in msg and "unmerged commits" in msg
    assert not [c for c in api.writes() if c[0] in ("PATCH", "POST")]
    assert api.writes()[0][2]["sha"]  # updating an existing file passes its sha


def test_merged_work_branch_is_fast_forwarded():
    routes = base_routes()
    routes[("GET", f"/repos/{REPO}/git/ref/heads/claude/automated-work")] = (200, {"object": {"sha": "w1"}})
    routes[("GET", f"/repos/{REPO}/compare/main...claude/automated-work")] = (200, {"ahead_by": 0, "behind_by": 3})
    routes[("PATCH", f"/repos/{REPO}/git/refs/heads/claude/automated-work")] = (200, {})
    gh, api = make_gh(routes)
    note = apply_mod.ensure_branch(gh, REPO, "main", apply=True)
    assert "fast-forward" in note
    assert api.writes()[0][2] == {"sha": "base111", "force": True}


def test_enable_alerts_only_when_disabled():
    routes = base_routes(existing=apply_mod.render_config(TEMPLATE, ["bundler", "github-actions"]))
    routes[("GET", f"/repos/{REPO}/dependabot/alerts?per_page=1")] = (403, {"message": "disabled"})
    gh, api = make_gh(routes)
    assert "would enable" in apply_mod.process_repo(gh, REPO, None, TEMPLATE, False, True)
    assert api.writes() == []
    routes[("PUT", f"/repos/{REPO}/vulnerability-alerts")] = (204, {})
    gh, api = make_gh(routes)
    assert "enabled alerts (HTTP 204)" in apply_mod.process_repo(gh, REPO, None, TEMPLATE, True, True)
