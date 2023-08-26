+++
title = "Compile-Time Invariants in Rust"
date = 2023-08-26
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = []
+++

Working on something completely unrelated, I stumbled across this comment in a
Rust project:

```rust
// TODO: Make sure this has at least one element
let kafka_brokers = vec!["kafka:9092", "kafka2:9092"];
```

The intent here was to make sure that there is at least one Kafka broker
(server) to connect to.

Right now, the program would happily compile with an
empty vector. We'd have to add a runtime check to make sure that the vector is not empty:

```rust
if kafka_brokers.is_empty() {
    panic!("At least one Kafka broker is required");
}
```

That's not great, because we have to remember to validate the vector before
we use it. During refactoring, the check could be accidentally removed, which
would lead to a runtime error.

## Wait, there's a crate for that!

Maybe you know about the [`vec1`](https://github.com/rustonaut/vec1) crate,
which provides a `Vec1` type that can **only** be constructed with **at least**
one element.

```rust
let kafka_brokers = vec1!["kafka:9092"]; // works
let kafka_brokers = vec1![]; // compile error
```


Now the program would not compile if we tried to use `vec1!` with zero
elements, which is exactly what we want!

## Type-driven development

There's a deeper lesson here, which applies to idiomatic Rust code in general:  
**Lean into the type system to enforce invariants at compile-time.**

An invariant is a condition that must always hold true. You want to enforce
these invariants as early as possible.

I recently learned about the term [type-driven
development](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/),
a practice that emphasizes the use of types to ensure program correctness.

To learn how it works, let's try to implement a basic version of `vec1` ourselves.

## Implementing `vec1`

The trick is to make our `Vec1` look like a regular `Vec` on the outside, but
internally we use two fields to enforce at least one element.

```rust
pub struct Vec1<T> {
    // Fields are not public, so we can enforce 
    // invariants during construction
    first: T,
    rest: Vec<T>,
}
```

To construct a `Vec1`, we can provide a macro that is similar to `vec!`:

```rust
#[macro_export]
macro_rules! vec1 {
    // The first element is mandatory, 
    // while additional elements are optional (denoted by the `*`).
    // Just like `vec!`, we also allow a trailing comma.
    [$x:expr $(, $xs:expr)* $(,)?] => {{
        Vec1 {
            first: $x,
            rest: vec![$($xs),*],
        }
    }};
    [] => {
        compile_error!("vec1! requires at least one element");
    };
}
```

[`compile_error!`](https://doc.rust-lang.org/std/macro.compile_error.html) is a
macro that will always fail to compile with the given error message.

Finally let's implement a few traits to make our `Vec1` behave like a
normal `Vec`.

For example, we probably want to
[iterate](https://doc.rust-lang.org/std/iter/trait.IntoIterator.html) over the
elements:

```rust
impl<T> IntoIterator for Vec1<T> {
    type Item = T;
    type IntoIter = std::vec::IntoIter<Self::Item>;

    fn into_iter(self) -> Self::IntoIter {
        let mut v = vec![self.first];
        v.extend(self.rest);
        v.into_iter()
    }
}
```

We also want to [index](https://doc.rust-lang.org/std/ops/trait.Index.html) into our `Vec1`:

```rust
impl<T> Index<usize> for Vec1<T> {
    type Output = T;

    fn index(&self, index: usize) -> &Self::Output {
        match index {
            0 => &self.first,
            // We can use `index - 1` because we know that
            // `index` is at least 1.
            i => &self.rest[i - 1],
        }
    }
}
```

To behave *exactly* like a `Vec`, we would need to implement [a lot more
traits](https://doc.rust-lang.org/std/vec/struct.Vec.html#trait-implementations),
but remember that the goal here is to learn about the general pattern of using
types to enforce invariants.

With that, let's write some tests:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_single_element() {
        let v = vec1!["Hello"];
        assert_eq!(v[0], "Hello");
    }

    #[test]
    fn test_multiple_elements() {
        let v = vec1!["Hello", "World"];
        assert_eq!(v[0], "Hello");
        assert_eq!(v[1], "World");
    }
    
    #[test]
    fn test_other_type() {
        let _v = vec1![1,2,3,4];
    }
    
    // This won't compile, which is what we want to enforce the invariant.
    // Uncommenting the next line will break the compilation.
    // #[test]
    // fn test_zero_elements() {
    //     let v = vec1![];
    // }
}
```

If you want to play around with that code, [here's a link to the Rust
playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=3c65cd2caaef8104914b8a6988bf2cb1).

We now have a vector with at least one element, but we can do better!

If we assume that the Kafka brokers don't change at runtime &mdash;
a reasonable assumption, given that it's a configuration value &mdash; we could
also use a [fixed-size
array](https://doc.rust-lang.org/std/primitive.array.html).

By using an array, we can statically allocate the whole collection, which is
more efficient than using a `Vec` (which is dynamically allocated on the heap).

## Using an Array

Here is the same code as above, but using an array instead of a `Vec`:

```rust
use std::ops::Index;

pub struct Array1<T, const N: usize> {
    first: T,
    rest: [T; N],
}

#[macro_export]
macro_rules! array1 {
    // Special case for a single element
    [$x:expr] => {
        Array1::<_, 0> {
            first: $x,
            rest: [],
        }
    };
    [$x:expr, $($xs:expr),+ $(,)?] => {
        {
            // Get the number of elements, N,
            // in `rest` at compile-time.
            const N: usize = [$($xs),+].len();
            Array1::<_, N> {
                first: $x,
                rest: [$($xs),+],
            }
        }
    };
    [] => {
        compile_error!("array1! requires at least one element")
    };
}

impl<T, const N: usize> Index<usize> for Array1<T, N> {
    type Output = T;

    fn index(&self, index: usize) -> &Self::Output {
        match index {
            0 => &self.first,
            i => &self.rest[i - 1],
        }
    }
}
```

Note that we needed to introduce a special case for a single element.
That's because we need to know the value `N` for our type parameter, but
we can only do so if the macro is called with at least two elements.

Our trait implementations now expect a `const` parameter, e.g.:

```rust
impl<const N: usize> Index<usize> for Array1<N> {
    type Output = &'static str;

    fn index(&self, index: usize) -> &Self::Output {
        match index {
            0 => &self.first,
            // We can use `index - 1` because we know that
            // `index` is at least 1.
            i => &self.rest[i - 1],
        }
    }
}
```

The unit tests are the same as before.

I like the fact that this avoids any runtime overhead, 
which can be helpful in memory-constrained environments or in situations
where dynamic allocation is not possible.

It depends on the use-case to decide whether this is a better approach than
using a `vec1`. 

## Further Improvements

One could think of a few ways to add more checks. For example, since we know
that Kafka brokers get represented as URLs, we could also enforce that invariant
at compile-time; but we'll leave it at that for now.

## Conclusion

In this post, we saw how the type system can be used to 
enforce invariants at compile-time. 
Rust has great support for type-driven design, which can help you write more
robust and idiomatic code.
Always be on the lookout for ways to let the type-system guide you towards
stronger abstractions. 

You might also be interested in my previous post on [making illegal states
unrepresentable in Rust](/blog/illegal-state).


