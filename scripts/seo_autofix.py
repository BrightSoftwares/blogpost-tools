#!/usr/bin/env python3
"""
seo_autofix.py — bounded, conservative auto-fixer for the unified SEO pipeline
(`reusable_seo-pipeline.yml`).

Scope (per `231.004.PRJ...` "Unified SEO Pipeline Spec", Open Question 3,
answered 2026-09-26 — feedback loop requirement):

  1. Missing `alt` attribute on `<img>` tags in the freshly built Jekyll site.
     If a reasonable alt text can be derived from the image filename, the
     source content file is patched and the change lands in a PR.
  2. Broken *internal* links (an `<a href="...">` pointing at a path that does
     not exist anywhere in this run's build output) where the broken path
     fuzzy-matches an existing page closely enough to be confident it is the
     same page under a new URL (e.g. after a rename/move). The source file is
     patched and the change lands in a PR.

Everything else (broken *external* links, GSC ranking/click issues, GSC index
coverage problems) is explicitly OUT of scope here — those are reported, never
auto-fixed, because acting on them needs judgment this script does not have.

Design decisions worth calling out (see reusable_seo-pipeline.yml's own
comments for the workflow-level rationale):

  - This module does **not** parse HTMLProofer's log text (undocumented,
    version-dependent format, and no historical sample was available to
    calibrate a parser against). Instead it does its own direct scan of the
    built HTML in `build_dir` for the two specific, narrow conditions above.
    This makes the contract stable and fully unit-testable without a live
    Jekyll build.
  - An *explicitly empty* `alt=""` is treated as intentional (a valid,
    accessibility-recommended way to mark a decorative image) and is never
    "fixed" — only a completely absent `alt` attribute is a candidate.
  - Every fix requires an *unambiguous* single match before it is applied
    (exactly one plausible source file, exactly one occurrence of the old
    value in that file). Anything else is reported under "needs follow-up"
    instead of guessed at — "when in doubt, don't auto-fix, just report."
  - Nothing here ever deletes content or touches files outside the given
    `content_dirs`.

Usage (invoked by reusable_seo-pipeline.yml as a step):

    python3 seo_autofix.py \
        --build-dir ./build \
        --content-dir _posts --content-dir _drafts --content-dir _pages \
        --site-url https://eagles-techs.com \
        --out-json /tmp/seo-pipeline/autofix.json
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Alt-text derivation
# ---------------------------------------------------------------------------

_SIZE_SUFFIX_RE = re.compile(
    r"[-_]?(\d{2,5}x\d{2,5}|@\dx|thumb(?:nail)?|scaled|small|medium|large|orig(?:inal)?|\d{2,5}w)$",
    re.IGNORECASE,
)
_DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[-_]")
_HEXY_RE = re.compile(r"^[0-9a-f]{6,}$", re.IGNORECASE)


def derive_alt_text(img_src: str) -> Optional[str]:
    """Best-effort, conservative alt text guess from an image filename.

    Returns None when no confident text can be derived (purely numeric /
    hash-like filenames, empty stems, etc.) — callers must treat None as
    "do not auto-fix this one, report it instead".
    """
    if not img_src:
        return None
    clean = img_src.split("?", 1)[0].split("#", 1)[0]
    basename = clean.rsplit("/", 1)[-1]
    if not basename or basename.startswith("."):
        # Dotfile-style name (e.g. ".png") -> pathlib would misread the
        # extension as the stem. There is no real basename to derive from.
        return None
    stem = basename.rsplit(".", 1)[0] if "." in basename else basename
    if not stem:
        return None

    prev = None
    while prev != stem:
        prev = stem
        stem = _SIZE_SUFFIX_RE.sub("", stem)
    stem = _DATE_PREFIX_RE.sub("", stem)
    stem = stem.strip(".")

    words = [w for w in re.split(r"[-_\s]+", stem) if w]
    # Drop tokens with no letters at all (stray punctuation, pure separators) —
    # a filename that reduces to nothing alphabetic gives no confident alt text.
    words = [w for w in words if re.search(r"[A-Za-z]", w)]
    if not words:
        return None

    joined = "".join(words)
    if _HEXY_RE.match(joined) or joined.isdigit():
        return None

    text = " ".join(w if w.isupper() and len(w) <= 5 else w.capitalize() for w in words)
    text = text.strip()
    if len(text) < 3:
        return None
    return text


# ---------------------------------------------------------------------------
# HTML scanning (stdlib only — no bs4 dependency for this hermetic script)
# ---------------------------------------------------------------------------

class _ImgAltScanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.missing_alt_srcs: list[str] = []

    def _handle(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "img":
            return
        attr_dict = dict(attrs)
        # Only a COMPLETELY ABSENT alt attribute is a candidate. An explicit
        # alt="" is a deliberate "decorative image" marker — never touch it.
        if "alt" not in attr_dict:
            src = attr_dict.get("src")
            if src:
                self.missing_alt_srcs.append(src)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self._handle(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self._handle(tag, attrs)


def find_missing_alt_images(html_text: str) -> list[str]:
    """Return `src` values of every `<img>` in html_text with NO alt attribute at all."""
    scanner = _ImgAltScanner()
    scanner.feed(html_text)
    return scanner.missing_alt_srcs


class _LinkScanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


_SKIP_HREF_PREFIXES = ("#", "mailto:", "tel:", "javascript:")


def find_internal_hrefs(html_text: str, site_url: str = "") -> list[str]:
    """Return hrefs from <a> tags that are relative or point at `site_url`'s own domain."""
    scanner = _LinkScanner()
    scanner.feed(html_text)
    domain = urlparse(site_url).netloc if site_url else ""
    internal = []
    for href in scanner.hrefs:
        if href.startswith(_SKIP_HREF_PREFIXES):
            continue
        parsed = urlparse(href)
        if parsed.netloc:
            if not domain or parsed.netloc != domain:
                continue  # external, or we can't tell -> never treat as internal
        internal.append(href)
    return internal


