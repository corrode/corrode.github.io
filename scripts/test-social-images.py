#!/usr/bin/env python3
"""Regression tests for the rendered social-image check (standard library only)."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "check_social_images", Path(__file__).with_name("check-social-images.py"))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SocialImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.page = self.root / "blog/example/index.html"
        self.page.parent.mkdir(parents=True)

    def post(self, image):
        self.page.write_text(
            '<meta property="og:type" content="article">'
            '<meta property="og:url" content="https://corrode.dev/blog/example/">'
            f'<meta property="og:image" content="{image}">', encoding="utf-8")

    def test_colocated_image(self):
        self.post("https://corrode.dev/blog/example/social.png")
        self.page.with_name("social.png").write_bytes(b"image")
        self.assertEqual(checker.check(self.root), (1, []))

    def test_fallback_image(self):
        self.post("/social/default.png")
        image = self.root / "social/default.png"
        image.parent.mkdir()
        image.write_bytes(b"image")
        self.assertEqual(checker.check(self.root), (1, []))

    def test_missing_and_empty_image(self):
        self.post("social.png")
        self.assertIn("missing or empty", checker.check(self.root)[1][0])
        self.page.with_name("social.png").touch()
        self.assertIn("missing or empty", checker.check(self.root)[1][0])

    def test_missing_metadata(self):
        self.post("")
        self.assertIn("missing og:image", checker.check(self.root)[1][0])

    def test_external_image(self):
        self.post("https://example.org/social.png")
        self.assertIn("must be local", checker.check(self.root)[1][0])

    def test_path_escape(self):
        self.post("/../outside.png")
        self.assertIn("escapes build", checker.check(self.root)[1][0])

    def test_redirects_and_sections_are_not_posts(self):
        self.page.write_text('<meta http-equiv="refresh" content="0;url=/blog/new/">')
        count, errors = checker.check(self.root)
        self.assertEqual(count, 0)
        self.assertIn("no rendered articles", errors[0])


if __name__ == "__main__":
    unittest.main()
