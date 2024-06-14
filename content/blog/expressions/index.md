+++
title = "Effective Use Of Expressions In Rust"
date = 2024-05-20
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = [
    { name = "Hanno Braun", url = "https://www.hannobraun.com/" },
    { name = "Thomas Zahner",  url = "https://github.com/thomas-zahner"}
]
resources = [
    "Rust By Example: Expressions &mdash; [doc.rust-lang.org](https://doc.rust-lang.org/rust-by-example/expression.html)",
    "Rust Reference: Expressions &mdash; [doc.rust-lang.org](https://doc.rust-lang.org/reference/expressions.html)",
    "[Rust, Ruby, and the Art of Implicit Returns &mdash; Earthly blog](https://earthly.dev/blog/single-expression-functions/)"
]
+++


Expressions are an underrated feature in Rust. 
They can easily be dismissed as a side-note, a nuance of Rust's syntax.
Underneath the surface, though, expressions have a deep impact on the semantics of the language. I would go as far as to say that they shaped the way I think about code in *any* language.

## Expressions In Other Languages

Languages like Go, C++, Java, TypeScript have expressions, too!
In comparison to Rust, though, they are often way more limited in their use. 

In Go, for example, an `if` statement is... well, a statement and not an expression. This has some surprising side-effects. For example, you can't use an `if` statement in a ternary expression like you would in Rust. 

```go
// This is not valid Go code
let x = if condition { 1 } else { 2 };
```

Instead, you'd have to write a full-blown `if` statement
along with a slightly unfortunate upfront variable declaration:

```go
var x int
if condition {
	x = 1
} else {
	x = 2
}
```

Since `if` is an expression in Rust, using it in a ternary expression is perfectly normal. 

```rust
let x = if condition { 1 } else { 2 };
```

```rust
let Some(x) = foo() else { return };
```

This works because `e









In Rust they are a core building block of the language.