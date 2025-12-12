+++
title = "Rust for Linux"
date = 2025-12-11
template = "episode.html"
draft = false
aliases = ["/p/s05e06"]
[extra]
guest = "Danilo Krummrich"
role = "Linux Kernel Maintainer"
season = "05"
episode = "06"
series = "Podcast"
+++

<div><script id="letscast-player-e15636c5" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/rust4linux-with-danilo-krummrich/player.js?size=s"></script></div>

Bringing Rust into the Linux kernel is one of the most ambitious modernization efforts in open source history. The Linux kernel, with its decades of C code and deeply ingrained development practices, is now opening its doors to a memory-safe language. It's the first time in over 30 years that a new programming language has been officially adopted for kernel development. But the journey is far from straightforward.

In this episode, we speak with Danilo Krummrich, Linux kernel maintainer and Rust for Linux core team member, about the groundbreaking work of integrating Rust into the Linux kernel. Among other things, we talk about the Nova GPU driver, a Rust-based successor to Nouveau for NVIDIA graphics cards, and discuss the technical challenges and cultural shifts required for large-scale Rust adoption in the kernel as well as the future of the Rust4Linux project. 

{{ codecrafters() }}

## Show Notes

### About Rust for Linux

Rust for Linux is a project aimed at bringing the Rust programming language into the Linux kernel. Started to improve memory safety and reduce vulnerabilities in kernel code, the project has been gradually building the infrastructure, abstractions, and tooling necessary for Rust to coexist with the kernel's existing C codebase.

### About Danilo Krummrich

Danilo Krummrich is a software engineer at Red Hat and a core contributor to the Rust for Linux project. His fundamental contribution to Rust for Linux is the driver-core infrastructure, the foundational framework that makes it possible to write drivers in Rust at all. This includes both C and Rust code that provides the core abstractions for device drivers in the kernel. Danilo is a maintainer for multiple critical kernel subsystems, including Driver Core, DRM (GPUVM, Rust, GPU Scheduler), GPU drivers for NVIDIA GPUs (Nova, Nouveau), Firmware Loader API, as well as Rust bindings for PCI, DMA, and ALLOC. He is the primary developer of the Nova GPU driver, a fully Rust-based driver for modern NVIDIA GPUs.

### Links From The Episode

- [AOSP](https://source.android.com/) - The Android Open Source Project
- [Kernel Mailing Lists](https://lore.kernel.org/) - Where the Linux development happens
- [Miguel Ojeda](https://ojeda.dev/) - Rust4Linux maintainer
- [Wedson Almeida Filho](https://github.com/wedsonaf) - Retired Rust4Linux maintainer
- [noveau driver](https://docs.kernel.org/gpu/nouveau.html) - The old driver for NVIDIA GPUs
- [Vulkan](https://en.wikipedia.org/wiki/Vulkan) - A low level graphics API
- [Mesa](https://www.mesa3d.org/) - Vulkan and OpenGL implementation for Linux
- [vtable](https://en.wikipedia.org/wiki/Virtual_method_table) - Indirect function call, a source of headaches in nouveau
- [DRM](https://docs.kernel.org/gpu/introduction.html) - Direct Rendering Manager, Linux subsystem for all things graphics
- [Monolithic Kernel](https://en.wikipedia.org/wiki/Monolithic_kernel) - Linux' kernel architecture
- [The Typestate Pattern in Rust](https://cliffle.com/blog/rust-typestate/) - A very nice way to model state machines in Rust
- [pinned-init](https://crates.io/crates/pinned-init ) - The userspace crate for pin-init
- [rustfmt](https://github.com/rust-lang/rustfmt) - Free up space in your brain by not thinking about formatting
- [kunit](https://docs.kernel.org/dev-tools/kunit/index.html) - Unit testing framework for the kernel
- [Rust core crate](https://doc.rust-lang.org/stable/core/index.html) - The only part of the Rust Standard Library used in the Linux kernel
- [Alexandre Courbot](https://github.com/Gnurou) - NVIDIA employed co-maintainer of nova-core
- [Greg Kroah-Hartman](http://www.kroah.com/linux/) - Linux Foundation fellow and major Linux contributor
- [Dave Airlie](https://github.com/airlied) - Maintainer of the DRM tree
- [vim](https://www.vim.org/) - not even neovim
- [mutt](http://www.mutt.org/) - classic terminal e-mail client
- [aerc](https://aerc-mail.org/) - a pretty good terminal e-mail client
- [Rust4Linux Zulip](https://rust-for-linux.com/contact#zulip-chat) - The best entry point for the Rust4Linux community

### Official Links

- [Rust for Linux GitHub](https://github.com/Rust-for-Linux)
- [Danilo Krummrich on GitHub](https://github.com/dakr) 
- [Danilo Krummrich on LinkedIn](https://www.linkedin.com/in/danilo-krummrich-796885153/)
