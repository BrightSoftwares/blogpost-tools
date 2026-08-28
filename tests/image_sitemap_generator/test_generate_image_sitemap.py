"""Tests for image-sitemap-generator/src/generate_image_sitemap.py.

New tool (231.004.PRJ t213-33): jekyll-sitemap generates page URLs only, no
image extension. This crawls the live site's own sitemap.xml and HTML to
build a companion Google Image Sitemap.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "image-sitemap-generator" / "src")
)

from generate_image_sitemap import (  # noqa: E402
    PageImages,
    extract_images,
    is_content_image,
    render_image_sitemap_xml,
)


class TestIsContentImage:
    def test_data_uri_is_excluded(self):
        assert is_content_image("data:image/png;base64,iVBORw0KGgo=") is False

    def test_ordinary_content_image_is_included(self):
        assert is_content_image("https://bright-softwares.com/assets/images/bsgen/hero.svg") is True

    def test_favicon_is_excluded(self):
        assert is_content_image("https://bright-softwares.com/favicon.ico") is False

    def test_logo_path_is_excluded(self):
        assert is_content_image("https://bright-softwares.com/assets/images/logo/mark.svg") is False

    def test_nav_icon_path_is_excluded(self):
        assert is_content_image("https://bright-softwares.com/assets/images/nav/menu.svg") is False

    def test_apple_touch_icon_is_excluded(self):
        assert is_content_image("https://bright-softwares.com/apple-touch-icon.png") is False


class TestExtractImages:
    PAGE_URL = "https://bright-softwares.com/blog/my-post/"

    def test_extracts_absolute_and_relative_images(self):
        html = (
            "<html><head><link rel='icon' href='/favicon.ico'></head><body>"
            '<img src="https://cdn.example.com/hero.jpg" alt="Hero shot">'
            '<img src="/assets/images/bsgen/card.svg" alt="">'
            "</body></html>"
        )
        images = extract_images(html, self.PAGE_URL)
        urls = [u for u, _ in images]
        assert "https://cdn.example.com/hero.jpg" in urls
        assert "https://bright-softwares.com/assets/images/bsgen/card.svg" in urls

    def test_head_images_are_ignored(self):
        # Only <body> content counts — head-only markup (e.g. a preload link,
        # not an <img>) must never surface as a sitemap entry.
        html = (
            "<html><head><img src='/should-not-count.png'></head>"
            "<body><img src='/should-count.png' alt='x'></body></html>"
        )
        images = extract_images(html, self.PAGE_URL)
        urls = [u for u, _ in images]
        assert "https://bright-softwares.com/should-not-count.png" not in urls
        assert "https://bright-softwares.com/should-count.png" in urls

    def test_alt_text_becomes_title(self):
        html = '<body><img src="/a.png" alt="A descriptive caption"></body>'
        images = extract_images(html, self.PAGE_URL)
        assert images == [("https://bright-softwares.com/a.png", "A descriptive caption")]

    def test_missing_alt_yields_empty_title(self):
        html = '<body><img src="/a.png"></body>'
        images = extract_images(html, self.PAGE_URL)
        assert images == [("https://bright-softwares.com/a.png", "")]

    def test_duplicate_images_are_deduped(self):
        html = '<body><img src="/a.png" alt="first"><img src="/a.png" alt="second"></body>'
        images = extract_images(html, self.PAGE_URL)
        assert len(images) == 1

    def test_data_uri_images_are_excluded(self):
        html = '<body><img src="data:image/png;base64,abc123"><img src="/real.png" alt="x"></body>'
        images = extract_images(html, self.PAGE_URL)
        urls = [u for u, _ in images]
        assert not any(u.startswith("data:") for u in urls)
        assert "https://bright-softwares.com/real.png" in urls

    def test_no_img_tags_returns_empty_list(self):
        html = "<body><p>No images here.</p></body>"
        assert extract_images(html, self.PAGE_URL) == []

    def test_images_capped_at_google_per_url_limit(self):
        # MAX_IMAGES_PER_URL = 1000 (Google's documented per-URL limit).
        tags = "".join(f'<img src="/img-{i}.png" alt="{i}">' for i in range(1200))
        html = f"<body>{tags}</body>"
        images = extract_images(html, self.PAGE_URL)
        assert len(images) == 1000


class TestRenderImageSitemapXml:
    def test_valid_xml_structure_with_namespace(self):
        pages = [
            PageImages(
                url="https://bright-softwares.com/post-1/",
                images=[("https://bright-softwares.com/a.png", "A caption")],
            )
        ]
        xml = render_image_sitemap_xml(pages)
        assert '<?xml version="1.0" encoding="UTF-8"?>' in xml
        assert 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"' in xml
        assert 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"' in xml
        assert "<loc>https://bright-softwares.com/post-1/</loc>" in xml
        assert "<image:loc>https://bright-softwares.com/a.png</image:loc>" in xml
        assert "<image:title>A caption</image:title>" in xml

    def test_empty_title_omits_title_tag(self):
        pages = [PageImages(url="https://x.com/p/", images=[("https://x.com/a.png", "")])]
        xml = render_image_sitemap_xml(pages)
        assert "<image:title>" not in xml

    def test_empty_pages_produces_valid_empty_urlset(self):
        xml = render_image_sitemap_xml([])
        assert "<urlset" in xml
        assert "</urlset>" in xml
        assert "<url>" not in xml

    def test_special_characters_are_xml_escaped(self):
        # xml.sax.saxutils.escape only escapes &, <, > in text content —
        # quotes are valid unescaped inside element text (only attribute
        # values require &quot;), so this checks the escaping that actually
        # matters for well-formed XML, not over-escaping.
        pages = [
            PageImages(
                url="https://x.com/p?a=1&b=2",
                images=[("https://x.com/a.png", "A <caption> & more")],
            )
        ]
        xml = render_image_sitemap_xml(pages)
        assert "https://x.com/p?a=1&amp;b=2" in xml
        assert "A &lt;caption&gt; &amp; more" in xml
        # The result must still be parseable as well-formed XML.
        from xml.etree import ElementTree

        ElementTree.fromstring(xml)

    def test_multiple_images_per_page(self):
        pages = [
            PageImages(
                url="https://x.com/p/",
                images=[
                    ("https://x.com/a.png", "First"),
                    ("https://x.com/b.png", "Second"),
                ],
            )
        ]
        xml = render_image_sitemap_xml(pages)
        assert xml.count("<image:image>") == 2
