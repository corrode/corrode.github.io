# Commercial inquiry flow

The homepage, services page, and workshops page use “Discuss Your Rust Migration”
to lead visitors to one form at `/services/#contact`. Visitors can describe their
project without choosing a meeting slot first. Navigation and newsletter signup
are unchanged.

## Form

The form asks for name, work email, company, current technology, project
description, and approximate timing. Timing includes “Within 3–6 months” and
“Not sure yet”. There are no team-size or engagement-model questions.

The submit button says “Send inquiry”. A successful response shows confirmation
and explains that Matthias will reply by email. While sending, the button is
disabled. Errors or a 20-second timeout keep the entered details available for
retry, with `hi@corrode.dev` as a fallback. Without JavaScript, the form submits
normally and the backend displays the result.

## Backend and privacy

Submissions still go to the existing endpoint:
`https://submit-form.com/r7PT0RxiL`. The planned backend migration has not happened
yet; removing provider branding from the form did not change where data is sent.
When migrating, update the form action, browser tests, and applicable privacy
disclosures.

The form asks visitors to omit confidential information and does not subscribe
them to the newsletter. Answers are not stored in URLs, browser history, or
local storage. No availability or pricing claims were added.

## Verification

Build with `zola build`, then run:

```sh
python3 scripts/test-inquiry.py public
python3 scripts/test-theme.py public
```

Both scripts accept `--browser` with a Chrome or Chromium executable path.
The inquiry tests cover CTA links, validation, success and error states,
duplicate submissions, and native submission without JavaScript. They check
320, 390, 768, and 1280px layouts in both themes and save screenshots under
`public/`.

All requests are intercepted locally. Before release, send an approved test
inquiry through the deployed site and confirm both the success message and
receipt in the intended inbox. Live delivery has not been verified.
