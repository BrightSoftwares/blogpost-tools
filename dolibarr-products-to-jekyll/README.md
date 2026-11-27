# dolibarr-products-to-jekyll

One script that publishes Dolibarr products to any Jekyll site that keeps products per language (`_products/<lang>/`). Stage 1: no payment, each page links OUT to the product's marketplace ads.

```bash
export DOLIBARR_URL=https://do.example DOLIBARR_API_KEY=...
python3 dolibarr_products_to_jekyll.py --site-dir ../my-site --lang fr                    # dry run
python3 dolibarr_products_to_jekyll.py --site-dir ../my-site --lang fr --mark --apply     # website_status=listed for live items with an ad
python3 dolibarr_products_to_jekyll.py --site-dir ../my-site --lang fr --apply --images --prune
```

- Source of truth: Dolibarr. A product is published when its extrafield `website_status` is `listed`, `reserved` or `sold` (`--mark` sets it for live items with an ad).
- Pages carry `generated_by: dolibarr-products-to-jekyll`; only those are overwritten or pruned.
- Pages render the shared include `common/ecommerce/resale-product.html` (repo `jekyll-theme-common-includes`) through a one-line site layout `resale-product`.
- Never put the site address in a marketplace ad.
- Adapted from `infra-automation/services/resale-photos/tools/resale/website_sync.py` (flat folder, Stripe links). Stripe checkout is stage 2 and not part of this script.
- Tests: `python3 -m pytest dolibarr-products-to-jekyll` (stdlib only otherwise).
