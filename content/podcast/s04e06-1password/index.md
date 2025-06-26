+++
title = "1Password"
date = 2025-06-26
template = "episode.html"
draft = false
aliases = ["/p/s04e06"]
[extra]
guest = "Andrew Burkhart"
role = "Senior Rust Engineer"
season = "04"
episode = "06"
series = "Podcast"
+++

<div><script id="letscast-player-0e3cbed3" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/1password-with-andrew-burkhart/player.js?size=s"></script></div>

Handling secrets is extremely hard.
You have to keep them safe (obviously), while at the same time you need to integrate with a ton of different systems and always provide a great user-experience, because otherwise people will just find a way around your system.
When talking to peers, a lot of people mention 1Password as a company that nailed this balance.

In today's episode, I talk to Andrew about how 1Password uses Rust to build critical systems that must never fail, how Rust helps them handle secrets for millions of users, and the lessons they learned when adopting Rust in their stack.

{{ codecrafters() }}

## Show Notes

### About 1Password 

1Password is a password manager that helps users securely store and manage their passwords, credit card information, and other sensitive data. It provides a user-friendly interface and strong security features to protect users' secrets across multiple devices.

### About Andrew Burkhart 

Andrew is a Senior Rust Developer at 1Password in the Product Foundations org, on the Frameworks team and specifically on the Core Platform squad handling the asynchronous frameworks other developers use to build features (i.e. requests into the Rust core from the Native clients, data sync, etc.).
He specifically specialized in that synchronization process, getting data federated from cloud to clients to native apps and back.

### Links From The Episode

- [Backend for Frontend Pattern](https://samnewman.io/patterns/architectural/bff/) - Architectural pattern for creating dedicated backends for specific frontends
- [typeshare](https://github.com/1Password/typeshare) - Generate types for multiple languages from Rust code
- [zeroize](https://docs.rs/zeroize/latest/zeroize) - Securely zero memory of sensitive data structures
- [arboard](https://github.com/1Password/arboard) - Cross-platform clipboard manager written in Rust
- [passkey-rs](https://github.com/1password/passkey-rs) - Pure Rust implementation of the WebAuthn Passkey specification
- [WebAssembly (WASM)](https://webassembly.org/) - Binary instruction format for portable execution across platforms
- [tokio](https://tokio.rs/) - The de facto standard async runtime for Rust
- [Clippy](https://github.com/rust-lang/rust-clippy) - A collection of lints to catch common mistakes in Rust
- [cargo-deny](https://github.com/EmbarkStudios/cargo-deny) - Cargo plugin for linting dependencies, licenses, and security advisories
- [Nix](https://nixos.org/) - Purely functional package manager for reproducible builds
- [Nix Flakes](https://nixos.wiki/wiki/Flakes) - Experimental feature for hermetic, reproducible Nix builds
- [direnv](https://direnv.net/) - Load and unload environment variables based on current directory
- [Rust Community Guilds](https://www.rust-lang.org/governance/wgs) - Working groups and teams in the Rust community
- [axum](https://github.com/tokio-rs/axum) - Ergonomic and modular web framework built on tokio and tower
- [tower](https://github.com/tower-rs/tower) - Library for building robust networking clients and servers
- [tracing](https://github.com/tokio-rs/tracing) - Application-level tracing framework for async-aware diagnostics
- [rusqlite](https://github.com/rusqlite/rusqlite) - Ergonomic wrapper for SQLite in Rust
- [mockall](https://docs.rs/mockall/latest/mockall/) - Powerful mock object library for Rust
- [pretty_assertions](https://docs.rs/pretty_assertions/latest/pretty_assertions/) - Better assertion macros with colored diff output
- [neon](https://neon-rs.dev/) - Library for writing native Node.js modules in Rust
- [nom-supreme](https://docs.rs/nom-supreme/latest/nom_supreme/) - Parser combinator additions and utilities for nom
- [crane](https://github.com/ipetkov/crane) - Nix library for building Cargo projects
- [Rust in Production: Zed](/podcast/s03e01-zed/) - High-performance code editor built in Rust
- [tokio-console](https://github.com/tokio-rs/console) - Debugger for async Rust programs using tokio
- [Rust Atomics and Locks by Mara Bos](https://marabos.nl/atomics/) - Free online book about low-level concurrency in Rust
- [The Rust Programming Language (Brown University Edition)](https://rust-book.cs.brown.edu/) - Interactive version of the Rust Book with quizzes
- [Rustlings](https://github.com/rust-lang/rustlings) - Small exercises to get you used to reading and writing Rust code

### Official Links

- [1Password](https://1password.com/)
- [Andrew on GitHub](https://github.com/DrewBurkhart)
- [Andrew on LinkedIn](https://www.linkedin.com/in/andrewburkhartdev/)
