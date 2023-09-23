+++
title = "The State of Async Rust: Runtimes"
date = 2023-09-13
draft = false
template = "article.html"
[extra]
series = "Rust Ecosystem"
reviews = []
revisions = """
In an earlier version of this article, I discussed async web frameworks.
However, to maintain focus, I've opted to address web frameworks in a dedicated
follow-up article.
"""
+++

Recently, I found myself returning to a compelling series of blog posts titled
[Zero-cost futures in Rust](https://aturon.github.io/blog/2016/08/11/futures/)
by Aaron Turon about what would become the foundation of Rust's async ecosystem
and the [Tokio](https://tokio.rs/) runtime.

This series stands as a cornerstone in writings about Rust. People like Aaron
are the reason why I wanted to be part of the Rust community in the first place.

While 2016 evokes nostalgic memories of excitement and fervor surrounding async
Rust, my sentiments regarding the current state of its ecosystem are now
somewhat ambivalent.

## Why Bother?

Through this series, I hope to address two different audiences:

- Newcomers to async Rust, seeking to get an overview of the current state of
  the ecosystem.
- Library maintainers and contributors to the async ecosystem, in the hope that
  my perspective can be a basis for discussion about the future of async Rust.

In the first article, we will focus on the current state of async Rust runtimes,
their design choices, and their implications on the broader Rust async ecosystem.

## One True Runtime

An inconvenient truth about async Rust is that [libraries still need to be
written against individual
runtimes](https://github.com/rust-lang/areweasyncyet.rs/issues/34). Writing your
async code in a runtime-agnostic fashion requires [conditional
compilation](https://github.com/launchbadge/sqlx/blob/d0fbe7feff4b3a200cf0453417d5e53bd011643a/sqlx-core/src/rt/mod.rs#L116-L136),
[compatibility layers](https://docs.rs/async-compat/latest/async_compat) and
[handling
edge-cases](https://github.com/seanmonstar/reqwest/issues/719#issuecomment-558758637).

This is the rationale behind most libraries gravitating towards the
One True Runtime &mdash; [Tokio](https://tokio.rs/).

Executor coupling is a big problem for async Rust as it breaks the ecosystem
into silos. [Documentation and examples for one runtime don't work with the
other
runtimes](https://www.reddit.com/r/rust/comments/f10tcq/confusion_with_rusts_async_architecture_and_how/fh1oagw/).

Moreover, much of the existing documentation on async Rust feels outdated or
incomplete. For example, the async book remains in draft, with concepts like
`FuturesUnordered` yet to be covered. (There is an open [pull
request](https://github.com/rust-lang/async-book/pull/96), though.)

That leaves us with a situation that is unsatisfactory for everyone involved:

- For new users, it is a big ask to [navigate this space](https://github.com/rust-netlink/netlink-proto/issues/7) and make future-proof decisions.
- For experienced users and library maintainers, [supporting multiple runtimes is an additional burden](https://github.com/launchbadge/sqlx/issues/1669#issuecomment-1032132220). It's no surprise that popular crates like [`reqwest`](https://github.com/seanmonstar/reqwest) [simply insist on Tokio as a runtime](https://github.com/seanmonstar/reqwest/blob/master/Cargo.toml#L109).

This close coupling, [recognized by the async working
group](https://github.com/rust-lang/wg-async/issues/45), has me worried about
its potential long-term impact on the ecosystem.

## The case of `async-std`

`async-std` was an attempt to create an alternative runtime that is closer to
the Rust standard library. Its promise was that you could almost use it as a
drop-in replacement.

Take, for instance, this straightforward synchronous file-reading code:

```rust
use std::fs::File;
use std::io::Read;

fn main() -> std::io::Result<()> {
    let mut file = File::open("foo.txt")?;
    let mut data = vec![];
    file.read_to_end(&mut data)?;
    Ok(())
}
```

In `async-std`, it is an [async
operation](https://docs.rs/async-std/latest/async_std/fs/struct.File.html#method.open)
instead:

```rust
use async_std::prelude::*;
use async_std::fs::File;
use async_std::io;

async fn read_file(path: &str) -> io::Result<()> {
    let mut file = File::open(path).await?;
    let mut data = vec![];
    file.read_to_end(&mut data).await?;
    Ok(())
}
```

The only difference is the `await` keyword.

While the the name might suggest it, `async-std` is not a drop-in replacement
for the standard library as there are many [subtle differences between the
two](https://github.com/seanmonstar/reqwest/issues/719#issuecomment-558758637).

It is hard to create a runtime that is fully compatible with the standard
library. Here are some examples of issues that are still open:

- [New thread is spawned for every I/O request](https://github.com/async-rs/async-std/issues/731)
- [OpenOptionsExt missing for Windows?](https://github.com/async-rs/async-std/issues/914)
- [Spawned task is stuck during flushing in
  File.drop()](https://github.com/async-rs/async-std/issues/900)

It is an enormous effort to replicate the standard library and it is not clear
to me if it is worth it.

Even if it _were_ a drop-in replacement, I'd still ponder its actual merit.
Rust is a language that values explicitness. This is especially true for
reasoning about runtime behavior, such as allocations and blocking operations.
The async-std's teams proposal to ["Stop worrying about
blocking"](https://www.reddit.com/r/rust/comments/ebfj3x/stop_worrying_about_blocking_the_new_asyncstd/)
was met with a [harsh community
response](https://www.reddit.com/r/rust/comments/ebpzqx/do_not_stop_worrying_about_blocking_in_async)
and later retracted.

As of this writing, [1754 public crates have a dependency on
`async-std`](https://lib.rs/crates/async-std/rev) and there
are companies that [rely on it in
production](https://github.com/launchbadge/sqlx/issues/1669#issuecomment-1028879475).

However, looking at the commits over time `async-std` is essentially abandoned
as there is [no active development
anymore](https://github.com/async-rs/async-std/graphs/contributors):

![Fading async-std contribution graph on Github](async-std-github.svg)

This leaves those reliant on the [`async-std`
API](https://docs.rs/async-std/latest/async_std/) – be it for concurrency
mechanisms, extension traits, or otherwise – in an unfortunate situation, as is
the case for libraries developed on top of `async-std`, such as
[`surf`](https://github.com/http-rs/surf). The core of `async-std` is now
powered by [`smol`](https://github.com/smol-rs/smol), but it is probably best to
use it directly for new projects.

## Can't we just embrace Tokio?

Tokio stands as Rust's canonical async runtime.
But to label Tokio merely as a runtime would be an understatement.
It has extra modules for
[fs](https://docs.rs/tokio/latest/tokio/fs/index.html),
[io](https://docs.rs/tokio/latest/tokio/io/index.html),
[net](https://docs.rs/tokio/latest/tokio/net/index.html),
[process-](https://docs.rs/tokio/latest/tokio/process/index.html) and [signal
handling](https://docs.rs/tokio/latest/tokio/signal/index.html) and
[more](https://docs.rs/tokio/latest/tokio/#modules).
That makes it more of a framework for asynchronous programming than just a
runtime.

Partially, this is because Tokio had a pioneering role in async Rust. It
explored the design space as it went along. And while you could exclusively use
the runtime and ignore the rest, it is easier and more common to buy into the
entire ecosystem.

Yet, my main concern with Tokio is that it makes a lot of assumptions about how
async code should be written and where it runs.

For example, [at the beginning of the Tokio
documentation](https://docs.rs/tokio/latest/tokio/), they state:

"The easiest way to get started is to enable all features. Do this by enabling
the `full` feature flag":

```rust
tokio = { version = "1", features = ["full"] }
```

By doing so, one would set up a [multi-threaded
runtime](https://docs.rs/tokio/latest/tokio/attr.main.html) which mandates that
types are `Send` and `'static` and makes it necessary to use synchronization
primitives such as [`Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html)
and [`Mutex`](https://doc.rust-lang.org/std/sync/struct.Mutex.html) for all but
the most trivial applications.

> The Original Sin of Rust async programming is making it multi-threaded by
> default. If premature optimization is the root of all evil, this is the mother
> of all premature optimizations, and it curses all your code with the unholy
> `Send + 'static`, or worse yet `Send + Sync + 'static`, which just kills all the
> joy of actually writing Rust.
>
> &mdash; [Maciej Hirsz](https://maciej.codes/2022-06-09-local-async.html)

Any time we reach for an `Arc` or a `Mutex` it's good idea to stop for a moment
and think about the future implications of that decision.

The choice to use Arc or Mutex might be indicative of a design that
hasn't fully embraced the ownership and borrowing principles that Rust
emphasizes. It's worth reconsidering if the shared state is genuinely necessary
or if there's an alternative design that could minimize or eliminate the need
for shared mutable state.

The problem, of course, is that Tokio imposes this design on you. It's not your
choice to make. 

Beyond the complexities of architecting async code atop these synchronization
mechanisms, they carry a performance cost: Locking means runtime overhead and
additional memory usage; in embedded environments, these mechanisms are often
not available at all.

**Multi-threaded-by-default runtimes cause accidental complexity completely
unrelated to the task of writing async code.**

Ideally, we'd lean on an explicit
`spawn::async` instead of `spawn::blocking`. Futures should be designed for
brief, scoped lifespans rather than the 'static lifetime.

Maciej suggested to use a [local async
runtime](https://maciej.codes/2022-06-09-local-async.html) which is
single-threaded by default and does **not** require types to be `Send` and
`'static`.

I fully agree.

However, I have little hope that the Rust community will change course at this
point. Tokio's roots run deep within the ecosystem and it feels like for better
or worse we're stuck with it.

In the realms of networking and web operations, it's likely that one of your
dependencies integrates Tokio, effectively nudging you towards its adoption. At
the time of writing, [Tokio is used at runtime in 20,768 crates (of which 5,245
depend on it optionally)](https://lib.rs/crates/tokio/rev).

![Runtime popularity bar chart between tokio, async-std, and smol with Tokio
greatly dominating](runtimes.svg)

In spite of all this, we should not stop innovating in the async space!

## Other Runtimes

Going beyond Tokio, several other runtimes deserve more attention:

- [smol](https://github.com/smol-rs/smol): A small async runtime,
  which is easy to understand. The entire executor is around
  [1000 lines of code](https://github.com/smol-rs/async-executor/blob/master/src/lib.rs)
  with other parts of the ecosystem being similarly small.
- [embassy](https://github.com/embassy-rs/embassy): An async runtime for
  embedded systems.
- [glommio](https://github.com/DataDog/glommio): An async runtime for I/O-bound
  workloads, built on top of io_uring and using a thread-per-core model.

These runtimes are important, as they explore alternative paths or open up new
use cases for async Rust. Drawing a parallel with, [Rust's error handling
story](https://mastodon.social/@mre/111019994687648975), the hope is that
competing designs will lead to a more robust foundation overall.
Especially, iterating on smaller runtimes that are less invasive and
single-threaded by default can help improve Rust's async story.

## Async vs Threads

Regardless of runtime choice, we end up doing part of the kernel's job in user
space.

If you allow me a play on [Greenspun's tenth
rule](https://en.wikipedia.org/wiki/Greenspun%27s_tenth_rule):

> Any sufficiently advanced async Rust program contains an ad hoc,
> informally-specified, potentially bug-ridden implementation of half of an
> operating system's scheduler.

Modern operating systems come with highly optimized schedulers that are
excellent at multitasking and support async I/O through
[io_uring](https://lwn.net/Articles/776703/) and
[splice](https://github.com/mre/fcat). We should make better use of these
capabilities.

Let's finally address the elephant in the room:
[Threads](https://doc.rust-lang.org/std/thread/), with their familiarity,
present a path to make synchronous code faster with minimal adjustments.

For example, take our sync code to read a file from above and put it into a
function:

```rust
fn read_contents<T: AsRef<Path>>(file: T) -> Result<String, Box<dyn Error>> {
    let mut file = File::open(file)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    return Ok(contents);
}
```

We can call this function inside the new [scoped
threads](https://doc.rust-lang.org/std/thread/fn.scope.html):

```rust
use std::error::Error;
use std::fs::File;
use std::io::Read;
use std::path::Path;
use std::{thread, time};

fn main() {
    thread::scope(|scope| {
        // worker thread 1
        scope.spawn(|| {
            let contents = read_contents("foo.txt");
            // do something with contents
        });

        // worker thread 2
        scope.spawn(|| {
            let contents = read_contents("bar.txt");
            // ...
        });

        // worker thread 3
        scope.spawn(|| {
            let contents = read_contents("baz.txt");
            // ...
        });
    });

    // No join; threads get joined
    // automatically once the scope ends
}
```

([Link to playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=890ada80a65e9057c4a0fc46199caf0c))

That code looks almost identical to the single-threaded version! Notably, there
are no `.await` calls.

Were `read_contents` part of a public API, it could be used by both async and
sync callers, eliminating the need for an asynchronous runtime.

Async Rust might be more memory-efficient than threads, at the cost of
complexity and worse ergonomics. As an example, if the function were _async_ and
you called it _outside_ of a runtime, it would compile, but not run. Futures do
nothing unless being polled. This is a common footgun for newcomers.

```rust
async fn read_contents<T: AsRef<Path>>(file: T) -> Result<String, Box<dyn Error>> {
    // ...
}

#[tokio::main]
async fn main() {
    // This will print a warning, but compile and do nothing at runtime
    read_contents("foo.txt");
}
```

([Link to playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=7dc4bc6783691c42fbf4cd5a76251da2))

In a recent benchmark, [async Rust was 2x faster than
threads](https://vorner.github.io/async-bench.html), but the _absolute_
difference was only _10ms per request_. To put this into perspective, [this
about as long as PHP takes to start](https://github.com/bdrung/startup-time). In
other words, the difference is negligible for most applications.

Thread-based frameworks, like the now-inactive
[iron](https://github.com/iron/iron), showcased the capability to effortlessly
handle [tens of thousands of requests per
second](https://github.com/iron/iron/wiki/How-to-Benchmark-hello.rs-Example).
This is further complemented by the fact modern Linux systems can manage [tens
of thousands of
threads](https://thetechsolo.wordpress.com/2016/08/28/scaling-to-thousands-of-threads/).

Turns out, computers are pretty good at doing multiple things at once!

As an important caveat, threads are not available or feasible in all
environments, such as embedded systems. My context for this article is primarily
conventional server-side applications that run on top of platforms like Linux or
Windows.

I would like to add that threaded code in Rust undergoes the same stringent
safety checks as the rest of your Rust code: It is protected from data races,
null dereferences, and dangling references, ensuring a level of thread safety
that prevents many common pitfalls found in concurrent programming, Since there
is no garbage collector, there never will be any stop-the-world pause to reclaim
memory. Traditional arguments against threads simply don't apply to Rust &mdash;
fearless concurrency is your friend!

If you find yourself needing to share state between threads, consider using a
channel:

```rust
use std::error::Error;
use std::path::Path;
use std::sync::mpsc;
use std::thread;

// Our error type needs to be `Send` to be used in a channel
// That's the only change we need to make to our original code
fn read_contents<T: AsRef<Path>>(file: T) -> Result<String, Box<dyn Error + Send>> {
    todo!()
}

fn main() {
    let (tx, rx) = mpsc::channel();

    thread::scope(|scope| {
        scope.spawn(|| {
            let contents = read_contents("foo.txt");
            tx.send(contents).unwrap();
        });
        scope.spawn(|| {
            let contents = read_contents("bar.txt");
            tx.send(contents).unwrap();
        });
        scope.spawn(|| {
            let contents = read_contents("baz.txt");
            tx.send(contents).unwrap();
        });
    });

    // Receive messages from the channel
    for received in rx {
        println!("Got: {:?}", received);
    }
}
```

## Summary

### Use Async Rust Sparingly

My original intention was to advise newcomers to sidestep async Rust for now,
giving the ecosystem time to mature. However, I since acknowledged that this is
not feasible, given that a lot of libraries are async-first and new users will
encounter async Rust one way or another.

Instead, I would recommend to use async Rust only when you really need it. Learn
how to write good synchronous Rust first and then, if necessary, transition to
async Rust. Learn to walk before you run.

If you have to use async Rust, stick to Tokio and well-established libraries
like [reqwest](https://github.com/seanmonstar/reqwest) and
[sqlx](https://github.com/launchbadge/sqlx).

While it may seem surprising given the context of this article, we can't
overlook Tokio's stronghold within the ecosystem. A vast majority of libraries
are tailored specifically for it. Navigating compatibility crates can pose
challenges, and sidestepping Tokio doesn't guarantee your dependencies won't
bring it in. I'm hoping for a future shift towards leaner runtimes, but for now,
Tokio stands out as the pragmatic choice for real-world implementations.

However, it's valuable to know that there are alternatives to Tokio and that
they are worth exploring.

### Consider The Alternatives

At its core, Rust and its standard library offer just the absolute
essentials for `async/await`. The bulk of the work is done in
crates developed by the Rust community.
We should make more use of the ability to iterate on async Rust and
experiment with different designs before we settle on a final solution.

In binary crates, think twice if you really need to use async. It's probably
easier to just spawn a thread and get away with blocking I/O. In case you have a
CPU-bound workload, you can use [rayon](https://github.com/rayon-rs/rayon) to
parallelize your code.

> If you don't need async for performance reasons, threads can often be the
> simpler alternative. &mdash; [the Async Book](https://rust-lang.github.io/async-book/01_getting_started/02_why_async.html#async-vs-threads-in-rust)

### Isolate Async Code

If async is truly indispensable, consider isolating your async code from the
rest of your application.

Keep your domain logic synchronous and only use async for I/O and external
services. Following these guidelines will make your code [more
composable](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/)
and accessible. On top of that, the error messages of sync Rust are much easier
to reason about than those of async Rust.

In your public library code, avoid async-only interfaces to make downstream
integration easier.

### Keep It Simple

[Async Rust feels like a different
dialect](https://www.chiark.greenend.org.uk/~ianmdlvl/rust-polyglot/async.html),
significantly more brittle than the rest of the language.

The default mode for writing Rust should be _synchronous_. Freely after
[Stroustup](https://news.ycombinator.com/item?id=22206779):  
*Inside Rust, there is a smaller, simpler language that is waiting to get out.*
It is this language that most Rust code should be written in.
