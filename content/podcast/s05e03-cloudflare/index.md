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

- [Pingora](https://github.com/cloudflare/pingora) - Cloudflare's open-source Rust framework for building network services
- [How we built Pingora](https://blog.cloudflare.com/how-we-built-pingora-the-proxy-that-connects-cloudflare-to-the-internet/) - Cloudflare blog post on Pingora's architecture
- [Open sourcing Pingora](https://blog.cloudflare.com/pingora-open-source/) - Announcement of Pingora's open source release
- [Pingora: saving compute 1% at a time](https://blog.cloudflare.com/pingora-saving-compute-1-percent-at-a-time/) - Kevin's blog post on performance optimization
- [nginx](https://nginx.org/) - The HTTP server and reverse proxy that Pingora replaced
- [nginx Proxy Server Setup](https://nginx.org/en/docs/beginners_guide.html#proxy) - A tutorial on configuring NGINX as a proxy server 
- [Tokio](https://tokio.rs/) - The async runtime powering Pingora
- [foundations](https://github.com/cloudflare/foundations) - Cloudflare's open-source Rust service foundation library
- [OpenResty](https://openresty.org/) - Nginx with Lua scripting support
- [Pingora](https://en.wikipedia.org/wiki/Pingora_Peak) - The actual mountain in Wyoming, U.S. where one of Cloudflare's product managers almost fell off
- [shellflip](https://github.com/cloudflare/shellflip)- Graceful process restarter in Rust, used by Pingora
- [Rain, Rustconf 2025 - Cancelling async Rust](https://sunshowers.io/posts/cancelling-async-rust/) - A talk by about async cancellation in Rust 
- [Bytes crate](https://docs.rs/bytes/latest/bytes/) - Efficient byte buffers for Rust
- [valuable](https://github.com/tokio-rs/valuable) - Lightweight serialization for tracing data
- [Dashmap](https://docs.rs/dashmap/latest/dashmap) - Concurrent HashMap for Rust
- [River Project](https://www.memorysafety.org/initiative/reverse-proxy/) - Blog post by Prossimo about building a reverse proxy in Rust
- [Pingap](https://crates.io/crates/pingap) -  A reverse proxy like nginx written in Rust, built on Pingora
- [Pull Request: Add Rustls compile time implementation to Pingora](https://github.com/cloudflare/pingora/pull/336) - by Harald Gutmann (hargut)
- [Pull Request: Add support for s2n-tls to Pingora](https://github.com/cloudflare/pingora/pull/675) - by  Bryan Gilbert (gilbertw1)
- [ClickHouse Rust client](https://clickhouse.com/docs/integrations/rust) - The official Rust client for connecting to ClickHouse, originally developed by Paul Loyd.

### Official Links

- [Cloudflare](https://www.cloudflare.com/)
- [Cloudflare Blog](https://blog.cloudflare.com/)
- [Pingora on GitHub](https://github.com/cloudflare/pingora)
- [Edward Wang's Blog Posts](https://blog.cloudflare.com/author/edward-h-wang/)
- [Kevin Guthrie's Blog Posts](https://blog.cloudflare.com/author/kevin-guthrie/)
