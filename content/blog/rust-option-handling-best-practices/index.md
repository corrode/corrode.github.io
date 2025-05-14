+++
title = "Don't Unwrap Options: There Are Better Ways"
date = 2024-08-29
date = 2025-05-14
template = "article.html"
[extra]
date = 2024-08-30
series = "Idiomatic Rust"
reviews = [
    { name = "woshilapin", url = "https://mastodon.social/@woshilapin@mamot.fr" },
    { name = "Artur Jakubiec", url = "https://www.linkedin.com/in/artur-jakubiec" },
]
+++

I noticed that handling the `None` variant of `Option` without falling back on `unwrap()` is a common papercut in Rust.
More specifically, the problem arises when you want to return early from a function that returns a `Result` if you encounter `None`.

It has been discussed a million times already, but, surprisingly, not even the Rust book mentions my favorite approach to handling that, and many forum posts are outdated.

With a bit of practice, robust handling of `None` can become as easy as `unwrap()`, but safer. 

Jump to the end if you're in a hurry and just need a quick recommendation.

## The Problem

Very commonly, people write code like this:

```rust
// Assume that this fetches the user from somewhere
fn get_user() -> Option<String> {
    None
}

fn get_user_name() -> Result<String> {
    let user = get_user()?;
    // Do something with `user`
    // ...
    Ok(user)
}
```

The goal here is to return early if you encounter `None` in an `Option`, so
they use the `?` operator to propagate errors. 

Alas, this code doesn't compile. Instead, you get a dreaded error message: 

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

Ouch. This is scary-looking!

There's a lot of visual noise in this error message. The `FromResidual` and `Yeet` are implementation details which could be confusing to a new user, and the relevant details are somewhat obscured. 

**And all we did was try to use the `?` operator for our `Option`.**

My main gripe with this error message is that it doesn't explain *why* the `?` operator doesn't work with `Option` in that case... just that it doesn't.

## What People End Up Doing

The most common approach I see is this:

- People are confused for a bit.
- They try to understand the error message.
- Eventually, they give up and just add `unwrap()`.
- They make a mental note to come back to it later.
- 'Later' never comes.

Here's what they end up with: 

```rust
fn get_user_name() -> Result<String, String> {
    let user = get_user().unwrap();
    // Do something with `user`
    Ok(user)
}
```

In trainings, I noticed that people are often too embarrassed to ask for help.
They think people are supposed to *"get this"* and they are the only ones who don't.

This just defers the problem. 
The user of the function might hit a `panic` at runtime. That user might be their future self.

`unwrap` is fine in many cases, but it shouldn't be the first intuition for dealing with unexpected situations.
Especially when you're writing a library or a function that is part of a larger codebase, you should strive to handle 
such situations gracefully.
And in production code, it sets a bad example:
one `unwrap` attracts another and the codebase becomes more fragile as you continue down this path. [^2]

[^2]: Sometimes, `unwrap()` can make code more readable by reducing noise, especially when the success case is overwhelmingly likely.
It's okay to use `unwrap()` when you can prove that a failure is impossible or when a panic is actually the desired behavior for failures. Andrew Gallant [wrote an article on this](https://blog.burntsushi.net/unwrap/) where he goes into more detail.

Okay, I've kept you waiting long enough. Let's demystify this error message.

## The Actual Problem

What the compiler is trying to tell us is that **you can't propagate optionals within functions which return `Result`**.

Everything works just fine if you're returning an `Option` instead:

```rust
fn get_user_name() -> Option<String> {
    // Works :)
    let user = get_user()?;
    // Do something with `user`
    // ...
    Some(user)
}
```

So if you can change the outer function to return an `Option` instead, you won't run into the above error message.
There's more info in the Rust documentation [here](https://doc.rust-lang.org/std/option/index.html#the-question-mark-operator-).

But what if the final return type of your function has to be a `Result`
or if you want to convey more information about the missing value to the caller?
After all, communicating the distinction between different `None` values can be helpful to the user of your function.

So, what if you *really* want your code to look like this?

```rust
fn get_user_name() -> Result<String, String> {
    // Doesn't work because we return a `Result`
    let user = get_user()?;
    // Some more, fallible operations, here
    // ...
    // Return a `Result`
    Ok(user)
}
```

Well, that's just a type error: `get_user()` returns an `Option`, but the outer function expects a `Result`. 

Our problem statement becomes easier:   
**How to return a helpful error message when an `Option` is `None` in this case?**

Turns out, there are multiple solutions!

## Solution 1: change the return type 

