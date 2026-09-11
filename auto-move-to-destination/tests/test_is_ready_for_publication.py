"""Tests for is_ready_for_publication() / is_approved() in auto-move-to-destination.

Context (2026-09-10 incident + fix): the original is_ready_for_publication()
never checked frontmatter `publish_status`, so 25 of 59 non-approved posts
were force-published by BrightSoftwares/corporate-website's pipeline. A first
attempt made the publish_status check unconditional, but this action is a
SHARED GitHub Action consumed by 4 other production sites (ieatmyhealth.com,
keke.li, olympics-paris2024.com, foolywise.com) whose fully-auto-scheduled
pipelines never set publish_status -- an unconditional gate would have
silently and permanently halted publishing on all four.

The fix makes the gate opt-in via `require_approval` (env var
INPUT_REQUIRE_APPROVAL, default "false"). These tests pin down both halves:
  1. require_approval=true  -> gate blocks anything not publish_status=approved
                                (corporate-website's case)
  2. require_approval=false (or unset) -> behavior is IDENTICAL to before the
                                fix existed: publish_status is never consulted
                                (the 4 other sites' case -- this is the test
                                that matters most, since it is the one
                                preventing silent breakage of production
                                publishing on those sites)

main.py executes module-level code (including calling the function named by
INPUT_FUNCTION_TO_RUN) on import, and reads INPUT_REQUIRE_APPROVAL once at
import time. So each test loads a fresh copy of the module under a unique
name, with a harmless no-op move target and the desired env vars set first.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import uuid
from pathlib import Path

import pytest

MAIN_PY = Path(__file__).parent.parent / "src" / "main.py"


def _load_main_module(*, require_approval_env=None, tmp_path):
    """Import a fresh copy of main.py with controlled env vars.

    Uses an empty src/dst folder pair and a harmless function_to_run so the
    module-level `function_to_run()` call at the bottom of main.py is a
    no-op (nothing to scan, nothing to move).
    """
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    src_dir.mkdir(exist_ok=True)
    dst_dir.mkdir(exist_ok=True)

    env_backup = dict(os.environ)
    try:
        os.environ["INPUT_SRC_PATH"] = str(src_dir)
        os.environ["INPUT_DST_PATH"] = str(dst_dir)
        os.environ["INPUT_FUNCTION_TO_RUN"] = "move_iscontentenough_to_destination"
        os.environ["INPUT_DRY_RUN"] = "true"
        if require_approval_env is None:
            os.environ.pop("INPUT_REQUIRE_APPROVAL", None)
        else:
            os.environ["INPUT_REQUIRE_APPROVAL"] = require_approval_env

        module_name = f"automove_main_{uuid.uuid4().hex}"
        spec = importlib.util.spec_from_file_location(module_name, MAIN_PY)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        os.environ.clear()
        os.environ.update(env_backup)


def _make_post(module, *, publish_status=None, extra_fields=None, content_len=2000):
    """Build a python-frontmatter Post that passes the pre-existing checks
    (content length, pretified, image) so only is_approved()/publish_status
    is what varies between test cases.
    """
    import frontmatter

    fields = {
        "pretified": True,
        "image": "https://res.cloudinary.com/example/blog/foo.jpg",
    }
    if publish_status is not None:
        fields["publish_status"] = publish_status
    if extra_fields:
        fields.update(extra_fields)

    return frontmatter.Post("x" * content_len, **fields)


# --- require_approval=true (corporate-website's case): gate is enforced ----

def test_require_approval_true_blocks_missing_publish_status(tmp_path):
    module = _load_main_module(require_approval_env="true", tmp_path=tmp_path)
    post = _make_post(module, publish_status=None)
    assert module.is_ready_for_publication(post) is False


def test_require_approval_true_blocks_non_approved_status(tmp_path):
    module = _load_main_module(require_approval_env="true", tmp_path=tmp_path)
    for status in ["draft", "review", "changes_requested", "superseded"]:
        post = _make_post(module, publish_status=status)
        assert module.is_ready_for_publication(post) is False, (
            f"publish_status={status!r} should NOT be ready for publication"
        )


def test_require_approval_true_allows_approved_status(tmp_path):
    module = _load_main_module(require_approval_env="true", tmp_path=tmp_path)
    post = _make_post(module, publish_status="approved")
    assert module.is_ready_for_publication(post) is True


def test_require_approval_true_still_enforces_prior_checks(tmp_path):
    """approved status alone isn't enough -- content/pretified/image checks
    from before this fix must still apply."""
    module = _load_main_module(require_approval_env="true", tmp_path=tmp_path)
    post = _make_post(module, publish_status="approved", content_len=10)
    assert module.is_ready_for_publication(post) is False


# --- require_approval=false/unset (the 4 other sites' case): behavior is ---
# --- IDENTICAL to before the is_approved() gate existed at all ------------

@pytest.mark.parametrize("flag_value", [None, "false", "False", "", "0"])
def test_require_approval_off_ignores_publish_status_entirely(tmp_path, flag_value):
    """This is the test that matters most: it proves posts with no
    publish_status field at all (true of every post on ieatmyhealth.com,
    keke.li, olympics-paris2024.com, foolywise.com) are judged exactly as
    they were before the incident fix -- ready for publication based only
    on content/pretified/image, never blocked for missing/wrong
    publish_status.
    """
    module = _load_main_module(require_approval_env=flag_value, tmp_path=tmp_path)

    post_no_status = _make_post(module, publish_status=None)
    assert module.is_ready_for_publication(post_no_status) is True

    for status in ["draft", "review", "changes_requested", "superseded"]:
        post = _make_post(module, publish_status=status)
        assert module.is_ready_for_publication(post) is True, (
            f"with require_approval off, publish_status={status!r} must not "
            "block publication (matches pre-fix behavior)"
        )


def test_require_approval_off_still_enforces_prior_checks(tmp_path):
    """The pre-existing content/pretified/image checks are untouched by
    this fix regardless of the flag."""
    module = _load_main_module(require_approval_env="false", tmp_path=tmp_path)
    post = _make_post(module, content_len=10)
    assert module.is_ready_for_publication(post) is False


# --- is_approved() itself: fails closed -------------------------------

def test_is_approved_fails_closed_on_missing_field(tmp_path):
    module = _load_main_module(require_approval_env="true", tmp_path=tmp_path)
    post = _make_post(module, publish_status=None)
    assert module.is_approved(post) is False


def test_is_approved_true_only_for_exact_string_approved(tmp_path):
    module = _load_main_module(require_approval_env="true", tmp_path=tmp_path)
    assert module.is_approved(_make_post(module, publish_status="approved")) is True
    assert module.is_approved(_make_post(module, publish_status="Approved")) is False
    assert module.is_approved(_make_post(module, publish_status="approved ")) is False
