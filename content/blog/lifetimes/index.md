+++
title = "Don't Worry About Lifetimes"
date = 2024-05-15
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

When people say that learning Rust is hard, they often mention lifetimes.
However, even after seven years of writing Rust, 95% of my code, probably more,
doesn't have any lifetime annotations! It is one of the areas of the language
that I definitely worried way too much about when learning Rust and I see many
beginners do the same.

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

You only have to write out the lifetimes yourself, if you have more than one
input lifetime and none of them are `&self` or `&mut self`.

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

This can get out of hand very quickly. The function signature is now more complex, and it is harder to understand what the function does. It also makes it harder to refactor your code because you have to move the lifetime annotation with it. Lifetimes are not free! It's very easy to put yourself into a corner, where it's hard to make fundamental changes to how your code works. Explicit lifetimes should be treated as a last resort, because they increase tech debt and alienate beginners.

## Don't Be Afraid Of Lifetimes Either

What if you depend on a library that requires lifetime annotations?

One example is servo's `html5ever`, a high-performance HTML5 parser written in Rust. It uses lifetimes extensively to ensure memory safety and performance. When using such a library, you have to deal with lifetimes, whether you like it or not. However, understanding the basics of lifetimes can help you navigate these situations more effectively. Remember that lifetimes are there to help you write safe and efficient code. They are not something to be afraid of but rather a powerful tool in your Rust toolkit.

Get comfortable with lifetimes even if you don't use them often. 

## Conclusion

Lifetimes in Rust can seem daunting at first, but with some practice, you'll find that you'll rarely have to think about them.
Most of the time, the compiler handles them for you through lifetime elision, so you don't have to worry about them. When you do need to use them explicitly, it's should be for a good reason.

Many people say, lifetimes contribute to Rust's steep learning curve and make
the syntax more complex. I would agree with that, but I also think that
lifetimes are a necessary part of Rust's safety guarantees. Don't let the fear
of lifetimes hold you back from learning and using Rust. Embrace them as part of
the language's robust safety guarantees, even if they are only necessary in a
small part of your codebase.