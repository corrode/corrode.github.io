+++
title = "Navigating Programming Paradigms in Rust"
date = 2023-12-04
updated = 2026-07-20
template = "article.html"
draft = false
[extra]
series = "Idiomatic Rust"
reviews = [
    { name = "Hanno Braun", url = "https://www.hannobraun.com/" },
    { name = "Guilliam Xavier", url = "https://github.com/guilliamxavier" },
    { name = "Vlad Hategan", url = "https://vlad-onis.github.io/" },
]
+++

Rust supports several programming styles. You can write plain imperative code, build APIs around structs and traits, or lean on iterators and algebraic data types. Which style fits best depends on the problem and on the habits you bring from other languages.

That flexibility is useful, but it can also make Rust feel less obvious than languages with one dominant style. A C++ developer, a Java developer, a Python developer, and a Haskell developer may all reach for different Rust patterns.

The [Rust Book explains](https://doc.rust-lang.org/book/ch17-00-oop.html) that Rust can be called object-oriented under some definitions. It also points out Rust's [functional programming influences](https://doc.rust-lang.org/book/ch13-00-functional-features.html). Both statements are true. Rust borrowed from several traditions, then made its own tradeoffs.

## Choosing The Right Style

Rust has object-oriented pieces, but they do not look like classical inheritance. You usually compose behavior with data types and impl blocks. Traits provide shared behavior without forcing a class hierarchy.

Rust also makes functional patterns easy to use. Immutability, iterators, algebraic data types, and pattern matching all show up in everyday Rust.

At the same time, Rust is not a pure functional language. Side effects are allowed, mutable state is normal when it helps, and Rust does not enforce [referential transparency](https://en.wikipedia.org/wiki/Referential_transparency).

The useful question is not which camp Rust belongs to. The useful question is which style makes a particular piece of code easier to understand and change. This article shows the decision process I use.

## A Small Example

There is nothing wrong with simple `for` loops in Rust.

```rust
let mut sum = 0;
for i in 0..10 {
    sum += i;
}
```

But even in such a short example, we can see a discrepancy between the problem
we're trying to solve and the code we're writing. The intermediate values of
`sum` are irrelevant! We only care about the final result.

Compare that to a more functional version:

```rust
let sum: u32 = (0..10).sum();
```

In a small example, this barely matters, but with nested loops, the bookkeeping starts to take over. More lines describe how to move data around than what result we want. That is accidental complexity, and even small amounts cost attention.

## A Slightly Bigger Example: Nested Loops

Let's use a slightly bigger example. Imagine a list of programming languages, the styles they support, and the number of production users for each language. The task is to find the five most-used languages that support functional programming.

```rust
// All data is made up for the sake of this example! We love you, Haskell.
let languages = vec![
    Language::new("Rust", vec![Style::Functional, Style::ObjectOriented], 100_000),
    Language::new("Go", vec![Style::ObjectOriented], 200_000),
    Language::new("Haskell", vec![Style::Functional], 5_000),
    Language::new("Java", vec![Style::ObjectOriented], 1_000_000),
    Language::new("C++", vec![Style::ObjectOriented], 1_000_000),
    Language::new("Python", vec![Style::ObjectOriented, Style::Functional], 1_000_000),
];
```

Here is a *painfully* explicit solution using nested `for` loops:

```rust
// Filter languages to keep only the functional ones
let mut functional_languages = vec![];
for language in languages {
    if language.styles.contains(&Style::Functional) {
        functional_languages.push(language);
    }
}

// Sort the functional languages by the number of users in descending order
for i in 1..functional_languages.len() {
    let mut j = i;
    while j > 0 && functional_languages[j].users > functional_languages[j - 1].users {
        functional_languages.swap(j, j - 1);
        j -= 1;
    }
}

// Keep only the top 5 languages
while functional_languages.len() > 5 {
    functional_languages.pop();
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=f9b28b96acde1f9d11e8dd5957539826))

This imperative version is verbose. It mutates the vector in place and throws away intermediate results as it goes. It works, but it is not how I would usually write this in Rust.

In practice, you would probably reach for a few more helper methods from the
standard library:

```rust
let mut top_languages = vec![];
for language in languages {
    if language.styles.contains(&Style::Functional) {
        top_languages.push(language);
    }
}

// Sort our languages in descending order of popularity.
// This line is already somewhat functional in nature.
top_languages.sort_by_key(|lang| std::cmp::Reverse(lang.users));

top_languages.truncate(5);
```

Since we're consuming `languages` anyway, we might as well be a little more
concise when filtering:

```rust
let mut top_languages = languages;
top_languages.retain(|language| language.styles.contains(&Style::Functional));
```

We still use a mutable variable, but the code is shorter. `retain` takes a closure, so the code has already moved a little toward a functional style. Let's keep going.

```rust
let mut top_languages = languages.clone();
top_languages.sort();

let top_languages: Vec<Language> = top_languages
    .into_iter()
    // Only keep functional languages
    .filter(|language| language.styles.contains(&Style::Functional))
    // Keep only the top 5 languages
    .take(5)
    // Collect the results into a vector
    .collect();
```

Or, if external crates are an option, we could use `sorted_by_key` from
[`itertools`](https://docs.rs/itertools/latest/itertools/trait.Itertools.html#method.sorted_by_key)
to chain all intermediate operations:

```rust
let top_languages: Vec<Language> = languages
    .iter()
    // Only keep functional languages
    .filter(|language| language.styles.contains(&Style::Functional))
    // Sort our languages in descending order of popularity.
    .sorted_by_key(|lang| Reverse(lang.users))
    // Keep only the top 5 languages
    .take(5)
    // Collect the results into a new vector
    .collect();
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=8c1d45de856b6a7980ea48ebeaf43290))

