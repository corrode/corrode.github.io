+++
title = "Zed"
date = 2024-10-17
template = "episode.html"
draft = false
aliases = ["/p/s03e01"]
[extra]
guest = "Conrad Irwin"
role = "Open Source Developer"
season = "03"
episode = "01"
series = "Podcast"
+++

<div><script id="letscast-player-b1a26f96" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/zed-with-conrad-irwin/player.js?size=s"></script></div>

[Next to writing their own operating system](/podcast/s02e07-system76/), another dream shared by many developers is building their own text editor. Conrad Irwin, a software engineer at Zed, is doing just that. Zed is a fully extensible, open-source text editor written entirely in Rust. It's fast, lightweight, and comes with excellent language support out of the box.

In the first episode of the third season, I sit down with Conrad to discuss Zed's mission to build a next-generation text editor and why it was necessary to rebuild the very foundation of text editing software from scratch to achieve their goals.

<!-- more -->

## Show Notes

{{ codecrafters() }}

### About Zed Industries

Zed isn't afraid of daunting tasks. Not only have they built a text editor from scratch, but they've also developed their own GUI toolkit, implemented advanced parsing techniques like tree-sitter, and integrated multi-user collaboration features directly into the editor. Zed is a text editor built for the future, with meticulous attention to detail and a focus on exceptional performance.

### About Conrad Irwin

Before joining Zed, Conrad worked on Superhuman, an email client renowned for its speed and efficiency. He is a seasoned developer with a deep understanding of performance optimization and building fast, reliable software. Conrad is passionate about open-source software and is a strong advocate for Rust. He's also an excellent pair-programming partner and invites people to join him while working on Zed.

### Links From The Episode (In Chronological Order)

- [Superhuman](https://superhuman.com/) - High-performance email client known for its speed and efficiency
- [Visual Studio Code](https://code.visualstudio.com/) - Popular, extensible code editor
- [Neovim](https://neovim.io/) - Vim-based text editor focused on extensibility and usability
- [gpui crate](https://github.com/zed-industries/zed/blob/main/crates/gpui) - Zed's custom GUI toolkit for building fast, native user interfaces
- [Leptos](https://leptos.dev/) - Rust framework for building reactive web applications
- [Dioxus](https://dioxuslabs.com/) - Rust library for building cross-platform user interfaces
- [Tokio](https://tokio.rs/) - Asynchronous runtime for Rust, powering many network applications
- [async-std](https://async.rs/) - Asynchronous version of the Rust standard library
- [smol](https://github.com/smol-rs/smol) - Small and fast async runtime for Rust
- [Glommio](https://github.com/DataDog/glommio) - Thread-per-core Rust async framework with a Linux-specific runtime
- [isahc](https://crates.io/crates/isahc) - HTTP client library that supports multiple async runtimes
- [`AsyncRead`, `AsyncWrite` traits](https://github.com/rust-lang/wg-async/issues/23)
- [Zed Editor YouTube channel](https://www.youtube.com/@zeddotdev) - Official channel for Zed editor tutorials and updates
- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) - Parser generator tool and incremental parsing library
- [Semgrep](https://github.com/semgrep/semgrep) - Static analysis tool for finding and preventing bugs
- [Zed release changelogs](https://zed.dev/releases/stable) - Official changelog for Zed editor releases
- [matklad's blog post: "Flat Is Better Than Nested"](https://matklad.github.io/2021/08/22/large-rust-workspaces.html) - Discusses organizing large Rust projects with a flat structure
- [rust-analyzer](https://rust-analyzer.github.io/) - Advanced language server for Rust, providing IDE-like features
- [Protobuf Rust crate](https://github.com/tokio-rs/prost) - Protocol Buffers implementation for Rust
- [Postcard](https://github.com/jamesmunns/postcard) - Compact serialization format for Rust, designed for resource-constrained systems
- [CBOR](https://crates.io/crates/cbor) - Concise Binary Object Representation, a data format similar to JSON but more compact
- [MessagePack](https://github.com/3Hren/msgpack-rust) - Efficient binary serialization format
- [RON (Rusty Object Notation)](https://github.com/ron-rs/ron) - Simple readable data serialization format similar to Rust syntax
- [James Munns' blog](https://jamesmunns.com/blog/) - Embedded systems expert and Rust consultant's blog
- [Delve](https://github.com/go-delve/delve) - Debugger for the Go programming language
- [LLDB](https://lldb.llvm.org/) - Next generation, high-performance debugger used with Rust and other LLVM languages

### Official Links

- [Zed Homepage](https://zed.dev/)
- [Zed on YouTube](https://www.youtube.com/@zeddotdev)
- [Conrad Irwin on GitHub](https://github.com/ConradIrwin)
- [Conrad Irwin on Twitter](https://twitter.com/conradirwin)
- [Conrad's Blog](https://cirw.in/)
