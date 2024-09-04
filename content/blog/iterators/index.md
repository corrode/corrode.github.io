+++
title = "Thinking in Iterators"
date = 2024-05-15
template = "article.html"
[extra]
updated = 2024-09-04
series = "Idiomatic Rust"
hero = "hero.svg"
hero_classes = "invert"
reviews = []
resources = [
    "[Rust Iterator Reference](https://doc.rust-lang.org/std/iter/trait.Iterator.html)",
    "[Iterator Tips and Tricks](https://blog.jetbrains.com/rust/2024/03/12/rust-iterators-beyond-the-basics-part-iii-tips-and-tricks/)",
]
+++

Python has this really neat feature called [list
comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions).

```python
# A list of bands
bands = [
    "Metallica",
    "Iron Maiden",
    "AC/DC",
    "Judas Priest",
    "Megadeth"
]

# A list comprehension to filter for bands that start with "M"
m_bands = [band for band in bands if band.startswith("M")]

# A list comprehension to uppercase the bands
uppercased = [band.upper() for band in m_bands]

# We get ["METALLICA", "MEGADETH"] 
```

List comprehensions are a concise way to create lists from other lists,
but they work with any iterable, like dicts!

```python
books = {
    "The Lord of the Rings": "J. R. R. Tolkien",
    "The Hobbit": "J. R. R. Tolkien",
    "Harry Potter": "J. K. Rowling"
}
tolkien_books = [
    book for book, author in books.items()
    if "Tolkien" in author
]
# tolkien_books = ["The Lord of the Rings", "The Hobbit"]
```

As a Pythonista, list comprehensions became second nature to me.
Their elegance is hard to beat. For a long time, I wished Rust had something
similar. It was one of the few things I *profoundly* missed from Python &mdash;
until I learned more about the philosophy behind Rust's iterator patterns.

## Enter Rust's Iterators

Rust has a notion of *chainable operations* on iterators, forming a pipeline where
each operation is applied to every element in sequence. Two of the most common
operations are [`map`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.map), which applies a function to each item, and [`filter`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.filter), which
selectively includes items that meet a certain condition.

Here's the equivalent Rust code for the first Python example above:

```rust
let bands = vec![
    "Metallica",
    "Iron Maiden",
    "AC/DC",
    "Judas Priest",
    "Megadeth",
];

let uppercased: Vec<_> = bands.iter()
                    .filter(|band| band.starts_with("M"))
                    .map(|band| band.to_uppercase())
                    .collect();

// uppercased = vec!["METALLICA", "MEGADETH"]
```

Sure, it's a tad more verbose than Python's list comprehensions, but oh, the
versatility!

For example, debugging an iterator chain is as simple as inserting an `inspect`
wherever you want to peek at the elements:

```rust
let uppercased: Vec<_> = bands
    .iter()
    .filter(|band| band.starts_with("M"))
    .inspect(|band| println!("Found band that starts with M: {band}"))
    .map(|band| band.to_uppercase())
    .collect();
```

Achieving the same effect with list comprehensions in Python is quite tricky.

I often find myself chaining iterator operations in Rust. And honestly? It's
pretty intuitive. Over time, I've even grown fond of its explicitness. (Or, you know,
maybe it's just some form of [Stockholm syndrome](https://en.wikipedia.org/wiki/Stockholm_syndrome).)

What I like the most is the flexibility of this pattern. Let me demonstrate!

## Collecting into different types

