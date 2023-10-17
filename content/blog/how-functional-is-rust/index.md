+++
title = "How Functional is Rust?"
date = 2023-10-15
template = "article.html"
draft = true
[extra]
series = "Idiomatic Rust"
+++

Rust is a multi-paradigm programming language, accommodating imperative,
object-oriented, and functional programming styles. The choice of style often
hinges on a developer's background and the specific problem they're addressing.

With Rust attracting developers from varied backgrounds like C++, Java, Python,
and Haskell, it has shaped its own unique set of styles and idioms. This
diversity is a strength, but it can also spark a question:  

> To what degree does idiomatic Rust embrace functional programming?

Let's establish some ground rules first:

* Rust is **not** a pure functional programming language: for instance, it permits
  side effects everywhere, and Rust doesn't strictly enforce [referential
  transparency](https://en.wikipedia.org/wiki/Referential_transparency) (the
  ability to replace an expression with its value without changing the program's
  behavior).
* For the most part, it doesn't matter.

However, Rust's design encourages patterns that align closely with functional
programming principles: immutability, iterator patterns, algebraic data types,
and pattern matching, so some guidance around the use of functional patterns can
be helpful for developers coming from other languages. This article delves into
the functional aspects of Rust, demonstrating how to craft clean and efficient
code that aligns with Rust's best practices.

## Iteration

There is nothing wrong with simple `for` loops in Rust.

```rust
let mut sum = 0;
for i in 0..10 {
    sum += i;
}
```

But even in this short example, we can see a discrepancy between the problem
we're trying to solve and the code we're writing:
The intermediate values of `sum` are irrelevant. We only care about the final
value.

Compare that to the more functional version:

```rust
let sum: u32 = (0..10).sum();
```

In smaller examples such as this, it's might not be a big deal, but the moment
we deal with nested loops, we find that more lines are concerned
with bookkeeping rather than the actual problem at hand.

As an example, imagine you had a list of programming languages, their supported design patterns,
and the number of production users for each language. You want to find the
top 5 languages by number of users that support the functional programming
paradigm.

```rust
// The data is made up for the sake of this example!
let languages = vec![
    Language::new("Rust", vec![Paradigm::Functional, Paradigm::ObjectOriented], 100_000),
    Language::new("Go", vec![Paradigm::ObjectOriented], 200_000),
    Language::new("Haskell", vec![Paradigm::Functional], 5_000),
    Language::new("Java", vec![Paradigm::ObjectOriented], 1_000_000),
    Language::new("C++", vec![Paradigm::ObjectOriented], 1_000_000),
    Language::new("Python", vec![Paradigm::ObjectOriented, Paradigm::Functional], 1_000_000),
];
```


Here is a solution using a `for` loop:

```rust
let mut top_languages = vec![];
for language in languages {
    if language.paradigms.contains(&Paradigm::Functional) {
        top_languages.push(language);
    }
}

top_languages.sort_by(|a, b| b.users.cmp(&a.users));
top_languages.truncate(5);
```

Not the prettiest code, but it gets the job done. It requires a mutable variable
to keep track of the intermediate result.

Now compare that to the functional approach:

```rust
let top_languages = languages
    .iter()
    .filter(|language| language.paradigms.contains(&Paradigm::Functional))
    .sorted_by(|a, b| b.users.cmp(&a.users))
    .take(5)
    .collect::<Vec<_>>();
```

Arguably, this solution is easier to read and understand; at least
to users who are a bit familiar with functional programming patterns.

Naturally, I picked a problem that is well-suited for functional programming.
But, like many other Rust developers I know, I do find myself reaching for the
functional approach for method chaining whenever feasible. It just feels more
natural.

There are a few reasons for this:

* **Readability**: The operations are tidily aligned below each other.
* **Immutability**: The Rust standard library provides many helpful combinators for iterators,
  which play nicely with immutable data structures.
* **Efficiency**: Under the hood, methods like `map` and `filter` create new 
  iterators that operate on the previous iterator and do not incur any allocations.
  The actual computations (like adding 1 or filtering even numbers) are only 
  executed when the final iterator is consumed, in this case by
  the `collect` method. The `collect` method makes a single allocation to store the
  results in a new vector.