Sorting the whole filtered list just to keep five elements can be wasteful. C++ has [`partial_sort`](https://en.cppreference.com/w/cpp/algorithm/partial_sort) in its standard library. Rust does not have the same operation in `std`, though third-party crates can fill the gap. A [BinaryHeap](https://doc.rust-lang.org/std/collections/struct.BinaryHeap.html) is another option.

I still find this version easier to reason about. The operations line up under each other, and the code reads like a description of the result. It can feel strange at first if you are new to iterator-heavy Rust.

Admittedly, I did pick a problem that fits functional code well.
But I find that method chains start to feel natural when you are doing ad-hoc transformations on immutable data.

There are a few reasons for that: 

* The steps are easy to follow.
* The standard library and crates provide iterator adapters that work well with immutable data.
* Methods like `map` and `filter` build lazy iterators, so they do not allocate by themselves. Work happens when the iterator is consumed. In this example, `collect` performs the allocation for the final vector.
* Independent chains can often be moved to parallel execution later.

[John Carmack put the tradeoff well](https://cbarrete.com/carmack.html): "No matter what language you work in, programming in a functional style provides benefits. You should do it whenever it is convenient, and you should think hard about the decision when it isn't convenient."

But can you take it too far?
Is there a point where functional Rust becomes inconvenient?
Let's try a more realistic example.

## Real-World Example: Filtering a List of Files

Here is a small Rust exercise: how would you list all XML files in a directory? Before reading on, try it yourself and notice which style you reach for first.

### Imperative Style

Here is my imperative solution:

```rust
fn xml_files(p: &Path) -> Result<Vec<PathBuf>> {
    let mut files = Vec::new();
    for f in fs::read_dir(p)? {
        // This line is necessary, because the file could have
        // been deleted since the call to `read_dir`.
        let f = f?;
        if f.path().extension() == Some(OsStr::new("xml")) {
            files.push(f.path());
        }
    }
    Ok(files)
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=f3314816d1584ea372e8cdf6bdccd426))


This version is fine. It has some bookkeeping, including `let f = f?;`, but that is not accidental complexity. Directory iteration can fail, and file extensions are not guaranteed to be valid UTF-8 on every platform.

As the [documentation for
`OsStr`](https://doc.rust-lang.org/std/ffi/struct.OsString.html) explains:

* On Unix systems, strings are often arbitrary sequences of non-zero bytes, in
  many cases interpreted as UTF-8.
* On Windows, strings are often arbitrary sequences of non-zero 16-bit values,
  interpreted as UTF-16 when it is valid to do so.

This example does not check whether the path is a file before checking the extension. I left that out to keep the example short.

### Functional Style

Here is the same problem written with iterator adapters:

```rust
fn xml_files(p: &Path) -> Result<Vec<PathBuf>> {
    let entries = fs::read_dir(p)?
        .filter_map(Result::ok)
        .map(|entry| entry.path())
        .filter(|path| path.extension() == Some(OsStr::new("xml")))
        .collect();

    Ok(entries)
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=448b6246dd4da2d1cd9b8cf1f4e1f09e))

This version maps directory entries to paths, filters out non-XML files, and collects the result without a mutable vector.

It also changes the behavior. `filter_map(Result::ok)` drops every error.

{% info(title="What is the difference between `filter` and `filter_map`?") %}
In Rust, `filter` takes a closure that returns a `bool` to decide whether to
include an element in the resulting iterator, whereas `filter_map` takes a
closure that returns an `Option<T>`.

For `filter_map`, if the closure returns `Some(value)`, that value is included
in the new iterator; if it returns `None`, the element is excluded. Essentially,
`filter_map` allows filtering and mapping in a single step.

{% end %}

Ignoring errors may be acceptable for a quick script, but production code should at least log them. We can use [`inspect`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.inspect) for that:

```rust
fn xml_files(p: &Path) -> Result<Vec<PathBuf>> {
    let entries = fs::read_dir(p)?
        // Logs each element of the iterator to stderr for debugging, then passes the value on.
        .inspect(|entry| {
            if let Err(e) = entry {
                eprintln!("Error: {}", e);
            }
        })
        .filter_map(Result::ok)
        .map(|entry| entry.path())
        .filter(|path| path.extension() == Some(OsStr::new("xml")))
        .collect();

    Ok(entries)
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=f3bd287c8c82ff661b9ec9616b5514a9))


At this point I still prefer the iterator version. Now let's add more requirements.

### Making Filtering More Generic

What if we want to filter by arbitrary file attributes, such as a prefix or extension?

We can add a `valid` parameter: a function that takes a `Path` and returns a `bool`. Functional programmers call this a predicate.

```rust
fn filter_files<F>(p: &Path, valid: &F) -> Result<Vec<PathBuf>>
where
    F: Fn(&Path) -> bool,
{
    Ok(fs::read_dir(p)?
        .filter_map(Result::ok)
        .map(|entry| entry.path())
        .filter(|path| valid(path))
        .collect())
}
```

This generic function works for many filters. It also shows that higher-order functions are a normal part of Rust.

The imperative version can take the same `valid` function. The line between imperative and functional Rust is blurry:

```rust
fn filter_files<F>(p: &Path, valid: &F) -> Result<Vec<PathBuf>> 
where
    F: Fn(&Path) -> bool,
{
    let mut files = Vec::new();
    for f in fs::read_dir(p)? {
        let f = f?;
        if valid(&f.path()) {
            files.push(f.path());
        }
    }
    Ok(files)
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=d89eb67e614ad324de56b7d94204dc7f))

