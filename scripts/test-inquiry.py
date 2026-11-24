#!/usr/bin/env python3
"""Offline inquiry regression tests. Requires Python Playwright and Chrome.

    zola build
    python3 scripts/test-inquiry.py public

All requests are intercepted; no inquiry or analytics leaves the browser.
Screenshots are saved under the (gitignored) build directory.
"""

import argparse
from pathlib import Path
from urllib.parse import parse_qs, urlparse

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


mentoring_payload = {
    "inquiryType": "mentoring",
    "name": "Test Person",
    "email": "test@example.com",
    "background": "Python engineer building my first Rust service.",
    "goals": "Learn to review ownership and API design decisions.",
    "support": "Ongoing mentoring",
    "availability": "Europe/Berlin, Tuesday afternoons.",
}


def fill_mentoring(page):
    for name, value in mentoring_payload.items():
        field = page.locator(f'#inquiry-form [name="{name}"]')
        if name == "inquiryType":
            expect(field).to_have_attribute("type", "hidden")
            expect(field).to_have_value(value)
        elif name == "support":
            field.select_option(label=value)
        else:
            field.fill(value)


def test_mentoring(page, width, theme, submissions, mode, held):
    page.goto("http://inquiry.test/mentoring/", wait_until="load")
    links = page.locator("main a.pro-btn")
    assert links.count() > 0
    for link in links.all():
        expect(link).to_have_text("Get Rust Mentoring")
        expect(link).to_have_attribute("href", "#contact")
    fits(page, "main a.pro-btn", width)
    links.first.click()
    assert page.url.endswith("/mentoring/#contact")
    assert page.locator('script[src="/services/inquiry.js"]').count() == 1
    form = page.locator("#inquiry-form")
    expect(form).to_be_visible()
    expect(form).to_have_attribute("action", endpoint)
    assert form.get_attribute("method").lower() == "post"
    assert form.locator("input, textarea, select").count() == 7
    button = form.get_by_role("button", name="Send mentoring inquiry", exact=True)
    before = len(submissions)
    submit_form(button)
    assert len(submissions) == before
    fill_mentoring(page)
    for name in ["name", "email", "background", "goals", "support", "availability"]:
        field = form.locator(f'[name="{name}"]')
        expect(field).to_have_attribute("required", "")
        if name == "support":
            assert field.evaluate("el => el.tagName") == "SELECT"
            options = field.locator("option").evaluate_all(
                "options => options.filter(o => o.value).map(o => o.textContent.trim())"
            )
            assert options == ["Ongoing mentoring", "Help with a specific problem", "Not sure yet"]
            for option in options:
                field.select_option(label=option)
                expect(field).to_have_value(option)
            field.select_option("")
        else:
            if name in ["background", "goals", "availability"]:
                assert field.evaluate("el => el.tagName") == "TEXTAREA"
            field.fill("")
        submit_form(button)
        assert len(submissions) == before
        assert not field.evaluate("el => el.checkValidity()")
        fill_mentoring(page)
    form.locator('[name="email"]').fill("invalid-email")
    submit_form(button)
    assert len(submissions) == before
    fill_mentoring(page)
    fits(page, "#contact input, #contact textarea, #contact select, #contact button", width)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert form.locator('[name="email"]').evaluate("el => parseFloat(getComputedStyle(el).fontSize)") >= 16
    if width in [390, 1280]:
        page.locator("#contact").screenshot(path=str(root / f"mentoring-inquiry-{width}-{theme}.png"))

    for failure in ["failure", "offline"]:
        mode["value"] = failure
        submit_form(button)
        expect(page.locator("#inquiry-status")).to_contain_text("couldn't confirm")
        expect(form).to_be_visible()
        expect(page.locator("#inquiry-success")).to_be_hidden()
        expect(button).to_be_enabled()
        assert page.evaluate("document.activeElement.id") == "inquiry-status"
        assert submissions[-1] == mentoring_payload
        for name, value in mentoring_payload.items():
            expect(form.locator(f'[name="{name}"]')).to_have_value(value)

    mode["value"] = "pending"
    before = len(submissions)
    submit_form(button)
    expect(button).to_be_disabled()
    expect(form).to_have_attribute("aria-busy", "true")
    expect(page.locator("#inquiry-success")).to_be_hidden()
    expect(page.locator("#inquiry-status")).to_contain_text("Sending")
    page.evaluate("document.getElementById('inquiry-form').requestSubmit()")
    # Flush browser work while the first response remains held by the mock.
    page.wait_for_timeout(100)
    assert len(submissions) == before + 1
    assert len(held) == 1
    assert submissions[-1] == mentoring_payload
    held.pop().fulfill(status=200, content_type="application/json", body="{}")
    expect(form).to_be_hidden()
    expect(page.locator("#inquiry-success")).to_be_visible()
    assert page.evaluate("document.activeElement.id") == "inquiry-success"
    assert page.evaluate("history.state") is None
    print(f"PASS: mentoring {width}px {theme}: CTAs, required fields, validation, failure/retry, pending/double-submit, success/focus, layout")


