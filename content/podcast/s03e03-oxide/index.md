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

### Links From The Show

- [The Rust Programming Language](https://doc.rust-lang.org/book/) ([No Starch Press version](https://nostarch.com/Rust))
- Steve's Rust 1.0 [FOSDEM](https://archive.fosdem.org/2015/schedule/event/the_story_of_rust/) / [ACM](https://www.youtube.com/watch?v=79PSagCD_AY) talk
- [Signing Party](https://folklore.org/Signing_Party.html?sort=date)
- [The Soul of a New Machine](https://en.wikipedia.org/wiki/The_Soul_of_a_New_Machine) by Tracy Kidder
- [I have come to bury the BIOS, not to open it](https://www.osfc.io/2022/talks/i-have-come-to-bury-the-bios-not-to-open-it-the-need-for-holistic-systems/) - Bryan's talk
- [Beowulf cluster](https://en.wikipedia.org/wiki/Beowulf_cluster)
- [Bryan Cantrill's blog post on Rust](https://bcantrill.dtrace.org/2018/09/18/falling-in-love-with-rust/)
- [JavaOS](https://en.wikipedia.org/wiki/JavaOS)
- [D Programming Language](https://dlang.org/)
- [Garbage Collection in early Rust](https://pcwalton.github.io/_posts/2013-06-02-removing-garbage-collection-from-the-rust-language.html)
- [Removing green threads RFC (2014)](https://github.com/rust-lang/rfcs/blob/master/text/0230-remove-runtime.md)
- [Hubris](https://github.com/oxidecomputer/hubris)
- [Tock OS](https://tockos.org/)
- [cargo-xtask](https://github.com/matklad/cargo-xtask)
- [Hubris Build Documentation](https://github.com/oxidecomputer/hubris#build)
- [Buck Build System](https://buck.build/)
- [Buildomat](https://github.com/oxidecomputer/buildomat)
- [Omicron](https://github.com/oxidecomputer/omicron)
- [illumos](https://illumos.org/)
- [bhyve](https://bhyve.org/)
- [About Self-hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners)
- [Async Drop Initiative](https://rust-lang.github.io/async-fundamentals-initiative/roadmap/async_drop.html)
- [Rust Playground Example for helpful error when using prefix `await` operator](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&code=async+fn+f()+%7B%0A++++await+f()%0A%7D)
- [Rust Book - Modules](https://doc.rust-lang.org/book/ch07-02-defining-modules-to-control-scope-and-privacy.html)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Dropshot](https://github.com/oxidecomputer/dropshot/)
- [Axum](https://github.com/tokio-rs/axum)
- [Oxide Web Console](https://github.com/oxidecomputer/console)
- [Oxide Web Console - Preview](https://console-preview.oxide.computer/projects)
- [Oxide RFD 1](https://rfd.shared.oxide.computer/rfd/0001)
- [Rust RFCs](https://rust-lang.github.io/rfcs/)
- [IETF RFCs](https://en.wikipedia.org/wiki/Request_for_Comments)
- [Zig](https://ziglang.org/)
- [TigerBeetle](https://tigerbeetle.com/)
- [Bun](https://bun.sh/)
- [CockroachDB](https://www.cockroachlabs.com/)
- [Oxide and Friends: Wither CockroachDB?](https://oxide.computer/podcasts/oxide-and-friends/2052742)
- [Mozilla Public License](https://choosealicense.com/licenses/mpl-2.0/)
- [Asahi Linux uses Rust to write drivers](https://asahilinux.org/)
- [Buck2](https://buck2.build/)
- [Jujutsu (jj)](https://martinvonz.github.io/jj/) - Git replacement
- [Steve's Jujutsu Tutorial](https://steveklabnik.github.io/jujutsu-tutorial/introduction/introduction.html)
- [Steve's Blog Post on Branch Naming](https://steveklabnik.com/writing/against-names/)

### Official Links

- [Oxide Computer Company](https://oxide.computer/) - Building servers as they should be
- [On The Metal Podcast](https://oxide.computer/podcasts/on-the-metal) - Stories from the hardware/software boundary
- [Steve Klabnik's Blog](https://words.steveklabnik.com/) - Thoughts on programming, Rust, and more
- [Steve Klabnik on Bluesky](https://bsky.app/profile/steveklabnik.com) - Follow Steve for Rust updates and more
