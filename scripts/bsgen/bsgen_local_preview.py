#!/usr/bin/env python3
"""
bsgen_local_preview.py

Runs the full bsgen block-processing chain (callouts -> assets -> related ->
social) against a COPY of a blog post, entirely locally: no Cloudinary, no
live Smart Assets Manager API, no network calls, nothing committed anywhere.
Built to let a human eyeball the generated placeholder images and the
transformed markdown before trusting the real pipeline (BSGEN_SAM_API_URL is
never set here, so process_assets.py always runs in its local placeholder
fallback mode).

Usage:
    python bsgen_local_preview.py <post_file> [--posts-dir DIR] [--site-url URL] [--out DIR] [--serve]

    <post_file>   Path to the source post (never modified in place — a copy
                  is made into the output directory and processed there).

Options:
    --posts-dir   Directory of published posts for the related-links step to
                  search against. Defaults to the post's own grandparent
                  '_posts' directory if one is found on the path, else skips
                  the related-links step with a warning.
    --site-url    Base site URL passed to process_related.py / process_assets.py
                  for link generation. Default: http://localhost:4000 (a
                  harmless placeholder — no request is ever made to it).
    --out         Output directory for the processed copy + generated assets.
                  Default: ./bsgen_preview_output/<post-stem>/ (gitignored,
                  see the .gitignore entry this repo already carries — check
                  before committing anything from here).
    --serve       After processing, start a throwaway local HTTP server
                  (python -m http.server) rooted at --out so you can open
                  http://localhost:8899/<post-stem>.html style links in a
                  browser. Ctrl-C to stop; nothing persists.

Exit codes:
    0 = all steps ran (individual step warnings are printed, not fatal)
    1 = post file not found, or a step hit a fatal (exit-1) error
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def run_step(name: str, cmd: list[str]) -> int:
    print(f"\n=== {name} ===")
    print(f"$ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode == 1:
        print(f"FATAL: {name} exited 1 — stopping preview.", file=sys.stderr)
    elif result.returncode == 2:
        print(f"WARNING: {name} exited 2 (partial success) — continuing.")
    else:
        print(f"OK: {name} exited 0.")
    return result.returncode


def guess_posts_dir(post_path: Path) -> Path | None:
    for parent in post_path.parents:
        candidate = parent / "_posts"
        if candidate.is_dir():
            return candidate
        if parent.name in ("_drafts", "_posts"):
            sibling = parent.parent / "_posts"
            if sibling.is_dir():
                return sibling
    return None


def render_markdown_to_html(md_path: Path, html_path: Path) -> None:
    """Minimal, dependency-free markdown-ish render — just enough to eyeball
    images/headings/callouts in a browser. Not a real Jekyll build."""
    text = md_path.read_text(encoding="utf-8")
    # Strip frontmatter for display purposes
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    lines = text.splitlines()
    html_lines = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        f"<title>bsgen local preview — {md_path.name}</title>",
        "<style>body{font-family:system-ui,sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem;line-height:1.6}",
        "img{max-width:100%;height:auto;border:1px solid #ddd;display:block;margin:1rem 0}",
        "pre{background:#f5f5f5;padding:1rem;overflow-x:auto;white-space:pre-wrap}</style></head><body>",
        f"<p><em>This is a raw markdown-to-HTML dump for visual debugging only — not a real Jekyll render. Source: {md_path.name}</em></p><hr>",
    ]
    for line in lines:
        if line.startswith("!["):
            html_lines.append(f"<pre>{line}</pre>")
        elif line.startswith("#"):
            level = min(len(line) - len(line.lstrip("#")), 6)
            html_lines.append(f"<h{level}>{line.lstrip('#').strip()}</h{level}>")
        elif line.strip():
            html_lines.append(f"<p>{line}</p>")
    html_lines.append("</body></html>")
    html_path.write_text("\n".join(html_lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("post_file")
    parser.add_argument("--posts-dir", default=None)
    parser.add_argument("--site-url", default="http://localhost:4000")
    parser.add_argument("--out", default=None)
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()

    post_path = Path(args.post_file).resolve()
    if not post_path.exists():
        print(f"ERROR: post file not found: {post_path}", file=sys.stderr)
        return 1

    out_dir = Path(args.out) if args.out else Path.cwd() / "bsgen_preview_output" / post_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    working_copy = out_dir / post_path.name
    shutil.copy2(post_path, working_copy)
    print(f"Working on a copy: {working_copy}\n(original {post_path} is never touched)")

    rc = run_step("1/4 process_callouts.py", [sys.executable, str(SCRIPT_DIR / "process_callouts.py"), str(working_copy)])
    if rc == 1:
        return 1

    # BSGEN_SAM_API_URL / KEY intentionally NOT set below — forces the
    # placeholder local-SVG fallback path in process_assets.py, so this
    # never calls SAM or Cloudinary.
    rc = run_step(
        "2/4 process_assets.py (local placeholder mode — no SAM, no Cloudinary)",
        [sys.executable, str(SCRIPT_DIR / "process_assets.py"), str(working_copy), str(assets_dir), "--site-url", args.site_url],
    )
    if rc == 1:
        return 1

    posts_dir = Path(args.posts_dir).resolve() if args.posts_dir else guess_posts_dir(post_path)
    if posts_dir and posts_dir.is_dir():
        rc = run_step(
            "3/4 process_related.py",
            [sys.executable, str(SCRIPT_DIR / "process_related.py"), str(working_copy), str(posts_dir), args.site_url],
        )
        if rc == 1:
            return 1
    else:
        print("\n=== 3/4 process_related.py — SKIPPED (no posts dir found; pass --posts-dir) ===")

    rc = run_step("4/4 process_social.py", [sys.executable, str(SCRIPT_DIR / "process_social.py"), str(working_copy), str(out_dir / "social")])
    if rc == 1:
        return 1

    html_path = out_dir / f"{post_path.stem}.html"
    render_markdown_to_html(working_copy, html_path)

    print(f"\n{'=' * 60}")
    print(f"Preview ready in: {out_dir}")
    print(f"  Processed markdown : {working_copy}")
    print(f"  Quick HTML dump    : {html_path}")
    print(f"  Generated assets   : {assets_dir}")
    print("Nothing here was committed or uploaded anywhere. Delete the whole")
    print(f"'{out_dir}' folder whenever you're done — it's throwaway.")
    print(f"{'=' * 60}")

    if args.serve:
        print(f"\nServing {out_dir} at http://localhost:8899/{html_path.name} — Ctrl-C to stop.")
        subprocess.run([sys.executable, "-m", "http.server", "8899", "--directory", str(out_dir)])

    return 0


if __name__ == "__main__":
    sys.exit(main())
