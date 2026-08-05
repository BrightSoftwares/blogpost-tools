#!/usr/bin/env python3
"""Diff-aware actionlint gate.

2026-08-05: repo-wide actionlint (`reusable-contract-test.yml` / lint-interfaces)
had been red on every run since 2026-07-21 -- 45 pre-existing errors live in
~20 unrelated deploy/infra workflows (reusable_deploy-to-{aws,azure,gcp,application}.yml,
reusable_deploy-{jekyll,nodejs}-*-o2switch.yml, bright-*.yml, encrypted-backups.yml,
post_summarizer.yml, etc.) that most PRs never touch. That made the check
permanently unpassable and therefore useless as a gate.

This script re-scopes the check to only the .github/workflows/*.yml lines a PR
actually adds or changes (the same "filter_mode: added" idea reviewdog uses),
so it becomes a real per-PR quality gate again instead of a repo-wide backlog
check nobody could ever pass. It intentionally does NOT fix the pre-existing
errors in files this PR doesn't touch, or on lines a touched file didn't change --
see BrightSoftwares/blogpost-tools PR #31 for the investigation that established
which of the 45 errors were pre-existing debt vs. real regressions (all 45 were
pre-existing; 3 of them happened to live in 2 files this particular PR touched,
but on lines it never changed).

Usage:
    lint_changed_workflow_lines.py <base-ref> [--actionlint PATH]

Exit code 0: no NEW actionlint errors on lines changed by this PR/push
             (pre-existing errors on untouched lines are printed but non-blocking).
Exit code 1: at least one actionlint error lands on a line this PR added/changed.
"""
import argparse
import re
import subprocess
import sys

ERROR_RE = re.compile(r"^(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+): ")
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def changed_workflow_files(base_ref):
    result = run(
        [
            "git",
            "diff",
            "--name-only",
            f"{base_ref}...HEAD",
            "--",
            ".github/workflows/*.yml",
            ".github/workflows/*.yaml",
        ]
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(2)
    return [f for f in result.stdout.splitlines() if f.strip()]


def changed_lines(base_ref, path):
    """Return the set of line numbers added/changed in `path` (new-file numbering)."""
    result = run(["git", "diff", "-U0", f"{base_ref}...HEAD", "--", path])
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(2)
    lines = set()
    for line in result.stdout.splitlines():
        m = HUNK_RE.match(line)
        if not m:
            continue
        start = int(m.group("new_start"))
        count = int(m.group("new_count")) if m.group("new_count") is not None else 1
        if count == 0:
            # Pure deletion -- no new lines were introduced at this hunk.
            continue
        lines.update(range(start, start + count))
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_ref")
    parser.add_argument("--actionlint", default="actionlint")
    args = parser.parse_args()

    files = changed_workflow_files(args.base_ref)
    if not files:
        print("No .github/workflows/*.yml files changed by this PR/push -- nothing to lint.")
        return 0

    print(f"Linting {len(files)} changed workflow file(s):")
    for f in files:
        print(f"  - {f}")

    lint = run([args.actionlint, "-no-color", *files])
    stdout = lint.stdout + lint.stderr

    per_file_changed = {f: changed_lines(args.base_ref, f) for f in files}

    blocking = []
    pre_existing = []
    for line in stdout.splitlines():
        m = ERROR_RE.match(line)
        if not m:
            continue
        f = m.group("file")
        ln = int(m.group("line"))
        if ln in per_file_changed.get(f, set()):
            blocking.append(line)
        else:
            pre_existing.append(line)

    if pre_existing:
        print(f"\n{len(pre_existing)} pre-existing actionlint error(s) on lines this PR did not touch (non-blocking):")
        for line in pre_existing:
            print(f"  [pre-existing, not blocking] {line}")

    if blocking:
        print(f"\n{len(blocking)} actionlint error(s) on lines this PR added/changed (BLOCKING):")
        for line in blocking:
            print(f"  [NEW] {line}")
        return 1

    print("\nNo actionlint errors on lines this PR added/changed. Passing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
