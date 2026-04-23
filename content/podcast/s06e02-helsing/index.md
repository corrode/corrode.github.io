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
- [CA-1 Eurpoa](https://helsing.ai/europa) - 
- [Rust in Python cryptography](https://cryptography.io/en/latest/faq/#why-does-cryptography-require-rust) - Rust being used in a Python library
- [Clippy Documentation: Adding Lints](https://doc.rust-lang.org/stable/clippy/development/adding_lints.html) - How to add custom lints to (your own fork of) clippy
- [anyhow's .context()](https://docs.rs/anyhow/latest/anyhow/trait.Context.html) - Use it everywhere, it's very very helpful
- [eyre](https://docs.rs/eyre/latest/eyre/) - Fork of anyhow with customizable error reports
- [miette](https://docs.rs/miette/latest/miette/) - Fancy errors for your Rust projects
- [buffrs](https://github.com/helsing-ai/buffrs) - `cargo` for Protobuf
- [sguaba](https://github.com/helsing-ai/sguaba) - Type-safe coordinate system math crate
- [Sguaba: Type-safe spatial math in Rust](https://www.youtube.com/watch?v=kESBAiTYMoQ) - Jon's introduction presentation at Rust Amsterdam
- [Apache Avro](https://avro.apache.org/) - Serialization format for streaming data
- [pubgrub](https://docs.rs/pubgrub/latest/pubgrub/) - Version constraint solver with good errors
- [CRDTs](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type) - Conflict-free replicated data type, Google Docs but data
- ADR
- [DSON: JSON CRDT using delta-mutations for document stores](https://dl.acm.org/doi/10.14778/3510397.3510403) - The 2022 paper that was the basis for Helsing's CRDT implementation
- [dson](https://docs.rs/dson/latest/dson/) - The implementation in Rust
- Jon's Livestreams - Started during his AWS employment, and still continues (check die dates, hat das während AWS angefangen?)
- WebAssembly in Rust - A cool technology and a useful skill to have as a Rust developer
- Rust for Rusteceans - 
- Cargo exploit based on tar crate
- [Wikipedia: Defence in Depth](https://en.wikipedia.org/wiki/Defence_in_depth_(non-military)#Information_security) - There is no silver bullet, you need layers
- SBOMs - Keep track of all the dependencies that went into an artifact
- [Helsing: AI-assisted vetting of software packages](https://blog.helsing.ai/posts/ai-assisted-vetting-of-software-packages/) - Make it more efficient to review dependencies you take in
- [Bevy](https://bevy.org/) - One big dependency, a game engine written in Rust
- [Tauri](https://tauri.app/) - Another big one, packaging Web Applications as desktop and mobile apps with Rust

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
