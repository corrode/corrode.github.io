+++
title = "Arroyo"
date = 2024-01-25
template = "episode.html"
draft = false
aliases = ["/p/s01e04"]
[extra]
guest = "Micah Wylde"
role = "Co-Founder and CEO"
season = "01"
episode = "04"
series = "Podcast"
+++

<div><script id="letscast-player-9614e85c" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/rust-in-production-ep-4-arroyo-s-micah-wylde/player.js?size=s"></script></div>

In this episode, we talk to Micah Wylde, Co-founder and CEO of 
[Arroyo](https://www.arroyo.dev/), about how they simplified stream processing
for data engineers with Rust.

<!-- more -->

## Show Notes

{{ codecrafters() }}

Data engineers are responsible for building and maintaining the data
infrastructure of a company. They are the ones who make sure that data is
collected, stored, and processed in a way that is useful for the business.

This poses a lot of challenges, especially when it comes to processing data
in real-time. The data is often coming from different sources, in different
formats, and at different rates. Visibility into the pipelines is often
limited, and debugging is hard.

Arroyo is a new stream processing engine that aims to solve these problems. It
is built in Rust and uses WebAssembly to allow users to transform, filter,
aggregate, and join streams using SQL, with sub-second results. It scales to
millions of events per second.
The Arroyo Streaming Engine is available as open source software on GitHub.

In this episode, Micah Wylde, Founder of Arroyo, walks us through the
architecture of the Arroyo Streaming Engine and explains why Rust is the
best language for building data infrastructure.

### About Arroyo

Arroyo was founded in 2022 by Micah Wylde and is based in San Francisco, CA.
It is backed by [Y Combinator](https://www.ycombinator.com/) (YC W23).
The companies' mission is to accelerate the transition from batch-processing to
a streaming-first world.

### About Micah Wylde

Micah was previously tech lead for streaming compute at Splunk and Lyft, where
he built real-time data infra powering Lyft's dynamic pricing, ETA, and safety
features. He spends his time rock climbing, playing music, and bringing
real-time data to companies that can't hire a streaming infra team.

### Tools and Services Mentioned

- [Apache Flink](https://flink.apache.org/)
- [Tokio Discord](https://discord.gg/tokio)
- [Clippy](https://github.com/rust-lang/rust-clippy)
- [Zero to Production in Rust by Luca Palmieri](https://www.zero2prod.com/)
- [Apache DataFusion](https://github.com/apache/arrow-datafusion)
- [Axum web framework](https://github.com/tokio-rs/axum)
- [`sqlx` crate](https://github.com/launchbadge/sqlx)
- [`log` crate](https://github.com/rust-lang/log)
- [`tokio tracing` crate](https://github.com/tokio-rs/tracing)
- [wasmtime - A standalone runtime for WebAssembly](https://github.com/bytecodealliance/wasmtime)

### References To Other Episodes

- [Rust in Production Season 1 Episode 1: InfluxData](https://corrode.dev/podcast/s01e01-influxdata)

### Official Links

- [Arroyo Homepage](https://www.arroyo.dev/)
- [Arroyo Streaming Engine](https://github.com/ArroyoSystems/arroyo)
- [Blog Post: Rust Is The Best Language For Data Infra](https://www.arroyo.dev/blog/rust-for-data-infra)
- [Micah Wylde on LinkedIn](https://www.linkedin.com/in/wylde/)
- [Micah Wylde on GitHub](https://github.com/mwylde)
- [Micah Wylde's Personal Homepage](https://www.micahw.com/)
