#!/usr/bin/env python3
"""
Readability Checker - GitHub Actions Ready

Scores Jekyll blog posts for readability using the Flesch Reading Ease and
Flesch-Kincaid Grade Level formulas (Flesch, 1948; Kincaid et al., 1975) —
the two most widely used, unit-testable readability metrics, implemented
from scratch here (no new external dependency; the repo already depends on
`python-frontmatter` for frontmatter parsing, reused below).

Never modifies the posts it scans. Follows the `seo-analysis` action's
output convention: timestamped + "latest" JSON, per-post CSV, a
human-readable summary_report_*.txt, GITHUB_OUTPUT keys, and an exit code
that only fails the build for a genuinely critical condition (never for
ordinary "below target" findings unless fail_on_below_min is set).
"""

import csv
import glob as globmod
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import frontmatter as fm_lib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Markdown/frontmatter stripping — pure functions, unit-tested in isolation.
# ---------------------------------------------------------------------------

# Fenced code blocks (```lang\n...\n```) are stripped ENTIRELY (not just the
# fences) — code is not prose and would otherwise skew word/sentence counts
# with identifiers, punctuation-as-syntax, and long unbroken tokens.
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
# Markdown/wikilink links: keep the visible text, drop the target.
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_WIKILINK_RE = re.compile(r"\[\[([^\]|#]*)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s*", re.MULTILINE)
_BLOCKQUOTE_RE = re.compile(r"^\s{0,3}>\s?", re.MULTILINE)
_LIST_MARKER_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+", re.MULTILINE)
_HR_RE = re.compile(r"^\s{0,3}(?:-{3,}|\*{3,}|_{3,})\s*$", re.MULTILINE)
_BOLD_ITALIC_RE = re.compile(r"(\*{1,3}|_{1,3})(\S.*?\S|\S)\1")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_TABLE_PIPE_RE = re.compile(r"\|")
_MULTI_WS_RE = re.compile(r"[ \t]+")
_MULTI_NL_RE = re.compile(r"\n{2,}")


