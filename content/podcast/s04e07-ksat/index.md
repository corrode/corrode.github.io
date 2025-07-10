+++
title = "KSAT"
date = 2025-07-10
template = "episode.html"
draft = false
aliases = ["/p/s04e07"]
[extra]
guest = "Vegard Sandengen"
role = "Rust Engineer"
season = "04"
episode = "07"
series = "Podcast"
+++

As a kid, I was always fascinated by space tech.
That fascination has only grown as I've learned more about the engineering challenges involved in space exploration.

In this episode, we talk to Vegard Sandengen, a Rust engineer at KSAT, a company that provides ground station services for satellites.
They use Rust to manage the data flow from hundreds of satellites, ensuring that data is received, processed, and stored efficiently.
This data is then made available to customers around the world, enabling them to make informed decisions based on real-time satellite data.

We dive deep into the technical challenges of building reliable, high-performance systems that operate 24/7 to capture and process satellite data.
Vegard shares insights into why Rust was chosen for these mission-critical systems, how they handle the massive scale of data processing,
and the unique reliability requirements when dealing with space-based infrastructure.

From ground station automation to data pipeline optimization, this conversation explores how modern systems programming languages
are enabling the next generation of space technology infrastructure.

{{ codecrafters() }}

## Show Notes

### About KSAT 

KSAT, or Kongsberg Satellite Services, is a global leader in providing ground station services for satellites.
The company slogan is "We Connect Space And Earth," and their mission-critical services are used by customers around the world to access satellite data
for a wide range of applications, including weather monitoring, environmental research, and disaster response.

### About Vegard Sandengen 

Vegard Sandengen is a Rust engineer at KSAT, where he works on the company's data management systems.
He has a Master's degree in computer science and has been working in the space industry for several years.

At KSAT, Vegard focuses on building high-performance data processing pipelines that handle satellite telemetry and payload data
from ground stations around the world. His work involves optimizing real-time data flows and ensuring system reliability
for mission-critical space operations.

### Links From The Episode

- [CCSDS](https://ccsds.org/) - Space data systems standardization body
- [SpaceX](https://www.spacex.com/) - Private space exploration company revolutionizing satellite launches
- [Blue Origin](https://www.blueorigin.com/) - Space exploration company focused on reusable rockets
- [Rocket Lab](https://www.rocketlabusa.com/) - Small satellite launch provider
- [AWS Ground Station](https://aws.amazon.com/ground-station/) - Cloud-based satellite ground station service
- [K2 Space](https://www.k2space.com/) - Space company building satellites entirely in Rust
- [RustConf Presentations](https://www.youtube.com/c/RustVideos) - Annual Rust conference presentations
- [Rust](https://www.rust-lang.org/) - Systems programming language focused on safety and performance
- [serde](https://serde.rs/) - Serialization and deserialization framework for Rust
- [axum](https://github.com/tokio-rs/axum) - Ergonomic web framework built on tokio and tower
- [sqlx](https://github.com/launchbadge/sqlx) - Async SQL toolkit with compile-time checked queries
- [utoipa](https://github.com/juhaku/utoipa) - OpenAPI specification generation from Rust code
- [rayon](https://github.com/rayon-rs/rayon) - Data parallelism library for Rust
- [tokio](https://tokio.rs/) - Asynchronous runtime for Rust applications
- [tokio-console](https://github.com/tokio-rs/console) - Debugger for async Rust applications
- [tracing](https://tracing.rs/) - Application-level tracing framework for async-aware diagnostics
- [W3C Trace Context](https://www.w3.org/TR/trace-context/) - Standard for distributed tracing context propagation
- [OpenTelemetry](https://opentelemetry.io/) - Observability framework for distributed systems
- [Honeycomb](https://www.honeycomb.io/) - Observability platform for complex distributed systems
- [Azure Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview) - Application performance monitoring service

### Official Links

- [KSAT](https://www.ksat.no/)
- [Vegard on GitHub](https://github.com/veeg)