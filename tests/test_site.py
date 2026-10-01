import base64
import hashlib
import os
import re
import unittest

os.environ.setdefault("F1_AUTO_SYNC", "0")

from src.app import server
from src.config import LANGUAGES, SITE_URL


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = server.app.test_client()

    def html(self, path):
        response = self.client.get(path)
        return response, response.get_data(as_text=True)

    def test_every_page_in_every_language_has_its_own_meta(self):
        titles = set()
        for path in ("/", "/privacy", "/terms"):
            for lang in LANGUAGES:
                url = path if lang == "en" else f"{path}?lang={lang}"
                with self.subTest(url=url):
                    response, html = self.html(url)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(f'<html lang="{lang}"', html)
                    title = re.search(r"<title>(.+?)</title>", html).group(1)
                    description = re.search(r'<meta name="description" content="(.+?)">', html).group(1)
                    self.assertTrue(len(description) > 40)
                    self.assertIn(f'<link rel="canonical" href="{SITE_URL}{url}">', html)
                    self.assertEqual(html.count('rel="alternate" hreflang='), len(LANGUAGES) + 1)
                    self.assertIn('property="og:image" content="', html)
                    self.assertIn('name="twitter:card" content="summary_large_image"', html)
                    titles.add(title)
        self.assertEqual(len(titles), 3 * len(LANGUAGES))

    def test_legal_pages_show_operator_details(self):
        for doc in ("privacy", "terms"):
            for lang in LANGUAGES:
                with self.subTest(doc=doc, lang=lang):
                    _, html = self.html(f"/{doc}?lang={lang}")
                    self.assertIn('class="card legal"', html)
                    self.assertIn("mailto:", html)
                    self.assertIn('class="site-footer"', html)

    def test_custom_404_page(self):
        response, html = self.html("/no-such-page")
        self.assertEqual(response.status_code, 404)
        self.assertIn('class="card notfound"', html)
        self.assertIn('<meta name="robots" content="noindex">', html)
        self.assertNotIn('rel="canonical"', html)

    def test_api_404_stays_json(self):
        response = self.client.get("/api/no-such-endpoint")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())

    def test_robots_and_sitemap(self):
        robots = self.client.get("/robots.txt").get_data(as_text=True)
        self.assertIn("Disallow: /api/", robots)
        self.assertIn(f"Sitemap: {SITE_URL}/sitemap.xml", robots)
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.mimetype, "application/xml")
        xml = response.get_data(as_text=True)
        self.assertEqual(xml.count("<url>"), 3 * len(LANGUAGES))
        self.assertIn(f"<loc>{SITE_URL}/privacy?lang=pl</loc>", xml)
        self.assertIn('hreflang="x-default"', xml)

    def test_every_image_has_alt_text(self):
        for path in ("/", "/privacy", "/no-such-page"):
            _, html = self.html(path)
            for tag in re.findall(r"<img\b[^>]*>", html):
                with self.subTest(path=path, tag=tag[:60]):
                    self.assertRegex(tag, r'alt="[^"]+"')

    def test_inline_scripts_are_allowed_by_hash(self):
        response, html = self.html("/")
        policy = response.headers["Content-Security-Policy"]
        for body in re.findall(r"<script>(.*?)</script>", html, re.S):
            digest = base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
            self.assertIn(f"'sha256-{digest}'", policy)
        self.assertNotIn("googleapis", policy)

    def test_assets_are_served_locally(self):
        for path, mimetype in (
            ("/static/fonts/titillium-web-regular.woff", "font/woff"),
            ("/static/brand/og-image.png", "image/png"),
            ("/favicon.ico", "image/vnd.microsoft.icon"),
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, mimetype)


if __name__ == "__main__":
    unittest.main()
