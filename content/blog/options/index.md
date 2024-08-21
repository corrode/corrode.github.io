+++
title = "Handling None - A Common Rust Papercut"
date = 2024-08-21
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

I noticed that handling the `None` variant of `Option` is a common papercut in Rust.
It has been discussed a million times already, but in this post, I also want to give you a bit of background on why it is the way it is
and teach you a bit about Rust's type system.
Jump to the end if you're in a hurry.

## The Problem

Very commonly, people want to write code like this where they use the `?` operator to propagate errors:

```rust
// Assume that this fetches the user from somewhere
fn get_user() -> Option<String> {
    None
}

fn get_user_name() -> Result<String> {
    let user = get_user()?;
    // Do something with `user`
    Ok(user)
}
```

Almost everyone has received the following dreaded error message:

```rust
error[E0277]: the `?` operator can only be used on `Result`s, not `Option`s, in a function that returns `Result`
  --> src/lib.rs:10:26
   |
9  | fn get_user_name() -> Result<String> {
   | ------------------------------------ this function returns a `Result`
10 |     let user = get_user()?;
   |                          ^ use `.ok_or(...)?` to provide an error compatible with `std::result::Result<String, Box<dyn std::error::Error>>`
   |
   = help: the trait `FromResidual<Option<Infallible>>` is not implemented for `std::result::Result<String, Box<dyn std::error::Error>>`
   = help: the following other types implement trait `FromResidual<R>`:
             <std::result::Result<T, F> as FromResidual<Yeet<E>>>
             <std::result::Result<T, F> as FromResidual<std::result::Result<Infallible, E>>>
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=7001ff6af6c0bcbf44249691d65b086f))

Ouch. This is scary-looking.
There's a lot of visual noise in this error message. The `FromResidual` and `Yeet` are implementation details that are not relevant to the user,
but the relevant details are somewhat obscured. 
We're not making a good first impression here.

**And all we did was use an `Option`!**

My main gripe with this error message is that it doesn't explain **why** the `?` operator doesn't work with `Option`...
just that it doesn't.
Granted, the error message is already quite long and it might not be the best place to teach Rust, but it would be nice to have a link to a more detailed explanation. After all, this is Rust: we take great pride in our error messages.

By the way, running `rustc --explain E0277` only gives you a very generic explanation about types which don't implement traits. 
That's not very actionable.

## What Do People Usually Do?

The most common solution I see is that people are confused for a bit,
try to understand the error message, and eventually just give up, use `unwrap`,
and make a mental note to come back to it later.

```rust
fn get_user_name() -> Result<String, String> {
    let user = get_user().unwrap();
    // Do something with `user`
    Ok(user)
}
```

Even with a trainer around, they are often too embarrassed to ask for help.
They think people are supposed to "get this" and they are the only ones who don't.

This just defers the problem. 
The user of the function will get a panic at runtime. It might be your future self.

Moreover, I advise people to avoid `unwrap` in production code, as this sets a bad example.

During trainings, this is where I pause for a moment and explain the error message.
It's a great point where we dig deeper to understand the root cause of the problem.

Okay, I've kept you waiting long enough. Let's demystify this error message.

## Why doesn't `?` work with `Option`?

The `?` operator takes a `Result` and unwraps it, returning the value inside if it is `Ok`, or returning early if it is `Err`. 

Essentially, `?` is implemented like this:

```rust
let value = match my_result {
    Ok(value) => value,
    Err(error) => return Err(error),
};
```

`Option` on the other hand **does not have an** `Err` variant. 

It is defined like this:

```rust
enum Option<T> {
    Some(T),
    None,
}
```

`None` doesn't have an associated error value. It's just a value that means "no value".
The `?` operator wouldn't know what error it should return:

```rust
let value = match my_option {
    Some(value) => value,
    None => todo!("What to return here? ¯\_(ツ)_/¯"),
};
```

That's actually the entire difference between `Result` and `Option` &ndash; at least from an implementation point-of-view.
If we had an `Err` variant, we would just use `Result` in the first place.
But there are cases where `None` is a completely valid value and we just don't have an error to return.
We can just say "there is no value" and that's it.

## What's The Solution?

There are multiple solutions!

The initial error message, while cryptic, gave us a hint:

```rust
use `.ok_or(...)?` to provide an error compatible with `Result<(), Box<dyn std::error::Error>>`.
```

Apparently we can use the `ok_or` method, which converts the `Option` into a `Result`:

```rust
let user = get_user().ok_or("No user")?;
```

Unfortunately, `ok_or` might not be the most discoverable name for this method.
I find it unintuitive and needed to look it up many times.
That's because `Ok` is commonly associated with the `Result` type, not `Option`.
There's `Option::Some`, so it could also be called `some_or`, but that would be hard to change now.
It was [actually suggested in 2014](https://github.com/rust-lang/rust/pull/17469#issuecomment-56919911), but the name `ok_or` won out,
because `ok_or(MyError)` reads nicely and I can see that. Guess we have to live with the minor inconsistency now.

## Just Use `match`

In the past, I used to recommend people to not be clever and just use a `match` statement.

```rust
let user = match get_user() {
    Some(user) => user,
    None => return Err("No user".into()),
};
```

`match` works in combination with `Option`, because it's just an enum and we can pattern match on it.
As long as we cover all cases, the compiler is happy. In this situation, we only have two cases: `Some` and `None`.
In the `None` case, we return early with an error. In the `Some` case, we continue with the value.
(`match` is an expression and the value of the last expression in the block is returned. In our case it's `user` and it
gets assigned to the `user` variable in the outer scope.)

This is more explicit and easier to understand for beginners.
The one issue I had when teaching this was that it looked a bit more verbose for simple cases like this.

## The Best Solution To Handle None With The Standard Library

Recently, the `let-else` expression was stabilized, so now you can write this: 

```rust
let Some(user) = get_user() else {
    return Err("No user".into());
};

