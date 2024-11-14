+++
title = "Oxide"
date = 2024-11-14
template = "episode.html"
draft = false
aliases = ["/p/s03e03"]
[extra]
guest = "Steve Klabnik"
role = "Author and Software Engineer"
season = "03"
episode = "03"
series = "Podcast"
+++

What's even cooler than writing your own [text editor](/podcast/s03e01-zed/) or your own [operating system](/podcast/s02e07-system76/)? Building your own hardware from scratch with all the software written in Rust -- including firmware, the scheduler, and the hypervisor. 
Oxide Computer Company is one of the most admired companies in the Rust community. They are building "servers as they should be" with a focus on security and performance to serve the needs of modern on-premise data centers.

In this episode, I talk to Steve Klabnik, a software engineer at Oxide and renowned Rustacean, about the advantages of building hardware and software in tandem, the benefits of using Rust for systems programming, and the state of the Rust ecosystem. 

<!-- more -->

## Show Notes

### About Oxide Computer Company

Founded by industry giants Bryan Cantrill, Jessie Frazelle, and Steve Tuck, Oxide Computer Company is a beloved name in the Rust community. They took on the daunting task of rethinking how servers are built -- starting all the way from the hardware and boot process (and no, there is no BIOS).
Their 'On The Metal' podcast is a treasure trove of systems programming stories and proudly served as a role model for 'Rust in Production.'

### About Steve Klabnik

In the Rust community, Steve does not need any introduction. He is a prolific writer, speaker, and software engineer who has contributed to the Rust ecosystem in many ways -- including writing the first version of the official Rust book. If you sent a tweet about Rust in the early days, chances are Steve was the one who replied. Previously, he worked at Mozilla and was a member of the Rust and Ruby core teams. 

### Links From The Episode (In Chronological Order)

- [The Rust Programming Language](https://doc.rust-lang.org/book/) ([No Starch Press version](https://nostarch.com/Rust)) - The official Rust book
- Steve's Rust 1.0 [FOSDEM](https://archive.fosdem.org/2015/schedule/event/the_story_of_rust/) / [ACM](https://www.youtube.com/watch?v=79PSagCD_AY) talk - Early history of Rust
- [Signing Party](https://folklore.org/Signing_Party.html?sort=date) - Story from Macintosh development
- [The Soul of a New Machine](https://en.wikipedia.org/wiki/The_Soul_of_a_New_Machine) by Tracy Kidder - Classic book on computer engineering
- [I have come to bury the BIOS](https://www.osfc.io/2022/talks/i-have-come-to-bury-the-bios-not-to-open-it-the-need-for-holistic-systems/) - Bryan's talk on firmware
- [Beowulf cluster](https://en.wikipedia.org/wiki/Beowulf_cluster) - Early parallel computing architecture
- [Bryan's blog post on Rust](https://bcantrill.dtrace.org/2018/09/18/falling-in-love-with-rust/) - Journey of a systems programmer to Rust
- [JavaOS](https://en.wikipedia.org/wiki/JavaOS) - Operating system written in Java
- [D Programming Language](https://dlang.org/) - Systems programming language
- [Garbage Collection in early Rust](https://pcwalton.github.io/_posts/2013-06-02-removing-garbage-collection-from-the-rust-language.html) - Historical Rust development
- [Removing green threads RFC](https://github.com/rust-lang/rfcs/blob/master/text/0230-remove-runtime.md) - Major change in Rust's concurrency model
- [Hubris](https://github.com/oxidecomputer/hubris) - Oxide's embedded operating system
- [Tock OS](https://tockos.org/) - Embedded operating system in Rust
- [cargo-xtask](https://github.com/matklad/cargo-xtask) - Build automation for Rust projects
- [Hubris Build Documentation](https://github.com/oxidecomputer/hubris#build) - Building Hubris
- [Buck Build System](https://buck.build/) - Facebook's build system
- [Buildomat](https://github.com/oxidecomputer/buildomat) - Oxide's build system
- [Omicron](https://github.com/oxidecomputer/omicron) - Oxide's manufacturing test framework
- [illumos](https://illumos.org/) - Unix operating system
- [bhyve](https://bhyve.org/) - Hypervisor
- [About Self-hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners) - GitHub Actions documentation
- [Async Drop Initiative](https://rust-lang.github.io/async-fundamentals-initiative/roadmap/async_drop.html) - Rust async development
- [Rust Playground Example](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&code=async+fn+f()+%7B%0A++++await+f()%0A%7D) - Demonstrating helpful error when using prefix `await` operator
- [Rust Book - Modules](https://doc.rust-lang.org/book/ch07-02-defining-modules-to-control-scope-and-privacy.html) - Rust module system
- [OpenAPI Specification](https://swagger.io/specification/) - API documentation standard
- [Dropshot](https://github.com/oxidecomputer/dropshot/) - Oxide's OpenAPI server framework
- [Axum](https://github.com/tokio-rs/axum) - Web framework for Rust
- [Oxide Console](https://github.com/oxidecomputer/console) - Oxide's web interface
- [Oxide Console Preview](https://console-preview.oxide.computer/projects) - Demo of Oxide Console using a mocked backend
- [Oxide RFD 1](https://rfd.shared.oxide.computer/rfd/0001) - Request for Discussion process
- [Rust RFCs](https://rust-lang.github.io/rfcs/) - Rust's design process
- [IETF RFCs](https://en.wikipedia.org/wiki/Request_for_Comments) - Internet standards process
- [Zig](https://ziglang.org/) - Systems programming language
- [TigerBeetle](https://tigerbeetle.com/) - Financial accounting database written in Zig
- [Bun](https://bun.sh/) - JavaScript toolkit written in Zig
- [CockroachDB](https://www.cockroachlabs.com/) - Distributed SQL database
- [Oxide and Friends: Wither CockroachDB?](https://oxide.computer/podcasts/oxide-and-friends/2052742) - Podcast episode
- [Mozilla Public License](https://choosealicense.com/licenses/mpl-2.0/) - Software license
- [Asahi Linux](https://asahilinux.org/) - Linux on Apple Silicon with Rust drivers
- [Buck2](https://buck2.build/) - Meta's build system
- [Jujutsu (jj)](https://martinvonz.github.io/jj/) - Git replacement
- [Steve's Jujutsu Tutorial](https://steveklabnik.github.io/jujutsu-tutorial/introduction/introduction.html) - Guide to jj
- [Steve's blog post on branch naming](https://steveklabnik.com/writing/against-names/)

### Official Links

- [Oxide Computer Company](https://oxide.computer/) - Building servers as they should be
- [On The Metal Podcast](https://oxide.computer/podcasts/on-the-metal) - Stories from the hardware/software boundary
- [Steve Klabnik's Blog](https://words.steveklabnik.com/) - Thoughts on programming, Rust, and more
- [Steve Klabnik on Bluesky](https://bsky.app/profile/steveklabnik.com) - Follow Steve for Rust updates and more
