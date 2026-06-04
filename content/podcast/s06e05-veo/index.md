+++
title = "Veo"
date = 2026-06-04
template = "episode.html"
draft = false
aliases = ["/p/s06e05"]
[extra]
guest = "Anders Hellerup Madsen and Gorm Casper"
role = "Software Engineers"
season = "06"
episode = "05"
series = "Podcast"
+++

<!-- TODO: replace with the real letscast embed once the episode is published -->
<div><script id="letscast-player-PLACEHOLDER" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/veo/player.js?size=s"></script></div>

I don't know about you, but to me there are few things as interesting as the hardware/software interface: the point where carefully written code meets the messy, physical world of sensors, lenses, and real-time constraints. It's where a clever abstraction either holds up or falls apart the moment a real signal hits it.

That makes Veo a perfect guest. The Copenhagen-based company builds AI-powered cameras that record and analyze sports matches, from grassroots football pitches to professional clubs, and then turn hours of raw footage into something coaches and players can actually use: automatic highlights, player tracking, and match analysis. To get there, they have to capture panoramic video on a custom camera, follow the action without an operator, and crunch an enormous amount of data, reliably and at scale.

My guests sit on both sides of that interface. Anders Hellerup Madsen works close to the metal on the camera itself, on the embedded firmware and the [GStreamer](https://gstreamer.freedesktop.org/) media pipeline that turns raw sensor data into video. Gorm Casper works further up the stack, on the backend that ingests, processes, and analyzes those matches in Rust. Together we talk about where Rust fits across that whole journey, the trade-offs of doing media and computer vision work in a systems language, and what convinced a sports-tech company to bet on Rust for the parts that absolutely cannot fall over.

{{ codecrafters() }}

## Show Notes

### About Veo

[Veo](https://www.veo.co/) (Veo Technologies) is a Danish sports-tech company, headquartered in Copenhagen, that builds AI-powered cameras and a video platform for recording and analyzing matches. Instead of relying on a human camera operator, a Veo camera captures the entire pitch in panoramic video and uses computer vision to automatically follow the ball, generate highlights, and produce analysis that coaches, players, and clubs can use. What started in football has grown into a platform used by tens of thousands of teams across the world, spanning many sports, from amateur clubs to professional organizations.

### About Anders Hellerup Madsen

Anders Hellerup Madsen is a Senior Software Engineer at Veo, where he works on embedded firmware and on the [GStreamer](https://gstreamer.freedesktop.org/)-based media processing pipeline that runs on the Veo camera. He is also a GStreamer contributor.

### About Gorm Casper

Gorm Casper is a Software Engineer at Veo. After many years working on the frontend, he now spends his time on the backend, writing Rust. He holds a Master's in Digital Design & Communication from the IT University of Copenhagen.

### Links From The Episode

- [Veo](https://www.veo.co/) - AI-powered cameras and analysis for sports
- [GStreamer](https://gstreamer.freedesktop.org/) - The open-source multimedia framework at the heart of Veo's camera pipeline
- [gstreamer-rs](https://gitlab.freedesktop.org/gstreamer/gstreamer-rs) - The Rust bindings for GStreamer

### Official Links

- [Veo Website](https://www.veo.co/)
- [Anders Hellerup Madsen on LinkedIn](https://dk.linkedin.com/in/anders-hellerup-madsen-78751b3)
- [Anders Hellerup Madsen on GitLab (freedesktop)](https://gitlab.freedesktop.org/ahem)
- [Gorm Casper's Website](https://gormcasper.dk/)
- [Gorm Casper on LinkedIn](https://www.linkedin.com/in/gormc)
- [Gorm Casper on GitHub](https://github.com/casperin)
