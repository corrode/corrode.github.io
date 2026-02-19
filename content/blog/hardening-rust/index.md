+++
title = "Hardening Rust Code Against Runtime Failures"
date = 2026-02-19
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
resources = [
   "[Patterns for Defensive Programming in Rust](/blog/defensive-programming) -- making your Rust code more robust by enforcing invariants",
   "[Pitfalls of Safe Rust](/blog/pitfalls-of-safe-rust) -- common mistakes even safe Rust programmers make",
]
+++

We talked about [patterns for defensive programming in Rust](/blog/defensive-programming) before, in which implicit invariants that aren't enforced by the compiler lead to demise and misery.
But being careful isn't enough.
Even valid code can fail at runtime in ways that are hard to predict and control.
That's what we're covering here.

This article is for you if you want to
- make your code resilient at runtime
- harden your Rust code for production 
- know how Rust code can fail in unexpected ways and how to recover from that

## Panic Semantics Are Part of Your API

Here's a question: what happens when a Rust program panics?

There is no single correct answer because `panic!` is not a "single behavior."

### Unwind vs. Abort

For starters, there's a difference between unwind and abort.

[`catch_unwind`](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html) invokes a closure, which captures the cause of an unwinding panic.

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
To handle them gracefully, you need to know exactly how and where your program will run, and design accordingly.
For example, in the case of `malloc`, avoid unbounded user input that could lead to excessive allocations.

### Thread-Level vs. Process-Level Failures

Another difference is between thread-level failures and process-level crashes.

A common misunderstanding is that `panic` terminates the entire program, but in a multi-threaded application, that is not necessarily the case.
For example, a background worker thread can panic while the main thread continues running.
What sounds like a benefit can leave the system in a partially degraded state. 

This distinction becomes especially important in long-running systems (servers, workers, async runtimes,...).
A panic in a request-handling thread might only abort that one request, while the rest of the service remains available.
Whether this is acceptable depends on the system's invariants.
If a panic indicates a violated assumption confined to a small scope, like a single request, letting the process continue may be reasonable.
But if it signals a global invariant violation, continuing execution can be outright dangerous.

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
Rust doesn't guarantee tail-call optimization—the compiler rewriting certain recursive calls into loops which don't grow the stack. This means deep recursion can lead to stack overflows, which cause unrecoverable crashes.

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

**Panic behavior isn't the only runtime failure mode you need to worry about.**

## Panic Hooks Are Your Last Line of Defense

Now that you understand how panics work, let's talk about observability.

When things go wrong, you want to know about it.
But by default, Rust panics just print to `stderr` and disappear into the void.
In production systems, that's not so great. 

You might prefer crash reporting, and/or centralized failure handling, and that's where panic hooks come in.
A panic hook is a function that gets called whenever a panic occurs, giving you a chance to handle it before the program terminates or unwinds.
It's your last line of defense to log, report, or clean up before the inevitable.

### Example Panic Hooks

Here's a simple example of setting a panic hook:

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

And here's a panic hook that sends structured JSON data to a crash reporting service:

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

