+++
title = "Cloudflare"
date = 2025-11-06
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
- [nginx](https://nginx.org/) - The HTTP server and reverse proxy that Pingora replaced
- [Tokio](https://tokio.rs/) - The async runtime powering Pingora
- [OpenResty](https://openresty.org/) - Nginx with Lua scripting support
- [rust-tracing](https://github.com/tokio-rs/tracing) - Application-level tracing for Rust
- [tokio-tracing](https://tokio.rs/tokio/topics/tracing) - Tokio's tracing integration
- [valuable](https://github.com/tokio-rs/valuable) - Lightweight serialization for tracing data
- [thingbuf](https://github.com/hawkw/thingbuf) - Lock-free circular queue by Eliza Weisman
- [River](https://github.com/memorysafety/river) - a Reverse Proxy Application based on the pingora library from Cloudflare by James Munns
- [Pingap](https://github.com/vicanso/pingap) - Community project built on Pingora
- [foundations](https://github.com/cloudflare/foundations) - Cloudflare's open-source Rust service foundation library
- [trie-hard](https://github.com/cloudflare/trie-hard) - Fast trie implementation for routing optimization
- [h2](https://github.com/hyperium/h2) - HTTP/2 implementation in Rust
- [Serde](https://serde.rs/) - Serialization framework for Rust
- [Tonic](https://github.com/hyperium/tonic) - gRPC framework for Rust
- [Advent of Code](https://adventofcode.com/) - Programming puzzles used for learning Rust
- [The Rust Book](https://doc.rust-lang.org/book/) - Official Rust programming language book
- [How we built Pingora](https://blog.cloudflare.com/how-we-built-pingora-the-proxy-that-connects-cloudflare-to-the-internet/) - Cloudflare blog post on Pingora's architecture
- [Open sourcing Pingora](https://blog.cloudflare.com/pingora-open-source/) - Announcement of Pingora's open source release
- [Pingora: saving compute 1% at a time](https://blog.cloudflare.com/pingora-saving-compute-1-percent-at-a-time/) - Kevin's blog post on performance optimization

### Official Links

- [Cloudflare](https://www.cloudflare.com/)
- [Cloudflare Blog](https://blog.cloudflare.com/)
- [Pingora on GitHub](https://github.com/cloudflare/pingora)
- [Edward Wang's Blog Posts](https://blog.cloudflare.com/author/edward-h-wang/)
- [Kevin Guthrie's Blog Posts](https://blog.cloudflare.com/author/kevin-guthrie/)
