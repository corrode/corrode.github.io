+++
title = "Don't Worry About Lifetimes"
date = 2024-05-15
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

When people say that learning Rust is hard, they often mention lifetimes. However, even after seven years of writing Rust, 95% of my code, probably more, doesn't have any lifetime annotations! It is one of the areas of the language that I definitely worried way too much about when learning Rust, and I see many beginners do the same.

## What are lifetimes?

Lifetimes tell the compiler how long a reference is valid.

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
3. If there are multiple input lifetimes but one of them is `&self` or `&mut self`, then the lifetime of `self` is applied to all output references.

You only have to write out the lifetimes yourself if you have more than one input lifetime and none of them are `&self` or `&mut self`.

{% end %}

In the example above, we have one input lifetime, so we don't have to write it out. This is equivalent (and easier on the eyes):

```rust
fn foo(bar: &str) {
    // ...
}
```

It turns out, lifetimes are *everywhere* in Rust, but they are just implicit most of the time.

## Reasons for lifetimes

Nowadays, I consider it an anti-pattern to prematurely add lifetime annotations to a piece of code without a good reason. There's really only two situations where you should add lifetime annotations:

1. **There is a performance bottleneck**: You found a slow piece of code in your hot path, and you have profiled it and determined that the bottleneck is indeed because of allocations. In this case, it could make sense to use lifetimes to avoid allocations. (The alternative is to refactor your code to use a better algorithm to avoid the hot path in the first place.)
2. **Code that you depend on requires lifetime annotations:** There's little you can do about this, other than to look for alternatives that don't require lifetimes.

In all other situations, let the compiler do its job.

In practice, I only have to add lifetimes in two kinds of situations: returning references from a function and storing a reference in a struct.

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

This can get out of hand very quickly. The function signature is now more complex, and it is harder to understand what the function does. It also makes it harder to refactor your code because you have to move the lifetime annotation with it. Lifetimes are not free! It's very easy to put yourself into a corner where it's hard to make fundamental changes to how your code works. Explicit lifetimes should be treated as a last resort because they increase tech debt and alienate beginners.

## Don't Be Afraid Of Lifetimes Either

What if you depend on a library that requires lifetime annotations?

One example is Servo's [`html5ever`](https://github.com/servo/html5ever/), a high-performance HTML parser written in Rust. It uses lifetimes extensively to ensure memory safety and performance. When using such a library, you have to deal with lifetimes, whether you like it or not. However, understanding the basics of lifetimes can help you navigate these situations more effectively. Remember that lifetimes are there to help you write safe and efficient code. They are not something to be afraid of but rather a powerful tool in your Rust toolkit.

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

As the compiler, you see that the function signature promises to return a reference (`&str`), but it doesn't specify which input reference (`x` or `y`) it corresponds to. Will the returned string live as long as `x` or `y`? It depends on which of the two strings is longer and this can only be determined at runtime.

Without this knowledge, you can't confirm that the returned reference will be valid: You need to specify the *relationship* between the input and the output to make this guarantee. If you pick the wrong one, you might end up with a dangling reference. The ambiguity makes it impossible for the compiler to guarantee the safety of the returned reference.

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

By adding `'a`, we specify that both input references `x` and `y` have the same lifetime `'a`, and the returned reference will also have this lifetime. This makes it clear to the compiler that the returned reference is guaranteed to be valid as long as *both* input references are valid. Now, the compiler can safely check and ensure that the references are used correctly throughout the code.

{% info(headline="Side Note: Other Programming Languages", icon="info") %}

"Hold on," you might say, "other programming languages don't require me to think about lifetimes. Why does Rust make it so complicated?"

The C programming language will happily let you access memory that has been freed, leading to undefined behavior. Dangling pointers are a common source of bugs, and this is what lifetimes in Rust aim to prevent. The Rust compiler makes you stop and think about the ambiguity in your code and forces you to make relationships between data explicit.

"But what about Python, PHP, or Java? We don't have to worry about lifetimes there, right?"

Yes, these languages have systems like reference counting or garbage collectors in place, which automatically handle memory management for you. There is an overhead to these mechanisms, though, and they have a performance overhead. In some restricted environments, like embedded systems or real-time applications, automatic memory management is not an option because they can introduce unpredictable pauses or the environment doesn't allow a runtime.

Rust's lifetimes are a way to ensure memory safety without the overhead of a garbage collector at the small cost of being explicit about lifetimes in the face of ambiguity.

{% end %}

## Naming Lifetimes

Part of why lifetimes look so scary is that they are often named `'a`, `'b`, or `'c`. This makes them look like some kind of cryptic, mathematical incantation. But in reality, lifetimes are just "labels", [you can name them however you want](https://www.possiblerust.com/pattern/naming-your-lifetimes).
This can be quite helpful if you need to juggle multiple borrow sources
or when you want to express the source of a reference more clearly. Serde uses this technique to great effect in its `Deserialize` trait:

```rust
fn deserialize<'de, D>(deserializer: D) -> Result<Self, D::Error>
where
    D: Deserializer<'de>,
{
    // ...
}
```

Here, `'de` means "this lifetime is tied to the deserializer". Suddenly, that syntax makes a lot more sense!

Think of lifetimes as just a signature for the same reason that types have
signature: Both can be inferred, but sometimes it's easier to just spell them
out to avoid mistakes. As an added bonus, the signature serves as documentation, too!

## Conclusion

At the start of my Rust journey, I worried about lifetimes way too much. I thought it's the key to understanding Rust and that I need to master it to write good code. But the truth is, you don't need to worry about lifetimes most of the time. The compiler does a great job of inferring lifetimes for you, and you should only add them when you have a good reason to do so.

