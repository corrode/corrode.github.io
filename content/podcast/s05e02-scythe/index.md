+++
title = "Scythe Robotics"
date = 2025-10-16
template = "episode.html"
draft = false
aliases = ["/p/s05e02"]
[extra]
guest = "Andrew Tinka"
role = "Director of Software Engineering"
season = "05"
episode = "02"
series = "Podcast"
+++

<div><script id="letscast-player-ae39496a" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/scythe-with-andrew-tinka/player.js?size=s"></script></div>

Building autonomous robots that operate safely in the real world is one of the most challenging engineering problems today. When those robots carry sharp blades and work around people, the margin for error is razor-thin.

In this episode, we talk to Andrew Tinka from Scythe Robotics about how they use Rust to build autonomous electric mowers for commercial landscaping. We discuss the unique challenges of robotics software, why Rust is an ideal choice for cutting-edge safety-critical systems, and what it takes to keep autonomous machines running smoothly in the field.

{{ codecrafters() }}

## Show Notes

### About Scythe Robotics

Scythe Robotics is building autonomous electric mowers for commercial landscaping. Their machines combine advanced sensors, computer vision, and sophisticated path planning to autonomously trim large outdoor spaces while ensuring safety around people and obstacles. By leveraging Rust throughout their software stack, Scythe achieves the reliability and safety guarantees required for autonomous systems breaking new ground in uncontrolled environments. The company is headquartered in Colorado and is reshaping how commercial properties are maintained.

### About Andrew Tinka

Andrew is the Director of Software Engineering at Scythe Robotics, where he drives the development of autonomous systems that power their robotic mowers. He specializes in planning and control for large fleets of mobile robots, with over a decade of experience in multi-agent planning technologies that helped pave the way at Amazon Robotics. Andrew has cultivated deep expertise in building safety-critical software for real-world robotics applications and is passionate about using Rust to create reliable, performant systems. His work covers everything from low-level embedded systems to high-level planning algorithms.

### Links From The Episode

- [Ski trails rating](https://en.wikipedia.org/wiki/Piste#North_America,_Australia_and_New_Zealand) - A difficulty rating system common in Colorado
- [NVIDIA Jetson](https://developer.nvidia.com/embedded/jetson-modules) - Combined ARM CPU with a GPU for AI workloads at the heart of every Scythe robot
- [The Rust Book: Variables and Mutability](https://doc.rust-lang.org/stable/book/ch03-01-variables-and-mutability.html#variables-and-mutability) - Immutability is the default in Rust
- [Jon Gjengset: Sguaba](https://www.youtube.com/watch?v=kESBAiTYMoQ) - A type safe spatial maths library
- [The Rust Book: Inheritance as a Type System and as Code Sharing](https://doc.rust-lang.org/stable/book/ch18-01-what-is-oo.html#inheritance-as-a-type-system-and-as-code-sharing) - Unlike Java, Rust doesn't have inheritance
- [Using `{..Default::default}` when creating structs](https://rust-unofficial.github.io/patterns/idioms/default.html) - The alternative is to initialize each field explicitly
- [The Rust Book: Refutability](https://doc.rust-lang.org/stable/book/ch19-02-refutability.html) - Rust tells you when you forgot something
- [Clippy](https://github.com/rust-lang/rust-clippy) - Rust's official linter
- [Deterministic fleet management for autonomous mobile robots using Rust - Andy Brinkmeyer from Arculus](https://www.youtube.com/watch?v=ao-CLgci-e8) - 2024 Oxidize warehouse robot talk with deterministic testing
- [ROS](https://www.ros.org/) - The Robot Operating System
- [Ractor](https://slawlor.github.io/ractor/) - A good modern actor framework
- [Rain: Cancelling Async Rust](https://youtu.be/zrv5Cy1R7r4) - RustConf 2025 talk with many examples of pitfalls

### Official Links

- [Scythe Robotics](https://scytherobotics.com/)
- [Scythe on LinkedIn](https://www.linkedin.com/company/scythe-robotics/)
- [Scythe on GitHub](https://github.com/scythe-robotics)
- [Andrew Tinka on LinkedIn](https://www.linkedin.com/in/andrewtinka/)
