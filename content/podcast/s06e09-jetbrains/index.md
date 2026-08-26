+++
title = "JetBrains"
date = 2026-07-30
template = "episode.html"
draft = false
aliases = ["/p/s06e09"]
[extra]
guest = "Orhun Parmaksız"
role = "Rust Developer Advocate"
season = "06"
episode = "09"
series = "Podcast"
+++

<div><script id="letscast-player-f02961e4" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/rustrover-with-orhun-parmaksiz-9e48c9f8-fa3f-45a6-8e32-442a5bd76600/player.js?size=s"></script></div>

Welcome to the final episode of this season of Rust in Production. My guest is Orhun Parmaksız from JetBrains, and we talk about building developer tools with Rust.

JetBrains is best known for IntelliJ IDEA, Kotlin, and a long line of IDEs for professional software teams. In the Rust world, that now includes RustRover: a commercial IDE built on the IntelliJ platform, with deep Rust support for navigation, refactoring, debugging, testing, and large codebases.

This episode is about where Rust fits into that world. We talk about why JetBrains does not plan to rewrite the IntelliJ platform in Rust, why Fleet used Rust for its File System Daemon, how Air builds on parts of Fleet's architecture, and why JetBrains prefers out-of-process Rust helpers over JNI inside the JVM. We also get into RustRover's internals: PSI, THIR, MIR-based expression evaluation in the debugger, procedural macro sandboxing, library stubs, parser regression testing, cargo-nextest support, and the practical trade-offs between JetBrains' indexing model and rust-analyzer's Salsa-based approach.

{{ svix() }}

## Show Notes

### Links From The Episode

- [Ratatui](https://ratatui.rs/) - The terminal UI library that changed Orhun's life
- [ratatuefi](https://github.com/sermuns/ratatuefi) - A demo showing Ratatui running in UEFI without an operating system kernel
- [Renaissance of Terminal User Interfaces with Rust](https://media.ccc.de/v/froscon2024-3147-renaissance_of_terminal_user_interfaces_with_rust) - Orhun's FrOSCon talk about Ratatui and Rust-powered TUIs
- [lychee](https://lychee.cli.rs/overview/) - Matthias' Rust link checker project
- [Orhun's Arch Linux packages](https://archlinux.org/packages/?maintainer=orhun) - A great way to discover Rust projects through packaging work
- [RustRover](https://www.jetbrains.com/rust/) - JetBrains' fully integrated Rust development suite
- [IdeaVim](https://lp.jetbrains.com/ideavim/) - Vim mode for JetBrains IDEs
- [LightEdit mode](https://www.jetbrains.com/help/idea/lightedit-mode.html) - Quick startup for simple editing tasks in JetBrains IDEs
- [Welcome to Fleet!](https://blog.jetbrains.com/blog/2021/11/29/welcome-to-fleet/) - The original Fleet announcement
- [Fleet Below Deck, Part I: Architecture Overview](https://blog.jetbrains.com/fleet/2022/01/fleet-below-deck-part-i-architecture-overview/) - Details on Fleet's hybrid architecture and Rust-based File System Daemon
- [JetBrains Air](https://air.dev/) - The agentic successor to Fleet
- [Rust MIR](https://rustc-dev-guide.rust-lang.org/mir/index.html) - The Mid-level IR used as a hook point for RustRover's debugger integrations
- [Fewer False Positives in RustRover 2026.1](https://blog.jetbrains.com/rust/2026/06/09/fewer-false-positives-rustrover/) - Background on JetBrains' Crate Rover-inspired diagnostics regression work
- [Crater](https://crater.rust-lang.org/) - The Rust Project's CI tool for rebuilding public crates and catching regressions
- [rust-analyzer](https://rust-analyzer.github.io/) - The Rust IDE backend solving many similar problems from a different architecture
- [Code in Rust with RustRover](https://www.youtube.com/watch?v=pnFS0YIKUJ8) - Vitaly Bragilevsky's RustRover talk
- [How Rust IDEs Understand Code](https://blog.jetbrains.com/rust/2026/05/29/how-rust-ides-understand-code/) - Recap of the RustRover and rust-analyzer livestream with Lukas Wirth and Vlad Beskrovny
- [Salsa](https://github.com/salsa-rs/salsa) - The incremental computation framework used by rust-analyzer
- [RustRover licenses for open source](https://www.jetbrains.com/community/opensource/) - One way JetBrains supports open-source projects
- [Rust Berlin Talks at JetBrains](https://www.youtube.com/watch?v=ut5EHZ2FK0c) - Berlin Rust meetup hosted at the JetBrains office
- [JetBrains Academy plugin](https://plugins.jetbrains.com/plugin/10081-jetbrains-academy) - Learn Rust inside RustRover and other JetBrains IDEs
- [Rust in Production: Rust with Niko Matsakis](https://corrode.dev/podcast/s04e04-rust/) - The Rust Project episode mentioned in this conversation
- [Rust Commercial Network](https://rustfoundation.org/rust-commercial-network/) - JetBrains and Ratatui are both part of the network
- [cargo-nextest](https://nexte.st/) - An alternative Rust test runner with benefits over plain `cargo test`
- [What's New in RustRover 2026.2](https://blog.jetbrains.com/rust/2026/07/22/whats-new-in-rustrover-2026-2/) - The latest RustRover release with tighter Axum and reqwest integration
- [PhpStorm](https://www.jetbrains.com/phpstorm/) - Matthias' first experience with JetBrains products
- [Zig 2026: No-AI Policy, $670K Foundation, Left GitHub & Why Zig Isn't 1.0](https://www.youtube.com/watch?v=iqddnwKF8HQ) - JetBrains' interview with Andrew Kelley
- [Interactive declarative macro tester](https://blog.jetbrains.com/rust/2026/07/22/whats-new-in-rustrover-2026-2/) - A RustRover feature for better macro debugging during development
- [Grindhouse](https://grindhouse.dev/) - A joke turned into a flourishing community
- [Terminal Tuesdays](https://www.youtube.com/@TerminalCollectiveOrg) - Orhun's terminal-focused livestreams and interviews
- [Terminal Collective Discord](https://discord.com/invite/6EUERBrAMs) - The terminal community Discord server
- [Ratty](https://github.com/orhun/ratty) - A fun GPU-rendered terminal emulator with inline 3D graphics

### Official Links

- [JetBrains Website](https://www.jetbrains.com/)
- [RustRover](https://www.jetbrains.com/rust/)
- [JetBrains Open Source Support](https://www.jetbrains.com/community/opensource/)
- [Orhun's Website](https://orhun.dev/)
- [Orhun on GitHub](https://github.com/orhun)
- [Orhun on YouTube](https://youtube.com/@orhundev)
- [Orhun on Bluesky](https://bsky.app/profile/orhun.dev)
- [Orhun on LinkedIn](https://www.linkedin.com/in/orhunp/)
