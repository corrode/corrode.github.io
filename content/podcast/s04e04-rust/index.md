+++
title = "Rust"
date = 2025-05-29
template = "episode.html"
draft = false
aliases = ["/p/s04e04"]
[extra]
guest = "Niko Matsakis"
role = "Rust Core Team Member"
season = "04"
episode = "04"
series = "Podcast"
+++

<div><script id="letscast-player-439d0634" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/rust-with-niko-matsakis/player.js?size=s"></script></div>

Few developers have been as influential to my career as Niko Matsakis.
Of course he is a world-class engineer with a PhD from ETH Zürich, a Rust core maintainer who has been
working on the language for way more than a decade, and a Senior Principal Engineer at AWS.
But more importantly, he is an empathetic human and an exceptional communicator.

I've personally been waiting for one year to get him on the show and steal one hour of his
precious time. Now, finally, I got my chance at live recording at Rust Week 2025.
The result is everything I hoped for: a trip down memory lane which takes us back 
to the early days of Rust, an honest and personal look at Rust's strengths and weaknesses, and a glimpse into the future of the language.
All of that packed with insightful anecdotes based on Niko's decades of experience.
If you like Rust, you will enjoy this episode.

{{ codecrafters() }}

## Show Notes

### About Rust

Rust is the language which brought us all together.
What started as a side-project of Graydon Hoare, a single developer at Mozilla, has grown into 
a worldwide community of hobbyists, professionals, and companies which all share the same goal:
to build better, safer software paired with great ergonomics and performance.

### About Niko Matsakis 

Niko is a long-time Rust core team member, having joined the project in 2012.
He was and still is part of the team which designed and implemented Rust's borrow checker,
which is the language's most important feature.
He has been a voice of reason and a guiding light for many of us, including myself.
His insightful talks and blog posts have helped countless developers to see the language and its goals in a new light.

### Special Thanks