* **Parallelism**: The functional approach makes it easy to parallelize the
  computation with the [`rayon`](https://github.com/rayon-rs/rayon) crate.

The result is clean, readable, and efficient code, which is why you'll see this
pattern a lot in idiomatic Rust code.

Of course, this is a contrived example! It would be possible to find equally
valid cases where the functional approach is less readable than the imperative
one.

The question is where to draw the line.

## Real-world Example: Quicksort

Entire (useful!) algorithms can be written in a functional style and without a
single `mut` keyword in Rust.

Let's look at a more realistic example: sorting algorithms.

Quicksort is a sorting algorithm that works by recursively partitioning an array
around a pivot element (the "comparison" element), which gets arbitrarily chosen.

Elements smaller than the pivot are moved to the left of the pivot and elements
larger than the pivot are moved to the right of the pivot. This is repeated
until the array is sorted.

## Mutable Quicksort

Here is a typical quicksort implementation, which mutates the original input:

```rust
pub fn quicksort_mut<T: PartialOrd>(mut arr: Vec<T>) -> Vec<T> {
    if arr.len() <= 1 {
        return arr;
    }

    let pivot = arr.remove(0);
    let mut left = vec![];
    let mut right = vec![];

    for item in arr {
        if item <= pivot {
            left.push(item);
        } else {
            right.push(item);
        }
    }

    let mut sorted_left = quicksort_mut(left);
    let mut sorted_right = quicksort_mut(right);

    sorted_left.push(pivot);
    sorted_left.append(&mut sorted_right);

    sorted_left
}
```

Depending on your background, this code might either be straightforward or it
might look like a a clown riding a unicycle on a minefield: slightly irritating
and unnecessarily dangerous.

Since the algorithm mutates the original array, the program's state changes
throughout its execution, which demands a lot of mental gymnastics from the reader.

Nonetheless, I would probably have written a quicksort implementation like this
when I started learning Rust. It's a very direct translation of 
what the algorithm **does** on a lower level, which is what I was used to from
other languages.

## Immutable Quicksort

Here is an "immutable" version which doesn't use `mut` at all:

```rust
pub fn quicksort_partition<T: PartialOrd + Clone>(array: &[T]) -> Vec<T> {
    if array.len() <= 1 {
        return array.to_vec();
    }

    let pivot = &array[0];
    let (higher, lower): (Vec<_>, Vec<_>) = array[1..].iter().cloned().partition(|x| x > pivot);

    [
        quicksort_partition(&lower),
        vec![pivot.clone()],
        quicksort_partition(&higher),
    ]
    .concat()
}
```

It looks a lot more like what you'd expect from a functional programming
language.

To me, this version is a lot easier to reason about. I don't have to chase
mutations of variables throughout the code or worry about indices and loops.
Less code to understand and less room for bugs.

Coincidentally, it is also the version that is closer to
what the algorithm **does** on a higher level. It's a direct translation of the
algorithm's description:

1. If the array is empty or has only one element, it is already sorted.
2. Otherwise, pick the first element as the pivot.
3. Create two new arrays: One with all elements smaller than the pivot and one
   with all elements larger than the pivot.
4. Recursively sort the two new arrays and concatenate them with the pivot in
   the middle.

Note how similar this is to the initial description of the algorithm above.

## Side Note: Performance

Maybe the functional version made you a little uneasy. After all, we clone the
entire array in every recursive call. This is a lot of copying!
Isn't that inefficient?

You might be wondering:
Just how much slower is the immutable version compared to the mutable one?

To test this, I created a [benchmark](https://github.com/mre/quicksort_bench)
that would run both versions on a vector with 1 million random values.
Here are the results:

![Benchmark results](./quicksort.svg)

As you can see, the performance is about the same. Generally speaking,
functional code isn't inherently slower than its imperative counterpart. Resist
the urge to use iterative style purely for performance reasons. Instead, give
Rust the chance to optimize the code for you. The generated code might look very
similar to the imperative version.

## Summary

Here are my rules of thumb:

* **Leverage functional patterns for data transformations.** Especially within
  smaller scopes like functions and closures, functional methods such as
  mapping, filtering, or reducing can make your code both concise and clear.
* **Embrace Object-oriented patterns for structure.** For organizing larger
  applications or modules, consider object-oriented constructs. Using struct or
  enum can encapsulate related data and functions, providing a clear structure.
* **Use imperative style for granular control.** In scenarios where you're
  working close to the hardware, or when you need explicit step-by-step
  execution, the imperative style is often a necessity. It allows for precise
  control over operations, especially with mutable data. This style can be
  particularly useful in performance-critical sections or when interfacing with
  external systems where exact sequencing matters. However, always weigh its
  performance gains against potential readability trade-offs. If possible,
  encapsulate imperative code within a limited scope.
* **Prioritize readability and maintainability.** Regardless of your chosen
  paradigm, always write code that's straightforward and easy to maintain. It
  benefits not only your future self but also your colleagues who might work on
  the same codebase.