def submit_form(button):
    # Keyboard activation avoids Playwright's frame-based click stability wait,
    # which can stall in the cached headless Chromium build.
    # Unlike form.submit(), Enter still runs native constraint validation.
    expect(button).to_be_visible()
    expect(button).to_be_enabled()
    button.press("Enter")


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
                submit_form(button)
                assert not submissions
                fill(page)
                form.locator('[name="email"]').fill("invalid-email")
                submit_form(button)
                assert not submissions
                form.locator('[name="email"]').fill(payload["email"])
                assert form.locator("input, textarea, select").count() == 6
                fits(page, "#contact input, #contact textarea, #contact select, #contact button", width)
                assert form.locator('[name="email"]').evaluate("el => parseFloat(getComputedStyle(el).fontSize)") >= 16
                if width in [390, 1280]:
                    page.locator("#contact").screenshot(path=str(root / f"inquiry-{width}-{theme}.png"))

                for failure in ["failure", "offline"]:
                    mode["value"] = failure
                    submit_form(button)
                    expect(page.locator("#inquiry-status")).to_contain_text("couldn't confirm")
                    expect(form).to_be_visible()
                    expect(page.locator("#inquiry-success")).to_be_hidden()
                    expect(button).to_be_enabled()
                    assert page.evaluate("document.activeElement.id") == "inquiry-status"
                    for name, value in payload.items():
                        expect(form.locator(f'[name="{name}"]')).to_have_value(value)

                mode["value"] = "pending"
                before = len(submissions)
                submit_form(button)
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
        submit_form(page.locator('#inquiry-form button'))
        expect(page.get_by_role("heading", name="Provider confirmation (test)")).to_be_visible()
        assert captured and "email=test%40example.com" in captured[0]
        print("PASS: no-JavaScript native POST; provider response mocked, not live delivery")
        context.close()

        for width in [320, 390, 768, 1280]:
            for theme in ["light", "dark"]:
                context = browser.new_context(viewport={"width": width, "height": 844}, color_scheme=theme, service_workers="block")
                submissions = []
                mode = {"value": "success"}
                held = []
                context.route("**/*", serve)
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                test_mentoring(page, width, theme, submissions, mode, held)
                assert not errors, errors
                context.close()

        context = browser.new_context(java_script_enabled=False, service_workers="block")
        context.route("**/*", serve)
        captured = []

        def native_mentoring_submit(route):
            assert route.request.method == "POST"
            captured.append(parse_qs(route.request.post_data))
            route.fulfill(content_type="text/html", body="<h1>Provider confirmation (test)</h1>")

        context.route(endpoint, native_mentoring_submit)
        page = context.new_page()
        page.goto("http://inquiry.test/mentoring/#contact")
        form = page.locator("#inquiry-form")
        expect(form).to_be_visible()
        expect(page.locator("#inquiry-success")).to_be_hidden()
        button = form.get_by_role("button", name="Send mentoring inquiry", exact=True)
        submit_form(button)
        assert not captured
        fill_mentoring(page)
        submit_form(button)
        expect(page.get_by_role("heading", name="Provider confirmation (test)")).to_be_visible()
        assert captured == [{name: [value] for name, value in mentoring_payload.items()}]
        print("PASS: mentoring no-JavaScript validation and native POST; provider response mocked, not live delivery")
        context.close()
    finally:
        browser.close()
