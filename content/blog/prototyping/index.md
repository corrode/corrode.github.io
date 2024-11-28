+++
title = "Prototyping in Rust"
date = 2024-11-27
draft = false
template = "article.html"
[extra]
hero = "hero.svg"
series = "Idiomatic Rust"
resources = [
    "[Excellent article on the topic for another perspective](https://vorner.github.io/2020/09/20/throw-away-code.html)",
]
+++

Contrary to popular belief, Rust is a joy for building prototypes.

For all its explicitness, Rust is surprisingly ergonomic and practical for prototyping.

With a few tricks, you can quickly sketch out a solution and gradually add constraints without the compiler forcing you to work on edge cases and minute details up front or switch languages in the middle of the project.

## Why You Should Prototype 

As much as we like to come up with the perfect solution from the start, it rarely works that way.
Programming is an iterative process.

In my experience, prototyping solutions helps tremendously in finding the best approach before committing to a design.

This iterative process isn't just useful for writing games – it's equally valuable when crafting a CLI tool where you need to figure out the command line interface, or when designing a library where you need to nail down the API.

**People prototype because they want to explore the design space.
When done right, this process leads to more idiomatic code.**

## Why People Believe Rust Is Not Good For Prototyping

The common narrative goes like this:

> When you start writing a program, you don't know what you want and you change your mind pretty often.
> Rust pushes back when you change your mind because the type system is very strict.
> On top of that, getting your idea to compile takes longer than in other languages, so the feedback loop is slower.

That's why people believe that Rust isn't a good fit for prototyping.

I've found that developers from other languages and Rust beginners often share this preconception about Rust.
These developers stumble over the strict type system and the borrow checker while trying to sketch out a solution.
They believe that with Rust you're either at 0% or 100% done (everything works and has no undefined behavior) and there's nothing in between.

Here are some typical misbeliefs: 

1. Rust always requires you to handle errors.
2. Memory safety gets in the way of prototyping.
3. Ownership and borrowing take out the fun of prototyping.
4. You have to get all the details right from the beginning. 

