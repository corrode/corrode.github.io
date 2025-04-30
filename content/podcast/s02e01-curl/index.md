+++
title = "curl"
date = 2024-05-02
template = "episode.html"
draft = false
aliases = ["/p/s02e01"]
[extra]
guest = "Daniel Stenberg"
role = "Open Source Maintainer and Public Speaker"
season = "02"
episode = "01"
series = "Podcast"
+++

<div><script id="letscast-player-82930892" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/rust-in-production-ep-8-curl-s-daniel-stenberg/player.js?size=s"></script></div>

In the season premier we talk to none other than Daniel Stenberg! We focus on integrating Rust modules in curl, their benefits, ways in which Rust and Rust crates helped improve curl, but also how curl helped those crates, and where curl is used in the official Rust toolchain. Along the way we also learn about the early history of curl and Rust, which section of your car's owner's-manual you should "re"-read, some weird HTTP edge-cases, and Daniel's experience in open-source maintainership.

<!-- more -->

{{ codecrafters() }}

## Show Notes

### About curl

Curl started as a simple way to download currency conversion rates from the
internet and evolved into a general data transfer library and cli tool with
support for not only HTTP, but also FTP, IMAP, MQTT, and many more. It rivals
with SQLite for the #1 spot on the most deployed software list, leaving Java
far behind.


### About Daniel Stenberg

Daniel Stenberg has been the lead developer of curl for more than 25 years, and
is an avid speaker and famous open source personality. Having worked at Mozilla
around the time Rust was created, he now works for
[WolfSSL](https://www.wolfssl.com/).


### Links From The Episode (In Chronological Order)

 - [httpget and curl history](https://curl.se/docs/history.html)
 - [AltaVista](https://en.wikipedia.org/wiki/AltaVista)
 - [curl licenses in the wild](https://daniel.haxx.se/blog/2016/10/03/screenshotted-curl-credits/)
 - [quiche](https://github.com/cloudflare/quiche)
 - [ISRG](https://www.abetterinternet.org/)
 - [hyper](https://hyper.rs/)
 - [rustls](https://github.com/rustls/rustls)
 - [curl's CI infrastructure](https://daniel.haxx.se/blog/2023/02/01/curls-use-of-many-ci-services/)
 - [coreutils in Rust](https://uutils.github.io/coreutils/)
 - [`curl -Z`](https://curl.se/docs/manpage.html#-Z)
 - [curl crate](https://github.com/alexcrichton/curl-rust)
 - [curl's 101 supported OSes](https://curl.se/docs/install.html#101-operating-systems)
 - ["I could rewrite curl" post](https://daniel.haxx.se/blog/2021/05/20/i-could-rewrite-curl/)
 - [curl's CONTRIBUTE.md](https://github.com/curl/curl/blob/master/docs/CONTRIBUTE.md)
 - [Daniel's FOSDEM'24 talk](https://fosdem.org/2024/schedule/event/fosdem-2024-1931-you-too-could-have-made-curl-/)
 - [Rust in curl](https://daniel.haxx.se/blog/2022/02/01/curl-with-rust/)


### Official Links

 - [curl](https://curl.se/)
 - [curl's GitHub repo](https://github.com/curl/curl)
 - [Daniel Stenberg on Twitter](https://twitter.com/bagder)
 - [Daniel's YouTube channel](https://www.youtube.com/user/danielhaxxse)
 - [Daniel Stenberg's blog](https://daniel.haxx.se/blog/)

