+++
title = "Practical Rust API Design"
date = 2026-09-30
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

A good metric for ergonomic system design is how much of a program you have to keep in your head at once to know what's going on. 
It's empowering if you can understand a function by its type signature and get immediate feedback on whether you used it correctly.
Other times, it feels like you're a code archaeologist:
was this value validated before?
Is it safe to retry this call?
Can this panic?
Bad APIs make local reasoning hard.  

*Local reasoning* means being able to understand a piece of code from a limited amount of surrounding context and the contracts of the APIs it uses. 
The main point is that you can rely on those contracts without additional knowledge of the implementation. 

I think that's what makes Rust feel different from other languages: the ability that you can encode invariants in the type system and that you can do so *at zero cost*.
The combination of both properties is rare.

You will notice this "local reasoning principle" throughout Rust's standard library;
through explicit unsafe blocks, borrows marked with `&`, the use of `Result` and `Option`, or the use of enums to represent a closed set of possibilities.
This information is always visible in every function signature.
You don't need to look elsewhere.
A simple way to write better Rust is to check if your function signatures communicate as much information as possible to the caller.
Maybe show the signature to a friend or colleague and ask them to explain what it does.
It's eye-opening.

## Put Relationships in the Signature

Consider this function signature:

```rust
fn first_line(text: &str) -> Option<&str>
```

Before even looking at the implementation, we already know that the function takes a borrowed input and may have no output. (Or, rather, it may return `None`.)
Actually, if you know Rust's lifetime elision rules, you know that the real signature is:

```rust
fn first_line<'text>(text: &'text str) -> Option<&'text str>
```

The input is tied to the output.
So we know that the caller can't keep using the returned string after the borrow of `text` has ended.
And by extenssion, the function can't returna  temporary string either.
That's super helpful to know.
It means that the function is not making any long-lived allocations.

That's a lot of useful information for just one function header! 

All of that is great, but equally important, there are a few "implicit" assumptions that the signature does *not* guarantee.
Take the function name: it suggests that the function returns "the first line of something." 
However, the type system does not prove that.
It could return the last line for all we know, and the signature would be identical. 

The function header also won't tell us whether anything is logged, how it performs, or whether it panics. 

Rust is often described as an explicit language.
Yet it also uses type inference, lifetime elision, automatic borrowing of method receivers, and implicit coercions.
That's because writing everything out would make many programs harder to read.
What you should make explicit depends on your context.

A good rule of thumb when designing an API, is to look for relationships that callers would otherwise have to remember.
Does your function really take a `&str`, or should it rather be a newtype like `Text`, with additional guarantees? 
Does an `Option<&str>` suffice, or should it rather return a `Result<&str, TextError>`?

## Keep Consequential Choices Visible

Consider these two calls, where `text` is a `String`:

```rust
inspect(&text);
consume(text);
```

The first call borrows `text` while the second one moves it.

Now let's look at the context of the borrowed call:

```rust
fn inspect(text: &str) {
    println!("{text}");
}

let text = String::from("hello");
inspect(&text);
```

The compiler applies a deref coercion automatically.
I think that's a good compromise: the ownership decision is still visible, but the compiler handles the bookkeeping.

Sometimes, people argue that we could go one step further.
We could automatically borrow an owned argument in an ordinary function call.
You could then write `inspect(text)` instead of `inspect(&text)`, which seems convenient.
But, as always, there's a cost to convenience.
Namely, saving the `&` would remove information readers currently get from the expression itself.[^deref]
The lesson here is that convenience does not mean better ergonomics.

This gives us a way to judge our own conveniences, too.
Implementing `Deref` for a wrapper makes its target's methods available implicitly.
That's convenient. 
But it's a slippery slope.
It can lead to leaky abstractions, where a wrapper type is treated as if it were the underlying type, but it is not quite the same. 

Suppose a `UserId` stores a `String`.
You might consider to `impl Deref<Target = str>` for it, so that callers can use it as if it were a `&str`.
That sounds convenient, but now you expose the whole string interface through `Deref`.
You implicitly allow callers to treat the identifier as text, sidestepping all your type invariants.
Instead, an explicit `as_str()` leaves a visible point where they choose to do that.
It also lets your `UserId` newtype have an API of its own.
That's great, because interaction with user ids becomes more deliberate. 

