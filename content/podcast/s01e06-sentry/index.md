+++
title = "Sentry"
date = 2024-02-22
template = "episode.html"
draft = false
[extra]
guest = "Arpad Borsos"
role = "Senior Native Platform Engineer"
season = "01"
episode = "06"
series = "Podcast"
+++

In this episode, we talk to Arpad Borsos, Systems Software Engineer at Sentry,
about how they use Rust to build a modern error monitoring platform for
developers.

<!-- more -->

## Show Notes

How do you know your application is working as expected?
Do you have an overview of the errors and exceptions that occur
in production?

This is where Sentry comes in. Sentry is a modern error monitoring platform
that helps developers discover, triage, and prioritize errors in real-time.

In this episode, we talk to Arpad Borsos, Systems Software Engineer at Sentry,
about how they use Rust to build a modern error monitoring platform for
developers.

We touch on the challenges of building a high-performance, low-latency
platform for processing and analyzing large amounts of data (like stack traces
and source maps) in real-time. 
Arpad maintains the [`symbolic`](https://github.com/getsentry/symbolic) crate
for stack trace symbolication, which also gets used on the Sentry platform.


### About Sentry

Sentry provides application performance monitoring and error tracking software
for JavaScript, Python, Ruby, Go, and more. Their platform also supports session
replay, profiling, cron monitoring, code coverage, and more.


### About Arpad Borsos

Arpad Borsos loves to work on high-performance, low-latency systems and
maintains open source projects like the popular
[`rust-cache`](https://github.com/Swatinem/rust-cache) GitHub Action, which is
used by 20.000 GitHub repositories to cache Rust dependencies in CI. 

He is an expert in asynchronous programming and gave a talk titled [async fn from Editor to
Executable](https://www.youtube.com/watch?v=id38OaSPioA) at EuroRust 2023.


### Links From The Show

- [`symbolic` crate](https://github.com/getsentry/symbolic)
- [Tokio Async Runtime](https://tokio.rs/)

### Official Links

- [Sentry](https://sentry.io/)
- [Sentry on GitHub](https://github.com/getsentry/sentry)
- [Sentry Tech Blog](https://sentry.engineering/)
- [Arpad Borsos on LinkedIn](https://www.linkedin.com/in/swatinem/)
- [Arpad Borsos on GitHub (Swatinem)](https://github.com/Swatinem)
- [Personal Blog of Arpad](https://swatinem.de/)