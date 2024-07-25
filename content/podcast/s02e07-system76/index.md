+++
title = "System76"
date = 2024-07-25
template = "episode.html"
draft = false
[extra]
guest = "Jeremy Soller"
role = "Software Engineer"
season = "02"
episode = "07"
series = "Podcast"
+++

<div><script id="letscast-player-e4782127" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/rust-in-production-ep-14-system76-s-jeremy-soller/player.js?size=s"></script></div>

Many devs dream of one day writing their own operating system. Ideally in their favorite language: Rust. For many of us, this dream remains just that: a dream.

Jeremy Soller from System76, however, didn't just contribute kernel code for Pop!_OS, but also started his own operating system, RedoxOS, which is completely written in Rust. One might get the impression that he likes to tinker with low-level code!

In this episode of Rust in Production, Jeremy talks about his journey. From getting hired as a kernel developer at Denver-based company System76 after looking at the job ad for 1 month and finally applying, to being the maintainer of not one but two operating systems, additional system tools, and the Rust-based Cosmic desktop. We'll talk about why it's hard to write correct C code even for exceptional developers like Jeremy and why Rust is so great for refactoring and sharing code across different levels of abstraction.

<!-- more -->

## Show Notes

### About System76

From hardware all the way up to the UI, System76 pushes hard for vertical integration. The company has a strong following amongst Linux enthusiasts and is a big advocate for Rust. They use it across the stack for most (all?) of their major projects. Instead of GNOME or KDE, the Denver-based company even built their own user interface in Rust, called COSMIC.

### About Jeremy Soller

Jeremy is a hardware and kernel hacker who has an intricate understanding of low-level computing. With Redox OS, an operating system fully written in Rust,
he was one of the first developers who pushed the boundaries of what was possible with the still young language.
The first release of Redox was in April 2015 when Rust hadn't even reached 1.0. By all means, Jeremy is a pioneer in the Rust community, an expert in low-level programming, and an advocate for robust, reliable systems programming.

### About our Sponsor: InfinyOn

Data pipelines are often slow, unreliable, and complex. [InfinyOn](https://infinyon.com/), the creators of [Fluvio](https://www.fluvio.io/), aims to fix this. Built in Rust, Fluvio offers fast, reliable data streaming. It lets you build event-driven pipelines quickly, running as a single 37 MB binary. With features like [SmartModules](https://infinyon.com/docs/tutorials/smartmodule-basics/), it handles various data types efficiently. Designed for developers, it offers a clean API and [intuitive CLI](https://infinyon.com/docs/cli/). Streamline your data infrastructure at [infinyon.com/rustinprod](https://infinyon.com/rustinprod).

### Links From The Show

- [RedoxOS](https://redox-os.org/)
- [System76 firmware updater](https://github.com/system76/firmware-update)
- [OpenCV](https://opencv.org/)
- [Old Rust syntax examples (click "start" to see changes over time!)](https://brson.github.io/archaea/)
- [iced](https://iced.rs/)
- [cosmic](https://github.com/pop-os/cosmic)
- [softbuffer, a framebuffer crate](https://crates.io/crates/softbuffer)
- [rust-boot](https://lib.rs/crates/rustboot)
- [x86_64_unknown_none target triplet](https://doc.rust-lang.org/rustc/platform-support/x86_64-unknown-none.html)
- [Osborne 1](https://en.wikipedia.org/wiki/Osborne_1)
- [CP/M](https://en.wikipedia.org/wiki/CP/M)
- [Security vulnerabilities in the Rust std library](https://www.cvedetails.com/vulnerability-list/vendor_id-19029/product_id-48677/Rust-lang-Rust.html)
- [StackOverflow Survey: Rust is the most-admired programming language with an 83% score in 2024.](https://survey.stackoverflow.co/2024/technology#admired-and-desired)
- [orbclient](https://gitlab.redox-os.org/redox-os/orbclient)
- [Intel 8051 Wikipedia](https://en.wikipedia.org/wiki/MCS-51)
- [Raspberry RP2040](https://www.raspberrypi.com/products/rp2040/)
- [Philipp Oppermann: "Writing an OS in Rust"](https://os.phil-opp.com/)
- [libcosmic](https://github.com/pop-os/libcosmic)
- [distinst](https://github.com/pop-os/distinst)
- [softbuffer](https://github.com/rust-windowing/softbuffer)

### Official Links

- [System76](https://system76.com/)
- [Redox OS](https://www.redox-os.org/)
- [Jeremy's private homepage](https://soller.dev/)
- [Jeremy on GitHub](https://github.com/jackpot51)
- [Jeremy on Mastodon](https://fosstodon.org/@soller)
- [InfinyOn's Homepage](https://infinyon.com/rustinprod)

### About corrode

"Rust in Production" is a podcast by corrode, a company that helps teams adopt
Rust. We offer training, consulting, and development services to help you
succeed with Rust. If you want to learn more about how we can help you, [please
get in touch](/about).