In Python, you can collect into different types like a [`set`](https://docs.python.org/3/tutorial/datastructures.html#sets):

```python
tolkien_books = {
    book for book, author in books.items()
    if "Tolkien" in author
}
# It's a set!
# tolkien_books = {"The Lord of the Rings", "The Hobbit"}
```

Note that the notation is irritatingly different from a list comprehension. Instead of square
brackets, we suddenly use curly braces now.

In contrast, to collect into different types in Rust, just specify the *type* you want to collect into; easy as cake! 

```rust
let books = HashMap::from_iter(vec![
    ("The Lord of the Rings", "J. R. R. Tolkien"),
    ("The Hobbit", "J. R. R. Tolkien"),
    ("Harry Potter", "J. K. Rowling"),
]);

// Collect into a vector
let tolkien_books: Vec<_> = books
    .iter()
    // Look at the second element of the tuple, which is the author
    .filter(|(_, author)| author.contains("Tolkien"))
    // Now only take the first element of the tuple, which is the book
    .map(|(book, _)| book)
    // Collect into a vector
    .collect();

// Alternatively, collect into a set.
// This works because `collect` can collect into any type that implements
// `FromIterator`, which `HashSet` does.
let tolkien_books: HashSet<_> = books
    .iter()
    .filter(|(_, author)| author.contains("Tolkien"))
    .map(|(book, _)| book)
    .collect();
```

What if we wanted to count the number of bands that start with the same letter?

```rust
let first_letters: HashMap<char, usize> = bands
    .iter()
    // Filter out bands that don't have a first letter.
    // (Yes, that's possible because we accept any string as input.)
    // `filter_map` is like `map` but it filters out `None` values.
    // If the band is empty, `chars().next()` will return `None`.
    .filter_map(|name| name.chars().next())
    // Start counting the occurrences of each letter
    .fold(HashMap::new(), |mut acc, c| {
        // Use the entry API to insert a new key or increment the value
        // https://doc.rust-lang.org/std/collections/hash_map/enum.Entry.html
        // Gets the entry for the character `c` and inserts 0 if it
        // doesn't exist
        *acc.entry(c).or_insert(0) += 1;
        acc
    });

// Printing the result
for (letter, count) in &first_letters {
    println!("{}: {}", letter, count);
}
```

Which gives us:

```text
M: 2
I: 1
A: 1
J: 1
```

Neat!

In Python, you would probably stop using list comprehensions altogether and
use the builtin `Counter` for this:

```python
from collections import Counter

# Note that we handle the case where a band 
# is an empty string with the `if len(band)` condition
first_letters = Counter([band[0] for band in bands if len(band)])
```

That's another API to learn and remember.

Rust also has a `Counter` implementation, but it lives outside the standard
library in the [counter](https://crates.io/crates/counter) crate.
Nevertheless, it fits right in &ndash; like a natural extension of the standard library.

```rust
use counter::Counter;

let first_letters: Counter<char, usize> = bands
    .iter()
    .filter_map(|name| name.chars().next())
    .collect();
```

We still use the same patterns that we used before and we didn't have
to refactor our code. It was all very seamless.
Again, we just changed the type we collect into!

Such a deep integration into the the iterator API would be much harder,
impossible even, in Python.

In Rust you get the best of both worlds: the flexibility of the ecosystem
and the native feel of the standard library.

## Behind the Scenes of `collect`

The convenience of collecting into a `Counter` is made possible by the fact that
`Counter` implements `FromIterator`.
That's all the compiler needs to know to be able to use `collect` with `Counter`.

Let's peek behind the curtain and see how it works.

Here is a code snippet from the `counter` crate:

```rust
impl<T, N> iter::FromIterator<T> for Counter<T, N>
where
    T: Hash + Eq,
    N: AddAssign + Zero + One,
{
    /// Produce a `Counter` from an iterator of items. This is called automatically
    /// by [`Iterator::collect()`].
    ///
    /// [`Iterator::collect()`]:
    /// https://doc.rust-lang.org/stable/std/iter/trait.Iterator.html#method.collect
    ///
    /// ```rust
    /// # use counter::Counter;
    /// # use std::collections::HashMap;
    /// let counter = "abbccc".chars().collect::<Counter<_>>();
    /// let expect = [('a', 1), ('b', 2), ('c', 3)].iter().cloned().collect::<HashMap<_, _>>();
    /// assert_eq!(counter.into_map(), expect);
    /// ```
    ///
    fn from_iter<I: IntoIterator<Item = T>>(iter: I) -> Self {
        Counter::<T, N>::init(iter)
    }
}
```

You can see that it just calls `Counter::init` where `init` is defined as:

```rust
impl<T, N> Counter<T, N>
where
    T: Hash + Eq,
    N: AddAssign + Zero + One,
{
    /// Create a new `Counter` initialized with the given iterable.
    pub fn init<I>(iterable: I) -> Counter<T, N>
    where
        I: IntoIterator<Item = T>,
    {
        let mut counter = Counter::new();
        counter.update(iterable);
        counter
    }

    /// Add the counts of the elements from the given iterable to this counter.
    pub fn update<I>(&mut self, iterable: I)
    where
        I: IntoIterator<Item = T>,
    {
        for item in iterable {
            let entry = self.map.entry(item).or_insert_with(N::zero);
            *entry += N::one();
        }
    }
}
```

That might look a little intimidating at first, but if you squint, you'll see that `Counter` uses a `for` loop to iterate over the elements of the iterator and also uses the `entry` API to insert a new key or increment the value; just like we did manually before.

The final, missing piece can be found in the Rust standard library
in the [`Iterator` trait](https://doc.rust-lang.org/std/iter/trait.Iterator.html):

```rust
fn collect<B: FromIterator<Self::Item>>(self) -> B
where
    Self: Sized,
{
    FromIterator::from_iter(self)
}
```

As you can see, the `collect` method is implemented for all types that implement
`FromIterator` and it's just a thin wrapper around [`FromIterator::from_iter`](https://doc.rust-lang.org/std/iter/trait.FromIterator.html).

The `Counter` crate implements `FromIterator` and therefore we can use 
it in combination with `collect`.
It's simple and effective &mdash; and without knowing all the details, it can
feel like magic.
In reality though, the flexibility is made possible by the trait system and the
iterator API.

If you want to learn more, the [`counter` source
code](https://github.com/coriolinus/counter-rs/blob/master/src/lib.rs) makes for
an interesting read.

What's important is that this integration needs to be done only once and then it
can be used by everyone. So as a mere user, you don't need to know how `collect`
works, just that it does. 


## Conclusion

It may be just a personal anecdote, but I feel like more experienced Rust
developers tend to prefer iterators over other methods of iteration like
`for` loops.

One reason might be that iterators are more versatile because they can be
chained and collected into custom types as we have seen
and they scale well with the complexity of the problem:
at no point are you forced to use a different API or pattern.

Another reason why I like iterator chains is that naming things is hard.
With iterators, you don't need to come up with a name for the intermediate
steps.

Just do me a favor and don't create pipelines which are super hard to read.
If the iterator chain is too long, or a step in the chain is longer than a few lines, there's no shame in breaking
it up into multiple steps.

My hope is that I was able to show you how powerful iterator patterns in Rust
are and they are a powerful stand-in for those list comprehensions you might 
know and love from Python.

I encourage you to explore the iterator API in Rust and see how you can use it
to make your code more expressive and concise. 
