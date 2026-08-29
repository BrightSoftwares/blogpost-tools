#!/usr/bin/env python3
"""
common/frontmatter_utils.py — shared Jekyll/Obsidian frontmatter parsing.

Named `frontmatter_utils`, not `frontmatter`, deliberately: this repo already
depends on the PyPI `python-frontmatter` package (importable as `frontmatter`)
in `internal-linking/requirements-test.txt` and `scripts/social/requirements.txt`
— reusing that import name here would silently shadow or be shadowed by that
package depending on `sys.path`/`sys.modules` state, which is exactly the kind
of footgun this extraction should not introduce.

Extracted 2026-08-28 (wave-6 of the 231.004 blog-automation campaign) after a
scan found frontmatter parsing independently reimplemented in ≥7 files across
≥5 tool folders (`retire-posts`, `jekyll-multi-language-tools`, `scripts`,
`scripts/bsgen`, `seo-links-enricher`) — two genuinely different techniques
(YAML-based via `yaml.safe_load` vs manual regex/line-split) solving the
identical problem, not coincidentally-named twins. See
`231.004.PRJ.solo.initiative.prj-automate-blog-post-creation.md`
(🆔 t213-commonlib-q) in `sergioafanou/my-obsidian` for the scan that found
this.

This module does NOT force every call site onto one signature — the original
functions genuinely differ (dict vs raw text, list support vs flat scalars,
tuple shapes) because their callers need different things (safe-YAML-to-dict
for read/write round-trips, raw-text splitting for surgical regex edits that
must not reformat the rest of the frontmatter block, a flat manual parser
for content — like Obsidian vault files — that can contain characters that
break `yaml.safe_load`, such as `[[wikilinks]]`). Instead it collects the
*duplicated implementations* into one place under distinct names, so a bug
fix (e.g. the missing YAMLError handling this extraction also fixes in
`parse_frontmatter_with_offsets`) lands once instead of N times.

Every function here is pure (no I/O) and takes/returns plain strings/dicts —
no dependency on any one tool folder's data model.

`yaml` is imported lazily inside the functions that need it, so importing
this module (and calling the manual/regex-only functions) never requires
PyYAML to be installed — several call sites (jekyll-multi-language-tools/)
don't currently depend on it and shouldn't gain a new runtime dependency as
a side effect of this refactor.
"""
from __future__ import annotations

import re

# Canonical frontmatter delimiter regex, DOTALL, tolerant of trailing
# whitespace after the opening/closing `---` (covers files edited by tools
# that leave a trailing space) — the union of the patterns previously
# duplicated across retire_posts.py / parse_bsgen_blocks.py.
FRONTMATTER_RE = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*\n", re.DOTALL)


