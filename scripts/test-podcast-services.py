#!/usr/bin/env python3
"""Offline regression test: zola build && python3 scripts/test-podcast-services.py public

Requires Python Playwright and its Chromium, or --browser /path/to/browser. External requests are blocked;
no bookings or emails are sent. Optional --screenshot saves the footer.
"""
import argparse
import json
from pathlib import Path
import tomllib
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("build", type=Path)
parser.add_argument("--screenshot", type=Path)
parser.add_argument("--browser", help="Optional Chromium-based browser executable")
args = parser.parse_args()
root = args.build.resolve()
source = Path(__file__).resolve().parent.parent
selected = []
for file in sorted((source / "content/podcast").glob("*/index.md")):
    data = tomllib.loads(file.read_text().split("+++", 2)[1])
    if data.get("extra", {}).get("services_prompt"):
        selected.append((file.parent.name, data["extra"]["services_prompt"]))
assert len(selected) == 15



def serve(route):
    request = route.request
    if request.method == "POST":
        route.abort()
        return
    url = urlparse(request.url)
    file = (root / url.path.lstrip("/")).resolve()
    if file.is_dir():
        file /= "index.html"
    if url.netloc == "podcast.test" and file.is_relative_to(root) and file.is_file():
        route.fulfill(path=str(file))
    else:
        route.abort()


with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=args.browser,
        headless=True,
    )
    page = browser.new_page()
    page.route("**/*", serve)
    for slug, prompt in selected:
        page.goto(f"http://podcast.test/podcast/{slug}/")
        footer = page.locator(".podcast-about")
        expect(footer).to_contain_text(prompt)
        expect(footer.locator("a")).to_have_count(1)
        link = footer.locator("a").get_attribute("href")
        tags = parse_qs(urlparse(link).query)
        assert tags == {
            "utm_source": ["rust-in-production"], "utm_medium": ["podcast"],
            "utm_campaign": ["services"], "utm_content": [slug],
        }, (slug, tags)
        assert urlparse(link).path == "/services/"
        assert page.locator(".episode-content").evaluate(
            "el => el.querySelector('.podcast-about').previousElementSibling !== null"
        )

    page.goto("http://podcast.test/podcast/s06e01-cloudsmith/")
    for width in [1440, 375]:
        page.set_viewport_size({"width": width, "height": 900})
        page.locator(".podcast-about").scroll_into_view_if_needed()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        if args.screenshot:
            page.screenshot(path=str(args.screenshot.with_name(f"{args.screenshot.stem}-{width}.png")))
    page.locator(".podcast-about a").click()
    page.wait_for_load_state("load")
    assert urlparse(page.url).path == "/services/"
    assert parse_qs(urlparse(page.url).query)["utm_content"] == ["s06e01-cloudsmith"]
    # Tagged arrivals must not rewrite booking or email links.
    expect(page.locator('script[src="/services/attribution.js"]')).to_have_count(0)
    expect(page.locator('a[data-cal-link="corrode/chat"]')).to_have_count(2)

    expect(page.locator('a[href="mailto:hi@corrode.dev"]')).to_have_count(2)
    for link in page.locator('a[data-cal-link="corrode/chat"]').all():
        assert json.loads(link.get_attribute("data-cal-config")) == {"layout": "month_view"}
        assert link.get_attribute("href") == "https://cal.com/corrode/chat"
    page.goto("http://podcast.test/podcast/s01e00-teaser/")
    expect(page.locator(".podcast-about")).not_to_contain_text("I'm Matthias")
    expect(page.locator(".podcast-about a")).to_have_attribute("href", "/services/")
    browser.close()
print("PASS: 15 episode CTAs, responsive footer, plain tagged links, unchanged booking/email links")
