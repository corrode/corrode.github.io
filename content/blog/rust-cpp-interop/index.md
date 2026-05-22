+++
title="Rust and C++ Interop"
date=2026-05-22
template = "article.html"
[extra]
series = "Idiomatic Rust"
chapter_title = "Living With Two Languages In One Process"
resources = [
    "[A tour of the Rust and C++ interoperability ecosystem](https://blog.tetrane.com/2022/Rust-Cxx-interop.html): eShard's hands-on comparison of `cxx`, `bindgen`, `cbindgen`, and `autocxx`",
    "[Integrating Rust and C++ in Firefox](https://manishearth.github.io/blog/2021/02/22/integrating-rust-and-c-plus-plus-in-firefox/): Manish Goregaokar's long-form post on the bindings Mozilla actually ships",
    "[Rust/C++ Interop in the Android Platform](https://security.googleblog.com/2021/06/rustc-interop-in-android-platform.html): Google's writeup on how AOSP wires Rust and C++ together",
    "[Weighing up Zngur and CXX for Rust/C++ Interop](https://www.kdab.com/weighing-up-zngur-and-cxx-for-rustc-interop/): KDAB's 2026 comparison of the two main approaches",
    "[Rust/C++ Interop Part 5 — Interop in 2025](https://tylerjw.dev/posts/20251003-rust-cpp-interop-2025-update/): Tyler Weaver's complete, working example with CMake, `cxx`, and Corrosion",
    "[Rust in Production: Rust for Linux Live with Alice Ryhl and Greg Kroah-Hartman](/podcast/s06e04-rust4linux/): the episode where Alice makes the case that interop, not rewrites, is how Rust wins",
    "[Rust in Production: Microsoft with Victor Ciura](/podcast/s04e01-microsoft/): our episode on what large-scale Rust/C++ interop looks like inside Microsoft",
    "[Rust has three reference types!](https://ssbr.xyz/blog/rust-has-three-reference-types/): the Crubit team on why `&T`, `&mut T`, and `Pin<&mut T>` aren't enough at the boundary",
]
+++

Every conversation I have with a team that ships Rust into an existing C++ codebase reaches the same point: "the language is great, the interop is the hard part."

That tracks with the [Microsoft episode of *Rust in Production*](/podcast/s04e01-microsoft/) we recorded with Victor Ciura. His one-line summary, paraphrased: *"The biggest challenge for gradual Rust adoption inside Microsoft is interop, and specifically interop with C++."* Google, Mozilla, KDAB, Canonical, Shopify, Brave, the Android team... everyone says some version of the same thing.

The sharpest framing of it I've heard recently came from Alice Ryhl on our most recent [*Rust for Linux* live episode](/podcast/s06e04-rust4linux/), recorded at Rust Week 2026 in Utrecht. Her argument, in essence:

> Interop, not rewrites, is how Rust wins inside Linux.
>
> &mdash; Alice Ryhl, *Rust in Production* S06E04

You can't rewrite 35 million lines of C, and you wouldn't want to. The work that matters is the work that lets a new Rust driver call into existing kernel subsystems without giving up the guarantees that made you reach for Rust in the first place. The same logic applies one level up: you're not going to rewrite Chromium, Office, Photoshop, or your in-house trading engine either. **Interop is the new rewrite.**

I don't think this is going to change soon. C++ is somewhere between [100 and 200 million lines](https://www.lwn.net/Articles/1036912/) of code inside Google alone, and roughly that order of magnitude across the rest of the industry. Most of the interesting Rust work over the next decade will happen *next to* a C++ codebase, not instead of one.

So let's talk about what actually goes wrong at that boundary, what the ecosystem looks like in 2026, and which patterns survive contact with production. Most of this post applies to C interop too, but C++ is where the sharp edges live, so that's where I'll focus.

## Pick The Right Tool, Not The Most Powerful One

The interop space has grown a lot, and it's easy to default to whatever tool a popular blog post happens to use. Here's the rough map as of 2026.

