+++
title = "Svix"
date = 2025-05-01
template = "episode.html"
draft = false
aliases = ["/p/s04e02"]
[extra]
guest = "Tom Hacohen"
role = "CEO"
season = "04"
episode = "02"
series = "Podcast"
+++

<div><script id="letscast-player-db5e5052" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/svix-with-tom-hacohen/player.js?size=s"></script></div>

We don't usually think much about Webhooks -- at least I don't.
It's just web requests after all, right? 
In reality, there is a lot of complexity behind routing webhook requests through the internet.

What if a webhook request gets lost?
How do you know it was received in the first place?
Can it be a security issue if a webhook gets handled twice? (Spoiler alert: yes)

<!-- more -->

Today I sit down with Tom from Svix to talk about what it takes to build an enterprise-ready 
webhook service. Of course it's written in Rust.

{{ codecrafters() }}

## Show Notes

### About Svix

Svix provides webhooks as a service.
They build a secure, reliable, and scalable webhook sending and receiving system using Rust. 
The company handles billions of webhooks a year, so they know a thing or two about the complexities involved.

### About Tom Hacohen 

Tom is an entrepreneur and open source maintainer from Tel-Aviv (Israel) and based in the US.
He's worked with people from all around the globe (excluding Antarctica).
Prior to Svix, he worked as an Engineer at Samsung's Open Source Group on the Enlightenment Foundation Libraries (EFL) 
that are used by the Samsung backed Tizen mobile operating system.

### Links From The Episode

- [Microsoft IIS](https://www.iis.net/) - Microsoft's HTTP server
- [Elixir](https://elixir-lang.org/) - General purpose programming language based on the Erlang VM
- [Go Spec: Exported Identifiers](https://go.dev/ref/spec#Exported_identifiers) - How to mark interface functions as public
- [Bob Nystrom: What Color is Your Function?](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/) - A good explanation of colored functions and the problems they introduce
- [jemallocator](https://github.com/tikv/jemallocator) - Use jemalloc as the global allocator in Rust
- [serde-json](https://github.com/serde-rs/json) - The go-to solution for parsing JSON in Rust
- [serde](https://serde.rs/) - High-level serilization and deserialization interface crate
- [axum](https://docs.rs/axum/latest/axum/) - The defacto async web server crate
- [seaorm](https://www.sea-ql.org/SeaORM/) - SeaORM is a relational ORM to help you build web services in Rust
- [redis-rs](https://github.com/redis-rs/redis-rs) - Redis library for rust
- [aide](https://docs.rs/aide/latest/aide/) - OpenAPI generation from axum code
- [dropshot](https://github.com/oxidecomputer/dropshot) - Oxide API framework that generates OpenAPI spec
- [KSUID](https://github.com/svix/rust-ksuid) - A pure-Rust K sorted UID implementation
- [omniqueue](https://github.com/svix/omniqueue-rs) - A queue abstraction layer for Rust
- [Python GIL](https://wiki.python.org/moin/GlobalInterpreterLock) - The Global Interpreter Lock Python wiki entry
- [Svix Blog: Robust APIs Through OpenAPI Generation](https://www.svix.com/blog/robust-apis-through-openapi-generation/) - How to build stable APIs through schema generation and reviews

### Official Links

- [Svix](https://www.svix.com/)
- [Tom Hacohen's Blog](https://stosb.com/)
- [Tom on GitHub](https://github.com/tasn/)
- [Tom on Mastodon](https://mastodon.social/@tasn)
