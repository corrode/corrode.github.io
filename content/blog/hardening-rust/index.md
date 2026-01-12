+++
title = "Hardening Rust Code Against Runtime Failures"
date = 2026-01-13
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

We talked about Patterns for Defensive Programming in Rust before, in which implicit invariants that aren't enforced by the compiler lead to demise and misery.
But even being careful to prevent these mistakes is not enough to make your code truly robust.
What's missing is that even valid code can fail at runtime in ways that are hard to predict and control.
That's the topic of this article.

This article is for you if you:
- need to harden your Rust code for production 
- want to know how Rust code can fail in unexpected ways and how to recover from that
- want to make your code resilient at runtime

## Panic Semantics Are Part of Your API

Here's a question: what happens when a Rust program panics?

There is no single correct answer because `panic!` is not a single behavior.

For starters, there's a difference between unwind and abort.

[`catch_unwind`](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html) invokes a closure, capturing the cause of an unwinding panic if one occurs.

```rust
let result = panic::catch_unwind(|| {
    panic!("oh no!");
});
```

But the [Rustonomicon](https://doc.rust-lang.org/nomicon/unwinding.html) has the following to say about unwinding panics:

> We would encourage you to only **do this sparingly**. In particular, Rust's current unwinding implementation is heavily optimized for the "doesn't unwind" case. If a program doesn't unwind, there should be no runtime cost for the program being ready to unwind. [...] Ideally, you should only panic for programming errors or extreme problems.

The alternative to unwinding is aborting the entire process. That does what it says on the tin: the program immediately terminates without unwinding the stack or running destructors.
Crash and burn.
Weirdly enough, that's often the safer choice, especially when dealing with FFI boundaries or performance-critical code.

To enable aborting on panic, add the following to your `Cargo.toml`:

```toml
[profile.release]
panic = "abort"
```

And **even if** you did not explicitly configure this, catastrophic panics like stack overflows and out-of-memory errors **always abort the process**. That's because unwinding in these situations is unsafe and can lead to undefined behavior.

- Panics that would unwind across an extern "C" boundary are defined to abort instead of unwinding, because [letting unwinding cross that boundary is undefined behavior](https://doc.rust-lang.org/nomicon/ffi.html#panic-can-be-stopped-at-an-abi-boundary).
- And if a `malloc` fails, [it aborts the process](https://news.ycombinator.com/item?id=11369457). If that's a problem, you need to proactively check for allocation sizes before allocating or avoid heap allocations altogether.

These failures are fundamentally different from ordinary panics in that they cannot be caught or recovered from.
In order to handle them gracefully, you need to know how exactly your program will run and where, and design accordingly.
For example, in the case of `malloc`, avoid unbounded user input that could lead to excessive allocations.

Another difference is between thread-level failures and process-level crashes.

A common misunderstanding is that `panic` terminates the entire program, but in a multi-threaded application, that is not necessarily the case.
For example, a background worker thread can panic while the main thread continues running.
What sounds like a benefit can leave the system in a partially degraded state. 

This distinction becomes especially important in long-running systems (servers, workers, async runtimes,...).
A panic in a request-handling thread might only abort that one request, while the rest of the service remains available.
Whether this is acceptable depends on the invariants of the system. If a panic indicates a violated assumption confined to 
a small scope, such as a request, letting the process continue may be reasonable, but if it indicates a global invariant violation, it can be outright dangerous to continue execution.

The key insight is that panic behavior is **part of your system's failure model**.
Treating all panics as equivalent hides important distinctions and leads to fragile assumptions.
You should be explicit about whether a failure is allowed to take down a single task, a single thread, or the entire process. 

**Never panic in an uncontrolled manner.**

## Stack Overflow as a Failure Mode

Okay, you handle errors gracefully and you know how your system behaves on panic.
But did you account for stack overflows as well? 

Here's some simple recursive code that can quickly exhaust stack space:

```rust
fn factorial(n: u64) -> u64 {
    if n == 0 {
        1
    } else {
        n * factorial(n - 1)
    }
}
```

If you allow users to call this function with large inputs, it might crash your program.
Rust does not guarantee tail-call optimization, which is the compiler's ability to optimize certain recursive calls into loops that don't grow the stack, so deep recursion can lead to stack overflows, which is an unrecoverable crash.

It requires some experience, but for recursive algorithms where you're not in control of the input size, it's often safer to use an iterative approach:

```rust
fn factorial(n: u64) -> u64 {
    let mut result = 1;
    for i in 1..=n {
        result *= i;
    }
    result
}
```

## Panic Hooks: Your Last Line of Defense

When things go wrong, you want to know about it.
But by default, Rust panics just print to stderr and disappear into the void.
In production systems, that's not so great. 

What you need is structured logging, crash reporting, and/or centralized failure handling, and that's where panic hooks come in.

A panic hook is a function that gets called whenever a panic occurs, giving you a chance to handle it before the program terminates or unwinds.

```rust
use std::panic;

fn main() {
    panic::set_hook(Box::new(|panic_info| {
        eprintln!("Panic occurred: {}", panic_info);
        // Log to your monitoring system
        // Send crash reports
        // Clean up resources
    }));

    panic!("Something went wrong!");
}
```

For example, here's a panic hook that sends structured JSON data to a crash reporting service:

```rust
panic::set_hook(Box::new(|panic_info| {
    let panic_data = serde_json::json!({
        "message": panic_info.to_string(),
        "location": panic_info.location().map(|l| format!("{}:{}:{}", l.file(), l.line(), l.column())),
        "timestamp": chrono::Utc::now().to_rfc3339(),
        "version": env!("CARGO_PKG_VERSION"),
    });

    // Send to your crash reporting service
    crash_reporter::report(panic_data);
}));
```

And here's [Sentry's panic hook handler](https://github.com/getsentry/sentry-rust/blob/625617015f2b64fabdf8264186911ca43873bb80/sentry-panic/src/lib.rs#L69-L77), which is even more sophisticated:

```rust
fn setup(&self, _cfg: &mut ClientOptions) {
    INIT.call_once(|| {
        let next = panic::take_hook();
        panic::set_hook(Box::new(move |info| {
            panic_handler(info);
            next(info);
        }));
    });
}
```

This:

- Logs the panic information 
- Preserves the previous panic hook behavior by calling `next(info)`
- Ensures the hook is only set once using `INIT.call_once`

But there's more to it than just logging. Panic hooks are your opportunity to prevent information leaks.
Remember that panic messages can contain sensitive data like file paths, internal state, or user information.
A well-designed panic hook sanitizes these messages before they reach logs or crash reports.

```rust
panic::set_hook(Box::new(|panic_info| {
    let sanitized_message = sanitize_panic_message(panic_info.to_string());
    log::error!("Application panic: {sanitized_message}");
}));
```

Also, setting a hook is a great way to perform cleanup operations.
Before the process potentially terminates, you might want to flush logs, close network connections, or notify other systems that this instance is going down. 

But be careful—these hooks run in an already-compromised environment, so avoid operations that could themselves panic.

Also remember that panic hooks only run for unwinding panics.
If your program is configured to abort on panic, or if the panic is caused by a stack overflow or out-of-memory condition, your hook won't execute.

My final rule is: **never rely on panic hooks for correctness.** 
They're purely for observability and graceful degradation; don't try to recover from logic errors as it is very hard to know the program's state at this point.

## Release and Debug Builds Are Two Different Programs

One of the most dangerous assumptions in Rust development is that debug and release builds are functionally equivalent.
They're not.
In many ways, you're shipping a different program than the one you tested.

The most obvious difference is integer overflow behavior. Debug builds panic on overflow, while release builds silently wrap around.
We covered that in [Pitfalls of Safe Rust](/blog/pitfalls-of-safe-rust/).

But the differences run much deeper than arithmetic.
The optimizer makes assumptions about your code that can fundamentally change its behavior.

For example, the optimizer can reorder operations in ways that break timing-sensitive code:

```rust
fn rate_limited_operation() -> bool {
    let start = std::time::Instant::now();

    // Do some work
    expensive_computation();

    let elapsed = start.elapsed();
    if elapsed < std::time::Duration::from_millis(100) {
        // Rate limiting: reject if too fast
        return false;
    }

    true
}
```

The optimizer might move the timing calculation or inline `expensive_computation()` in ways that fundamentally change the timing behavior, which could break your rate-limit logic.
One way around this is to use `black_box` from `std::hint` to prevent the optimizer from making assumptions about certain values:

```rust
use std::hint::black_box;

fn rate_limited_operation() -> bool {
    let start = std::time::Instant::now();

    // Do some work
    black_box(expensive_computation());

    let elapsed = start.elapsed();
    if elapsed < std::time::Duration::from_millis(100) {
        // Rate limiting: reject if too fast
        return false;
    }

    true
}
```

It's telling the compiler: "Don't touch this; assume it could have side effects you don't know about."

### Making Release Behavior Explicit

The fact that tests pass in debug mode tells you almost nothing about production behavior.
**Run your tests against release builds**. 

```bash
# Add this to your CI pipeline
cargo test --release
```

Remember: if your code relies on behavior that only exists in debug builds, it's not actually tested.
The optimizer can and will eliminate code it deems unnecessary.


## Supply-Chain Security

Your code is only as safe as your dependencies.
You should regularly audit your dependencies for known vulnerabilities.
Two helpful tools for that are [`cargo-audit`](https://github.com/rustsec/rustsec/tree/main/cargo-audit) and [`cargo-deny`](https://embarkstudios.github.io/cargo-deny/).

## Runtime Hardening Tooling

Here are some useful tools to harden your Rust code against runtime failures:

- [`miri`](https://github.com/rust-lang/miri)
- [`cargo-fuzz`](https://github.com/rust-fuzz/cargo-fuzz)
- [`honggfuzz`](https://github.com/google/honggfuzz)
- [`cargo-geiger`](https://github.com/geiger-rs/cargo-geiger)
- [`cargo-valgrind`](https://github.com/jfrimmel/cargo-valgrind)
- [`cargo-tarpaulin`](https://github.com/xd009642/tarpaulin)

The tools above help catch undefined behavior, memory safety issues, code coverage gaps, and performance bottlenecks.
They are dynamic analysis tools that complement Rust's static guarantees.