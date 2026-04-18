+++
title = "Migrating from TypeScript to Rust"
date = 2024-12-13
updated = 2026-04-10
template = "article.html"
draft = false
[extra]
series = "Migration Guides"
icon = "typescript.svg"
resources = [
    "[Syntax comparison between TypeScript and Rust - Robbie Cook](https://blog.robbie.digital/posts/typescript-to-rust)",
    "[My experience migrating TypeScript libraries to Rust - Patrick Desjardins](https://patrickdesjardins.com/blog/migrating-typescript-library-to-rust)",
    "[Node.js to Rust in 2024 - Pascal Poredda](https://pascal-poredda.de/blog/migrating-from-node-to-rust)"
]
+++

TypeScript excels at making JavaScript more maintainable.

However, eventually you'll hit its limits.
Those might be performance ceilings or a type system that can simply be bypassed with `any`.

A lot of my clients come to Rust after "outgrowing" TypeScript.
And for good reason, because Rust is a great next step with its strong type system and the absence of a garbage collector and `null` values.

Teams often ask me how to make the transition as smooth as possible, and what the differences between the two languages are.

That's why I wrote this guide, which maps what you already know in TypeScript directly to Rust; from the syntax, the patterns, all the way to the ecosystem and tooling.
Everything you need to hit the ground running.

And hey, if you have any questions, suggestions, or want to share your own experience migrating from TypeScript to Rust, feel free to reach out. Happy to help you and your team take the leap to Rust!

## A First Look At The Most Important Commands 

TypeScript developers are used to assembling a toolchain from multiple tools. Here's how Rust maps to your daily workflow:

| TypeScript tool           | Rust equivalent       | Notes                                                                        |
| ------------------------- | --------------------- | ---------------------------------------------------------------------------- |
| `tsconfig.json`           | `Cargo.toml`          | Project config and dependency manifest                                       |
| `npm` / `yarn`            | `cargo`               | Package manager, build tool, and task runner                                 |
| `ts-node` / `tsx`         | `cargo run`           | Run your project                                                             |
| `jest` / `vitest`         | `cargo test`          | Testing built into the toolchain                                             |
| `eslint`                  | `cargo clippy`        | Linter with actionable suggestions                                           |
| `prettier`                | `cargo fmt`           | Auto-formatter, zero config                                                  |
| `nodemon` / `tsx --watch` | `cargo watch`         | Re-run on file changes (install separately with `cargo install cargo-watch`) |
| `tsc --noEmit`            | `cargo check`         | Fast type-check without a full build                                         |

As you can see, **everything comes with Rust**. There's no decision fatigue around which test framework, formatter, or linter to use. The ecosystem has converged on `cargo` as the single tool for almost everything. That's pretty neat!

## Key Differences Between TypeScript and Rust

|                    | TypeScript                             | Rust                                   |
| ------------------ | -------------------------------------- | -------------------------------------- |
| Stable Release     | 2014                                   | 2015                                   |
| Packages           | 3 million+ (npm)                       | 250,000+ (crates.io)                   |
| Type System        | Optional                               | Mandatory                              |
| Memory Management  | Garbage collected                      | Automatic with ownership and borrowing |
| Speed              | Moderate                               | Exceptional                            |
| Concurrency model  | Single-threaded event loop             | Multi-threaded with async support      |
| Error Handling     | Exceptions                             | Errors as values, no exceptions        |
| Learning Curve     | Moderate                               | Steep                                  |

## TypeScript as a Bridge to Rust

Your background with TypeScript's type system is a real advantage. You already think in terms of types, you've felt the pain of `any`, and you understand why explicit error handling matters. Rust takes these ideas further and makes them non-optional.

The main tradeoff you'll notice immediately is that Rust has stronger compile-time guarantees but [slower compile times](/blog/tips-for-faster-rust-compile-times/).
Most developers find this worthwhile because the borrow checker catches so many issues that would otherwise surface in production.

