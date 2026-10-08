import datetime as dt

from fleet_helpers import file_payload, make_gh
import fleet_close_superseded_dependabot as mod

TEMPLATE = open(mod.TEMPLATE, encoding="utf-8").read()
REPO = "a/site"
TODAY = dt.date(2026, 10, 8)
LOCK = """GEM
  specs:
    ffi (1.16.3)
    i18n (1.14.7)
    jekyll (4.3.4)
    jekyll-feed (0.16.0)
    rexml (3.2.9)
    jekyll-obsidian-wikilinks (2.1.1)
    ffi (1.17.4-x86_64-linux-gnu)
"""
GEMFILE = """gem "jekyll", "~> 4.3.4"
gem "ffi", "= 1.16.3"
group :jekyll_plugins do
  gem 'jekyll-obsidian-wikilinks',
      git: 'https://github.com/BrightSoftwares/blogpost-tools.git',
      tag: 'jekyll-obsidian-wikilinks-v2.1.1'
end
"""


def pr(number, branch, title, body="", user="dependabot[bot]", created="2026-10-06T10:00:00Z"):
    return {"number": number, "user": {"login": user}, "head": {"ref": branch}, "title": title,
            "body": body, "created_at": created}


def ctx(lock=LOCK, gemfile=GEMFILE):
    return {"ecosystems": mod.template_ecosystems(TEMPLATE), "pip_dirs": set(mod.PIP_SCOPE_DIRS),
            "lock": lock, "gemfile": gemfile}


def classify(p, c=None, routes=None):
    gh, _ = make_gh(routes or {})
    return mod.classify(gh, REPO, p, c or ctx(), TODAY, sleep=lambda s: None)


# ---- helpers

def test_parse_version_variants():
    assert mod.parse_version("jekyll-obsidian-wikilinks-v2.1.1") == (2, 1, 1)
    assert mod.parse_version("~> 2.9.1") == (2, 9, 1)
    assert mod.parse_version(">=1.0") == (1, 0)
    assert mod.parse_version("1.17.4-x86_64-linux-gnu") == (1, 17, 4)
    assert mod.parse_version("main") is None and mod.parse_version(None) is None
    assert mod.cmp_versions((4, 3), (4, 3, 0)) == 0 and mod.cmp_versions((4, 3, 2), (4, 3, 4)) < 0


def test_template_ecosystems_exclude_npm():
    assert mod.template_ecosystems(TEMPLATE) == {"bundler", "github-actions", "pip"}


def test_parse_updates_from_title_body_and_group():
    assert mod.parse_updates("Bump rexml from 3.2.5 to 3.2.6", "") == [("rexml", "3.2.5", "3.2.6")]
    assert mod.parse_updates("Bump x from 1 to 2 in /scripts", "") == [("x", "1", "2")]
    body = "Updates `a` from 1.0 to 1.1\nstuff\nUpdates `b` to 2.0\n"
    assert mod.parse_updates("bump the group with 2 updates", body) == [("a", "1.0", "1.1"), ("b", None, "2.0")]


def test_lock_and_gemfile_versions():
    assert mod.lock_version(LOCK, "ffi") == (1, 17, 4)  # highest across platform variants
    assert mod.lock_version(LOCK, "missing") is None
    assert mod.gemfile_version(GEMFILE, "ffi") == (1, 16, 3)
    assert mod.gemfile_version(GEMFILE, "jekyll-obsidian-wikilinks") == (2, 1, 1)  # git tag wins
    assert mod.current_version(None, GEMFILE, "jekyll") == (4, 3, 4)  # no lock: Gemfile fallback


# ---- rule A

def test_rule_a_wikilinks_downgrade_is_closed():
    p = pr(1, "dependabot/bundler/jekyll-obsidian-wikilinks-jekyll-obsidian-wikilinks-v2.1.0",
           "chore(deps): bump jekyll-obsidian-wikilinks from jekyll-obsidian-wikilinks-v2.1.1 to jekyll-obsidian-wikilinks-v2.1.0",
           "Bumps [jekyll-obsidian-wikilinks](https://x) from jekyll-obsidian-wikilinks-v2.1.1 to jekyll-obsidian-wikilinks-v2.1.0.\n")
    v = classify(p)
    assert v and v.rule.startswith("A")


def test_rule_a_not_applied_to_a_mixed_group():
    body = "Updates `jekyll-feed` from 0.16.0 to 0.15.0\nUpdates `i18n` from 1.14.7 to 1.15.2\n"
    assert classify(pr(2, "dependabot/bundler/grp-abc", "bump the bundler-minor-patch group with 2 updates", body)) is None


