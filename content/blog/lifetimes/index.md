+++
title = "Don't Worry About Lifetimes"
date = 2024-05-15
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

When people say that learning Rust is hard, they often mention lifetimes. However, even after seven years of writing Rust, 95% of my code, probably more, doesn't have any lifetime annotations! It is one of the areas of the language that I definitely worried way too much about when learning Rust and I see many beginners do the same.

## What are lifetimes?

Lifetimes are a way to tell the compiler how long a reference is valid for.

```rust
fn foo<'a>(bar: &'a str) {
    // ...
}
```

Here, we are telling the compiler that the reference `bar` is valid for the lifetime `'a`. The compiler will then check that the reference is not used after the lifetime `'a` ends.

Rust has a concept of lifetime *elision*, which means that you don't have to write lifetime annotations in many cases. The compiler will infer them for you.

{% info(headline="Lifetime Rules Recap", icon="info") %}

The rules are simple:

1. Every input reference to a function gets a distinct lifetime.
2. If there's exactly one input lifetime, it gets applied to all output references.
3. If there's multiple input lifetimes but one of them is `&self` or `&mut self`, then the lifetime of `self` is applied to all output references.

You only have to write out the lifetimes yourself if you have more than one input lifetime and none of them are `&self` or `&mut self`.

{% end %}

In the above example, we have one input lifetime, so we don't have to write it out. This is equivalent (and easier on the eyes):

```rust
fn foo(bar: &str) {
    // ...
}
```

It turns out, lifetimes are *everywhere* in Rust, they are just implicit most of the time.

## Reasons for lifetimes

Nowadays, I consider it an anti-pattern to prematurely add lifetime annotations to a piece of code without a good reason. There's really only two situations where you should add lifetime annotations:

1. There is a performance bottleneck in a hot path of your code, and you have profiled it and determined that the bottleneck is indeed because of allocations.
2. Code that you depend on requires lifetime annotations.

In all other situations, let the compiler do its job.

## Lifetimes are contagious!

The problem with lifetimes is that they spread in your codebase like a virus. Once you add a lifetime annotation, you have to add it to all the functions that call it, and all the functions that call those functions, and so on.

For example, let's say you have a struct that contains a `String`:

```rust
struct Foo {
    bar: String
}
```

And you want to optimize it by using a `&str` instead to avoid allocations:

```rust
struct Foo<'a> {
    bar: &'a str
}
```

Now you have to add the lifetime annotation to all the functions that use `Foo`:

```rust
fn foo<'a>(foo: &'a Foo) {
    // ...
}
```

This can get out of hand very quickly. The function signature is now more complex, and it is harder to understand what the function does. It also makes it harder to refactor your code because you have to move the lifetime annotation with it. Lifetimes are not free! It's very easy to put yourself into a corner, where it's hard to make fundamental changes to how your code works. Explicit lifetimes should be treated as a last resort because they increase tech debt and alienate beginners.

## Don't Be Afraid Of Lifetimes Either

What if you depend on a library that requires lifetime annotations?

One example is servo's `html5ever`, a high-performance HTML5 parser written in Rust. It uses lifetimes extensively to ensure memory safety and performance. When using such a library, you have to deal with lifetimes, whether you like it or not. However, understanding the basics of lifetimes can help you navigate these situations more effectively. Remember that lifetimes are there to help you write safe and efficient code. They are not something to be afraid of but rather a powerful tool in your Rust toolkit.

Get comfortable with lifetimes even if you don't use them often.

## A Practical Example

Let's look at a practical example where lifetimes need to be explicitly added. Consider a function that returns the longest of two string slices.

```rust
fn longest(x: &str, y: &str) -> &str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

If we tried to compile that, we'd get an error:

```
error[E0106]: missing lifetime specifier
 --> src/lib.rs:1:33
  |
1 | fn longest(x: &str, y: &str) -> &str {
  |               ----     ----     ^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but the signature does not say whether it is borrowed from `x` or `y`
help: consider introducing a named lifetime parameter
  |
1 | fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
  |           ++++     ++          ++          ++
```

What went wrong?

## Put Yourself Into the Shoes of the Compiler

To understand the error, imagine you are the Rust compiler. Your job is to ensure that references are always valid and that no reference outlives the data it points to. In this example, the function `longest` takes two string slices and returns one of them. 

As the compiler, you see that the function signature promises to return a reference (`&str`), but it doesn't specify which input reference (`x` or `y`) it corresponds to. This ambiguity makes it impossible for you to guarantee the safety of the returned reference. 

Consider this situation: if you had to make sure a book borrowed from a library was returned on time, but you didn't know which library it came from, you'd have a hard time enforcing the due date. Similarly, the compiler needs to know the relationship between the input and output lifetimes to enforce correct borrowing rules.

To fix this, we need to add a lifetime parameter to the function signature:

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

In this example, we have two input lifetimes, so we need to specify them explicitly. The function takes two references, `x` and `y`, both with the same lifetime `'a`, and returns a reference with the same lifetime `'a`. This ensures that the returned reference is valid as long as both input references are valid.

## Conclusion

Lifetimes in Rust can seem daunting at first, but with some practice, you'll find that you'll rarely have to think about them. Most of the time, the compiler handles them for you through lifetime elision, so you don't have to worry about them. When you do need to use them explicitly, it should be for a good reason.

Many people say lifetimes contribute to Rust's steep learning curve and make the syntax more complex. I would agree with that, but I also think that lifetimes are a necessary part of Rust's safety guarantees. Don't let the fear of lifetimes hold you back from learning and using Rust. Embrace them as part of the language's robust safety guarantees, even if they are only necessary in a small part of your codebase.

Happy coding!