These are all [common misconceptions](https://medium.com/@victor.ronin/love-hate-relationship-with-rust-language-part-2-c36f57d5485d) and they are not true. 

It turns out you can avoid all of these pitfalls and still get a lot of value from prototyping in Rust. 
The interaction between types is the central part of the prototyping stage, and that's where Rust shines compared to other languages.

## Problems with Prototyping in Other Languages

If you're happy with a scripting language like Python, why bother with Rust?

That's a fair question.
After all, Python is known for its quick feedback loop and dynamic type system, and you can always rewrite the code in Rust later.

Yes, Python is a great choice for prototyping.
But I've been a Python developer for a long time, and I find that I very quickly grow out of the "prototype" phase – which is when the language falls apart for me.

One thing I found particularly challenging in Python was hardening my prototype into a robust, production-ready codebase.
Exception sources are not obvious, the type system is weak, and I make mistakes while refactoring.
I often ended up with functions that could throw exceptions in unexpected places, which I would only discover when the program crashed in production.

I've found that the really hard bugs in Python are often type-related: deep down in your call chain, the program crashes because you passed the wrong type to a function. This happens frequently in practice, and it's especially frustrating when it occurs in a long-running process
after hours or days of operation.

It doesn't help that Python's type system feels tacked-on (because it is), so it won't catch these bugs effectively
unless you spend serious extra time on type annotations and fine tuning the Mypy config, which, of course, you don't do in the prototype phase.

Even putting these concerns aside, switching languages mid-project is a huge undertaking.
Maybe you'll have to maintain two codebases simultaneously for a while.
On top of that, Rust follows different idioms than Python, so you might have to rethink the software architecture.
And to make matters worse, you have to change build systems, testing frameworks, and deployment pipelines as well.

Wouldn't it be nice if you could use the same language for prototyping and production?

If you start with Rust, you could:

1. gradually improve the code quality by following cargo's and [clippy's](https://doc.rust-lang.org/clippy/) suggestions
2. start with a robust codebase from the get-go
3. ship the prototype for early feedback
4. lean into Rust's strong type system to catch errors early and help you refactor later

All without having to change languages during the project!
It saves you the context switch between languages once you're done with the prototype.

## What Makes Rust Great for Prototyping 

I prototype in Rust frequently when I need to explain systems-level concepts to clients or sketch out a prototype for a new project of my own.

When I allow myself to try a few alternatives rapidly, it leads to more idiomatic code in the long run.
It's like sketching out or modeling a design of a physical product: problems become apparent and you can get a feel for the real thing.
Unlike a sketch or a model, however, the code can be turned into a fully functional version, and that often happens when prototypes make it to production.

That's not necessarily a bad thing if the prototype turned out to be robust, but if it isn't, at least Rust gradually guides us toward a better design.
In a sense, it's like an outline for a book: I can ask others for feedback and improve it over time.

To me, it's super nice to have a single language I know well and can use for all stages of a project. 
A language that I can learn and understand all the way down to the implementation of the standard library (by going to the source code).
Other languages are often written in C/C++, and it's hard to understand what's going on under the hood.

When you explore a new language or domain, it's helpful to start with a prototype rather than aiming for a full-fledged production-ready solution right away.
Otherwise, you get stuck in minor details, and due to sunk cost fallacy, you don't want to throw away the code you wrote, so you end up keeping a suboptimal design.

Rust allows you to avoid these pitfalls by being very explicit about error conditions, but also by providing escape hatches in case you choose to ignore them for a while.

Perhaps the most important point, however, is that eventually management will say "ship it" and you'll have to live with the code you wrote.
In an ideal world, you'd have plenty of time to perfect the code, but in reality, deadlines are tight and you have to make compromises.
If that's the case, a rewrite is often not an option.
Rust allows you to have a solid foundation from the beginning.
Even the first version is often good enough for production.

Phew, with that out of the way, let's finally dive into the practical aspects of prototyping in Rust!

## What Rust Prototyping Looks Like

There's an overlap between prototyping and "[easy Rust](https://www.youtube.com/watch?v=33FG6O3qejM)."

You allow yourself to ignore some of the best practices for production code for a while.
The difference is that you are aware that you are prototyping.
It's a different mode of thinking: you are exploring!

Allow yourself to take some shortcuts early on.
During this phase, it's also fine to throw away a lot of code and ideas.

Python has a few good traits that we can learn from:

- fast feedback loop
- changing your mind is easy
- it's simple to use if you ignore the edge cases
- there is very little boilerplate
- it's easy to experiment and refactor
- you can write a script in a few lines
- no compilation step 

The goal is to get as close to that experience in Rust as possible while staying true to Rust's core principles.
We want to make changes quick and painless and rapidly iterate on your design without painting ourselves into a corner.

## Tips And Tricks For Prototyping In Rust

### Start small

It turns out you can model a surprisingly large system with just a few types and functions!
The main idea is to defer all the unnecessary parts to later by using a "simple Rust" if you will.

It's possible, but you need to switch off your inner critic who always wants to write perfect code from the beginning.
Don't let perfect be the enemy of good.
Rust enables you to comfortably defer perfection.
You can make the rough edges obvious so that you can sort them out later.

One of the biggest mistakes I observe is an engineer's perfectionist instinct to jump on minor details which don't have a broad enough impact to warrant the effort.
Take a step back and focus on the big picture.

Remember, you are exploring!
Use a coarse brush to paint the landscape first.
Try to get into a flow state where you can quickly iterate on your design.
Don't get distracted by the details too early.

### Use Simple Types

Even while prototyping, the type system is not going away.
There are ways to make this a blessing rather than a curse.

Use simple types like `i32`, `String`, `Vec` in the beginning.
We can always make things more complex later if we need to -- the reverse is much harder.

Here's a quick reference for common prototype-to-production type transitions:

| Prototype        | Production          | When to switch                                                                     |
| ---------------- | ------------------- | ---------------------------------------------------------------------------------- |
| `String`         | `&str`              | When you need to avoid allocations or store string data with a clear lifetime      |
| `Vec<T>`         | `&[T]`              | When the owned vector becomes too expensive to clone or you can't afford the heap  |
| `Box<T>`         | `&T` or `&mut T`    | When `Box` becomes a bottleneck or you don't want to deal with heap allocations    | 
| `Rc<T>`          | `&T`                | When the reference counting overhead becomes too expensive or you need mutability  | 
| `Arc<Mutex<T>>`  | `&mut T`            | When you can guarantee exclusive access and don't need thread safety               |
| `String`         | `Cow<'static, str>` | When you want to optimize string reuse or avoid allocations                        |

These owned types sidestep most ownership and lifetime issues, but they do it by allocating memory on the heap - just like Python or JavaScript would.
You can always refactor when you need to optimize for performance or tighten up resource usage, but chances are you won't need to.

### Make use of type inference

Rust is a statically, strongly typed language.
It would be tedious to write out all the types all the time if it weren't for Rust's type inference.

You can often omit (also called "elide") the types and let the compiler figure it out from the context.

```rust
let x = 42;
let y = "hello";
let z = vec![1, 2, 3];
```

This is a great way to get started quickly and defer the decision about types to later.
The system scales well with more complex types, so you can use this technique even in larger projects.

```rust
let x: Vec<i32> = vec![1, 2, 3];
let y: Vec<i32> = vec![4, 5, 6];

// Rust can infer the item type of z
let z = x.iter().chain(y.iter()).collect::<Vec<_>>();
```

Here's a more complex example which shows just how powerful Rust's type inference can be: 

```rust
use std::collections::HashMap;

// Start with some nested data
let data = vec![
    ("fruits", vec!["apple", "banana"]),
    ("vegetables", vec!["carrot", "potato"]),
];

// Let Rust figure out this complex transformation
let categorized = data
    .into_iter()
    .flat_map(|(category, items)| {
        items.into_iter().map(move |item| (item, category))
    })
    .collect::<HashMap<_, _>>();

// categorized is now a HashMap<&str, &str> mapping items to their categories
println!("What type is banana? {}", categorized.get("banana").unwrap());
```

([Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=fac339eecef40b69b919a1670a0a53df))

It's not easy to visualize the structure of `categorized` in your head, but Rust can do it for you!

### Use `unwrap` liberally

It's okay to use `unwrap` in the early stages of your project.
An explicit `unwrap` is like a stop sign that tells you "here's something you need to fix later."
You can easily grep for `unwrap` and replace it with proper error handling when you polish your code.
This way, you get the best of both worlds: quick iteration cycles and a clear path to robust error handling.

```rust
use std::fs;
use std::path::PathBuf;

fn main() {
    // Quick and dirty path handling during prototyping
    let home = std::env::var("HOME").unwrap();
    let config_path = PathBuf::from(home).join(".config").join("myapp");
    
    // Create config directory if it doesn't exist
    fs::create_dir_all(&config_path).unwrap();
    
    // Read the config file, defaulting to empty string if it doesn't exist
    let config_file = config_path.join("config.json");
    let config_content = fs::read_to_string(&config_file)
        .unwrap_or_default();
    
    // Parse the JSON config
    let config: serde_json::Value = if !config_content.is_empty() {
        serde_json::from_str(&config_content).unwrap()
    } else {
        serde_json::json!({})
    };
    
    println!("Loaded config: {:?}", config);
}
```

See all those unwraps?
To more experienced Rustaceans, they stand out like a sore thumb -- and that's a good thing!

Compare that to languages like JavaScript which can throw exceptions your way at any time.
It's much harder to ensure that you handle all the edge-cases correctly.
At the very least, it costs time. Time you could spend on more important things.

While prototyping with Rust, you can safely ignore error handling and focus on
the happy path without losing track of potential flaws.

### Use `bacon` for quick feedback cycles

Rust is not a scripting language; there is a compile step!

However, for small projects, the compile times are negligible.
Unfortunately, you have to manually run `cargo run` every time you make a change 
or use [rust-analyzer](https://rust-analyzer.github.io/) in your editor to get instant feedback.

To fill the gap, you can use external tools like [`bacon`](https://github.com/Canop/bacon) to automatically recompile and run your code whenever you make a change.
This way, you can get *almost* the same experience as with a REPL in, say, Python or Ruby.

The setup is simple:

```sh
# Install bacon
cargo install --locked bacon

# Run bacon in your project directory
bacon
```

And just like that, you can get some pretty compilation output alongside your code editor.

![bacon](bacon.png)

Oh, and in case you were wondering, `cargo-watch` was another popular tool for
this purpose, but it's since been deprecated.

### Use the Rust playground

You probably already know about the [Rust Playground](https://play.rust-lang.org).
It is great for working on small code snippets.
I find it quite useful for quickly noting down a bunch of functions or types to test out a design idea. 
The playground doesn't support auto-complete, but it's still great when you're on the go and don't have access to your full-fledged development environment.

### `cargo-script` is awesome

Did you know that cargo can also run scripts?

For example, put this into a file called `script.rs`:

```rust
#!/usr/bin/env cargo +nightly -Zscript

fn main() {
    println!("Hello prototyping world");
}
```

Now you can make the file executable with `chmod +x script.rs` and run it with `./script.rs` which it will compile and execute your code!
This allows you to quickly test out ideas without having to create a new project.
There is support for dependencies as well.

At the moment, `cargo-script` is a nightly feature, but it will be released soon on stable Rust.
You can read more about it in the [RFC](https://rust-lang.github.io/rfcs/3424-cargo-script.html).

### Don't Worry About Performance

You have to try really really hard to write slow code in Rust.
Use that to your advantage: during the prototype phase, try to keep the code as simple as possible; you can always optimize later.

I gave a talk titled ["The Four Horsemen of Bad Rust Code"](https://github.com/corrode/four-horsemen-talk) where I
argue that premature optimization is one of the biggest sins in Rust. 

Especially experienced developers coming from C or C++ might be tempted to optimize too early.

Rust makes code perform well by default - you get memory safety at virtually zero runtime cost. When developers try to optimize too early, they often fight the borrow checker by using complex lifetime annotations and intricate reference patterns in pursuit of better performance.
This leads to harder-to-maintain code that may not actually run faster.

Resist the urge to optimize too early.
You will thank yourself later. [^1]

[^1]: In the talk, I show an example where early over-optimization led to the wrong abstraction and made the code slower. The actual bottleneck was elsewhere and hard to uncover without profiling.

### Use `println!` and `dbg!` for debugging 

I find that printing values is pretty handy while prototyping.
It's one less context switch to make compared to starting a debugger.

Most people use `println!` for that, but [`dbg!`](https://doc.rust-lang.org/std/macro.dbg.html) has a few advantages:

- It prints the file name and line number where the macro is called.
- It outputs the expression as well as its value.
- It's less syntax-heavy than `println!`; e.g. `dbg!(x)` vs. `println!("{x:?}")`.
- It's only active in debug builds, so you don't have to worry about removing it later.

Where `dbg!` really shines is in recursive functions or when you want to see the intermediate values during an iteration:

```rust
fn factorial(n: u32) -> u32 {
    // `dbg!` returns the argument, 
    // so you can use it in the middle of an expression
    if dbg!(n <= 1) {
        dbg!(1)
    } else {
        dbg!(n * factorial(n - 1))
    }
}

dbg!(factorial(4));
```

The output is nice and tidy:

```rust
[src/main.rs:2:8] n <= 1 = false
[src/main.rs:2:8] n <= 1 = false
[src/main.rs:2:8] n <= 1 = false
[src/main.rs:2:8] n <= 1 = true
[src/main.rs:3:9] 1 = 1
[src/main.rs:7:9] n * factorial(n - 1) = 2
[src/main.rs:7:9] n * factorial(n - 1) = 6
[src/main.rs:7:9] n * factorial(n - 1) = 24
[src/main.rs:9:1] factorial(4) = 24
```

If you're interested, here are [more details on how to use that handy `dbg!` macro](https://edgarluque.com/blog/rust-dbg-macro/).

### Play With Types

Quite frankly, the type system is one of the main reasons I love Rust.
It feels great to express my ideas in types and see them come to life.
I would encourage you to heavily lean into the type system during the prototyping phase.

Try to build up a vocabulary of concepts and own types which describe your system. 
In the beginning, you won't have a good idea of the types in your system.
That's fine!
Start with *something* and quickly sketch out solutions and gradually add constraints to model the business requirements.
Don't stop until you find a version that feels just right. [^2]

[^2]: I usually know when I found a good abstraction once I can use all of Rust's features like expression-oriented programming and pattern matching together with my own types. The types feel like a natural extension of the language and fit in seamlessly.

Let's look at an example:
Say you're modeling a student management system.
You might start with a `Student` type and a `Course` type. 

```rust
struct Student {
    name: String,
    age: u8,
    courses: Vec<Course>,
}

struct Course {
    name: String,
    teacher: String,
    students: Vec<Student>,
}
```

When you try to create actual instances, you'll run into issues because:

- Each `Course` contains entire `Student` structs (not references)
- Each `Student` contains entire `Course` structs (not references)

This means if you wanted to add a student to multiple courses, you'd need to duplicate the entire Student struct for each course. And if you update a student's information (like their age), you'd need to update it in every Course they're in.
You built a circular dependency that's hard to resolve with this design.

After giving it some thought, you might realize that the relationship between students and courses is many-to-many.
You can then refactor the code to look like this: 

```rust
struct Student {
    name: String,
    age: u8,
}

struct Course {
    name: String,
    teacher: String,
}

struct Enrollment {
    student: Rc<Student>,
    course: Rc<Course>,
}
```

This is a more flexible design that allows you to model more complex relationships between students and courses.

Iterating on your data model is a crucial part of the prototyping phase.
The result of this phase is not the code itself, but a deeper understanding of the problem domain.
You can then use this knowledge to build a more robust and maintainable solution.
So don't be afraid to play around with types and refactor your code as you go.

### The `todo!` Macro

One of the cornerstones of prototyping is that you don't have to have all the answers right away.
In Rust, I find myself reaching for the [`todo!`](https://doc.rust-lang.org/std/macro.todo.html) macro quite often. 

I will just scaffold out the functions or a module and then fill in the blanks later.
It's like sketching: you don't have to fill in all the details right away and you can come back to it later once the composition is clear.

```rust
// We don't know yet how to process the data
// but we're pretty certain that we need a function
// that takes a Vec<i32> and returns an i32
fn process_data(data: Vec<i32>) -> i32 {
    todo!()
}

// There exists a function that loads the data and returns a Vec<i32>
// How exactly it does that is not important right now
fn load_data() -> Vec<i32> {
    todo!()
}

fn main() {
    // Given that we have a function to load the data
    let data = load_data();
    // ... and a function to process it
    let result = process_data(data);
    // ... we can print the result
    println!("Result: {}", result);
}
```

We did not do much here, but we have a clear idea of what the program should do.
Now we can go and iterate on the design.
For example, should `process_data` take a reference to the data?
Should we create a struct to hold the data and the processing logic?
How about using an iterator instead of a vector?
Should we introduce a trait to support algorithms for processing the data?

These are all helpful questions that we can answer without having to worry about the details of the implementation. 
And yet our code is typesafe and compiles, and it is ready for refactoring. 

### Avoid Generics

Chances are, you might not know which parts of your application should be generic in the beginning.
Therefore it's better to be conservative and use concrete types instead of generics until necessary. 

So instead of writing this:

```rust
fn foo<T>(x: T) -> T {
    x
}
```

Write this:

```rust
fn foo(x: i32) -> i32 {
    x
}
```

If you need the same function for a different type, feel free to just copy and paste the function and change the type. 
This way, you avoid the trap of settling on the wrong kind of abstraction too early.
Maybe the two functions only differ by type signature for now, but they might serve a completely different purpose.
If the function is not generic from the start, it's easier to remove the duplication later. 

Only introduce generics when you see a clear pattern emerge in multiple places.

Also avoid "fancy" generic type signatures:

```rust
fn foo<T: AsRef<str>>(x: T) -> String {
    x.as_ref().to_string()
}
```

Yes, this allows you to pass in a `&str` or a `String`, but it's also harder to read.

Better use an owned type for your first implementation:

```rust
fn foo(x: String) -> String {
    x
}
```

Chances are, you won't need the flexibility at all.

In summary, generics are powerful, but they can make the code harder to read and write.
Avoid them until you have a clear idea of what you're doing. 

### Ownership

One major blocker for rapid prototyping is Rust's ownership system.
If you play by the rules, it can be a bit cumbersome to pass around references and mutable references.
The compiler is constantly reminding you of ownership and lifetimes and that can break your flow.

```rust
// First attempt with references - compiler error!
struct Note<'a> {
    title: &'a str,
    content: &'a str,
}

fn create_note() -> Note<'_> {  // ❌ lifetime error
    let title = String::from("Draft");
    let content = String::from("My first note");
    Note {
        title: &title,
        content: &content
    }
}
```

This code doesn't compile because the references are not valid outside of the function.

```rust
   Compiling playground v0.0.1 (/playground)
error[E0106]: missing lifetime specifier
 --> src/lib.rs:7:26
  |
7 | fn create_note() -> Note<'_> {  // ❌ lifetime error
  |                          ^^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but there is no value for it to be borrowed from
help: consider using the `'static` lifetime, but this is uncommon unless you're returning a borrowed value from a `const` or a `static`, or if you will only have owned values
  |
```

([Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=7274f20a06226316c93d9984f1d66b5f))

A simple way around that is to avoid lifetimes altogether.
They are not necessary in the beginning.
Use owned types like `String` and `Vec` and you can always refactor later.
Also, use `.clone()` wherever you need to get around it.

```rust
// Much simpler with owned types
struct Note {
    title: String,
    content: String,
}

fn create_note() -> Note {  // ✓ just works
    Note {
        title: String::from("Draft"),
        content: String::from("My first note")
    }
}
```

If you have a type that you need to move between threads (i.e. it needs to be `Send`), you can use `Arc<Mutex<T>>` to get around the borrow checker.
If you're worried about performance, remember that other languages like Python or Java do this implicitly behind your back.

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let note = Arc::new(Mutex::new(Note {
    title: String::from("Draft"),
    content: String::from("My first note")
}));

let note_clone = Arc::clone(&note);
thread::spawn(move || {
    let mut note = note_clone.lock().unwrap();
    note.content.push_str(" with additions");
});
```

([Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=4b93a53ebc1d7ee6bc2b39c91543fba7))

### Use A Flat Module Hierarchy

Your `main.rs` is a great place for the entire prototype. 
That's fine because you can always split it up later as soon as this becomes "uncomfortable."
By then, you have a clear vision of what things should be called and how they should interact.

I keep modules in the same file until they grow too large:

```rust
mod foo {
    pub fn bar() {
        println!("Hello from foo::bar");
    }
}

mod baz {
    pub fn qux() {
        println!("Hello from baz::qux");
    }
}

fn main() {
    foo::bar();
    baz::qux();
}
```

This allows me to quickly move around in the codebase (as it's just one file) and also move code around by just cutting and pasting from one scope to another.
It's very cheap.
The individual modules can be moved to their own files later.

On top of that, the individual modules can be treated like a black box.
When I'm working on a library, this helps me to quickly test the API and see if the naming makes sense and if the modules are structured correctly.
E.g. I might have a `config` module with a `load` function that returns a `Config` struct, which gets used by the `server` module to start the server. 

```rust
mod config {
    pub struct Config {
        pub port: u16,
    }

    pub fn load() -> Config {
        Config { port: 8080 }
    }
}

mod server {
    use crate::config;

    pub struct Server {
        config: config::Config,
    }

    impl Server {
        pub fn new(config: config::Config) -> Self {
            Server { config }
        }

        pub fn start(&self) {
            println!("Starting server on port {}", self.config.port);
        }
    }
}

use server::Server;

fn main() {
    let config = config::load();
    let server = Server::new(config);
    server.start();
}
```

In general, I try to keep a flat hierarchy in the beginning and only introduce more structure when it becomes necessary.
See also [Matklad's article on large Rust workspaces](https://matklad.github.io/2021/08/22/large-rust-workspaces.html).

## Summary

That's it!

Rust makes for an all-around great language, from prototyping all the way to production.

Gradual improvement is very pleasant in Rust.
This way, you get the best of both worlds: you can quickly iterate on your design, but you can also make the code more robust over time.
You can do all of this without sacrificing the advantages of Rust.

It turns out, even "bad" Rust code is pretty decent compared to code I wrote in other languages; it's still safe and fast, covers most cases, and I have an easier time refactoring it later because flaws are more obvious (capital-case types, missing error handling, explicit allocations with `Box` and all).

If you have any more tips or tricks for prototyping in Rust, [get in touch](/about) and I'll add them to the list!