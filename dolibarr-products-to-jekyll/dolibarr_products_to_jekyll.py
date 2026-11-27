#!/usr/bin/env python3
"""Dolibarr products -> a Jekyll `products` collection. One script for every Jekyll site (stage 1: no payment, buy links to the marketplace ads).

Adapted from infra-automation `services/resale-photos/tools/resale/website_sync.py` (flat folder, Stripe links) for sites that keep
products per language (`_products/<lang>/`) and use shared includes (`jekyll-theme-common-includes`).

  python3 dolibarr_products_to_jekyll.py --site-dir ../eagles-techs.com --lang fr --list           # what would be published (dry run, default)
  python3 dolibarr_products_to_jekyll.py --site-dir ... --lang fr --mark --apply                   # website_status=listed for live items with an ad
  python3 dolibarr_products_to_jekyll.py --site-dir ... --lang fr --apply --images --prune         # write pages + photos, remove stale generated pages

Selection (explicit, never guessed): products whose Dolibarr extrafield `website_status` is listed, reserved or sold.
`--mark` is the only thing that sets it: lifecycle listed AND at least one marketplace URL AND not sold. Sold items stay as a "Vendu" page.
Pages carry `generated_by: dolibarr-products-to-jekyll`; only those are ever overwritten or pruned. Nothing outside the collection is touched.
The page links OUT to the ads (buy_links). Never put the site address in a marketplace ad (marketplace rules).
Env: DOLIBARR_URL, DOLIBARR_API_KEY (or DOLIBARR_APIKEY). Python stdlib only; the Dolibarr front rejects the default urllib agent, so a curl agent is sent.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

MARK = "generated_by: dolibarr-products-to-jekyll"
SITE_STATUSES = ("listed", "reserved", "sold")
CONDITION_LABEL = {"fr": {"new": "Neuf", "like_new": "Comme neuf", "good": "Bon état", "fair": "État correct", "parts": "Pour pièces"},
                   "en": {"new": "New", "like_new": "Like new", "good": "Good condition", "fair": "Fair condition", "parts": "For parts"}}
BUY_LABEL = {"fr": "Acheter sur {}", "en": "Buy on {}"}
STATUS = {"listed": "available", "reserved": "reserved", "sold": "sold"}
IMG_RE = re.compile(r"\.(jpe?g|png|webp)$", re.I)


class Dolibarr:
    def __init__(self, url: str, key: str):
        self.base, self.key = url.rstrip("/") + "/api/index.php", key

    def _req(self, method: str, path: str, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"DOLAPIKEY": self.key, "User-Agent": "curl/8.5.0", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)

    def products(self) -> list[dict]:
        out, page = [], 0
        while True:
            rows = self._req("GET", f"/products?limit=100&page={page}&sortfield=t.rowid&sortorder=ASC&includeextrafields=1")
            out += rows
            if len(rows) < 100:
                return out
            page += 1

    def documents(self, product_id) -> list[dict]:
        try:
            return self._req("GET", f"/documents?modulepart=product&id={product_id}") or []
        except Exception:
            return []

    def download(self, ref: str, name: str) -> bytes:
        f = self._req("GET", "/documents/download?modulepart=product&original_file=" + urllib.request.quote(f"{ref}/{name}"))
        return base64.b64decode(f["content"])

    def update(self, product_id, body: dict):
        return self._req("PUT", f"/products/{product_id}", body)


def opt(p: dict, name: str):
    v = (p.get("array_options") or {}).get("options_" + name)
    return None if v in ("", None) else v


def slugify(text: str) -> str:
    t = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:70].strip("-")


def to_text(raw: str) -> str:
    t = re.sub(r"(?i)<\s*br\s*/?>|</p>|</li>|</div>", "\n", raw or "")
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+\n", "\n", t)).strip()


def page_slug(p: dict) -> str:
    ref = str(opt(p, "public_ref") or p.get("ref") or p.get("id")).lower()
    title = re.sub(r"\s*[-·]\s*R\d+\s*$", "", p.get("label") or "", flags=re.I)   # titles end with the ref: do not repeat it
    return f"{ref}-{slugify(title)}".strip("-")


def wants_site(p: dict) -> bool:
    return opt(p, "website_status") in SITE_STATUSES


def markable(p: dict) -> bool:
    """Live on a marketplace (lifecycle listed + an ad URL), not sold, and not already on the site."""
    return (opt(p, "lifecycle") == "listed" and bool(opt(p, "vinted_url") or opt(p, "leboncoin_url")) and not opt(p, "website_status")
            and opt(p, "vinted_status") != "sold" and opt(p, "leboncoin_status") != "sold")


def buy_links(p: dict, lang: str) -> list[dict]:
    out = []
    for key, name in (("vinted_url", "Vinted"), ("leboncoin_url", "Leboncoin")):
        u = opt(p, key)
        if u and str(u).startswith("https://"):
            out.append({"label": BUY_LABEL[lang].format(name), "url": u})
    return out


def front_matter(p: dict, lang: str, images: list[str], layout: str, currency: str) -> dict:
    s = page_slug(p)
    price = opt(p, "website_price") or p.get("price_ttc") or p.get("price") or 0
    fm = {"layout": layout, "lang": lang, "title": re.sub(r"\s*[-·]\s*R\d+\s*$", "", p.get("label") or s, flags=re.I),
          "description": to_text(p.get("description"))[:160].replace("\n", " "), "price": round(float(price), 2), "currency": currency,
          "product_id": opt(p, "public_ref") or p.get("ref"), "slug": s, "permalink": f"/{lang}/products/{s}/", "category": "occasion",
          "condition": CONDITION_LABEL[lang].get(opt(p, "item_condition") or ""), "status": STATUS.get(opt(p, "website_status"), "available"),
          "dolibarr_id": int(p["id"])}
    if images:
        fm["image"], fm["images"] = images[0], images
    links = buy_links(p, lang)
    if links:
        fm["buy_links"] = links
    return {k: v for k, v in fm.items() if v not in (None, "")}


def render(p: dict, lang: str, images: list[str], layout: str, currency: str, include: str) -> str:
    fm = front_matter(p, lang, images, layout, currency)
    lines = ["---", MARK] + [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fm.items()] + ["---"]
    return "\n".join(lines) + f"\n\n{to_text(p.get('description'))}\n\n{{% include {include} %}}\n"


def sync(api, site: Path, lang: str, apply: bool, images: bool, prune: bool, mark: bool, collection: str, layout: str, currency: str,
         include: str, out=print) -> dict:
    coll = site / collection.format(lang=lang)
    rows = api.products()
    res = {"marked": [], "written": [], "pruned": [], "images": 0}
    if mark:
        for p in rows:
            if markable(p):
                res["marked"].append(opt(p, "public_ref"))
                out(f"[{'MARK ' if apply else 'DRY  '}] {opt(p, 'public_ref')} website_status=listed")
                if apply:
                    api.update(p["id"], {"array_options": {"options_website_status": "listed"}})
                    p.setdefault("array_options", {})["options_website_status"] = "listed"
    keep = set()
    for p in rows:
        if not wants_site(p):
            continue
        s = page_slug(p)
        keep.add(f"{s}.md")
        imgs: list[str] = []
        if images:
            for d in sorted(api.documents(p["id"]), key=lambda d: d.get("name", "")):
                n = d.get("name", "")
                if not IMG_RE.search(n):
                    continue
                imgs.append(f"/assets/products/{s}/{n}")
                dest = site / "assets" / "products" / s / n
                if apply and not dest.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(api.download(p["ref"], n))
                    res["images"] += 1
        text = render(p, lang, imgs, layout, currency, include)
        path = coll / f"{s}.md"
        if not path.exists() or path.read_text() != text:
            out(f"[{'WRITE' if apply else 'DRY  '}] {path} ({opt(p, 'website_status')}, {opt(p, 'public_ref')})")
            res["written"].append(str(path))
            if apply:
                coll.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
    if prune and coll.exists():
        for f in sorted(coll.glob("*.md")):
            if f.name not in keep and MARK in f.read_text()[:400]:
                out(f"[{'PRUNE' if apply else 'DRY  '}] {f}")
                res["pruned"].append(str(f))
                if apply:
                    f.unlink()
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--site-dir", required=True, help="checkout of the Jekyll site")
    ap.add_argument("--lang", default="fr")
    ap.add_argument("--collection", default="_products/{lang}", help="folder under the site, {lang} is replaced")
    ap.add_argument("--layout", default="resale-product")
    ap.add_argument("--include", default="common/ecommerce/resale-product.html", help="shared include rendered at the end of each page")
    ap.add_argument("--currency", default="EUR")
    ap.add_argument("--mark", action="store_true", help="set website_status=listed on live items that have an ad")
    ap.add_argument("--images", action="store_true", help="copy the Dolibarr product photos into assets/products/<slug>/")
    ap.add_argument("--prune", action="store_true")
    ap.add_argument("--apply", action="store_true", help="write (default is a dry run)")
    ap.add_argument("--list", action="store_true", help="accepted for readability; the default is already a dry run")
    a = ap.parse_args(argv)
    key = os.environ.get("DOLIBARR_API_KEY") or os.environ.get("DOLIBARR_APIKEY")
    if not key or not os.environ.get("DOLIBARR_URL"):
        print("set DOLIBARR_URL and DOLIBARR_API_KEY", file=sys.stderr)
        return 2
    r = sync(Dolibarr(os.environ["DOLIBARR_URL"], key), Path(a.site_dir), a.lang, a.apply, a.images, a.prune, a.mark, a.collection, a.layout,
             a.currency, a.include)
    print(f"# marked {len(r['marked'])}, pages {len(r['written'])}, images {r['images']}, pruned {len(r['pruned'])}, mode={'APPLY' if a.apply else 'DRY RUN'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
