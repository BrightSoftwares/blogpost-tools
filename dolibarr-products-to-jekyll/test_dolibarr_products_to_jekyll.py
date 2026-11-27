"""Tests with an injected fake Dolibarr: selection, front matter, idempotence, prune only touches generated pages."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dolibarr_products_to_jekyll as m  # noqa: E402


def prod(i, ref, label, **o):
    return {"id": str(i), "ref": f"MAT-{i}", "label": label, "description": "<p>Bon <b>adaptateur</b><br>Vendu en l'état</p>", "price": "8.00000000",
            "array_options": {f"options_{k}": v for k, v in {"public_ref": ref, **o}.items()}}


class Fake:
    def __init__(self, rows):
        self.rows, self.updates = rows, []

    def products(self): return self.rows
    def documents(self, pid): return [{"name": "MAT-1-02.jpg"}, {"name": "MAT-1-01.jpg"}, {"name": "note.pdf"}]
    def download(self, ref, name): return b"jpg"
    def update(self, pid, body): self.updates.append((pid, body))


ROWS = lambda: [
    prod(1, "R44", "Adaptateur Mini DisplayPort blanc - R44", lifecycle="listed", vinted_url="https://www.vinted.fr/items/1", leboncoin_url="https://www.leboncoin.fr/ad/x/2", item_condition="good", website_status="listed"),
    prod(2, "R45", "Casque Bluedio", lifecycle="listed", leboncoin_url="https://www.leboncoin.fr/ad/x/3", item_condition="like_new"),
    prod(3, "R46", "Vendu déjà", lifecycle="sold", vinted_url="https://www.vinted.fr/items/9", website_status="sold"),
    prod(4, "R47", "Pas encore", lifecycle="draft"),
]


def run(tmp, rows=None, **kw):
    args = dict(apply=True, images=False, prune=False, mark=False, collection="_products/{lang}", layout="resale-product", currency="EUR", include="common/ecommerce/resale-product.html", out=lambda s: None)
    args.update(kw)
    return m.sync(Fake(rows or ROWS()), tmp, "fr", **args)


def test_slug_drops_the_ref_suffix_and_accents():
    assert m.page_slug(ROWS()[0]) == "r44-adaptateur-mini-displayport-blanc"
    assert m.slugify("Café à l'huile") == "cafe-a-l-huile"


def test_only_website_listed_reserved_sold_are_published(tmp_path):
    run(tmp_path)
    assert sorted(p.name for p in (tmp_path / "_products" / "fr").glob("*.md")) == ["r44-adaptateur-mini-displayport-blanc.md", "r46-vendu-deja.md"]


def test_front_matter_has_links_condition_and_no_html(tmp_path):
    run(tmp_path)
    t = (tmp_path / "_products/fr/r44-adaptateur-mini-displayport-blanc.md").read_text()
    assert "generated_by: dolibarr-products-to-jekyll" in t and '"layout": "resale-product"' not in t and 'layout: "resale-product"' in t
    assert 'condition: "Bon état"' in t and 'status: "available"' in t and "price: 8.0" in t
    assert '"label": "Acheter sur Vinted"' in t and '"label": "Acheter sur Leboncoin"' in t
    assert "<b>" not in t and "Vendu en l'état" in t and "{% include common/ecommerce/resale-product.html %}" in t
    assert 'permalink: "/fr/products/r44-adaptateur-mini-displayport-blanc/"' in t


def test_sold_page_status(tmp_path):
    run(tmp_path)
    assert 'status: "sold"' in (tmp_path / "_products/fr/r46-vendu-deja.md").read_text()


def test_dry_run_writes_nothing_and_second_run_is_a_noop(tmp_path):
    assert run(tmp_path, apply=False)["written"] and not (tmp_path / "_products").exists()
    assert run(tmp_path)["written"] and run(tmp_path)["written"] == []


def test_mark_selects_live_items_with_an_ad_only(tmp_path):
    f = Fake(ROWS())
    r = m.sync(f, tmp_path, "fr", True, False, False, True, "_products/{lang}", "resale-product", "EUR", "x", out=lambda s: None)
    assert r["marked"] == ["R45"] and f.updates == [("2", {"array_options": {"options_website_status": "listed"}})]
    assert (tmp_path / "_products/fr" / "r45-casque-bluedio.md").exists()      # marked in the same run, so it is published


def test_prune_removes_only_generated_stale_pages(tmp_path):
    coll = tmp_path / "_products/fr"
    coll.mkdir(parents=True)
    (coll / "stale.md").write_text(f"---\n{m.MARK}\n---\n")
    (coll / "handmade.md").write_text("---\ntitle: mine\n---\n")
    r = run(tmp_path, prune=True)
    assert r["pruned"] == [str(coll / "stale.md")] and (coll / "handmade.md").exists()


def test_images_are_copied_in_name_order_and_non_images_skipped(tmp_path):
    r = run(tmp_path, images=True)
    d = tmp_path / "assets/products/r44-adaptateur-mini-displayport-blanc"
    assert sorted(x.name for x in d.iterdir()) == ["MAT-1-01.jpg", "MAT-1-02.jpg"] and r["images"] == 4
    assert 'image: "/assets/products/r44-adaptateur-mini-displayport-blanc/MAT-1-01.jpg"' in (tmp_path / "_products/fr/r44-adaptateur-mini-displayport-blanc.md").read_text()


def test_non_https_links_are_dropped():
    p = prod(5, "R5", "x", vinted_url="javascript:alert(1)", leboncoin_url="http://x")
    assert m.buy_links(p, "fr") == []
