+++
title="Rust and C++ Interop"
date=2026-07-30
template = "article.html"
[extra]
series = "Idiomatic Rust"
chapter_title = "Living With Two Languages In One Process"
resources = [
    "[A tour of the Rust and C++ interoperability ecosystem](https://www.eshard.com/blog/rust-cxx-interop): eShard's hands-on comparison of `cxx`, `bindgen`, `cbindgen`, and `autocxx`",
    "[Integrating Rust and C++ in Firefox](https://manishearth.github.io/blog/2021/02/22/integrating-rust-and-c-plus-plus-in-firefox/): Manish Goregaokar's long-form post on the bindings Mozilla actually ships",
    "[Rust/C++ Interop in the Android Platform](https://security.googleblog.com/2021/06/rustc-interop-in-android-platform.html): Google's writeup on how AOSP wires Rust and C++ together",
    "[Weighing up Zngur and CXX for Rust/C++ Interop](https://www.kdab.com/weighing-up-zngur-and-cxx-for-rustc-interop/): KDAB's 2026 comparison of the two main approaches",
    "[Rust/C++ Interop Part 5 — Interop in 2025](https://tylerjw.dev/posts/20251003-rust-cpp-interop-2025-update/): Tyler Weaver's complete, working example with CMake, `cxx`, and Corrosion",
    "[Rust in Production: Rust for Linux Live with Alice Ryhl and Greg Kroah-Hartman](/podcast/s06e04-rust4linux/): the episode where Alice makes the case that interop, not rewrites, is how Rust wins",
    "[Rust in Production: Microsoft with Victor Ciura](/podcast/s04e01-microsoft/): our episode on what large-scale Rust/C++ interop looks like inside Microsoft",
    "[Rust has three reference types!](https://ssbr.xyz/blog/rust-has-three-reference-types/): the Crubit team on why `&T`, `&mut T`, and `Pin<&mut T>` aren't enough at the boundary",
    "[How we interfaced single-threaded C++ with multi-threaded Rust](https://antithesis.com/blog/2026/rust_cpp/): Antithesis's deep dive on `MainThreadToken`, `SendWrapper`, and the C++ `ref_ptr` segfault that started it all",
    "[FFI optimizations and benchmarking](https://godot-rust.github.io/dev/ffi-optimizations-benchmarking/): the godot-rust team measures FFI overhead at single-digit nanoseconds and dispels the \"FFI is slow\" myth",
    "[Rust on Android \u2014 Lessons from the Edge](https://greptime.com/blogs/2025-04-14-rust-in-android-edge-based-practice): GreptimeDB on stripped binaries, split debug info, and reconstructing readable panic backtraces in production",
    "[Actors and Factories in Rust (RustConf 2024)](https://2024.rustconf.com/schedule#actors-and-factories-in-rust-distributed-processing-overload-protection): a real-world account of bridging Folly's C++ executors and futures with Tokio",
    "[`cxx-async`](https://github.com/pcwalton/cxx-async): Patrick Walton's companion crate that maps Rust `Future`s to C++20 awaitables \u2014 the closest thing to a turnkey async-FFI solution today",
    "[Rust async is colored, and that's not a big deal](https://morestina.net/blog/1686/rust-async-is-colored): the clearest explanation of why bridging two async runtimes is fundamentally harder than bridging two type systems",
    "[Cancelling async Rust](https://sunshowers.io/posts/cancelling-async-rust/) and [Mutex without lock, Queue without push](https://cliffle.com/blog/lilos-cancel-safety/): the two essential reads on cancel safety before you design any async boundary",
    "[C++ Migration Strategies (Oxidize 2024)](https://www.youtube.com/watch?v=Je2wIns8x80): Til Adam (KDAB) and Florian Gilcher (Ferrous Systems) on what actually works when you ship Rust into a C++ codebase \u2014 the best single overview talk on this topic",
]
+++

> Interop, not rewrites, is how Rust wins inside Linux.
>
> &mdash; [Alice Ryhl, *Rust in Production* S06E04](/podcast/s06e04-rust4linux/)

I really like this quote by Alice, who is a Tokio core maintainer and a Rust4Linux contributor.

Experienced developers are not against using Rust (most of them think the language is great!), but they know that interop is the hard part.

That aligns with the [Microsoft episode of *Rust in Production*](/podcast/s04e01-microsoft/) with Victor Ciura. My takeaway was that the biggest challenge for gradual Rust adoption inside Microsoft is interop, and specifically interop with C++.

You can't rewrite 35 million lines of C, neither would you want to. The work that matters is the work that lets a new Rust service call into existing subsystems without giving up the guarantees that made you reach for Rust in the first place. The same logic applies one level up: you're not going to rewrite Chromium, Office, Photoshop, or your in-house engine either. **Interop is the new rewrite.**

I don't think this is going to change anytime soon. C++ is somewhere between [100 and 200 million lines](https://lwn.net/Articles/1036912/) of code inside Google *alone*. Most of the interesting Rust work over the next decade will happen *next to* a C++ codebase, not instead of one.

So let's talk about what actually goes wrong at that boundary and the state of the ecosystem.

## Interop Tooling Overview 

The interop space has grown a lot, and it's hard to keep track of all the options.

