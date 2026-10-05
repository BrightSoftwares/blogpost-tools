import pytest
from fleet_helpers import make_gh
from fleet_common import GitHub, GitHubError, parse_repo_list


def test_parse_repo_list_handles_comments_and_branch():
    text = "# fleet\nacme/site-a\n\nacme/site-b gh-pages  # old\n"
    assert parse_repo_list(text) == [("acme/site-a", None), ("acme/site-b", "gh-pages")]


def test_parse_repo_list_rejects_garbage():
    with pytest.raises(ValueError):
        parse_repo_list("not a repo")


def test_token_required():
    with pytest.raises(ValueError):
        GitHub("")


def test_from_env_reads_token(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "abc")
    monkeypatch.delenv("GH_TOKEN", raising=False)
    assert GitHub.from_env(transport=lambda *a: (200, {}, b"[]"))._token == "abc"


def test_paginate_follows_link_header_cursor():
    link = '<https://api.github.com/x?per_page=100&after=abc>; rel="next", <https://api.github.com/x?last>; rel="last"'
    gh, api = make_gh({
        ("GET", "/x?per_page=100"): (200, [{"n": 1}], {"Link": link}),
        ("GET", "/x?per_page=100&after=abc"): (200, [{"n": 2}]),
    })
    assert [i["n"] for i in gh.paginate("/x")] == [1, 2]
    assert len(api.calls) == 2


def test_paginate_raises_instead_of_returning_empty_on_error():
    gh, _ = make_gh({("GET", "/x?per_page=100"): (403, {"message": "no"})})
    with pytest.raises(GitHubError):
        list(gh.paginate("/x"))