// Do something with user
```

In my opinion, that's the best of both worlds: it's compact and easy to understand.
It's unanimously loved by beginners and experienced Rustaceans alike.

For some explanation: if `get_user()` returns `Some`, the `let` statement will destructure the `Some` variant and assign the value to the `user` variable. If `get_user()` returns `None`, the `else` block will be executed and we return early with an error.

My favorite thing about `let-else` is that it clearly highlights the 'happy path' of your code. Unlike a `match` statement where you need to read both arms to understand the intended flow, `let-else` makes it immediately clear what the expected case is, with the `else` block handling the exceptional case.

This is a clear winner.
It is way more intuitive for beginners.
Once they understand the pattern, they use it all the time!

## Handling `None` With `anyhow`

If you're writing an application (not a library) and you're using the
[`anyhow`](https://github.com/dtolnay/anyhow) crate already, you can also use their `context`
method to handle `None`:

```rust
use anyhow::{Context, Result};

fn get_user_name() -> Result<String> {
    let user = get_user().context("No user")?
    // Do something with `user`
    Ok(user)
}
```

It's slightly less verbose than `let-else`, but remember that `anyhow` is an external dependency.
If you build an application, that's probably fine, but you might not want to use it in a library as users of
your library can no longer match on the concrete error variant then. [^1]

[^1] For libraries, there's [`thiserror`](https://github.com/dtolnay/thiserror), but it [doesn't provide a `context` method](https://github.com/dtolnay/thiserror/issues/313).

## Conclusion

That's why I believe that `let-else` is the best solution for handling `None` in most cases.

- It's part of the standard library.
- It works for building libraries and applications.
- It's easy to understand for beginners.
- It's reasonably compact.
- It allows for more complex error handling logic in the `else` block if needed.
- Learning the mechanics behind it is helpful in other places.

I hope this helps more people handle `Option` properly in Rust.
If it helps a single person avoid a single `unwrap`, it was worth it.
