+++
title = "Aim for Immutability"
date = 2023-09-20
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

As programmers, we think a lot about state.
Is the user logged in? Can this edge-case ever occur?
Is the coffee pot empty again?

The problem is, that humans are pretty bad at keeping track of state.
(Unless you're a Chess Grandmaster or a parent of a toddler, that is.)  
We forget things, we make mistakes, we get distracted...
I get reminded of this every time I forget where I put my keys.

To make our lives easier, Rust has a few ways to help manage state.
If you follow some rules, you can write code that is easier to reason about for
me and you.

Before, we already talked about [making illegal states unrepresentable](/blog/illegal-state/).
Another simple rule is: **Aim for immutability**.
If a variable can be immutable, it should be.

That is the topic of this article.

## Immutability

In Rust, variables are immutable by default, which means that once a
variable is bound to a value, it cannot be changed.

```rust
let x = 42;
x = 13; // error: re-assignment of immutable variable `x`
```

Especially C programmers [tend to be surprised by that design
choice](https://users.rust-lang.org/t/is-immutability-by-default-worth-the-hassle/83668)
and their first Rust programs typically contain a lot of `mut` keywords.

I think **immutability is a great default**, because it helps reduce complexity.
If the default was mutability, you'd have to check every function call
to see if it changes the value of a variable.

```rust
x = 42;
black_box(x)
// Is x still 42? Who knows! Better check.
```

Rust is very explicit about mutability. It makes you write it out every time you
create or pass a mutable variable.

```rust
let mut x = 42;
black_box(&mut x);
// Is x still 42? Who knows! Better check.
```

...and it even warns you if something is mutable, but needn't be!

```rust
fn main() {
    let mut x = 42;
    black_box(x);
}
```

```rust
warning: variable does not need to be mutable
 --> src/main.rs:4:9
  |
4 |     let mut x = 42;
  |         ----^
  |         |
  |         help: remove this `mut`
  |
  = note: `#[warn(unused_mut)]` on by default
```

A lot more things can be immutable than you might think.
For example, I find it useful to return _new_ values from functions instead of
mutating existing ones.

```rust
let x = 42;
let y = do_something(x);
println!("{}", x); // x is still 42
println!("{}", y); // y is the "new" result of do_something
```

If you follow this principle, you'll find that you'll use `mut` a lot more sparingly.
Entire algorithms can be written without a single `mut` keyword.
Here is a _functional quicksort_ implementation that doesn't use `mut` at all:

```rust
fn quicksort<T: Ord + Clone>(array: &[T]) -> Vec<T> {
    if array.len() <= 1 {
        return array.to_vec();
    }

    let pivot = &array[0];
    let higher: Vec<T> = array[1..].iter().cloned().filter(|x| x > pivot).collect();
    let lower: Vec<T> = array[1..].iter().cloned().filter(|x| x <= pivot).collect();

    [quicksort(&lower), vec![pivot.clone()], quicksort(&higher)].concat()
}
```

To me, it's a lot easier to reason about this code than a mutable version. I
don't have to chase mutations of variables throughout the code or worry about
indices and loops to keep track of the current state of the program in my head.

The above algorithm can be summarized in four simple steps:

1. If the array is empty or has only one element, it is already sorted.
2. Otherwise, pick the first element as the pivot.
3. Create two new arrays: One with all elements smaller than the pivot and one
   with all elements larger than the pivot.
4. Recursively sort the two new arrays and concatenate them with the pivot in
   the middle.

Let's give it a spin:

```rust
fn main() {
    let array = vec![3, 2, -1, 1, 5, 4];
    let sorted_array = quicksort(&array);
    println!("{:?}", sorted_array); // [-1, 1, 2, 3, 4, 5]
}
```

## The Cost of Immutability

One reason why some people are hesitant to use immutability is _performance_.
The story goes a bit like that:
"Copying data requires allocations. Allocations cost time and memory. Therefore,
you should avoid copying data."

If you have a large enough data structure, you don't want to copy it every time
you want to change something; that's fair.

Just _how big_ does a data structure have to be before you should start
worrying about copies? And how many copies do you have to make for it to
actually matter?

To test this, I wrote a benchmark that copies a vector with 1 million random
values 100 times. Here is the code:

```rust
#![feature(test)]

extern crate test;

use test::{black_box, Bencher};
use rand::random;

#[bench]
fn copy_vector_100_times(b: &mut Bencher) {
    // Creating a vector of random values
    let vec: Vec<u32> = (0..1_000_000).map(|_| rand::random::<u32>()).collect();

    b.iter(|| {
        for _ in 0..100 {
            // Copy the vector and use black_box to avoid compiler optimizations
            let _copied_vec = black_box(vec.clone());
        }
    });
}
```

On my M1 Macbook Pro, this benchmark takes around 29,815,141 ns/iter (+/- 1,410,548).
**That's 29 milliseconds to copy a vector with 1 million values 100 times!
This means that you can copy a vector with 1 million values 3,354,068 times per second on
a consumer laptop!**

How many times do you need to copy a 4 MB data structure millions of times per
second?

Turns out, Computers are pretty good at copying things these days.

Besides! Immutable data structures might even _unlock_ performance optimizations
that you didn't think of before. For example, you can cache the result of a
function call, because you know that it will never change.

```rust
use std::collections::HashMap;

fn expensive_function(x: i32) -> i32 {
    println!("expensive_function({})", x);
    x * 2
}

fn main() {
    let mut cache = HashMap::new();
    let x = 42;
    let y = cache.entry(x).or_insert(expensive_function(x));
    println!("{}", y); // y is 84
    let y = cache.entry(x).or_insert(expensive_function(x));
    println!("{}", y); // y is still 84
}
```

Another nice property of immutable data structures is that they are easier to
share between threads, which helps with parallelism.
For instance, the above quicksort code can be trivially
be parallelized by using the [`rayon`](https://github.com/rayon-rs/rayon) crate.

```rust
use rayon::prelude::*;

pub fn quicksort_par<T: Ord + Clone + Sync + Send>(array: &[T]) -> Vec<T> {
    // ...
    let higher: Vec<T> = array[1..] .par_iter() .cloned() .filter(|x| x > pivot) .collect();
    let lower: Vec<T> = array[1..] .par_iter() .cloned() .filter(|x| x <= pivot) .collect();
    // ...
}
```

All we have to do is to use `par_iter` and add `Sync` and `Send` to the type bounds of the generic
type `T`. The `rayon` crate takes care of the rest.
With mutable data structures, this would be a lot more complicated as you'd need
to ensure that no two threads are trying to mutate the same piece of data
simultaneously. This requires synchronization primitives like
[locks](https://doc.rust-lang.org/std/sync/struct.Mutex.html),
[semaphores](https://doc.rust-lang.org/std/sync/struct.Barrier.html),
or [atomic operations](https://doc.rust-lang.org/std/sync/atomic/index.html),
which can introduce both performance overhead and complexity.

For example, imagine you had a mutable array that multiple threads were
attempting to sort. If two threads tried to swap elements at the same time
without proper synchronization, you could end up with data races, where the
outcome is unpredictable and might even corrupt your data. This requires you to
sprinkle your code with locks, which in turn can lead to other issues like
deadlocks if not handled carefully.

Note: This is _not_ a good example of parallelism, because the overhead of
spawning threads and distributing the work is probably larger than the performance gain.
The point is that parallelism is easy, because we don't have to worry about
mutability and shared state. Always profile your changes before and after.

As a nice bonus, you get code, which can be chained together neatly.
The Rust standard library provides a number of helpful combinators for iterators,
which play nicely with immutable data structures:

```rust
let v = vec![1, 2, 3].iter()
            .map(|x| x + 1)
            .filter(|x| x % 2 == 0)
            .collect::<Vec<_>>();
println!("{:?}", v); // v is [2, 4]
```

Under the hood, the `map` and `filter` methods create new iterators that operate on
the previous iterator. The actual computations (like adding 1 or filtering even
numbers) are only executed when the final iterator is consumed, in this case by
the `collect` method. The `collect` method then allocates memory to store the
results in a new vector. While this involves an allocation, the convenience and
expressiveness often make it a worthy trade-off, which is why you'll see this
pattern a lot in idiomatic Rust code.

## Conclusion

In summary, immutability is a great default, because it helps reduce complexity,
makes your code easier to reason about and can even unlock performance
optimizations.

The use of `mut` should be the exception, not the rule.