{% podcast_quote(player="s05e04-roc?t=45:10", attribution="Richard Feldman, Creator of Roc") %}
"I certainly think that the degree to which compile times bother you would depend, sort of obviously, on what you're used to and what you think of as sort of possible or normal. Like if I'm used to Elm and sub-second recompiles and stuff like that, then yeah, I mean, it's going to bother me when I'm waiting 10 seconds to be able to build my thing or to run my tests."
{% end %}

{% podcast_quote(player="s03e05-zoo?t=40:33", attribution="Jessie Frazelle, CEO of Zoo") %}
"Writing Rust is so much more natural to me that even TypeScript is hard for me to write. I\'m just looking for a match statement, or things where I want to abort a Promise. In Tokio you can abort an async operation; you can\'t do that in TypeScript. That drives me nuts."
{% end %}

## Syntax at a Glance

The best way to understand Rust from a TypeScript background is to see the patterns you already know, side by side.

### Error Handling: `try/catch` vs `Result<T, E>`

TypeScript uses exceptions for error handling:

```typescript
async function readConfig(path: string): Promise<Config> {
  try {
    const data = await fs.readFile(path, "utf8");
    return JSON.parse(data);
  } catch (err) {
    throw new Error(`Failed to read config: ${err}`);
  }
}
```

Rust makes errors part of the type signature. The `?` operator propagates errors automatically:

```rust
fn read_config(path: &str) -> Result<Config, Box<dyn Error>> {
    let data = fs::read_to_string(path)?;
    let config = serde_json::from_str(&data)?;
    Ok(config)
}
```

If a function can fail, its return type must reflect that.
You can't forget to handle exceptions (because there are none!).
Every error must be handled explicitly in Rust, which leads to more robust code.

### Null Safety: `undefined`/`null` vs `Option<T>`

TypeScript gives you `undefined` and `null`, and it's easy to forget to check:

```typescript
function getUser(id: string): User | undefined {
  return users.find((u) => u.id === id);
}

const user = getUser("123");
console.log(user.name); // Oof, runtime crash if user is undefined.
```

On the other side, Rust uses `Option<T>` and the compiler always **forces** you to handle the missing case:

```rust
fn get_user(id: &str) -> Option<User> {
    users.iter().find(|u| u.id == id).cloned()
}

let user = get_user("123");
// unwraps will panic if user is None.
// You can search for "unwrap" in your
// entire codebase to find all the places
// you need to handle!
println!("{}", user.unwrap().name);

// or, safely:
if let Some(user) = get_user("123") {
    println!("{}", user.name);
}
```

### Interfaces vs Traits

This is a very common pitfall for people coming from TypeScript (and other languages with interfaces).
Rust does not have interfaces, but it has something similar called traits.
Sometimes you will read that "traits are like interfaces," but I always found that comparison to be misleading.
It's better to think of them as a way to do composition in Rust.

My way of thinking about it is:

- Interfaces express a "is-a" relationship. A `Car` is a `Vehicle`.
- Traits express a "can-do" relationship. A `Car` can `Drive`.

Here's another example using geometrical shapes.
In TypeScript you'd define a `Drawable` interface and implement it for each shape: 

```typescript
interface Drawable {
  draw(): void;
  boundingBox(): { x: number; y: number; width: number; height: number };
  area(): number;
}

class Circle implements Drawable {
  constructor(private x: number, private y: number, private radius: number) {}

  draw() { console.log(`Drawing circle at (${this.x}, ${this.y})`); }
  boundingBox() {
    return { x: this.x - this.radius, y: this.y - this.radius,
             width: this.radius * 2, height: this.radius * 2 };
  }
  area() { return Math.PI * this.radius ** 2; }
}

// Rectangle implements Drawable similarly...

function renderIfVisible(shape: Drawable, viewport: { width: number; height: number }) {
  const bb = shape.boundingBox();
  if (bb.x < viewport.width && bb.y < viewport.height) {
    shape.draw();
  }
}
```

