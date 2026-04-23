+++
title = "Helsing"
date = 2026-04-23
template = "episode.html"
draft = false
aliases = ["/p/s06e02"]
[extra]
guest = "Jon Gjengset"
role = "Principal Engineer"
season = "06"
episode = "02"
series = "Podcast"
+++

<div><script id="letscast-player-placeholder" src=""></script></div>

Jon Gjengset is one of the most recognizable names in the Rust community, the author of *Rust for Rustaceans*, a prolific live-streamer, and a long-time contributor to the Rust ecosystem. Today he works as a Principal Engineer at Helsing, a European defense company that has made Rust a foundational part of its engineering stack. Helsing builds safety-critical software for real-world defense applications, where correctness, performance, and reliability are non-negotiable. In this episode, Jon talks about what it means to build mission-critical systems in Rust, why Helsing bet on Rust from the start, and what lessons from his years of Rust education have shaped the way he writes and thinks about production code.

{{ codecrafters() }}

## Show Notes

### About Helsing

### About Jon Gjengset

### Links From The Episode

- [Helsing's Eurofighter Project](https://helsing.ai/newsroom/helsing-ai-selected-for-eurofighter-upgrade)
- [CA-1 Europa](https://helsing.ai/europa) - Helsing's Autonomous Uncrewed Combat Aerial Vehicle
- [Rust in Python cryptography](https://cryptography.io/en/latest/faq/#why-does-cryptography-require-rust) - Why the PyCA cryptography library rewrote its core in Rust for safety and performance
- [Clippy Documentation: Adding Lints](https://doc.rust-lang.org/stable/clippy/development/adding_lints.html) - How to write and add custom lints to Clippy, Rust's official linter
- [anyhow's .context()](https://docs.rs/anyhow/latest/anyhow/trait.Context.html) - Add human-readable context to any Rust error with a single method call
- [eyre](https://docs.rs/eyre/latest/eyre/) - A fork of `anyhow` with support for customizable, pluggable error report handlers
- [miette](https://docs.rs/miette/latest/miette/) - Fancy, diagnostic-rich error reporting for Rust with source snippets and labels
- [buffrs](https://github.com/helsing-ai/buffrs) - Helsing's Cargo-inspired package manager for Protocol Buffers, written in Rust
- [sguaba](https://github.com/helsing-ai/sguaba) - Helsing's Rust crate for type-safe coordinate system math, preventing unit and frame mix-ups at compile time
- [Sguaba: Type-safe spatial math in Rust](https://www.youtube.com/watch?v=kESBAiTYMoQ) - Jon's talk at Rust Amsterdam introducing the sguaba crate and the type-system techniques behind it
- [Apache Avro](https://avro.apache.org/) - A compact binary serialization format for streaming data, with a Rust implementation available via the `apache-avro` crate
- [pubgrub](https://docs.rs/pubgrub/latest/pubgrub/) - A Rust implementation of the PubGrub version-solving algorithm, as used in Cargo and uv
- [CRDTs](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type) - Conflict-free Replicated Data Types: data structures that can be merged across distributed nodes without conflicts
- [ADR (Architecture Decision Record)](https://adr.github.io/) - A lightweight way to document important architectural decisions and their context
- [DSON: JSON CRDT using delta-mutations for document stores](https://dl.acm.org/doi/10.14778/3510397.3510403) - The 2022 paper that was the basis for Helsing's CRDT implementation
- [dson](https://docs.rs/dson/latest/dson/) - Helsing's Rust implementation of the DSON JSON CRDT
- [Jon's Livestreams on YouTube](https://www.youtube.com/@jonhoo) - Deep-dive Rust coding sessions where Jon implements real-world libraries and systems from scratch
- [WebAssembly with Rust](https://rustwasm.github.io/docs/book/) - The official Rust and WebAssembly book, covering how to compile Rust to Wasm for use in browsers and beyond
- [Rust for Rustaceans](https://nostarch.com/rust-rustaceans) - Jon's book for intermediate Rust developers covering ownership, traits, async, and the finer points of the language
- [CVE-2024-24576: Cargo/tar supply chain vulnerability](https://blog.rust-lang.org/2023/08/03/cve-2022-46176.html) - A security issue in the `tar` crate that affected Cargo's package extraction
- [Wikipedia: Defence in Depth](https://en.wikipedia.org/wiki/Defence_in_depth_(non-military)#Information_security) - The security principle of using multiple independent layers of protection; Rust is one layer, not a silver bullet
- [SBOMs (Software Bill of Materials)](https://www.cisa.gov/sbom) - A machine-readable inventory of all components in a software artifact; Cargo's lock files make this tractable for Rust projects
- [Helsing: AI-assisted vetting of software packages](https://blog.helsing.ai/posts/ai-assisted-vetting-of-software-packages/) - Make it more efficient to review dependencies you take in
- [Bevy](https://bevy.org/) - A data-driven game engine built entirely in Rust, and a notable example of a large, complex Rust dependency
- [Tauri](https://tauri.app/) - A Rust-powered framework for building lightweight desktop and mobile apps with a web frontend, an alternative to Electron

### Official Links

- [Helsing Website](https://helsing.ai)
- [Helsing Tech Blog](https://blog.helsing.ai)
- [Helsing on GitHub](https://github.com/helsing-ai)
- [Helsing on LinkedIn](https://www.linkedin.com/company/helsing/)
- [Jon Gjengset's Website](https://thesquareplanet.com)
- [Jon Gjengset on GitHub](https://github.com/jonhoo)
- [Jon Gjengset on YouTube](https://www.youtube.com/@jonhoo)
- [Jon Gjengset on Bluesky](https://bsky.app/profile/jonhoo.eu)
- [Rust for Rustaceans](https://nostarch.com/rust-rustaceans)