Use `Deref` only when the wrapper transparently behaves like its target and dereferencing is cheap and unsurprising.
[The standard library agrees.](https://doc.rust-lang.org/std/ops/trait.Deref.html#when-to-implement-deref-or-derefmut)

## Give Names a Purpose

Take a look at this function signature:

```rust
fn visit<F: FnMut(&str)>(callback: F)
```

Here, we introduce a name, `F`, give it a bound of `FnMut(&str)`, and then use it exactly once for `callback`.
I think that signature would be clearer if we put the requirement right next to where it's used:

```rust
fn visit(callback: impl FnMut(&str))
```

Now you can read signature from left to right. 
This saves you from jumping back and forth just to figure out what `F` means.
One less thing to keep in your head while reading.[^impl-trait]

Now, I'm not saying that version two is *always* better.
For example, it can be helpful to keep generics separate from the rest of the signature when the generic type is used in multiple places:

```rust
fn choose<T>(first: T, second: T, take_first: bool) -> T {
    if take_first { first } else { second }
}
```

Here, `T` tells us that both arguments as well as the return value have the same type.
The same thinking applies to return types:

```rust
fn nonempty(lines: &[String]) -> impl Iterator<Item = &str> {
    lines.iter().map(String::as_str).filter(|s| !s.is_empty())
}
```

`impl Iterator<Item = &str>` tells the caller what they can do with the result, namely iterate over borrowed strings.
Besides, if you tried writing out the concrete return type of that function, it would be unnecessarily long and complicated. 

Ask yourself: does naming this type help the caller understand something?

## Ownership Beyond Memory

We usually learn about ownership in the context of memory.

But the same questions apply to file descriptors.
On Unix, a raw file descriptor is just an integer.
That integer doesn't tell you whether the descriptor is still open, or who's responsible for closing it.
Worse, once it's closed, the operating system can reuse the number for something else.

Consider these two signatures, using types from `std::os::fd`:

```rust
fn inspect(fd: RawFd) -> std::io::Result<()>
```

```rust
fn inspect(fd: BorrowedFd<'_>) -> std::io::Result<()>
```

Just by looking at the signature, we know that that the descriptor stays alive.[^io-safety]
You can get that borrow from a `File`, for example:

```rust
use std::fs::File;
use std::os::fd::AsFd;

let file = File::open("notes.txt")?;
inspect(file.as_fd())?;
```

Now the compiler can help!
You can't drop `file` and then keep using the descriptor borrowed from it in safe Rust.
You no longer need to search through the code to check whether someone closed it earlier.
Those "Time-Of-Check to Time-Of-Use" bugs are a [common pitfall of safe Rust](/blog/pitfalls-of-safe-rust).

But what if our function should really take ownership of the file descriptor? 
Use `OwnedFd` instead.
When dropped, the descriptor is closed automatically, so the caller doesn't have to remember to do it.

In a sense, memory and file descriptors share a similar set of types with different guarantees:

| Memory      | File descriptors | Use-Case                                                                                           |
| ----------- | ---------------- | -------------------------------------------------------------------------------------------------- |
| `Box<T>`    | `OwnedFd`        | "I want to own this resource and close it when I'm done."                                          |
| `&T`        | `BorrowedFd<'a>` | "I want to borrow this resource for a limited time."                                               |
| Raw pointer | `RawFd`          | "I want to use this resource, but I don't know who owns it or how long it will live."              |

Look guards are another example.

```rust
{
    let _guard = lock.lock();
    // do cool things with lock
} 
// We no longer have access to the lock here, because `_guard` was dropped. 
```

If you can access the data, you hold the lock.
You don't have to "trace the program back" to an earlier `lock()` call and check every path for an unlock.
In C, that's very much the case, and easy to get wrong.

Of course, these types only guarantee what they encode.
A `BorrowedFd` keeps track of one borrow, but it doesn't guarantee exclusivity over the underlying resource. 
Another process might still be writing to the same file.

But in general, you can stop relying on callers to remember the provenance of a resource. 
That's a much stronger guarantee than if your API documentation says "keep this open until you're done."

Raw handles are still necessary at a low-level boundary, but you don't have to pass them through your entire application.
Provide a safe Rust wrapper instead.

## Explain Who Is Responsible

Sometimes things are truly outside of Rust's control. 
We use unsafe APIs to make make that division of responsibility explicit. 

An `unsafe fn` says: "Before you call me, you MUST establish these conditions. This is your responsibility."
An `unsafe` block means you're responsible for satisfying the conditions of the unsafe operations inside the block.[^unsafe]
Those are two different responsibilities, even though they share the same keyword.

```rust
/// # Safety
/// `index` must be less than `values.len()`.
unsafe fn element_unchecked(values: &[u8], index: usize) -> u8 {
    // SAFETY: The caller guarantees that `index` is in bounds.
    unsafe { *values.get_unchecked(index) }
}
```

The caller promises that the index is within bounds.
The implementation relies on that promise when calling `get_unchecked`.
It's a good practice to add a safety comment to make users aware.

This is just an example and you should not do that specific thing in practice.
You'd use `get(index)` here to handle the `None` case, but the example shows why the distinction between an unsafe block and an unsafe function matters. 
Suppose someone adds another unsafe operation to this function later.
Does knowing that `index` is in bounds make that operation safe, too?
Maybe.
You have to check.

Quick tip: in Rust 2024, unsafe operations inside unsafe functions warn by default unless you put them in an explicit unsafe block.
You can enforce that with `#![deny(unsafe_op_in_unsafe_fn)]`.

Another tip: When you write a safety comment, explain *why* the operation is safe.
"This is safe" doesn't help the next person, but
"The caller guarantees that the index is in bounds" gives them something they can check.

## Don't Make Callers Do Your Work

You've probably heard the advice to panic for programmer errors and return `Result` for recoverable failures.
That's reasonable, but who decides what counts as a programmer error?

You do, when you design the API.[^errors]

Consider the difference between indexing and `get`:

```rust
let item = items[index];
```

```rust
let item = items.get(index);
```

If you use indexing, you need to know that the index is valid to avoid a panic.
With `get`, you can try the lookup and handle `None` if it fails.
Remember that both are safe Rust: an invalid index doesn't cause undefined behavior in either case.

Now suppose the index comes from user input.
Is an out-of-bounds index really a bug in your program?
Or is it something you should expect and handle?

One escape hatch is to make every caller check the index before calling your function.
A strict precondition might make your work simpler, but think about your users. 
Before you document another thing the caller "must" do, ask whether your API could do it instead.
For example, you could return an `Option` and let callers decide what to do next.

That doesn't mean you should avoid indexing altogether.
If an index is indeed valid by construction, indexing can express that assumption directly.
A panic then points to a bug in your API.

And sometimes you can sidestep those issues entirely.
For example, if you need to visit each element of a collection, use an iterator.
This way, you don't have to worry about indices at all.

## Decide What You Want to Promise

Another mental model for building great APIs is to think about what you want to guarantee to your users.
Remember [Hyrum's Law](https://www.hyrumslaw.com/):

> With a sufficient number of users of an API,
> it does not matter what you promise in the contract:
> all observable behaviors of your system
> will be depended on by somebody.

With that in mind, think about what happens when you try to change your API. 

For example, users can match on every variant of your public enum.
They can't forget a case, because the compiler will warn them about it.
That's local reasoning at work, which is great.
But on the flipside, it also means that you can't add a variant without breaking their code.
You've broken a guarantee they depended on.

To prevent that, mark your enum as `#[non_exhaustive]` so you can add variants later:

```rust
#[non_exhaustive]
pub enum ServiceError {
    Unavailable,
    Rejected,
}
```

In that case, users have to include a fallback when matching the enum.[^non-exhaustive]
You've pushed the responsibility to the call-site, which is likely the better place to decide what to do with an unexpected variant.
Exhaustive matching still works inside your own crate.

Should you add `#[non_exhaustive]` to every public enum just in case?
If the set of possibilities really is closed, exhaustive matching gives users a useful guarantee.
Don't take it away without a reason.
Examples of closed sets include days of the week, months of the year, or the suits of a deck of cards: 

```rust
pub enum Suit {
    Hearts,
    Diamonds,
    Clubs,
    Spades,
}
```

If you make this enum non-exhaustive, users can't use your crate to implement a card game without having to handle an impossible case.

The awkward middle ground is a set that looks closed but isn't.
HTTP status codes are a good example: mapping all the standard codes doesn't mean you're safe from a vendor inventing their own codes. 
This caused a real problem in `http-types`: [a user reported](https://github.com/http-rs/http-types/issues/507) that constructing a response with Cloudflare's custom status codes panicked because the library's `StatusCode` enum couldn't represent them.

`#[non_exhaustive]` doesn't solve that problem by itself.
It lets you add additional variants in the future, but it doesn't allow users to represent unknown codes today.
How about we add `Unregistered(u16)`?

```rust
#[non_exhaustive]
pub enum Status {
    Ok,
    NotFound,
    // Other known status codes we can't name yet...
    Unregistered(u16),
}
```

Now users can handle codes which don't have a name yet: 

```rust
fn is_early_hints(status: Status) -> bool {
    match status {
        Status::Unregistered(103) => true,
        _ => false,
    }
}
```

But that introduces another compatibility trap.
Suppose a later release adds an `EarlyHints` variant and starts returning it for code `103`.
The function now returns `false` for the same HTTP status code.
The code still compiles, but its *behavior* has changed.
I recommend reading [“Pattern Matching and Backwards Compatibility”](https://seanmonstar.com/blog/pattern-matching-and-backwards-compatibility/)
by Sean McArthur, the author of the `http` crate, about how even an enum with a catch-all variant can make promises you didn't intend.

The escape hatch for the `http` crate was to make `StatusCode` an opaque struct with associated constants for the known codes like `StatusCode::OK`.
Users can then construct values from numeric codes, even when the library doesn't have a name for them:

```rust
use http::StatusCode;

let status = StatusCode::from_u16(599).unwrap();
assert_eq!(status.as_u16(), 599);
```

They can still match on familiar codes, but they have to include a fallback.
And they can handle an unnamed code by inspecting its numeric value:

```rust
use http::StatusCode;

fn describe(status: StatusCode) -> &'static str {
    match status {
        StatusCode::OK => "success",
        code if code.as_u16() == 103 => "early hints",
        _ => "some other status",
    }
}
```

That's pretty clever, because adding a new constant like `StatusCode::EARLY_HINTS` assigns a name to a value without changing the underlying representation; numeric checks continue to work.

So before making something public, ask yourself: am I willing to uphold this guarantee forever? 
This applies to all public types, not just enums like public fields inside a struct.

Changing things later can break user code.
From their perspective, it was part of the API all along.

## Try It on Your Own APIs

Pick a function in your codebase and look at it from the caller's perspective.
What do you have to know to use it correctly?
Can you get that information from the signature, or do you have to read the implementation first?

Look for instructions in the documentation that the compiler could help enforce.
Instead of writing "keep this resource alive", maybe you can return a borrowed type. 
"Only pass validated text" might become a newtype with some validation in the constructor. 

You don't have to follow every single suggestion in this article, either. 
The goal is to make your API easier to understand and harder to misuse.

[^deref]: [RFC 241: Deref coercions](https://github.com/rust-lang/rfcs/blob/master/text/0241-deref-conversions.md) discusses why automatically borrowing arguments would make local reasoning harder.

[^impl-trait]: [RFC 1951: Expand `impl Trait`](https://rust-lang.github.io/rfcs/1951-expand-impl-trait.html) explains ergonomics in terms of how much you have to keep in your head, and discusses who chooses the concrete type.

[^io-safety]: [RFC 3128: I/O safety](https://rust-lang.github.io/rfcs/3128-io-safety.html) explains the analogy between raw handles and raw pointers, and introduces owned and borrowed handle types.

[^unsafe]: [RFC 2585: Unsafe blocks in unsafe functions](https://rust-lang.github.io/rfcs/2585-unsafe-block-in-unsafe-fn.html) separates defining safety obligations from satisfying them.
    The [Rust 2024 edition guide](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html) covers the lint's current default.

[^errors]: [RFC 236: Error conventions](https://github.com/rust-lang/rfcs/blob/master/text/0236-error-conventions.md) recommends expressing contracts through types where possible, and using `Result` or `Option` when a stricter contract is hard to justify.
    The discussion of task failure predates Rust 1.0; the advice about API contracts is the relevant part here.

[^non-exhaustive]: [RFC 2008: Non-exhaustive enums and structs](https://rust-lang.github.io/rfcs/2008-non-exhaustive.html) discusses exhaustive matching and the freedom to add new variants.
