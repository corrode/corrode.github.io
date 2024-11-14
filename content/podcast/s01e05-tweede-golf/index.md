+++
title = "Tweede Golf"
date = 2024-02-08
template = "episode.html"
draft = false
aliases = ["/p/s01e05"]
[extra]
guest = "Folkert de Vries"
role = "Systems Software Engineer"
season = "01"
episode = "05"
series = "Podcast"
+++

<div><script id="letscast-player-b30f560a" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/rust-in-production-ep-5-tweede-golf-s-folkert-de-vries/player.js?size=s"></script></div>

In this episode, we talk to Folkert de Vries, Systems Software Engineer at Tweede Golf, about how they use Rust to modernize the NTP protocol and build a new generation of time synchronization services.

<!-- more -->

## Show Notes

The Network Time Protocol (NTP) is a cornerstone of the internet.
It provides accurate time synchronization on millions of devices, but its
C-based implementation, which dates back to the
1980s, is showing its age. In this episode, we talk to Folkert de Vries, Systems
Software Engineer at Tweede Golf, about their work on reimplementing NTP in Rust
as part of [Project Pendulum](https://tweedegolf.nl/en/pendulum).


[`ntpd-rs`](https://github.com/pendulum-project/ntpd-rs) is an open-source
implementation of the Network Time Protocol, completely written in Rust with the
goal of creating a modern, memory-safe implementation of the NTP protocol.

Funding for the project came from the [Internet Security Research
Group](https://www.abetterinternet.org/) and the [Sovereign Tech
Fund](https://www.sovereigntechfund.de/).

### About Tweede Golf

Tweede Golf is a Dutch software consultancy that specializes in safe and
privacy-friendly software. They work on projects that are critical for creating
a safe internet infrastructure, protecting citizens' privacy, and securing
connected devices with Embedded Rust.

Tweede Golf is also an organizing partner of [RustNL](https://2024.rustnl.org/), a
conference about the Rust programming language, which takes place in the
Netherlands.

### About Folkert de Vries

Folkert is a Systems Software Engineer at Tweede Golf, where he works on
low-level protocols that ensure the safety and security of the internet
and devices connected to it. He is an open source maintainer and polyglot,
working with and extending languages as diverse as Rust, Elm, and Roc.

### Links From The Episode (In Chronological Order)

- [The Roc programming language](https://www.roc-lang.org/)
- [`ntpd-rs` - Implementation of the Network Time Protocol in Rust](https://github.com/pendulum-project/ntpd-rs)
- [Network Time Protocol (NTP)](https://en.wikipedia.org/wiki/Network_Time_Protocol)
- [Precision Time Protocol (PTP)](https://en.wikipedia.org/wiki/Precision_Time_Protocol)
- [Simple Network Time Protocol (SNTP)](https://en.wikipedia.org/wiki/Network_Time_Protocol#SNTP)
- [`sudo-rs` - A memory safe implementation of sudo and su](https://github.com/memorysafety/sudo-rs)
- [Fuzzing in Rust with `cargo-fuzz`](https://github.com/rust-fuzz/cargo-fuzz)
- [Tokio Async Runtime](https://tokio.rs/)
- [Internet Security Research Group](https://www.abetterinternet.org/)
- [Sovereign Tech Fund](https://www.sovereigntechfund.de/)

### Official Links

- [Tweede Golf](https://tweedegolf.nl/)
- [Tweede Golf - About Folkert de Vries](https://tweedegolf.nl/en/about/21/folkert)
- [Folkert de Vries on GitHub](https://github.com/folkertdev)
- [Folkert de Vries on Twitter](https://twitter.com/flokkievids)
- [Folkert de Vries on LinkedIn](https://www.linkedin.com/in/folkert-de-vries-24ab691b7/)
- [Prossimo Project](https://www.memorysafety.org/)
- [Project Pendulum](https://tweedegolf.nl/en/pendulum)
- [RustNL Conference, May 7 & 8, 2024](https://2024.rustnl.org/)
