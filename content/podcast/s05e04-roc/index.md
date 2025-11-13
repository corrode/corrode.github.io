+++
title = "Roc"
date = 2025-11-13
template = "episode.html"
draft = false
aliases = ["/p/s05e04"]
[extra]
guest = "Richard Feldman"
role = "Creator of Roc"
season = "05"
episode = "04"
series = "Podcast"
+++

<div><script id="letscast-player-080f1fca" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/roc-with-richard-feldman/player.js?size=s"></script></div>

Building a new programming language from scratch is a monumental undertaking. In this episode, we talk to Richard Feldman, creator of the Roc programming language, about building a functional language that is fast, friendly, and functional. We discuss why the Roc team moved away from using Rust as a host language and instead is in the process of migrating to Zig. What was the decision-making process like? What can Rust learn this decision? And how does Zig compare to Rust for this kind of systems programming work?

{{ codecrafters() }}

## Show Notes

### About Roc

Roc is a fast, friendly, functional programming language currently in alpha development. It's a single-paradigm functional language with 100% type inference that compiles to machine code or WebAssembly. Roc takes inspiration from Elm but extends those ideas beyond the frontend, introducing innovations like platforms vs applications, opportunistic mutation, and purity inference. The language features static dispatch, a small set of simple primitives that work well together, and excellent compiler error messages. Roc is already being used in production by companies like Vendr, and is supported by a nonprofit foundation with corporate and individual sponsors.

### About Richard Feldman

Richard Feldman is the creator of the Roc programming language and author of "Elm in Action." He works at Zed Industries and has extensive experience with functional programming, particularly Elm. Richard is also the host of Software Unscripted, a weekly podcast featuring casual conversations about code with programming language creators and industry experts. He's a frequent conference speaker and teacher, with courses available on Frontend Masters. Richard has been a longtime contributor to the functional programming community and previously worked at NoRedInk building large-scale Elm applications.

### Links From The Episode

- [Zig](https://ziglang.org/) - Better than Rust?
- [Rust in Production: Zed](https://corrode.dev/podcast/s03e01-zed/) - Our interview with Richard's colleague with more details about Zed
- [Richards blogpost about migrating from Rust to Zig](https://gist.github.com/rtfeldman/77fb430ee57b42f5f2ca973a3992532f) - Sent in by many listeners
- [Elm](https://elm-lang.org/) - Initial inspiration for Roc
- [NoRedInk](https://www.noredink.com/) - Richard's first experience with Elm
- [Haskell](https://www.haskell.org/) - A workable Elm on the backend substitute
- [OCaml](https://ocaml.org/) - Functional language, but pure functions only encouraged
- [F#](https://fsharp.org/) - Similar shortcomings as OCaml
- [Evan Czaplicki](https://github.com/evancz) - Creator of Elm
- [Ghostty](https://ghostty.org/) - Terminal emulator from Mitchel Hashimoto with lots of code contributions in Zig
- [RAII](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization) - Resource acquisition is initialization, developed for C++, now a core part of Rust
- [Frontend Masters: The Rust Programming Language](https://frontendmasters.com/courses/rust/) - Richard's course teaching Rust
- [Rust by Example: From and Into](https://doc.rust-lang.org/rust-by-example/conversion/from_into.html) - Traits for ergonomic initialising of objects in Rust
- [The Rust Programming Language: Lifetime Annotations on Struct Definitions](https://doc.rust-lang.org/stable/book/ch10-03-lifetime-syntax.html#lifetime-annotations-in-struct-definitions) - Learn from Roc: try to avoid having lifetime type parameters
- [Rust By Example: Box, stack and heap](https://doc.rust-lang.org/rust-by-example/std/box.html#box-stack-and-heap) - Putting objects on the heap can slow down your application
- [Design Patterns: Elements of Reusable Object-Oriented Software](https://en.wikipedia.org/wiki/Design_Patterns) - Seminal book popularising many common patterns in use today, written by the so-called "Gang of Four"
- [Casey Muratori: The Big OOPs](https://www.youtube.com/watch?v=wo84LFzx5nI) - Game developer explaining why OOP was an obvious mistake for high performance code
- [Alan Kay](https://en.wikipedia.org/wiki/Alan_Kay) - Coined the term "object-oriented" while developing the Smalltalk language in the 70s
- [Niklaus Wirth](https://en.wikipedia.org/wiki/Niklaus_Wirth) - Working on Modula, a modular programming language, at the same time
- [Kotlin](https://kotlinlang.org/) - A new and popular language, basically Java++
- [Go](https://go.dev/) - Popular "greenfield" language, i.e. not coupled to an existing language, not using the object oriented paradigm
- [Cranelift backend for Rust](https://github.com/rust-lang/rustc_codegen_cranelift) - A faster backend than LLVM, but still not released
- [Andrew Kelly](https://andrewkelley.me/) - Creator of Zig
- [Software Unscripted](https://pod.link/1602572955) - Richard's Podcast
- [GPUI](https://www.gpui.rs/) - Zed's own UI crate
- [Structure of Arrays vs Array of structures](https://en.wikipedia.org/wiki/AoS_and_SoA) - A big source of unsafe code in the Rust implementation of Roc
- [The Zig Programming Language: comptime](https://ziglang.org/documentation/0.15.2/#comptime) - Zig's replacement for Rust's proc-macros, with much broader utility
- [crabtime](https://docs.rs/crabtime/latest/crabtime/) - Comptime crate for Rust
- [Roc](https://en.wikipedia.org/wiki/Roc_(mythology)) - Roc's namesake, the mythical bird
- [Rust in Production: Tweede Golf](https://corrode.dev/podcast/s01e05-tweede-golf/) - Podcast episode with Volkert de Vries, one of the first contributors to Roc

### Official Links

- [Roc Programming Language](https://www.roc-lang.org/)
- [Roc on GitHub](https://github.com/roc-lang/roc)
- [Richard Feldman on GitHub](https://github.com/rtfeldman)
- [Richard Feldman on LinkedIn](https://www.linkedin.com/in/rtfeldman/)
- [Richard Feldman on X](https://x.com/rtfeldman)
- [Software Unscripted Podcast](https://pod.link/1602572955)

