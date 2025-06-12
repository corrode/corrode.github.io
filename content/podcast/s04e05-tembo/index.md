+++
title = "Tembo"
date = 2025-06-12
template = "episode.html"
draft = false
aliases = ["/p/s04e05"]
[extra]
guest = "Adam Hendel"
role = "Founding Engineer"
season = "04"
episode = "05"
series = "Podcast"
+++

<div><script id="letscast-player-a72393de" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/tembo-with-adam-hendel/player.js?size=s"></script></div>

Recently I was in need of a simple job queue for a Rust project. I already had
Postgres in place and wondered if I could reuse it for this purpose. I found PGMQ by
[Tembo](https://www.tembo.io/). PGMQ a simple job queue written in Rust that uses
Postgres as a backend. It fit the bill perfectly. 

In today's episode, I talk to [Adam
Hendel](https://www.linkedin.com/in/adam-hendel/), the founding engineer of
Tembo, about one of their projects, PGMQ, and how it came to be. We discuss the design
decisions behind job queues, interfacing from Rust to Postgres, and the
engineering decisions that went into building the extension.

It was delightful to hear that you could build all of this yourself, but that
you would probably just waste your time doing so and would come up with the same
design decisions as Adam and the team.

{{ codecrafters() }}

## Show Notes

### About Tembo

Tembo builds developer tools that help teams build and ship software faster.
Their first product, [PGMQ](https://github.com/pgmq/pgmq/), was created to solve
the problem of job queues in a simple and efficient way, leveraging the power of
Postgres. They since made a pivot to focus on AI-driven code assistance, but
PGMQ can be used independently and is available as an open-source project.

### About Adam Hendel 

Adam Hendel is the founding engineer at Tembo, where he has been instrumental in
developing PGMQ and other tools like
[pg_vectorize](https://github.com/ChuckHend/pg_vectorize). He has since moved on
to work on his own startup, but remains involved with the PGMQ project.

### Links From The Episode

- [PostgreSQL](https://www.postgresql.org/about/) - Super flexible ~40 year old relational database that just works
- [R](https://www.r-project.org/) - Statistical  Programming Language
- [pgrx](https://github.com/pgcentralfoundation/pgrx/) - Extend Postgres with Rust
- [Postgres Docs: PL/pgSQL](https://www.postgresql.org/docs/current/plpgsql.html) - Scripting with Procedural Language in PostgreSQL
- [Postgres Docs: SPI](https://www.postgresql.org/docs/current/spi.html) - The Postgres Server Programming Interface
- [pgmq](https://github.com/pgmq/pgmq) - A lightweight message queue extension, initially written in Rust
- [Tembo Blog: Introducing PGMQ](https://www.tembo.io/blog/introducing-pgmq) - a blog post about the project
- [sqlx](https://github.com/launchbadge/sqlx) - All of the great things of an ORM, without all of the bad things of an ORM
- [tokio](https://tokio.rs/) - The de facto standard async runtime for Rust
- [AWS SQS](https://aws.amazon.com/sqs/) - Amazon Web Services Simple Queue Service
- [Postgres Docs: LISTEN](https://www.postgresql.org/docs/current/sql-listen.html) - The native Postgres `sub` part of of pubsub
- [Postgres Docs: NOTIFY](https://www.postgresql.org/docs/current/sql-notify.html) - The native Postgres `pub` part of of pubsub
- [tokio-stream](https://docs.rs/tokio-stream/latest/tokio_stream/) - Tokio utility for asynchronous series of values
- [Postgres Docs: Full Text Search](https://www.postgresql.org/docs/current/textsearch.html) - Postgres included FTS capabilities
- [pgvector](https://github.com/pgvector/pgvector) - The standard extension for vector/AI workloads in Postgres
- [pg_vectorize](https://github.com/ChuckHend/pg_vectorize) - Automatically create embeddings for use with pgvector
- [Python Standard Library: None](https://docs.python.org/3/library/constants.html#None) - A type, but not an enum
- [Rust in Production: Astral with Charlie Marsh](https://corrode.dev/podcast/s04e03-astral/) - Massively improving Python day 1 experience
- [Hugging Face candle](https://github.com/huggingface/candle) - Use ML models in Rust

### Official Links

- [Tembo](https://www.tembo.io/)
- [Adam on LinkedIn](https://www.linkedin.com/in/adam-hendel/)
- [Adam on GitHub](https://github.com/ChuckHend)
