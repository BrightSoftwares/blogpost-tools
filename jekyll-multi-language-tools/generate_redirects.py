#!/usr/bin/env python3
"""
Generate 301 Redirects Script

Adds jekyll-redirect-from frontmatter to posts to redirect from old
date-based URLs to new SEO-friendly URLs.

Old format: /en/2026/01/20/welcome-to-beacon-harbor/
New format: /en/wisdom/announcements/welcome-to-beacon-harbor/

Usage:
    python generate_redirects.py --posts-dir _posts --dry-run
    python generate_redirects.py --posts-dir _posts (apply changes)
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def parse_post_filename(filename: str) -> Optional[Dict[str, str]]:
    """Extract date and slug from Jekyll post filename."""
    # Format: YYYY-MM-DD-slug.md
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)\.md$', filename)
    if not match:
        return None

    year, month, day, slug = match.groups()
    return {
        'year': year,
        'month': month,
        'day': day,
        'slug': slug
    }


def extract_frontmatter(content: str) -> tuple[Dict[str, str], str, str]:
    """Extract and parse frontmatter from post content."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return {}, '', content

    frontmatter_str, remaining_content = match.groups()
    frontmatter = {}

    for line in frontmatter_str.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter, frontmatter_str, remaining_content


def generate_old_url(lang: str, year: str, month: str, day: str, slug: str) -> str:
    """Generate old date-based URL format."""
    return f"/{lang}/{year}/{month}/{day}/{slug}/"


def generate_redirect_from_list(frontmatter: Dict[str, str], file_info: Dict[str, str]) -> List[str]:
    """Generate list of old URLs to redirect from."""
    lang = frontmatter.get('lang', 'en')
    year = file_info['year']
    month = file_info['month']
    day = file_info['day']
    slug = file_info['slug']

    old_url = generate_old_url(lang, year, month, day, slug)

    # Check if redirect_from already exists
    existing_redirects = frontmatter.get('redirect_from', '')

    if existing_redirects:
        # Parse existing redirects (could be string or list)
        if existing_redirects.startswith('['):
            # Already a list format
            return None  # Don't modify
        else:
            # Single redirect
            if old_url in existing_redirects:
                return None  # Already has this redirect
            else:
                return [existing_redirects, old_url]
    else:
        return [old_url]


def update_post_with_redirects(file_path: Path, redirects: List[str], dry_run: bool = False) -> bool:
    """Add redirect_from to post frontmatter."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter, frontmatter_str, remaining_content = extract_frontmatter(content)

    if not frontmatter:
        print(f"   ⚠️  No frontmatter found")
        return False

    # Build new frontmatter with redirect_from
    redirect_lines = '\nredirect_from:\n'
    for redirect in redirects:
        redirect_lines += f'  - {redirect}\n'

    # Insert redirect_from after title or at end of frontmatter
    lines = frontmatter_str.split('\n')
    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)
        if line.startswith('title:') and not inserted:
            # Insert after title
            for redirect in redirects:
                new_lines.append(f'redirect_from:')
                new_lines.append(f'  - {redirect}')
                break
            inserted = True

    if not inserted:
        # Insert at end
        for redirect in redirects:
            new_lines.append(f'redirect_from:')
            new_lines.append(f'  - {redirect}')
            break

    new_frontmatter = '\n'.join(new_lines)
    new_content = f"---\n{new_frontmatter}\n---\n{remaining_content}"

    if dry_run:
        print(f"   Would add redirects: {redirects}")
        return True

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"   ✅ Added redirects: {redirects}")
    return True


def process_posts(posts_dir: Path, dry_run: bool = False) -> Dict[str, int]:
    """Process all posts and add redirects."""
    stats = {'processed': 0, 'skipped': 0, 'updated': 0}

    # Find all post files
    post_files = list(posts_dir.glob('**/*.md'))

    print(f"\nFound {len(post_files)} post files")

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")

    for file_path in sorted(post_files):
        print(f"\n📝 Processing: {file_path.relative_to(posts_dir)}")
        stats['processed'] += 1

        # Parse filename
        file_info = parse_post_filename(file_path.name)
        if not file_info:
            print(f"   ⚠️  Invalid filename format")
            stats['skipped'] += 1
            continue

        # Read and parse post
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, _, _ = extract_frontmatter(content)

        if not frontmatter:
            print(f"   ⚠️  No frontmatter")
            stats['skipped'] += 1
            continue

        # Generate redirect list
        redirects = generate_redirect_from_list(frontmatter, file_info)

        if redirects is None:
            print(f"   ℹ️  Already has redirects")
            stats['skipped'] += 1
            continue

        # Update post
        if update_post_with_redirects(file_path, redirects, dry_run):
            stats['updated'] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(description='Generate 301 redirects for Jekyll posts')
    parser.add_argument('--posts-dir', required=True, help='Path to _posts directory')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')

    args = parser.parse_args()

    posts_dir = Path(args.posts_dir)

    if not posts_dir.exists():
        print(f"Error: Posts directory not found: {posts_dir}")
        exit(1)

    print("=" * 60)
    print("Jekyll Post Redirect Generator")
    print("=" * 60)

    stats = process_posts(posts_dir, args.dry_run)

    print("\n" + "=" * 60)
    print(f"✅ Complete")
    print(f"   Processed: {stats['processed']}")
    print(f"   Updated: {stats['updated']}")
    print(f"   Skipped: {stats['skipped']}")
    print("=" * 60)


if __name__ == '__main__':
    main()