Thanks to [RustNL](https://rustnl.org/), the organizers of Rust Week 2025 for inviting Simon and me
to record this episode live. They did a fantastic job organizing the event,
and it was an honor to be part of it.

### Links From The Episode

- [RustWeek 2025](https://rustweek.org/) - Rust conference in Utrecht where we recorded this live episode
- [DataPower](https://en.wikipedia.org/wiki/DataPower) - Niko's employer before working on Rust
- [XSLT](https://en.wikipedia.org/wiki/XSLT) - Language to transform arbitrarily shaped XML into different arbitrary shapes
- [ETH Zürich](https://ethz.ch/) - Niko's Alma Mater
- [Mozilla](https://www.mozilla.org/en-GB/) - Niko's first employer while working on Rust
- [rustboot](https://github.com/rust-lang/rust/tree/ef75860a0a72f79f97216f8aaa5b388d98da6480/src/boot) - Rust's first compiler written in OCaml
- [Don Quixote](https://en.wikipedia.org/wiki/Don_Quixote) - Personification of impractical idealism, just like Rust was in the beginning
- [Steve Klabnik's FOSDEM talk](https://archive.fosdem.org/2015/schedule/event/the_story_of_rust/) - Coining "The Graydon years", [Slides](https://steveklabnik.github.io/history-of-rust/), [Recording of the same talk for ACM](https://youtu.be/79PSagCD_AY)
- [Rust 0.2 Keywords](https://github.com/rust-lang/rust/blob/0.2/doc/rust.md#keywords) - `ret` for `return`, `cont` for `continue`
- [Boxes in Rust 0.8](https://github.com/rust-lang/rust/blob/0.8/doc/tutorial.md#boxes) - `~T` and `@T` as syntax features instead of `Box<T>` and `Rc<T>`
- [Green Threads](https://en.wikipedia.org/wiki/Green_thread) - Like OS threads, but greener!
- [`std::threads`](https://doc.rust-lang.org/std/thread/index.html) - Not green, just part of the standard library
- [`std::rc::Rc`](https://doc.rust-lang.org/std/rc/struct.Rc.html) - The `@T` of `std`
- [`std::boxed::Box`](https://doc.rust-lang.org/std/boxed/struct.Box.html) - The `~T` of `std` with some special compiler sauce
- [`std::sync::Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html) - Thread safe `Rc`
- [`pyo3::Py`](https://docs.rs/pyo3/latest/pyo3/struct.Py.html) - A pointer type in a different library!
- [The Rust Book: Understanding Ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html) - Ownership and borrowing are the first third of "the simple core of Rust"
- [The Rust Book: Using Trait Objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html) - Trait-based dispatch being the second part of "the simple core of Rust"
- [`std::marker::Send`](https://doc.rust-lang.org/std/marker/trait.Send.html) - A trait without even a method to dispatch, aptly placed in the `marker` module
- [`std::marker::Sync`](https://doc.rust-lang.org/std/marker/trait.Sync.html) - Another example of a marker trait
- [Linear Type Systems](https://en.wikipedia.org/wiki/Substructural_type_system#Linear_type_systems) - Foundational research topic for borrowing in Rust
- [regex](https://github.com/rust-lang/regex) - "Real stuff" built in Rust
- [rayon](https://github.com/rayon-rs/rayon) - Turning iterators into parallel processing
- [Tokio Async Runtime](https://tokio.rs/) - An entire async ecosystem as a perfomant library
- [Comment on RFC 2394](https://github.com/rust-lang/rfcs/pull/2394#discussion_r179909812) - The beginning of the `await x` / `x.await` discussion?
- [Alex Crichton](https://github.com/alexcrichton) - Rust compiler, wasm, and lang-advisors team member
- [cramertj](https://github.com/cramertj) - Rust lang-advisors and libs-contributors team member
- [withoutboats](https://without.boats/) - Rust team alumni
- [Carl Lerche](https://carllerche.com/) - tokio maintainer
- [aturon](https://aturon.github.io/) - Rust team alumni
- [ALGOL 60](https://en.wikipedia.org/wiki/ALGOL_60#Code_sample_comparisons) - Doesn't look like C
- [try blocks](https://doc.rust-lang.org/nightly/unstable-book/language-features/try-blocks.html) - Do we need a postfix `match` operator for this?
- [Rust Blog: Announcing Rust 1.31 and Rust 2018](https://blog.rust-lang.org/2018/12/06/Rust-1.31-and-rust-2018/) - A watershed moment for Rust
- [Non-lexical lifetimes](https://blog.rust-lang.org/2018/12/06/Rust-1.31-and-rust-2018/#non-lexical-lifetimes) - Included in 1.31 and Rust 2018
- [Santiago Pastorino](https://santiagopastorino.com/) - Rust compiler contributor, worked on non-lexical lifetimes
- [Makefile Example](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/Makefile) - "We don't need cargo, Make is fine"
- [Rust Blog: Laying the foundation for Rust's future](https://blog.rust-lang.org/2020/08/18/laying-the-foundation-for-rusts-future/) - Mozilla's parting gift to Rust?
- [Tyler Mandry](https://github.com/tmandry) - Rust lang team co-lead with Niko
- [Josh Triplett](https://joshtriplett.org/) - Rust lang, cargo, and libs team member
- [Amazon S3 Express One Zone storage class](https://aws.amazon.com/s3/storage-classes/express-one-zone/) - Super low latency S3, written in Rust
- [Amazon Aurora DSQL](https://aws.amazon.com/rds/aurora/dsql/) - Serverless SQL, an AWS project that started 100% in JVM and finished 100% Rust
- [Just make it scale: An Aurora DSQL story](https://www.allthingsdistributed.com/2025/05/just-make-it-scale-an-aurora-dsql-story.html) - Blog post detailing the Aurora DSQL Rust rewrite
- [Rust in 2025: Targeting foundational software](https://smallcultfollowing.com/babysteps/blog/2025/03/10/rust-2025-intro/) - Niko's vision for Rust
- [Be excellent to each other](https://youtu.be/rph_1DODXDU) - Party on dudes!

### Official Links

- [Rust Language](https://www.rust-lang.org/)
- [Rust Foundation](https://rustfoundation.org/)
- [Niko Matsakis' Homepage](https://smallcultfollowing.com/babysteps/)
- [Niko Matsakis on GitHub](https://github.com/nikomatsakis)
