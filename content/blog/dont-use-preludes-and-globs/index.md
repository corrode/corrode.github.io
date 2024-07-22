+++
title = "Don't Use Preludes And Globs"
date = 2024-07-22
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

Have you ever wondered why you don't have to import `std::result::Result` before you can use it?

The reason is Rust's [prelude](https://doc.rust-lang.org/std/prelude/index.html), which re-exports a bunch of types, that automatically get added to your program's namespace.
A more correct definition is: *Preludes are collections of names automatically brought into scope in every module of a crate.*

In fact, there are multiple preludes like
[`std::prelude::v1`](https://doc.rust-lang.org/std/prelude/v1/index.html), [`std::prelude::rust_2015`](https://doc.rust-lang.org/std/prelude/rust_2015/index.html), and [`std::prelude::rust_2024`](https://doc.rust-lang.org/nightly/std/prelude/rust_2024/index.html), and more in the future.

It would be jarring to import those basic types over and over again so I'd say it's a win to have a prelude for the standard library.

Maybe that's the reason why popular libraries started to provide their own preludes: [Rayon has one](https://docs.rs/rayon/latest/rayon/prelude/index.html) and so does 
[pyo3](https://docs.rs/pyo3/latest/pyo3/prelude/index.html) and [bevy](https://docs.rs/bevy/latest/bevy/prelude/index.html) and
[ratatui](https://docs.rs/ratatui/latest/ratatui/prelude/index.html). 

Some people consider preludes and glob imports[^1] to be antipatterns &ndash; I'm one of them. Let me explain why.

[^1]: A glob import (also called a wildcard import) is an import that brings all items of a module into scope. For example, `use std::collections::HashMap;` vs `use std::collections::*;`. 

## I don't like preludes

Preludes help beginners start quickly with zero boilerplate, but can cause namespace pollution and naming conflicts for experienced developers in larger projects.

I have a hard time reviewing your code which uses preludes: looking up a definition might not work in my code review tool, and I'd have to manually track down where a types came from.

Explicit imports bring clarity.

Speaking of which! A good compromise between convenience and clarity is to import whole modules instead of individual items, such as `use std::fmt`. Then you can say `fmt::Debug` instead of `std::fmt::Debug`.

Unless you write a highly critical framework which provides well-established types, which are *absolutely positively always* mandatory in every (or at least most) interactions with your library, don't add a prelude. Even then, make sure that prelude carries its own weight. [Tokio removed their prelude because that wasn't the case](https://github.com/tokio-rs/tokio/issues/3257).

An explicit import might not be that bad. In fact, it might even clear things up for your users, because it's easier to see where imports come from.

If you're worried about ergonomics, why not re-export common types in root? Then they can get imported with `use mycrate::SomeType;` instead of `use mycrate::mymodule::SomeType;`.

```rust
// Re-export a type in the your lib.rs
pub use mymodule::SomeType;
```

On the same note, avoid glob imports (like `use prelude::*`
or `use mycrate::mymodule::*`).
The reasons are the same: they hide dependencies and make it harder to grep for usages of a type or function.

## Common Arguments for Preludes And Glob Imports

Let's address some common arguments in favor of preludes and glob imports
and see if there's a better way to achieve the same goal.

### Preludes in examples

Some people like to use preludes in their documentation examples.

This can be sweet when you quickly want to show how to use your library without too much boilerplate. But at what cost? At what terrible cost?[^2]

[^2]: I'm exaggerating. Bear with me.

Users *can and will* start to copy-paste that prelude into their code, at which point you'll have to support it. It's convenient in the beginning, but can result in a maintenance burden in the long run.

Instead, why not use hidden code lines for imports in your documentation examples? This way, the examples are still easy to read, but users can't copy-paste the imports:

```rust
//! # Examples
//!
//! ```
//! # use mycrate::SomeType;
//! # fn main() {
//! let t = SomeType::new(); 
//! # }
//! ```
```

This will render as:

```rust
let t = SomeType::new();
```

### Reducing boilerplate

Another common argument for preludes is that they reduce friction when importing types.

I don't think that's true anymore. IDE support for Rust has made great strides in the last years. Nowadays, your IDE will just auto-import the type for you. (Largely thanks to [Rust Analyzer](https://rust-analyzer.github.io/) and [Rust Rover](https://www.jetbrains.com/rust/))
Problem solved!

And to also address the root cause: If you see the urge to add a prelude, because your crate requires importing many modules to be usable, maybe your public API is too big? Try to reduce the number modules.

### Trait-only preludes

Preludes, which only bring traits into scope might be acceptable.
This trick is sometimes used in combination with extension traits, which add extra functionality to common types. `rayon` does that, for example, and it's quite magical if you can suddenly parallelize an iterator by just swapping `iter` with `par_iter`.

From their documentation:

```rust
use rayon::prelude::*;
fn sum_of_squares(input: &[i32]) -> i32 {
    input.par_iter() // <-- just change that!
         .map(|&i| i * i)
         .sum()
}
```

I think that's a solid use case for a prelude, but I never had such a clear-cut case in my own code.

### Glob imports in tests

The only exception for using glob imports I can think of is in tests. It's common to see `use super::*;` in tests to bring all functions from the parent module into scope. This can be a helpful mechanism to reduce boilerplate.

```rust
fn foo() -> i32 {
    42
}

mod tests {
    use super::*;
    
    #[test]
    fn test_something() {
        assert_eq!(foo(), 42);
    }
}
```

## Conclusion

In your own code, avoid preludes and, by extension, glob imports.

Here are the main disadvantages:

- Makes it harder to know where types and functions come from
- Can lead to naming conflicts, especially in larger codebases and when using multiple crates.
- Complicates security audits because it's hard to see where code came from.
- May hide module hierarchy and structure, which is useful if you want to learn how a crate is designed.
- Can make IDE name resolution less reliable: if you have a name conflict, the IDE might not know which one you mean or might not be able to find the definition. 
- Hides imports in documentation examples, making it harder to understand

As you can see, the list of downsides is long. The only upside is that it saves a few keystrokes when writing code, which isn't worth it in the long run.

**Pro tips:**

- Enable the [clippy lint for wildcard imports](https://rust-lang.github.io/rust-clippy/master/index.html#/wildcard_imports) to catch glob imports in your code.
- If you absolutely must use a prelude, use preludes for traits and macros only, not for types
- If you use a crate, which has a prelude, consider not using it and instead importing the types you need explicitly. This way, you can avoid conflicts down the road and make it easier to see where a type come from.
