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

It has become a trope by now: "Cars are computers on wheels." In modern cars, not only the infotainment system but also the engine, brakes, and steering wheel are controlled by software. Better make sure that software is safe.

Alexandru Radovici is a Software Engineer at OxidOS, a company that builds a secure, open-source operating system for cars built on Rust and [Tock](https://github.com/tock/tock).
We talk about the challenges of certifying Rust code for the automotive industry and the new possibilities with Rust-based car software.

<!-- more -->

## Show Notes

### About OxidOS

OxidOS is a Rust-based secure ecosystem for safety critical automotive ECUs. Their solution consists of a Rust-based Secure Operating System and DevTools for medium-size microcontrollers inside automotive ECUs, designed for safety-critical applications. The OxidOS ecosystem provides significant security and safety enhancements while reducing development and certification time by half for automotive ECU software development projects. This is achieved through the usage of Rust that brings benefits such as memory and thread safety enforced at compile time. The OxidOS architecture runs memory sandboxed applications, which have cryptographic credentials and are digitally signed.

### About Alexandru Radovici

Alexandru Radovici is an Associate Professor at the Politehnica University in Bucharest, Romania, where he has been using Rust to teach for a few years. Alexandru is also one of the maintainers of the Tock embedded operating system, written fully in Rust.

### Links From The Show

- [microkernel](https://en.wikipedia.org/wiki/Microkernel)
- [WASM](https://webassembly.org/)
- [Embassy](https://embassy.dev/)
- [Alex's embedded course (it's free)](https://ocw.cs.pub.ro/courses/iot/courses/01)
- [`probe-rs`](https://probe.rs/)
- [Alex's Tock book: "Getting Started with Secure Embedded Systems: Developing IoT Systems for micro:bit and Raspberry Pi Pico Using Rust and Tock"](https://www.amazon.com/Getting-Started-Secure-Embedded-Systems/dp/1484277880)
- [Tour of Rust](https://tourofrust.com/)
- [`sudo-rs`](https://www.memorysafety.org/initiative/sudo-su/)
- [`ntpd-rs`](https://www.memorysafety.org/initiative/ntp/)

### Official Links

- [OxidOS](https://www.oxid-os.com/)
- [Tock](https://github.com/tock/tock)
- [Alexandru Radovici on LinkedIn](https://www.linkedin.com/in/alexandruradovici/)

### About corrode

"Rust in Production" is a podcast by corrode, a company that helps teams adopt
Rust. We offer training, consulting, and development services to help you
succeed with Rust. If you want to learn more about how we can help you, [please
get in touch](/about).
