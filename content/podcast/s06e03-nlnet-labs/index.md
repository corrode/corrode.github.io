+++
title = "NLnet Labs"
date = 2026-05-07
template = "episode.html"
aliases = ["/p/s06e03"]
[extra]
guest = "Arya Khanna and Martin Hoffmann"
role = "Engineers"
season = "06"
episode = "03"
series = "Podcast"
+++

<div><script id="letscast-player-d2dce55d" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/nlnet-labs-with-arya-khanna-and-martin-hoffmann/player.js?size=s"></script></div>

Every time you load a website, send an email, or update an app, you're quietly relying on a handful of unglamorous services that route your packets to the right place: DNS to translate names into addresses, and BGP to figure out how to actually get there. When these systems break, or get attacked, the Internet doesn't just slow down but stops working.

For more than 25 years, NLnet Labs has been one of the small, non-profit teams keeping that core infrastructure running. Their software, including the DNS servers NSD and Unbound, the RPKI tools Krill and Routinator, and the new DNSSEC signer Cascade, is deployed everywhere from hobbyist Pi-Hole setups to Let's Encrypt and major Internet operators. And increasingly, it's written in Rust!

In this episode, I talk to Arya Khanna and Martin Hoffmann from NLnet Labs about what it takes to maintain critical Internet infrastructure as a small team, why they bet on Rust for new projects like the `domain` crate and Cascade and what the rest of us can learn from a codebase whose users include the people who keep your routes flowing.

{{ codecrafters() }}

## Show Notes

### About NLnet Labs

NLnet Labs is a non-profit foundation based in Amsterdam that develops open source software and open standards for the core infrastructure of the Internet. Since 1999, the small but dedicated team has built some of the most widely deployed building blocks of the modern web, including the authoritative DNS nameserver [NSD](https://nlnetlabs.nl/projects/nsd/about/), the recursive DNS resolver [Unbound](https://nlnetlabs.nl/projects/unbound/about/), and the RPKI tools [Krill](https://github.com/NLnetLabs/krill) and [Routinator](https://nlnetlabs.nl/projects/routing/routinator/), which secure global Internet routing. Their work is trusted by operators ranging from hobbyist Pi-Hole users to Let's Encrypt and major Internet service providers. In recent years, NLnet Labs has been steadily moving its new development to Rust, with projects like the [domain](https://nlnetlabs.nl/projects/domain/about/) crate and the [Cascade](https://nlnetlabs.nl/news/2025/Oct/07/cascade-0.1.0-released/) DNSSEC signer leading the way.


### Links From The Episode

- [NSD](https://nlnetlabs.nl/projects/nsd/about/) - NLNet Labs first project
- [Lychee](https://github.com/lycheeverse/lychee) - A link-checker that receives funding from NLNet, not NLNet labs
- [unbound](https://nlnetlabs.nl/projects/unbound/about/) - A DNS server like BIND, but only for recursive queries
- [Cascade](https://nlnetlabs.nl/news/2025/Oct/07/cascade-0.1.0-released/) - The new DNSSEC signing solution from NLNet Labs
- [Pi-Hole](https://pi-hole.net/) - A small usecase for unbound
- [Let's Encrypt](https://letsencrypt.org/) - A big user of unbound with scale and security requirements
- [Asahi Linux](https://asahilinux.org/) - Linux on Apple Silicon, mostly with Rust
- [Binder CVE](https://social.kernel.org/notice/B1JLrtkxEBazCPQHDM) - A CVE in Rust
- [LDNS](https://nlnetlabs.nl/projects/ldns/about/) - A collection of DNS functions, written in C, now in maintenance mode
- [domain](https://nlnetlabs.nl/projects/domain/about/) - The new collection of DNS functions, written in Rust
- [tokio](https://tokio.rs/) - The biggest shared dependency across the Rust ecosystem, first announced in 2017
- [Rust in Production: Helsing with Jon Gjengset](https://corrode.dev/podcast/s06e02-helsing/) - You _can_ take generics too far
- [bytes](https://github.com/tokio-rs/bytes) - Tokio's ARC of bytes
- [Arc Welding](https://en.wikipedia.org/wiki/Arc_welding) - The other type of "fixing"
- [Alejandra GonzÃ¡lez' crate dependency analysis](https://tech.lgbt/@blyxyas/116252699616176134) - 46% of published crates depend directly on tokio
- [RPKI](https://en.wikipedia.org/wiki/Resource_Public_Key_Infrastructure) - Signing and validating IPs and routing information
- [Routinator](https://nlnetlabs.nl/projects/routing/routinator/) - A RPKI validator, one of the first Rust applications in production
- [hyper](https://hyper.rs/) - The ubiquitous HTTP crate
- [Krill](https://github.com/NLnetLabs/krill) - The RPKI Certificate Authority tool with "fun" shutdown code
- [Roto](https://codeberg.org/NLnetLabs/roto) - Tert's scripting language, used by another NLNet Labs project, Rotonda

### Official Links

- [NLnet Labs Website](https://nlnetlabs.nl)
- [Arya Khanna's Website](https://bal-e.org/)
- [Arya Khanna on GitHub](https://github.com/bal-e)
- [Arya Khanna on Mastodon](https://tech.lgbt/@bal4e)
- [Martin Hoffmann on GitHub](https://github.com/partim)
- [Martin Hoffmann on Mastodon](https://social.tchncs.de/@partim)
