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

Recently I was in need of a simple job queue for a Rust project. I already had
Postgres in place and wondered if I could reuse it for this purpose. I found
[Tembo](https://www.tembo.io/), a simple job queue written in Rust that uses
Postgres as a backend. It fit the bill perfectly. 

In today's episode, I talk to [Adam
Hendel](https://www.linkedin.com/in/adam-hendel/), the founding engineer of
Tembo, about their project, PGMQ, and how it came to be. We discuss the design
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

- [PGMQ](https://github.com/pgmq/pgmq/)
- [Introducing PGMQ](https://www.tembo.io/blog/introducing-pgmq) - a blog post about the project

### Official Links

- [Tembo](https://www.tembo.io/)
- [Adam on LinkedIn](https://www.linkedin.com/in/adam-hendel/)
- [Adam on GitHub](https://github.com/ChuckHend)