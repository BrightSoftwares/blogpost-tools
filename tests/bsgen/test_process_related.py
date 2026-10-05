"""Tests for process_related permalink resolution.

Regression: a site `_config.yml` with `collections.posts.permalink: /:categories/...`
plus a top-level `permalink: pretty` made related links come out as
https://site/pretty/ (the style name was used literally and the collection
permalink was ignored).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "bsgen"))

import process_related  # noqa: E402
from process_related import (  # noqa: E402
    load_posts_index,
    site_posts_permalink,
    url_from_filepath,
)

SITE = "https://example.com"


def _post(posts_dir: Path, name: str, fm: str = "") -> Path:
    p = posts_dir / name
    p.write_text(f"---\ntitle: T\n{fm}---\nbody\n", encoding="utf-8")
    return p


def test_collection_permalink_wins_over_toplevel_pretty():
    cfg = {
        "permalink": "pretty",
        "collections": {"posts": {"permalink": "/blog/:year/:slug/"}},
    }
    assert site_posts_permalink(cfg) == "/blog/:year/:slug/"


def test_named_style_pretty_is_expanded_not_literal():
    tpl = site_posts_permalink({"permalink": "pretty"})
    assert tpl == "/:categories/:year/:month/:day/:title/"


def test_no_config_returns_none():
    assert site_posts_permalink({}) is None


def test_url_never_contains_pretty_segment(tmp_path):
    p = _post(tmp_path, "2026-03-04-hello-world.md", "categories: [tech]\n")
    url = url_from_filepath(p, SITE, "en", {"permalink": "pretty"})
    assert "/pretty" not in url
    assert url == f"{SITE}/tech/2026/03/04/hello-world/"


def test_collection_permalink_used_for_url(tmp_path):
    p = _post(tmp_path, "2026-03-04-hello-world.md", "categories: [tech]\n")
    cfg = {"permalink": "pretty", "collections": {"posts": {"permalink": "/:categories/:slug/"}}}
    assert url_from_filepath(p, SITE, "en", cfg) == f"{SITE}/tech/hello-world/"


def test_no_categories_segment_dropped(tmp_path):
    p = _post(tmp_path, "2026-03-04-hello-world.md")
    assert url_from_filepath(p, SITE, "en", {"permalink": "pretty"}) == f"{SITE}/2026/03/04/hello-world/"


def test_post_frontmatter_style_name_not_used_literally(tmp_path):
    p = _post(tmp_path, "2026-03-04-hello-world.md", "permalink: pretty\n")
    url = url_from_filepath(p, SITE, "en", {"permalink": "pretty"})
    assert "/pretty" not in url
    assert url.endswith("/2026/03/04/hello-world/")


def test_post_frontmatter_explicit_path_wins(tmp_path):
    p = _post(tmp_path, "2026-03-04-hello-world.md", "permalink: /custom/path/\n")
    assert url_from_filepath(p, SITE, "en", {"permalink": "pretty"}) == f"{SITE}/custom/path/"


def test_date_style_uses_html_extension(tmp_path):
    p = _post(tmp_path, "2026-03-04-hello-world.md")
    assert url_from_filepath(p, SITE, "en", {"permalink": "date"}) == f"{SITE}/2026/03/04/hello-world.html"


def test_load_posts_index_reads_config_from_parent(tmp_path):
    (tmp_path / "_config.yml").write_text(
        "permalink: pretty\ncollections:\n  posts:\n    permalink: /:year/:slug/\n",
        encoding="utf-8",
    )
    posts = tmp_path / "en" / "_posts"
    posts.mkdir(parents=True)
    _post(posts, "2026-03-04-hello-world.md")
    idx = load_posts_index(posts, SITE, "en")
    assert [e["url"] for e in idx] == [f"{SITE}/2026/hello-world/"]


def test_end_to_end_process_has_no_pretty_links(tmp_path):
    (tmp_path / "_config.yml").write_text(
        "permalink: pretty\ncollections:\n  posts:\n    permalink: /:year/:slug/\n",
        encoding="utf-8",
    )
    posts = tmp_path / "_posts"
    posts.mkdir()
    _post(posts, "2026-01-01-alpha.md", "tags: [x]\n")
    cur = posts / "2026-02-02-current.md"
    cur.write_text(
        "---\ntitle: Current\ntags: [x]\n---\n\n```bsgen:related\n"
        "anchors:\n  - wikilink: \"[[alpha]]\"\n    anchor_text: Alpha\n```\n",
        encoding="utf-8",
    )
    process_related.process(cur, posts, SITE, "en")
    out = cur.read_text(encoding="utf-8")
    assert "/pretty" not in out
    assert f'href="{SITE}/2026/alpha/"' in out
