+++
title = "Migrating from Python to Rust"
date = 2024-12-13
updated = 2026-04-14
template = "article.html"
draft = false
[extra]
series = "Migration Guides"
icon = "python.svg"
resources = [
  "[Rewrite everything in Rust? What we learned from introducing Rust in Strawberry-GraphQL - Erik Wrede](https://www.youtube.com/watch?v=fpxHT1Uvv2w) - A thoughtful talk on a practical migration from Python to Rust",
]
+++


Python is an incredibly versatile language that powers everything from web applications to data science pipelines.
Before Rust, my main language was Python, and I loved it for its elegance and conciseness.
However, eventually I hit its limits, particularly around performance, type safety, and robustness.
I was reaching for more.

While Rust isn't a direct replacement for Python, it has some answers to its challenges and that's what made it attractive to me in the first place.
That's why I wrote this guide to help more Python developers understand the tradeoffs and benefits of Rust, and to perhaps make the transition themselves.
I am obviously a little biased but my heart beats for both languages, so I will try to be as fair and objective as I can.

## Is Rust the right choice for you?

Ultimately, that's a question for you to answer, but at least I can give you as much guidance as possible to set you up for success.

In this article, you'll learn: 

- How to evaluate whether Rust is the right choice for your Python codebase
- How a Python-to-Rust migration looks in practice
- Common pitfalls and how to avoid them
- Ways to maintain productivity while switching the stack 
- How to retain Python's strengths while adopting Rust 

## A First Look At The Most Important Commands

Python developers are used to assembling a toolchain from multiple tools. 
It has gotten a lot better with [`uv`](/podcast/s04e03-astral/) lately, but many real-world codebases still use a plethora of different tools for dependency management, testing, formatting, and so on.

Here's how Rust maps to your daily workflow:

| Python tool | Rust equivalent | Notes |
| --- | --- | --- |
| `requirements.txt` / `pyproject.toml` | `Cargo.toml` | Project config and dependency manifest |
| `pip` / `poetry` / `uv` | `cargo` | Package manager, build tool, and task runner |
| `python main.py` | `cargo run` | Run your project |
| `pytest` / `unittest` | `cargo test` | Testing built into the toolchain |
| `flake8` / `ruff` / `pylint` | `cargo clippy` | Linter with actionable suggestions |
| `black` / `ruff format` | `cargo fmt` | Auto-formatter, zero config |
| `mypy` / `pyright` | `cargo check` | Fast type-check without a full build |

or, if you made the switch to uv (which is written in Rust, by the way):

| Python tool | Rust equivalent | Notes |
| --- | --- | --- |
| `pyproject.toml` / `uv.lock` | `Cargo.toml` / `Cargo.lock` | Project config and dependency manifest |
| `uv` | `cargo` | Package manager, build tool, and task runner |
| `uv run main.py` | `cargo run` | Run your project |
| `uv run pytest` | `cargo test` | Testing built into the toolchain |
| `ruff check` | `cargo clippy` | Linter with actionable suggestions |
| `ruff format` | `cargo fmt` | Auto-formatter, zero config |
| `uv run mypy` / `uv run pyright` | `cargo check` | Fast type-check without a full build |

As you can see, **everything comes with Rust**. There's no decision fatigue around which test framework, formatter, or linter to use. The ecosystem has converged on `cargo` as the single tool for almost everything.

## Key Differences Between Python and Rust

| Aspect            | Python 🐍                    | Rust 🦀                             |
| ----------------- | ---------------------------- | ----------------------------------- |
| Type System       | Dynamic, optional type hints | Static, strong type system          |
| Memory Management | Garbage collected            | No GC, ownership and borrowing      |
| Performance       | Moderate                     | High performance, low-level control |
| Deployment        | Runtime required             | Single binary, minimal runtime      |
| Package Manager   | Multiple (pip, conda, uv)    | cargo (built-in)                    |
| Error Handling    | Exceptions                   | Results                             |
| Concurrency       | Limited by GIL               | Zero-cost abstractions, no GIL      |
| Learning Curve    | Gentle                       | Steep                               |
| Ecosystem Size    | Large (800,000+ packages)    | Medium (250,000+ crates)            |

