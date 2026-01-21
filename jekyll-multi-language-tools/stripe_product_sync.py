#!/usr/bin/env python3
"""
Stripe Product Sync Script

Reads product markdown files from Jekyll blog, creates products in Stripe,
and updates the files with real Stripe Price IDs.

Usage:
    python stripe_product_sync.py --products-dir /path/to/_products --stripe-key sk_test_xxx
"""

import os
import re
import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import stripe
except ImportError:
    print("Error: stripe package not installed. Install with: pip install stripe")
    exit(1)


def parse_product_frontmatter(file_path: Path) -> Dict[str, str]:
    """Extract frontmatter from markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter (between --- markers)
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = match.group(1)
    data = {}

    # Parse YAML-like frontmatter
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip().strip('"')

    return data


def extract_price_from_string(price_str: str) -> Tuple[int, str]:
    """Extract numeric price and currency from string like '$29' or '€39'."""
    # Remove spaces and extract number
    price_match = re.search(r'[\$€]?(\d+)', price_str)
    if not price_match:
        raise ValueError(f"Could not extract price from: {price_str}")

    amount = int(price_match.group(1))

    # Detect currency
    if '€' in price_str:
        currency = 'eur'
    else:
        currency = 'usd'

    # Convert to cents
    amount_cents = amount * 100

    return amount_cents, currency


def create_stripe_product(title: str, description: str, price_str: str,
                          stripe_key: str, lang: str) -> Tuple[str, str]:
    """Create product in Stripe and return product_id and price_id."""
    stripe.api_key = stripe_key

    amount_cents, currency = extract_price_from_string(price_str)

    # Create product
    product = stripe.Product.create(
        name=f"{title} ({lang.upper()})",
        description=description[:500],  # Stripe limits description length
        metadata={
            'lang': lang,
            'source': 'beaconharbor-blog'
        }
    )

    # Create price
    price = stripe.Price.create(
        product=product.id,
        unit_amount=amount_cents,
        currency=currency,
    )

    print(f"✅ Created: {title} ({lang.upper()}) - {price_str} - Price ID: {price.id}")

    return product.id, price.id


def update_product_file(file_path: Path, new_price_id: str) -> None:
    """Update stripe_price_id in product file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace placeholder with real price ID
    updated_content = re.sub(
        r'stripe_price_id:\s*["\']?price_PLACEHOLDER[^"\']*["\']?',
        f'stripe_price_id: "{new_price_id}"',
        content
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"   Updated file: {file_path.name}")


def sync_products(products_dir: Path, stripe_key: str, dry_run: bool = False) -> Dict[str, str]:
    """Sync all products to Stripe and update files."""
    results = {}

    # Find all product markdown files
    product_files = list(products_dir.glob('**/*.md'))

    print(f"\nFound {len(product_files)} product files")
    print(f"Stripe API Key: {stripe_key[:20]}...")

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made to Stripe\n")

    for file_path in sorted(product_files):
        print(f"\n📦 Processing: {file_path.relative_to(products_dir)}")

        # Parse frontmatter
        data = parse_product_frontmatter(file_path)

        if not data:
            print(f"   ⚠️  Skipped: No frontmatter found")
            continue

        title = data.get('title', 'Untitled')
        price = data.get('price', '$0')
        lang = data.get('lang', 'en')
        ref = data.get('ref', '')
        stripe_price_id = data.get('stripe_price_id', '')

        # Skip if already has real Stripe ID
        if stripe_price_id and not stripe_price_id.startswith('price_PLACEHOLDER'):
            print(f"   ℹ️  Skipped: Already has Stripe ID ({stripe_price_id})")
            continue

        # Extract description from content (first paragraph after frontmatter)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Get first heading or paragraph as description
        desc_match = re.search(r'#{1,6}\s+(.+?)(?:\n|$)', content)
        if desc_match:
            description = desc_match.group(1)
        else:
            description = title

        if dry_run:
            print(f"   Would create: {title} ({lang}) - {price}")
            continue

        try:
            # Create in Stripe
            product_id, price_id = create_stripe_product(
                title=title,
                description=description,
                price_str=price,
                stripe_key=stripe_key,
                lang=lang
            )

            # Update file
            update_product_file(file_path, price_id)

            results[str(file_path)] = price_id

        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue

    return results


def main():
    parser = argparse.ArgumentParser(description='Sync Jekyll products to Stripe')
    parser.add_argument('--products-dir', required=True, help='Path to _products directory')
    parser.add_argument('--stripe-key', required=True, help='Stripe secret key (sk_test_... or sk_live_...)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')

    args = parser.parse_args()

    products_dir = Path(args.products_dir)

    if not products_dir.exists():
        print(f"Error: Products directory not found: {products_dir}")
        exit(1)

    print("=" * 60)
    print("Stripe Product Sync")
    print("=" * 60)

    results = sync_products(products_dir, args.stripe_key, args.dry_run)

    print("\n" + "=" * 60)
    print(f"✅ Sync Complete: {len(results)} products synced")
    print("=" * 60)

    if results:
        print("\nUpdated files:")
        for file_path, price_id in results.items():
            print(f"  • {Path(file_path).name} → {price_id}")


if __name__ == '__main__':
    main()
