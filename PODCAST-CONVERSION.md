# Podcast services mentions

## Editorial approach

Reviewed the written summaries and show notes of all 51 episodes, not their audio.
Selected 15 with concrete connections to integration, production architecture,
team adoption, or maintainable Rust. Each uses one topic-specific question and a
shared services mention in the existing **About corrode** footer, after all show
notes and official links. It replaces, rather than supplements, the generic pitch.
No banners, popups, new styles, guest endorsements, or changes to descriptions,
guest biographies, sponsor placements, or technical resource links.

The remaining episodes retain their existing footer. Teasers, finales, holidays,
and governance-led episodes were not prioritized. Narrow hardware and certification
stories need a matching specialist offer rather than a generic migration pitch.
The Roc episode's move away from Rust is not framed as a reason to adopt Rust.
C integration stories are not mislabeled as C++ migrations.

## Modified episodes

All source paths below are relative to `content/podcast/` and end in `/index.md`.

| Episode | Source directory | Context supporting the mention |
| --- | --- | --- |
| S01E06 Sentry | `s01e06-sentry` | Performance-critical components; notes link PyO3/maturin. Interoperability, not a claimed Python application rewrite. |
| S03E04 GitButler | `s03e04-gitbutler` | Notes cover module organization, Clippy, and `thiserror` versus `anyhow`. |
| S03E07 Brave | `s03e07-brave` | Rust ad-blocking inside Chromium; CXX and build-system links. |
| S03E08 Volvo | `s03e08-volvo` | Embedded production use and building an internal Rust ecosystem. |
| S04E01 Microsoft | `s04e01-microsoft` | Adoption at scale, C++ interoperability, and toolchain integration. |
| S04E03 Astral | `s04e03-astral` | Python developer tools written in Rust, not migrating Python applications. |
| S04E05 Tembo | `s04e05-tembo` | Queue architecture and Rust/Postgres integration. |
| S04E06 1Password | `s04e06-1password` | Native clients connected to a shared Rust core. |
| S04E07 KSAT | `s04e07-ksat` | Continuous data processing; notes include incremental replacement and observability. |
| S05E03 Cloudflare | `s05e03-cloudflare` | Pingora, async cancellation, Tokio metrics, and graceful restarts. |
| S05E08 Radar | `s05e08-radar` | Simplifying data infrastructure with a Rust service backed by RocksDB. |
| S06E01 Cloudsmith | `s06e01-cloudsmith` | Incremental Rust extensions in a Python/Django monolith, without a full rewrite. |
| S06E02 Helsing | `s06e02-helsing` | Notes cover contextual errors, type-safe math, custom lints, and architecture decisions. |
| S06E06 ClickHouse | `s06e06-clickhouse` | Rust components in a mostly C++ server, including CMake integration. |
| S06E07 Rising Academies | `s06e07-rising-academies` | Engineering-management decisions about adopting Rust for a new backend. |

## Reusable copy

The shared copy lives in `templates/snippets/podcast-services.html`:

> [Episode-specific question] I'm Matthias, the host of Rust in Production.
> I help engineering teams plan migrations, review architecture, and build the
> expertise to maintain Rust in production. [Find out how I can help].

To opt in another episode, add a short `services_prompt` under its existing
`[extra]` table. Keep it tied to the actual episode, not merely a language name
in the resource list. The template supplies the services link and episode tag.

Optional shorter copy for externally hosted episode descriptions:

> Considering Rust for an existing system? I help engineering teams plan migrations,
> review architecture, and build the expertise to maintain Rust in production.
> [Rust consulting with Matthias Endler](https://corrode.dev/services/?utm_source=rust-in-production&utm_medium=podcast&utm_campaign=services&utm_content=s06e01-cloudsmith)

Use the actual episode slug in `utm_content`. Place it after editorial notes and
label it as a host/services note; never put it in a guest quotation. This repository
change does **not** update the external LetsCast feed, Apple Podcasts, Spotify, or
YouTube descriptions. Leave those untouched unless separately publishing the note.

## Attribution and limits

Links carry these public, non-identifying labels:

- `utm_source=rust-in-production`
- `utm_medium=podcast`
- `utm_campaign=services`
- `utm_content=<episode-directory-slug>`

These are ordinary HTML links. No attribution JavaScript, cookies, or browser
storage are added. Tags remain in the services-page URL but are **not forwarded
to Cal.com or email links**. Bookings and email drafts behave exactly as before.

The deployed `https://oxitrack.corrode.dev/count.js`, inspected during this work,
records **pathname**, dwell time, and external referrer origin. It ignores query
strings and same-origin referrers; it counts only after its minimum active-time
threshold (currently 20 seconds). Therefore it can report episode and services
page traffic, but **cannot report podcast-to-services clicks, UTM campaign traffic,
or a joined visitor conversion funnel**. Tags do not magically add that support.
No unsupported tracking API calls or extra analytics vendor were added.

The services page no longer includes the quiz following upstream's migration-focused
redesign (#146). No quiz attribution or form-submission changes are needed.

For now, ask “How did you hear about corrode?” during qualification and record
podcast referrals manually. Use episode traffic for context, not as an exact
listener-conversion denominator: website visits are not audio listens.
Classify inquiries by actual fit (existing stack, Rust experience, team size,
and project needs), not by clicks alone.

The tags label the route for possible future campaign reporting; they do not
provide automated inquiry attribution with the current setup. If precise CTA
traffic counts become necessary, add explicit campaign support to OxiTrack as a
separate change. Query strings may exist in server logs, but this repository does
not establish their availability or retention.

## Validation

```sh
zola build
python3 scripts/test-podcast-services.py public
```

The browser test requires Python Playwright and its Chromium. Use `--browser`
with an installed Chromium-based executable if needed. It checks all 15 rendered
links, untouched generic footers, mobile overflow, navigation to services, and
unchanged booking and email links after a tagged arrival.
All external requests are blocked; no bookings or emails are sent.
Use `--screenshot public/podcast-footer.png` to capture desktop/mobile footers.