### Recursively Filtering Directories For Files

Let's go one step further.

So far, the function only handles one directory. What if we want to recurse into subdirectories?

Here is the mostly imperative version with mutable state:

```rust
fn filter_files<F>(p: &Path, valid: &F) -> Result<Vec<PathBuf>>
where
    F: Fn(&Path) -> bool,
{
    let mut files = Vec::new();
    for f in fs::read_dir(p)? {
        let f = f?;
        if f.path().is_dir() {
            // Recursively filter the directory
            files.extend(filter_files(&f.path(), valid)?);
        } else if valid(&f.path()) {
            files.push(f.path());
        }
    }
    Ok(files)
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=e55738f928e70d9f42e2408e10166e1e))

This adds one level of nesting, but the imperative version still holds together.

Now compare the iterator version:

```rust
fn filter_files<F>(p: &Path, valid: &F) -> Result<Vec<PathBuf>>
where
    F: Fn(&Path) -> bool,
{
    Ok(fs::read_dir(p)?
        .filter_map(Result::ok)
        .map(|entry| entry.path())
        .flat_map(|path| match path {
            p if p.is_dir() => filter_files(&p, valid).unwrap_or_default(),
            p if valid(&p) => vec![p],
            _ => vec![],
        })
        .collect())
}
```

Now we have an iterator that can produce many paths for one input path, so we reach for `flat_map`. That forces each branch to return a collection, even when it has nothing to return. The `unwrap_or_default` is a smell here.

This is the point where I stop trying to force everything into one chain. The code needs a boundary around the traversal state. Rust gives us a good way to do that with a struct and an `Iterator` implementation.

### Transitioning to Object-Oriented Rust

Instead of pushing the traversal into a longer function, introduce a `FileFilter` struct that owns the filtering and iteration state.

```rust
pub struct FileFilter {
    predicates: Vec<Box<Predicate>>,
    start: Option<PathBuf>,
    stack: Vec<fs::ReadDir>,
}
```

Each `FileFilter` value stores the predicates, the starting path, and the directory stack.

A predicate is defined like this:

```rust
type Predicate = dyn Fn(&Path) -> bool;
```

You might be surprised to see a `dyn` here. The [Rust Reference](https://doc.rust-lang.org/reference/types/closure.html) says each closure has its own anonymous type. Even two identical closures have different types.

To store several closures in one `Vec`, we use a trait object with dynamic dispatch. Boxing each closure gives us a `Box<Predicate>` (`Box<dyn Fn(&Path) -> bool>`), so different closure types can live in the same collection.

#### Adding Filters

Earlier versions exposed the filtering loop directly. `FileFilter` hides that detail behind a small API.

Consider the `add_filter` method:

```rust
pub fn add_filter(mut self, predicate: impl Fn(&Path) -> bool + 'static) -> Self {
    self.predicates.push(Box::new(predicate));
    self
}
```

Now callers can add filters by chaining method calls. The filter setup is separate from the traversal code.

```rust
let filter = FileFilter::new()
    .add_filter(|path| {
        // check if path begins with "foo"
        path.file_name()
            .and_then(OsStr::to_str)
            .map(|name| name.starts_with("foo"))
            .unwrap_or(false)
    })  
    .add_filter(|path| path.extension() == Some(OsStr::new("xml")));