| Tool | Direction | What it's good at | When to avoid |
|---|---|---|---|
| Hand-written `extern "C"` | both | small, stable C-shaped APIs; total control | non-trivial C++ types, large surface |
| [`bindgen`](https://github.com/rust-lang/rust-bindgen) | C/C++ → Rust | parsing C headers, basic C++ | anything with templates, overloads, exceptions |
| [`cbindgen`](https://github.com/mozilla/cbindgen) | Rust → C/C++ | generating C/C++ headers from Rust | round-tripping C++ types |
| [`cxx`](https://github.com/dtolnay/cxx) | bidirectional | the 80% case; a curated subset of C++ that maps cleanly to Rust | exotic C++ (templates, virtual inheritance, exceptions in your hot path) |
| [`autocxx`](https://github.com/google/autocxx) | C++ → Rust (mostly) | larger existing C++ APIs you don't want to wrap by hand | when you need rock-solid stability today |
| [`Crubit`](https://github.com/google/crubit) | bidirectional | deep, mostly-automatic C++ ↔ Rust integration | anywhere outside a Bazel monorepo, today |
| [`Zngur`](https://github.com/HKalbasi/zngur) | bidirectional | owned C++ values, templates, generics across the boundary | early days; smaller community |
| [`CXX-Qt`](https://github.com/KDAB/cxx-qt) | bidirectional | Qt/QML applications with Rust business logic | non-Qt projects |

A few honest opinions on top of that table.

**Reach for `cxx` first.** It is, by a wide margin, the most battle-tested option. Mozilla uses it in Firefox, Google uses it in parts of Android, Brave embeds it deep in their browser ([they talked about it on the podcast](/podcast/s03e07-brave/)), and Slint, CXX-Qt, and a long tail of smaller projects all build on it. The KDAB team summarized the trade-off well in their [Zngur comparison](https://www.kdab.com/weighing-up-zngur-and-cxx-for-rustc-interop/): `cxx` is *opinionated* about which C++ shapes it will let through, and that opinionatedness is exactly why it's safe.

**Be careful with `bindgen` for C++.** `bindgen` is wonderful for C. For C++ it silently skips anything it can't represent (templates, overloads, non-trivial constructors), and what you get back is `unsafe` *everything*. Manish's [Firefox post](https://manishearth.github.io/blog/2021/02/22/integrating-rust-and-c-plus-plus-in-firefox/) is still the best honest writeup of what that costs you in practice.

**Don't deploy `Crubit` into a project that isn't Google-shaped.** Crubit is genuinely impressive (Taylor Cramer's [RustConf 2025 interview](https://www.youtube.com/watch?v=eUTsOWbOHeY) is worth the 45 minutes), and Google funded it alongside a [$1M grant to the Rust Foundation](https://security.googleblog.com/2024/09/eliminating-memory-safety-vulnerabilities-Android.html) specifically to push this story forward. But it lives inside a Bazel monorepo and depends on bleeding-edge compiler features. For now it's a research lead-indicator, not a tool you drop into your repo on Monday.

### Rule: Match the tool to the API shape, not the language

If your C++ interface is already C-shaped (`extern "C"` headers, POD structs, opaque handles), don't reach for a code generator. Hand-written `extern "C"` plus a thin Rust wrapper is shorter, easier to debug, and easier to audit. Save `cxx` for the moment you actually need `std::unique_ptr`, `std::string`, or shared enums.

## `#[repr(Rust)]` Is Not An ABI

This is the single most common antipattern I see in code reviews: a struct gets defined on the Rust side, passed to C++, and "it works on my machine." Then a compiler upgrade reshuffles the fields and you get silent data corruption.

Rust's default `#[repr(Rust)]` layout is [intentionally unspecified](https://github.com/rust-lang/rfcs/blob/master/text/0079-undefined-struct-layout.md). The compiler reorders fields, packs niches into enum discriminants, and may change those decisions between versions. Aria Desires' [*Notes on type layouts and ABIs in Rust*](https://gankra.github.io/blah/rust-layouts-and-abis/) is the canonical deep dive; her [ABI Café](https://faultlore.com/blah/abi-puns/) post is the canonical horror story.

For anything that crosses the boundary, you need one of:

```rust
#[repr(C)]            // C-compatible layout
#[repr(transparent)]  // same layout and ABI as the single inner field
#[repr(u8)] / #[repr(i32)] / ...  // for enums with a fixed discriminant
```

A few field-level rules that fall out of this.

**Don't pass Rust enums with data across FFI.** A `Result<T, E>` or `Option<NonZeroU32>` has a defined layout *in your version of rustc, today*, but it isn't part of the language contract. Either lower it to a `#[repr(C)]` enum with explicit discriminants ([RFC 2195](https://github.com/rust-lang/rfcs/blob/master/text/2195-really-tagged-unions.md) calls these "really tagged unions"), or split it into a status code plus an out-parameter.

**Don't pass `&str` or `String`.** A Rust `String` carries a capacity field and uses Rust's allocator. A C++ `std::string` doesn't, and uses C++'s. They are not the same type at the bytes level. Use `&[u8]` / `*const u8 + len`, or let `cxx` give you a `CxxString` and a `&str` on either side.

**Pointers and slices have edge cases.** David Benjamin's [*Passing nothing is surprisingly difficult*](https://davidben.net/2024/01/15/empty-slices.html) explains why an empty `&[T]` may have a non-null but unaligned `data` pointer, while C and C++ APIs frequently expect either null or a real allocation. If your callee dereferences `data` even when `len == 0`, you have undefined behavior. Wrap with `if slice.is_empty() { ptr::null() } else { slice.as_ptr() }` at the boundary.

**Bitfields don't work.** Rust does not have C-compatible bitfields. `bindgen` emits getter/setter shims, but if you're hand-writing the struct, you need to pack and unpack the bits yourself. The Immunant team has [a good writeup](https://immunant.com/blog/2020/01/bitfields/) of how much pain this still is in 2026.

### Rule: Treat every struct that crosses the boundary as part of your public ABI

That means `#[repr(C)]` (or `transparent`), explicit field types (`u32`, not `usize`, unless you really mean `size_t`), no Rust-shaped enums, no `String`, no `Vec` by value. If you find yourself reaching for the standard library at the FFI line, you're about to ship a bug.

## C++ Has Move Constructors. Rust Has `Pin`. They Don't Match.

This is the conceptual gap that most newcomers underestimate. In C++, *every non-trivial type is effectively pinned* — it may hold pointers into itself, and the type's move constructor exists specifically to fix up those pointers when the object is relocated. In Rust, every value is trivially memmove-able unless it's wrapped in `Pin`.

If you try to translate a `std::string`, `std::list`, or any class with a user-defined move constructor naïvely, you end up with self-references that get torn apart the first time the Rust side moves the value. The classic symptom is "everything looks fine for a while, then segfaults under load."

The Crubit team has [the clearest writeup](https://ssbr.xyz/blog/rust-has-three-reference-types/) of why this is fundamental: in a codebase doing serious C++ interop, `Pin<&mut T>` is as common as `&mut T`, and the ergonomic gap shows. `cxx` solves this pragmatically by only ever letting you touch a C++ value through a `&CxxString`, `Pin<&mut CxxString>`, or `UniquePtr<CxxString>`. That sounds restrictive until you've debugged a use-after-move once.

Miguel Young de la Sota's [*Move Constructors: Is it Possible?*](https://www.youtube.com/watch?v=UrDhMWISR3w) RustConf talk and the [`moveit`](https://crates.io/crates/moveit) crate explore what a fuller answer might look like. It's a glimpse of a future where this is solved at the type-system level; in the meantime, the practical rules are:

1. **Never put a C++ object with a non-trivial move constructor on the Rust stack by value.** Always go through `Box`, `UniquePtr`, or a reference.
2. **Treat anything coming out of a C++ container as pinned.** No `mem::replace`, no `mem::swap`, no destructuring.
3. **If you need to construct a C++ object in place, use a helper that takes a `Pin<&mut MaybeUninit<T>>`.** `cxx` and `moveit` both provide patterns here. Inventing your own is a research project.

### Rule: Don't try to "own" a C++ value in Rust

Own a handle to it (`UniquePtr<T>`, `SharedPtr<T>`, `Box<T>` from C++'s `new`) and let the C++ destructor do the cleanup. The moment you try to teach Rust about C++ move semantics by hand, you're writing your own miniature [`moveit`](https://crates.io/crates/moveit) and you will get it wrong.

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

The teams that ship Rust/C++ interop successfully all converge on the same shape: **a coarse-grained boundary**. They define a small number of operations that take large, owned chunks of work, instead of a large number of operations that shuffle small values back and forth.

Manish's Firefox post puts numbers on this:

> Lots and lots of back-and-forth FFI, thread-safety concerns, Rust code regularly dealing with nontrivial C++ abstractions, a need for nontrivial abstractions to be passed over FFI. All of this conspires to make for some really complicated FFI code.

The cleanest production architectures look more like a service boundary than a function call. Brave's ad-blocker, Mozilla's `encoding_rs`, Microsoft's DWriteCore Rust components, Shopify's [Ruby ↔ Rust shim](https://shopify.engineering/shopify-rust-systems-programming) — all of these expose a handful of "do this whole job for me" entry points, not a leaky abstraction of internal types.

### Rule: Design the boundary in terms of *work*, not *types*

A good interop API has verbs at the boundary (`compile_shader`, `parse_html`, `process_batch`) and nouns inside (the types stay local to the language that owns them). If your boundary signature mentions a vocabulary type from the other language, ask whether you really need it there or whether it could be encapsulated.

## Use The Sanitizers. All Of Them.

If you take one thing from this post: **always run your interop test suite under AddressSanitizer and UndefinedBehaviorSanitizer.** Tyler Weaver's [2025 update](https://tylerjw.dev/posts/20251003-rust-cpp-interop-2025-update/) makes this point well, and the audit experience from `uutils` and the Pixel baseband Rust work both confirm it: ASan and UBSan catch the class of bugs your code reviewer won't.

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

Miri won't see into your C++, but it will catch undefined behavior in the Rust glue, which is where most real interop bugs live. For a fuller story, see [`cargo-careful`](https://github.com/RalfJung/cargo-careful), [`cargo-fuzz`](https://github.com/rust-fuzz/cargo-fuzz), and the [ABI Café](https://github.com/Gankra/abi-cafe) project, which tests whether two compilers agree on the layout of a given type. The last one has caught real rustc/clang disagreements.

### Rule: Sanitizers are a hard gate, not a "nice to have"

If you can't run your interop tests under ASan and UBSan in CI, you don't have a test suite, you have a smoke test. This is doubly true for code that handles untrusted input.

## Tooling and Build Systems

The build story used to be a horror show. It's better now, but you still need to make a choice and commit to it.

- **[Corrosion](https://github.com/corrosion-rs/corrosion)** is the practical answer if your build is already CMake-based. It teaches CMake how to invoke Cargo, and CMake handles the linking. Slint, ROS, KDE projects, and most of the `tylerjw.dev` interop examples use it.
- **`cxx-build`** plus a plain `build.rs` is the answer if your build is already Cargo-based and the C++ is in your own repo.
- **[Meson](https://mesonbuild.com/Rust.html)** has first-class Rust support and is a reasonable choice if you're starting fresh and want something less ceremonious than CMake. GNOME components like `librsvg` use this path.
- **Bazel** plus `rules_rust` plus Crubit is what Google uses internally. It is fantastic if you're already in that ecosystem and miserable if you're not.

A few practical tips that come up over and over.

**Pin your toolchains.** Layout-affecting compiler bugs are rare but real. If your release builds are reproducible, layout bugs become reproducible too, and that's what makes them fixable.

**Track your bindgen and cxx versions carefully.** The [Rust 2024 edition upgrade post on `codeandbitters.com`](https://codeandbitters.com/rust-2024-upgrade/) describes a real migration where `bindgen` 0.71 and `cxx` 1.0.130 had to be upgraded together to get clean unsafe blocks in the right places.

**Set `CARGO_TARGET_DIR` outside your CMake build tree.** Otherwise CMake will helpfully delete your `target/` directory on a clean build, and you'll spend an evening figuring out why your incremental builds take 4 minutes instead of 40 seconds.

**Use `extern_visibility` if you're on nightly.** [RFC 3834](https://github.com/rust-lang/rfcs/blob/master/text/3834-export-visibility.md) is specifically there to make Rust binaries smaller and link cleaner in mixed-language settings. It's not stable yet, but if you're hitting binary-size or symbol-clash problems, it's worth knowing about.

## Antipatterns I See In Production

Here's a grab-bag of mistakes I've actually found in code reviews and audits over the last year. None of them are exotic; most got past at least one reviewer.

**1. Returning `Result<T, E>` from an `extern "C"` function.** The layout of `Result` is not stable. Always lower to `(success_code, out_value)` at the boundary. (See [`#[repr(Rust)]` Is Not An ABI](#repr-rust-is-not-an-abi) above.)

**2. Hanging onto a `&str` derived from a C string.** `CStr::to_str` borrows from the C buffer. If the C side frees that buffer (or even calls a function that might), your `&str` dangles. Either copy to a `String` immediately, or scope the borrow tightly. Greyblake's [old but accurate post](http://greyblake.com/blog/2017/08/10/exposing-rust-library-to-c/) walks through the full pattern.

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

Google's [Android security team reported](https://security.googleblog.com/2024/09/eliminating-memory-safety-vulnerabilities-Android.html) that the proportion of memory-safety vulnerabilities in Android dropped from 76% in 2019 to 24% in 2024, driven primarily by new code being written in Rust rather than rewriting old code. The interop boundary is where the *remaining* bugs live, but the absolute count is way down.

The point of being careful at the boundary isn't that interop is dangerous in some special way Rust can't help with. It's that the boundary is *exactly* the place where Rust's guarantees stop, and you have to do the work the compiler usually does for you. Treat it that way, and the math still works out enormously in your favor.

## Idiomatic Interop Is Boring Interop

When I look at the Rust/C++ codebases I admire most — Firefox's pieces, Slint, CXX-Qt, the Pixel baseband, the embedded RTOS work at [Ferrous Systems](https://ferrous-systems.com/blog/rust-and-threadx/) — the common thread isn't clever tricks. It's *boring discipline*.

A small, coarse boundary. A single chosen tool (`cxx`, or hand-rolled `extern "C"`, but not both in the same crate). Every public function `unsafe` until proven otherwise, with a `// SAFETY:` comment that mentions the actual invariants. Sanitizers in CI. `panic = "abort"` or `C-unwind` everywhere, never a mix. `#[repr(C)]` on every type that crosses. Ownership documented in prose, on the function that allocates *and* the function that frees.

None of it is exciting. All of it is what separates "we shipped Rust into our C++ product" from "we shipped a CVE."

If you're starting out, my honest recommendation: read Tyler Weaver's [five-part series](https://tylerjw.dev/posts/20251003-rust-cpp-interop-2025-update/), copy his Cargo+CMake+Corrosion+`cxx` skeleton, and resist the temptation to invent your own bindings layer until you've hit a wall the existing tools genuinely can't solve. Most teams never hit that wall. The ones that do tend to end up at Google, contributing to Crubit.

{% info(title="Need Help With Rust and C++ Interop?", icon="crab") %}

I work with teams that are introducing Rust into existing C++ codebases, or building new Rust components that need to live next to one. From boundary design and tooling choices to security-focused audits of the FFI layer itself, [get in touch](/#contact) if you'd like a second pair of eyes on yours.

{% end %}
