+++
title = "Rust for Linux"
date = 2025-12-04
template = "episode.html"
draft = false
aliases = ["/p/s05e06"]
[extra]
guest = "Danilo Krummrich"
role = "Rust for Linux Kernel Developer at Red Hat"
season = "05"
episode = "06"
series = "Podcast"
+++

<div><script id="letscast-player-XXXXXXXX" src="https://letscast.fm/podcasts/rust-in-production-XXXXXXXX/episodes/XXXXXXXX/player.js?size=s"></script></div>

Bringing Rust into the Linux kernel is one of the most ambitious modernization efforts in open source history. The Linux kernel, with its decades of C code and deeply ingrained development practices, is now opening its doors to a memory-safe language. It's the first time in over 30 years that a new programming language has been officially adopted for kernel development. But the journey is far from straightforward.

In this episode, we speak with Danilo Krummrich, a Rust for Linux kernel developer at Red Hat, about the groundbreaking work of integrating Rust into the Linux kernel. Among other things, we we talk about the Nova GPU driver, a Rust-based successor to Nouveau for NVIDIA graphics cards, and discuss the technical challenges and cultural shifts required for large-scale Rust adoption in the kernel as well as the future of the Rust4Linux project. 

{{ codecrafters() }}

## Show Notes

### About Rust for Linux

Rust for Linux is a project aimed at bringing the Rust programming language into the Linux kernel. Started to improve memory safety and reduce vulnerabilities in kernel code, the project has been gradually building the infrastructure, abstractions, and tooling necessary for Rust to coexist with the kernel's existing C codebase.

### About Danilo Krummrich

Danilo Krummrich is a software engineer at Red Hat and a core contributor to the Rust for Linux project. In January 2025, he was officially added as a reviewer to the RUST entry in the kernel's MAINTAINERS file, recognizing his expertise in developing Rust abstractions and APIs for kernel development. Danilo maintains the `staging/dev` and `staging/rust-device` branches and is the primary developer of the Nova GPU driver, a fully Rust-based driver for modern NVIDIA GPUs. He is also a maintainer of RUST [ALLOC] and several DRM-related kernel subsystems.

### Links From The Episode

### Official Links

- [Rust for Linux GitHub](https://github.com/Rust-for-Linux)
- [Danilo Krummich on GitHub](https://github.com/dakr) 
- [Danilo Krummrich on LinkedIn](https://www.linkedin.com/in/danilo-krummrich-796885153/)
