"""Regression tests for scripts/seo_links_populator.py.

Every test here pins down one of the defects (D1..D7) that produced the garbage
`seo.links` on
`en/_posts/2026-11-09-we-built-a-crm-feature-on-ourselves-first-...md`
in BrightSoftwares/corporate-website (written by the scheduled
`seo-links-populate.yml` run of 2026-09-07, commit 65b679a):

    seo:
      links:
      - https://www.wikidata.org/wiki/Q134035659   # "Built" — a family name
      - https://www.wikidata.org/wiki/Q485643      # customer relationship mgmt (the only good one)
      - https://www.wikidata.org/wiki/Q47092857    # unverifiable
      - https://www.wikidata.org/wiki/Q7478101     # "we" — an English pronoun

No test here touches the network: `search_wikidata` / `resolve_entities` are
monkeypatched with recorded fixtures.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "seo_links_populator",
    Path(__file__).resolve().parent.parent.parent / "scripts" / "seo_links_populator.py",
)
pop = importlib.util.module_from_spec(_SPEC)
sys.modules["seo_links_populator"] = pop
_SPEC.loader.exec_module(pop)


POST = """---
title: We Built a CRM Feature on Ourselves First. It Found Two Bugs No Demo Would Have.
lang: en
seo:
  links:
  - https://www.wikidata.org/wiki/Q134035659
  - https://www.wikidata.org/wiki/Q485643
silot_terms: dogfooding crm sales pipeline automation code review saas bugs
tags:
- automation
- crm
- code-review
categories:
- automation
- saas
---

