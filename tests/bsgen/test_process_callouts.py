"""Tests for bsgen callout processing — over-length content must NOT fail the pipeline.

Regression: an over-length callout `content` field used to raise a fatal validation
error, causing process_callouts.py to exit 2 and halt the whole bsgen pipeline
(corporate-website runs 29548218047 / 29561138919). Callouts render as flowing HTML
<p> that wraps naturally, so over-length content is a soft brevity nudge, not a
rendering failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "bsgen"))

import process_callouts  # noqa: E402
from parse_bsgen_blocks import (  # noqa: E402
    CALLOUT_CONTENT_SOFT_LIMIT,
    validate_callout,
)

POST_TEMPLATE = """---
title: Test post
---

Intro paragraph.

```bsgen:callout
type: {ctype}
content: "{content}"
```

Outro paragraph.
"""


def _write_post(tmp_path: Path, ctype: str, content: str) -> Path:
    post = tmp_path / "post.md"
    post.write_text(POST_TEMPLATE.format(ctype=ctype, content=content), encoding="utf-8")
    return post


def test_over_length_callout_is_not_a_validation_error() -> None:
    long_content = "x" * (CALLOUT_CONTENT_SOFT_LIMIT + 50)
    errors = validate_callout({"type": "WARNING", "content": long_content}, index=1)
    assert errors == [], "over-length callout content must be a soft warning, not a fatal error"


def test_over_length_stat_callout_is_not_a_validation_error() -> None:
    long_content = "y" * (CALLOUT_CONTENT_SOFT_LIMIT + 50)
    errors = validate_callout(
        {"type": "STAT", "content": long_content, "stat_value": "42", "stat_label": "x"},
        index=1,
    )
    assert errors == [], "over-length STAT content must be a soft warning, not a fatal error"


def test_over_length_callout_warns_on_stderr(capsys) -> None:
    long_content = "z" * (CALLOUT_CONTENT_SOFT_LIMIT + 50)
    validate_callout({"type": "WARNING", "content": long_content}, index=3)
    captured = capsys.readouterr()
    assert "WARNING: callout #3" in captured.err
    assert "rendering anyway" in captured.err


def test_missing_content_is_still_a_validation_error() -> None:
    errors = validate_callout({"type": "TIP"}, index=1)
    assert any("missing 'content'" in e for e in errors)


def test_process_renders_over_length_callout_and_exits_zero(tmp_path: Path) -> None:
    long_content = "This callout is deliberately far longer than the soft brevity " \
                   "guideline so that it would previously have failed the pipeline entirely."
    assert len(long_content) > CALLOUT_CONTENT_SOFT_LIMIT
    post = _write_post(tmp_path, "WARNING", long_content)

    # process() returns the process exit code: 0 = success, 2 = validation errors.
    assert process_callouts.process(post) == 0

    rendered = post.read_text(encoding="utf-8")
    assert "bs-callout bs-callout--warning" in rendered
    assert "bsgen:callout" not in rendered  # fence was replaced
    assert long_content in rendered  # content preserved in full, not truncated


def test_short_callout_still_renders(tmp_path: Path) -> None:
    post = _write_post(tmp_path, "TIP", "Short and sweet.")
    assert process_callouts.process(post) == 0
    assert "bs-callout bs-callout--tip" in post.read_text(encoding="utf-8")


def test_missing_content_callout_still_exits_two(tmp_path: Path) -> None:
    post = tmp_path / "post.md"
    post.write_text(
        "---\ntitle: t\n---\n\n```bsgen:callout\ntype: TIP\n```\n", encoding="utf-8"
    )
    # A genuinely invalid callout (missing content) must still be a hard error.
    assert process_callouts.process(post) == 2
