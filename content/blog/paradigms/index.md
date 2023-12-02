+++
title = "Navigating Programming Paradigms in Rust"
date = 2023-12-02
template = "article.html"
draft = true
[extra]
series = "Idiomatic Rust"
reviews = [
    { link = "https://www.hannobraun.com/", name = "Hanno Braun" },
    { link = "https://github.com/guilliamxavier", name = "Guilliam Xavier"},
]
+++

Rust is a multi-paradigm programming language, accommodating imperative,
object-oriented, and functional programming styles. The choice of style often
depends on a developer's background and the specific problem they're addressing.

With Rust attracting developers from varied backgrounds like C++, Java, Python,
and Haskell, it has shaped its own *unique* set of styles and idioms. This
diversity is a strength, but it also leads to uncertainty about which style to
use in various scenarios.

As the [Rust Book explains](https://doc.rust-lang.org/book/ch17-00-oop.html):
> Many competing definitions describe what Object-Oriented Programming
> is, and by some of these definitions Rust is object-oriented.

However, it [also states](https://doc.rust-lang.org/book/ch13-00-functional-features.html):
> Rust’s design has taken inspiration from many existing languages and
> techniques, and one significant influence is functional programming.

These statements are not contradictory, but they do leave a lot of room for
interpretation and personal preference.

## Guiding Principles For Choosing The Right Paradigm

Rust is certainly influenced by object-oriented programming concepts. One factor
that sets it apart from other object-oriented languages is its composition-based
nature, as opposed to being inheritance-based. Its trait system is a core
component of this object-oriented design, a concept absent in languages like C++
and Java.

Similarly, Rust's design encourages patterns that align closely with functional
programming principles: immutability, iterator patterns, algebraic data types,
and pattern matching.

Just as Rust adopts certain object-oriented principles without being a purely
object-oriented language, it similarly embraces functional programming concepts
without being a purely functional language. It allows side effects everywhere
and does not strictly enforce [referential
transparency](https://en.wikipedia.org/wiki/Referential_transparency) — the
ability to replace an expression with its value without changing the program's
behavior.

In conclusion, providing some guidance on using different paradigms in Rust
might be helpful, especially for developers transitioning from other languages.
This article explores my personal decision-making process when choosing between
different paradigms in Rust, a process that has by now become almost second
nature.

## A Small Example

There is nothing wrong with simple `for` loops in Rust.

```rust
let mut sum = 0;
for i in 0..10 {
    sum += i;
}
```

But even in such a short example, we can see a discrepancy between the problem
we're trying to solve and the code we're writing: The intermediate values of
`sum` are irrelevant! We only care about the final result.

Compare that to a more functional version:

```rust
let sum: u32 = (0..10).sum();
```

In small examples like this, it might not matter much, but when we start working
with nested loops, we see that in the imperative approach, more lines are
dedicated to bookkeeping than to the actual problem. This causes the code's
accidental complexity (the unnecessary complexity we introduce ourselves)
to increase.

## A Slightly Bigger Example: Nested Loops

Let's consider a slightly bigger example. Imagine we had a list of programming
languages, their supported paradigms, and the number of production users for
each language. The task is to find the top five languages that support
functional programming and have the most users.

```rust
// All data is made up for the sake of this example! We love you, Haskell.
let languages = vec![
	Language::new("Rust", vec![Paradigm::Functional, Paradigm::ObjectOriented], 100_000),
	Language::new("Go", vec![Paradigm::ObjectOriented], 200_000),
	Language::new("Haskell", vec![Paradigm::Functional], 5_000),
	Language::new("Java", vec![Paradigm::ObjectOriented], 1_000_000),
	Language::new("C++", vec![Paradigm::ObjectOriented], 1_000_000),
	Language::new("Python", vec![Paradigm::ObjectOriented, Paradigm::Functional], 1_000_000),
];
```

Here is a *painfully* explicit solution using nested `for` loops:

```rust
// Filter languages to keep only the functional ones
let mut functional_languages = vec![];
for language in languages {
	if language.paradigms.contains(&Paradigm::Functional) {
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

This is a *very verbose*, imperative solution. We mutate the vector in-place and
destroy the intermediate results in the process. While it's not incorrect, I
would argue that it's not the most idiomatic Rust code either.

In practice, you would probably reach for a few more helper methods from the
standard library:

```rust
let mut top_languages = vec![];
for language in languages {
	if language.paradigms.contains(&Paradigm::Functional) {
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
top_languages.retain(|language| language.paradigms.contains(&Paradigm::Functional));
```

We still use a mutable variable, but now the code looks more succinct. `retain`
is a higher-order method that takes a closure as an argument, so the code
naturally became a little more functional. Let's continue down this path and
see where it takes us next.

```rust
let mut top_languages = languages.clone();
top_languages.sort();

let top_languages: Vec<Language> = top_languages
    .into_iter()
    // Only keep functional languages
    .filter(|language| language.paradigms.contains(&Paradigm::Functional))
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
    .filter(|language| language.paradigms.contains(&Paradigm::Functional))
    // Sort our languages in descending order of popularity.
    .sorted_by_key(|lang| Reverse(lang.users))
    // Keep only the top 5 languages
    .take(5)
    // Collect the results into a new vector
    .collect();
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=8c1d45de856b6a7980ea48ebeaf43290))

Sorting the entire list (even if it's filtered) to extract just the top 5
elements seems somewhat inefficient. This highlights a limitation in Rust
compared to C++, which offers a
[partial_sort](https://en.cppreference.com/w/cpp/algorithm/partial_sort)
function in its standard library. While Rust doesn't have an equivalent in std,
there are third-party crates. Alternatively, a [BinaryHeap](https://doc.rust-lang.org/std/collections/struct.BinaryHeap.html)
can be used. 

To me, this solution is easier to reason about. The operations are
neatly aligned below each other, and the code reads like a description of what
we're trying to achieve. I do admit, however, that it takes some getting used
to, especially if you're not familiar with functional programming patterns.

One could say that I hand-picked a problem that is well-suited for functional
programming, and that is certainly the case. The truth is, that this way of
method chaining just feels natural after a while &mdash; especially for ad-hoc
transformations on immutable data structures.

There are a few reasons for this:

* **Readability**: The steps are easy to follow.
* **Library Support**: The Rust standard library and external crates provide
  many helpful combinators for iterators, which play nicely with immutable data structures.
* **Efficiency**: Under the hood, methods like `map` and `filter` create new
  iterators that operate on the previous iterator and do not incur any allocations.
  The actual computations (like adding 1 or filtering even numbers) are only
  executed when the final iterator is consumed, in this case by
  the `collect` method. The `collect` method makes a single allocation to store the
  results in a new vector. Our higher-level abstractions incur no runtime
  overhead.
* **Parallelism**: The functional approach lends itself to parallel computation.
  Each chain of operations is independent of the others, allowing them
  to be executed simultaneously on modern hardware.

The result is clean, readable, and efficient code, which is why you'll see this
pattern a lot.

I always liked John Carmack's open-minded take on this:

> No matter what language you work in, programming in a functional style provides
> benefits. You should do it whenever it is convenient, and you should think hard
> about the decision when it isn't convenient. &mdash; [John Carmack](https://web.archive.org/web/20120427212006/www.altdevblogaday.com/2012/04/26/functional-programming-in-c/)

Carmack talks about *convenience* here. What is the tipping point where
functional programming becomes inconvenient? Let's explore that with a more
realistic example.

## Real-World Example: Filtering a List of Files

Here is a little Rust exercise: how would you list all XML files in a directory?
Before you continue, feel free to try this yourself. See
which style you would naturally lean towards. Why not try different approaches
and see which one you prefer?

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


Not great, not terrible.

We have to do some bookkeeping, and there are some minor paper cuts like `let f
= f?;` and the bit about `OsStr::to_str`, but overall it's fine. The paper cuts
are due to the *inherent* complexity of the problem: dealing with the
possibility of errors and the fact that the file extension might not be valid
UTF-8 on all platforms.

As the [documentation for
`OsStr`](https://doc.rust-lang.org/std/ffi/struct.OsString.html) explains:

* On Unix systems, strings are often arbitrary sequences of non-zero bytes, in
  many cases interpreted as UTF-8.
* On Windows, strings are often arbitrary sequences of non-zero 16-bit values,
  interpreted as UTF-16 when it is valid to do so.

The astute reader might have noticed that we don’t check if the path is
actually a file before we check the extension. This is done in the interest of
brevity.

### Functional Style

Let's see how we can solve this problem in a more functional style:

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

This implementation is arguably more streamlined. It maps directory
entries to paths, filters out non-XML files, and collects the results, all
without needing mutable variables or conditional branching.

That said, the solution also has its drawbacks.
Most importantly, it is not equivalent to the imperative version.
That is because `filter_map(Result::ok)` filters out all errors.
Whether we want to ignore errors depends on the use case;
it is a tradeoff between correctness and ergonomics.
In production code, we should at least log all errors, though.

So far, I would still lean towards the functional version, but let's see
how both approaches hold up as we add more complexity.

### Making Filtering More Generic

What if we wanted to filter by arbitrary file attributes?
For instance, we might want to find all files with a given prefix or extension.

We could introduce a new parameter, `valid`, which would be a function that
takes a `Path` and returns a `bool`. (This is also known as a *predicate* in
functional programming.)

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

This is a generic function that can be used for many different use cases.
Higher-order functions like this are a typical pattern in functional programming
and are also available in Rust.

The imperative version, while concise, now incorporates a higher-order function,
demonstrating that the line between functional and imperative programming is
often blurry:

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

Let's go one more step further.

So far, our solution only works for a single directory. What if we wanted to
*recursively* filter a directory and all its subdirectories for files?

First, the (mostly) imperative version with mutable state:

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

While we have one more level of nesting, the imperative version holds up
reasonably well.

Next, the functional version:

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

We're dealing with an iterator of iterators here, so we need to flatten it to
get a single iterator of paths with the help of `flat_map`. However, this also
means that we need to return a vector of paths in all cases, even if it's empty.
The `unwrap_or_default` is a symptom of this.

I will let you be the judge of which version you prefer.

Either way, this is where I feel the flow of logic is in need of improvement.
What I want is better encapsulation and modularity to keep
the complexity in check. Rust allows us to seamlessly transition to an
object-oriented style to do just that.

### Transitioning to Object-Oriented Rust

In contrast to the functional and imperative examples discussed earlier,
let's introduce a new struct, `FileFilter`, which encapsulates the logic for
filtering files and file iteration.

```rust
pub struct FileFilter {
    predicates: Vec<Box<Predicate>>,
    start: Option<PathBuf>,
    stack: Vec<fs::ReadDir>,
}
```

Each `FileFilter` object carries its state: a collection of predicates for
filtering, a starting path, and a stack of directories for iteration. 

#### Adding Filters

In functional programming, we leveraged the power of iterators and closures to
filter files. In the imperative style, we directly manipulated vectors with
loops and conditions. The FileFilter, however, abstracts these details away.

Consider the `add_filter` method:

```rust
pub fn add_filter(mut self, predicate: impl Fn(&Path) -> bool + 'static) -> Self {
    self.predicates.push(Box::new(predicate));
    self
}
```

This allows us to easily add multiple filters by chaining calls &mdash;
something that was previously closely coupled with the iteration logic.

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

What truly showcases the OOP approach in Rust is the implementation of the
`Iterator` trait for `FileFilter`:

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

In doing so, `FileFilter` becomes a building block that neatly integrates
with Rust's powerful iterator ecosystem and can be used in all the same places
as any other iterator. This design allows for complex iteration logic to be
encapsulated
*within* the object, abstracting away the details from the user.

You can find the full implementation of `FileFilter` [on
GitHub](https://github.com/corrode/filefilter) or [on the Rust
Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=671cc691f748dcf79db59e3b1ec96786).
The code was closely modeled after the excellent
[Walkdir](https://github.com/BurntSushi/walkdir) crate, which I recommend for
production use.

#### Encapsulation and Reusability

The `FileFilter` example illustrates how OOP in Rust can lead to solid
encapsulation and modularity. Unlike the earlier examples where the logic for
filtering files was tightly coupled with iteration, we now separate
the *what* (the predicates) from the *how* (the iteration and filtering logic).
The trait system allows us to easily integrate our custom iterator with the
rest of the ecosystem.
Having these tools at our disposal makes the code more composable and reusable.

## Summary

Rust is a multi-paradigm language. Mixing different styles is not only possible, but encouraged!
This can also be seen by taking a look at [Rust's key influences on its language design](https://doc.rust-lang.org/reference/influences.html).
Influences as diverse as C++, Haskell, OCaml, and Erlang have shaped Rust's
design. In the beginning, Rust was even more functional in nature, but it has since
evolved into a more balanced language.

The question is where to draw the line between different programming paradigms.

Here are my personal rules of thumb:

* **Leverage functional patterns for data transformations.** Especially within
  smaller scopes like functions and closures, functional methods such as
  mapping, filtering, or reducing can make your code both concise and clear.
* **Embrace object-oriented patterns for organization.** For organizing larger
  applications, consider object-oriented constructs. Using structs or
  enums can encapsulate related data and functions, providing a clear structure.
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
  benefits not only your future self, but also your colleagues who might work on
  the same codebase.

Lastly, avoid bias towards any particular paradigm. Don't prematurely
optimize for performance at the cost of readability. The real bottleneck
might be elsewhere. Measure first, then optimize.
It's not unusual for the most elegant solution to also be the fastest.