If "not having a value" is truly an error condition in your program's logic, you should use `Result` instead of `Option`. `Option` is best used when the absence of a value is a normal, expected possibility, not an error state.

In our case, if you can change `get_user()` to return a `Result` instead of an `Option`, you can use the `?` operator as you intended:

```rust
fn get_user() -> Result<String, String> {
    // ...
    Ok("Alice".to_string())
}

fn get_user_name() -> Result<String, String> {
    let user = get_user()?;
    // Do something with `user`
    // ...
    Ok(user)
}
```

However, you might not be able to change `get_user()` to return a `Result` for various reasons,
for example, if it's part of a library or if it's used in many places
or if other callers don't treat the absence of a user as an error. 

In that case, read on!

## Solution 2: `ok_or` 

The initial error message, while cryptic, gave us a hint:

```rust
use `.ok_or(...)?` to provide an error compatible with `Result<(), Box<dyn std::error::Error>>`.
```

Apparently we can use the `ok_or` method, which converts the `Option` into a `Result`:

```rust
let user = get_user().ok_or("No user")?;
```

That's convenient! It also chains well when we use iterator patterns:

```rust
let user = get_user()
    .ok_or("No user")?
    .do_something()
    .ok_or("Something went wrong")?;
```

([Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=c3053fe0b08b3157d377d3dce68d9e00)

`ok_or` is also great if you can recover from `None` and handle that case gracefully:

```rust
let user = get_user().ok_or(get_logged_in_username())?;
```

These are good use cases for `ok_or`.

On the other side, it might not be immediately obvious to everyone what `ok_or` does.
I find the name `ok_or` unintuitive and needed to look it up many times.
That's because `Ok` is commonly associated with the `Result` type, not `Option`.
There's `Option::Some`, so it could have been called `some_or`, which was [actually suggested in 2014](https://github.com/rust-lang/rust/pull/17469#issuecomment-56919911), but the name `ok_or` won out,
because `ok_or(MyError)` reads nicely and I can see why. Guess we have to live with the minor inconsistency now.

I think `ok_or` is a quick solution to the problem, but there are alternatives that might be more readable.

## Solution 3: `match`

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

This is already more explicit and easier to understand for beginners.
The one issue I had when teaching this was that it looked a bit more verbose for simple cases.

## Solution 4: `let-else`

With Rust 1.65, [the `let-else` expression was stabilized](https://blog.rust-lang.org/2022/11/03/Rust-1.65.0.html#let-else-statements), so now you can write this: 

```rust
let Some(user) = get_user() else {
    return Err("No user".into());
};

// Do something with user
```

In my opinion, that's the best of both worlds: it's compact while still being easy to understand.
It's unanimously loved by beginners and experienced Rustaceans alike.

For some explanation: if `get_user()` returns `Some`, the `let` statement will destructure the `Some` variant and assign the value to the `user` variable. If `get_user()` returns `None`, the `else` block will be executed and we return early with an error.

**My favorite thing about `let-else` is that it clearly highlights the 'happy path' of your code.**

Unlike a `match` statement where you need to read both arms to understand the intended flow, `let-else` makes it immediately clear what the expected case is, with the `else` block handling the exceptional case.

This is a clear winner.
It is way more intuitive for beginners; once they understand the pattern, they use it all the time!

## Bonus: `anyhow`

I wanted to add one honorable mention here.

If you're writing an application (not a library) and you're using the
[`anyhow`](https://github.com/dtolnay/anyhow) crate already, you can also use their `context`
method to handle `None`:

```rust
use anyhow::{Context, Result};

fn get_user_name() -> Result<String> {
    let user = get_user().context("No user")?;
    // Do something with `user`
    Ok(user)
}
```

It's slightly less verbose than `let-else`, which makes it appealing.
Just remember that `anyhow` is an external dependency.
It's probably fine for applications, but you might not want to use it in a library as users of
your library can no longer match on the concrete error variant then.

That's why I believe that `let-else` is the best solution for handling `None` in most cases.

## Conclusion

For most cases, I prefer this syntax:

```rust
let Some(value) = some_function() else {
    return Err("Descriptive error message".into());
};
```

To me, `let-else` is the best solution for handling `None` because:

- It's part of the standard library.
- It works for both libraries and applications.
- It's easy to understand for beginners.
- It's reasonably compact.
- It allows for more complex error handling logic in the `else` block if needed.
- Learning the mechanics behind it is helpful in other places in Rust.

I hope this helps more people handle `Option` in a more robust way.
If it helps a single person avoid one `unwrap`, it was already worth it.