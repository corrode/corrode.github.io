+++
title = "Migrating from TypeScript to Rust"
date = 2024-12-13
updated = 2025-02-06
template = "article.html"
draft = false
[extra]
series = "Migration Guides"
icon = "typescript.svg"
resources = [
    "[Syntax comparison between TypeScript to Rust - Robbie Cook](https://blog.robbie.digital/posts/typescript-to-rust)",
    "[My experience migrating TypeScript libraries to Rust - Patrick Desjardins](https://patrickdesjardins.com/blog/migrating-typescript-library-to-rust)",
    "[Node.js to Rust in 2024 - Pascal Poredda](https://pascal-poredda.de/blog/migrating-from-node-to-rust)"
]
+++

{% info(title="A Practical Guide for Decision Makers" ) %}
I wrote this guide for technical leaders and developers considering a move from TypeScript to Rust.
After years of helping teams make this transition, I'll share what works, what doesn't, and how to make your migration successful.
{% end %}

TypeScript excels at making JavaScript more maintainable, but teams often hit scaling challenges as their codebases grow.
You might be facing performance bottlenecks, reliability issues, or maintenance overhead.
Rust offers compelling solutions to these problems, but migration needs careful planning and execution.
Let me show you how to evaluate if Rust is right for your team, plan a successful migration, and keep your team productive during the transition.

In this article, you'll learn:

- How to evaluate if Rust is right for your team
- Practical strategies for TypeScript-to-Rust migration
- Common pitfalls and how to avoid them
- Ways to maintain productivity during transition

## Your Toolchain, Translated

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

## Why Teams Consider Rust

TypeScript is a great language, but many teams hit a wall around the 10k to 100k lines of code mark.
At this scale, the codebase becomes hard to maintain and teams start to feel the pain.
The honeymoon phase with TypeScript codebases is surprisingly short - when working with larger applications, adding functionality or performing large-scale refactoring becomes increasingly challenging.

