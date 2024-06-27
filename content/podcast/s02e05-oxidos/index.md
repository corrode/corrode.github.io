+++
title = "OxidOS"
date = 2024-06-27
template = "episode.html"
draft = false
[extra]
guest = "Alexandru Radovici"
role = "Software Engineer"
season = "02"
episode = "05"
series = "Podcast"
+++

<div><script id="letscast-player-18346472" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/rust-in-production-ep-12-oxidos-alexandru-radovici/player.js?size=s"></script></div>

It has become a trope by now: "Cars are computers on wheels." In modern cars, not only the infotainment system but also the engine, brakes, and steering wheel are controlled by software. Better make sure that software is safe.

Alexandru Radovici is a Software Engineer at OxidOS, a company that builds a secure, open-source operating system for cars built on Rust and [Tock](https://tockos.org/).
We talk about the challenges of certifying Rust code for the automotive industry and the new possibilities with Rust-based car software.

<!-- more -->

## Show Notes

### About OxidOS

OxidOS is a Rust-based secure ecosystem for safety critical automotive ECUs. Their solution consists of a Rust-based Secure Operating System and DevTools for medium-size microcontrollers inside automotive ECUs, designed for safety-critical applications. The OxidOS ecosystem provides significant security and safety enhancements while reducing development and certification time by half for automotive ECU software development projects. This is achieved through the usage of Rust that brings benefits such as memory and thread safety enforced at compile time. The OxidOS architecture runs memory sandboxed applications, which have cryptographic credentials and are digitally signed.

### About Alexandru Radovici

Alexandru Radovici is an Associate Professor at the Politehnica University in Bucharest, Romania, where he has been using Rust to teach for a few years. Alexandru is also one of the maintainers of the Tock embedded operating system, written fully in Rust.

### Links From The Show

- [llvm-cov](https://llvm.org/docs/CommandGuide/llvm-cov.html)
- [Pietro Albini at Rust Nation UK: "How Ferrocene qualified the Rust Compiler"](https://youtu.be/_ITnWoPvMKA)
- [microkernel](https://en.wikipedia.org/wiki/Microkernel)
- [Postcard](https://github.com/jamesmunns/postcard)
- [WASM](https://webassembly.org/)
- [Embassy](https://embassy.dev/)
- [Alex's embedded course (it's free)](https://ocw.cs.pub.ro/courses/iot/courses/01)
- [`probe-rs`](https://probe.rs/)
- [Alex's Tock book: "Getting Started with Secure Embedded Systems: Developing IoT Systems for micro:bit and Raspberry Pi Pico Using Rust and Tock"](https://www.amazon.com/Getting-Started-Secure-Embedded-Systems/dp/1484277880)
- [Tour of Rust](https://tourofrust.com/)
- [`sudo-rs`](https://www.memorysafety.org/initiative/sudo-su/)
- [`ntpd-rs`](https://www.memorysafety.org/initiative/ntp/)
- [embedded world](https://www.embedded-world.de/en)

### Official Links

- [OxidOS](https://www.oxid-os.com/)
- [Tock](https://tockos.org/)
- [Alexandru Radovici on LinkedIn](https://www.linkedin.com/in/alexandruradovici/)

### About corrode

"Rust in Production" is a podcast by corrode, a company that helps teams adopt
Rust. We offer training, consulting, and development services to help you
succeed with Rust. If you want to learn more about how we can help you, [please
get in touch](/about).