def strip_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Return (frontmatter_dict, body) using python-frontmatter.

    Safe against malformed/absent frontmatter: python-frontmatter returns an
    empty metadata dict and the full content as the body when there is no
    `---` delimited block.
    """
    post = fm_lib.loads(content)
    return dict(post.metadata), post.content


def strip_markdown(text: str) -> str:
    """Strip Jekyll/Markdown syntax so word/sentence/syllable counts reflect
    prose only, not markup. Order matters: code fences before inline code,
    images before generic links (an image is `![alt](url)`, a subset of the
    link pattern), wikilinks before plain links.
    """
    text = _CODE_FENCE_RE.sub(" ", text)
    text = _INLINE_CODE_RE.sub(" ", text)
    text = _IMAGE_RE.sub(" ", text)
    text = _WIKILINK_RE.sub(lambda m: m.group(2) or m.group(1), text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _HTML_TAG_RE.sub(" ", text)
    text = _HEADING_RE.sub("", text)
    text = _BLOCKQUOTE_RE.sub("", text)
    text = _HR_RE.sub(" ", text)
    text = _LIST_MARKER_RE.sub("", text)
    text = _BOLD_ITALIC_RE.sub(r"\2", text)
    text = _TABLE_PIPE_RE.sub(" ", text)
    text = _MULTI_WS_RE.sub(" ", text)
    text = _MULTI_NL_RE.sub("\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Readability scoring — Flesch Reading Ease + Flesch-Kincaid Grade Level.
# ---------------------------------------------------------------------------

_SENTENCE_SPLIT_RE = re.compile(r"[.!?]+(?:\s+|\n|$)")
_WORD_RE = re.compile(r"[A-Za-z']+")


def count_syllables(word: str) -> int:
    """Approximate syllable count via vowel-group heuristic (standard
    technique used by textstat-style tools; not phonetically perfect but
    stable and dependency-free).
    """
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_was_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def count_sentences(text: str) -> int:
    sentences = [s for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]
    # A body with no terminal punctuation at all is still one "sentence".
    return max(len(sentences), 1 if text.strip() else 0)


def count_words(text: str) -> List[str]:
    return _WORD_RE.findall(text)


def flesch_reading_ease(text: str) -> Optional[float]:
    """206.835 - 1.015*(words/sentences) - 84.6*(syllables/words). Higher is
    easier (100 = very easy, 0 = very difficult). Returns None for text with
    no words (nothing to score).
    """
    words = count_words(text)
    if not words:
        return None
    sentences = count_sentences(text)
    syllables = sum(count_syllables(w) for w in words)
    score = 206.835 - 1.015 * (len(words) / sentences) - 84.6 * (syllables / len(words))
    return round(score, 2)


def flesch_kincaid_grade(text: str) -> Optional[float]:
    """0.39*(words/sentences) + 11.8*(syllables/words) - 15.59. Returns the
    approximate US school grade level required to understand the text.
    """
    words = count_words(text)
    if not words:
        return None
    sentences = count_sentences(text)
    syllables = sum(count_syllables(w) for w in words)
    grade = 0.39 * (len(words) / sentences) + 11.8 * (syllables / len(words)) - 15.59
    return round(grade, 2)


# ---------------------------------------------------------------------------
# Per-post analysis.
# ---------------------------------------------------------------------------

def analyze_post(path: Path, min_score: float, target_grade_level: float) -> Optional[Dict[str, Any]]:
    """Return a result dict for one post, or None if the post has no
    scoreable prose (empty body after stripping) — logged as a warning, not
    an error; an empty post is not a fatal condition for the batch.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning("Skipping non-UTF8 file: %s", path)
        return None
    except OSError as e:
        logger.warning("Could not read %s: %s", path, e)
        return None

    fm, body = strip_frontmatter(raw)
    prose = strip_markdown(body)
    words = count_words(prose)

    if not words:
        logger.warning("Skipping %s: no scoreable prose after stripping frontmatter/markdown.", path)
        return None

    ease = flesch_reading_ease(prose)
    grade = flesch_kincaid_grade(prose)
    sentences = count_sentences(prose)

    return {
        "file": str(path),
        "title": fm.get("title", path.stem),
        "word_count": len(words),
        "sentence_count": sentences,
        "flesch_reading_ease": ease,
        "flesch_kincaid_grade": grade,
        "below_min_score": ease is not None and ease < min_score,
        "above_target_grade": grade is not None and grade > target_grade_level,
    }


def find_posts(posts_glob: str) -> List[Path]:
    # glob.glob with recursive=True supports the `**` segment used by the
    # default pattern (_posts/**/*.md); relative patterns resolve against
    # the current working directory (the checked-out repo root in CI), so a
    # `../` segment could only ever escape to the runner's own filesystem,
    # not to another repo's secrets — still resolved+deduped defensively.
    matches = globmod.glob(posts_glob, recursive=True)
    paths = sorted({Path(m).resolve() for m in matches if Path(m).is_file()})
    return paths


# ---------------------------------------------------------------------------
# Reporting — mirrors seo-analysis's output_dir convention.
# ---------------------------------------------------------------------------

