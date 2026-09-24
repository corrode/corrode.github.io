#!/usr/bin/env python3
"""Offline browser regression test (requires Python Playwright and installed Chrome).

    zola build --output-dir public/theme-test --force
    python3 scripts/test-theme.py public/theme-test

All page requests are fulfilled from the build directory or aborted, including
analytics and fonts. No server, package download, or external HTTP call is needed.
"""

import argparse
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("build", type=Path)
parser.add_argument("--browser", default="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
parser.add_argument("--screenshot", type=Path)
args = parser.parse_args()
root = args.build.resolve()
assert (root / "index.html").is_file(), "Build the site first"

# These exercise combinations that the old append/delete approach mishandled.
probes = """<style>
html { --compound: no; --nested: no; --either: no; --negated: no; }
@media screen and (max-width: 950px) and (prefers-color-scheme: dark) {
    html { --compound: yes; }
}
@supports (display: grid) {
    @media (prefers-color-scheme: light) { html { --nested: yes; } }
}
@media (max-width: 950px) and (prefers-color-scheme: light),
       (min-width: 951px) and (prefers-color-scheme: dark) {
    html { --either: yes; }
}
@media not all and (prefers-color-scheme: dark) {
    html { --negated: yes; }
}
</style>"""


def serve(route):
    url = urlparse(route.request.url)
    file = (root / (url.path.lstrip("/") or "index.html")).resolve()
    if url.netloc != "theme.test" or not file.is_relative_to(root) or not file.is_file():
        route.abort()
    elif file.name == "index.html":
        html = file.read_text().replace("</head>", probes + "</head>")
        html = html.replace("</body>", '<span id="syntax-probe" class="z-comment" hidden></span></body>')
        route.fulfill(body=html, content_type="text/html")
    else:
        route.fulfill(path=str(file))


def check(page, scheme, width):
    dark = scheme == "dark"
    mobile = width <= 950
    expect(page.locator("body")).to_have_css(
        "background-color", "rgb(45, 49, 64)" if dark else "rgb(250, 183, 28)"
    )
    expect(page.locator("#icon-moon")).to_have_css("display", "block" if dark else "none")
    expect(page.locator("#icon-sun")).to_have_css("display", "none" if dark else "block")
    expect(page.locator(".menu")).to_have_css("flex-direction", "column" if mobile else "row")
    expect(page.locator("#syntax-probe")).to_have_css(
        "color", "rgb(98, 114, 164)" if dark else "rgb(149, 129, 94)"
    )
    if mobile:
        background = "rgb(26, 28, 38)" if dark else "rgb(250, 183, 28)"
        expect(page.locator(".menu")).to_have_css("background-color", background)
        expect(page.locator(".nav-theme-toggle")).to_have_css("background-color", background)
        expect(page.locator("#theme-toggle")).to_have_css(
            "color", "rgb(255, 255, 255)" if dark else "rgb(17, 17, 17)"
        )
        # Button retains the full menu-row tap target.
        button = page.locator("#theme-toggle").bounding_box()
        row = page.locator(".nav-theme-toggle").bounding_box()
        assert button["width"] == row["width"] and button["height"] == row["height"]
    state = page.evaluate("""() => {
        const style = getComputedStyle(document.documentElement);
        return {
            probes: ['compound', 'nested', 'either', 'negated'].map(
                name => style.getPropertyValue('--' + name).trim()),
            syntax: [...document.querySelectorAll('link[href*="syntax-theme"]')].map(
                link => matchMedia(link.media).matches),
        };
    }""")
    assert state["syntax"] == [dark, not dark], state
    assert state["probes"] == [
        "yes" if mobile and dark else "no",
        "no" if dark else "yes",
        "yes" if mobile != dark else "no",
        "no" if dark else "yes",
    ], state


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=args.browser, headless=True)
    cases = 0
    toggles = 0
    try:
        for system in ["light", "dark"]:
            for width in [390, 950, 951, 1280]:
                for saved in [None, "light", "dark"]:
                    context = browser.new_context(
                        viewport={"width": width, "height": 844},
                        color_scheme=system,
                        service_workers="block",
                    )
                    context.route("**/*", serve)
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto("http://theme.test/", wait_until="networkidle")
                    if saved:
                        page.evaluate("scheme => localStorage.setItem('scheme', scheme)", saved)
                        page.reload(wait_until="networkidle")
                    if width <= 950:
                        page.locator(".menu-button-container").click()
                    scheme = saved or system
                    check(page, scheme, width)
                    for _ in range(4):
                        page.get_by_role("button", name="Toggle color scheme", exact=True).click()
                        toggles += 1
                        scheme = "light" if scheme == "dark" else "dark"
                        check(page, scheme, width)
                        assert page.evaluate("localStorage.getItem('scheme')") == (
                            None if scheme == system else scheme
                        )
                    # Resizing must still obey responsive conditions after mutations.
                    other_width = 1280 if width <= 950 else 390
                    page.set_viewport_size({"width": other_width, "height": 844})
                    if other_width <= 950:
                        page.locator(".menu-button-container").click()
                    check(page, scheme, other_width)
                    page.reload(wait_until="networkidle")
                    if other_width <= 950:
                        page.locator(".menu-button-container").click()
                    check(page, scheme, other_width)
                    assert not errors, errors
                    if args.screenshot and system == "light" and width == 1280 and saved is None:
                        page.screenshot(path=str(args.screenshot))
                    context.close()
                    cases += 1
        print(f"PASS: {cases} cases, {toggles} button toggles, reloads and breakpoint changes; no external requests")
    finally:
        browser.close()