And finally, here's [Sentry's panic hook handler](https://github.com/getsentry/sentry-rust/blob/625617015f2b64fabdf8264186911ca43873bb80/sentry-panic/src/lib.rs#L69-L77), which is even more sophisticated:

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

Sentry's panic hook:
- Logs the panic information 
- Preserves the previous panic hook behavior by calling `next(info)`
- Ensures the hook is only set once using `INIT.call_once`

There's a lot to learn from these few lines of code!

### Sanitizing Sensitive Data

Panic hooks are also your final opportunity to prevent information leaks.
Remember that panic messages can contain sensitive data like file paths, internal state, or user information (PII).
A well-designed panic hook sanitizes these messages before they reach logs or crash reports.

```rust
panic::set_hook(Box::new(|panic_info| {
    let sanitized_message = sanitize_panic_message(panic_info.to_string());
    log::error!("Application panic: {sanitized_message}");
}));
```

### Cleanup Operations

Before the process terminates, you might want to flush logs, close network connections, or notify other systems that this instance is going down. 
Setting a hook is a great way to perform such cleanup operations.
But be careful: these hooks run in an already-compromised environment, so avoid operations that could panic themselves.

### Limitations

Remember that panic hooks only run for unwinding panics.
If your program aborts on panic, or if the panic is caused by a stack overflow or out-of-memory condition, **your hook won't execute**.

Therefore **never rely on panic hooks for correctness.** 

They're purely for observability and graceful degradation; don't try to recover from logic errors as it is very hard to rely on a system's fragile underpinnings at this stage. 

## Release and Debug Builds Are Two Different Programs

One of the most dangerous assumptions in Rust development is that debug and release builds are functionally equivalent.
They're not.
In many ways, you're shipping a different program than the one you tested.

The most obvious difference is integer overflow behavior. Debug builds panic on overflow, while release builds silently wrap around.
We covered that in [Pitfalls of Safe Rust](/blog/pitfalls-of-safe-rust/).

But the differences run deeper than arithmetics.
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

The optimizer might move the timing calculation or inline `expensive_computation()` in ways that change the timing behavior and break your rate-limit logic.
One way around this is `black_box` from `std::hint`, which prevents the optimizer from making assumptions about certain values:

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

### Testing Release Behavior 

The fact that tests pass in debug mode tells you almost nothing about production behavior.
**Run your tests against release builds**. 

```bash
# Add this to your CI pipeline
cargo test --release
```

## Supply-Chain Security

Your code is only as safe as your dependencies.
You should regularly audit your dependencies for known vulnerabilities.
Two helpful tools for that are [`cargo-audit`](https://github.com/rustsec/rustsec/tree/main/cargo-audit) and [`cargo-deny`](https://embarkstudios.github.io/cargo-deny/).
It's recommended to run those as part of CI.

## Secure Allocations With mimalloc 

[mimalloc] is a drop-in global allocator built by Microsoft.
What's special about it is that it also has a **secure mode**, which "adds guard pages, randomized allocation, encrypted free lists, etc." to prevent heap-based vulnerabilities.
The performance penalty is usually around 10% according to mimalloc's own benchmarks, which is typically acceptable because Rust is never the bottleneck. [^mimalloc_safe]

To enable secure mode, put in Cargo.toml:

```toml
[dependencies]
mimalloc = { version = "*", features = ["secure"] }
```

Then use it as your global allocator:

```rust
use mimalloc::MiMalloc;

#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;
```

Now, all heap allocations in your Rust program will use mimalloc's secure allocator, which will automatically catch common heap vulnerabilities like buffer overflows and use-after-free bugs at runtime.
So even if your code has a memory safety issue, it will be much harder for an attacker to exploit it.

[mimalloc]: https://github.com/microsoft/mimalloc
[^mimalloc_safe]: https://docs.rs/mimalloc-safe/latest/mimalloc_safe/

## Limit Your Runtime Attack Surface

Even well-written Rust code can be compromised through its dependencies, environment, or C FFI boundaries.
The idea is to reduce your blast radius.
Now, how you do that depends on your deployment environment, but generally people use Docker and Linux, so I thought I'd share some techniques for those; specifically, how to build minimal container images and filesystem sandboxing.

### Minimal Docker images

A minimal production image contains exactly what you put in it.
No shell, no package manager, no utilities an attacker could abuse for lateral movement.
Even if your service is compromised, the attacker has very limited tools at their disposal to do further damage.

My recommendation is [Google's distroless images](https://github.com/GoogleContainerTools/distroless).
They are minimal Debian-based images stripped of everything unnecessary, while still including libc, TLS certificates, timezone data, and a non-root user.
Everything a typical service needs and nothing more.

```dockerfile
# Build stage
# Compile our Rust code into a statically linked binary
FROM rust:slim-bookworm AS build

RUN apt-get update && apt-get install -y musl-tools lld

WORKDIR /app
COPY . .
RUN cargo build --release

# Final image
FROM gcr.io/distroless/static-debian12

COPY --from=build /app/target/release/myapp /bin/myapp

USER nonroot
ENTRYPOINT ["/bin/myapp"]
```

Make sure to look up the latest `static-debian` variant [here](https://github.com/GoogleContainerTools/distroless).
It is essentially `FROM scratch` but with CA certificates and a `nonroot` user already included.
If you need libc (e.g. for SQLite or other C dependencies), use `gcr.io/distroless/cc-debian` instead.

{% info(title="A Note On Alpine Base Images", icon="info") %}

Alpine base images are a well-known alternative, but they can cause subtle runtime issues with Tokio and async runtimes due to musl's thread-local storage implementation.
([1](https://www.reddit.com/r/rust/comments/sq53vx/alpine_fails_to_run_my_app_what_steps_should_i/hwjloqz/)
[2](https://martinheinz.dev/blog/92)
[3](https://github.com/astral-sh/uv/issues/2732))

Distroless sidesteps this entirely.

{% end %}

### Filesystem sandboxing with Landlock

Even inside a minimal container, your process *still* has access to any file the container mounts.
[Landlock](https://docs.kernel.org/userspace-api/landlock.html) is a Linux security module that lets a process restrict its own filesystem access.
If your service is ever exploited, the attacker can only reach the files you explicitly allowed. [^below]

[^below]: This approach would have prevented a [vulnerability in Meta's `below` crate](https://security.opensuse.org/2025/03/12/below-world-writable-log-dir.html), a tool for recording and displaying system data like hardware utilization and cgroup information on Linux.

```rust
use landlock::{
    Access, AccessFs, PathBeneath, PathFd, Ruleset, RulesetAttr,
    RulesetCreatedAttr, ABI,
};

fn sandbox() -> Result<(), Box<dyn std::error::Error>> {
    let abi = ABI::V3;

    Ruleset::default()
        .handle_access(AccessFs::from_read(abi))?
        .create()?
        // Allow read-only access to /etc for config files
        .add_rule(PathBeneath::new(PathFd::new("/etc")?, AccessFs::from_read(abi)))?
        // Allow read+write access to /var/data for your app's data
        .add_rule(PathBeneath::new(
            PathFd::new("/var/data")?,
            AccessFs::from_all(abi),
        ))?
        .restrict_self()?;

    Ok(())
}

fn main() {
    sandbox().expect("failed to apply landlock sandbox");

    // Your service starts here.
    // The service is now restricted to /etc (read) and /var/data (read/write)
    // Any attempt to open /tmp, /home, /proc etc. will be denied!
}
```

Call `sandbox()` as early as possible in `main`, before spawning threads or accepting connections.
The restrictions apply to the entire process from that point forward.

The two approaches really go hand in hand: 
- `FROM scratch` limits what's *in* the container
- Landlock limits what the process can *touch* at runtime.

The big picture is that security hardening is about reducing the surface of things that can go wrong.
Every capability your process holds unnecessarily is a liability and everything your code manages that could be delegated to the OS, init system, or container runtime probably should be. 

## Runtime Hardening Tooling

Finally, here are some tools that help you catch problems before they hit production.

- [`miri`](https://github.com/rust-lang/miri) -- detects undefined behavior at runtime
- [`cargo-fuzz`](https://github.com/rust-fuzz/cargo-fuzz) -- fuzz testing for Rust code
- [`honggfuzz`](https://github.com/google/honggfuzz) -- another fuzzer with Rust support
- [`cargo-geiger`](https://github.com/geiger-rs/cargo-geiger) -- detects usage of unsafe code
- [`cargo-valgrind`](https://github.com/jfrimmel/cargo-valgrind) -- runs Valgrind on Rust code to find memory errors
- [`cargo-tarpaulin`](https://github.com/xd009642/tarpaulin) -- code coverage analysis for Rust projects

The tools above help catch undefined behavior, memory safety issues, code coverage gaps, and performance bottlenecks.
They are dynamic analysis tools that complement Rust's static guarantees.