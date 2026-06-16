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

<!-- TODO: Replace with the real Letscast player embed once the episode is uploaded. -->
<div><script id="letscast-player-PLACEHOLDER" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/clickhouse-with-alexey-milovidov-and-austin-bonander/player.js?size=s"></script></div>

There's a particular kind of pressure that comes with maintaining software at the very bottom of someone else's stack. When your database is the thing that has to be fast, correct, and still standing after a decade of relentless production load, every language decision stops being a matter of taste and becomes a matter of risk. ClickHouse lives in exactly that spot: roughly 1.5 million lines of mostly C++, tens of millions of tests every single day, and an OLAP engine that people reach for precisely because it does not fall over.

So what happens when you start introducing Rust into a codebase like that? Not as a rewrite, not as a manifesto, but as a dependency you link into a C++ server with a CMake build that demands reproducibility and FIPS compliance? That's the messy, interesting reality we get into today, from the politics of allocation across an FFI boundary to the question of whether the hardest part is Rust the language or Rust the ecosystem.

My guests come at this from two very different altitudes. Alexey Milovidov is the creator of ClickHouse and its CTO. He started the project back in 2009 and has spent more than a decade thinking about performance, correctness, and what it actually takes to keep a database honest at scale. Austin Bonander is a Senior Software Engineer at ClickHouse and a long-time fixture of the Rust ecosystem as a maintainer of [sqlx](https://github.com/launchbadge/sqlx); he works close to the Rust tooling and the CLI. Together we talk about where Rust fits inside a C++ monolith, what it would take for Rust to earn a rewrite of core components, supply-chain and compliance headaches, and whether Rust is heading for the same accumulation of regrets that every "trendy" language eventually collects.

{{ codecrafters() }}

## Show Notes

### About ClickHouse

[ClickHouse](https://clickhouse.com/) is an open-source, column-oriented OLAP database management system built for real-time analytics over very large datasets. The first version was written in 2009, it went into production in 2012, and it was open-sourced in 2016. Today it's roughly 1.5 million lines of mostly C++, exercised by tens of millions of automated tests per day and a heavy regime of sanitizers and linters. ClickHouse is known for its raw query performance, and it powers analytics workloads at companies all over the world, from observability and logging platforms to large-scale data warehouses.

### About Alexey Milovidov

Alexey Milovidov is the creator of ClickHouse and the CTO of ClickHouse Inc. He started the project in 2009 while working at Yandex and has guided its evolution from an internal analytics tool into one of the most popular open-source databases in the world. He's spent his career obsessing over performance, correctness, and the kind of low-level engineering discipline it takes to keep a database trustworthy at scale.

### About Austin Bonander

Austin Bonander is a Senior Software Engineer at ClickHouse, where he works on Rust tooling and the ClickHouse CLI. He is a long-time member of the Rust community and a maintainer of [sqlx](https://github.com/launchbadge/sqlx), the async, pure-Rust SQL toolkit. Through that work he has thought deeply about database protocols, API ergonomics, and the long-term maintenance burden of widely used open-source libraries.

### Links From The Episode

- [ClickHouse](https://clickhouse.com/) - The open-source, column-oriented OLAP database at the center of the conversation
- [sqlx](https://github.com/launchbadge/sqlx) - The async, pure-Rust SQL toolkit Austin maintains
- [clickhouse-rs](https://github.com/ClickHouse/clickhouse-rs) - The Rust client for ClickHouse, supporting both its native TCP and HTTP interfaces
- [Corrosion](https://github.com/corrosion-rs/corrosion) - CMake integration for Rust, used to link Rust into a C++ build
- [Cargo](https://doc.rust-lang.org/cargo/) - Rust's build system and package manager, not designed for multi-language monorepos
- [CMake](https://cmake.org/) - The build system that dominates the ClickHouse server
- [delta-kernel-rs](https://github.com/delta-io/delta-kernel-rs) - A Rust implementation of the Delta Lake kernel, with a non-trivial dependency graph
- [ring](https://github.com/briansmith/ring) - A popular Rust crypto crate that is not FIPS compliant, pulled in transitively via object-store
- [object_store](https://docs.rs/object_store/latest/object_store/) - The Rust crate for working with object stores like S3
- [Poco](https://pocoproject.org/) - The C++ libraries used by the ClickHouse server, without HTTP/2 support
- [hyper](https://hyper.rs/) - A fast HTTP implementation for Rust
- [Hyrum's Law](https://www.hyrumslaw.com/) - With enough users, every observable behavior of your system will be depended on by somebody
- [Zig](https://ziglang.org/) - A systems language with a first-party, multi-language build system, raised as a contrast to Rust's tooling story
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/) - The dark arts of unsafe Rust and FFI
- [crates.io](https://crates.io/) - The Rust package registry, discussed in the context of supply-chain security and 2FA
- [Where's the next generation of senior Rust devs going to come from?](https://blog.magosomni.com/posts/2026-02-18-grimdark-gen-ai/) - The blog post on Gen AI, junior hiring, and the Rust talent pipeline that we discuss near the end
- [Rust in Production: Astral](/podcast/s04e03-astral/) - Another team building Rust tooling at the edges of a different ecosystem

### Official Links

- [ClickHouse Website](https://clickhouse.com/)
- [ClickHouse on GitHub](https://github.com/ClickHouse/ClickHouse)
- [Alexey Milovidov on GitHub](https://github.com/alexey-milovidov)
- [Austin Bonander on GitHub](https://github.com/abonander)
