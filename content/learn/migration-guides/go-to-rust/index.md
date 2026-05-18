+++
title = "Migrating from Go to Rust"
date = 2026-05-19
template = "article.html"
[extra]
series = "Migration Guides"
icon = "go.svg"
resources = [
  "[Rust vs Go: A Hands-On Comparison (Shuttle)](https://www.shuttle.dev/blog/2023/09/27/rust-vs-go-comparison): a longer, code-heavy comparison I wrote with the Shuttle team",
  "[Go vs Rust? Choose Go. (2017)](https://endler.dev/2017/go-vs-rust/): an earlier post of mine on the same topic",
  "[Discussion on Lobste.rs](https://lobste.rs/s/g44oeq/rust_vs_go_hands_on_comparison): the comment thread on the Shuttle article, with several points that informed this guide",
  "[Finding duplicate words: Go vs Rust (YouTube)](https://www.youtube.com/watch?v=dSoP7EF2YJ4): a side-by-side concurrent program in both languages",
  "[JetBrains State of Developer Ecosystem 2024](https://www.jetbrains.com/lp/devecosystem-2024/): source for the Go usage figures cited in this guide",
]
+++

Out of all the migrations I help teams with, Go to Rust is a bit of an outlier. 
It's not a question of "is Rust faster?" or "does Rust have types?", Go already gets you most of the way there.
The discussion is mostly about **correctness guarantees**, **runtime tradeoffs**, and **developer ergonomics**.

A quick disclaimer before we start: this guide is **heavily backend-focused**.
Backend services are where Go is strongest, small static binaries, a standard library focused on networking, and an ecosystem of libraries for HTTP servers, gRPC, databases, etc.

That's also where most teams considering Rust are coming from (at least the ones who reach out to me), so I think that's the comparison that's actually useful in practice. 
If you're writing CLI tools, embedded firmware, or game engines, some of this still applies, but to be honest, I I'm afraid this is not the best resource for you. 

For context, I've written about Go and Rust before: ["Go vs Rust? Choose Go."](https://endler.dev/2017/go-vs-rust/) back in 2017, and later the ["Rust vs Go: A Hands-On Comparison"](https://www.shuttle.dev/blog/2023/09/27/rust-vs-go-comparison) with the Shuttle team, which walks through a small backend service in both languages.

{% info(title="What you will learn in this article") %}

- Where Go and Rust overlap, and where they diverge.
- How Go patterns map to Rust.
- What you gain from the borrow checker.
- Where I tell people to keep Go and where Rust is worth the migration cost .
- How to migrate Go services incrementally.

{% end %}

## Where I'm Coming From 

I'll be upfront: I'm not a fan of Go. I think it's a *badly designed* language, even if a very successful one. It confuses [*easiness* with *simplicity*](https://www.youtube.com/watch?v=SxdOUGdseq4), and several of its core design tradeoffs (`nil` everywhere, error handling as a discipline rule rather than a type, the long absence of generics) point in a direction I disagree with.
That said, success matters! Go has captured a real and persistent share of working developers, hovering around 17–19% in the JetBrains Developer Ecosystem Survey. Rust is growing steadily but is still a smaller slice:

![Go and Rust usage among developers, 2017–2024. Go holds steady around 17–19%; Rust has grown from 2% to 11%.](go-usage.svg)

Go is clearly working for a lot of people, and a guide that pretends otherwise isn't helpful.
So I'll do my very best to be objective in this guide rather than relitigate old arguments. But you should know my priors so you can calibrate.

The other prior worth disclosing: I run a Rust consultancy; of course I'm biased!
More people using Rust is good for my business.
But I've also worked in both languages professionally and shipped Go services to production.

This guide is for Go developers who want an honest, side-by-side look at what changes when you move to Rust.

