# Commercial inquiry flow

## CTA audit and changes

Rebased onto upstream `master` at `0df30b8a` (PR #146). Upstream already refocused the services copy on migrations, adopted the requested CTA label, and removed the quiz and Tally embed. Those changes are preserved, including the new headline, testimonial, and Assess / Migrate / Enable sections. The remaining changes unify the destinations and add the short inquiry flow; they do not restore the old services copy.

| Page / location | Previous action | Updated action |
| --- | --- | --- |
| Homepage hero | Book a Free Strategy Call → embedded calendar | Discuss Your Rust Migration → `/services/#contact` |
| Homepage introduction | Let's talk → embedded calendar | Discuss Your Rust Migration → `/services/#contact` |
| Homepage closing section | Free 30-minute strategy call, calendar, services link | Requested supporting copy and primary CTA → `/services/#contact`; contact alternatives retained |
| Services introduction and closing CTAs | Discuss Your Rust Migration → Cal.com modal; email alternative | Same CTA label → `#contact`; email fallback retained |
| Services inquiry | Calendar booking only; upstream removed the former ten-step quiz | One form with six visible fields, after the engagement-process section |
| Services availability FAQ | General accommodation language | Ask for project timing without implying availability |
| Workshops closing section | Book a workshop → services page | Primary CTA → `/services/#contact`; workshop context retained |
| Shared navigation | Consulting styled as a competing CTA | Consulting retained as an ordinary navigation link |

Service discovery links, workshop materials, PDF downloads, personal mentorship links, social links, and footer navigation remain secondary destinations. The newsletter remains separate and unchanged. The shared navigation styling change appears site-wide; the commercial content changes affect `/`, `/services/`, and `/workshops/`.

## Infrastructure and privacy

The existing Formspark endpoint, `https://submit-form.com/r7PT0RxiL`, remains the submission backend. There is one inquiry form on the services page, not one per service. Cal.com embeds were removed from these pages to avoid requiring a meeting slot before an initial inquiry; calendar pages and other existing booking routes were not changed. Upstream already removed the unused Tally embed script from services. The old shared quiz assets remain because migration-guide pages still use them.

The form collects name, work email, company, current stack, project description, and approximate timing. Role, team size, Rust experience, and engagement-model questions are omitted. Timing includes a 3–6 month option as well as later and uncertain horizons. No availability, pricing, or engagement commitment has been added.

The former services quiz had no consent checkbox or privacy notice. The replacement does not remove any consent gate. The copy explains that details are used to respond to the inquiry, asks visitors to omit confidential information, and states that the form does not subscribe them to the newsletter. At the owner's request, provider-specific wording and the provider privacy link were removed in preparation for a backend migration. The current endpoint still sends submissions to Formspark until that migration is implemented; applicable privacy disclosures should reflect the actual backend. Answers are not put in URLs, browser history, or local storage. The existing newsletter flow is unchanged. This is not a legal review of the site's privacy disclosures or the owner's provider configuration.

## Submission behavior and verification

- Successful HTTP responses hide the form and focus an explicit confirmation: “Thank you. Your inquiry has been sent.” The next step is an email reply, not a promised strategy deliverable.
- While pending, the submit button is disabled and repeated submissions are ignored.
- HTTP errors, network errors, and a 20-second timeout retain entered values and show a retry/email fallback rather than claiming success. No automatic retry occurs, because delivery can be uncertain after a lost response.
- Native required-field and email validation apply. Without JavaScript, the form posts to the same provider and uses the provider's response page.
- Visible labels, autocomplete, 16px inputs, minimum 48px control heights, live status text, and focus management support mobile and keyboard use.

Validation performed:

- `zola build` passed.
- `scripts/test-inquiry.py public --browser <installed Chromium executable>` passed at 320, 390, 768, and 1280px in light and dark themes: CTA routing, required/email validation, HTTP/network failures and retry, pending state, duplicate-submit protection, JSON payload, success visibility/focus, and control bounds. Native POST without JavaScript was also tested.
- Mobile light/dark and desktop screenshots were reviewed. Screenshots are generated under the ignored `public/` directory.
- `scripts/test-theme.py` passed all 24 cases and 96 toggles.

All browser requests were intercepted locally. The tests simulate provider responses; they do **not** verify the live endpoint, provider-side spam/origin rules, notification routing, inbox delivery, or the provider's actual no-JavaScript confirmation page. Before release, submit an owner-approved test inquiry through the deployed site and confirm both the success state and receipt in the intended inbox. No live test inquiry was sent during this change.