Body text.
"""


# --- D1: the "already has seo.links" guard --------------------------------

def test_existing_nested_seo_links_are_detected():
    """The flat frontmatter parser cannot see nested seo.links (this is why a
    force=false scheduled run overwrote a post that already had links)."""
    fm, raw_fm, _body = pop.parse_frontmatter(POST)
    assert fm.get("seo") == [], "precondition: the flat parser still mis-parses seo:"

    links = pop.extract_existing_seo_links(raw_fm)
    assert links == [
        "https://www.wikidata.org/wiki/Q134035659",
        "https://www.wikidata.org/wiki/Q485643",
    ]


def test_existing_seo_links_inline_list_form():
    raw = "title: T\nseo:\n  links: [https://www.wikidata.org/wiki/Q1, https://www.wikidata.org/wiki/Q2]\n"
    assert pop.extract_existing_seo_links(raw) == [
        "https://www.wikidata.org/wiki/Q1",
        "https://www.wikidata.org/wiki/Q2",
    ]


def test_no_seo_block_returns_no_links():
    assert pop.extract_existing_seo_links("title: T\nlang: en\n") == []


def test_process_file_skips_a_post_that_already_has_links(tmp_path, capsys):
    f = tmp_path / "post.md"
    f.write_text(POST, encoding="utf-8")
    assert pop.process_file(f, force=False) is False
    assert "already has 2 seo links" in capsys.readouterr().out
    assert f.read_text(encoding="utf-8") == POST


# --- D2: topic extraction --------------------------------------------------

def test_generic_title_words_are_not_topics():
    fm, _raw, body = pop.parse_frontmatter(POST)
    topics = dict(pop.extract_topics(fm, body))
    for junk in ("built", "ourselves", "found", "two", "demo", "first", "feature"):
        assert junk not in topics, f"{junk!r} is prose, not a topic"


def test_curated_fields_are_kept_and_marked_curated():
    fm, _raw, body = pop.parse_frontmatter(POST)
    topics = dict(pop.extract_topics(fm, body))
    assert topics["crm"] == pop.SOURCE_CURATED
    assert topics["code review"] == pop.SOURCE_CURATED
    assert topics["dogfooding"] == pop.SOURCE_CURATED


# --- D3: the relevance gate ------------------------------------------------

@pytest.mark.parametrize("topic,label,expected", [
    ("crm", "customer relationship management", "acronym"),
    ("docker", "Docker", "exact"),
    ("code review", "code review", "exact"),
    ("kubernetes", "Kubernetes cluster", None),   # single-word topics must match exactly
    ("code review", "code review process", "all_words"),
    ("ourselves", "we", None),          # the production failure
    ("built", "Built to Spill", None),
    ("two", "2", None),
])
def test_label_match_kind(topic, label, expected):
    assert pop.label_match_kind(topic, label) == expected


@pytest.mark.parametrize("description", [
    "first-person plural personal pronoun",
    "family name",
    "male given name",
    "1913 film",
    "commune in France",
    "scientific article published in 2009",
    "species of moth",
    "Wikimedia disambiguation page",
])
def test_non_topical_descriptions_are_rejected(description):
    assert pop.entity_is_non_topical(description) is True


@pytest.mark.parametrize("description", [
    "approach to managing a company's interaction with customers",
    "software licensing and delivery model",
    "set of software development practices",
])
def test_topical_descriptions_are_accepted(description):
    assert pop.entity_is_non_topical(description) is False


def test_pronoun_entity_is_never_selected(monkeypatch):
    """The exact production failure: searching 'ourselves' must not yield Q7478101."""
    monkeypatch.setattr(pop, "search_wikidata", lambda q, limit=3: [
        {"qid": "Q7478101", "label": "we",
         "description": "first-person plural personal pronoun", "match_type": "alias"},
        {"qid": "Q7108464", "label": "Ourselves", "description": "1913 film",
         "match_type": "label"},
    ])
    monkeypatch.setattr(pop.time, "sleep", lambda *_: None)
    assert pop.find_best_entities([("ourselves", pop.SOURCE_TITLE)],
                                  min_links=1, max_links=2, verbose=False) == []


def test_family_name_entity_is_never_selected(monkeypatch):
    monkeypatch.setattr(pop, "search_wikidata", lambda q, limit=3: [
        {"qid": "Q134035659", "label": "Built", "description": "family name",
         "match_type": "label"},
    ])
    monkeypatch.setattr(pop.time, "sleep", lambda *_: None)
    assert pop.find_best_entities([("built", pop.SOURCE_TITLE)],
                                  min_links=1, max_links=2, verbose=False) == []


def test_relevant_entity_is_selected(monkeypatch):
    monkeypatch.setattr(pop, "search_wikidata", lambda q, limit=3: [
        {"qid": "Q123", "label": "continuous delivery",
         "description": "software engineering practice", "match_type": "label"},
    ])
    monkeypatch.setattr(pop.time, "sleep", lambda *_: None)
    assert pop.find_best_entities([("continuous delivery", pop.SOURCE_CURATED)],
                                  min_links=1, max_links=2, verbose=False) == [
        "https://www.wikidata.org/wiki/Q123"
    ]


def test_nothing_is_padded_in_to_reach_min_links(monkeypatch):
    monkeypatch.setattr(pop, "search_wikidata", lambda q, limit=3: [
        {"qid": "Q9", "label": "unrelated thing", "description": "1999 album",
         "match_type": "label"},
    ])
    monkeypatch.setattr(pop.time, "sleep", lambda *_: None)
    out = pop.find_best_entities([("automation", pop.SOURCE_CURATED)],
                                 min_links=3, max_links=4, verbose=False)
    assert out == []


# --- D4: writing -----------------------------------------------------------

def test_update_seo_links_preserves_sibling_seo_keys():
    content = (
        "---\ntitle: T\nseo:\n  description: hand written\n  links:\n"
        "  - https://www.wikidata.org/wiki/Q1\n  type: Article\nlang: en\n---\nbody\n"
    )
    out = pop.update_seo_links(content, ["https://www.wikidata.org/wiki/Q485643"])
    assert "description: hand written" in out
    assert "type: Article" in out
    assert "Q485643" in out
    assert "Q1\n" not in out


def test_update_seo_links_inserts_a_seo_block_when_absent():
    content = "---\ntitle: T\nlang: en\n---\nbody\n"
    out = pop.update_seo_links(content, ["https://www.wikidata.org/wiki/Q485643"])
    _fm, raw, _body = pop.parse_frontmatter(out)
    assert pop.extract_existing_seo_links(raw) == ["https://www.wikidata.org/wiki/Q485643"]
    assert "title: T" in out and "lang: en" in out


def test_update_seo_links_roundtrips():
    content = "---\ntitle: T\n---\nbody\n"
    once = pop.update_seo_links(content, ["https://www.wikidata.org/wiki/Q1"])
    twice = pop.update_seo_links(once, ["https://www.wikidata.org/wiki/Q2"])
    _fm, raw, _ = pop.parse_frontmatter(twice)
    assert pop.extract_existing_seo_links(raw) == ["https://www.wikidata.org/wiki/Q2"]


# --- D5/D6: the hand-curated dictionary ------------------------------------

def test_dictionary_lookup_is_exact_not_substring():
    """'java' must not resolve to JavaScript's QID."""
    out = pop.find_best_entities([("java", pop.SOURCE_CURATED)],
                                 min_links=1, max_links=1, verbose=False)
    assert out == [f"https://www.wikidata.org/wiki/{pop.SINGLE_KEYWORDS['java']}"]
    assert pop.SINGLE_KEYWORDS["java"] != pop.SINGLE_KEYWORDS["javascript"]


