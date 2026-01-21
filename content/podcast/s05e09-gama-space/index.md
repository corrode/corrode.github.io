+++
title = "Gama Space"
date = 2026-01-22
template = "episode.html"
draft = false
aliases = ["/p/s05e09"]
[extra]
guest = "Sebastian Scholz"
role = "Engineer"
season = "05"
episode = "09"
series = "Podcast"
+++

<div><script id="letscast-player-XXXXXXXX" src="https://letscast.fm/podcasts/rust-in-production-XXXXXXXX/episodes/XXXXXXXX/player.js?size=s"></script></div>

Space exploration demands software that is reliable, efficient, and able to operate in the harshest environments imaginable. When a spacecraft deploys a solar sail millions of kilometers from Earth, there's no room for memory bugs, race conditions, or software failures. This is where Rust's robustness guarantees become mission-critical.

In this episode, we speak with Sebastian Scholz, an engineer at Gama Space, a French company pioneering solar sail and drag sail technology for spacecraft propulsion and deorbiting. We explore how Rust is being used in aerospace applications, the unique challenges of developing software for space systems, and what it takes to build reliable embedded systems that operate beyond Earth's atmosphere.

{{ codecrafters() }}

## Show Notes

### About Gama Space

Gama Space is a French aerospace company founded in 2020 and headquartered in Ivry-sur-Seine, France. The company develops space propulsion and orbital technologies with a mission to keep space accessible. Their two main product lines are solar sails for deep space exploration using the sun's infinite energy, and drag sails—the most effective way to deorbit satellites and combat space debris. After just two years of R&D, Gama successfully launched their satellite on a SpaceX Falcon 9. The Gama Alpha mission is a 6U cubesat weighing just 11 kilograms that deploys a large 73.3m² sail. With 48 employees, Gama is at the forefront of making space exploration more sustainable and accessible.

### About Sebastian Scholz

Sebastian Scholz is an engineer at Gama Space, where he works on developing software systems for spacecraft propulsion technology. His work involves building reliable, safety-critical embedded systems that must operate flawlessly in the extreme conditions of space. Sebastian brings expertise in systems programming and embedded development to one of the most demanding environments for software engineering.

### Links From The Episode

- [GAMA-ALPHA](https://www.satcat.com/sats/55084) - The demonstration satellite launched in January 2023
- [Ada](https://ada-lang.io/) - Safety-focused programming language used in aerospace
- [probe-rs](https://probe.rs/) - Embedded debugging toolkit for Rust
- [hyper](https://hyper.rs/) - Fast and correct HTTP implementation for Rust
- [Flutter](https://flutter.dev/) - Google's UI toolkit for cross-platform development
- [UART](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter) - Very common low level communication protocol
- [Hamming Codes](https://en.wikipedia.org/wiki/Hamming_code) - Error correction used to correct bit flips
- [Rexus/Bexus](https://en.wikipedia.org/wiki/Rexus/Bexus) - European project for sub-orbital experiments by students
- [Embassy](https://embassy.dev/) - The EMBedded ASsYnchronous framework
- [CSP](https://github.com/libcsp/libcsp) - The Cubesat Space Protocol
- [std::num::NonZero](https://doc.rust-lang.org/std/num/struct.NonZero.html) - A number in Rust that can't be 0
- [std::ffi::CString](https://doc.rust-lang.org/std/ffi/struct.CString.html) - A null-byte terminated String
- [Rust in Production: KSAT](https://corrode.dev/podcast/s04e07-ksat/) - Our episode with Vegard about using Rust for Ground Station operations
- [Rust in Production: Oxide](https://corrode.dev/podcast/s03e03-oxide/) - Our episode with Steve, mentioning Hubris
- [Hubris](https://github.com/oxidecomputer/hubris) - Oxide's embedded operating system
- [ZeroCopy](https://docs.rs/zerocopy/latest/zerocopy/) - Transmute data in-place without allocations
- [std::mem::transmute](https://doc.rust-lang.org/std/mem/fn.transmute.html) - Unsafe function to treat a memory section as a different type than before

### Official Links

- [Gama Space Website](https://www.gamaspace.com/)
- [Gama Space on LinkedIn](https://www.linkedin.com/company/gamaspace/)
- [Gama Space on Crunchbase](https://www.crunchbase.com/organization/gama-22d7)

