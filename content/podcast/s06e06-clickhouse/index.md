+++
title = "ClickHouse"
date = 2026-06-18
template = "episode.html"
draft = false
aliases = ["/p/s06e06"]
[extra]
guest = "Alexey Milovidov and Austin Bonander"
role = "CTO and Senior Software Engineer"
season = "06"
episode = "06"
series = "Podcast"
+++

<div><script id="letscast-player-9e435c01" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/clickhouse-with-alexey-milovidov-and-austin-bonander/player.js?size=s"></script></div>

There's a particular kind of pressure that comes with maintaining software at the very bottom of someone else's stack. ClickHouse lives in exactly that spot: roughly 1.5 million lines of mostly C++ and tens of millions of tests every single day.

So what happens when you start introducing Rust into a codebase like that? Not as a rewrite, but linked into a C++ server with a CMake build process that has to be reproducible and FIPS compliant? In today's episode, we get into the messy, interesting reality. We talk about the question of whether the hardest part is Rust the language or Rust the ecosystem.

My guests come at this from two very different angles. Alexey Milovidov is the creator of ClickHouse and its CTO. He started the project back in 2009 and has spent decades thinking about performance, correctness, and what it actually takes to build a production database. Austin Bonander is a Senior Software Engineer at ClickHouse and a renowned open-source maintainer of [sqlx](https://github.com/launchbadge/sqlx). He works close to the Rust tooling and the CLI. Together we talk about where Rust fits inside a C++ monolith, what it would take for Rust to earn a rewrite of core components, supply-chain and compliance headaches, and whether Rust is heading for the same accumulation of regrets that every "trendy" language eventually accumulates.

{{ codecrafters() }}

## Show Notes

### About ClickHouse

[ClickHouse](https://clickhouse.com/) is an open-source, column-oriented OLAP database management system built for real-time analytics over very large datasets. The first version was written in 2009, it went into production in 2012, and it was open-sourced in 2016. Today it's roughly 1.5 million lines of mostly C++, exercised by tens of millions of automated tests per day and a heavy regime of sanitizers and linters. ClickHouse is known for its raw query performance, and it powers analytics workloads at companies all over the world, from observability and logging platforms to large-scale data warehouses.

### About Alexey Milovidov

Alexey Milovidov is the creator of ClickHouse and the CTO of ClickHouse Inc. He started the project in 2009 while working at Yandex and has guided its evolution from an internal analytics tool into one of the most popular open-source databases in the world. He's spent his career obsessing over performance, correctness, and the kind of low-level engineering discipline it takes to keep a database trustworthy at scale.

### About Austin Bonander

Austin Bonander is a Senior Software Engineer at ClickHouse, where he works on Rust tooling and the ClickHouse CLI. He is a long-time member of the Rust community and a maintainer of [sqlx](https://github.com/launchbadge/sqlx), the async, pure-Rust SQL toolkit. Through that work he has thought deeply about database protocols, API ergonomics, and the long-term maintenance burden of widely used open-source libraries.

### Links From The Episode

- [OLAP](https://en.wikipedia.org/wiki/Online_analytical_processing) - A type of database used for analytics, not storing relational data
- [sqlx](https://github.com/launchbadge/sqlx) - The async, pure-Rust SQL toolkit Austin maintains
- [Official /r/rust "Who's Hiring" thread for job-seekers and job-offerers](https://www.reddit.com/r/rust/search?sort=new&restrict_sr=on&q=flair%3A%F0%9F%92%BC%2Bjobs%2Bmegathread) - Where Austin found the Clickhouse job
- [Clickhouse's C++ & Rust Journey](https://www.youtube.com/watch?v=cIXKsb0FYpc) - Alexeys talk at P99 CONF 2025
- [No-Panic Rust: A Nice Technique for Systems Programming](https://blog.reverberate.org/2025/02/03/no-panic-rust.html) - Using linker checks to guarantee no panic calls in Rust code
- [delta-kernel-rs](https://github.com/delta-io/delta-kernel-rs) - A Rust implementation of the Delta Lake kernel, with a non-trivial dependency graph
- [ring](https://github.com/briansmith/ring) - BoringSSL crypto code packaged as a Rust crate
- [H3](https://h3geo.org/) - Uber’s Geo Hashing using hexagons, currently used in ClickHouse
- [H3O](https://docs.rs/h3o/latest/h3o/) - The same H3 Geo Hashing algorithm implemented in Rust, with better performance
- [stdx](https://github.com/brson/stdx) - An attempt at creating an extended standard library with commonly used crates
- [Hyrum's Law](https://www.hyrumslaw.com/) - With enough users, every observable behavior of your system will be depended on by somebody
- [Corrosion](https://github.com/corrosion-rs/corrosion) - CMake integration for Rust, used to link Rust into a C++ build
- [Cargo](https://doc.rust-lang.org/cargo/) - Rust's build system and package manager, not designed for multi-language monorepos
- [CMake](https://cmake.org/) - The build system that dominates the ClickHouse server
- [Poco](https://pocoproject.org/) - The C++ libraries used by the ClickHouse server, without HTTP/2 support
- [hyper](https://hyper.rs/) - A fast HTTP implementation for Rust

### Official Links

- [ClickHouse Website](https://clickhouse.com/)
- [ClickHouse on GitHub](https://github.com/ClickHouse/ClickHouse)
- [clickhouse-rs](https://github.com/ClickHouse/clickhouse-rs) - The Rust client for ClickHouse, supporting both its native TCP and HTTP interfaces
- [Alexey Milovidov on GitHub](https://github.com/alexey-milovidov)
- [Austin Bonander on GitHub](https://github.com/abonander)