def test_product_names_do_not_map_to_google_workspace():
    for bogus in ("pilotflow", "notiwise"):
        assert bogus not in pop.SINGLE_KEYWORDS


def test_no_two_keywords_share_a_qid_by_accident():
    seen: dict[str, str] = {}
    collisions = []
    for kw, qid in pop.SINGLE_KEYWORDS.items():
        if qid in seen:
            collisions.append((seen[qid], kw, qid))
        seen[qid] = kw
    assert collisions == [], f"duplicate QIDs in SINGLE_KEYWORDS: {collisions}"


# --- audit mode ------------------------------------------------------------

def test_audit_csv_flags_the_pronoun_and_keeps_the_acronym(tmp_path, monkeypatch):
    f = tmp_path / "post.md"
    f.write_text(POST.replace(
        "  - https://www.wikidata.org/wiki/Q485643",
        "  - https://www.wikidata.org/wiki/Q485643\n  - https://www.wikidata.org/wiki/Q7478101",
    ), encoding="utf-8")

    monkeypatch.setattr(pop, "resolve_entities", lambda qids: {
        "Q134035659": {"label": "Built", "description": "family name", "missing": False},
        "Q485643": {"label": "customer relationship management",
                    "description": "approach to managing a company's interaction with customers",
                    "missing": False},
        "Q7478101": {"label": "we", "description": "first-person plural personal pronoun",
                     "missing": False},
    })

    csv_path = tmp_path / "audit.csv"
    counts = pop.audit_files([f], csv_path)

    import csv as _csv
    rows = {r["qid"]: r for r in _csv.DictReader(csv_path.open(encoding="utf-8"))}
    assert rows["Q7478101"]["relevance"] == "non-topical"
    assert rows["Q134035659"]["relevance"] == "non-topical"
    # "crm" is a tag on the post; the acronym rule keeps the good link.
    assert rows["Q485643"]["relevance"] == "ok"
    assert counts["non-topical"] == 2 and counts["ok"] == 1
    assert set(_csv.DictReader(csv_path.open(encoding="utf-8")).fieldnames) == set(pop.AUDIT_COLUMNS)


def test_audit_csv_reports_missing_qids(tmp_path, monkeypatch):
    f = tmp_path / "post.md"
    f.write_text(POST, encoding="utf-8")
    monkeypatch.setattr(pop, "resolve_entities", lambda qids: {
        q: {"label": "", "description": "", "missing": True} for q in qids
    })
    csv_path = tmp_path / "audit.csv"
    counts = pop.audit_files([f], csv_path)
    assert counts["missing"] == 2


def test_audit_offline_yields_unresolved(tmp_path):
    f = tmp_path / "post.md"
    f.write_text(POST, encoding="utf-8")
    csv_path = tmp_path / "audit.csv"
    counts = pop.audit_files([f], csv_path, offline=True)
    assert counts["unresolved"] == 2


def test_replace_irrelevant_keeps_good_links_and_drops_bad(tmp_path, monkeypatch):
    f = tmp_path / "post.md"
    f.write_text(POST.replace(
        "  - https://www.wikidata.org/wiki/Q485643",
        "  - https://www.wikidata.org/wiki/Q485643\n  - https://www.wikidata.org/wiki/Q7478101",
    ), encoding="utf-8")
    monkeypatch.setattr(pop, "resolve_entities", lambda qids: {
        "Q134035659": {"label": "Built", "description": "family name", "missing": False},
        "Q485643": {"label": "customer relationship management",
                    "description": "approach to managing a company's interaction with customers",
                    "missing": False},
        "Q7478101": {"label": "we", "description": "first-person plural personal pronoun",
                     "missing": False},
    })
    monkeypatch.setattr(pop, "search_wikidata", lambda q, limit=3: [])
    monkeypatch.setattr(pop.time, "sleep", lambda *_: None)

    assert pop.process_file(f, replace_irrelevant=True) is True
    _fm, raw, _ = pop.parse_frontmatter(f.read_text(encoding="utf-8"))
    assert pop.extract_existing_seo_links(raw) == ["https://www.wikidata.org/wiki/Q485643"]
