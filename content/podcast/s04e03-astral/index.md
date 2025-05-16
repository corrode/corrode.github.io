+++
title = "Astral"
date = 2025-05-15
template = "episode.html"
draft = false
aliases = ["/p/s04e03"]
[extra]
guest = "Charlie Marsh"
role = "Founder & CEO"
season = "04"
episode = "03"
series = "Podcast"
+++

<div><script id="letscast-player-7b80a2f5" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/uv-with-charlie-marsh/player.js?size=s"></script></div>

Up until a few years ago, Python tooling was a nightmare:
basic tasks like installing packages or managing Python versions was a pain.
The tools were brittle and did not work well together,
mired in a swamp of underspecified implementation defined behaviour.

Then, apparently suddenly, but in reality backed by years of ongoing work on formal interoperability specifications,
we saw a renaissance of new ideas in the Python ecosystem.
It started with [Poetry](https://python-poetry.org/) and [pipx](https://pypa.github.io/pipx/) and continued with tooling written in Rust like [rye](https://rye.astral.sh/), which later got incorporated into 
[Astral](https://astral.sh/).

Astral in particular contributed a very important piece to the puzzle: `uv`
-- an extremely fast Python package and project manager that supersedes all previous attempts;
For example, it is 10x-100x faster than pip.

<!-- more -->

In this episode I talk to Charlie Marsh, the Founder and CEO of Astral.
We talk about Astral's mission and how Rust plays an important role in it. 

{{ codecrafters() }}

## Show Notes

### About Astral

Astral is a company that builds tools for Python developers.
What sounds simple is actually a very complex problem:
Python's ecosystem is huge, but fragmented and often incompatible.
Astral’s mission is to make the Python ecosystem more productive by building high-performance developer tools, starting with Ruff.
In their words: "Fast, unified, futuristic."

### About Charlie Marsh 

Charlie is a long-time open source developer and entrepreneur.
He has an impressive CV, graduating with highest honors from Princeton University.
After that, he worked at Khan Academy and others before eventually founding Astral in '22.
Charlie is an engaging speaker and a great communicator.

### Links From The Episode

- [ruff](https://docs.astral.sh/ruff/) - Python static linter and formatter written in Rust
- [uv](https://docs.astral.sh/uv/) - Python package and project manager written in Rust
- [rustfmt](https://github.com/rust-lang/rustfmt) - Rust code formatter
- [clippy](https://github.com/rust-lang/rust-clippy/) - Linter for Rust code
- [The Rust Programming Language: Cargo Workspaces](https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html) - The Rust Book's chapter on workspaces
- [pip](https://pip.pypa.io/en/stable/) - The standard Package Installer for Python
- [pip documentation: Requirements File Format](https://pip.pypa.io/en/stable/reference/requirements-file-format/) - A description of the format of requirements.txt, including a list of embedded CLI options
- [uv's CI](https://github.com/astral-sh/uv/tree/main/.github/workflows) - Build scripts for many different platforms
- [jemalloc](https://jemalloc.net/) - Alternative memory allocator
- [reqwest](https://github.com/seanmonstar/reqwest) - An easy and powerful Rust HTTP Client
- [zlib-ng](https://github.com/zlib-ng/zlib-ng) - Next Generation zlib implementation in C
- [zlib-rs](https://github.com/trifectatechfoundation/zlib-rs) - Pure Rust implementation of zlib
- [XCode Instruments](https://developer.apple.com/tutorials/instruments) - Native macOS performance profiler
- [CodSpeed](https://codspeed.io/) - Continuous benchmarking in CI
- [hyperfine](https://github.com/sharkdp/hyperfine) - "macro benchmarking" tool, coincidentally written in Rust
- [samply](https://github.com/mstange/samply) - Sampling based profiler written in Rust
- [cargo flamegraph](https://github.com/flamegraph-rs/flamegraph) - Cargo profiling plugin
- [tokio](https://tokio.rs) - Asynchronous runtime for Rust
- [curl-rust](https://github.com/alexcrichton/curl-rust) - Network API used in cargo
- [tar-rs](https://github.com/alexcrichton/tar-rs) - Sync tar crate
- [async-tar](https://github.com/dignifiedquire/async-tar) - Async tar crate based on the async_std runtime
- [tokio-tar](https://github.com/vorot93/tokio-tar) - Async tar crate based on tokio
- [astral-tokio-tar](https://github.com/astral-sh/tokio-tar) - Async tar crate based on tokio, maintained by Astral
- [RustPython](https://rustpython.github.io/) - Python interpreter written in Rust
- [lalrpop](https://github.com/lalrpop/lalrpop) - The parser generator used by RustPython
- [Charlie's EuroRust 2024 Talk](https://youtu.be/zOY9mc-zRxk) - Mentions the version number parser at 18:45
- [ripgrep](https://github.com/BurntSushi/ripgrep) - Andrew Gallant's idiomatic Rust project, which also happens to be a very fast CLI file search tool

### Official Links

- [Astral](https://astral.sh/)
- [Charlie's Website](https://crmarsh.com/)
- [Charlie on GitHub](https://github.com/charliermarsh)