# ---- rule B / D

def test_rule_b_old_pr_with_target_below_lock():
    p = pr(3, "dependabot/bundler/rexml-3.2.6", "Bump rexml from 3.2.5 to 3.2.6", created="2023-01-01T00:00:00Z")
    v = classify(p)
    assert v and v.rule.startswith("B") and "3.2.6 <= 3.2.9" in v.reason


def test_rule_d_fresh_pr_whose_target_lock_already_has():
    p = pr(4, "dependabot/bundler/i18n-1.14.7", "Bump i18n from 1.14.1 to 1.14.7", created="2026-10-05T00:00:00Z")
    v = classify(p)
    assert v and v.rule.startswith("D")


def test_rule_b_uses_gemfile_when_there_is_no_lock():
    p = pr(5, "dependabot/bundler/jekyll-4.3.2", "Bump jekyll from 4.3.1 to 4.3.2", created="2023-03-01T00:00:00Z")
    v = classify(p, ctx(lock=None))
    assert v and v.rule.startswith("B")


def test_rule_b_group_requires_every_update_to_be_satisfied():
    body = "Updates `rexml` from 3.2.5 to 3.2.6\nUpdates `i18n` from 1.14.1 to 1.15.2\n"
    p = pr(6, "dependabot/bundler/grp-x", "bump the bundler-minor-patch group with 2 updates", body,
           created="2023-01-01T00:00:00Z")
    assert classify(p, routes={("GET", f"/repos/{REPO}/pulls/6"): (200, {"mergeable": True})}) is None


def test_rule_b_stale_conflicting_pr_is_closed_but_mergeable_one_is_not():
    p = pr(7, "dependabot/bundler/jekyll-seo-tag-2.8.0", "Bump jekyll-seo-tag from 2.7.1 to 2.8.0",
           created="2022-09-12T00:00:00Z")
    v = classify(p, routes={("GET", f"/repos/{REPO}/pulls/7"): (200, {"mergeable": False})})
    assert v and v.rule.startswith("B") and "no longer mergeable" in v.reason
    assert classify(p, routes={("GET", f"/repos/{REPO}/pulls/7"): (200, {"mergeable": True})}) is None


def test_mergeable_null_is_retried_then_left_alone():
    p = pr(8, "dependabot/bundler/jekyll-seo-tag-2.8.0", "Bump jekyll-seo-tag from 2.7.1 to 2.8.0",
           created="2022-09-12T00:00:00Z")
    gh, api = make_gh({("GET", f"/repos/{REPO}/pulls/8"): (200, {"mergeable": None})})
    assert mod.classify(gh, REPO, p, ctx(), TODAY, sleep=lambda s: None) is None
    assert len([c for c in api.calls if c[1] == f"/repos/{REPO}/pulls/8"]) == mod.MERGEABLE_RETRIES


# ---- rule C

def test_rule_c_npm_is_out_of_scope():
    p = pr(9, "dependabot/npm_and_yarn/backup/dev-awesome-tool/semver-6.3.1", "Bump semver from 6.3.0 to 6.3.1 in /backup/dev-awesome-tool")
    v = classify(p)
    assert v and v.rule.startswith("C") and "npm" in v.reason


def test_rule_c_pip_tooling_directory_closed_but_site_directory_kept():
    tooling = pr(10, "dependabot/pip/scripts/numpy-gte-2.5.3", "update numpy requirement from >=1.24.0 to >=2.5.3 in /scripts")
    v = classify(tooling)
    assert v and v.rule.startswith("C") and "/scripts" in v.reason
    site = pr(11, "dependabot/pip/_data/cleanup_scripts/yt-1.2.4", "bump youtube-transcript-api from 0.6.3 to 1.2.4 in /_data/cleanup_scripts")
    assert classify(site) is None


def test_rule_c_directory_is_read_from_files_when_title_has_none():
    p = pr(12, "dependabot/pip/migration/grp-abc", "bump the pip-minor-patch group with 2 updates")
    routes = {("GET", f"/repos/{REPO}/pulls/12/files?per_page=100"): (200, [{"filename": "migration/requirements.txt"}])}
    v = classify(p, routes=routes)
    assert v and v.rule.startswith("C") and "/migration" in v.reason


# ---- legitimate upgrades / authors are never closed

