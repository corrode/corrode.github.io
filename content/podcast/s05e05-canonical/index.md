+++
title = "Canonical"
date = 2025-11-27
template = "episode.html"
draft = false
aliases = ["/p/s05e05"]
[extra]
guest = "Jon Seager"
role = "VP Engineering for Ubuntu"
season = "05"
episode = "05"
series = "Podcast"
+++

<div><script id="letscast-player-84d68eec" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/canonical-with-jon-seager-ea273862-48ff-40d8-b3d6-bc85c680a3a6/player.js?size=s"></script></div>

What does it take to rewrite the foundational components of one of the world's most popular Linux distributions? Ubuntu serves over 12 million daily desktop users alone, and the systems that power it, from sudo to core utilities, have been running for decades with what Jon Seager, VP of Engineering for Ubuntu at Canonical, calls "shaky underpinnings."

In this episode, we talk to Jon about the bold decision to "oxidize" Ubuntu's foundation. We explore why they're rewriting critical components like sudo in Rust, how they're managing the immense risk of changing software that millions depend on daily, and what it means to modernize a 20-year-old operating system without breaking the internet.

{{ codecrafters() }}

## Show Notes

### About Canonical

Canonical is the company behind Ubuntu, one of the most widely-used Linux distributions in the world. From personal desktops to cloud infrastructure, Ubuntu powers millions of systems globally. Canonical's mission is to make open source software available to people everywhere, and they're now pioneering the adoption of Rust in foundational system components to improve security and reliability for the next generation of computing.

### About Jon Seager

Jon Seager is VP Engineering for Ubuntu at Canonical, where he oversees the Ubuntu Desktop, Server, and Foundations teams. Appointed to this role in January 2025, Jon is driving Ubuntu's modernization strategy with a focus on Communication, Automation, Process, and Modernisation. His vision includes adopting memory-safe languages like Rust for critical infrastructure components. Before this role, Jon spent three years as VP Engineering building Juju and Canonical's catalog of charms. He's passionate about making Ubuntu ready for the next 20 years of computing.

### Links From The Episode

- [Juju](https://juju.is/) - Jon's previous focus, a cloud orchestration tool
- [GNU coretuils](https://www.gnu.org/software/coreutils/) - The widest used implementation of commands like ls, rm, cp, and more
- [uutils coreutils](https://github.com/uutils/coreutils) - coreutils implementation in Rust
- [sudo-rs](https://github.com/trifectatechfoundation/sudo-rs) -  For your Rust based sandwiches needs
- [LTS](https://en.wikipedia.org/wiki/Long-term_support) - Long Term Support, a release model popularized by Ubuntu
- [coreutils-from-uutils](https://git.launchpad.net/~juliank/+git/coreutils-from/tree/debian/coreutils-from-uutils.links?h=main) - List of symbolic links used for coreutils on Ubuntu, some still point to the GNU implementation
- [man: sudo -E](https://manpages.ubuntu.com/manpages/questing/en/man8/sudo.8.html#:~:text=%2DE%2C%20%2D%2Dpreserve%2Denv) - Example of a feature that sudo-rs does not support
- [SIMD](https://en.wikipedia.org/wiki/Single_instruction%2C_multiple_data) - Single instruction, multiple data
- [rust-coreutils](https://packages.ubuntu.com/questing/rust-coreutils) - The Ubuntu package with all it's supported CPU platforms listed
- [fastcat](https://endler.dev/2018/fastcat/) - Matthias' blogpost about his faster version of `cat`
- [systemd-run0](https://www.freedesktop.org/software/systemd/man/devel/run0.html) - Alternative approach to sudo from the systemd project
- [AppArmor](https://apparmor.net/) - The Linux Security Module used in Ubuntu
- [PAM](https://github.com/linux-pam/linux-pam) - The Pluggable Authentication Modules, which handles all system authentication in Linux
- [SSSD](https://sssd.io/) - Enables LDAP user profiles on Linux machines
- [ntpd-rs](https://github.com/pendulum-project/ntpd-rs) - Timesynchronization daemon written in Rust which may land in Ubuntu 26.04
- [Trifecta Tech Foundation](https://trifectatech.org/) - Foundation supporting sudo-rs development
- [Sequioa PGP](https://sequoia-pgp.org/) - OpenPGP tools written in Rust
- [Mir](https://mir-server.io/) - Canonicals wayland compositor library, uses some Rust
- [Anbox Cloud](https://canonical.com/anbox-cloud) - Canonical's Android streaming platform, includes Rust components
- [Simon Fels](https://github.com/morphis) - Original creator of Anbox and Anbox Cloud team lead at Canonical
- [LXD](https://canonical.com/lxd) - Container and VM hypervisor
- [dqlite](https://canonical.com/dqlite) - SQLite with a replication layer for distributed use cases, potentially being rewritten in Rust
- [Rust for Linux](https://rust-for-linux.com/) - Project to add Rust support to the Linux kernel
- [Nova GPU Driver](https://rust-for-linux.com/nova-gpu-driver) - New Linux OSS driver for NVIDIA GPUs written in Rust
- [Ubuntu Asahi](https://ubuntuasahi.org/) - Community project for Ubuntu on Apple Silicon
- [debian-devel: Hard Rust requirements from May onward](https://lists.debian.org/debian-devel/2025/10/msg00285.html) - Parts of apt are being rewritten in Rust (announced a month after the recording of this episode)
- [Go Standard Library](https://pkg.go.dev/std) - Providing things like network protocols, cryptographic algorithms, and even tools to handle image formats
- [Python Standard Library](https://docs.python.org/3/library/) - The origin of "batteries included"
- [The Rust Standard Library](https://doc.rust-lang.org/stable/std/index.html#what-is-in-the-standard-library-documentation) - Basic types, collections, filesystem access, threads, processes, synchronisation, and not much more
- [clap](https://github.com/clap-rs/clap) - Superstar library for CLI option parsing
- [serde](https://serde.rs/) - Famous high-level serilization and deserialization interface crate

- [zlibrs](https://github.com/trifectatechfoundation/zlib-rs) - Memory-safe zlib implementation in Rust
- [Debcrafters](https://jnsgr.uk/2025/06/introducing-debcrafters/) - Global team ensuring Ubuntu Archive health
- [Jon's Blog: Engineering Ubuntu For The Next 20 Years](https://jnsgr.uk/2025/02/engineering-ubuntu-for-the-next-20-years/)
- [Jon's Blog: Ubuntu Engineering in 2025](https://jnsgr.uk/2025/10/ubuntu-25)

### Official Links

- [Canonical](https://canonical.com/)
- [Ubuntu](https://ubuntu.com/)
- [Jon Seager's Website](https://jnsgr.uk/)
- [Canonical Blog](https://canonical.com/blog)
- [Ubuntu Blog](https://ubuntu.com/blog)
- [Canonical Careers: Engineering](https://canonical.com/careers/engineering) - Apply your Rust skills in the Linux ecosystem

