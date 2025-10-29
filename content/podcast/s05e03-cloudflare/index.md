+++
title = "Cloudflare"
date = 2025-10-30
template = "episode.html"
draft = false
aliases = ["/p/s05e03"]
[extra]
guest = "Edward Wang & Kevin Guthrie"
role = "Software Engineers"
season = "05"
episode = "03"
series = "Podcast"
+++

<div><script id="letscast-player-PLACEHOLDER" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/cloudflare-with-edward-wang-and-kevin-guthrie/player.js?size=s"></script></div>

How do you build a system that handles 90 million requests per second? That's the scale that Cloudflare operates at, processing roughly 25% of all internet traffic through their global network of 330+ edge locations.

In this episode, we talk to Kevin Guthrie and Edward Wang from Cloudflare about Pingora, their open-source Rust-based proxy that replaced nginx across their entire infrastructure. We'll find out why they chose Rust for mission-critical systems handling such massive scale, the technical challenges of replacing battle-tested infrastructure, and the lessons learned from "oxidizing" one of the internet's largest networks.

{{ codecrafters() }}

## Show Notes

### About Cloudflare

Cloudflare is a global network designed to make everything you connect to the Internet secure, private, fast, and reliable. Their network spans 330+ cities worldwide and handles approximately 25% of all internet traffic. Cloudflare provides a range of services including DDoS protection, CDN, DNS, and serverless computing—all built on infrastructure that processes billions of requests every day.

### About Kevin Guthrie

Kevin Guthrie is a Software Architect and Principal Distributed Systems Engineer at Cloudflare working on Pingora and the production services built upon it. He specializes in performance optimization at scale. Kevin has deep expertise in building high-performance systems and has contributed to open-source projects that power critical internet infrastructure.

### About Edward Wang

Edward Wang is a Systems Engineer at Cloudflare who has been instrumental in developing Pingora, Cloudflare's Rust-based HTTP proxy framework. He co-authored the announcement of Pingora's open source release. Edward's work focuses on performance optimization, security, and building developer-friendly APIs for network programming.

### Links From The Episode

- [Pingora](https://github.com/cloudflare/pingora) - Serving 90+ million requests per second (7e12 per day) at Cloudflare
- [How we built Pingora](https://blog.cloudflare.com/how-we-built-pingora-the-proxy-that-connects-cloudflare-to-the-internet/) - Cloudflare blog post on Pingora's architecture
- [Open sourcing Pingora](https://blog.cloudflare.com/pingora-open-source/) - Announcement of Pingora's open source release
- [Pingora: saving compute 1% at a time](https://blog.cloudflare.com/pingora-saving-compute-1-percent-at-a-time/) - Kevin's blog post on performance optimization
- [Pingora Peak](https://en.wikipedia.org/wiki/Pingora_Peak) - The actual mountain in Wyoming where a Cloudflare product manager almost fell off
- [nginx](https://nginx.org/) - The HTTP server and reverse proxy that Pingora replaced
- [OpenResty](https://openresty.org/) - Nginx with Lua scripting support
- [Oxy](https://blog.cloudflare.com/introducing-oxy/) - Another proxy developed at Cloudflare in Rust
- [Tokio](https://tokio.rs/) - The async runtime powering Pingora
- [foundations](https://github.com/cloudflare/foundations) - Cloudflare's foundational crate exposing Tokio internal metrics
- [shellflip](https://github.com/cloudflare/shellflip) - Graceful process restarter in Rust, used by Pingora
- [tableflip](https://github.com/cloudflare/tableflip) - Go library that inspired shellflip
- [bytes](https://github.com/tokio-rs/bytes) - Reference-counted byte buffers for Rust
- [valuable](https://github.com/tokio-rs/valuable) - Object introspection for logging and tracing
- [DashMap](https://github.com/xacrimon/dashmap) - Concurrent HashMap with minimal lock contention
- [mio](https://github.com/tokio-rs/mio) - Tokio's abstraction over epoll and async I/O interfaces
- [hyper](https://hyper.rs/) - Fast HTTP implementation for Rust
- [h2](https://github.com/hyperium/h2) - HTTP/2 implementation in Rust
- [Rustls](https://github.com/rustls/rustls) - Memory-safe TLS implementation
- [River](https://www.memorysafety.org/initiative/reverse-proxy/) - Prossimo-funded reverse proxy based on Pingora
- [Prossimo](https://www.memorysafety.org/about/) - Initiative for memory safety in critical internet infrastructure
- [Pingap](https://crates.io/crates/pingap) - Reverse proxy built on Pingora
- [ClickHouse Rust client](https://clickhouse.com/docs/integrations/rust) - Official Rust client by Paul Loyd
- [Rain: Cancelling Async Rust](https://sunshowers.io/posts/cancelling-async-rust/) - RustConf 2025 talk on async cancellation pitfalls
- [cargo audit](https://github.com/rustsec/rustsec) - Security vulnerability scanner for Rust dependencies
- [epoll](https://en.wikipedia.org/wiki/Epoll) - Linux async I/O event notification API
- [io_uring](https://en.wikipedia.org/wiki/Io_uring) - Modern Linux async I/O interface
- [Anycast](https://www.cloudflare.com/learning/cdn/glossary/anycast-network/) - Routing traffic to the closest point of presence
- [Ashley Williams](https://github.com/ashleygwilliams) - Rust developer who worked at Cloudflare
- [Yuchen Wu](https://github.com/eaufavor) - Early driver of Pingora development
- [Andrew Hauck](https://github.com/andrewhavck/) - Early driver of Pingora development
- [Noah Kennedy](https://github.com/Noah-Kennedy) - Tokio expert on the Pingora team
- [ThePrimeTime: Cloudflare Trie Hard](https://www.youtube.com/watch?v=xV4rLfpidIk&t=111s) - "It's not a millie, it's not a billie, it's a trillie"
- [Add Rustls to Pingora PR](https://github.com/cloudflare/pingora/pull/336) - by Harald Gutmann
- [Add s2n-tls to Pingora PR](https://github.com/cloudflare/pingora/pull/675) - by Bryan Gilbert
- [Cargo Book: Git Dependencies](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html#specifying-dependencies-from-git-repositories) - Using git repos as dependencies
- [Rust in Production: Oxide](/podcast/s03e03-oxide/) - Interview with Steve Klabnik 

### Official Links

- [Cloudflare](https://www.cloudflare.com/)
- [Cloudflare Blog](https://blog.cloudflare.com/)
- [Pingora on GitHub](https://github.com/cloudflare/pingora)
- [Edward Wang's Blog Posts](https://blog.cloudflare.com/author/edward-h-wang/)
- [Kevin Guthrie's Blog Posts](https://blog.cloudflare.com/author/kevin-guthrie/)