But note how we tangled up two separate concerns (drawing and area calculation) into one interface.

In Rust, it's often better to have small, focused traits.
`Draw` implies "something that can be rendered," while `area` and `bounding_box` imply "something that has a shape." 
So you could split this into multiple traits:

```rust
// Separate geometry from rendering
pub trait Shape {
    fn bounding_box(&self) -> (f64, f64, f64, f64); // (x, y, width, height)
    fn area(&self) -> f64;
}

// `Draw: Shape` means "anything that implements Draw must also implement Shape"
pub trait Draw: Shape {
    fn draw(&self);
}

pub struct Circle { pub x: f64, pub y: f64, pub radius: f64 }

impl Shape for Circle {
    fn bounding_box(&self) -> (f64, f64, f64, f64) {
        (self.x - self.radius, self.y - self.radius,
         self.radius * 2.0, self.radius * 2.0)
    }
    fn area(&self) -> f64 { std::f64::consts::PI * self.radius.powi(2) }
}

// Note: we can implement Draw separately from Shape.
// This lets us use Circle in a physics engine (which only needs Shape)
// without forcing it to know how to draw itself.
impl Draw for Circle {
    fn draw(&self) { println!("Drawing circle at ({}, {})", self.x, self.y); }
}

fn render_if_visible(shape: &impl Draw, viewport_limit: f64) {
    let (x, _, _, _) = shape.bounding_box();
    if x >= 0.0 && x <= viewport_limit { shape.draw(); }
}
```

This allows you to pass objects to a physics engine (which needs `Shape`) without requiring them to know how to draw themselves.
Rust's `&impl Draw` lets you accept any type that implements the trait without needing inheritance or wrapper types.

This is what is often referred to as "**composition over inheritance**," because you can compose behavior by implementing multiple traits on the same struct, rather than relying on a class hierarchy as you would with interfaces.

### Union Types vs Enums

TypeScript union types are a common way to express "one of these shapes":

```typescript
type Shape = { kind: "circle"; radius: number } | { kind: "rect"; width: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rect":
      return shape.width * shape.height;
  }
}
```

Note how in the above case, we could easily forget to handle a new shape type, and the compiler wouldn't tell us.
In Rust, you would use an enum, and the compiler forces you to handle every case, so you can never forget:

```rust
enum Shape {
    Circle { radius: f64 },
    Rect { width: f64, height: f64 },
}

fn area(shape: &Shape) -> f64 {
    match shape {
        Shape::Circle { radius } => std::f64::consts::PI * radius * radius,
        Shape::Rect { width, height } => width * height,
    }
}
```

If you add a new variant to the enum, the compiler will tell you every place that needs updating.
That's one example of why refactoring Rust code is amazing.

### Async: `Promise<T>` vs `async fn`

Concurrent programming is super central in TypeScript.
A lot of people want to know the equivalent in Rust very early in their learning journey.
That's fair, but just note that you can use Rust without async at all, and it's plenty fast out of the box.
And if you want to use multithreading, you can do that without async as well.
However, if you do a lot of web things, chances are one of your dependencies will require async, and then it's good to know your way around it.

So here's a quick comparison of how async works in both languages.

TypeScript async is built on the JavaScript event loop:

```typescript
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}
```

Node.js has one event loop (libuv, which is a wrapper around epoll/kqueue/IOCP) and Promises are built into the language. You rarely think about the runtime.
In TypeScript, async is invisible infrastructure, which is quite handy.

Here is the equivalent in Rust:

```rust
async fn fetch_user(id: &str) -> Result<User, reqwest::Error> {
    let user = reqwest::get(format!("/api/users/{}", id))
        .await?
        .json::<User>()
        .await?;
    Ok(user)
}
```

Rust async is different in one important way: **there is no built-in runtime**.
Sure, Rust's standard library includes the `async`/`.await` syntax, but executing futures requires that you bring your own async runtime in the form of a library. 

