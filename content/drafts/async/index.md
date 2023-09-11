+++
title = "The State of Async Rust"
date = 2023-09-07
template = "article.html"
[extra]
series = "Commentary"
reviews = []
+++

Recently, I found myself returning to a compelling series of blog posts 
titled [Zero-cost futures in Rust](https://aturon.github.io/blog/2016/08/11/futures/) by Aaron Turon about what would become the foundation of Rust's async ecosystem.

This series stands as a cornerstone in writings about Rust.
People like Aaron are the reason why I wanted to be part of the Rust
community in the first place.

While 2016 evokes nostalgic memories of excitement and frevor surrounding async Rust, my sentiments regarding the current state of its ecosystem are now somewhat ambivalent.

## Why Bother?

With this article, I hope to address two different audiences:

- Newcomers to async Rust, seeking to get an overview of the current state of
  the ecosystem.
- Library maintainers and contributors to the async ecosystem, in the hope that
  my perspective can be a basis for discussion about the future of async Rust.
  
I recently came across an article titled ['Async Rust Is A Bad Language'](https://bitbashing.io/async-rust.html). Though that article presents a bold perspective, I found it somewhat wanting in depth and evidence. 
My intention with this post is to provide a comprehensive view backed by 
references, hoping to give readers a more nuanced perspective.
It's worth noting that the timing of our publications is purely coincidental.

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

Moreover, much of the existing documentation on async Rust feels outdated or incomplete. For example, the async book remains in draft,
with concepts like `FuturesUnordered` yet to be covered.
(There is an open [pull request](https://github.com/rust-lang/async-book/pull/96), though.)

That leaves us with a situation that it unsatisfactory for everyone involved:

- For new users, it is a big ask to [navigate this space](https://github.com/rust-netlink/netlink-proto/issues/7) and make future-proof (no pun intended) decisions.
- For experienced users and library maintainers, [supporting multiple runtimes is an additional burden](https://github.com/launchbadge/sqlx/issues/1669#issuecomment-1032132220). It's no surprise that popular crates like [`reqwest`](https://github.com/seanmonstar/reqwest) [simply insist on Tokio as a runtime](https://github.com/seanmonstar/reqwest/blob/master/Cargo.toml#L109).
  This close coupling is a known issue, which is [acknowledged by the async working group](https://github.com/rust-lang/wg-async/issues/45).

## The case of `async-std`

`async-std` was an attempt to create an alternative runtime that is closer to
the Rust standard library. Its promise was that you could almost use it as a
drop-in replacement for the standard library.

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

However, looking at the commits over time `async-std` is essentially abandoned as there is [no active
development anymore](https://github.com/async-rs/async-std/graphs/contributors):

![Fading async-std contribution graph on Github](async-std-github.svg)

This leaves those reliant on the [`async-std`
API](https://docs.rs/async-std/latest/async_std/) – be it for concurrency mechanisms, extension traits, or otherwise – in an unfortunate situation,
as is the case for libraries developed on top of `async-std`, such as
[`surf`](https://github.com/http-rs/surf).
The core of `async-std` is now powered by [`smol`](https://github.com/smol-rs/smol), but it is probably best to use it directly for new projects.

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

Partially, this is because Tokio had a pioneering role in async Rust. It explored the design space as it went along. And while you could exclusively use the runtime and ignore the rest, it is easier and more common to buy into the entire ecosystem.

However, my main concern with Tokio is that it makes a lot of assumptions about how async code should be written and where it runs.

For example, [at the beginning of the Tokio documentation](https://docs.rs/tokio/latest/tokio/), they state:

> The easiest way to get started is to enable all features. Do this by enabling the full feature flag:
> ```rust
> tokio = { version = "1", features = ["full"] }
> ```

This sets up a [multi-threaded runtime](https://docs.rs/tokio/latest/tokio/attr.main.html) and mandates that types are `Send` and `'static`, which makes it
necessary to use synchronization primitives such as
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

Every time we use an `Arc` or a `Mutex` it's good idea to stop for a moment and
think about the future implications of that decision.

It's not only more inconvenient to write async code on top of these
synchronization primitives, they are also more expensive from a performance
perspective: Locking means runtime overhead and additional memory usage; in
embedded environments, these mechanisms are often not available at all.

On top of it, writing async code is a mental burden.

**Multi-threaded-by-default runtimes cause accidential complexity completely
unrelated to the task of writing async code.**

The entirety of async Rust is a minefield of leaky abstractions caused
by overengineering and bad defaults.
We should not have an explicit `spawn::blocking` , but a `spawn::async`.
Futures should not be expected to have a `'static` lifetime, but
exist within a small scope for a short period of time.

Maciej suggested to use a [local async
runtime](https://maciej.codes/2022-06-09-local-async.html) which is
single-threaded by default and does **not** require types to be `Send` and
`'static`.

I fully agree.

However, I have little hope that the Rust community will change
course at this point. Tokio is too deeply ingrained in the ecosystem already
and it feels like we're stuck with it.

Chances are, one of your dependencies pulls in Tokio anyway, at which point
you're forced to use it as well. At the time of writing, [Tokio is used at
runtime in 20,768 crates (of which 5,245 depend on it
optionally)](https://lib.rs/crates/tokio/rev).

![Runtime popularity bar chart between tokio, async-std, and smol with Tokio greatly dominating](runtimes.svg)

In spite of all this, we should not stop innovating in the async space!

## Other Runtimes

In that spirit, there are three other runtimes that are worth highlighting:

- [smol](https://github.com/smol-rs/smol): A small async runtime,
  which is easy to understand. The entire executor is around
  [1000 lines of code](https://github.com/smol-rs/async-executor/blob/master/src/lib.rs)
  with other parts of the ecosystem being similarly small.
- [embassy](https://github.com/embassy-rs/embassy): An async runtime for
  embedded systems.
- [glommio](https://github.com/DataDog/glommio): An async runtime for I/O-bound
  workloads, built on top of io_uring and using a thread-per-core model.

These runtimes are important, as they explore alternative paths or open up new
use cases for async Rust. [Similar to Rust's error handling
story](https://mastodon.social/@mre/111019994687648975), the hope is that
competing designs will lead to a more robust foundation in the long run.
Especially iterating on smaller runtimes that are less invasive and
single-threaded by default can help improve Rust's async story.

## Async vs Threads

No matter the runtime, we end up doing part of the Kernel's job in user space.
Modern operating systems come with highly optimized schedulers that are
designed to run many tasks in parallel and support async I/O through
[io_uring](https://lwn.net/Articles/776703/) and [splice](https://github.com/mre/fcat). We should make better use of these
capabilities.

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

We can call this function in the new [scoped threads](https://doc.rust-lang.org/std/thread/fn.scope.html):

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

Async Rust is likely more memory-efficient than threads, at the cost of
complexity and worse ergonomics. 
As an example, if the function were _async_ and you called it outside of a runtime, the code
would compile, but not do anything at runtime. Futures are _lazy_ and only run when being
polled. This is a common footgun for newcomers.

```rust
async fn read_contents<T: AsRef<Path>>(file: T) -> Result<String, Box<dyn Error>> {
    // ...
}

#[tokio::main]
async fn main() {
    // This will print a warning, but not do anything at runtime
    read_contents("foo.txt"); 
}
```

([Link to playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=7dc4bc6783691c42fbf4cd5a76251da2))

In a recent benchmark, [async Rust was 2x
faster than threads](https://vorner.github.io/async-bench.html), but the _absolute_ difference
was only _10ms per request_. In other words, the difference is negligible for most
applications.
For comparison, [this about as long as Python or PHP take to start](https://github.com/bdrung/startup-time).

Frameworks based on threads can easily handle [tens of thousands
of requests per second](https://github.com/iron/iron#performance)
and modern Linux can handle tens of [thousands of
threads](https://thetechsolo.wordpress.com/2016/08/28/scaling-to-thousands-of-threads/).

Turns out, computers are pretty good at doing multiple things at once nowadays.

As an important caveat, threads are not avaible or feasible in all environments,
such as embedded systems. My context for this article is primarily traditional
server-side applications that run on top of operating systems like Linux or
Windows.

I would like to add that threaded code in Rust undergoes the same stringent
safety checks as the rest of your Rust code: It is protected from data races,
null dereferences, and dangling references, ensuring a level of thread safety
that prevents many common pitfalls found in concurrent programming,
Since there is no garbage collector, there never will be any stop-the-world pause to reclaim memory.
Traditional arguments against threads simply don't apply to Rust;
fearless concurrency is your friend!

And if you need to share state between threads, consider to use
a channel:

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

As a summary, I would like to quote [the async book](https://rust-lang.github.io/async-book/01_getting_started/02_why_async.html#async-vs-threads-in-rust):

> If you don't need async for performance reasons, threads can often be the
> simpler alternative.

## Rust Web Frameworks

If you allow me one last digression, I would like to talk about Rust web
frameworks for a moment.

Why does every web framework in Rust have to be async-first?

I don't know about your use cases, but I usually write simple CRUD applications
that fetch data from a database and render it as HTML.
From time to time, I might need to call an external API, but that's about it.
An async-first web framework just isn't worth the trouble.

And even if I had a use case for async, I would *still* prefer to use a
single-threaded runtime to avoid the complexity of synchronization primitives.
If your primary concern is I/O-bound work (like handling many simultaneous
connections that are mostly waiting on I/O), then even a single-threaded Tokio
runtime can handle thousands to tens of thousands of simultaneous connections,
depending on the nature of the tasks and the specifics of the environment.

I would like to see more web frameworks that are synchronous by default and
allow you to opt into async when needed.
We should resist the tendency to annotate our `main` function with `#[tokio::main]`.

```rust
#[get("/")]
fn index() -> impl Response {
    let users = db::get_users();
    Response::ok().body(render_template("index.html", users))
}

// A route, which profits from concurrent IO
// It sends multiple requests to an external API and aggregates the results
// Note how the function itself is does not need to be async 
#[get("/users")]
fn users(count: usize) -> impl Response {
    // Start a local, single-threaded runtime with smol's async-executor
    let rt = smol::LocalExecutor::new();
    
    // Run the async code on the runtime
    let results = rt.run(async {
        let mut results = Vec::new();
        for id in 0..count {
            let result = reqwest::get(format!("https://api.example.com/users/{}", id)).await?;
            results.push(result);
        }
        Ok(results)
    });
    
    Response::ok().body(render_template("users.html", results))
}

// This does not need to be async either
// In the background, it might use a thread pool to handle multiple requests
fn main() -> Result<()> {
    let app = App::new()
        .mount("/", index)
        .mount("/users", users)
        .run();
}
```

## So What?

### Use Async Rust Sparingly

My original intention was to advice newcomers to just skip async Rust for now
and wait until the ecosystem has matured. However, I since realized that this is
not feasible given that lot of libraries are async-only and new users will get
in touch with async Rust one way or another.

Instead, I would recommend to use async Rust only when you really need it.
Learn how to write synchronous Rust first and then maybe move on to async Rust.

If you have to use async Rust, stick to Tokio and well-established libraries
like [reqwest](https://github.com/seanmonstar/reqwest) and
[sqlx](https://github.com/launchbadge/sqlx). In your own code, try to avoid
async-only public APIs to make downstream usage easier.

However, it's important to know that there are alternatives to Tokio
and that they are worth exploring.

### Consider The Alternatives

Currently, Rust's core language and its standard library offer just the absolute
essentials for `async/await` capabilities. The bulk of the work is done in
crates developed by the Rust community.
We should make more use of this possibility to iterate on async Rust and
experiment with different designs before we settle on a final solution.

In binary crates, think twice if you really need to use async. It's probably
easier to just spawn a thread and get away with blocking I/O. In case you have a
CPU-bound workload, you can use [rayon](https://github.com/rayon-rs/rayon) to
parallelize your code.

### Isolate Async Code

If you _really_ need async, consider isolating your
async code from the rest of your application. 
Keep your domain logic synchronous
and only use async for I/O and external services.
Following these guidelines will make your code [more
composable](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/)
and accessible.
On top of that, the error messages of sync Rust are much easier to reason about
than those of async Rust.

### Keep It Simple

The default mode for writing Rust should be synchronous.

**Inside Rust, there is a smaller, simpler language that is waiting to get out.
It is this language that most Rust code should be written in.**