| Tool | Direction | What it's good at | When to avoid |
|---|---|---|---|
| Hand-written `extern "C"` | both | small, stable C-shaped APIs; total control | non-trivial types, large surface area |
| [`bindgen`](https://github.com/rust-lang/rust-bindgen) | C/C++ → Rust | parsing C headers, maybe some basic C++ | anything with templates, overloads, exceptions |
| [`cbindgen`](https://github.com/mozilla/cbindgen) | Rust → C/C++ | generating C/C++ headers from Rust | round-tripping C++ types |
| [`cxx`](https://github.com/dtolnay/cxx) | bidirectional | the 80% case; a curated subset of C++ that maps cleanly to Rust | exotic C++ (templates, virtual inheritance, exceptions in your hot path) |
| [`autocxx`](https://github.com/google/autocxx) | C++ → Rust (mostly) | larger existing C++ APIs you don't want to wrap by hand | when you need rock-solid stability today |
| [`Crubit`](https://github.com/google/crubit) | bidirectional | deep, mostly-automatic C++ ↔ Rust integration | anywhere outside a Bazel monorepo (today) |
| [`Zngur`](https://github.com/HKalbasi/zngur) | bidirectional | owned C++ values, templates, generics across the boundary | early days; smaller community |
| [`CXX-Qt`](https://github.com/KDAB/cxx-qt) | bidirectional | Qt/QML applications with Rust business logic | non-Qt projects |

In their Oxidize talk [*C++ Migration Strategies*](https://www.youtube.com/watch?v=Je2wIns8x80), Til Adam (KDAB) and Florian Gilcher (Ferrous Systems) give a great overview of the current state of affairs. They each ship Rust/C++ interop for paying customers (KDAB on the Qt and KDE side, Ferrous Systems on safety-critical and embedded).

{{ yt(id="Je2wIns8x80", title="C++ Migration Strategies — Til Adam (KDAB) & Florian Gilcher (Ferrous Systems), Oxidize 2024") }}

## My Current Recommendations For Most Teams

**Reach for `cxx` first.** It is, by a wide margin, the most battle-tested option. Mozilla uses it in Firefox, Google uses it in parts of Android, Brave embeds it deep in their browser ([they talked about it on the podcast](/podcast/s03e07-brave/)), and Slint, CXX-Qt, and a long tail of smaller projects all build on it.[^cxx-users] The KDAB team summarized the trade-off well in their [Zngur comparison](https://www.kdab.com/weighing-up-zngur-and-cxx-for-rustc-interop/): `cxx` is *opinionated* about which C++ types it will let through, and that opinionatedness is exactly why it's safe.

**Be careful with `bindgen` for C++.** `bindgen` is wonderful for C. For C++ it **silently** skips anything it can't represent (templates, overloads, non-trivial constructors), and what you get back is `unsafe` *everything*. Manish's [Firefox post](https://manishearth.github.io/blog/2021/02/22/integrating-rust-and-c-plus-plus-in-firefox/) is still the best writeup of what that means in practice.

**Don't deploy `Crubit` yet (unless you use Bazel).** Crubit is quite impressive (see Taylor Cramer's [RustConf 2025 interview](https://www.youtube.com/watch?v=eUTsOWbOHeY)), and Google funded it alongside a [$1M grant to the Rust Foundation](https://security.googleblog.com/2024/09/eliminating-memory-safety-vulnerabilities-Android.html) specifically to push this story forward. But it lives inside a Bazel monorepo and depends on bleeding-edge compiler features. For now it's a research-only project, not a tool you drop into your repo without scrutiny.

{{ yt(id="eUTsOWbOHeY", title="Taylor Cramer Interview, Crubit Development Lead at Google (RustConf 2025)") }}

### Rule: The tool should match your API, not the language 

If your C++ interface is already C-like (`extern "C"` headers, POD structs, opaque handles), don't reach for a code generator. Hand-written `extern "C"` plus a thin Rust wrapper is shorter, easier to debug, and easier to audit. If you heavily use `std::unique_ptr`, `std::string`, or shared enums, `cxx` is most likely the right choice.

## `#[repr(Rust)]` Is Not An ABI

You might believe that `#[repr(Rust)]` is a stable layout, but it is not.
It can happen that you define a struct in Rust, pass it to C++, and it works fine; but then you upgrade your compiler and the layout changes, which leads to silent data corruption.

Rust's default `#[repr(Rust)]` layout is [intentionally unspecified](https://github.com/rust-lang/rfcs/blob/master/text/0079-undefined-struct-layout.md). The compiler reorders fields, packs niches into enum discriminants, and may change those decisions between versions.
For a deep dive, read Aria Desires' [Notes on type layouts and ABIs in Rust](https://faultlore.com/blah/rust-layouts-and-abis/).

In practice, that means for anything that crosses the boundary, you need one of:

```rust
#[repr(C)]                 // C-compatible layout
#[repr(transparent)]       // same layout and ABI as the single inner field
#[repr(u8)] / #[repr(i32)] // for enums with a fixed discriminant
```

A useful mental model for what's safe to put on the wire:

| Leave on the Rust side | Convert at the edge to | Safe to cross the boundary |
|---|:---:|---|
| `String`, `&str` | &rarr; | `#[repr(C)]` structs |
| `Vec<T>`, `&[T]` | &rarr; | `#[repr(transparent)]` newtypes |
| `Result<T, E>`, `Option<T>` (with data) | &rarr; | Fixed-width integers (`u32`, `i64`, ...) |
| `Box<dyn Trait>`, `&dyn Trait` | &rarr; | Raw pointers (`*const T`, `*mut T`) |
| Tuples, closures | &rarr; | C-like enums (`#[repr(u8)]` / `#[repr(i32)]`) |

The left column is what you write inside your Rust code. The right column is what you let cross an `extern` function signature. The job of your FFI wrapper is the conversion in the middle.

A few corollaries: 

### Don't pass Rust enums with data across FFI.

A `Result<T, E>` or `Option<NonZeroU32>` has a defined layout *in your version of rustc, today*, but it isn't part of the language contract. Either lower it to a `#[repr(C)]` enum with explicit discriminants ([RFC 2195](https://github.com/rust-lang/rfcs/blob/master/text/2195-really-tagged-unions.md) calls these "really tagged unions"), or split it into a status code plus an out-parameter.

If you're using `cxx`, you get a slightly better version: a Rust function declared as `-> Result<T>` in the bridge marshals as a C++ function that may throw a single exception type, and a C++ function that throws is reflected back into Rust as a `Result<T, cxx::Exception>`.

The eShard team's [tour of the interop ecosystem](https://www.eshard.com/blog/rust-cxx-interop) demonstrates this pattern. 
Their `OpenDatabase` struct carries a `UniquePtr<ResourceDatabase>`, an explicit `OpenDatabaseStatus` enum, and a `String error_message`, all `#[repr(C)]` via `cxx`.

```rust
#[cxx::bridge]
mod ffi {
    #[namespace = "reven::sqlite::ffi"]
    enum OpenDatabaseStatus {
        Ok,
        DatabaseError,
        ReadMetadataError,
    }

    #[namespace = "reven::sqlite::ffi"]
    struct OpenDatabase {
        db: UniquePtr<ResourceDatabase>, // `ResourceDatabase` is a C++ type
        status: OpenDatabaseStatus,
        error_message: String,
    }
}
```

The status code is the wire contract.
The rich error data is carried in the `error_message` string.
That's the "status code plus out-parameter" pattern, and it's how you can propagate `anyhow`-style context without exporting `anyhow::Error`.

If you need true rich error chains, encode them on the Rust side and pass them across as a serialized blob (`Vec<u8>` with a stable format, such as protobuf, postcard, JSON), then reconstruct on the other side. Trying to share a `dyn std::error::Error` across the boundary is just asking for trouble.[^vtable]

[^vtable]: The vtable layout is not part of the language contract, and you can't guarantee that the C++ side will be able to call back into Rust correctly. 

```rust
// Wrong: layout of Result is not part of the language contract.
#[no_mangle]
pub extern "C" fn parse(input: *const u8, len: usize) -> Result<u64, ParseError> {
    /* ... */
}

// Right: explicit status code + out-parameter.
#[repr(C)]
pub enum ParseStatus { Ok = 0, Empty = 1, Overflow = 2, BadDigit = 3 }

#[no_mangle]
pub unsafe extern "C" fn parse(
    input: *const u8,
    len: usize,
    out: *mut u64,
) -> ParseStatus {
    /* ... write *out only on ParseStatus::Ok ... */
    ParseStatus::Ok
}
```

### Don't pass `&str` or `String`.

A Rust `String` carries a capacity field and uses Rust's allocator. A C++ `std::string` doesn't, and uses C++'s. They are not the same type at the bytes level. Use `&[u8]` / `*const u8 + len`, or let `cxx` give you a `CxxString` and a `&str` on either side.

{% mermaid() %}
flowchart TB
    subgraph rust ["Rust String (3 words, Rust allocator)"]
        direction TB
        r1["ptr"] --- r2["len"] --- r3["capacity"]
    end
    subgraph cpp ["C++ std::string (impl-defined, may use SSO)"]
        direction TB
        c1["SSO buffer"] --- c2["ptr"] --- c3["len"] --- c4["capacity"]
    end
    subgraph wire ["Wire format across FFI"]
        direction TB
        w1["ptr"] --- w2["len"]
    end
    rust -. "copy bytes" .-> wire
    cpp -. "copy bytes" .-> wire
{% end %}

Neither layout is part of a stable ABI. The only thing both sides agree on is a pointer and a length, so that's what you put on the wire, with the receiving side copying into its own native type if it wants ownership.

```rust
// Wrong: layout of String is not stable, allocator mismatch.
extern "C" { fn cpp_log(msg: String); }

// Right: pass the bytes; let the receiver copy if it wants ownership.
extern "C" { fn cpp_log(msg: *const u8, len: usize); }

fn log(msg: &str) {
    unsafe { cpp_log(msg.as_ptr(), msg.len()) }
}
```

With `cxx`, this becomes:

```rust
#[cxx::bridge]
mod ffi {
    extern "Rust" {
        fn log(msg: &str);            // safe: cxx generates the marshalling
    }
    unsafe extern "C++" {
        fn cpp_log(msg: &CxxString);  // borrow a real std::string from C++
    }
}
```

### Pointers and slices have edge cases.

David Benjamin's [*Passing nothing is surprisingly difficult*](https://davidben.net/2024/01/15/empty-slices.html) explains why an empty `&[T]` may have a non-null but unaligned `data` pointer, while C and C++ APIs frequently expect either null or a real allocation. If your callee dereferences `data` even when `len == 0`, you have undefined behavior. Wrap with `if slice.is_empty() { ptr::null() } else { slice.as_ptr() }` at the boundary.

### Bitfields don't work.

Rust does not have C-compatible bitfields. `bindgen` emits getter/setter shims, but if you're hand-writing the struct, you need to pack and unpack the bits yourself. The Immunant team has [a good writeup](https://immunant.com/blog/2020/01/bitfields/) of how much pain this still is.

```c
// C header:
struct Flags { uint8_t a : 3; uint8_t b : 5; };
```

```rust
// Rust equivalent: one byte, pack and unpack by hand.
#[repr(transparent)]
pub struct Flags(u8);

impl Flags {
    pub fn a(self) -> u8 { self.0 & 0b0000_0111 }
    pub fn b(self) -> u8 { (self.0 >> 3) & 0b0001_1111 }
    pub fn new(a: u8, b: u8) -> Self {
        Self((a & 0b111) | ((b & 0b1_1111) << 3))
    }
}
```

Watch out: C bitfield ordering is implementation-defined.

<details>
    <summary>
        Always check what <code>clang -fdump-record-layouts</code> says before assuming little-endian-first.
(Click here for an example.)
    </summary>

```sh
❯ printf 'typedef struct S { unsigned a:3; unsigned b:5; unsigned c:8; } S;\nint f(void) { return sizeof(S); }\n' | clang -Xclang -fdump-record-layouts -fsyntax-only -x c -

*** Dumping AST Record Layout
         0 | struct S
     0:0-2 |   unsigned int a
     0:3-7 |   unsigned int b
     1:0-7 |   unsigned int c
           | [sizeof=4, align=4]
```
</details>

{% info(title="Rule: Treat every struct that crosses the boundary as part of your public ABI") %}

That means `#[repr(C)]` (or `transparent`), explicit field types (`u32`, not `usize`, unless you really mean `size_t`), no Rust-style enums, no `String`, no `Vec` by value.
If you find yourself reaching for the standard library at the FFI line, you're most likely doing it wrong (unless you use `cxx`).

{% end %}

## C++ Has Move Constructors. Rust Has `Pin`. They Don't Match.

In C++, *every non-trivial type is effectively pinned*.
It may hold pointers into itself, and the type's move constructor exists specifically to fix up those pointers when the object is relocated.
In Rust, it's the opposite: every value is trivially `memmove`-able unless it's wrapped in `Pin`.

If you try to translate a `std::string`, `std::list`, or any class with a user-defined move constructor naïvely, you end up with self-references that get torn apart the first time the Rust side moves the value. The typical symptom is that everything looks fine for a while, then segfaults under load. (Because under load, the allocator is more likely to relocate the value, which is when the self-references break.)

The Crubit team has [a good writeup](https://ssbr.xyz/blog/rust-has-three-reference-types/) of why this is important: in a codebase doing serious C++ interop, `Pin<&mut T>` is as common as `&mut T`, and that's quite unergonomic. `cxx` solves this pragmatically by only ever letting you touch a C++ value through a `&CxxString`, `Pin<&mut CxxString>`, or `UniquePtr<CxxString>`. That sounds restrictive, but much better than debugging a use-after-move.

Miguel Young de la Sota's [*Move Constructors: Is it Possible?*](https://www.youtube.com/watch?v=UrDhMWISR3w) RustConf talk and the [`moveit`](https://crates.io/crates/moveit) crate explore what a fuller answer could look like. It's a glimpse of a future where this is solved at the type-system level.

{{ yt(id="UrDhMWISR3w", title="RustConf 2021 — Move Constructors: Is it Possible? by Miguel Young de la Sota") }}

The rules of thumb are:

1. **Never put a C++ object with a non-trivial move constructor on the Rust stack by value.** Always go through `Box`, `UniquePtr`, or a reference.
2. **Treat anything coming out of a C++ container as pinned.** No `mem::replace`, no `mem::swap`, no destructuring.
3. **If you need to construct a C++ object in place, use a helper that takes a `Pin<&mut MaybeUninit<T>>`.** `cxx` and `moveit` both provide patterns here. 

### Rule: Don't try to "own" a C++ value in Rust

Own a handle to it (`UniquePtr<T>`, `SharedPtr<T>`, `Box<T>` from C++'s `new`) and let the C++ destructor do the cleanup. The moment you try to teach Rust about C++ move semantics by hand, you're writing your own miniature [`moveit`](https://crates.io/crates/moveit) and you will get it wrong.

## Templates, Generics, And The Container Problem

This is the question that derails more `cxx` adoptions than any other: "how do I pass a `std::vector<MyType>` across the boundary?"

The honest answer is: you mostly don't. `cxx` ships with a curated set of containers it understands — `CxxVector<T>`, `CxxString`, `UniquePtr<T>`, `SharedPtr<T>`, `Vec<T>`, `String`, `Box<T>` — and `T` has to be a type `cxx` knows how to marshal. Nested generics (`std::vector<std::vector<T>>`, `std::map<K, V>`, `std::optional<T>`) and your own templated classes are not supported. The escape hatch is the *opaque newtype*: wrap the offending type in a class with a non-templated name, expose only the operations you need, and treat the inside as a black box.

The KDAB team's [Zngur vs CXX comparison](https://www.kdab.com/weighing-up-zngur-and-cxx-for-rustc-interop/) is the clearest writeup of the trade-off. Zngur lets you cross with `Vec<Vec<i32>>`, `HashMap<K, V>`, and `Box<dyn Trait>` directly, at the cost of having to declare each concrete instantiation in an IDL file:

```text
// Zngur IDL: every concrete generic instantiation is declared by hand.
type Vec<i32> {
    #layout(size = 24, align = 8);
    fn new() -> Vec<i32>;
    fn push(&mut self, i32);
    fn len(&self) -> usize;
}
type Vec<Vec<i32>> { /* ... */ }
```

`cxx` won't let you write that at all, but it will let you wrap it:

```rust
// cxx: an opaque newtype that hides the generic from the bridge.
#[cxx::bridge]
mod ffi {
    unsafe extern "C++" {
        include!("matrix.h");
        type Matrix;                       // opaque, C++-side only
        fn new_matrix(rows: usize, cols: usize) -> UniquePtr<Matrix>;
        fn get(&self, r: usize, c: usize) -> i32;
        fn set(self: Pin<&mut Matrix>, r: usize, c: usize, v: i32);
    }
}
```

My recommendation matches the KDAB writeup: if your codebase has a handful of templated types at the boundary, use `cxx` with opaque newtypes — you'll write a little more glue but you get static `Send`/`Sync` checks and a much larger community. If your boundary is *dominated* by generic containers (numerical code, graph libraries, ECS), Zngur becomes interesting despite the rough edges. If you have C++ templates with non-trivial generic logic that you actually want monomorphized in Rust, you're in Crubit territory — see the tooling section.

## Async/Sync Mismatch Is The Hard Part

If your Rust side runs Tokio and your C++ side runs an event loop, a thread pool, or [Folly](https://github.com/facebook/folly) coroutines, you have an *executor* problem before you have an *interop* problem. The two runtimes don't know about each other, can't cooperatively yield to each other, and have wildly different cancellation semantics. None of the existing bindings generators (as of 2026) fully solve this; they only give you the primitives to solve it yourself. The closest thing to a turnkey answer is [`cxx-async`](https://github.com/pcwalton/cxx-async), Patrick Walton's companion crate to `cxx` that maps Rust `Future`s to C++20 awaitables and vice versa — useful when both sides have already chosen modern coroutine machinery, and noted by the KDAB team as one of [`cxx`'s real advantages over Zngur](https://www.kdab.com/weighing-up-zngur-and-cxx-for-rustc-interop/). For everyone else, you're building the bridge by hand.

It's worth dwelling for a moment on *why* this is hard, because the underlying issue isn't C++-specific. Yoshua Wuyts' essay [*Rust async is colored, and that's not a big deal*](https://morestina.net/blog/1686/rust-async-is-colored) is the clearest explanation I know: every async runtime has its own scheduler, its own notion of "task," and its own rules about what counts as blocking. When you bridge two runtimes, you're not just translating types — you're deciding which runtime's notion of "a thing currently happening" is canonical, and how the other one is allowed to participate. The Encore team's [Rust-runtime-for-TypeScript writeup](https://encore.dev/blog/rust-runtime) describes exactly the same problem in a different domain: a JavaScript Promise has to become a Tokio future via a `.then()` callback that resolves through a channel. Different host, same shape.

The pattern that survives in production is the same one the Antithesis team [arrived at after two rewrites](https://antithesis.com/blog/2026/rust_cpp/):

1. Keep a **thin synchronous Rust shim** that is called directly by C++.
2. That shim's only job is to push work into an `async` channel and (sometimes) await a reply on another channel.
3. The actual async Rust lives on a Tokio runtime that the shim owns, on threads C++ never touches directly.

{% mermaid() %}
flowchart LR
    cpp["C++ main loop<br/>(synchronous)"]
    shim["Sync Rust shim<br/>cxx::bridge surface"]
    chan1(["async channel<br/>(request)"])
    chan2(["async channel<br/>(reply)"])
    rt["Tokio runtime<br/>async controller"]
    cpp -->|call| shim
    shim -->|send| chan1
    chan1 --> rt
    rt -->|send| chan2
    chan2 --> shim
    shim -->|return| cpp
{% end %}

This turns the impedance mismatch into a queue, which is a problem you already know how to reason about: bounded vs. unbounded, backpressure, drop-on-overload. The Antithesis team uses this to drive a single-threaded C++ fuzzer from a multi-threaded async Rust controller; Tomasz Pieczerak's [RustConf 2024 talk](https://www.youtube.com/watch?v=zQ6EyQJRxIs) describes the same pattern at production scale, bridging Folly's C++ executors, futures, and coroutines into a Tokio-based actor framework. It's the best 20-minute video on this topic that I know of.

{{ yt(id="zQ6EyQJRxIs", title="Actors and Factories in Rust — RustConf 2024") }}

For the related problem of exposing Rust futures *out* to a host language (Python, TypeScript, Ruby), Sam Lijin's [Seattle Rust talk](https://www.youtube.com/watch?v=Zs6Uer3VAyQ) is the best survey of what the runtime-bridging menu looks like in 2025. The C++ case is harder than any of those (because C++ also has its own native coroutines), but the failure modes are identical.

A few specific traps to know about:

- **Don't `block_on` inside a `cxx` callback that may itself be called from a Tokio worker.** You'll deadlock the runtime the first time the work the callback waits for happens to land on the same worker thread. The morestina post covers this anti-pattern in detail under the "don't hide the color" rule.
- **Cancellation is not portable.** A dropped Rust future runs destructors and stops polling; a cancelled C++ coroutine does whatever the host runtime decides. If you need cancellation to cross, encode it as an explicit "cancel" message on the channel, not as a future drop. Rain Paharia's [*Cancelling async Rust*](https://sunshowers.io/posts/cancelling-async-rust/) and Cliff Biffle's [*Mutex without lock, Queue without push*](https://cliffle.com/blog/lilos-cancel-safety/) are the two best treatments of *cancel safety* itself — read them before you design the cancel side of your bridge, not after.
- **Pin the Tokio runtime's lifetime to something C++ understands.** If C++ tears down the process while a Tokio worker is mid-syscall, you get the kind of shutdown crash that only reproduces in CI. A `tokio::runtime::Runtime` held in a `UniquePtr`-equivalent that C++ explicitly destroys works well.
- **Be careful what kind of future you put on the channel.** If the future itself holds a C++ resource (e.g., a `Pin<&mut CxxString>`), you've recreated the threading problem from the previous section *inside* the async one. The safe pattern is: channels carry owned values or `SendWrapper`s, the C++-touching work happens on the sync shim side.

### Rule: Treat async/sync as a queue boundary, not a function-call boundary

The moment you try to make one runtime's primitives directly visible to the other, you're building a custom executor bridge. Almost nobody actually needs that. A channel and a sync shim get you 95% of the way there with vastly less risk — and when you do need the remaining 5%, `cxx-async` is the place to start, not a hand-rolled `RawWaker`.

## Threading: `Send`, `Sync`, And Methods That Aren't Either

Rust's thread-safety model is *per-type*: a `T` is either `Send` or it isn't, and either `Sync` or it isn't. C++'s is *per-method*, *per-instance*, and frequently *in the documentation only*. Reconciling these is the second-hardest interop problem after async.

The Antithesis writeup is, I think, the best treatment of this anywhere. Their problem in one sentence: some C++ methods on the same class are safe to call from any thread, some are only safe to call from the main thread, and `cxx` (rightly) gives you a single `Sync` bit to express that with. Their solution has three moving parts worth knowing about even if you don't copy them verbatim:

**1. A `MainThreadToken` zero-sized type that proves you're on the main thread.**

```rust
#[derive(Clone, Copy)]
pub struct MainThreadToken(PhantomData<*mut ()>);
//                                       ^^^^^^^ makes the token !Send + !Sync

impl MainThreadToken {
    /// # Safety: must be called from the designated main thread.
    pub unsafe fn new() -> Self {
        assert_eq!(*MAIN_THREAD_ID, std::thread::current().id());
        Self(PhantomData)
    }
}
```

Methods that require main-thread access take `_token: MainThreadToken` as an argument. The token is unconstructible elsewhere and uncopyable across threads, so the compiler enforces the rule at every call site.

**2. A `SendWrapper<T>` that promises `Send` without promising `Sync`.**

```rust
pub struct SendWrapper<T>(ManuallyDrop<T>);
unsafe impl<T> Send for SendWrapper<T> {}
impl<T: Sync> Deref for SendWrapper<T> { /* ... */ }  // &T only if T: Sync
```

This lets you ship a non-`Send` C++ object across threads as cargo (you can hold it, move it, drop it on the right thread later) without exposing any operation that would actually be unsafe on the wrong thread.

**3. `SYNC` / `UNSYNC` marker macros on the C++ side.**

```cpp
#define SYNC      // no-op; reviewer-facing tag
#define UNSYNC    // no-op; reviewer-facing tag

int get_immutable_data()         SYNC   const;
int get_mutable_data_unsync()    UNSYNC const;  // _unsync suffix is the contract
```

The macros do nothing at compile time. They exist for code review and for a 1:1 mapping into the Rust side: `SYNC const` methods become safe `&self` methods, `UNSYNC const` methods become `unsafe fn` with a `// SAFETY:` comment, and a safe wrapper takes a `MainThreadToken` to call the unsafe version.

The whole scheme is described in [Antithesis's writeup](https://antithesis.com/blog/2026/rust_cpp/) and is worth reading even if you steal nothing from it but the vocabulary.

A few rules of thumb that fall out of all this:

- **`cxx` does not implement `Send` or `Sync` for opaque C++ types by default.** That is the correct default. Overriding it requires `unsafe impl Send for MyCppType {}`, which is exactly the line that caused the war story at the top of this post. Don't write it without a written safety argument.
- **"const" in C++ is not "`&self`-safe" in Rust.** A `const` C++ method can mutate anything reachable through a non-owned pointer. Treat C++ `const` as evidence, not proof.
- **Drop order matters.** If your C++ type must be destroyed on a specific thread (Qt's `QObject`, COM objects, anything with thread-affine internals), your Rust `Drop` impl must arrange for that — typically by sending the value to a drop queue rather than freeing in place.

### Rule: Encode the C++ side's threading contract in the Rust type system, not in code comments

If a method is unsafe to call off the main thread, make the Rust signature `unsafe` (or require a token). If a value is unsafe to drop off a specific thread, make the `Drop` impl forward to a queue. If a type is `Sync` only because the C++ side has internal locks, write that down in the `unsafe impl Sync` block. The discipline pays for itself the first time a refactor would have introduced a data race and the compiler refuses to build instead.

## Unwinding Across The Boundary Is Undefined Behavior (Until You Opt In)

Until [RFC 2945](https://github.com/rust-lang/rfcs/blob/master/text/2945-c-unwind-abi.md) stabilized the `"C-unwind"` ABI, *any* panic or C++ exception crossing an `extern "C"` boundary was undefined behavior. A lot of production Rust still relies on the older `extern "C"` and silently assumes nothing throws. That assumption breaks the first time a downstream C++ library starts using exceptions, or someone introduces an `unwrap()` deep in a callback.

The 2026 playbook:

```rust
// Old: UB if a panic escapes, UB if a C++ exception arrives.
extern "C" {
    fn cpp_callback(f: extern "C" fn());
}

// New: well-defined unwinding both directions, if both sides cooperate.
extern "C-unwind" {
    fn cpp_callback(f: extern "C-unwind" fn());
}
```

And on the Rust side of any callback exposed to C++:

```rust
#[no_mangle]
pub extern "C-unwind" fn rust_callback(state: *mut State) -> i32 {
    let result = std::panic::catch_unwind(|| {
        // ... real work ...
        do_thing(unsafe { &mut *state })
    });
    match result {
        Ok(code) => code,
        Err(_) => -1, // or whatever your error convention is
    }
}
```

A few things that surprise people:

- **`"C-unwind"` does not make panics safe.** It makes them *defined*. If you don't `catch_unwind`, a panic will still unwind the C++ stack, which can run C++ destructors that weren't expecting it, and that can absolutely still corrupt invariants.
- **`-C panic=abort` short-circuits all of this.** If you compile with `panic = "abort"` (which a lot of embedded and FFI-heavy projects do, and Henri Sivonen [recommended for `encoding_rs`](https://hsivonen.fi/modern-cpp-in-rust/) back in 2018), panics never unwind. That's the simplest safe answer for many production crates.
- **C++ exceptions are not free even when nothing throws.** The presence of an exception specification changes codegen on both sides. If you can constrain your C++ surface to `noexcept`, do.

### Rule: Decide your unwinding policy at the crate level, in writing

Write a one-paragraph note in the crate README. Either "this crate aborts on panic, configure your linker accordingly," or "this crate uses `C-unwind` and every exposed function wraps its body in `catch_unwind`." Make it part of code review that every new `extern` function follows it.

## Don't Cross The Boundary More Often Than You Have To

This is the most important *performance* lesson and also the most important *design* lesson.

Each FFI call carries:

- A real CPU cost (function-call overhead, register save/restore, sometimes a TLS access for panic state).
- A reasoning cost (you must check unsafety preconditions at every site).
- A lifetime cost (Rust's borrow checker can't see across the boundary, so you're back to manual discipline).

The CPU cost is smaller than people think. The godot-rust team [measured their `extern "C"` calls](https://godot-rust.github.io/dev/ffi-optimizations-benchmarking/) at 4–5 nanoseconds round-trip after a one-time function-pointer cache lookup — in the same ballpark as a virtual call through `dyn Trait`. Their takeaway, which I think is correct: *"FFI is fast. We should embrace FFI calls where they make sense, not try to avoid them."* The reason to keep the boundary coarse isn't that crossings are individually expensive; it's that each crossing is a place where the *reasoning* and *lifetime* costs accumulate. A 100ns hot loop with 20 FFI calls in it is fine. A codebase with 2,000 FFI call sites is unauditable.

A rough budget table for sanity-checking your design:

| Operation | Order of magnitude | Notes |
|---|---|---|
| Plain `extern "C"` call, scalar args | ~2–5 ns | indistinguishable from a `dyn Trait` call |
| `cxx` call with `&str` / `&CxxString` | ~5–10 ns | one length+pointer marshal |
| Call wrapped in `catch_unwind` | +5–10 ns | TLS access for panic state |
| `UniquePtr<T>` round-trip (alloc + free) | ~50–200 ns | dominated by the allocator |
| Crossing with a `Vec<u8>` copy | bytes×memcpy | linear in payload size |

These are wall-clock numbers from published benchmarks on commodity x86, not guarantees — measure your own. The point is the *shape*: marshalling is cheap, copies are cheap until they aren't, and allocator round-trips dominate everything once you're doing them per-call.

The teams that ship Rust/C++ interop successfully all converge on the same shape: **a coarse-grained boundary**. They define a small number of operations that take large, owned chunks of work, instead of a large number of operations that shuffle small values back and forth.

Manish's Firefox post puts numbers on this:

> Lots and lots of back-and-forth FFI, thread-safety concerns, Rust code regularly dealing with nontrivial C++ abstractions, a need for nontrivial abstractions to be passed over FFI. All of this conspires to make for some really complicated FFI code.

The cleanest production architectures look more like a service boundary than a function call. Brave's ad-blocker, Mozilla's `encoding_rs`, Microsoft's DWriteCore Rust components, Shopify's [Ruby ↔ Rust shim](https://shopify.engineering/shopify-rust-systems-programming) — all of these expose a handful of "do this whole job for me" entry points, not a leaky abstraction of internal types.[^prod-arch]

### Rule: Design the boundary in terms of *work*, not *types*

A good interop API has verbs at the boundary (`compile_shader`, `parse_html`, `process_batch`) and nouns inside (the types stay local to the language that owns them). If your boundary signature mentions a vocabulary type from the other language, ask whether you really need it there or whether it could be encapsulated.

## Use The Sanitizers. All Of Them.

If you take one thing from this post: **always run your interop test suite under AddressSanitizer and UndefinedBehaviorSanitizer.** Tyler Weaver's [2025 update](https://tylerjw.dev/posts/20251003-rust-cpp-interop-2025-update/) makes this point well, and the audit experience from `uutils` and the Pixel baseband Rust work both confirm it: ASan and UBSan catch the class of bugs your code reviewer won't.[^pixel-baseband]

What this looks like in practice:

```bash
# Build with sanitizers on both sides
RUSTFLAGS="-Z sanitizer=address" \
CFLAGS="-fsanitize=address -fsanitize=undefined" \
CXXFLAGS="-fsanitize=address -fsanitize=undefined" \
  cargo +nightly test --target x86_64-unknown-linux-gnu

# And under Miri for the pure-Rust parts
cargo +nightly miri test
```

Miri won't see into your C++, but it will catch undefined behavior in the Rust glue, which is where most real interop bugs live. For a fuller story, see [`cargo-careful`](https://github.com/RalfJung/cargo-careful), [`cargo-fuzz`](https://github.com/rust-fuzz/cargo-fuzz), and the [ABI Café](https://github.com/Gankra/abi-cafe) project, which tests whether two compilers agree on the layout of a given type. The last one has caught real rustc/clang disagreements.[^abi-cafe]

### Rule: Sanitizers are a hard gate, not a "nice to have"

If you can't run your interop tests under ASan and UBSan in CI, you don't have a test suite, you have a smoke test. This is doubly true for code that handles untrusted input.

## Debugging Across The Boundary

When something does go wrong at the boundary — and it will — you'll spend most of your time fighting your tools before you get anywhere near the bug. A few things worth setting up *before* you need them:

**Keep symbols even when you strip the binary.** This is the single most useful thing you can do. The GreptimeDB team's [Android writeup](https://greptime.com/blogs/2025-04-14-rust-in-android-edge-based-practice) describes the production pattern: build *two* artifacts from each release, one stripped (the one you ship), one with full symbols and debug info (the one you keep). When the stripped binary panics in the field, you correlate the base address of each loaded object back to the symbolized binary off-line and reconstruct a real backtrace. It's the same workflow Android, iOS, and game consoles have used for years; it just isn't part of the standard Rust release story by default.

```toml
# Cargo.toml: keep debug info in release, strip at install time.
[profile.release]
debug = true       # full DWARF in the build artifact
strip = false      # do not strip at the linker step
lto = true
codegen-units = 1
```

Then strip explicitly when packaging, and archive the unstripped `.so` / `.dylib` / `.pdb` alongside the release.

**Install a panic hook that captures a backtrace and base addresses.** The Rust `backtrace` crate plus the `phdrs` crate (on Linux/Android) will give you everything you need to recover a usable trace from a stripped binary:

```rust
pub fn set_panic_hook() {
    std::panic::set_hook(Box::new(|info| {
        let bt = backtrace::Backtrace::new();
        log::error!("panic: {info:?}\nbacktrace:\n{bt:#?}");
        for o in phdrs::objects() {
            log::error!("object {:?} base {:#x?}", o.name(), o.addr());
        }
    }));
}
```

Note that `std::backtrace` had [a long-standing bug on Android](https://greptime.com/blogs/2025-04-14-rust-in-android-edge-based-practice) where it returned empty traces until Rust 1.82; the `backtrace` crate works around it on older toolchains.

**Demangle on read, not on write.** Rust symbols look like `_ZN10panic_demo1b17h9ebbf8c80464f859E` raw and like `panic_demo::b::h9ebbf...` after demangling. Install [`rustfilt`](https://github.com/luser/rustfilt) and pipe `addr2line`, `objdump`, or `c++filt` output through it; trying to read raw mangled names while debugging is a waste of an hour.

**Set up your debugger to walk both stacks.** Modern `lldb` and `gdb` can step from C++ into Rust and back without complaint, but they need symbols for both sides loaded *and* sourced. A few tips:

- `rust-lldb` and `rust-gdb` are thin wrappers that load Rust's pretty-printers — use them, not raw `lldb`/`gdb`, when your Rust code is on the stack.
- Compile both sides with `-g` (`debug = true` in Cargo, `-g` in your C++ flags). Mixed-language traces with one side stripped are useless.
- Set a breakpoint on `rust_panic` and on `__cxa_throw` to catch the moment either side starts unwinding. That single trick has saved me more time than any other debugger setup.
- On Linux, `RUST_BACKTRACE=full cargo test --no-fail-fast 2>&1 | rustfilt` is the fastest way to see what's actually happening when an FFI test segfaults.

**Use `cargo-show-asm` or `cargo-asm` when the bug looks like a calling-convention mismatch.** If your Rust side and C++ side disagree about whether the return value goes in a register or in a hidden out-parameter, no amount of source-level debugging will tell you. Reading the actual generated assembly for one offending function for ten minutes is faster than guessing for two days.

### Rule: Decide your symbol strategy before your first release, not after your first crash report

If production traffic ever returns `0x7fff8c2a1480 - <unknown>` in your error log, you have already lost the next hour. Build the two-binary split, archive the symbols, and write the symbolize-from-base-address script *before* you need it.


## Tooling and Build Systems

The build story used to be a horror show. It's better now, but you still need to make a choice and commit to it.

- **[Corrosion](https://github.com/corrosion-rs/corrosion)** is the practical answer if your build is already CMake-based. It teaches CMake how to invoke Cargo, and CMake handles the linking. Slint, ROS, KDE projects, and most of the `tylerjw.dev` interop examples use it.
- **`cxx-build`** plus a plain `build.rs` is the answer if your build is already Cargo-based and the C++ is in your own repo.
- **[Meson](https://mesonbuild.com/Rust.html)** has first-class Rust support and is a reasonable choice if you're starting fresh and want something less ceremonious than CMake. GNOME components like `librsvg` use this path.[^librsvg]
- **Bazel** plus `rules_rust` plus Crubit is what Google uses internally. It is fantastic if you're already in that ecosystem and miserable if you're not.

A few practical tips that come up over and over.

**Pin your toolchains.** Layout-affecting compiler bugs are rare but real. If your release builds are reproducible, layout bugs become reproducible too, and that's what makes them fixable.

**Track your bindgen and cxx versions carefully.** The [Rust 2024 edition upgrade post on `codeandbitters.com`](https://codeandbitters.com/rust-2024-upgrade/) describes a real migration where `bindgen` 0.71 and `cxx` 1.0.130 had to be upgraded together to get clean unsafe blocks in the right places.

**Set `CARGO_TARGET_DIR` outside your CMake build tree.** Otherwise CMake will helpfully delete your `target/` directory on a clean build, and you'll spend an evening figuring out why your incremental builds take 4 minutes instead of 40 seconds.

**Use `extern_visibility` if you're on nightly.** [RFC 3834](https://github.com/rust-lang/rfcs/blob/master/text/3834-export-visibility.md) is specifically there to make Rust binaries smaller and link cleaner in mixed-language settings. It's not stable yet, but if you're hitting binary-size or symbol-clash problems, it's worth knowing about.

## Antipatterns I See In Production

Here's a grab-bag of mistakes I've actually found in code reviews and audits over the last year. None of them are exotic; most got past at least one reviewer.

**1. Returning `Result<T, E>` from an `extern "C"` function.** The layout of `Result` is not stable. Always lower to `(success_code, out_value)` at the boundary. (See [`#[repr(Rust)]` Is Not An ABI](#repr-rust-is-not-an-abi) above.)

**2. Hanging onto a `&str` derived from a C string.** `CStr::to_str` borrows from the C buffer. If the C side frees that buffer (or even calls a function that might), your `&str` dangles. Either copy to a `String` immediately, or scope the borrow tightly. Greyblake's [old but accurate post](https://www.greyblake.com/blog/2017/08/10/exposing-rust-library-to-c/) walks through the full pattern.

**3. `Box::from_raw` on a pointer you didn't `Box::into_raw` yourself.** This is the FFI equivalent of `free(p)` where `p` came from `malloc` in a different allocator. Always document who owns the allocation, in code:

```rust
/// SAFETY: `ptr` must have been returned by `make_thing` and not yet freed.
#[no_mangle]
pub unsafe extern "C" fn free_thing(ptr: *mut Thing) {
    if !ptr.is_null() {
        drop(Box::from_raw(ptr));
    }
}
```

**4. Treating `*mut T` and `&mut T` as interchangeable.** They aren't. A `&mut T` is a *unique* reference and the optimizer will assume nothing else aliases it. If C++ might still hold a pointer to the same value, you must use raw pointers all the way.

**5. Calling Rust from a C++ signal handler.** Most of Rust's standard library is not async-signal-safe. This includes `println!` and most allocators. If you absolutely must, restrict yourself to `#![no_std]` code that touches nothing but atomics.

**6. Assuming `bindgen` output is safe because it compiles.** Manish puts it bluntly:

> `bindgen` is great. Everything it emits is `unsafe`. That's a feature, not a bug. The wrapper module that turns it into a safe API is the *actual* interop layer, and it's the part you have to write yourself.

**7. Sharing a Rust allocator-backed value with C++.** A `Vec<u8>` returned by reference does not mean the C++ side can grow it, shrink it, or free it. If C++ needs ownership, copy into a C++ buffer at the boundary, or use a type designed for cross-allocator transfer.

**8. Ignoring `cargo build --release` differences.** Some interop bugs are debug-only (uninitialized memory that happens to read as zero in debug), some are release-only (LLVM-optimized aliasing assumptions). Run sanitizers in both profiles.

## A Realistic Mental Model

After working through this material with several teams, the model I find most useful is to treat the FFI boundary the way you'd treat a network boundary.

- Things on the other side may disappear or behave differently than documented.
- Data crossing the boundary has a *wire format*, separate from either side's internal types.
- You serialize and deserialize at the boundary. The serializer is your safe Rust wrapper.
- You don't trust the other side's invariants, you check them.

If you've ever built a service that talks gRPC or JSON to a partner, you already know how to structure this. The fact that the other "service" happens to be in the same process and the "wire" happens to be a function call doesn't change the discipline.

## What Rust *Does* Buy You Here

Reading this list, you might wonder whether interop is worth the trouble at all. It is.

Even with all of these sharp edges, the parts of your codebase you actually write in Rust still get:

- Memory safety inside the Rust code (which is, statistically, the majority of any large rewrite).
- Sound thread-safety inside the Rust code, including across `Send` and `Sync`.
- No null-pointer dereferences inside the Rust code.
- A type system that can express *most* of the boundary's invariants, even when it can't enforce them across it.
- A test and tooling story (Miri, `cargo-fuzz`, sanitizers, Clippy) that is honestly better than the C++ side, even for shared code.

Google's [Android security team reported](https://security.googleblog.com/2024/09/eliminating-memory-safety-vulnerabilities-Android.html) that the proportion of memory-safety vulnerabilities in Android dropped from 76% in 2019 to 24% in 2024, driven primarily by new code being written in Rust rather than rewriting old code.[^android-stats] The interop boundary is where the *remaining* bugs live, but the absolute count is way down.

The point of being careful at the boundary isn't that interop is dangerous in some special way Rust can't help with. It's that the boundary is *exactly* the place where Rust's guarantees stop, and you have to do the work the compiler usually does for you. Treat it that way, and the math still works out enormously in your favor.

## The FFI Boundary Checklist

If you read nothing else, read this. Every item is a rule the rest of the post argues for in detail; together they're the difference between "we shipped Rust into our C++ product" and "we shipped a CVE."

**Layout & ABI**

- [ ] Every type that crosses the boundary is `#[repr(C)]`, `#[repr(transparent)]`, or a `#[repr(integer)]` enum.
- [ ] No `String`, `Vec<T>` by value, `Result<T, E>`, or `Option<T>` (with data) in any `extern` signature.
- [ ] Pointers crossing the boundary are documented with who allocates, who frees, and which allocator.
- [ ] Empty slices are normalized at the boundary (`null` pointer if `len == 0`).

**Unwinding**

- [ ] Unwinding policy (`panic = "abort"` *or* `extern "C-unwind"` + `catch_unwind`) is written in the crate README.
- [ ] Every `extern` function exposed to C++ either is `C-unwind` with a `catch_unwind` wrapper, or runs under `panic = "abort"`.
- [ ] No mixed policies in the same process.

**Threading**

- [ ] No `unsafe impl Send` or `unsafe impl Sync` for a C++ type without a written safety argument in the source.
- [ ] Methods that are only safe on a specific thread take a token (`MainThreadToken`, `&UiContext`, etc.) or are marked `unsafe fn`.
- [ ] Drop is forwarded to the right thread for any type with thread affinity.

**Async**

- [ ] The Rust async runtime is owned and torn down by Rust, with C++ holding only a handle.
- [ ] No `block_on` inside an FFI callback.
- [ ] Cancellation crosses the boundary as an explicit message, not as a future drop.

**Safety hygiene**

- [ ] Every `unsafe extern "C"` function has a `// SAFETY:` comment that names the invariants the caller must uphold.
- [ ] The wrapper crate exposes a safe API; the `extern` surface is `pub(crate)` or hidden behind `unsafe`.

**CI & release**

- [ ] AddressSanitizer and UndefinedBehaviorSanitizer run on the interop test suite in CI, both in debug and release.
- [ ] Miri runs on the pure-Rust glue.
- [ ] Release artifacts are built with `debug = true`, then explicitly stripped, with the unstripped binary archived for symbolication.
- [ ] `bindgen`, `cxx`, and toolchain versions are pinned and upgraded deliberately.

If any of these is unchecked, you have a known unknown. That's fine — know it.

## Idiomatic Interop Is Boring Interop

When I look at the Rust/C++ codebases I admire most — Firefox's pieces, Slint, CXX-Qt, the Pixel baseband, the embedded RTOS work at [Ferrous Systems](https://ferrous-systems.com/blog/rust-and-threadx/) — the common thread isn't clever tricks. It's *boring discipline*.

A small, coarse boundary. A single chosen tool (`cxx`, or hand-rolled `extern "C"`, but not both in the same crate). Every public function `unsafe` until proven otherwise, with a `// SAFETY:` comment that mentions the actual invariants. Sanitizers in CI. `panic = "abort"` or `C-unwind` everywhere, never a mix. `#[repr(C)]` on every type that crosses. Ownership documented in prose, on the function that allocates *and* the function that frees.

None of it is exciting. All of it is what separates "we shipped Rust into our C++ product" from "we shipped a CVE."

If you're starting out, my honest recommendation: read Tyler Weaver's [five-part series](https://tylerjw.dev/posts/20251003-rust-cpp-interop-2025-update/), copy his Cargo+CMake+Corrosion+`cxx` skeleton, and resist the temptation to invent your own bindings layer until you've hit a wall the existing tools genuinely can't solve. Most teams never hit that wall. The ones that do tend to end up at Google, contributing to Crubit.

[^cxx-users]: Mozilla's use of `cxx` in Firefox is documented in Manish Goregaokar's [*Integrating Rust and C++ in Firefox*](https://manishearth.github.io/blog/2021/02/22/integrating-rust-and-c-plus-plus-in-firefox/). Google's use in AOSP is covered in the [*Rust/C++ Interop in the Android Platform*](https://security.googleblog.com/2021/06/rustc-interop-in-android-platform.html) post on the Google Security Blog. Brave's use is discussed by Anton Lazarev on our [Brave episode](/podcast/s03e07-brave/), where CXX is explicitly listed in the show notes.

[^prod-arch]: Sources for each: Brave's adblocker on the [podcast](/podcast/s03e07-brave/); Mozilla's [`encoding_rs`](https://hsivonen.fi/modern-cpp-in-rust/) writeup by Henri Sivonen; Microsoft's DWriteCore, which [*The Register* reported](https://www.theregister.com/2023/04/27/microsoft_windows_rust/) reached about 152,000 lines of Rust in 2023, with the Rust effort starting in 2020; Shopify's [systems-programming post](https://shopify.engineering/shopify-rust-systems-programming).

[^pixel-baseband]: Google's [*Bringing Rust to the Pixel Baseband*](https://security.googleblog.com/2026/04/bringing-rust-to-pixel-baseband.html) post describes the sanitizer and `no_std` work needed to land Rust in modem firmware on Pixel 10, including allocator and panic-handler integration with the existing C/C++ codebase.

[^abi-cafe]: ABI Café is described in Aria Desires' [*Pair Your Compilers At The ABI Café*](https://faultlore.com/blah/abi-puns/), which walks through several concrete cases where rustc and clang disagreed on the ABI of types that *look* identical, including subtle differences for option-of-pointer and small structs.

[^librsvg]: librsvg's port to Rust began with the [2.41.0 release in 2017](https://mail.gnome.org/archives/desktop-devel-list/2017-January/msg00001.html), which announced *"the big news is that parts of librsvg are now implemented in the Rust programming language."* It is one of the longest-running Rust-in-C library projects and a useful case study for incremental adoption.

[^android-stats]: The 76% → 24% figure is for the share of *Android's annual vulnerability budget* that is memory-safety-related, not an absolute count. Google's [*Eliminating Memory Safety Vulnerabilities at the Source*](https://security.googleblog.com/2024/09/eliminating-memory-safety-vulnerabilities-Android.html) post argues this shift is driven primarily by *new* code being written in Rust rather than C/C++, while pre-existing C/C++ ages out of the active codebase. The pattern is consistent with academic research on vulnerability density vs. code age.

{% info(title="Need Help With Rust and C++ Interop?", icon="crab") %}

I work with teams that are introducing Rust into existing C++ codebases, or building new Rust components that need to live next to one. From boundary design and tooling choices to security-focused audits of the FFI layer itself, [get in touch](/#contact) if you'd like a second pair of eyes on yours.

{% end %}
