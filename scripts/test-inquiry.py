#!/usr/bin/env python3
"""Offline inquiry regression tests. Requires Python Playwright and Chrome.

    zola build
    python3 scripts/test-inquiry.py public

All requests are intercepted; no inquiry or analytics leaves the browser.
Screenshots are saved under the (gitignored) build directory.
"""

import argparse
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("build", type=Path)
parser.add_argument("--browser", default="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
args = parser.parse_args()
root = args.build.resolve()
assert (root / "index.html").is_file(), "Build the site first"
endpoint = "https://submit-form.com/r7PT0RxiL"
cta = "Discuss Your Rust Migration"
payload = {
    "name": "Test Person",
    "email": "test@example.com",
    "company": "Example",
    "currentStack": "C++ and a Rust prototype",
    "challenges": "Review the prototype before migrating a service.",
    "timeline": "Within 3–6 months",
}


def fill(page):
    for name, value in payload.items():
        field = page.locator(f'#inquiry-form [name="{name}"]')
        if name == "timeline":
            field.select_option(label=value)
        else:
            field.fill(value)


def fits(page, selector, width):
    for box in page.locator(selector).all():
        if box.is_visible():
            bounds = box.bounding_box()
            assert bounds["x"] >= -1 and bounds["x"] + bounds["width"] <= width + 1, (selector, bounds, width)


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=args.browser, headless=True)
    try:
        for width in [320, 390, 768, 1280]:
            for theme in ["light", "dark"]:
                context = browser.new_context(viewport={"width": width, "height": 844}, color_scheme=theme, service_workers="block")
                submissions = []
                mode = {"value": "success"}
                held = []

                def serve(route):
                    request = route.request
                    if request.url == endpoint:
                        submissions.append(request.post_data_json)
                        assert request.method == "POST"
                        if mode["value"] == "pending":
                            held.append(route)
                        elif mode["value"] == "offline":
                            route.abort()
                        else:
                            route.fulfill(status=200 if mode["value"] == "success" else 500, content_type="application/json", body="{}")
                        return
                    url = urlparse(request.url)
                    file = (root / url.path.lstrip("/")).resolve()
                    if file.is_dir():
                        file /= "index.html"
                    if url.netloc == "inquiry.test" and file.is_relative_to(root) and file.is_file():
                        route.fulfill(path=str(file))
                    else:
                        route.abort()

                context.route("**/*", serve)
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                for path in ["/", "/workshops/", "/services/"]:
                    page.goto("http://inquiry.test" + path, wait_until="networkidle")
                    links = page.locator("main a.cta-button")
                    assert links.count() > 0
                    for link in links.all():
                        expect(link).to_have_text(cta)
                        assert link.get_attribute("href") in ["/services/#contact", "#contact"]
                    fits(page, "main a.cta-button", width)
                    assert page.locator('[data-cal-link], #my-cal-inline, #quiz-question-container').count() == 0
                    links.first.click()
                    expect(page.locator("#inquiry-form")).to_be_visible()
                    assert page.url.endswith("/services/#contact")

                form = page.locator("#inquiry-form")
                button = form.get_by_role("button", name="Send inquiry", exact=True)
                button.click()
                assert not submissions
                fill(page)
                form.locator('[name="email"]').fill("invalid-email")
                button.click()
                assert not submissions
                form.locator('[name="email"]').fill(payload["email"])
                assert form.locator("input, textarea, select").count() == 6
                fits(page, "#contact input, #contact textarea, #contact select, #contact button", width)
                assert form.locator('[name="email"]').evaluate("el => parseFloat(getComputedStyle(el).fontSize)") >= 16
                if width in [390, 1280]:
                    page.locator("#contact").screenshot(path=str(root / f"inquiry-{width}-{theme}.png"))

                for failure in ["failure", "offline"]:
                    mode["value"] = failure
                    button.click()
                    expect(page.locator("#inquiry-status")).to_contain_text("couldn't confirm")
                    expect(form).to_be_visible()
                    expect(page.locator("#inquiry-success")).to_be_hidden()
                    expect(button).to_be_enabled()
                    assert page.evaluate("document.activeElement.id") == "inquiry-status"
                    for name, value in payload.items():
                        expect(form.locator(f'[name="{name}"]')).to_have_value(value)

                mode["value"] = "pending"
                before = len(submissions)
                button.click()
                expect(button).to_be_disabled()
                expect(page.locator("#inquiry-success")).to_be_hidden()
                page.evaluate("document.getElementById('inquiry-form').requestSubmit()")
                assert len(submissions) == before + 1
                assert submissions[-1] == payload
                held.pop().fulfill(status=200, content_type="application/json", body="{}")
                expect(form).to_be_hidden()
                expect(page.locator("#inquiry-success")).to_be_visible()
                assert page.evaluate("document.activeElement.id") == "inquiry-success"
                assert page.evaluate("history.state") is None
                assert not errors, errors
                context.close()
                print(f"PASS: {width}px {theme}: CTA routes, validation, failure/retry, pending/double-submit, success/focus, layout")

        # Native submission still uses the same endpoint when JavaScript is off.
        context = browser.new_context(java_script_enabled=False, service_workers="block")
        context.route("**/*", serve)
        page = context.new_page()
        page.goto("http://inquiry.test/services/#contact")
        fill(page)
        captured = []

        def native_submit(route):
            captured.append(route.request.post_data)
            route.fulfill(content_type="text/html", body="<h1>Provider confirmation (test)</h1>")

        context.route(endpoint, native_submit)
        page.locator('#inquiry-form button').click()
        expect(page.get_by_role("heading", name="Provider confirmation (test)")).to_be_visible()
        assert captured and "email=test%40example.com" in captured[0]
        print("PASS: no-JavaScript native POST; provider response mocked, not live delivery")
        context.close()
    finally:
        browser.close()