```

#### Iterator Implementation

The object-oriented part becomes useful when `FileFilter` implements `Iterator`:

```rust
impl Iterator for FileFilter {
    type Item = Result<PathBuf>;

    fn next(&mut self) -> Option<Self::Item> {
        // Iteration logic to filter entries.
        // This is outside the scope of this article
        // Check out the full implementation on GitHub
        // or on the Rust Playground
    }
}
```

With that implementation, `FileFilter` becomes a normal Rust iterator. Callers can chain it with the rest of the iterator ecosystem while the traversal logic stays inside the struct.

You can find the full implementation of `FileFilter` [on
GitHub](https://github.com/corrode/filefilter) or [on the Rust
Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=d0b5ce70c858b39151ca46cf9dc07369).
The code was closely modeled after the excellent
[Walkdir](https://github.com/BurntSushi/walkdir) crate, which I recommend for
production use.

#### Encapsulation and Reusability

The `FileFilter` example shows what object-oriented Rust is good at: encapsulation. We separate the predicates from the traversal machinery, then expose the result as an iterator. The trait system lets that custom iterator work with the rest of Rust.

## Summary

Rust works well when you mix styles deliberately. That should not be surprising. The language draws from [C++, Haskell, OCaml, Erlang](https://doc.rust-lang.org/reference/influences.html), and more.

I often use a functional core with an imperative shell. Small functions transform data. The outer code handles I/O and sequencing. Error reporting sits at the boundary. For larger parts of an application, I use Rust's type system to keep related data and behavior together.

My rules of thumb:

* Use object-oriented patterns for organization. Structs and enums are good places to keep related data. Traits are good boundaries between parts of the program.
* Use functional patterns for data transformations. Inside functions and closures, iterator adapters can make the data flow easier to read.
* Use imperative code when sequencing matters. Explicit loops are often clearer near I/O, mutation, performance-sensitive code, or low-level details. Keep that code in a small scope when you can.
* Prefer readability over allegiance to a style. Code that is easy to read and change usually beats code that follows one programming tradition perfectly.
* Measure before optimizing. The bottleneck may not be where you expect, and readable code is easier to tune once you know what matters.

Do not let your favorite style make the decision for you. Try the obvious version first, then refactor when the code starts to become unwieldy. 



