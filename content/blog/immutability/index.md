+++
title = "Aim For Immutability"
date = 2023-09-21
template = "article.html"
[extra]
series = "Idiomatic Rust"
revisions = """
An earlier version of this article chose different examples to illustrate the
benefits of immutability. These were a better fit for an article about
functional programming in Rust, so I will use them in a future article.
"""
+++

Some Rustaceans go to great lengths to avoid copying data — even once.

This is typically noticeable among those with a background in systems
programming, who are deeply conscious of performance and memory usage, sometimes
to the detriment of code readability. They make heavy use of `mut` to mutate
data in place and frequently try to sidestep `.clone()` calls at every turn in
an attempt to (prematurely) optimize their code.

I believe this approach is misguided. Immutability &mdash; which means once something
is created, it can't be changed &mdash; results in code that is easier to
understand, refactor and parallelize. The `mut` should be used sparingly; 
preferably only in tight scopes.

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

Instead, Rust is very explicit about mutability. It makes you write it out every time you
create or pass a mutable variable.

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
Rust ensures developers are acutely aware of its implications, especially in
concurrent programming where mutable states can introduce complexity.

While immutability is often touted for its theoretical advantages, its
real-world application can be less straightforward. Let's explore a concrete
example to illustrate how an immutable approach can shape our design decisions
and can prevent anti-patterns like intertwined variables that often emerge over
a project's lifespan.

## Mutability and Object-Oriented Programming

Consider the following (problematic) implementation of a `Mailbox`:

```rust
pub struct Mailbox {
    emails: Vec<String>,
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
        let word_count: usize = email.split_whitespace().count();
        self.total_word_count += word_count;
        self.emails.push(email.to_string());
    }

    pub fn get_word_count(&self) -> usize {
        self.total_word_count
    }

    // ... other methods ...
}
```

{% info() %}

In a real-world scenario, we would probably have a `Message` struct of some sort,
which encapsulates the email's content and metadata, but for the sake of the example,
I've omitted it here.

{% end %}

Note how `add_email` takes a `&mut self`, changing both the `emails` and
`total_word_count` fields. 

The idea here was to optimize for performance by keeping track of the total word
count on insertion, so that we don't have to iterate over all emails every time
we want to get the word count later. As a result , `emails` and
`total_word_count` are now tightly coupled. We might refactor the code and
forget to update the `total_word_count` field, leading to bugs.

In functional programming paradigms or in languages that emphasize immutability,
such issues are less prevalent. For example, 
Haskell [doesn't even have mutable variables except when using the state monad](https://wiki.haskell.org/Mutable_variable). Therefore, the `Mailbox` type could look like this:

```haskell
newtype Mailbox = Mailbox [String]

addEmail :: Mailbox -> String -> Mailbox
addEmail (Mailbox emails) email = Mailbox (email : emails)

getWordCount :: Mailbox -> Int
getWordCount (Mailbox emails) = sum $ map (length . words) emails
```

This returns a new `Mailbox` every time we add a message. 

To systems programmers, this might seem inefficient, because we're allocating a
new `Mailbox` every time we add an email. However, this is not as bad as it
sounds for a few reasons:

* In the `addEmail` function, you're prepending an email to the list with the
  `:` operator. Prepending to a linked list in Haskell is an `O(1)` operation,
  so it's quite efficient. 
* While you're returning a new `Mailbox`, Haskell's lazy evaluation and the way
  it handles memory can mitigate some of the potential inefficiencies. For
  instance, unchanged parts of a data structure might be shared between the old
  and new versions.

In practice, the code is a lot easier to reason about and it might not even be
slower.

The functional version pushed us towards a better design, because it made it
obvious that we don't need the `totalWordCount` field at all: 
It was much easier to write a version which calculates the sum on the fly
instead of mutating state.

While we *could* use an identical approach, it is much less common in Rust.
Instead, that's where the `mut` keyword might come in handy.
We can use it to indicate that we want to mutate the original
`Mailbox` instead of returning a new one, while still avoiding the 
`total_word_count` field from the original code.


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
            .map(|email| email.split_whitespace().count())
            .sum()
    }

    // ... other methods ...
}
```

This is a trade-off between performance and readability 
and a pragmatic compromise between functional and imperative programming
that is quite common in Rust.

## Event Sourcing and Immutability

Event sourcing is another example where immutability shines. Event sourcing is
a pattern where you store the state of your application as a series of events.
This is useful for auditing and debugging, because you can replay the events
to see how the state of your application changed over time.

In event sourcing, you don't modify existing events. That would be like
rewriting history.
Instead, you create a new event that describes the change and append it to the
event log. This makes it a lot easier to reason about.

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

Don't worry about a few `.clone()` calls here and there. Instead,
write code that is easy to understand and maintain.

The alternative is often to use locks and these have a runtime cost, too.
On top of that, they are a common source of deadlocks.

### Immutability is a great default.

Immutable code is easier to test, parallelize, and reason about. It's also
easier to refactor, because you don't have to worry about side effects.

Rust pushes you towards immutability and offers `mut` as an opt in escape hatch
hot paths. Many other languages do the opposite: they push you to `mut` and ask
you to opt into immutability.

The use of `mut` should be the exception, not the rule.
