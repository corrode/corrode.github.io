+++
title = "The State of Async Rust"
date = 2023-09-07
template = "article.html"
[extra]
series = "Commentary"
reviews = []
+++

Lately, I revisted the original blog post series by Aaron Turon
about the creation of the Tokio async runtime for Rust, titled
[Zero-cost futures in Rust](https://aturon.github.io/blog/2016/08/11/futures/).

It is a seminal body of work and one of my favorite pieces of writing about Rust
in general. People like Aaron are the reason why I wanted to be part of the Rust
community in the first place.

Although I have fond memories about the energy and excitement around async Rust
in 2016, I now have mixed feelings about the state of the ecosystem.

## Why Write This?

With this article, I want to address three different audiences:

- People who are new to (async) Rust and want to get an overview of the current state of the ecosystem.
- People who are already using async Rust and want to know my opinion about the current problems and challenges.
- Library maintainers and contributors to the async ecosystem in the hope that my perspective can be the basis for a discussion about the future of async Rust.

## One True Executor

An unconvenient truth about async Rust is that [libraries still need to be
written against individual
runtimes](https://github.com/rust-lang/areweasyncyet.rs/issues/34). Writing your
async code in a runtime-agnostic fashion requires [conditional
compilation](https://github.com/launchbadge/sqlx/blob/d0fbe7feff4b3a200cf0453417d5e53bd011643a/sqlx-core/src/rt/mod.rs#L116-L136),
[compatibility layers](https://docs.rs/async-compat/latest/async_compat) and
[handling
edge-cases](https://github.com/seanmonstar/reqwest/issues/719#issuecomment-558758637).

That's why most libraries only support a single runtime &mdash;
[Tokio](https://tokio.rs/).

Executor coupling is a big problem for async Rust as it breaks the ecosystem
into silos. [Documentation and examples for one runtime don't work with the
other
runtimes](https://www.reddit.com/r/rust/comments/f10tcq/confusion_with_rusts_async_architecture_and_how/fh1oagw/).

Speaking of which, documentation on async Rust is outdated and lacking behind in
general. For example, the async book is still in draft status and important
concepts like `FuturesUnordered` are not covered yet. (There is an open [pull
request](https://github.com/rust-lang/async-book/pull/96), though.)

That leaves us with a situation that it unsatisfactory for everyone involved:

- For new users, it is a big ask to [navigate this space](https://github.com/rust-netlink/netlink-proto/issues/7) and make future-proof (no pun intended) decisions.
- For experienced users and library maintainers, [supporting multiple runtimes is a burden](https://github.com/launchbadge/sqlx/issues/1669#issuecomment-1032132220). That's why popular crates like [`reqwest`](https://github.com/seanmonstar/reqwest) [require Tokio as a runtime](https://github.com/seanmonstar/reqwest/blob/master/Cargo.toml#L109).
  This close coupling is a known issue, which is [acknowledged by the async working group](https://github.com/rust-lang/wg-async/issues/45).

## The case of `async-std`

`async-std` was an attempt to create a runtime that is closer to the Rust
standard library. Its promise was that you could almost use it as a drop-in
replacement for the standard library.

For example,
[`File::open`](https://doc.rust-lang.org/std/fs/struct.File.html#method.open) is
a blocking operation in the standard library.

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

Even if it _were_ a drop-in replacement, I would still question the value of it.
Rust is a language that values explicitness. This is especially true for
reasoning about runtime behavior, such as allocations and blocking operations.
The async-std's teams proposal to ["Stop worrying about
blocking"](https://www.reddit.com/r/rust/comments/ebfj3x/stop_worrying_about_blocking_the_new_asyncstd/)
was met with a [harsh community
response](https://www.reddit.com/r/rust/comments/ebpzqx/do_not_stop_worrying_about_blocking_in_async)
and later retracted.

As of today, [1754 public crates have a dependency on
`async-std`](https://lib.rs/crates/async-std/rev) and there
a companies that [rely on it in
production](https://github.com/launchbadge/sqlx/issues/1669#issuecomment-1028879475).

However, as of 2023, `async-std` is essentially abandoned as there is [no active
development anymore](https://github.com/async-rs/async-std/graphs/contributors).

Whoever relied on [`async-std`'s
API](https://docs.rs/async-std/latest/async_std/) (concurrency primitives,
extension traits, etc.) is now stuck with a project that is not actively
developed anymore and this is also true for the [libraries that were written
against it](https://github.com/http-rs/surf).

## Can't we just embrace Tokio?

Tokio is the canonical async runtime for Rust. In fact, Tokio is more than just
a runtime; it has extra modules for
[fs](https://docs.rs/tokio/latest/tokio/fs/index.html),
[io](https://docs.rs/tokio/latest/tokio/io/index.html),
[net](https://docs.rs/tokio/latest/tokio/net/index.html),
[process-](https://docs.rs/tokio/latest/tokio/process/index.html) and [signal
handling](https://docs.rs/tokio/latest/tokio/signal/index.html) and
[more](https://docs.rs/tokio/latest/tokio/#modules).
That makes it more of a framework for asynchronous programming than just a
runtime.

Partially, this is because Tokio pioneered async Rust and had to explore the
design space as it went along. And while you could exclusively use the runtime
and ignore the rest, it is just easier to just buy into the whole ecosystem.

My main concern with Tokio is that it makes a lot of assumptions about how async
code should be written and where it runs.
For example, it assumes that you want to use a [multi-threaded
runtime](https://docs.rs/tokio/latest/tokio/attr.main.html) (as per their
default) and mandates that types are `Send` and `'static`, which makes it
necessary to know about synchronization primitives such as
[`Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html) and
[`Mutex`](https://doc.rust-lang.org/std/sync/struct.Mutex.html) for all
but the most trivial applications.

> The Original Sin of Rust async programming is making it multi-threaded by
> default. If premature optimization is the root of all evil, this is the mother
> of all premature optimizations, and it curses all your code with the unholy
> `Send + 'static`, or worse yet `Send + Sync + 'static`, which just kills all the
> joy of actually writing Rust.
>
> &mdash; [Maciej Hirsz](https://maciej.codes/2022-06-09-local-async.html)

It's not only more inconvenient to write async code on top of these synchronization primitives,
they are also more expensive from a performance perspective: Locking
means runtime overhead and additional memory usage; in embedded environments,
these mechanisms are often not available at all.

On top of it, writing async code is a mental burden.
The entirety of async Rust is a minefield of leaky abstractions.

Maciej suggested to use a [local async
runtime](https://maciej.codes/2022-06-09-local-async.html) which is
single-threaded by default and does **not** require types to be `Send` and `'static`.

I fully agree.

However, I have little hope that the Rust community will change
course at this point. Tokio is too deeply ingrained in the ecosystem already
and it feels like we're stuck with it.

Chances are, one of your dependencies pulls in Tokio anyway, at which point
you're forced to use it as well. [Tokio is used at runtime in 20,768 crates (of
which 5,245 optionally)](https://lib.rs/crates/tokio/rev).

In spite of all this, we should not stop innovating in the async space!

## Other Runtimes

In that spirit, there are three other runtimes that are worth highlighting:

- [smol](https://github.com/smol-rs/smol): A small async runtime, which is easy to understand. The entire executor is around [1000 lines of code](https://github.com/smol-rs/async-executor/blob/master/src/lib.rs).
- [embassy](https://github.com/embassy-rs/embassy): An async runtime for
  embedded systems.
- [glommio](https://github.com/DataDog/glommio): An async runtime for I/O-bound workloads, built on top of io_uring and using a thread-per-core model.

These runtimes are important, as they explore alternative paths for async Rust.
[Similar to Rust's error handling story](https://mastodon.social/@mre/111019994687648975), the hope is that competing designs will lead to a more robust foundation in the long run.
Especially iterating on smaller runtimes that are less invasive and
single-threaded by default can help improve Rust's async story.

## Async vs Threads

The main alternative to async Rust is &mdash; you guessed it &mdash; using
[threads](https://doc.rust-lang.org/std/thread/).
Threads allow you to reuse existing synchronous code without significant code
changes.

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

We can call this function from multiple [scoped threads](https://doc.rust-lang.org/std/thread/fn.scope.html):

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

    // Threads get joined automatically once the scope ends
}
```

([Link to playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=890ada80a65e9057c4a0fc46199caf0c))

That code looks almost identical to the single-threaded version!
Notably, there are no `.await` calls.

If `read_contents` was part of a public API, it could be used by both async and
sync callers and you would not be forced to initialize a runtime to use it.

If the function were _async_ however and you called it outside of a runtime, the code
would compile, but not do anything at runtime. Futures are _lazy_ and only run when being
polled. This is a common footgun for newcomers.

```rust
async fn read_contents<T: AsRef<Path>>(file: T) -> Result<String, Box<dyn Error>> {
    // ...
}

#[tokio::main]
async fn main() {
    read_contents("foo.txt"); // This will print a warning, but it would compile
}
```

([Link to playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=7dc4bc6783691c42fbf4cd5a76251da2))

In a recent benchmark, [async Rust was 2x
faster than threads](https://vorner.github.io/async-bench.html), but the **absolute** difference
was only _10ms per request_. In other words, the difference is negligible for most
applications.
For comparison, [this about as long as Python or PHP take to start](https://github.com/bdrung/startup-time).

Frameworks based on threads can easily handle [tens of thousands
of requests per second](https://github.com/iron/iron#performance)
and modern Linux can handle tens of [thousands of
threads](https://thetechsolo.wordpress.com/2016/08/28/scaling-to-thousands-of-threads/).

Turns out, computers are pretty good at doing multiple things at once nowadays.

Async Rust is likely more memory-efficient than threads, at the cost of added
complexity. Even the async book
[acknowledges this](https://rust-lang.github.io/async-book/01_getting_started/02_why_async.html#async-vs-threads-in-rust):

> If you don't need async for performance reasons, threads can often be the
> simpler alternative.

I would like to add that threaded code in Rust undergoes the same stringent
safety checks as the rest of your Rust code: It is protected from data races,
null dereferences, and dangling references, ensuring a level of thread safety
that prevents many common pitfalls found in concurrent programming,
so some of the traditional arguments against threads do not apply to Rust.

## How to Improve The State Of Async Rust

Currently, Rust's core language and its standard library offer just the absolute
essentials for `async/await` capabilities. The bulk of the work is done in
crates developed by the Rust community. This is a good thing as it allows the
community to iterate on async Rust before it is stabilized.

The abstractions we have are relatively conservative in their
guarantees.
In the definition of the `Future` trait you provided, there are no constraints
on the associated `Output` type to be `Send`, `Sync`, or `'static`.

```rust
pub trait Future {
    type Output;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

We should keep it that way as we continue to add new abstractions.

## So What?

My original intention was to advice people to just skip async Rust for now and
wait until the ecosystem has matured. However, I since realized that this is not
feasible given that lot of libraries are async-only and new users will get in
touch with async Rust one way or another.

Instead, I would recommend to use async Rust only when you really need it.
Learn how to write synchronous Rust first and then maybe move on to async Rust.

If you have to use async Rust, stick to Tokio and well-established libraries
like [reqwest](https://github.com/seanmonstar/reqwest) and
[sqlx](https://github.com/launchbadge/sqlx). In your own code, try to avoid
async-only public APIs to make downstream usage easier.

In binary crates, think twice if you really need to use async. It's probably
easier to just spawn a thread and get away with blocking I/O. In case you have a
CPU-bound workload, you can use [rayon](https://github.com/rayon-rs/rayon) to
parallelize your code.

If you _really_ need async, consider isolating your
async code from the rest of your application. Keep your domain logic synchronous
and only use async for I/O and external services.

Following these guideliens will make your code [more
composable](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/)
and accessible.
On top of that, the error messages of sync Rust are much easier to reason about
than those of async Rust.

**Inside Rust, there is a smaller, simpler language that is waiting to get out.
It is this language that most Rust code should be written in.**