For a deliberately opposite take, I recommend reading ["Just Fucking Use Go"](https://blainsmith.com/articles/just-fucking-use-go/) by Blain Smith. Holding both views in your head at once is more useful than either one alone.

If you prefer to watch rather than read, here's a video from the Shuttle article above, read and commented by the Primeagen: 

{{ yt(id="dSoP7EF2YJ4", title="Finding duplicate words: Go vs Rust") }}

## A First Look At The Most Important Commands

Go developers already have one of the cleanest toolchains in the industry.
Back in the day, it started off a trend of "batteries included" toolchains that give you a single, consistent interface for building, testing, formatting, linting, and managing dependencies. I'm glad that Rust followed suit, because it's a great model. It's one of my favorite parts about both ecosystems.

`cargo` has even more built-in:

| Go tool                      | Rust equivalent             | Notes                                                                  |
| ---------------------------- | --------------------------- | ---------------------------------------------------------------------- |
| `go.mod` / `go.sum`          | `Cargo.toml` / `Cargo.lock` | Project config and dependency manifest                                 |
| `go get` / `go mod tidy`     | `cargo add` / `cargo update`| Add and resolve dependencies                                           |
| `go build`                   | `cargo build`               | Compile the project                                                    |
| `go run .`                   | `cargo run`                 | Build and run                                                          |
| `go test ./...`              | `cargo test`                | Testing built into the toolchain                                       |
| `go vet ./...`               | `cargo clippy`              | Linter, Clippy is significantly more opinionated than `vet`           |
| `gofmt` / `goimports`        | `cargo fmt`                 | Auto-formatter, zero config                                            |
| `golangci-lint run`          | `cargo clippy -- -D warnings` | Strict lint mode                                                     |
| `go install ./cmd/foo`       | `cargo install --path .`    | Install a binary                                                       |
| `go doc`                     | `cargo doc --open`          | Generate and view API docs                                             |
| `pprof`                      | `cargo flamegraph` / `samply` | CPU profiling                                                        |
| `govulncheck`                | `cargo audit`               | Vulnerability scanning against an advisory database                    |

The big difference is that in Go you typically reach for third-party tools (`golangci-lint`, `mockgen`, `air`, `goreleaser`) to fill gaps.
In Rust, the first-party ecosystem covers more out of the box.
Things that *do* require external crates (e.g. `cargo watch`, `cargo nextest`) install with one command and feel native, e.g. `cargo install cargo-nextest` gives you `cargo nextest` right away.

Both communities have converged on the same insight about formatters: a single canonical style, even an imperfect one, is worth more than the bikeshedding it eliminates.

> Gofmt's style is no one's favorite, yet gofmt is everyone's favorite.
>
> — Rob Pike, [Go Proverbs](https://go-proverbs.github.io/)

The same is true of `rustfmt`: not everyone likes every detail, but the absence of style debates in code review is worth far more than the occasional formatting preference you'd have made differently.

## Key Differences Between Go and Rust

|                       | Go                                             | Rust                                                   |
| --------------------- | ---------------------------------------------- | ------------------------------------------------------ |
| Stable Release        | 2012                                           | 2015                                                   |
| Type System           | Static, structural, generics since 1.18        | Static, nominal, generics + traits + lifetimes         |
| Memory Management     | Garbage collected (concurrent, low-pause)      | Ownership and borrowing, no GC                         |
| Null Safety           | `nil` is everywhere                            | No null; `Option<T>` is the type-level replacement     |
| Error Handling        | `error` interface, `if err != nil { ... }`     | `Result<T, E>`, `?` operator, exhaustive matching      |
| Concurrency           | Goroutines + channels (CSP)                    | `async`/`await` on `tokio` + channels + threads        |
| Cancellation          | `context.Context` (convention, not enforced)   | `CancellationToken` / explicit, type-checked plumbing  |
| Data Races            | Caught at runtime via `-race` (probabilistic, at runtime) | Caught at **compile time** by `Send`/`Sync`            |
| Compile Times         | Very fast                                      | Slow, especially clean builds                          |
| Runtime               | ~2 MB Go runtime + GC                          | None beyond `libc` (or fully static with MUSL)         |
| Binary Size           | Small to medium (a few MB)                     | Comparable; very small with `panic = "abort"` + LTO    |
| Learning Curve        | Gentle                                         | Steep                                                  |
| Ecosystem Size        | ~750k+ modules                                 | 250,000+ crates                                        |

The headline is that Go and Rust are both compiled, statically typed, single-binary-deploy languages with strong concurrency stories.
The differences are about **what guarantees you get from the compiler** and **how much control you have over runtime behaviour**.

## Why Go Developers Consider Rust

Go developers don't usually come to Rust because Go is "too slow."
For most backend workloads, Go is plenty fast.
People are generally a bit frustrated with Go's verbose error handling, the danger of segmentation faults from `nil` pointers, and the lack of generics (for a long time) or any sophisticated type system features, such as enums or traits. Interfaces are not a worthy replacement for traits, and the Go standard has some weird gaps, such as the lack of a `Set` type.

### `nil` Panics in Production

> I call it my billion-dollar mistake. It was the invention of the null reference in 1965 … This has led to innumerable errors, vulnerabilities, and system crashes, which have probably caused a billion dollars of pain and damage in the last forty years.
>
> — Tony Hoare, inventor of `null`, [QCon London 2009](https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare/)

This is the one I hear most often.
You ship a Go service, it runs fine for months, and then one Tuesday at 3 a.m. a code path runs where someone forgot to check whether a pointer was `nil`, and the goroutine panics.

```go
func (s *Service) Handle(req *Request) error {
    user := s.repo.Find(req.UserID) // returns *User, may be nil
    return user.Notify()             // boom if nil
}
```

Go's compiler does not force you to consider the absence case.
Rust's `Option<T>` does:

```rust
fn handle(&self, req: &Request) -> Result<(), ServiceError> {
    let user = self.repo.find(req.user_id)?;   // returns Option<User>; ? short-circuits None into an error
    user.notify()
}
```

You literally cannot dereference an `Option` without acknowledging the `None` case.
Whole categories of pager-duty incidents disappear.

### Data Races That `-race` Didn't Catch

`go test -race` is a great tool, but it's a runtime detector, it only finds races that *actually execute* during your tests.
Mutating a map from two goroutines without a lock compiles fine in Go and only blows up in production under load.

In Rust, sharing mutable state across threads requires types that implement `Send` and `Sync`.
Try to share a plain `HashMap` between threads and **the program does not compile**.
You're forced to wrap it in an `Arc<Mutex<...>>`, an `Arc<RwLock<...>>`, or use a channel.
The race condition becomes a type error, not a Tuesday-at-3-a.m. error.

### Composable Error Handling

`if err != nil { return err }` is fine for a while.
After a few years, you notice three things:

1. The boilerplate dilutes the actual logic of your function.
2. Wrapping with `fmt.Errorf("doing X: %w", err)` is a discipline rule, not a compiler rule. It's easy to drop context on the floor.
3. Sentinel errors via `errors.Is`/`errors.As` work, but the compiler doesn't tell you when you forgot to handle a new variant.

It's worth being honest about the counter-argument here, since it came up in the [Lobste.rs thread](https://lobste.rs/s/g44oeq/rust_vs_go_hands_on_comparison) on my Shuttle article: experienced Go developers point out that `errcheck` and `golangci-lint` catch most of the "forgot to handle the error" cases in practice, and that explicit `if err != nil` is *easier to read* than dense `?` chains.
Both points are fair, and the explicit style is a deliberate cultural value, not an accident:

> I think that error handling should be explicit, this should be a core value of the language.
>
> — Peter Bourgon, [GoTime #91](https://changelog.com/gotime/91), quoted in Dave Cheney's [Zen of Go](https://dave.cheney.net/2020/02/23/the-zen-of-go)

My take is that lints are an opt-in safety net you have to remember to set up, while Rust's `Result<T, E>` is the type signature itself, there's no way to forget. The boilerplate-vs-readability tradeoff is more genuinely subjective.

In Rust:

```rust
#[derive(Debug, thiserror::Error)]
pub enum UserError {
    #[error("user {0} not found")]
    NotFound(UserId),
    #[error("user already exists")]
    AlreadyExists,
    #[error(transparent)]
    Repo(#[from] RepoError),
}

pub fn rename(id: UserId, name: &str) -> Result<User, UserError> {
    let mut user = repo::get(id)?;        // ? converts RepoError -> UserError automatically
    user.name = name.to_string();
    Ok(user)
}
```

The `?` operator handles propagation; `#[from]` handles wrapping; and a `match` on `UserError` is **exhaustively checked**.
Add a new variant tomorrow and the compiler shows you every place that needs updating.

### Generics That Don't Box

Go got generics in 1.18, and they're useful, but the implementation has constraints (no methods with type parameters, GC shape stenciling, occasional surprising performance characteristics).
Rust generics monomorphize, each instantiation produces specialized code with zero runtime cost.
Combined with traits, this gives you real zero-cost abstractions.

This matters less in handler code and more in shared infrastructure (middleware, generic repositories, decoders, parsers), where Go often pushes you back to `interface{}`/`any` plus type assertions.

### Predictable Latency

Go's GC is excellent, concurrent, low-pause, well-tuned for typical service workloads.
But "low-pause" is not "no-pause."
Under heavy allocation, P99 latency tails are noticeably worse than a Rust equivalent that simply doesn't allocate on the hot path.

I won't oversell this, for the vast majority of services, Go's GC is a non-issue.
But for latency-sensitive systems (trading, real-time bidding, network proxies, high-throughput ingestion), the lack of GC pauses is a genuine selling point.

### In Summary

Go is death by a thousand paper cuts. It is a very pragmatic language and if you are willing to glance over the above issues, you can be very productive in it. But at a certain codebase size, the problems start to compound.
There is no single moment when Go loses its appeal, but teams find themselves wishing for more (more safety, more control, more expressiveness) and that's when they start looking around for alternatives.

## Comparing Both Languages Side by Side

The fastest way to feel comfortable in Rust is to map patterns you already know.
For a longer, fully-worked example of building the same backend service in both languages, see the [Shuttle comparison](https://www.shuttle.dev/blog/2023/09/27/rust-vs-go-comparison), the section below focuses on the patterns that come up most often.

### Error Handling: `if err != nil` vs `Result<T, E>`

Go:

```go
func ReadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("reading config: %w", err)
    }
    var cfg Config
    if err := json.Unmarshal(data, &cfg); err != nil {
        return nil, fmt.Errorf("parsing config: %w", err)
    }
    return &cfg, nil
}
```

Rust:

```rust
fn read_config(path: &Path) -> Result<Config, ConfigError> {
    let data = fs::read_to_string(path)?;
    let cfg = serde_json::from_str(&data)?;
    Ok(cfg)
}
```

The `?` operator does the `if err != nil { return err }` dance for you, including type conversion if `From<E1> for E2` is implemented (idiomatic with `thiserror`'s `#[from]`).

### Null: `nil` vs `Option<T>`

Go:

```go
func GetUser(id string) *User {
    for _, u := range users {
        if u.ID == id {
            return &u
        }
    }
    return nil
}

u := GetUser("123")
fmt.Println(u.Name) // panics if nil
```

Rust:

```rust
fn get_user(id: &str) -> Option<User> {
    users.iter().find(|u| u.id == id).cloned()
}

let user = get_user("123");
println!("{}", user.name); // compile error: `user` is Option<User>, not User
// You must handle both cases:
match get_user("123") {
    Some(u) => println!("{}", u.name),
    None    => println!("not found"),
}
```

There is no `nil` in safe Rust. References can't be null. Pointers can be, but you almost never use raw pointers in application code.

### Interfaces vs Traits

Go's interfaces are structural, a type satisfies an interface implicitly:

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

Rust's traits are nominal, you implement them explicitly:

```rust
pub trait Reader {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize>;
}

impl Reader for MyType {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> { /* ... */ }
}
```

The Go style is great for ad-hoc duck typing.
The Rust style is great for refactoring and discoverability, you can grep for every implementer of a trait.

The closest equivalent of `interface{}` / `any` in Rust is `Box<dyn Any>`, but you almost never want it. The Go community knows the cost of reaching for `interface{}` too:

> interface{} says nothing.
>
> — Rob Pike, [Go Proverbs](https://go-proverbs.github.io/)

Generic functions with trait bounds (`fn handle<R: Reader>(r: R)`) cover the vast majority of cases and give you monomorphization with no runtime dispatch. Where Go pre-1.18 would have forced you back to `interface{}` plus a type assertion, Rust's traits + generics let you stay specific.

When you do want runtime dispatch (e.g. heterogeneous storage of different implementers), reach for `Box<dyn Trait>` or `Arc<dyn Trait>`. That's the direct Rust analog of holding an `interface` value in Go.

### Goroutines vs Async Tasks

Go's concurrency model is famously simple:

```go
go doWork(ctx, input)
```

Goroutines are cheap, the runtime schedules them across OS threads, and channels (`chan T`) are the primary coordination primitive. The Go proverb captures the philosophy:

> Don't communicate by sharing memory; share memory by communicating.
>
> — Rob Pike, [Go Proverbs](https://go-proverbs.github.io/)

This is the area where Go genuinely shines, several commenters in the [Lobste.rs discussion](https://lobste.rs/s/g44oeq/rust_vs_go_hands_on_comparison) made the point that goroutines "just disappear" into normal-looking blocking code, and that's worth giving Go credit for. Rust async is more powerful, but it's also more visible in your code.

Rust uses `async`/`await` on top of an executor (almost always `tokio` for backend services):

```rust
tokio::spawn(async move {
    do_work(input).await;
});
```

The shape is similar. The differences:

- Rust async functions return `Future`s. They don't run until awaited or spawned.
- The compiler tracks `Send`/`Sync` across `.await` points. If you hold a non-`Send` value across an await, you get a compile error explaining exactly why.
- There's no built-in goroutine-style preemption. Long CPU-bound work in an async task starves the executor; you offload to `tokio::task::spawn_blocking` or `rayon` instead.
- Channels (`tokio::sync::mpsc`, `broadcast`, `watch`) are first-class but live in libraries, not the language.

For most backend code, the day-to-day feel is similar: spawn a task, communicate via channels, use timeouts liberally.

### `context.Context` vs `CancellationToken`

In Go, you plumb a `context.Context` through every blocking call:

```go
func (s *Service) Fetch(ctx context.Context, id string) (*User, error) {
    return s.client.Get(ctx, "/users/"+id)
}
```

Rust has no built-in `context.Context`. The closest equivalent for cancellation is `tokio_util::sync::CancellationToken`:

```rust
pub async fn fetch(&self, token: CancellationToken, id: &str) -> Result<User, FetchError> {
    tokio::select! {
        _ = token.cancelled() => Err(FetchError::Cancelled),
        res = self.client.get(&format!("/users/{id}")) => res,
    }
}
```

For timeouts, `tokio::time::timeout(dur, fut)` wraps any future.
For deadlines/values, you typically pass them as explicit arguments or via `tracing` spans rather than a single context object.

Some Go developers miss the implicit-feel of `ctx`. In practice, the explicit Rust style is easier to reason about, you always know exactly what's cancellable and what isn't. The deeper point is that *neither* language gives you cancellation for free, the discipline just shows up at different layers:

> Go doesn't have a way to tell a goroutine to exit. There is no stop or kill function, for good reason. If we cannot command a goroutine to stop, we must instead ask it, politely.
>
> — Dave Cheney, [The Zen of Go](https://dave.cheney.net/2020/02/23/the-zen-of-go)

In Go that "asking politely" is a `context.Context` plumbed through every call site by convention. In Rust it's a `CancellationToken` (or a `watch` channel) plumbed through every call site, but the compiler can actually tell you when you forgot.

### Channels

Both languages have channels. The translation is direct:

```go
ch := make(chan int, 10)
go func() {
    ch <- 42
}()
v := <-ch
```

```rust
let (tx, mut rx) = tokio::sync::mpsc::channel::<i32>(10);
tokio::spawn(async move {
    tx.send(42).await.unwrap();
});
let v = rx.recv().await.unwrap();
```

Rust's channels distinguish sender and receiver as separate types, which makes ownership and `Send`-ness explicit at the type level.

### Structs and Methods

Go:

```go
type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}
```

Rust:

```rust
pub struct Circle {
    pub radius: f64,
}

impl Circle {
    pub fn area(&self) -> f64 {
        std::f64::consts::PI * self.radius * self.radius
    }
}
```

Rust's `&self` is the equivalent of a Go value receiver; `&mut self` is a pointer receiver with mutation. Owned `self` (consuming the value) has no Go analog and is occasionally very useful (typestate, builders).

### Strings: `string` vs `String` and `&str`

Go's `string` is a UTF-8 byte slice with copy-on-assign semantics (the header is copied, the underlying bytes are shared and immutable).
Rust splits this into two types:

- `String`, owned, heap-allocated, growable. Equivalent to `[]byte` you intend to mutate.
- `&str`, a borrowed view into someone else's string data. Equivalent to a Go `string` *parameter* most of the time.

As a rule of thumb, take `&str` in arguments, return `String` when you produce new data.

```rust
fn greet(name: &str) -> String {
    format!("Hello, {name}")
}
```

This is mostly painless once you internalize it. The `&str` vs `String` split is a microcosm of Rust's broader "borrow vs own" model.

## Go Generics Are Too Little, Too Late

Go got generics in 1.18 (March 2022), thirteen years after the language shipped.
They are useful, but they feel tacked on, and in practice they have most of the *downsides* of a generic type system without delivering the *upsides* you'd expect coming from Rust, Haskell, or even modern C++.

This is a strong claim, so let me back it up.

### The Standard Library Barely Uses Them

The most telling signal is that three years after generics landed, Go's own standard library still mostly avoids them.
`sort.Slice` still takes a `func(i, j int) bool` closure instead of a `cmp.Ordered` constraint.
`sync.Map` is still typed as `any`/`any`.
The generic helpers that *do* exist live in a small handful of packages: `slices`, `maps`, `cmp`, and a few entries under `sync`.

Compare that to Rust, where generics permeate the standard library from day one: `Option<T>`, `Result<T, E>`, `Vec<T>`, `HashMap<K, V>`, `Iterator`, `From`/`Into`, `AsRef`, `Borrow`, every collection, every smart pointer.
You cannot write idiomatic Rust without using generics, because the standard library *is* generic.

In Go, generics are an opt-in feature for library authors who really need them. In Rust, they're the substrate everything else is built on.

### No Trait System, Just Structural Constraints

Rust's generics are tied to traits, which double as the language's mechanism for ad-hoc polymorphism, supertraits, associated types, blanket impls, and coherence.

Go's constraints are just interfaces with an extra `~` operator for type-set membership. There are no:

- **Supertraits / constraint hierarchies.** In Rust you write `trait Ord: Eq + PartialOrd`, and any `T: Ord` automatically satisfies `Eq` and `PartialOrd`. Go has no equivalent; you stack interface embeddings, but the constraint solver doesn't reason about hierarchies the way Rust's trait system does.
- **Associated types.** Rust's `Iterator` has `type Item;`, so `T::Item` is a first-class thing you can name in bounds. Go's closest equivalent is a second type parameter, which leaks into every signature.
- **Blanket impls.** In Rust, `impl<T: Display> ToString for T` automatically gives every `Display` type a `to_string()` method. Go has no way to add methods to a type from outside its defining package, generic or not.
- **Methods with their own type parameters.** This is an explicit, [documented](https://go.googlesource.com/proposal/+/refs/heads/master/design/43651-type-parameters.md#No-parameterized-methods) non-feature in Go. You cannot write `func (s Set[T]) Map[U](f func(T) U) Set[U]`. In Rust, generic methods on generic types are routine.

The practical consequence is that the moment your abstraction needs more than "a function that works for any `T` with these few operations," Go pushes you back to `any` plus type assertions, code generation, or runtime reflection.

### Type Inference Stops at the Function Boundary

Rust uses a Hindley-Milner-style inference engine that propagates type information through entire expressions, including across closures, iterator chains, and `?` operators. You routinely write:

```rust
let evens: Vec<_> = (0..100).filter(|n| n % 2 == 0).collect();
```

and the compiler figures out `_` is `i32` from the range, and `Vec<_>` is `Vec<i32>` from the `collect` target.

Go's inference is much shallower. It can usually infer type parameters from function arguments, but it [cannot infer from return-position context](https://go.dev/blog/type-inference), cannot chain inference through generic builders the way Rust does, and frequently forces explicit type arguments at call sites:

```go
result := slices.Collect[int](iter)  // often required
```

In Rust this is the exception; in Go it's still common.

### Monomorphization vs GC Shape Stenciling

Rust monomorphizes: every `Vec<i32>` and `Vec<String>` produces specialized machine code with zero runtime dispatch. Go uses [GCShape stenciling with dictionaries](https://go.googlesource.com/proposal/+/refs/heads/master/design/generics-implementation-gcshape.md), where types that share a "GC shape" share the same compiled function and dispatch through a dictionary at runtime.

The result is a compile-time/runtime tradeoff that often surprises people: generic Go code can be measurably *slower* than the equivalent hand-written non-generic version, because every method call on a type parameter goes through an indirection. There's a [well-known PlanetScale post](https://planetscale.com/blog/generics-can-make-your-go-code-slower) showing exactly this.

In Rust, generic code is the *fast* path. Reaching for `dyn Trait` (the equivalent of Go's interface dispatch) is a deliberate choice you make when you want runtime polymorphism.

### They Don't Plaster Over Holes In The Type System

This is the part that bothers me most.

A good generics system *removes* reasons to fall back to escape hatches. In Rust, generics + traits eliminate most of what you'd otherwise need `Box<dyn Any>` or runtime reflection for. The type system gets stronger.

In Go, generics did not remove `any`, did not remove `reflect`, did not remove code generation as the dominant pattern for things like ORMs, decoders, and mocks. `encoding/json` still uses reflection. `database/sql` still uses `any`. `mockgen` still generates code. The places where a real generics system would shine are the same places Go reaches for runtime mechanisms it had before 1.18.

Generics in Go feel additive, a new tool in the box that's useful in narrow cases. Generics in Rust feel foundational; remove them and the language collapses.

That's the difference, and it's why generic Go code, in my experience, doesn't read better than the `interface{}`-based code it replaced; it just reads differently, with more punctuation.

## Popular Go Packages and Their Rust Counterparts

| Concern              | Go                                                | Rust                                              |
| -------------------- | ------------------------------------------------- | ------------------------------------------------- |
| HTTP server          | `net/http`, `chi`, `gin`, `echo`, `fiber`         | `axum` (on `hyper`)                               |
| HTTP client          | `net/http`, `resty`                               | `reqwest`                                         |
| gRPC                 | `google.golang.org/grpc` + `protoc-gen-go`        | `tonic` + `prost`                                 |
| OpenAPI (codegen)    | `oapi-codegen`                                    | `utoipa` (code-first) or `openapi-generator`      |
| SQL                  | `database/sql`, `sqlc`, `sqlx`, `gorm`            | `sqlx`, `sea-orm`, `diesel`                       |
| Migrations           | `golang-migrate`, `goose`                         | `sqlx migrate`, `refinery`                        |
| JSON                 | `encoding/json`, `sonic`, `goccy/go-json`         | `serde` + `serde_json`                            |
| Logging              | `log/slog`, `zerolog`, `zap`                      | `tracing` + `tracing-subscriber`                  |
| Metrics              | `prometheus/client_golang`                        | `metrics` + `metrics-exporter-prometheus`         |
| Config               | `viper`, `koanf`                                  | `config` (config-rs), `figment`                   |
| CLI                  | `cobra`, `urfave/cli`                             | `clap` (derive)                                   |
| Validation           | `go-playground/validator`                         | `validator`                                       |
| Errors               | `errors`, `pkg/errors`                            | `thiserror` (libraries), `anyhow` (binaries)      |
| Testing              | `testing`, `testify`, `gomega`                    | built-in `#[test]`, `rstest`, `assert_matches`    |
| Mocking              | `mockgen`, `moq`                                  | hand-written fakes (idiomatic), `mockall`         |
| HTTP mocking         | `httptest`                                        | `httpmock`, `wiremock-rs`                         |
| Real deps in tests   | `testcontainers-go`                               | `testcontainers`                                  |
| Retry/backoff        | `cenkalti/backoff`                                | `backon`                                          |
| Background tasks     | goroutines + `errgroup`                           | `tokio::spawn` + `JoinSet`                        |

If you're already opinionated in Go, the Rust ecosystem has converged to a similar level of "default picks." For a typical backend service: `axum` + `sqlx` + `tokio` + `tracing` + `serde` + `clap` covers 90% of what you need.

## Key Challenges in Transitioning to Rust

I want to be straightforward here. Coming from Go, [**you will hit a wall**](/blog/flattening-rusts-learning-curve/). The wall has a name.

### The Borrow Checker

Go's runtime handles memory and aliasing for you. Rust pushes that decision into the type system.
The first few weeks you'll write code that "should obviously work" and the compiler will refuse it.

The patterns that bite Go developers most often:

1. **Long-lived references.** In Go, you'd happily hold a `*User` from a map for as long as you want. In Rust, that borrow blocks mutation of the map for its whole lifetime. The fix is usually to clone, or to scope the borrow tighter.
2. **Self-referential structs.** Common in Go (a struct holding both data and an iterator over it). In Rust, this requires `Pin`, `ouroboros`, or a redesign. Almost always: redesign.
3. **Sharing mutable state across goroutines.** What you'd write as `mu sync.Mutex; data map[K]V` becomes `Arc<Mutex<HashMap<K, V>>>`. Slightly more verbose, much more checked.
4. **Returning references from functions.** [Lifetime annotations](/blog/lifetimes/) show up. They're not as bad as their reputation, but they're new.

With all of these rules, the borrow checker truly sounds like a "gatekeeper" of sorts, which keeps getting in the way and is just overall frustrating to deal with.
That is not the mental mindset you should have when learning Rust. 
The borrow checker truly uncovers real and very existing bugs in your code, and if you don't address them, your program will deal with safety issues.
So whenever you get a compiler error from `rustc`, take a step back and think how your code could break.
A few questions you can ask yourself:

- If a value *got moved* from one place to another, what would happen if the original place tried to use it again?
- If a value *is shared* across threads, what would happen if one thread modified it while another thread is using it?
- If a pointer *is dereferenced*, what would happen if it was null or dangling?
- When a value *goes out of scope*, what would happen if it was still being used somewhere else?

That is the mindset you need to understand the borrow checker.
Humans are genuinely bad at reasoning about memory.
We forget that pointers can be null, that old references can outlive the data they point to, and that multiple threads can touch the same data at the same time.
We tend to have a "linear" mental model of how data flows through a program, but in reality it's closer to a complex graph with many paths and interactions.
Every `if` condition forces you to consider what happens in *both* branches.
Every loop forces you to consider what happens on *every* iteration.
That is exactly the kind of reasoning the borrow checker is designed to do for you!
It enforces best practices at compile time, and it can feel annoying when your own mental model disagrees with the borrow checker's (which is the more accurate one 99% of the time).
There *are* cases where the borrow checker is genuinely too strict, but they are rare, and as a beginner you'll almost never run into them.
I got memory management wrong plenty of times in my early days, but I approached it with a *learner's mindset*, which helped me ask "what's wrong with my code?" instead of "what's wrong with the compiler?", a reaction I see a lot in trainings.

The good news is that once you internalize borrowing, it stops fighting you.
Most experienced Rust developers will tell you the borrow checker became an ally somewhere between weeks 4 and 12.
The first month is the hardest.

### Compile Times

Be honest with your team, Rust compile times are a real downgrade from Go's.
A clean release build of a medium service can take minutes in comparison to Go's near-instantaneous compiles.
Incremental builds and `cargo check` are reasonable and compile times have gotten much better over the years, but you'll feel the difference.

To mitigate, use `cargo check` in your edit loop, split into a workspace once it pays off, and keep proc-macro-heavy crates in their own crate so they only recompile when they change.
See [tips for faster Rust compile times](/blog/tips-for-faster-rust-compile-times/) for a deeper dive.

### Async Coloring

Go's "one type of function, sync everywhere, the runtime handles concurrency" is genuinely simpler than Rust's split between `fn` and `async fn`.
You'll need to think about which of your functions are async, where you `.await`, and how that interacts with traits.
Async traits (stable since Rust 1.75) help a lot, but there are still rough edges (especially around `dyn Trait` with async methods).

### Smaller Ecosystem in Some Niches

Rust's crate ecosystem is growing and libraries are high-quality across the board, but Go has a head start in some backend-adjacent domains: Kubernetes operators, cloud-provider SDKs, database drivers for certain niche stores.
Before you commit, spend a day checking that the libraries you depend on have Rust equivalents you're willing to use.
Teams I help often have to hand-roll at least one or two core libraries themselves. For example, they might have to update an abandoned crate for XML schema validation, or write their own client for a lesser-known protocol.

## Integration Strategies

You don't have to rewrite everything in one go. The strategies that work best, in order of how I usually recommend them:

### 1. Carve Off a Hot Path as a Service

If one specific service in your fleet is the perpetual problem child (high CPU, latency-sensitive, or constantly hit with reliability issues), rewrite *just that one* in Rust, behind the same API contract.
This is the lowest-risk migration. Other Go services keep talking to it via HTTP/gRPC, oblivious to the underlying language.

### 2. Replace a Sidecar / Worker Process

Background workers, queue consumers, ingestion pipelines, and CPU-bound batch jobs are excellent first targets.
They typically have a clear input/output boundary (a queue, a topic) and no shared in-process state with the rest of the system.

### 3. cgo Is Possible But Painful

You *can* call Rust from Go via cgo, and [there are good guides on how to do it](https://blog.arcjet.com/calling-rust-ffi-libraries-from-go/).
(Reach out if you'd be interested in a guide on this from me.)
In practice, I rarely recommend it for backend services.
The build complexity and FFI overhead usually outweigh the benefits compared to "just stand up a Rust service and put it behind a network call."
For libraries and CLI tools, it's more viable.

### 4. Strangler Pattern Behind a Gateway

If you have an API gateway or reverse proxy, you can route specific endpoints to a new Rust service while the rest stays in Go.
This works particularly well when one bounded context (auth, search, billing) is the right unit to migrate.
The pattern is often called ["strangler fig,"](https://martinfowler.com/bliki/StranglerFigApplication.html) because the new service grows around the old one until it eventually replaces it entirely.

## Practical Migration Tips

**Start with a service that has a clear boundary.** Don't pick the most central, most-deployed service in your fleet. Pick the one where the contract with the rest of the system is well-defined and the blast radius is small.

**Keep the same API contract.** If your Go service exposes a REST API, your Rust service should too: same paths, same JSON shapes, same error envelope. The migration is invisible to clients, and you can swap traffic incrementally with a gateway.

**Don't translate idioms verbatim.** Resist the urge to write Go-flavoured Rust. `if err != nil { return err }` becomes `?`. Goroutine-per-request becomes `tokio::spawn` only when you actually need it (axum already concurrently handles requests). Interfaces with one method usually become trait bounds on a generic, not `Box<dyn Trait>`.

**Use the compiler as a pair programmer.** Rust's compiler errors are usually pretty good. Read them slowly. They almost always tell you the right answer. The team members who struggle longest are the ones who fight the compiler instead of treating it as a collaborator.

**Invest in training early.** I've seen teams try to do a Rust migration "on the side," learning as they go. It rarely ends well.
It's a bit like training for a marathon by signing up for the race and then trying to run it without any prior training. You can do it, but it's going to be painful and you might not finish.
Block off real time for learning: a workshop, [an online course](https://course.corrode.dev/), paired sessions on real code. The upfront investment pays back many times over once the team is fluent.
(Hey, if you want to talk about training options, [I'm happy to chat](/services).)

## Keeping Go's Strengths

Not everything should be migrated.
Go is excellent for:

- **Kubernetes-native tooling**: operators, controllers, CRDs. The ecosystem is overwhelmingly in Go.
- **CLI utilities and dev tooling**: fast compiles, easy cross-compilation, simple deployment.
- **Glue services**: thin API layers, proxies, format converters. The boilerplate ratio in Rust isn't worth it here.
- **Anywhere your team velocity matters more than absolute correctness guarantees**.

A hybrid strategy is fine and common.
Many of the teams I work with end up with a polyglot backend: Go for the "boring" services, Rust for the ones where reliability and performance pay back the extra effort.

## Expected Improvements

Numbers vary wildly by workload, so take these as rough guidance. Not promises!
But here are some ballpark numbers, based on Go-to-Rust migrations I've helped with:

- CPU usage: 20–60% reduction. Less dramatic than Python-to-Rust, because Go is already efficient. The wins come from no GC and tighter loops.
- Memory: 30–50% reduction, mostly from the absence of GC overhead and a smaller runtime.
- P99 latency: significantly more consistent. Rust services tend to flatline where Go services have visible GC-induced jitter. (This has gotten much better on the Go-side ever since they introduced their low-latency GC, but the difference is still there under heavy load.)
- Production incidents: this is the one teams report most enthusiastically. The classes of bugs that survive `go test -race` and reach production (data races, nil dereferences, missed error paths) just don't compile in Rust. Oncall rotations are typically very boring after a Rust migration.

Honestly, you're unlikely to get a 10x throughput improvement going from Go to Rust the way you might from Python.
What you get is fewer "silly errors" and flatter latency tails, plus the ability to expand into other domains like embedded development or systems programming while still using the same language.
That's often the most surprising side-effect of a migration: there's a lot of opportunity for code-sharing across teams that previously had to use different stacks. You can use Rust for everything.

## Conclusion

Going from Go to Rust is a different kind of migration than coming from [Python](/learn/migration-guides/python-to-rust) or [TypeScript](/learn/migration-guides/typescript-to-rust).
Coming from Go, you know the benefits of a statically-typed, compiled language. So you're not trading away dynamic typing or a slow runtime, you're trading away `nil` in exchange for a more robust codebase with fewer footguns, and a stricter compiler that catches more mistakes at compile time. There is a steeper learning curve, however.

For [foundational services](/blog/foundational-software/) (services that your organization relies on, that have high uptime requirements, that are critical to your business), that trade is obviously worth it.
For others, Go remains the right answer.
The point of a migration is to put each problem in the language that solves it best.

{% info(title="Ready to Make the Move to Rust?", icon="crab") %}

I help backend teams evaluate, plan, and execute Go-to-Rust migrations.
Whether you need an architecture review, training, or hands-on help porting a critical service, [let's talk about your needs](/services).

{% end %}