def save_results(results: List[Dict[str, Any]], skipped: List[str], output_dir: Path) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    scores = [r["flesch_reading_ease"] for r in results if r["flesch_reading_ease"] is not None]
    average_score = round(sum(scores) / len(scores), 2) if scores else None
    below_threshold = sum(1 for r in results if r["below_min_score"])

    payload = {
        "metadata": {
            "analysis_timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "posts_analyzed": len(results),
            "posts_skipped": len(skipped),
        },
        "statistics": {
            "average_flesch_reading_ease": average_score,
            "posts_below_min_score": below_threshold,
        },
        "posts": results,
        "skipped": skipped,
    }

    json_file = output_dir / f"readability_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    latest_json = output_dir / "readability_latest.json"
    with open(latest_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    csv_file = output_dir / f"readability_{timestamp}.csv"
    if results:
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
    else:
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("")

    summary_file = output_dir / f"summary_report_{timestamp}.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("READABILITY CHECKER SUMMARY\n")
        f.write("=" * 70 + "\n")
        f.write(f"Posts analyzed: {len(results)}\n")
        f.write(f"Posts skipped (empty/unreadable): {len(skipped)}\n")
        f.write(f"Average Flesch Reading Ease: {average_score}\n")
        f.write(f"Posts below min score: {below_threshold}\n\n")
        for r in sorted(results, key=lambda x: (x["flesch_reading_ease"] is None, x["flesch_reading_ease"] or 0)):
            flag = " [BELOW MIN]" if r["below_min_score"] else ""
            flag += " [DENSE]" if r["above_target_grade"] else ""
            f.write(f"- {r['file']}: ease={r['flesch_reading_ease']} grade={r['flesch_kincaid_grade']}{flag}\n")
        if skipped:
            f.write("\nSkipped:\n")
            for s in skipped:
                f.write(f"- {s}\n")
    logger.info("Saved summary report: %s", summary_file)

    return {
        "latest_json": latest_json,
        "average_score": average_score,
        "below_threshold": below_threshold,
    }


def main() -> int:
    posts_glob = os.getenv("INPUT_POSTS_GLOB", "_posts/**/*.md")
    min_score = float(os.getenv("INPUT_MIN_SCORE", "60"))
    target_grade_level = float(os.getenv("INPUT_TARGET_GRADE_LEVEL", "10"))
    fail_on_below_min = os.getenv("INPUT_FAIL_ON_BELOW_MIN", "false").lower() == "true"
    output_dir = Path(os.getenv("INPUT_OUTPUT_DIR", "_seo/readability-checker/output"))

    logger.info("=" * 70)
    logger.info("READABILITY CHECKER CONFIGURATION")
    logger.info("=" * 70)
    logger.info("Posts glob: %s", posts_glob)
    logger.info("Min score: %s", min_score)
    logger.info("Target grade level: %s", target_grade_level)
    logger.info("Fail on below min: %s", fail_on_below_min)
    logger.info("Output dir: %s", output_dir)
    logger.info("=" * 70)

    posts = find_posts(posts_glob)
    if not posts:
        logger.warning("No posts matched glob %s — nothing to analyze.", posts_glob)

    results: List[Dict[str, Any]] = []
    skipped: List[str] = []
    for path in posts:
        try:
            result = analyze_post(path, min_score, target_grade_level)
        except Exception as e:  # noqa: BLE001 - one bad post must not crash the batch
            logger.warning("Error analyzing %s: %s", path, e)
            skipped.append(str(path))
            continue
        if result is None:
            skipped.append(str(path))
        else:
            results.append(result)

    stats = save_results(results, skipped, output_dir)

    print("\n" + "=" * 70)
    print("READABILITY CHECK COMPLETE")
    print("=" * 70)
    print(f"Posts analyzed: {len(results)}")
    print(f"Posts skipped: {len(skipped)}")
    print(f"Average Flesch Reading Ease: {stats['average_score']}")
    print(f"Posts below min score ({min_score}): {stats['below_threshold']}")
    print("=" * 70)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as fh:
            print(f"report_file={stats['latest_json']}", file=fh)
            print(f"posts_analyzed={len(results)}", file=fh)
            print(f"posts_below_threshold={stats['below_threshold']}", file=fh)
            print(f"average_score={stats['average_score']}", file=fh)

    if fail_on_below_min and stats["below_threshold"] > 0:
        logger.warning("Critical: %s post(s) below min_score with fail_on_below_min=true", stats["below_threshold"])
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
