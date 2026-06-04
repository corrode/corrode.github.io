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

<div><script id="letscast-player-035dc666" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/veo-with-anders-hellerup-madsen-and-gorm-casper/player.js?size=s"></script></div>

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

- [GStreamer](https://gstreamer.freedesktop.org/) - The open-source multimedia framework at the heart of Veo's camera pipeline
- [gstreamer-rs](https://gitlab.freedesktop.org/gstreamer/gstreamer-rs) - The Rust bindings for GStreamer
- [OpenCV](https://opencv.org/) - The open-source computer vision library
- [Nvidia Jetson](https://developer.nvidia.com/embedded-computing) - Like a Raspberry Pi, but with more video processing capabilities
- [glib](https://docs.gtk.org/glib/) - The foundation of gstreamer, also of GTK, Gnome, and many more
- [ffmpeg](https://ffmpeg.org/) - An easier video manipulation tool, but without good support for custom pipeline elements
- [CUDA](https://developer.nvidia.com/cuda-toolkit) - Nvidia's tooling to run C++ code on the GPU
- [Sebastian Dröge](https://coaxion.net/) - Amazing Rust and GStreamer developer
- [OCaml](https://ocaml.org/) - A really nice language and an inspiration for Rust
- [Rustonomicon](https://doc.rust-lang.org/nomicon/) - The dark arts of unsafe Rust
- [Latest Announcement from Nvidia - CUDA for Rust](https://www.marktechpost.com/2026/05/09/nvidia-ai-just-released-cuda-oxide-an-experimental-rust-to-cuda-compiler-backend-that-compiles-simt-gpu-kernels-directly-to-ptx/) - Nvidia's experimental Rust-to-CUDA compiler, cuda-oxide
- [Rust GPU](https://rust-gpu.github.io/) - Write and run GPU code in Rust, announced on 2026-05-12
- [Temporal](https://temporal.io/) - A durable workflow engine
- [Rust in Production: Astral](/podcast/s04e03-astral/) - The Python company that does uv and ruff, with Rust
- [serde_json::Value](https://docs.rs/serde_json/latest/serde_json/enum.Value.html) - The Rust analogue to Python's dict
- [ReasonML](https://reasonml.github.io/) - OCaml with a better syntax
- [bedquilt](https://bedquilt.io/) - Write 80s Text Adventures with Rust
- [Rust Book: Transfer Data Between Threads with Message Passing](https://doc.rust-lang.org/book/ch16-02-message-passing.html) - The chapter explaining the Go motto "Do not communicate by sharing memory; instead, share memory by communicating"

### Official Links

- [Veo Website](https://www.veo.co/)
- [Anders Hellerup Madsen on LinkedIn](https://dk.linkedin.com/in/anders-hellerup-madsen-78751b3)
- [Anders Hellerup Madsen on GitLab (freedesktop)](https://gitlab.freedesktop.org/ahem)
- [Gorm Casper's Website](https://gormcasper.dk/)
- [Gorm Casper on LinkedIn](https://www.linkedin.com/in/gormc)
- [Gorm Casper on GitHub](https://github.com/casperin)
