+++
title = "Don't Use Preludes And Globs"
date = 2024-07-29
draft = false
template = "article.html"
[extra]
updated = 2024-08-07
series = "Idiomatic Rust"
reviews = [
    { name = "Brett Witty", url = "https://www.brettwitty.net" },
    { name = "Ludwig Weinzierl", url = "https://weinzierlweb.com/ludwig" },
]
+++

Have you ever wondered why you don't have to import `std::result::Result` before you can use it?

The reason is Rust's [prelude](https://doc.rust-lang.org/std/prelude/index.html), which re-exports a bunch of types that automatically get added to your program's namespace.
A more correct definition is: *Preludes are collections of names automatically brought into scope in every module of a crate.*

In fact, there are multiple preludes like
[`std::prelude::v1`](https://doc.rust-lang.org/std/prelude/v1/index.html), [`std::prelude::rust_2015`](https://doc.rust-lang.org/std/prelude/rust_2015/index.html), and [`std::prelude::rust_2024`](https://doc.rust-lang.org/nightly/std/prelude/rust_2024/index.html), and more in the future.

It would be jarring to import those basic types over and over again so I'd say it's a win to have a prelude for the standard library.

Maybe that's the reason why popular libraries started to provide their own preludes: [Rayon has one](https://docs.rs/rayon/latest/rayon/prelude/index.html) and so do 
[pyo3](https://docs.rs/pyo3/latest/pyo3/prelude/index.html) and [bevy](https://docs.rs/bevy/latest/bevy/prelude/index.html) and
[ratatui](https://docs.rs/ratatui/latest/ratatui/prelude/index.html). 

Some people consider preludes and glob imports[^1] to be antipatterns &ndash; I'm one of them. Let me explain why.

[^1]: A glob import (also called a wildcard import) is an import that brings all items of a module into scope. For example, `use std::collections::HashMap;` vs `use std::collections::*;`. 

## I don't like preludes

Preludes help beginners start quickly and with zero boilerplate, but they also prevent users from understanding the full picture of a crate. 
For larger projects, preludes can cause namespace pollution and naming conflicts.

I have a hard time reviewing code which uses preludes: looking up a definition might not work in my code review tool, and I'd have to manually track down where types came from.

Explicit imports bring clarity.

Speaking of which! A good compromise between convenience and clarity is to import whole modules instead of individual items, such as `use std::fmt`. Then you can say `fmt::Debug` instead of `std::fmt::Debug`. It's a little easier on the eyes, but still provides clarity.

Unless you write a highly critical framework which uses well-established types, which are *absolutely positively always* mandatory in every (or at least most) interaction with your library, don't add a prelude. Even then, make sure that prelude carries its own weight. [Tokio removed their prelude because that wasn't the case](https://github.com/tokio-rs/tokio/issues/3257).

An explicit import might not be that bad. In fact, it might even clear things up for your users, because it's easier to see where imports come from.

If you're worried about ergonomics, why not re-export common types in root? Then they can get imported with `use mycrate::SomeType;` instead of `use mycrate::mymodule::SomeType;`.

```rust
// Re-export a type in your lib.rs
pub use mymodule::SomeType;
```

On the same note, avoid glob imports (like `use prelude::*`
or `use mycrate::mymodule::*`).
The reasons are the same: they hide dependencies and make it harder to grep for usages of a type or function.

## Common Arguments for Preludes

Let's address some common arguments in favor of preludes and glob imports
and see if there's a better way to achieve the same goal.

### Preludes in examples

Some people like to use preludes in their documentation examples.

This can be sweet when you quickly want to show how to use your library without too much boilerplate. But at what cost?

Users *can and will* start to copy-paste that prelude into their code, at which point you'll have to support it. It's convenient in the beginning, but can result in a maintenance burden in the long run.

One way to avoid that is to hide code lines for imports in your documentation examples. With that, examples are still easy to read, while users can't copy-paste the imports:

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

{% info(headline="Caution When Hiding Code in Examples", icon="warning") %}

Be careful with this approach and don't overdo it. Try to keep your examples simple and don't hide too much code because it can be a frustrating experience for your users if they copy-paste your examples and they don't work.

{% end %}

To address the root cause: If you feel the urge to add a prelude because your crate requires importing many modules to be usable, consider whether your public API is too large. Try reducing the number of modules and types by refactoring your public API. This way, you won't need to hide imports in the first place.

### Reducing boilerplate

Another common argument for preludes is that they reduce friction when importing types.

I don't think that's true anymore. Editor support for Rust has made great strides in the last years. Nowadays, your editor will just auto-import the type for you. (Largely thanks to [Rust Analyzer](https://rust-analyzer.github.io/) and [Rust Rover](https://www.jetbrains.com/rust/)). Problem solved! [^editor]

[^editor]: I should mention that many modern editors can often show you the fully qualified path of a type, even when it's imported via a prelude. This does away with some of the clarity concerns associated with preludes.

### Trait-only preludes

Preludes which only bring traits into scope might be acceptable.
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

I think that's a solid use case for a prelude, but I've never had such a clear-cut case in my own libraries. 

### Flexibility For Library Authors

Preludes can let library authors refactor their code without causing unnecessary churn for users:
If you often reorganize your internal structure, a prelude can provide a stable public API for common types.
The Bevy game engine uses this pattern, for example.

But hold on! This doesn't mean the internal logic stays the same, and a prelude doesn't guarantee API stability either.
These hidden changes might cause subtle bugs (e.g., when the prelude contains extension traits) which are hard to pin down. 

Ask yourself: why does my public API change so much? There seems to be a deeper-rooted problem here. 
For example, you might have leaked internal details into your public API, which you now want to change.

One way to provide stability without a prelude is to embrace semantic versioning. Before 1.0, you're free to change your API frequently, with users expecting some churn. Once you're happy with the API, switch to 1.0 and promise to maintain backwards compatibility. This approach gives you the flexibility of early prototyping paired with the stability guarantees of more mature libraries.

### Sane Defaults Out of the Box

For complex libraries, a well-designed prelude can improve clarity by curating important types. This seems appealing in security-sensitive domains to prevent misuse of incorrect types.

For example, a crypto library might provide a prelude with only the most secure algorithms. This way, users are guided towards secure defaults without needing to understand the intricacies of each algorithm.

That's a valid argument, but I'd argue that it's a slippery slope. First off, switching an algorithm is still a breaking change and it might still require changes in user code. Second, a prelude is no substitute for good documentation, examples, and a "Getting Started" guide.

Consider using Rust's `#[deprecated]` attribute to phase out old behavior. This way, users get time to adapt to the new API.
Leverage Rust's type system: Use newtypes, [sealed traits](https://predr.ag/blog/definitive-guide-to-sealed-traits-in-rust/), and visibility modifiers (like `pub(crate)`) to guide users towards correct usage without relying on a prelude.

My rule of thumb here is to avoid hiding complexity behind a prelude and err on the side of explicitness.

## Common Arguments for Glob Imports

Now that we've covered preludes, let's look at some common arguments for why people use glob imports 
and why you should be careful.

### Preludes are convenient for beginners

Some people argue that preludes are beginner-friendly.
The argument goes that beginners don't have to worry about importing types and can focus on learning the core concepts of a library.

As we will see, this can backfire quickly.

Here's the catch: when you use glob imports, you're opening yourself up to potential build breaks from minor version updates.
Adding new public items is considered a minor change according to [semantic versioning](https://semver.org) rules. That means when a crate bumps its version from, say, 1.2.0 to 1.3.0, it's allowed to add new public items without breaking backwards compatibility.

Now, picture this scenario: You're using a crate with a glob import, bringing all its public items into scope. You update the crate to the latest minor version, and suddenly your code doesn't compile anymore. Ouch.

Well, that new minor version might have added a new public item that conflicts with a name in your code.

Here's a quick example to illustrate:

```rust
// In your code you update some_crate from 1.2.0 to 1.3.0
// In 1.3.0, some_crate added a new public item called Ferris.
use some_crate::*;

// In your own code, you have a struct called Ferris
// Now you have a naming conflict, and your code won't compile!
pub struct Ferris;
```

The crate author didn't break any promises &ndash; adding new public items is allowed in minor versions. But because of the glob import, what should have been a harmless update turned into a breaking change for your codebase and a minor headache for you.

Explicit imports protect you from these unexpected conflicts and make your code more resilient to changes in your dependencies.


### Glob imports in tests

It's common to see `use super::*;` in tests to bring all functions from the parent module into scope. This can be a helpful mechanism to reduce boilerplate.
That's the only exception I can think of where glob imports are acceptable.

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
- Can lead to naming conflicts, especially in larger codebases and when using multiple crates
- Complicates security audits because it's hard to see where code came from
- May hide module hierarchy and structure, which is useful if you want to learn how a crate is designed
- Can make IDE name resolution less reliable: if you have a name conflict, the IDE might not know which one you mean or might not be able to find the definition
- Hides imports in documentation examples, making it harder to understand

As you can see, the list of downsides is long. The only upside is that it saves a few keystrokes when writing code, which isn't worth it in the long run.

**Pro tips:**

- Enable the [clippy lint for wildcard imports](https://rust-lang.github.io/rust-clippy/master/index.html#/wildcard_imports) to catch glob imports in your code.
- If you really want to create a prelude, at least use it for traits and macros only, not for types. Extending behavior of existing types (like adding a `par_iter` method to iterators with Rayon) is an acceptable use case for preludes if used in moderation. To avoid naming conflicts, consider using a unique prefix for extension traits like `CrateNameHashmapExt` instead of `HashMapExt`.
- If you depend on a crate which has a prelude, consider not using it and instead importing the types you need explicitly. This way, you can avoid conflicts down the road and make it easier to see where a type comes from.