def test_legitimate_upgrade_is_not_closed():
    p = pr(13, "dependabot/bundler/ffi-1.17.5", "update ffi requirement from = 1.16.3 to 1.17.5")
    assert classify(p) is None
    p = pr(14, "dependabot/bundler/jekyll-seo-tag-tw-2.9.1", "update jekyll-seo-tag requirement from ~> 2.7.1 to ~> 2.9.1")
    assert classify(p, ctx(lock=LOCK + "    jekyll-seo-tag (2.7.1)\n")) is None
    # an old but mergeable legitimate upgrade is kept too
    old = pr(15, "dependabot/bundler/jekyll-feed-0.17.0", "Bump jekyll-feed from 0.16.0 to 0.17.0", created="2022-10-17T00:00:00Z")
    assert classify(old, routes={("GET", f"/repos/{REPO}/pulls/15"): (200, {"mergeable": True})}) is None


def test_github_actions_prs_are_kept():
    p = pr(16, "dependabot/github_actions/actions-abc", "chore(ci): bump actions/checkout from 4 to 7 in the actions group")
    assert classify(p) is None


def test_non_dependabot_author_is_never_touched():
    p = pr(17, "dependabot/npm_and_yarn/x/y-1.0", "Bump y from 0.9 to 1.0", user="fullbright")
    assert classify(p) is None
    p = pr(18, "claude/automated-work", "ci: whatever", user="fullbright", created="2020-01-01T00:00:00Z")
    assert classify(p) is None


# ---- scan / apply

def routes_for_repo(prs):
    return {
        ("GET", f"/repos/{REPO}"): (200, {"default_branch": "main"}),
        ("GET", f"/repos/{REPO}/pulls?state=open&per_page=100"): (200, prs),
        ("GET", f"/repos/{REPO}/contents/Gemfile.lock?ref=main"): (200, file_payload(LOCK)),
        ("GET", f"/repos/{REPO}/contents/Gemfile?ref=main"): (200, file_payload(GEMFILE)),
    }


def sample_prs():
    return [
        pr(1, "dependabot/npm_and_yarn/a/b-1.0", "Bump b from 0.9 to 1.0 in /a"),
        pr(2, "dependabot/bundler/ffi-1.17.5", "update ffi requirement from = 1.16.3 to 1.17.5"),
        pr(3, "claude/automated-work", "human PR", user="fullbright"),
    ]


def test_scan_dry_run_never_writes_and_reports_groups():
    gh, api = make_gh(routes_for_repo(sample_prs()))
    results, kept, errors = mod.scan(gh, [(REPO, None)], TEMPLATE, today=TODAY, sleep=lambda s: None)
    assert [(n, v.rule[0]) for _, n, _, v in results] == [(1, "C")]
    assert [n for _, n, _ in kept] == [2]  # the human PR is not even listed
    assert errors == [] and api.writes() == []
    text = mod.render(results, kept, errors, apply=False)
    assert text.startswith("DRY-RUN: 1 PR(s) to close, 1 kept") and "## Rule C out-of-scope (1)" in text


def test_close_pr_comments_with_rule_then_closes_and_never_deletes():
    routes = {("POST", f"/repos/{REPO}/issues/1/comments"): (201, {}), ("PATCH", f"/repos/{REPO}/pulls/1"): (200, {})}
    gh, api = make_gh(routes)
    assert mod.close_pr(gh, REPO, 1, mod.Verdict("C out-of-scope", "ecosystem npm"))
    assert [(m, p) for m, p, _ in api.writes()] == [("POST", f"/repos/{REPO}/issues/1/comments"),
                                                   ("PATCH", f"/repos/{REPO}/pulls/1")]
    assert "rule C out-of-scope" in api.writes()[0][2]["body"] and "\n" not in api.writes()[0][2]["body"]
    assert api.writes()[1][2] == {"state": "closed"}
    assert not [c for c in api.calls if c[0] == "DELETE"]


def test_close_pr_reports_failure():
    gh, _ = make_gh({("POST", f"/repos/{REPO}/issues/1/comments"): (201, {}), ("PATCH", f"/repos/{REPO}/pulls/1"): (403, {})})
    assert mod.close_pr(gh, REPO, 1, mod.Verdict("C", "x")) is False


def test_inaccessible_repo_is_reported_not_fatal():
    gh, _ = make_gh({})
    results, kept, errors = mod.scan(gh, [(REPO, None)], TEMPLATE, today=TODAY)
    assert results == [] and errors == [f"{REPO}: repo not accessible"]