# ---------------------------------------------------------------------------
# Family A — YAML-based dict extraction (safe: never raises on bad YAML)
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) from a Jekyll/Obsidian file's content.

    Safe against malformed YAML (e.g. bare `[[wikilinks]]` or stray `?`
    chars): returns `{}` for the frontmatter rather than raising.
    Equivalent to the former `retire-posts/src/retire_posts.py::parse_frontmatter`.
    """
    import yaml

    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}, content
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    if not isinstance(fm, dict):
        fm = {}
    body = content[m.end():]
    return fm, body


def parse_frontmatter_dict(content: str) -> dict:
    """Return just the frontmatter dict (no body), safe against bad YAML.

    Equivalent to the former `scripts/bsgen/parse_bsgen_blocks.py::extract_frontmatter`.
    """
    fm, _ = parse_frontmatter(content)
    return fm


def parse_frontmatter_with_offsets(content: str) -> tuple[dict, str, int, int]:
    """Return (frontmatter_dict, body, start, end).

    `start` is always `0` and `end` is the offset where the frontmatter
    block ends in `content` — preserved exactly as the original returned
    them (both values are vestigial: the sole caller in
    `seo-links-enricher/src/enrich_seo_links.py` discards them via `_, _`)
    so `content[start:end]` still reproduces the original frontmatter block
    for any future caller that wants it.

    Unlike the original `enrich_seo_links.py::extract_frontmatter`, this is
    now safe against malformed YAML (bug fix folded into the extraction:
    the original had no try/except and would crash the whole enrichment run
    on one bad post's frontmatter).
    """
    import yaml

    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}, content, -1, -1
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    if not isinstance(fm, dict):
        fm = {}
    start = 0
    end = m.end()
    return fm, content[end:], start, end


def write_frontmatter(fm: dict, body: str) -> str:
    """Serialize frontmatter dict + body back to a Jekyll/Obsidian file string.

    Equivalent to the former `retire-posts/src/retire_posts.py::write_frontmatter`
    and `seo-links-enricher/src/enrich_seo_links.py::rebuild_frontmatter`
    (byte-for-byte identical `yaml.dump` calls in both originals).
    """
    import yaml

    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return f"---\n{fm_str}---\n{body}"


# ---------------------------------------------------------------------------
# Family B — manual flat line-split dict (no YAML; tolerant of content that
# would break yaml.safe_load, e.g. Obsidian [[wikilinks]]; scalar values only)
# ---------------------------------------------------------------------------

_FLAT_FM_RE = re.compile(r'^---\n(.*?)\n---', re.DOTALL)
_FLAT_FM_WITH_BODY_RE = re.compile(r'^---\n(.*?)\n---\n(.*)$', re.DOTALL)


def _flat_parse_lines(raw_fm: str) -> dict[str, str]:
    fm: dict[str, str] = {}
    for line in raw_fm.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def parse_frontmatter_flat(content: str) -> dict[str, str]:
    """Extract frontmatter as a flat {str: str} dict via manual line-split
    (no `yaml.safe_load`) — safe against vault content that would break
    YAML parsing (e.g. `[[wikilinks]]`).

    Equivalent to the former
    `jekyll-multi-language-tools/scan_completed_subprojects.py::parse_frontmatter`.
    Note: strips both single and double surrounding quotes (the original
    only stripped double quotes) — a strict superset for values that never
    had surrounding single quotes, and matches the sibling implementation
    in `generate_redirects.py` below.
    """
    match = _FLAT_FM_RE.match(content)
    if not match:
        return {}
    return _flat_parse_lines(match.group(1))


def parse_frontmatter_flat_with_body(content: str) -> tuple[dict[str, str], str, str]:
    """Return (flat_frontmatter_dict, raw_frontmatter_str, remaining_content).

    Equivalent to the former
    `jekyll-multi-language-tools/generate_redirects.py::extract_frontmatter`.
    """
    match = _FLAT_FM_WITH_BODY_RE.match(content)
    if not match:
        return {}, '', content
    frontmatter_str, remaining_content = match.groups()
    return _flat_parse_lines(frontmatter_str), frontmatter_str, remaining_content


# ---------------------------------------------------------------------------
# Family C — manual mini-YAML parser with list support (no PyYAML dependency)
# ---------------------------------------------------------------------------

def parse_frontmatter_yaml_lite(content: str) -> tuple[dict | None, str, str]:
    """Return (frontmatter_dict, raw_frontmatter, body) or (None, '', content).

    A hand-rolled subset of YAML that additionally understands block lists
    (`key:\\n  - a\\n  - b`) and inline lists (`key: [a, b]`) — unlike
    `parse_frontmatter_flat` above, which only handles flat scalars.

    Equivalent to the former `scripts/seo_links_populator.py::parse_frontmatter`.
    """
    if not content.startswith("---"):
        return None, "", content

    second = content.index("---", 3)
    raw_fm = content[3:second].strip()
    body = content[second + 3:]

    fm: dict = {}
    current_key = ""
    current_list: list | None = None

    for line in raw_fm.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("- ") and current_list is not None:
            current_list.append(stripped[2:].strip())
            continue

        if current_list is not None:
            fm[current_key] = current_list
            current_list = None

        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            current_key = key
            if val == "":
                current_list = []
            elif val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
            else:
                fm[key] = val.strip("'\"")

    if current_list is not None:
        fm[current_key] = current_list

    return fm, raw_fm, body


# ---------------------------------------------------------------------------
# Family D — raw-text frontmatter/body split (no dict at all) for surgical
# regex edits that must preserve the rest of the frontmatter block verbatim
# ---------------------------------------------------------------------------

def extract_frontmatter_text(content: str) -> tuple[str, str]:
    """Split content into (frontmatter_text, body) without parsing values.

    Equivalent to the former, byte-for-byte-identical duplicate in
    `jekyll-multi-language-tools/detect_post_languages.py::extract_frontmatter`
    and `jekyll-multi-language-tools/translate_posts.py::extract_frontmatter`
    ("mirrors translate_posts.py" per the original docstring).
    """
    if not content.startswith("---"):
        return "", content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return "", content
    return parts[1], parts[2]


def get_frontmatter_value(fm_text: str, field_name: str) -> str:
    """Extract a single field's value from raw frontmatter text via regex.

    Equivalent to the former, byte-for-byte-identical duplicate in
    `jekyll-multi-language-tools/detect_post_languages.py::get_frontmatter_value`
    and `jekyll-multi-language-tools/translate_posts.py::get_frontmatter_value`.
    """
    match = re.search(
        rf"^{re.escape(field_name)}:\s*[\"']?(.+?)[\"']?\s*$", fm_text, re.MULTILINE
    )
    return match.group(1) if match else ""