# ---------------------------------------------------------------------------
# Build-output <-> source-file mapping
# ---------------------------------------------------------------------------

def slug_from_build_path(build_html_path: Path, build_dir: Path) -> str:
    """Derive the Jekyll-style URL slug for a built HTML file, e.g.
    build/2026/09/26/my-post/index.html -> "my-post".
    """
    rel = build_html_path.relative_to(build_dir)
    parts = list(rel.parts)
    if not parts:
        return ""
    if parts[-1].lower() == "index.html":
        parts = parts[:-1]
    else:
        parts = parts[:-1] + [Path(parts[-1]).stem]
    return parts[-1] if parts else ""


def find_source_file_for_slug(slug: str, content_dirs: list[Path]) -> Optional[Path]:
    """Find exactly one content file whose slug matches. Returns None on zero
    or on more than one match — ambiguity is never guessed at.
    """
    if not slug:
        return None
    slug_lower = slug.lower()
    candidates: list[Path] = []
    for cdir in content_dirs:
        if not cdir.exists():
            continue
        for path in sorted(cdir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in (".md", ".markdown", ".html"):
                continue
            stem = path.stem.lower()
            stem_no_date = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
            if stem_no_date == slug_lower or stem == slug_lower:
                candidates.append(path)
    unique = list(dict.fromkeys(candidates))
    return unique[0] if len(unique) == 1 else None


def map_build_to_source(build_html_path: Path, build_dir: Path, content_dirs: list[Path]) -> Optional[Path]:
    slug = slug_from_build_path(build_html_path, build_dir)
    return find_source_file_for_slug(slug, content_dirs)


# ---------------------------------------------------------------------------
# Applying fixes to source files (each requires an unambiguous single match)
# ---------------------------------------------------------------------------

def apply_alt_fix(source_path: Path, img_src: str, alt_text: str) -> bool:
    text = source_path.read_text(encoding="utf-8")
    basename = Path(img_src.split("?", 1)[0]).name
    if not basename:
        return False
    escaped = re.escape(basename)

    # Markdown image syntax with an EMPTY alt: ![](...basename...)
    md_pattern = re.compile(r"!\[\]\(([^)]*" + escaped + r"[^)]*)\)")
    md_matches = list(md_pattern.finditer(text))

    # Raw <img> tag referencing basename with NO alt= attribute at all.
    img_pattern = re.compile(
        r"<img\b(?![^>]*\balt\s*=)[^>]*\bsrc\s*=\s*[\"'][^\"']*" + escaped + r"[^\"']*[\"'][^>]*>",
        re.IGNORECASE,
    )
    img_matches = list(img_pattern.finditer(text))

    if len(md_matches) + len(img_matches) != 1:
        return False  # none, or ambiguous -> do not guess

    if md_matches:
        m = md_matches[0]
        new_fragment = f"![{alt_text}]({m.group(1)})"
    else:
        m = img_matches[0]
        original = m.group(0)
        new_fragment = original[:4] + f' alt="{alt_text}"' + original[4:]

    text = text[: m.start()] + new_fragment + text[m.end():]
    source_path.write_text(text, encoding="utf-8")
    return True


def apply_link_fix(source_path: Path, old_href: str, new_href: str) -> bool:
    text = source_path.read_text(encoding="utf-8")
    if text.count(old_href) != 1:
        return False  # zero or ambiguous -> do not guess
    text = text.replace(old_href, new_href, 1)
    source_path.write_text(text, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Build-output helpers for the internal-link check
# ---------------------------------------------------------------------------

def _href_target_path(href: str, build_dir: Path) -> Path:
    path = urlparse(href).path.lstrip("/")
    return build_dir / path


def target_exists_in_build(href: str, build_dir: Path) -> bool:
    path = urlparse(href).path
    if not path or path == "/":
        return True  # homepage / fragment-only link, nothing to check
    p = _href_target_path(href, build_dir)
    if p.exists() and p.is_file():
        return True
    if (p / "index.html").exists():
        return True
    if Path(str(p) + ".html").exists():
        return True
    if Path(str(p) + "/index.html").exists():
        return True
    return False


def all_page_urls(build_dir: Path) -> list[str]:
    urls = []
    for html_file in sorted(build_dir.rglob("*.html")):
        rel = html_file.relative_to(build_dir).as_posix()
        if rel == "index.html":
            rel = ""
        elif rel.endswith("/index.html"):
            rel = rel[: -len("index.html")]
        urls.append("/" + rel)
    return urls


def fuzzy_match_internal_link(broken_href: str, candidate_urls: list[str], cutoff: float = 0.72) -> Optional[str]:
    path = urlparse(broken_href).path or broken_href
    matches = difflib.get_close_matches(path, candidate_urls, n=1, cutoff=cutoff)
    if not matches or matches[0] == path:
        return None
    return matches[0]


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

@dataclass
class AutofixResult:
    alt_fixed: list[dict] = field(default_factory=list)
    alt_skipped: list[dict] = field(default_factory=list)
    link_fixed: list[dict] = field(default_factory=list)
    link_skipped: list[dict] = field(default_factory=list)
    changed_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "alt_fixed": self.alt_fixed,
            "alt_skipped": self.alt_skipped,
            "link_fixed": self.link_fixed,
            "link_skipped": self.link_skipped,
            "changed_files": self.changed_files,
        }


def run_autofix(build_dir: Path, content_dirs: list[Path], site_url: str = "") -> AutofixResult:
    result = AutofixResult()
    changed: set[str] = set()

    html_files = sorted(build_dir.rglob("*.html")) if build_dir.exists() else []

    # --- Missing alt text ---------------------------------------------------
    for html_file in html_files:
        text = html_file.read_text(encoding="utf-8", errors="ignore")
        for img_src in find_missing_alt_images(text):
            rel_page = str(html_file.relative_to(build_dir))
            entry = {"page": rel_page, "img_src": img_src}
            alt_text = derive_alt_text(img_src)
            if alt_text is None:
                entry["reason"] = "could not derive a confident alt text from the filename"
                result.alt_skipped.append(entry)
                continue
            source = map_build_to_source(html_file, build_dir, content_dirs)
            if source is None:
                entry["reason"] = "could not map this build page to a unique source content file"
                result.alt_skipped.append(entry)
                continue
            entry["source"] = str(source)
            entry["alt_text"] = alt_text
            if apply_alt_fix(source, img_src, alt_text):
                result.alt_fixed.append(entry)
                changed.add(str(source))
            else:
                entry["reason"] = "no single unambiguous match for this image in the source file"
                result.alt_skipped.append(entry)

    # --- Broken internal links ----------------------------------------------
    candidate_urls = all_page_urls(build_dir) if build_dir.exists() else []
    for html_file in html_files:
        text = html_file.read_text(encoding="utf-8", errors="ignore")
        for href in find_internal_hrefs(text, site_url):
            if target_exists_in_build(href, build_dir):
                continue
            rel_page = str(html_file.relative_to(build_dir))
            entry = {"page": rel_page, "href": href}
            suggestion = fuzzy_match_internal_link(href, candidate_urls)
            if suggestion is None:
                entry["reason"] = "no confident fuzzy match found among this run's existing pages"
                result.link_skipped.append(entry)
                continue
            source = map_build_to_source(html_file, build_dir, content_dirs)
            if source is None:
                entry["reason"] = "could not map this build page to a unique source content file"
                result.link_skipped.append(entry)
                continue
            entry["source"] = str(source)
            entry["suggested_href"] = suggestion
            if apply_link_fix(source, href, suggestion):
                result.link_fixed.append(entry)
                changed.add(str(source))
            else:
                entry["reason"] = "old href did not appear exactly once in the source file"
                result.link_skipped.append(entry)

    result.changed_files = sorted(changed)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--content-dir", action="append", default=[], type=Path,
                         help="A content directory to search for source files (repeatable).")
    parser.add_argument("--site-url", default="")
    parser.add_argument("--out-json", required=True, type=Path)
    args = parser.parse_args()

    content_dirs = args.content_dir or [Path("_posts"), Path("_drafts"), Path("_pages")]
    result = run_autofix(args.build_dir, content_dirs, args.site_url)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Alt-text fixed: {len(result.alt_fixed)} | skipped: {len(result.alt_skipped)}")
    print(f"Internal links fixed: {len(result.link_fixed)} | skipped: {len(result.link_skipped)}")
    print(f"Changed source files: {len(result.changed_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