The most widely used runtime is [Tokio](https://tokio.rs), which is very mature:

```rust
#[tokio::main]
async fn main() {
    let result = fetch_user("123").await;
}
```

The `#[tokio::main]` attribute sets up the Tokio runtime for you, so in practice it doesn't add much boilerplate.

{% info(title="Async TypeScript and Rust: a quick summary" ) %}

**What's the same:**

- `async`/`await` works in both languages.
- You can run tasks concurrently with `tokio::join!` (similar to `Promise.all`).
- Error propagation with `?` works inside async functions. You can use the same error handling patterns as in synchronous code.

**What's different:**

- Rust has no built-in runtime; you bring your own (Tokio is the standard choice for web services)
- In Rust, `.await` goes *after* the expression, not before it
- Futures in Rust are lazy: they don't start until you `.await` them or spawn them. In TypeScript, Promises start executing immediately when created.
- Background tasks require `tokio::spawn` rather than a fire-and-forget async call
- You'll occasionally see `Send + Sync` bounds on async code, related to Rust's thread safety guarantees

**Why does Rust require an explicit runtime?**

By leaving the runtime as a library choice, you only pay for what you use.
Rust targets embedded systems and environments where a large built-in runtime would be unacceptable.
Different applications also have different concurrency needs: single-threaded, multi-threaded, work-stealing schedulers, and so on.

{% end %}

As mentioned, for backend web services, Tokio is the standard choice. It's multi-threaded, battle-tested, and what frameworks like [axum](https://github.com/tokio-rs/axum) have first-class support for it.

## Rust's Infamous Learning Curve

Rust enforces stronger guarantees than TypeScript through its ownership system and borrow checker. Most developers need a few months to get comfortable with the ownership model and will go through a phase of ["fighting the borrow checker"](https://www.youtube.com/watch?v=ZNFdkTIzdXM). This is normal and temporary. Once it clicks, it becomes one of the things you'll miss most when you go back to other languages. (This and the amazing compiler error messages.) There are ways to [flatten Rust's learning curve](/blog/flattening-rusts-learning-curve/) that can help you get there faster.

{% podcast_quote(player="s04e06-1password?t=53:08", attribution="Andrew Burkhart, Senior Rust Engineer at 1Password") %}
"I had never touched memory coming from TypeScript. I could not get through the Rust code at first, but luckily they hired me anyway. Everything I know about Rust I\'ve learned in the last three years. It\'s definitely something you can pick up. The hardest thing to get from zero to productive isn\'t the syntax: good Rust requires a bit of engineering knowledge the book doesn\'t always cover."
{% end %}

## Rust Has Its Roots In Systems Programming

Rust requires you to understand [systems concepts](/blog/foundational-software/) that TypeScript never surfaced.
You need to know the difference between stack and heap allocation.
You'll work with different string types like `String` and `&str`.
And you'll need a working understanding of what a pointer or a mutex is.

These concepts might seem intimidating at first, but they're what makes Rust efficient.
Rust won't hide any details from you; its philosophy is: "explicit is better than implicit."

You don't need to be a systems programmer to use Rust, but you will need to learn these concepts
to become proficient in it. The compiler will guide you through most of it.

## String Types: `String` vs `&str`

This will trip you up. In TypeScript, strings are... just strings? In Rust, there are many string types and you need to understand when to use each.

**`String`** is a heap-allocated, owned string. You can modify it and it owns its memory:

```rust
let mut greeting = String::from("Hello");
greeting.push_str(", world!"); // can modify
```

**`&str`** is a string *slice*, a reference to string data that lives somewhere else (a `String`, a string literal, etc.). It's immutable and "borrowed":

```rust
let greeting: &str = "Hello, world!"; // string literals are &str
```

The practical rules:

- Use `&str` for function parameters when you just need to read a string
- Use `String` when you need to own, build, or return a string
- String literals in your code are `&str` by default

```rust
// Prefer &str for function parameters
// Works with both String and &str
fn greet(name: &str) {
    println!("Hello, {}!", name);
}

let owned = String::from("Alice");
greet(&owned);   // works – &String coerces to &str
greet("Bob");    // works – string literals are &str
```

You'll see `&str` in most function signatures and `String` in structs and return types. The compiler will tell you when you've got it wrong, and the fix is usually straightforward once you understand the distinction.

## Safety and Reliability

The strict Rust compiler is your strongest ally.
You can refactor without fear because the compiler has your back.

It sounds like a cliché, but to truly understand what I mean by that, you have to experience it for yourself.
You won't deal with `null` or `undefined` errors, but you will end up modeling a lot of your code with strong types and use `Option<T>` and `Result<T, E>` a lot to handle cases that would be runtime errors in TypeScript.
[Aim for immutability](/blog/immutability/) wherever you can: it makes Rust code easier to reason about and plays well with the borrow checker.

## Ecosystem Maturity

NPM gives you more packages, but Rust's ecosystem is of excellent quality and growing rapidly.

{% podcast_quote(player="s05e08-radar?t=08:55", attribution="Jeff Kao, Staff Engineer at Radar") %}
"Rust really feels modern. There\'s a rich cargo crate ecosystem, a formatter, flame graphs, and the paradigms are very functional, but you\'re not forced to use them. Having a rich data structure ecosystem in the standard library, being able to process vectors with all the functions that many developers are used to these days, really felt refreshing. Especially for a team with largely a background in TypeScript."
{% end %}

> In September 2022 over 2.1 million packages were reported being listed in the npm registry, making it the biggest single language code repository on Earth -- Source: [Nodejs.org](https://nodejs.org/en/learn/getting-started/an-introduction-to-the-npm-package-manager)

A small portion of these packages provide type definitions (i.e. TypeScript support).
Many packages are outdated or are no longer actively maintained.
According to [SC Media](https://www.scworld.com/news/npm-registry-users-download-2-1b-deprecated-packages-weekly-researchers-say), "NPM registry users download 2.1B deprecated packages weekly".

Compare that to Rust's crate ecosystem.
At the time of writing, it lists over 250k crates. That is a fraction of NPM's packages.
Crates also can't be easily removed from the registry:

> Take care when publishing a crate, because a publish is permanent. The version can never be overwritten, and the code cannot be deleted. There is no limit to the number of versions which can be published, however.

That's a feature, not a bug.
It means that your build pipelines won't break due to a missing dependency.
You can [yank](https://doc.rust-lang.org/cargo/reference/publishing.html#cargo-yank) a version to indicate that it's no longer supported, but the code remains available for those who depend on it.

Libraries maintain strong backward compatibility.
Breaking changes are rare.
Rust itself releases new [editions](https://doc.rust-lang.org/edition-guide/editions/) every three years with opt-in changes.

The quality difference becomes especially noticeable in larger applications.
While the Rust ecosystem may be smaller, the crates are typically more reliable and provide better documentation compared to the TypeScript ecosystem.
When you build a large application, that higher quality standard makes a significant difference.

Many Rust crates stay in 0.x versions longer than you might expect.
Don't let this worry you: Rust's type system ensures robust functionality even before reaching 1.0.
The ecosystem grows fast, and the existing libraries work reliably.
For specific use cases, writing your own library is common and well-supported.

## Popular Packages And Their Rust Counterparts

One of the first questions TypeScript developers ask: "What do I use instead of X?"

Here's a practical mapping of common npm packages to their Rust crate equivalents:


| npm package            | Rust crate(s)                   | Notes                                                   |
| ---------------------- | ------------------------------- | ------------------------------------------------------- |
| `zod`                  | `serde` + `validator`           | `serde` handles serialization; add validators for rules |
| `axios` / `fetch`      | `reqwest`                       | Async HTTP client, supports JSON natively               |
| `express` / `fastify`  | `axum` / `actix-web`            | `axum` is the most actively developed                   |
| `winston` / `pino`     | `tracing`                       | Structured, async-aware logging                         |
| `dotenv`               | `dotenvy`                       | Drop-in equivalent                                      |
| `jest`                 | built-in `#[test]`              | Testing is built into the language and `cargo`          |
| `date-fns` / `luxon`   | `chrono` / `time`               | Date and time handling                                  |
| `uuid`                 | `uuid`                          | Same name, same purpose                                 |
| `lodash`               | built-in iterators              | Rust's iterator API covers most of lodash               |

**A key difference:** You won't find a Rust equivalent for every small utility package.
Where npm culture encourages installing tiny single-function packages, Rust culture favors using the standard library or writing the utility yourself. The standard library's [iterator](/blog/iterators/), collections, and string APIs are rich enough that you rarely need external packages for basic operations.

## Rust vs TypeScript For Backend Services

TypeScript is a great language for backend services.
A lot of companies use it successfully.
There are many frameworks to choose from, like Express, NestJS, or Fastify.
These frameworks are mature and well-documented.

By comparison, Rust's backend ecosystem is smaller.
You have Axum, Actix, and Rocket, among others.
These frameworks are fast and reliable, but they don't provide a "batteries-included" experience like Express.

That said, Rust's ecosystem is growing fast and most companies find the available libraries sufficient.
I personally recommend [axum](https://github.com/tokio-rs/axum) as it has the largest momentum and is backed by the Tokio team.

Deployment is straightforward.
You can build your Rust service into a single binary and deploy it to a container or as a bare-metal binary. 
Rust binaries are small and have no runtime dependencies.
This makes deployment easy and reliable.

## Rust is Really Fast!

You might have guessed that, but even then, teams are often shocked by *how* fast Rust really is. 
You can expect **an order of magnitude better CPU and memory usage if you're coming from JS/TS**.
That is consistently what we see in production when we migrate services from TypeScript to Rust.
The effects of that are very real: reduced cloud costs, less hardware, and faster response times.

Most importantly, **your runtime behavior becomes predictable**.
Production incidents decrease.
Your operations team will thank you for the reduced overhead.

## Planning Your Migration

Before you start, write down what you're trying to solve:

- What problems do you face today?
- [Why will Rust solve these problems?](/blog/why-rust/)
- Could you fix them in TypeScript instead?

This clarity matters when things get hard. Start with something real but low-risk such as a CLI tool, a background worker, a performance-critical library. Avoid big-bang rewrites. Incremental migrations give you feedback loops and let you build confidence before betting the whole system on Rust. Think about [long-term Rust project maintenance](/blog/long-term-rust-maintenance/) from the start, not as an afterthought. There's also a checklist for [making your first real-world Rust project a success](/blog/successful-rust-business-adoption-checklist/) that's worth going through before you commit.

## Integration Strategies

You have two main ways to integrate Rust with TypeScript.

### WebAssembly

WebAssembly is the smoothest migration path for TypeScript teams that want to keep their frontend in TypeScript while moving performance-critical code to Rust. You keep your existing TS codebase and call Rust functions from it.

The core toolchain:

- **[wasm-bindgen](https://github.com/wasm-bindgen/wasm-bindgen)** – Generates the JavaScript/TypeScript bindings for your Rust code automatically
- **[wasm-pack](https://github.com/wasm-bindgen/wasm-pack)** – Builds and packages your Rust code as an npm-compatible WASM module

A typical setup looks like this:

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn process_data(input: &str) -> String {
    // your high-performance Rust logic here
    format!("processed: {}", input)
}
```

After `wasm-pack build`, you get an npm package you can import directly:

```typescript
import { process_data } from "./pkg";

const result = process_data("hello");
```

**When to use WASM:**

- CPU-intensive operations (parsing, encoding, compression, crypto)
- Reusing Rust logic on both the frontend and a Rust backend
- Gradually migrating hot paths without a full rewrite

**When to use a separate service instead:**

- When you need access to the filesystem, network, or system resources
- For long-running background work
- When latency of the WASM call boundary matters less than operational simplicity

### Standalone Web Service

Alternatively, you can deploy Rust as separate services.
This fits well with microservice architectures.
Your TypeScript and Rust components communicate over the network.
This gives you a clean separation and lets you migrate gradually.

A common pattern is a Rust backend with a TypeScript frontend connected through a typed API layer. The [`ts-rs`](https://github.com/Aleph-Alpha/ts-rs) crate can automatically generate TypeScript types from your Rust types, giving you closed-loop type safety across both sides with almost no extra work:

{% podcast_quote(player="s02e02-amp?t=48:58", attribution="Carter Schultz, Robotics Architect at AMP") %}
"We have a Rust backend and TypeScript frontend. There\'s an amazing crate, `ts-rs`, that for any Rust types you define will generate TypeScript types for them, so you have closed-loop type safety between them. We end up using `serde_json` to serialize a Rust type, send it to the frontend, and the frontend uses `ts-rs` to get TypeScript types for it. We have closed-loop type safety across both applications for practically free. It was so easy to set up."
{% end %}

Oxide Computer takes this further with a fully generated API layer: their server framework [Dropshot](https://github.com/oxidecomputer/dropshot) generates an OpenAPI spec directly from Rust endpoint definitions, which then drives a TypeScript client generator. No need to write or maintain API definitions by hand:

{% podcast_quote(player="s03e03-oxide?t=1:23:42", attribution="Steve Klabnik, Author and Software Engineer at Oxide Computer") %}
"I write my server-side definition, say \'please generate stuff and regenerate the client in TypeScript,\' and when I switch back to my TypeScript file it gives me a type error if I\'m not passing something correctly. I get full type safety the whole way up through the stack. We\'ve been very happy with TypeScript. It\'s a pragmatic decision to engage with that ecosystem deeply, and it\'s been very, very nice."
{% end %}

## What About Deno and Bun?

If you're evaluating alternatives to Node.js + TypeScript, you'll likely come across Deno and Bun. Both are worth understanding:

**Deno** is a Node.js alternative by Ryan Dahl (Node's original creator). It has first-class TypeScript support, a built-in standard library, and better security defaults. It solves several npm/Node.js pain points but remains in the JavaScript/TypeScript ecosystem with the same fundamental tradeoffs: garbage collection, a single-threaded event loop, and similar performance ceiling. (Deno itself is written in Rust, by the way.)

**Bun** is a fast JavaScript runtime and toolkit that dramatically improves startup time and throughput compared to Node.js. For many workloads it's an easy drop-in replacement and genuinely fast. (Bun is written in Zig.)

**The honest answer:** If your goal is to fix tooling friction or [slow CI pipelines](/blog/tips-for-faster-ci-builds/), Deno or Bun might be all you need. They're lower-risk changes.

If your goal is to do a rewrite or a port of a larger portion of your codebase, Rust could be a [solid long-term investment](/blog/rust-in-ten-years/).
It offers predictable memory usage, maximum throughput, fearless concurrency, and eliminating many runtime errors at the compiler level.
Those are Rust's strengths, and no JavaScript runtime will close that gap.

Most teams that choose Rust do so not because Node.js alternatives don't exist, but because they've hit limits that moving to a different JS runtime won't solve
or they learn that their problems are fundamentally about the language and ecosystem, not the runtime.

## Starting Your Journey

Don't rewrite everything at once!
Start small.
Maybe pick a monitoring service or CLI tool – something important but not critical.
Perhaps you'll give it a shot during a hackathon or a sprint.
Build confidence through early wins.

{% info(title="Need Help With Your TypeScript to Rust Migration?", icon="crab") %}

Migrating a production codebase is a big step, and the learning curve is real.
I help engineering teams make successful transitions to Rust, from training and architecture reviews to hands-on migration planning.
If you want to move faster and avoid the common pitfalls, [let's talk about your project](/services).

{% end %}
