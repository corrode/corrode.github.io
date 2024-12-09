+++
title = "Compile-Time Invariants in Rust"
date = 2023-08-27
updated = 2024-07-12
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = [
    { name = "Guilliam Xavier", url = "https://github.com/guilliamxavier" },
]
resources  = [
    "The [nonempty](https://github.com/cloudhead/nonempty) is a production-ready implementation of a non-empty list.",
]
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
fn connect_to_kafka(brokers: Vec<&str>) -> Result<KafkaClient, Box<dyn Error>> { 
    if brokers.is_empty() {
        return Err("At least one Kafka broker is required");
    }
    // Connect to brokers
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
**If in doubt, lean into the type system to enforce invariants at compile-time.**

An invariant is a condition that must always hold true. You want to enforce
these invariants as early as possible.

I recently learned about the term [type-driven
development](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/),
a practice that emphasizes the use of types to ensure program correctness.

To see how it works, let's try to implement a basic version of `vec1` ourselves.

## The `vec1` macro

Let's create a macro that behaves like `vec!`, but doesn't allow an empty vector.

The macro handles two cases:
- The first case matches a single element, followed by zero or more elements.
- The second case matches an empty vector and will panic at compile-time.

```rust
#[macro_export]
macro_rules! vec1 {
    // The first element is mandatory, 
    // while additional elements are optional (denoted by the `*`).
    // Just like `vec!`, we also allow a trailing comma (denoted by the `?`).
    [$x:expr $(, $xs:expr)* $(,)?] => {
        // Just create an ordinary `Vec`
        vec![$x, $($xs),*]
    };
    [] => {
        compile_error!("vec1! requires at least one element")
    };
}

fn main() {
    // This works
    let _ = vec1!["Hello", "World"];

    // This will fail to compile, which is what we want.
    let _ = vec1![];
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=6449703583b75ea1a76a763be9a0ba5f))

We use [`compile_error!`](https://doc.rust-lang.org/std/macro.compile_error.html),
from the standard library, which will always fail to compile with the given
error message.

This does indeed look like it solves our problem!  
However, it only does so superficially.
There's a nifty bug hiding in disguise. 

Since we return an ordinary `Vec`, the information that there must be at least one element is not a part of the type and the invariant will *not* be enforced by the type system later on.
We only handle the case where we construct the vector, but not when we use it.

Nothing keeps us from passing an empty vector to a function that requires at least one element. As a result, we would still need our `brokers.is_empty()` runtime check from above. Dolorous.

All of the hard work was for naught.

But, can we do better?

## Second Try: Implementing a `Vec1` type

The trick is to create a new type, `Vec1`, that behaves like an ordinary `Vec`,
but encapsulates the knowledge we just gained about our input. 

We do this by using two fields internally, `first` and `rest`:

```rust
// Note: Fields are not public, so we can enforce 
// invariants during construction
pub struct Vec1<T> {
    // The first element is mandatory
    first: T,
    // The rest is optional
    rest: Vec<T>,
}
```

Let's update our macro to return a `Vec1` instead of a `Vec`:

```rust
#[macro_export]
macro_rules! vec1 {
    [$x:expr $(, $xs:expr)* $(,)?] => {
        Vec1 {
            first: $x,
            rest: vec![$($xs),*],
        }
    };
    [] => {
        compile_error!("vec1! requires at least one element");
    };
}
```

To make our `Vec1` behave like any ordinary `Vec`, we can implement the same traits.

For example, we probably want to
[iterate](https://doc.rust-lang.org/std/iter/trait.IntoIterator.html) over the
elements:

```rust
impl<T> IntoIterator for Vec1<T> {
    type Item = T;
    type IntoIter = iter::Chain<iter::Once<T>, vec::IntoIter<Self::Item>>;

    fn into_iter(self) -> Self::IntoIter {
        iter::once(self.first).chain(self.rest)
    }
}
```

The associated `IntoIter` type is a bit tricky, but it's just a way to chain
together the first element and the rest of the elements without additional
allocations.

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

Note that we cannot simply implement `Deref` and `DerefMut` to
delegate to the underlying `Vec`, because that would allow us to mutate the
vector in a way that violates our invariant. Furthermore, we would need a custom
implementation of `remove` and `pop` to make sure that the vector is never
empty.

On the other hand, your own types are probably very specific to your use-case,
so you might not need to implement as many traits.

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

We now have a vector with at least one element.
If you want to play around with the code, [here's a link to the Rust
playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=316d933bfa7bf97eac0f4c8f152d5d61).

In any real-world scenario, you would probably want to use the `vec1` crate
instead of rolling your own implementation. And yes, the `vec1` crate 
implements all the necessary traits to make `Vec1` behave like a `Vec`
in a similar fashion to what we did above.

## Using a fixed-size array

If we assume that the list of Kafka brokers doesn't change at runtime (a
reasonable assumption, given that it's a configuration setting) we could also use
a [fixed-size array](https://doc.rust-lang.org/std/primitive.array.html).

By using an array, we can statically allocate the whole collection, which is
more efficient than using a `Vec` (a dynamically allocated datatype on the heap).

Here is the same code as above, but using an array instead of a `Vec`.

```rust
pub struct Array1<T, const N: usize> {
    first: T,
    rest: [T; N],
}

#[macro_export]
macro_rules! array1 {
    [$x:expr $(, $xs:expr)* $(,)?] => {
        Array1 {
            first: $x,
            rest: [$($xs),*],
        }
    };
    [] => {
        compile_error!("array1! requires at least one element")
    };
}
```

Note that the compiler will infer `N` (the number of elements in `rest`)
as well as `T` (the type of elements).

Our trait implementations now expect a `const` parameter, e.g.:

```rust
impl<T, const N: usize> Index<usize> for Array1<T, N> {
    // contents unchanged
}
```

The unit tests are the same as before.
[Here's the entire code](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=88011ae90e333502c352e7a50d21c632).

I like the fact that this avoids any runtime overhead, 
which can be helpful in memory-constrained environments or in situations
where dynamic allocation is not possible.

It depends on your use-case to decide whether this is a better approach than
using a `vec1`. It's fun how all of the guarantees can be enforced without any
runtime overhead, though!

## Further Improvements

One could think of a few ways to add more checks. For example, since we know
that Kafka brokers get represented as URLs, we could also enforce that invariant
at compile-time.

Which additional checks you want to add depends on your use-case.
For instance, if Kafka brokers are a central part of your application, you might want to create your own `KafkaBroker` type that enforce additional invariants. 

Here's a nice general rule of thumb:

> Model your data using the most precise data structure you reasonably can.  
> &mdash; [Alexis King](https://lexi-lambda.github.io/about.html) in [Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)

## Conclusion

Rust has great support for type-driven design, which can guide you towards
robust and idiomatic code to enforce invariants at compile-time. 

Always be on the lookout for ways to let the type-system guide you towards
stronger abstractions. 

If you liked this, you might also be interested in my previous post on [making illegal states unrepresentable in Rust](/blog/illegal-state).
