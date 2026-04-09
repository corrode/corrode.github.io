+++
title = "Cloudsmith"
date = 2026-04-09
template = "episode.html"
draft = false
aliases = ["/p/s06e01"]
[extra]
guest = "Cian Butler"
role = "Service Reliability Engineer"
season = "06"
episode = "01"
series = "Podcast"
+++

<div><script id="letscast-player-0efbeff6" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/gama-space-with-sebastian-scholz/player.js?size=s"></script></div>

Rust adoption can be loud, like when companies such as Microsoft, Meta, and Google announce their use of Rust in high-profile projects. But there are countless smaller teams quietly using Rust to solve real-world problems, sometimes even without them noticing. This episode tells one such story. Cian and his team at Cloudsmith have been adopting Rust in their Python monolith not because they wanted to rewrite everything in Rust, but because the Rust extensions were simply best-in-class for the specific performance problems they were trying to solve in their Django application. As they had these initial successes, they gained more confidence in Rust and started using it in more and more areas of their codebase.

{{ codecrafters() }}

## Show Notes

### About Cloudsmith

Made with love in Belfast and trusted around the world. Cloudsmith is the fully-managed solution for controlling, securing, and distributing software artifacts. They analyze every package, container, and ML model in an organizations supply chain, allow blocking bad packages before they reach developers, and build an ironclad chain of custody.

### About Cian Butler 

Cian is a Service Reliability Engineer located in Dublin, Ireland. He has been working with Rust for 10 years and has a history of helping companies build reliable and efficient software. He has a BA in Computer Programming from Dublin City University.

### Links From The Episode

- [(Not) the Tao of Cloudsmith](https://www.skillen.io/not-the-tao-of-cloudsmith/) - A blog post from Lee Skillen, Cloudsmith's co-founder explaining why they chose Python for their monolith
- [Django](https://www.djangoproject.com/) - Python on Rails
- [Django Mixins](https://docs.djangoproject.com/en/6.0/topics/class-based-views/mixins/) - Great for scaling up, not great for long-term maintenance
- [SBOM](https://en.wikipedia.org/wiki/Software_bill_of_materials) - Software Bill of Materials
- [Microservice vs Monolith](https://martinfowler.com/articles/microservices.html) - Martin Fowler's canonical explanation
- [Jaeger](https://www.jaegertracing.io/) - "Debugger" for microservices
- [PyO3](https://pyo3.rs/) - Rust-to-Python and Python-to-Rust FFI crate
- [orjson](https://github.com/ijl/orjson) - Pretty fast JSON handling in Python using Rust
- [drf-orjson-renderer](https://github.com/brianjbuck/drf_orjson_renderer) - Simple orjson wrapper for Django REST Framework
- [Rust in Python cryptography](https://cryptography.io/en/latest/faq/#why-does-cryptography-require-rust) - Parsing complex data formats is just safer in Rust!
- [jsonschema-py](https://github.com/Stranger6667/jsonschema/tree/master/crates/jsonschema-py) - jsonschema in Python with Rust, mentioned in the PyO3 docs
- [WSGI](https://peps.python.org/pep-3333/) - Python's standard for HTTP server interfaces
- [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) - A application server providing a WSGI interface
- [rustimport](https://github.com/mityax/rustimport) - Simply import Rust files as modules in Python, great for prototyping
- [granian](https://github.com/emmett-framework/granian) - WSGI application server written in Rust with tokio and hyper
- [hyper](https://hyper.rs/) - HTTP parsing and serialization library for Rust
- [HAProxy](https://www.haproxy.org/) - Feature rich reverse proxy with good request queue support
- [nginx](https://nginx.org/en/) - Very common reverse proxy with very nice and readable config
- [locust](https://locust.io/) - Fantastic load-test tool with configuration in Python
- [goose](https://www.tag1.com/goose/) - Locust, but in Rust
- [Podman](https://podman.io/) - Daemonless container engine
- [Docker](https://www.docker.com/) - Container platform
- [buildx](https://github.com/docker/buildx) - Docker CLI plugin for extended build capabilities with BuildKit
- [OrbStack](https://orbstack.dev/) - Faster Docker for Desktop alternative
- [Rust in Production: curl with Daniel Stenberg](https://corrode.dev/podcast/s02e01-curl/) - Talking about hyper's strictness being at odds with curl's permissive design
- [axum](https://docs.rs/axum/latest/axum/) - Ergonomic and modular web framework for Rust
- [rocket](https://rocket.rs/) - Web framework for Rust