The problems are clear and specific.
While TypeScript has a type system, it remains a dynamically typed language built on JavaScript.
Types are optional and can be [bypassed using `any` or `unknown`](https://dev.to/martinpersson/a-guide-to-using-the-option-type-in-typescript-ki2) or by freely [casting](https://medium.com/livefront/to-cast-or-not-to-cast-a-typescript-dilemma-c0c20c53c6d9) between types.
Without enough discipline, this leads to runtime errors and bugs.

Memory leaks and security vulnerabilities become more common, especially in large, long-running backend services.
Some companies I've worked with needed regular service restarts to manage memory leaks.

External packages often have security vulnerabilities and need regular updates.
Breaking changes are common, and packages frequently become [unmaintained](https://www.aquasec.com/blog/deceptive-deprecation-the-truth-about-npm-deprecated-packages/).
[Frameworks like Next.js introduce frequent breaking changes](https://www.propelauth.com/post/nextjs-challenges), forcing teams to spend time on updates instead of business logic.

Performance isn't guaranteed.
TypeScript is fast enough for most cases, but performance-critical applications will hit limitations.
[Error handling through exceptions and promises can be hard to reason about.](https://dev.to/mpiorowski/typescript-with-gorust-errors-no-trycatch-heresy-49mf)
Large TypeScript codebases become difficult to refactor and maintain, even with type safety.

## TypeScript as a Bridge to Rust

TypeScript's type system creates an excellent foundation for Rust adoption.
Your team already understands static typing and values its benefits.
This gives you a head start with Rust, which takes these concepts further and adds more powerful guarantees.

The developer experience differs in two key ways: Rust has stronger type guarantees but slower compile times compared to TypeScript.
Many developers find this tradeoff worthwhile, especially because you can write high-level Rust code without dropping into systems-level programming.
Rust's powerful abstractions like the trait system and generics allow you to model behavior in just the right way.

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
You can't forget to handle exceptions (because there are none).
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

On the other side, Rust uses `Option<T>` and the compiler forces you to handle the missing case:

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

TypeScript interfaces define the "shape" of an object:

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

In Rust, it's often better to have small, focused traits.
`Draw` implies "something that can be rendered," while `area` and `bounding_box` are geometric properties.
So you would split this into multiple traits:

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

### Union Types vs Enums

TypeScript union types:

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

Note how in the above case, we could easily forget to handle a new shape type, and the compiler wouldn't warn us.
In Rust, you would use an enum, and the compiler forces you to handle every case:

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

If you add a new variant to the enum, the compiler will tell you every match that needs updating.

### Async: `Promise<T>` vs `async fn`

Concurrent programming is super central to TypeScript.
A lot of people want to know the equivalent in Rust very early in their learning journey.
Here's a quick comparison of how async works in both languages.

TypeScript async is built on the JavaScript event loop:

```typescript
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}
```

Node.js has one event loop and Promises are built into the language. You rarely think about the runtime.
In TypeScript, async is invisible infrastructure.

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
Rust's standard library includes the `async`/`.await` syntax, but executing futures requires a runtime you choose and include as a dependency.

The most widely used runtime is [Tokio](https://tokio.rs):

```rust
#[tokio::main]
async fn main() {
    let result = fetch_user("123").await;
}
```

The `#[tokio::main]` attribute sets up the Tokio runtime for you, so in practice it doesn't add much boilerplate.

{% info(title="TypeScript vs Rust: async at a glance" ) %}

**What's the same:**

- `async`/`await` works in both languages
- You can run tasks concurrently with `tokio::join!` (similar to `Promise.all`)
- Error propagation with `?` works inside async functions

**What's different:**

- Rust has no built-in runtime; you bring your own (Tokio is the standard choice for web services)
- In Rust, `.await` goes *after* the expression, not before it
- Futures in Rust are lazy: they don't start until you `.await` them or spawn them
- Background tasks require `tokio::spawn` rather than a fire-and-forget async call
- You'll occasionally see `Send + Sync` bounds on async code, related to Rust's thread safety guarantees

{% end %}

{% info(title="Why does Rust require an explicit runtime?" ) %}

Rust targets embedded systems and environments where a large built-in runtime would be unacceptable.
Different applications also have different concurrency needs: single-threaded, multi-threaded, work-stealing schedulers, and so on.
By leaving the runtime as a library choice, you only pay for what you use.

{% end %}

For backend web services, Tokio is the standard choice. It's multi-threaded, battle-tested, and what frameworks like [axum](https://github.com/tokio-rs/axum) have first-class support for it.

## Understanding Rust's Learning Curve

Rust enforces stronger guarantees than TypeScript through its ownership system and borrow checker.
You'll need to plan for an adjustment period.
Most developers need 2-4 months to become comfortable with Rust's ownership model.
They'll go through a phase of ["fighting the borrow checker"](https://www.youtube.com/watch?v=ZNFdkTIzdXM) – this is normal and temporary.
Your job is to keep the team motivated during this learning curve.
I've seen time and again that developers who push through this phase become the strongest Rust advocates.
These developers then become valuable mentors for their teammates.

## Rust Has Its Roots In Systems Programming

Rust pushes your team to understand systems concepts better than TypeScript ever required.
You need to know the difference between stack and heap allocation.
You'll work with different string types like `String` and `&str`.
And you should be willing to learn what a pointer or a mutex is.

These concepts might seem intimidating at first, but they make Rust fast.
Rust won't hide these details from you.
The idea is that explicit is better than implicit.

Your team will write more efficient code because Rust makes these low-level details explicit and manageable.

You don't need to be a systems programmer to use Rust and yet, you will need to learn these concepts
to become proficient in Rust.

## String Types: `String` vs `&str`

This will trip you up. In TypeScript, strings are... just strings. In Rust, there are many string types and you need to understand when to use each.

**`String`** is a heap-allocated, owned string. You can modify it and it owns its memory:

```rust
let mut greeting = String::from("Hello");
greeting.push_str(", world!"); // can modify
```

**`&str`** is a string *slice* – a reference to string data that lives somewhere else (a `String`, a string literal, etc.). It's immutable and borrowed:

```rust
let greeting: &str = "Hello, world!"; // string literals are &str
```

The practical rules:

- Use `&str` for function parameters when you just need to read a string
- Use `String` when you need to own, build, or return a string
- String literals in your code are `&str` by default

```rust
// Prefer &str for function parameters – works with both String and &str
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
You can refactor without fear because the compiler catches mistakes early and consistently.
You won't deal with `null` or `undefined` errors, but you will end up modeling a lot of your code with strong types and use `Option<T>` and `Result<T, E>` a lot to handle cases that would be runtime errors in TypeScript.

## Ecosystem Maturity

NPM gives you more packages, but Rust's ecosystem is of excellent quality and growing rapidly.

> In September 2022 over 2.1 million packages were reported being listed in the npm registry, making it the biggest single language code repository on Earth -- Source: [Nodejs.org](https://nodejs.org/en/learn/getting-started/an-introduction-to-the-npm-package-manager)

A small portion of these packages provide type definitions (i.e. TypeScript support).
Many packages are outdated or are actively maintained.
According to [SC Media](https://www.scworld.com/news/npm-registry-users-download-2-1b-deprecated-packages-weekly-researchers-say), "NPM registry users download 2.1B deprecated packages weekly".

Compare that to Rust's crate ecosystem.
At the time of writing, it lists over 250k crates, but that is a fraction of NPM's packages.
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
Don't let this worry you – Rust's type system ensures robust functionality even before reaching 1.0.
The ecosystem grows fast, and the existing libraries work reliably.
For specific use cases, writing your own library is common and well-supported.

## From npm to Cargo: Common Package Equivalents

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
Where npm culture encourages installing tiny single-function packages, Rust culture favors using the standard library or writing the utility yourself. The standard library's iterator, collections, and string APIs are rich enough that you rarely need external packages for basic operations.

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
You can build your Rust service into a single binary and deploy it to a container or a server.
Rust binaries are small and have no runtime dependencies.
This makes deployment easy and reliable.

## Rust is Really Fast

Teams are often shocked that Rust is so fast.
They go in expecting Rust to be fast, but the reality still surprises them.
You can expect an order of magnitude better CPU and memory usage if you're coming from JS/TS.
The effects of that are very real: reduced cloud costs, less hardware, and faster response times.

Most importantly, **your runtime behavior becomes predictable**.
Production incidents decrease.
Your operations team will thank you for the reduced overhead.

## Planning Your Migration

Write down why you want to migrate before you start:

- What problems do you face today?
- Why will Rust solve these problems?
- Could you fix them in TypeScript instead?

This clarity helps when things get tough.

I know this evaluation isn't easy.
We often struggle to see our codebase's problems clearly.
Politics and inertia hold us back.
Sometimes you need an outside perspective.
I can help you evaluate your situation objectively and create a solid migration plan.
This might sound expensive, but think about your team's salaries and the cost of making the wrong decision.
Good consulting pays for itself quickly. [Reach out for a free consultation](/services).

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

## What About Deno and Bun?

If you're evaluating alternatives to Node.js + TypeScript, you'll likely come across Deno and Bun. Both are worth understanding:

**Deno** is a Node.js alternative by Ryan Dahl (Node's original creator). It has first-class TypeScript support, a built-in standard library, and better security defaults. It solves several npm/Node.js pain points but remains in the JavaScript/TypeScript ecosystem with the same fundamental tradeoffs: garbage collection, a single-threaded event loop, and similar performance ceiling. (Deno itself is written in Rust, by the way.)

**Bun** is a fast JavaScript runtime and toolkit that dramatically improves startup time and throughput compared to Node.js. For many workloads it's an easy drop-in replacement and genuinely fast. (Bun is written in Zig.)

**The honest answer:** If your goal is to fix tooling friction or slow CI pipelines, Deno or Bun might be all you need. They're lower-risk changes.

If your goal is to do a rewrite or a port of a larger portion of your codebase, Rust could be a solid long-term investment.
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

{% info(title="Ready to make the switch to Rust?", icon="crab") %}
I help teams make successful transitions from TypeScript to Rust.
Whether you need training, architecture guidance, or migration planning, [let's talk about your needs](/services).
{% end %}
