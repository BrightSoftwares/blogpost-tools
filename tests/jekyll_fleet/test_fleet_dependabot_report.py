import datetime as dt

from fleet_helpers import file_payload, make_gh
import fleet_dependabot_report as rep


def alert(sev):
    return {"security_advisory": {"severity": sev}}


def routes_for(repo, alerts_resp, gemfile="gem 'jekyll'", plugin=False, dependabot=True):
    r = {
        ("GET", f"/repos/{repo}"): (200, {"default_branch": "main"}),
        ("GET", f"/repos/{repo}/dependabot/alerts?state=open&per_page=1"): alerts_resp,
        ("GET", f"/repos/{repo}/dependabot/alerts?state=open&per_page=100"): alerts_resp,
        ("GET", f"/repos/{repo}/contents/Gemfile?ref=main"): (200, file_payload(gemfile)),
        ("GET", f"/repos/{repo}/commits?path=Gemfile.lock&per_page=1&sha=main"):
            (200, [{"commit": {"committer": {"date": "2026-09-25T10:00:00Z"}}}]),
    }
    if plugin:
        r[("GET", f"/repos/{repo}/contents/_plugins/wikilinks.rb?ref=main")] = (200, file_payload("x"))
    if dependabot:
        r[("GET", f"/repos/{repo}/contents/.github/dependabot.yml?ref=main")] = (200, file_payload("version: 2"))
    return r


def test_counts_by_severity_and_columns():
    gh, _ = make_gh(routes_for("a/b", (200, [alert("high"), alert("high"), alert("low")]), plugin=True))
    rows = rep.collect(gh, [("a/b", None)], today=dt.date(2026, 10, 5))
    row = rows[0]
    assert row["counts"] == {"critical": 0, "high": 2, "medium": 0, "low": 1}
    assert row["lock_age"] == 10
    assert row["wikilinks"] == "local-copy"
    assert row["dependabot_yml"] is True


def test_gem_mode_wins_over_local_copy():
    gh, _ = make_gh(routes_for("a/b", (200, []), gemfile="gem 'jekyll-obsidian-wikilinks', git: 'x'", plugin=True))
    assert rep.wikilinks_mode(gh, "a/b", "main") == "gem"


def test_alerts_disabled_is_reported_not_zero():
    gh, _ = make_gh(routes_for("a/b", (403, {"message": "Dependabot alerts are disabled for this repository."}), dependabot=False))
    row = rep.collect(gh, [("a/b", None)])[0]
    assert row["counts"] is None and row["note"] == "alerts disabled"
    table = rep.render([row])
    assert "n/a (alerts disabled)" in table
    assert "| NO |" in table


def test_inaccessible_repo():
    gh, _ = make_gh({})
    rows = rep.collect(gh, [("a/missing", None)])
    assert rows == [{"repo": "a/missing", "error": "repo not accessible"}]
    assert "repo not accessible" in rep.render(rows)


def test_render_totals():
    rows = [
        {"repo": "a/1", "branch": "main", "counts": {"critical": 0, "high": 2, "medium": 1, "low": 0},
         "note": "", "dependabot_yml": True, "lock_age": 3, "wikilinks": "gem"},
        {"repo": "a/2", "branch": "main", "counts": {"critical": 1, "high": 0, "medium": 0, "low": 4},
         "note": "", "dependabot_yml": False, "lock_age": None, "wikilinks": "none"},
    ]
    out = rep.render(rows)
    assert "| **Fleet total** | | 1 | 2 | 1 | 4 | 8 |" in out
    assert "| ? |" in out


def test_paging_failure_is_reported_not_zero():
    routes = routes_for("a/b", (200, [alert("high")]))
    routes[("GET", "/repos/a/b/dependabot/alerts?state=open&per_page=100")] = (403, {"message": "denied"})
    gh, _ = make_gh(routes)
    row = rep.collect(gh, [("a/b", None)])[0]
    assert row["counts"] is None and "HTTP 403" in row["note"]


def test_footnote_when_alerts_unreadable():
    row = {"repo": "a/x", "branch": "main", "counts": None, "note": "alerts disabled",
           "dependabot_yml": False, "lock_age": 1, "wikilinks": "none"}
    assert "exclude 1 repo(s)" in rep.render([row])
