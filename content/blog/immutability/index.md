+++
title = "Aim For Immutability in Rust"
date = 2023-09-21
updated = 2025-01-14
template = "article.html"
[extra]
series = "Idiomatic Rust"
revisions = """
An earlier version of this article chose different examples to illustrate the
benefits of immutability. These were a better fit for an article about
functional programming in Rust, so I replaced them.
"""
reviews = [
    { name = "llogiq", url = "https://llogiq.github.io/" },
]
+++

Some Rustaceans go to great lengths to avoid copying data &mdash; even once.

This is typically noticeable among those with a background in systems
programming, who are deeply conscious of performance and memory usage, sometimes
to the detriment of code readability. They make heavy use of `mut` to mutate
data in place and frequently try to sidestep `.clone()` calls at every turn in
an attempt to (prematurely) optimize their code.

I believe this approach is misguided. Immutability &mdash; which means once something
is created, it can't be changed &mdash; results in code that is easier to
understand, refactor and parallelize and it doesn't have to be slow either.

Immutability is an incredible complexity killer.

> Mutable objects are the new spaghetti code. And by that, I mean that you, eventually, with mutable objects, create an intractable mess. And encapsulation does not get rid of that. Encapsulation just means: well, I am in charge of this mess. But the real mess comes from this network that you create of objects that can change, and your inability to look at the state of a system and understand how it got there, how to get it there to test it next time. So it is hard to understand a program where things can change out from underneath you.
> &mdash; [Rick Hickey](https://github.com/matthiasn/talk-transcripts/blob/master/Hickey_Rich/ClojureConcurrency.md)

The `mut` keyword should be used sparingly; preferably only in tight scopes.

This article aims to convince you that **embracing immutability is central to
writing idiomatic Rust**.

## Immutability and State

As programmers, we think a lot about state.

The problem is, that humans are pretty bad at keeping track of state transitions
and multiple moving parts.
(That is, unless you're a chess grandmaster or the parent of a toddler, of course.)

> A large fraction of the flaws in software development are due to programmers
> not fully understanding all the possible states their code may execute in.  
> &mdash; [John Carmack](http://www.sevangelatos.com/john-carmack-on/)

Immutability can help us reduce the cognitive load of keeping track of state.
Instead of having to keep track of all the ways in which a variable can change,
we know that it can't change at all.

This brings us to Rust, a language that has chosen to prioritize immutability.

## Why Did Rust Choose Immutability By Default?

In Rust, variables are immutable by default, which means that once a
variable is bound to a value, it cannot be changed
(unless you [try excruciatingly hard to shoot yourself in the foot](https://stackoverflow.com/a/54242058/270334)).

```rust
let x = 42;
x = 23; // error: re-assignment of immutable variable `x`
```

Especially C and C++ programmers [tend to be surprised by that design
decision](https://users.rust-lang.org/t/is-immutability-by-default-worth-the-hassle/83668)
and their first Rust programs typically contain a lot of `mut` keywords.

In my opinion, choosing immutability was a good decision, because it helps
reduce mental overhead. It is a nod to [Rust's functional
roots](https://doc.rust-lang.org/reference/influences.html) and a consequence of
its focus on safety.

If the default was mutability, you'd have to check every
function to see if it changes the value of a variable.

Instead, Rust is very explicit about mutability.
It makes you write it out every time you create or pass a mutable variable.

```rust
fn main() {
    let mut x = 42;
    black_box(&mut x);
    println!("{}", x);
}

fn black_box(x: &mut i32) {
    *x = 23;
}
```

Oh, how awfully, painfully explicit!

Warning signs all over the place, which indicate that we are leaking state
changes to the outside world.

Compare that to C++:

```cpp
#include <iostream>

void black_box(int* x) {
    *x = 23;
}

int main() {
    int x = 42;
    black_box(&x);
    std::cout << x << std::endl;
}
```

Here we have to read the function body to see if it modifies our 
variable. We need to use the `const` keyword in C++ to indicate that a pointer
shouldn't modify the data it points to.

```cpp
void black_box(const int* x) {
    // This would be an error
    // *x = 23;
}
```

This is somewhat analogous to Rust's immutability, *but it is opt-in in C++*,
meaning you have to remember to use it.

In Rust, explicit mutability is part of the function signature, which makes it
easier to understand the implications of that function call at a glance. It even
warns you if something is mutable, but needn't be!

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

Rust's immutability-by-default is not just a syntactic choice; it's a deliberate
decision to promote code clarity and safety. By requiring explicit mutability,
Rust ensures developers are acutely aware of its implications. Especially in
concurrent programming, where mutable states can introduce complexity, this can be a lifesaver.

Mutability means state: a thing can be in one of many states. Immutability means no state: the thing won't change.
That's why immutability is a good default: most of the time you don't need all that state in the first place.

The real-world implications of immutability can be less straightforward.
Let's explore a concrete example to illustrate how an immutable approach can impact our design decisions for the better.

## Side Note: Function Signatures

In Rust, function signatures are very explicit about what a function does.
For instance, what is the difference between these two function signatures?

```rust
fn my_function1(a: &mut T) { ... }
fn my_function2(mut a: &T) { ... }
```

The first function takes an immutable reference to a mutable value.
This means that the value being pointed to can be modified through the reference, but the reference itself cannot be reassigned.

The second function takes a mutable binding to an immutable reference.
This means that the binding `a` can be reassigned to point to different values, but cannot modify any value it points to.

The difference is subtle, but it goes to show how Rust makes you think about mutability in a very explicit way.

You would typically use the first form (`a: &mut T`) when you need to modify the original value in place, like updating a struct's fields or modifying an element in a data structure.
The second form (`mut a: &T`) is less common and is used when you need to temporarily point to different values within a function, like when comparing multiple values or iterating through a collection of references.

## Controlling Mutability

Consider the following (problematic) implementation of a `Mailbox`:

```rust
pub struct Mailbox {
    /// The emails in the mailbox
    // Obviously, don't represent emails as strings in real code!
    // Use higher-level abstractions instead.
    emails: Vec<String>,
    /// The total number of words in all emails
    total_word_count: usize,
}

impl Mailbox {
    pub fn new() -> Self {
        Mailbox {
            emails: Vec::new(),
            total_word_count: 0,
        }
    }

    pub fn add_email(&mut self, email: &str) {
        self.emails.push(email.to_string());

        // Misguided optimization: Track the total word count
        let word_count: usize = email.split_whitespace().count();
        self.total_word_count += word_count;
    }

    pub fn get_word_count(&self) -> usize {
        self.total_word_count
    }

    // ... other methods ...
}
```

{% info(headline="Note") %}

This is a contrived example and not idiomatic Rust code! 
In a real-world scenario, we should use better abstractions, such as a `Message`
struct of some sort, which encapsulates the email's content and metadata, but
bear with me for the sake of the argument.

{% end %}

Note how `add_email` takes a `&mut self`, changing both the `emails` and
`total_word_count` fields. 

The idea here was to optimize for performance by keeping track of the total word
count on insertion, so that we don't have to iterate over all emails every time
we want to get the word count later. 
In what may have been a well-intentioned effort to optimize, `emails` and
`total_word_count` have now become tightly coupled.
We might refactor the code and forget to update the `total_word_count` field, causing bugs!

## Immutability In Purely Functional Programming

Issues with mutable state are less prevalent in purely functional programming
languages. For example, Haskell [doesn't even have mutable variables except when
using the state monad](https://wiki.haskell.org/Mutable_variable). Therefore,
our naive `Mailbox` type might look like this in Haskell:

```haskell
newtype Mailbox = Mailbox [String]

addEmail :: Mailbox -> String -> Mailbox
addEmail (Mailbox emails) email = Mailbox (email : emails)

getWordCount :: Mailbox -> Int
getWordCount (Mailbox emails) = sum $ map (length . words) emails
```

This returns a new `Mailbox` every time we add a message. 

To the keen-eyed systems programmer, this might sound appalling: "A fresh
Mailbox for each email? Really?" But before entirely dismissing that idea, remember that
in purely functional languages like Haskell, such practices are quite common
because they are quite efficient:

* In the `addEmail` function, you're prepending an email to the list with the
  `:` operator. Prepending to a linked list in Haskell is an `O(1)` operation,
  so it's quite performant. 
* While we're returning a new `Mailbox`, Haskell's lazy evaluation and the way
  it handles memory can mitigate some of the potential inefficiencies. For
  instance, unchanged parts of a data structure might be shared between the old
  and new versions.
* [Linked lists in Haskell are similar to "streams" in other languages](https://www.reddit.com/r/haskell/comments/w25rj7/how_does_haskell_internally_represent_lists/igpurex/),
  which helps put the performance expectations into perspective.

The functional approach pushed us towards a better design, because it made it
obvious that we don't need the `totalWordCount` field at all: 
It was much easier to write a version which calculates the sum on the fly
instead of mutating state.

The code is a lot easier to reason about and it might not even be slower. While
lazy evaluation has many advantages, its main drawback is that [memory usage
becomes hard to predict](https://wiki.haskell.org/Lazy_evaluation).

Which brings us back to Rust.

## Rust's Pragmatic Approach To Mutability

Rust does not have lazy evaluation, in part due to its focus on predictable
runtime behavior and its commitment to zero-cost abstractions. Thus, we can't
rely on the same optimizations as in languages that support lazy evaluation.

Instead, many Rust developers would probably opt for a middle ground:

```rust
pub struct Mailbox {
    emails: Vec<String>,
}

impl Mailbox {
    pub fn new() -> Self {
        Mailbox {
            emails: Vec::new(),
        }
    }

    pub fn add_email(&mut self, email: &str) {
        self.emails.push(email.to_string());
    }

    pub fn get_word_count(&self) -> usize {
        self.emails
            .iter()
            // In real code, `email` might have a `body` field with a
            // `word_count()` method instead
            .map(|email| email.split_whitespace().count())
            .sum()
    }

    // ... other methods ...
}
```

We mutate the original `Mailbox`, while now avoiding the `total_word_count`
field from the original code.
We don't carry the extra state around, and we calculate the word count on the
fly when needed.

The compiler prevents multiple
mutable references to the same data, making this approach safe.

Our Haskell example wasn't a mere detour; it highlighted how an immutable
mindset can often lead to stronger application design, even outside purely
functional contexts. We should strive to embrace immutability in Rust as well.

## A Word On Performance

In case counting the words becomes expensive, an alternative would be to
refactor the the code such that `add_email` takes a `Mail` struct, which contains
the metadata:

```rust
pub struct Mail {
    body: String,
    // Cache word count for faster access
    word_count: usize,
}

impl Mail {
    pub fn new(body: &str) -> Self {
        Mail {
            body: body.to_string(),
            word_count: body.split_whitespace().count(),
        }
    }

    pub fn word_count(&self) -> usize {
        self.word_count
    }
}
```

Then our `get_word_count` method could look like this:

```rust
pub fn get_word_count(&self) -> usize {
    self.emails.iter().map(|email| email.word_count()).sum()
}
```

Even in this case, we don't need any mutable state to implement the global word
count. Our intuition should be finding better abstractions, not mutating state.

## Summary

### Move instead of `mut`

Lean into Rust's ownership model to avoid mutable state.

It is safe to move variables into functions and structs, so use that to your
advantage. This way you can avoid `mut` in many cases and avoid
copies, which is especially important for large data structures.

## Don't Be Afraid Of Copying Data.

If you have the choice between a lot of `mut` and a few `.clone()` calls,
copying data is not as expensive as you might think. 

As computers get more cores and memory becomes cheaper, the benefits of
immutability outweigh the costs: 
especially in distributed systems, synchronization and coordination of
mutable data structures is hard and has a runtime cost.
Immutability can help you avoid a lot of headaches.

[Don't worry about a few `.clone()` calls here and there.](http://xion.io/post/code/rust-borrowchk-tricks.html) Instead, write code that is easy to understand and maintain.

The alternative is often to use locks and these have a runtime cost, too.
On top of that, they are a common source of deadlocks.

## Immutability Is A Great Default

Immutable code is easier to test, parallelize, and reason about. It's also
easier to refactor, because you don't have to worry about side effects.

Where [C/C++ requires you to explicitly declare things as immutable](https://stackoverflow.com/a/29682542/270334), Rust requires you to explicitly declare things as mutable, making everything else immutable by default.

Rust pushes you towards immutability and offers `mut` as an opt-in escape hatch
for hot paths and tight loops. Many (perhaps most) other languages do the exact
opposite: they use mutability as the default and require you to consciously 
choose immutability.

## Limit Mutability To Tight Scopes

Good code keeps mutable state short-lived, making it easier to reason about.
The use of `mut` should be the exception, not the rule.
