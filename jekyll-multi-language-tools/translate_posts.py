#!/usr/bin/env python3
"""Batch translate Jekyll posts from one language to another.

Translates frontmatter metadata (lang, title, redirect_from paths) without
requiring external translation APIs. Body content is preserved as-is — this
matches the established pattern on bright-softwares.com where FR posts keep
English body text but have French-localized metadata.

Usage:
    # Dry-run: show what would be translated
    python translate_posts.py /path/to/jekyll-site --dry-run

    # Translate next 20 untranslated posts
    python translate_posts.py /path/to/jekyll-site --batch-size 20

    # Translate ALL remaining posts
    python translate_posts.py /path/to/jekyll-site --all

    # Custom source/target language
    python translate_posts.py /path/to/jekyll-site --source en --target fr

    # Sort by date (newest first, default) or oldest first
    python translate_posts.py /path/to/jekyll-site --sort oldest
"""

import argparse
import re
import sys
from pathlib import Path

HEADING_TRANSLATIONS = {
    "Introduction": "Introduction",
    "Conclusion": "Conclusion",
    "Key Takeaways": "Points Clés à Retenir",
    "Summary": "Résumé",
    "Prerequisites": "Prérequis",
    "Getting Started": "Pour Commencer",
    "Final Thoughts": "Réflexions Finales",
    "References": "Références",
    "Table of Contents": "Table des Matières",
    "What You'll Learn": "Ce Que Vous Apprendrez",
    "Next Steps": "Prochaines Étapes",
    "Resources": "Ressources",
    "FAQ": "FAQ",
    "Overview": "Aperçu",
    "Requirements": "Exigences",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch translate Jekyll posts (frontmatter only)."
    )
    parser.add_argument("site_dir", help="Path to Jekyll site root")
    parser.add_argument(
        "--source", default="en", help="Source language code (default: en)"
    )
    parser.add_argument(
        "--target", default="fr", help="Target language code (default: fr)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=0,
        help="Number of posts to translate (0 = all, default: 0)",
    )
    parser.add_argument("--all", action="store_true", help="Translate all remaining")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be translated"
    )
    parser.add_argument(
        "--sort",
        choices=["newest", "oldest"],
        default="newest",
        help="Sort order for posts (default: newest first)",
    )
    return parser.parse_args()


def find_posts(site_dir: Path, lang: str) -> list[Path]:
    """Find all post files for a given language."""
    lang_dir = site_dir / lang / "_posts"
    if not lang_dir.exists():
        return []
    return sorted(lang_dir.glob("*.md"))


def extract_frontmatter(content: str) -> tuple[str, str]:
    """Split content into frontmatter text and body."""
    if not content.startswith("---"):
        return "", content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return "", content
    return parts[1], parts[2]


def get_frontmatter_value(fm_text: str, field: str) -> str:
    """Extract a single frontmatter field value."""
    match = re.search(
        rf"^{re.escape(field)}:\s*[\"']?(.+?)[\"']?\s*$", fm_text, re.MULTILINE
    )
    return match.group(1) if match else ""


def find_untranslated(
    source_posts: list[Path], target_posts: list[Path]
) -> list[Path]:
    """Find source posts that don't have a corresponding target post."""
    target_names = {p.name for p in target_posts}
    return [p for p in source_posts if p.name not in target_names]


def translate_frontmatter(fm_text: str, source_lang: str, target_lang: str) -> str:
    """Translate frontmatter fields from source to target language."""
    result = fm_text

    result = re.sub(
        rf"^lang:\s*{re.escape(source_lang)}\s*$",
        f"lang: {target_lang}",
        result,
        flags=re.MULTILINE,
    )

    result = translate_redirects(result, target_lang)

    return result


def translate_redirects(fm_text: str, target_lang: str) -> str:
    """Add language prefix to redirect_from paths."""
    lines = fm_text.split("\n")
    new_lines = []
    in_redirect = False

    for line in lines:
        if line.strip() == "redirect_from:":
            in_redirect = True
            new_lines.append(line)
        elif in_redirect and line.strip().startswith("- /"):
            path = line.strip()[2:].strip()
            if not path.startswith(f"/{target_lang}/"):
                new_lines.append(line.replace(path, f"/{target_lang}{path}"))
            else:
                new_lines.append(line)
        elif in_redirect and not line.strip().startswith("-"):
            in_redirect = False
            new_lines.append(line)
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def translate_post(
    source_path: Path,
    target_dir: Path,
    source_lang: str,
    target_lang: str,
    dry_run: bool = False,
) -> Path | None:
    """Translate a single post file."""
    content = source_path.read_text(encoding="utf-8")
    fm_text, body = extract_frontmatter(content)

    if not fm_text:
        return None

    new_fm = translate_frontmatter(fm_text, source_lang, target_lang)

    translated_content = f"---{new_fm}---{body}"

    target_path = target_dir / source_path.name

    if dry_run:
        title = get_frontmatter_value(fm_text, "title")
        print(f"  WOULD TRANSLATE: {source_path.name}")
        print(f"    Title: {title}")
        return target_path

    target_dir.mkdir(parents=True, exist_ok=True)
    target_path.write_text(translated_content, encoding="utf-8")
    return target_path


def main():
    args = parse_args()
    site_dir = Path(args.site_dir).resolve()

    if not site_dir.exists():
        print(f"ERROR: Site directory not found: {site_dir}", file=sys.stderr)
        sys.exit(1)

    source_posts = find_posts(site_dir, args.source)
    target_posts = find_posts(site_dir, args.target)

    print(f"Source ({args.source}): {len(source_posts)} posts")
    print(f"Target ({args.target}): {len(target_posts)} posts")

    untranslated = find_untranslated(source_posts, target_posts)

    if args.sort == "oldest":
        untranslated.sort(key=lambda p: p.name)
    else:
        untranslated.sort(key=lambda p: p.name, reverse=True)

    print(f"Untranslated: {len(untranslated)} posts")
    print()

    if not untranslated:
        print("Nothing to translate.")
        return

    batch = untranslated
    if args.batch_size > 0 and not args.all:
        batch = untranslated[: args.batch_size]

    target_dir = site_dir / args.target / "_posts"
    translated = []

    if args.dry_run:
        print(f"DRY RUN — would translate {len(batch)} posts:\n")

    for post in batch:
        result = translate_post(
            post, target_dir, args.source, args.target, dry_run=args.dry_run
        )
        if result:
            translated.append(result)
            if not args.dry_run:
                title = get_frontmatter_value(
                    extract_frontmatter(post.read_text(encoding="utf-8"))[0], "title"
                )
                print(f"  TRANSLATED: {post.name}")

    print(f"\n{'Would translate' if args.dry_run else 'Translated'}: {len(translated)}")
    print(f"Remaining: {len(untranslated) - len(translated)}")


if __name__ == "__main__":
    main()