## Why Python Developers Consider Rust

{% podcast_quote(player="s06e01-cloudsmith?t=05:42", attribution="Cian Butler, Staff Software Engineer at Cloudsmith") %}
"I know that we wouldn't have scaled as fast as we did without Django and Python because we wouldn't be able to roll features out as quickly as we did. ... [But] what made it really good for scaling on day one has kind of like caught up and made it really difficult to understand and handle now."
{% end %}

Many Python developers don't have a *single* reason to migrate to Rust; it's rather a combination of factors:

1. Developers interested in Rust are likely willing to understand systems programming concepts.
   They outgrew Python's limitations and are looking for more control over performance and memory management.

2. Python developers often long for stronger type guarantees.
   They appreciate Rust's static type system and the "reliability" that comes with it. 

3. Developers with a Python background often work on data processing or web applications.
   These are areas where Rust's performance benefits shine, especially at scale. 

While Python is very readable and great for prototyping, you often hit scaling challenges as your applications grow...

### Performance Bottlenecks

Python's Global Interpreter Lock (GIL) limits true parallelism.
Past a certain point, this makes it challenging to fully utilize multi-core systems.
There is a version of Python without the GIL, but it [doesn't solve the performance issues yet](https://news.ycombinator.com/item?id=41677131). 

If your workloads are I/O bound, [asyncio](https://docs.python.org/3/library/asyncio.html) is great and can get you very far.
In this case, you might not need to switch for performance reasons alone. 

However, if your workload is CPU-intensive that's a different story.
That's where teams often have to resort to complex workarounds involving multiple sub-processes or fall back to C extensions, which are a security risk and hard to maintain on multiple platforms (except if you use containers).
I've hit that glass ceiling many times in Python, and it has never been fun. 
Typically, you run into bottlenecks at the exact worst possible time: when your application is under heavy load and in production.
Those are the days you wish for more headroom, but you spend your time firefighting and monkey-patching your architecture to squeeze out every last bit of performance. 

### Type Safety Concerns

{% podcast_quote(player="s04e02-svix?t=14:54", attribution="Tom Hacohen, Founder of Svix") %}
"...we were doing what we could to make sure that Python has a very rich type system. So I think we were already doing a fairly good job in terms of catching a lot of issues... But the problem with Python is that all the hacks that I mentioned were not real, right? It's not really a type. It's an annotation that we added. So we still had issues where we got the annotation wrong."
{% end %}

Despite Python's type hints, runtime type errors still occur.
Types are optional in Python. 
It's all too easy to say: "I'll add those type hints later" and then never get around to it.
Or you add the famous `Any` type or a `# type: ignore` comment just to make the type checker stop complaining.
I don't blame you.

As developers it requires discipline to add and maintain type hints consistently, which can be challenging in large codebases.
And even if you do, your colleagues might not, which can lead to discussions about typesafety and code quality that can be frustrating and unproductive.
Furthermore, adoption is inconsistent across the Python ecosystem (I'm looking at you, third-party libraries).
As a consequence, large Python applications can become difficult to maintain and refactor confidently.

From my experience, there is a breaking point around the 10-100k lines of code mark where the lack of type safety becomes a significant liability.[^1]

[^1]: See discussions on large-scale Python applications on [Reddit](https://www.reddit.com/r/Python/comments/a7zrjn/why_do_people_say_that_python_is_not_good_for/) and [HN](https://news.ycombinator.com/item?id=25073308).

Overall, we see more and more Python code that's written with type-safety in mind, but it's a slow and tedious battle, that consumes a lot of time and energy.
In Rust, types are front and center, and the compiler enforces them. You simply can't forget to handle any edge cases.
Initially, that is super annoying, but the payoff when you're knee-deep in a large refactor is priceless.
I have done many large refactors in both languages, and I will take the Rust developer experience any day of the week.

### Deployment Complexity

Python applications require managing runtime environments, dependencies, and potential version conflicts. 
A lot of the issues can be mitigated with containerization.
However, bundling Python applications for deployment is never fun, especially when targeting platforms with different architectures.
The dynamic nature of the language, paired with C extensions means that you will spend a lot of time testing and debugging release builds on different platforms.

A lot of the issues only surface once you execute the application and trigger a specific code path, which can be a nightmare to debug.
In Rust, most of the time you can just `cargo build --release` and ship the resulting binary.
Rust binaries are self-contained, statically linked binaries, which can be copied to any target system and just run forever.
It's pretty much night and day compared to Python, and it's a huge relief for the ops team.

### Resource Usage

Python has a relatively manageable memory profile, but it can be inefficient for certain workloads.
For example, Python's memory overhead can be significant for large-scale data processing or long-running services.
If you ever had to deserialize a bunch of large JSON objects in Python, you know how memory usage can balloon out of control.
Fortunately, CPU-bound tasks can often get offloaded to C extensions, which are fast and memory efficient,
but they come with their own set of challenges, adding complexity and FFI overhead.
People are shocked when they migrate to Rust and their memory chart shows a flat line around the 30% mark of whatever Python was using before.
I've seen people double-check that the monitoring is working because it looked too good to be true. 

### In Summary

None of the above problems are dealbreakers for Python and you can get a lot of mileage out it, but when you hit problem after problem, you start looking for alternatives. 
A lot of Rust developers started out as Python developers, and I think you can now see why.
Rust just resolves some of the most common pain points of Python at the cost of a steeper learning curve and a smaller ecosystem.
If that tradeoff is worth it for you is something only you can decide.

## Comparing Both Languages Side by Side 

The best way to understand Rust is to map its features to concepts you already know. 

### Error Handling: `try/except` vs `Result<T, E>`

Python uses exceptions for error handling:

```python
import json

def read_config(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as err:
        raise RuntimeError(f"Failed to read config: {err}")
```

Rust makes errors part of the type signature. The `?` operator propagates errors automatically:

```rust
use std::fs;
use std::error::Error;

fn read_config(path: &str) -> Result<Config, Box<dyn Error>> {
    let data = fs::read_to_string(path)?;
    let config = serde_json::from_str(&data)?;
    Ok(config)
}
```

If a function can fail, its return type must reflect that. You can't forget to handle exceptions (because there are none!). Every error must be handled explicitly in Rust, which leads to more robust code.

### Null Safety: `None` vs `Option<T>`

Python gives you `None`, and it's easy to forget to check:

```python
def get_user(user_id: str):
    for u in users:
        if u.id == user_id:
            return u
    return None

user = get_user("123")
print(user.name) # Oof, runtime crash if user is None.
```

On the other side, Rust uses `Option<T>` and the compiler always **forces** you to handle the missing case:

```rust
fn get_user(id: &str) -> Option<User> {
    users.iter().find(|u| u.id == id).cloned()
}

let user = get_user("123");
// unwraps will panic if user is None.
// You can search for "unwrap" in your entire codebase to find all the places you need to handle!
println!("{}", user.unwrap().name);

// or, safely:
if let Some(user) = get_user("123") {
    println!("{}", user.name);
}
```

### Classes vs Structs and Traits

Python uses classes and duck-typing for object-oriented programming:

```python
class Circle:
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius ** 2

    def draw(self):
        print(f"Drawing a circle with radius {self.radius}")
```

Rust separates data (structs) from behavior (traits and impl blocks). It prefers composition over inheritance:

```rust
// The data
pub struct Circle {
    pub radius: f64,
}

// Behavior specific to Circle
impl Circle {
    pub fn new(radius: f64) -> Self {
        Self { radius }
    }
}

// Shared behavior (like a Protocol or Abstract Base Class in Python)
pub trait Shape {
    fn area(&self) -> f64;
}

impl Shape for Circle {
    fn area(&self) -> f64 {
        std::f64::consts::PI * self.radius.powi(2)
    }
}
```

### Async: `asyncio` vs `async fn`

Python's `asyncio` runs an event loop to handle concurrent I/O operations:

```python
import asyncio
import httpx

async def fetch_user(user_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/api/users/{user_id}")
        return response.json()

asyncio.run(fetch_user("123"))
```

Here is the equivalent in Rust using the `reqwest` and `tokio` crates:

```rust
async fn fetch_user(id: &str) -> Result<User, reqwest::Error> {
    let user = reqwest::get(format!("/api/users/{}", id))
        .await?
        .json::<User>()
        .await?;
    Ok(user)
}

#[tokio::main]
async fn main() {
    let result = fetch_user("123").await;
}
```

Rust async is different in one important way: **there is no built-in runtime**. Rust's standard library includes the `async`/`.await` syntax, but executing futures requires a library like [Tokio](https://tokio.rs).

By contrast, in Python, the `asyncio` library is part of the standard library and provides a built-in event loop.
That's great because it's ready to use out of the box, but it also means that Python imposes a runtime on you, which can be limiting (for example, if you like to run your code in an embedded environment).

In practice, almost 100% of production Rust applications use Tokio as their async runtime and it's just one `cargo add tokio` away, so I'd say the tradeoff is worth it for the flexibility and performance benefits you get from Rust's async model. But that's just my personal opinion.

## String Types: `String` vs `&str`

In Python, there is only one string type: `str`. It is immutable and garbage-collected.
In Rust, you will encounter two main string types: `String` and `&str`. This is one of the most common stumbling blocks for beginners.
Python developers rarely have to think about the difference between "stack" and "heap" memory or the difference between owned and borrowed data, but in Rust, these concepts are fundamental and non-trivial programs won't compile until you understand them.

In Rust:

- `String` is an owned, heap-allocated, type. It's the closest thing to Python's `str`. 
- `&str` is a borrowed string slice. It's an immutable *view* into a string.

Both types are guaranteed to be valid UTF-8, just like strings in Python 3+. 

```rust
// This is a &str (string literal)
let greeting = "Hello";

// This is a String
let mut owned_greeting = String::from("Hello");
owned_greeting.push_str(", world!");

// Functions often take &str so they can accept both String and &str
fn print_length(s: &str) {
    println!("Length is {}", s.len());
}

print_length(greeting); // Passing &str
print_length(&owned_greeting); // Passing String as &str via borrowing
```

## Popular Packages And Their Rust Counterparts

{% podcast_quote(player="s04e05-tembo?t=46:19", attribution="Adam Hendel, Founding Engineer at Tembo") %}
"I'm going to grab SQLx... 10 years ago it would have been Flask or FastAPI... I have the equivalent of everything that I, you know, five years ago would have gone to something in Python. For me, I'd just pick Rust. It's just easier. It's a better experience."
{% end %}

Python's rich ecosystem is a major draw. Rust's ecosystem is smaller but highly capable, especially for backend and data tasks.

| Python Package | Rust Equivalent | Notes |
| --- | --- | --- |
| `requests` / `httpx` | `reqwest` | The standard HTTP client in Rust |
| `FastAPI` / `Flask` | `axum` / `actix-web` | Axum is highly recommended and built on Tokio |
| `pydantic` / `marshmallow` | `serde` | Serde is the universal serialization framework in Rust |
| `SQLAlchemy` | `sqlx` / `diesel` | SQLx offers compile-time checked SQL queries |
| `click` / `argparse` | `clap` | Clap is the gold standard for CLI argument parsing |
| `pandas` | `polars` | Polars is actually written in Rust! |
| `pytest` | `cargo test` | Built directly into the Rust toolchain |
| `celery` | `faktory` / `river` | Background job processing |

## Key Challenges in Transitioning to Rust

The transition from Python to Rust presents unique challenges:

### Ownership and Borrowing

Python developers need to adjust to start "thinking in Rust" to avoid common pitfalls. 
Plan for a 3-4 month learning period where developers will need to understand concepts like:

- Stack vs heap
- Borrowing and move semantics
- Trait-based composition (instead of Python's OOP model)

These are fundamental concepts in Rust that Python developers are not used to, and it's important to get them right to become really effective.

Lifetimes are another concept that can be challenging to grasp initially, but you can get a long way without fully understanding them. [Don't worry about lifetimes](/blog/lifetimes) when you're just starting out. [Keep it simple](/blog/simple).

Pointer handling and boxing is another area where Python developers need to adjust. However, beginners can often get by without understanding this in detail.

While these concepts are often cited as major hurdles for newcomers, the payoff is immense: once you understand the core mechanics, it becomes much easier to write code that safely handles parallelism without extra effort: 

{% podcast_quote(player="s05e09-gama-space?t=50:21", attribution="Sebastian, Software Engineer at Gama") %}
"I, myself, after learning Rust this way, have come back to various Python projects and found out that code that I thought was perfectly fine, that I wrote many years ago... in Python, there's very little help for you to avoid [concurrency issues]."
{% end %}

### Type System Adaptation

Moving from Python's dynamic typing to Rust's static typing is another shift in mindset.

All of a sudden, you need to:

- Think about types upfront
- Understand generics and traits
- Lean into `Option<T>` and `Result<T, E>` for error handling
- Use enums for modeling complex states

This can feel intimidating at first, but it's actually a lot of fun once you get the hang of it.
The compiler is truly helpful and will guide you along the way, and you can start without a deep understanding of all the concepts.
(Just make sure you always read the full error message!)

Many Pythonistas like one Rust feature in particular: pattern matching.
It's is often cited as one of the most enjoyable features of Rust.

```rust
match agent {
    Some(spy) if spy.is_double_o_seven() && spy.face() == Actor::Lazenby => println!("This never happened to the other fella."),
    Some(_) => println!("Just another blunt instrument."),
    None => println!("Must be an operative of SPECTRE."),
}
```

## Integration Strategies

{% podcast_quote(player="s03e08-volvo?t=35:56", attribution="Julius Gustavsson, Senior Software Engineer at Volvo") %}
"But we also have a Python binding package around probe-rs so that we can use that in our system tests which are Python-based. And then you can essentially use it as any other Python library within our system tests."
{% end %}

There are several ways to integrate Rust into your Python codebase:

### 1. PyO3 (Python-Rust Bindings)

{% podcast_quote(player="s01e06-sentry?t=1:12:48", attribution="Arpad Borsos, Software Engineer at Sentry") %}
"And Rust, by the way, as we talked about, we use it from Python. And from Python, I can really recommend PyO3. It's a game changer from the ways we did it before. So it's actually very easy to use Rust from within other languages."
{% end %}

[PyO3](https://pyo3.rs/) lets you write Python extensions in Rust or call Rust functions from Python. 

PyO3 is ideal for:

- Optimizing performance-critical components
- Gradually introducing Rust while maintaining Python interfaces
- Creating Python packages with Rust internals

If you'd like to speed up a single Python code path which contains custom logic, using the foreign function interface (FFI) and PyO3 is the way to go.

{% podcast_quote(player="s06e01-cloudsmith?t=22:15", attribution="Cian Butler, Staff Software Engineer at Cloudsmith") %}
"If you didn't know it was written in Rust, you might not even have cared about it because it was yet another Python package that you just integrate into your workflow. And it was a drop-in replacement."
{% end %}

### 2. Microservices

For distributed systems, you can:

- Build new services in Rust
- Migrate existing services one at a time
- Use REST or gRPC for inter-service communication

If you already have a microservices architecture, this can be a great way to start.
You can build new services in Rust and gradually replace old Python services as needed.
The new services can be deployed alongside the old ones, and you can ensure that the APIs are compatible.

### 3. CLI Tools and Utilities

If you're just starting out, I recommend to write a command-line tool, which is an excellent candidate for
getting your feet wet. 

CLI tools have all the positive indicators for a successful first project: 

- They are self-contained, so you don't have to worry about integrating with the rest of the codebase 
- The deployment is simple, as you can just ship a single binary 
- Rust shines in this area, as it's very convenient to write command-line tools in Rust
- There is no "startup cost" when a CLI tool runs with Rust (as opposed to Python where the interpreter needs to start up) 

### 4. Worker Processes

Let's say you have a web application that needs to do some heavy lifting.
One common way is to offload the work to a worker queue.
That's a great place to test out Rust, as you can directly compare the performance and developer experience with Python.

You can use a message queue like RabbitMQ or Kafka to communicate between the Python web application and the Rust worker. 

### Data Processing Pipelines

Are you using Python for data science or ETL tasks?
For example, you might be using Pandas or Dask for data processing.

Rust has some excellent libraries for data processing, like [Polars](https://pola.rs/) and [Apache Arrow](https://arrow.apache.org/).
Many developers start by moving data preprocessing and ETL tasks to Rust, and they like it so much that they move more and more of the business logic over. 

That worked extremely well for a few clients I worked with, as they could leverage Rust's performance and reliability for the most critical parts of their data processing pipeline.
After a short learning period, the team was as productive in Rust as they were in Python.

## Planning Your Migration

A successful migration requires careful planning:

1. **Start Small**

   - Choose non-critical components first
   - Focus on areas where Rust's benefits are most valuable
   - Build team confidence through [early wins](/blog/successful-rust-business-adoption-checklist/)

2. **Invest in Training**

   - Allocate time for learning Rust fundamentals
   - Consider bringing in [external expertise](/services) for guidance
   - Set realistic expectations for the learning curve

3. **Measure Success**

   - Define clear metrics (performance, resource usage, development velocity)
   - Document improvements and challenges
   - Adjust strategy based on results

## Practical Migration Tips

Based on real-world experience from helping developers migrate from Python to Rust, here are some practical tips for a successful transition:

### Identify Bounded Contexts

Focus on modules with clear interfaces to the rest of your system. No tangled spaghetti code!
(That also means that you should refactor your Python codebase in case it's a mess.)

- Look for self-contained parts of your codebase that share common functionality
- Document the data flow and dependencies between these contexts. This will help you understand the impact of migration
  and can serve as a blueprint for the migration process and a reference for future developers.
- Map out how these components communicate with each other: which functions are called, which data is passed around, and which interfaces are used.

### Prioritize CPU-Bound Tasks First

Start with computationally intensive operations that don't require heavy I/O.
That's where Rust shines the most, as it can provide significant performance improvements over Python.

- Look for tasks that are currently bottlenecked by Python's performance (measure first!).
- Avoid beginning with components that make heavy use of async/IO operations.
  Async Python is quite efficient and Rust might not provide a significant improvement.
  Be cautious with async operations between languages, as they can introduce significant overhead.

### Minimize Calls Between Language Boundaries 

Evaluate how frequently your Rust code needs to call back into Python
and try to minimize the number of cross-language calls.

If you have a large number of small calls, the overhead of crossing the language boundary can add up.
Instead, consider batching operations to reduce the number of transitions

### Baby Steps

Break down the migration into small, measurable pieces. You want quick wins to keep the team motivated.

- Start with a single component and validate its performance.
- Add functionality piece by piece rather than attempting a complete rewrite.
- Maintain comprehensive tests throughout the migration process.

### Continuously Monitor Performance 

Do you have a performance baseline for your Python code?
If not, set one up before you start the migration.
It's very easy to get lost in the weeds and lose track of the performance improvements.
If that happens, you have no clear way to measure the success of the migration.

- Set up benchmarks before starting the migration.
- Track performance metrics for each migrated component.
- Use tools like `cspeed` to monitor improvements.
- Document performance gains and any unexpected bottlenecks.
- Make performance monitoring part of your PR review process.
- Choose components where you can easily compare performance.
- Look for opportunities to run old and new implementations in parallel.

## Navigating the Rust Ecosystem

Rust's ecosystem is smaller than Python's.

On top of that, Rust has a much smaller standard library compared to Python. 
This means you'll commonly rely on third-party crates for functionality that's built into Python.

Depending on your use case, here are some comparisons between Python packages and their Rust equivalents:

### Data Science

Python dominates data science with libraries like [NumPy](https://numpy.org/) and [Pandas](https://pandas.pydata.org/).
However, Rust is making inroads with libraries like [Polars](https://pola.rs/) and [Apache's Arrow](https://arrow.apache.org/).

You don't have to migrate your entire data science stack to Rust.
Chances are, you have experts on your team who are comfortable with doing data analysis in Python. 
You can start by using the Rust libraries for data preprocessing and ETL tasks.
They have Python bindings, so you get a lot of the benefits of Rust without having to do a full migration.

### Backend Services

Rust wasn't initially planned to be a strong contender in the web development space.
This has changed in recent years with the rise of frameworks like [Axum](https://axum.rs/) and [Loco](https://loco.rs/).
Now, Rust is a viable option for building [high-performance APIs](/blog/why-rust/) and web applications.
It is one key area the Rust team is investing in, and the ecosystem is maturing rapidly.

In combination with [sqlx](https://github.com/launchbadge/sqlx) for database access and [serde](https://serde.rs/) for serialization, Rust is a very effective choice for web backends. 
What surprises many Python developers is how similar it is to working with other web frameworks like Flask or FastAPI.
Another surprise is how robust the final product is, as it catches many bugs at compile time and scales extremely well.
Production Rust web applications are extremely robust.
This lifts a lot of the burden from the operations team.
I expect more backend services to be written in Rust in the future -- especially for high-performance applications.

## Keeping Python's Strengths

Not everything needs to be migrated! Python excels at:

- [I personally prototype in Rust](/blog/prototyping), but Python is still a fine choice for prototyping. 
- Data analysis and visualization are great in Python (e.g., Pandas, Matplotlib)
- Machine learning workflows (e.g., TensorFlow, PyTorch)
- Admin interfaces and tools (e.g., Django admin)

Consider a hybrid approach where each language handles what it does best.

One winning strategy is to explore a space in Python and moving production-workloads to Rust once the requirements are clear
and the project can benefit from performance and scale.
Speaking of which...

## Expected Big Performance Improvements

Actual performance numbers vary significantly based on workload and implementation,
so take these numbers with a grain of salt.

Based on my experience helping teams migrate, here are typical improvements:

- **CPU Usage**: 2-10x reduction in CPU utilization
- **Memory Usage**: 30-70% reduction in memory footprint
- **Latency**: 50-90% improvement in response times
- **Throughput**: 2-5x increase in requests/second

Especially the P90 latency improvements are often surprising to teams.
**There are very few outliers and things tend to run smoothly, no matter the load.**
In Python, this is a common source of frustration, where a single request can take significantly longer than the rest.
Production payloads are extremely boring in Rust. The DevOps team will thank you.

## Get Your Customized Migration Plan

I help teams migrate from Python to Rust, providing tailored guidance and training.
If you're considering a migration, answer a few questions about your project, and I'll reach out with a customized plan.

{% quiz() %}

const questions = [
  {
    type: "multipleChoice",
    question: "Which languages are currently used in your codebase?",
    id: "currentLanguages",
    options: languageOptions,
  },
  {
    type: "multipleChoice",
    question: "Which types of applications are you looking to migrate?",
    id: "applicationType",
    direction: "column",
    options: [
      "Web services / APIs",
      "CLI tools",
      "Embedded systems",
      "Desktop applications",
      "WebAssembly modules",
      "Data processing pipelines",
      "Machine learning systems",
      "Other",
    ],
  },
  {
    type: "radio",
    question: "What's the size of your codebase?",
    id: "codebaseSize",
    options: ["< 10k lines", "< 100k lines", "> 100k lines"],
  },
  {
    type: "radio",
    question: "What's your team's experience with Rust?",
    id: "rustExperience",
    direction: "column",
    options: [
      "No experience yet",
      "Some team members have experimented with it",
      "We have one or more small projects in production",
      "We have significant production experience",
    ],
  },
  {
    type: "multipleChoice",
    question: "What are your main motivations for migrating to Rust?",
    direction: "column",
    id: "motivations",
    options: [
      "Performance improvements",
      "Better type safety",
      "Memory efficiency",
      "Production reliability",
      "Cross-platform deployment",
      "WebAssembly support",
      "Embedded systems development",
      "Microservices migration",
      "Other",
    ],
  },
  {
    type: "multipleChoice",
    question: "What are your main concerns about migrating to Rust?",
    id: "concerns",
    direction: "column",
    options: [
      "Learning curve for the team",
      "Migration complexity",
      "Maintaining productivity during transition",
      "Finding Rust developers",
      "Integration with existing Python code",
      "Third-party library availability",
      "Build times",
      "Testing and deployment changes",
      "None/Other",
    ],
  },
  {
    type: "radio",
    question: "What's your timeline for the migration?",
    id: "timeline",
    options: [
      "Immediate (next 3 months)",
      "Medium-term (3-12 months)",
      "Long-term (12+ months)",
    ],
  },
  {
    type: "multipleChoice",
    question: "What kind of support is most important for your team?",
    id: "supportNeeded",
    direction: "column",
    options: [
      "Planning and strategy",
      "Project audit",
      "Training and workshops",
      "Code reviews and mentoring",
      "PyO3 integration support",
      "Performance optimization",
      "Architecture design",
      "Best practices guidance",
      "Team hiring support",
    ],
  },
  {
    type: "radio",
    question: "How many developers would be involved in the migration?",
    options: ["1", "2-3", "4-9", "10+"],
    id: "teamSize",
  },
  {
    type: "input",
    question: "Anything else you'd like to share about your migration plans?",
    id: "additionalComments",
    placeholder: "Share your thoughts...",
    optional: true,
  },
  {
    type: "email",
    question:
      "What's your email? I'll send you a customized migration strategy based on your responses.",
    id: "email",
    placeholder: "Your email address",
  },
];

const formURL = "https://submit-form.com/YkAFE1mIq";

{% end %}

## Conclusion

{% podcast_quote(player="s06e01-cloudsmith?t=1:08:44", attribution="Cian Butler, Staff Software Engineer at Cloudsmith") %}
"I didn't think 10 years ago I'd be still writing Python or JavaScript, but I'm still writing Python and JavaScript. But you look at them, and they're a lot different... I think Rust is here to stay. It's in low-level libraries for Python. It's in UV... It's becoming a core part of our industry."
{% end %}

Migrating to a different programming language is a significant undertaking that requires careful planning and execution.
The step from Python to Rust is no exception.

While the learning curve is steep, the benefits in terms of performance, reliability, and maintainability can be substantial. 

Success depends on:

- Realistic timeline expectations
- Strong team support and training
- Clear understanding of migration goals
- A pragmatic approach to choosing what to migrate

Remember that this isn't an all-or-nothing decision!
Many organizations successfully use Python and Rust together.
Before you start the migration, write down your reasoning for the migration.
Many issues can be solved in Python, and changing the entire stack might not be necessary.
However, if you do hit the limits of Python, Rust is a strong contender and I've seen many success stories of teams that made the switch and never looked back. 

{% info(title="Ready to Make the Move to Rust?", icon="crab") %}

I help teams make successful transitions from Python to Rust.
My clients moved critical workloads to Rust and saw significant improvements in performance and reliability.
If you liked my guide, chances are you will like the way I work as well. 
Whether you need training, architecture guidance, or migration planning, [let's talk about your needs](/services).

{% end %}