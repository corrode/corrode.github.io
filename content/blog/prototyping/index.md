+++
title = "Prototyping in Rust"
date = 2024-11-26
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
resources = [
    "[Excellent article on the topic for another perspective](https://vorner.github.io/2020/09/20/throw-away-code.html)",
]
+++

Contrary to popular belief, Rust is a joy for building prototypes.

For all its explicitness, Rust is surprisingly ergonomic and practical for prototyping.

With a few tricks you can quickly sketch out a solution and gradually add constraints without the compiler forcing you to work on the edge cases and minute details up front
or switching languages in the middle of the project.

## What makes prototyping so important

Programming is an iterative process and as much as we like to come up with the perfect solution from the start, it's rarely done.
I found that prototyping solutions helps me a lot in coming up with the best approach, similar to creating a sketch before painting a picture.

People prototype because they want to explore the design space. 

This iterative process is not only useful if you're writing a game, but it's also if you're writing a CLI
tool where you need to figure out the command line interface or if you're
writing a library where you need to figure out the API.

## Why people believe Rust is not good for prototyping

The common narrative is as follows:

In the beginning of writing a program, you don't know what you want and you change your mind pretty often
Rust doesn't like it if you change your mind because the type system is very strict
On top of that, getting your idea to compile takes longer than in other languages, so the feedback loop is slower
That's why people believe that Rust is not a good language for prototyping

If found that developers from other languages and Rust beginners often share that preconception about Rust.


These developers stumble over the strict type system and the borrow checker while they are trying to sketch out a solution.

They believe that with Rust you are either 0% done or 100% done (everything works and has no undefined behavior) and there's nothing in between.

Here's what they believe:

1. You have to define your types up front
2. Rust requires you to handle errors
3. Ownership gets in the way
4. To add insult to injury, you might have to deal with lifetimes

This is a [common misconception](https://medium.com/@victor.ronin/love-hate-relationship-with-rust-language-part-2-c36f57d5485d) and it's not true.

It turns out that you can skip all but part 1 and still get a lot of value out of Rust. 
The interaction between types is the central part of the prototyping stage anyway and that's where Rust shines.
If done right, memory safety does not get in the way of prototyping.

On top of that, you can iterate quickly and get from idea to working code in no time. 

## Why should you even use Rust for prototyping

If you're happy with a scripting language like Python, you might wonder why you should even consider Rust for prototyping.
After all, Python is known for its quick feedback loop and its dynamic type system and you can always rewrite the code in Rust later.

Yes, Python, it's a great choice for prototyping
But I've been a Python developer for a long time and I find that I very quickly get out of the "prototype" phase. This is when the language falls apart for me. Exceptions are not obvious, the type system is weak, I make mistakes while refactoring.

Something I found hard to do in Python was to hardening my prototype into a robust, production-ready codebase.  
I often ended up with functions which could throw exceptions in unexpected places, which I would only find out about when the program crashed in production.
I found that the really hard bugs in Python are often type-related: deep down in your call-chain the program crashes because you passed the wrong type to a function. 
It doesn't help that the type system in Python is tacked-on, so it does not help much in catching these errors.
This happens a lot in practice and it's very frustrating if it happens in a long-running process.

Even putting these concerns aside, switching languages mid-project is a huge undertaking.
You might have to work on two codebases at the same time, and you might have to throw away the code you wrote in the first place.
On top of that, Rust follows different idioms than Python, so you might have to rethink the software architecture as well.
And on top of it all, you have to change build systems, testing frameworks, and deployment pipelines.

Instead, if you start with Rust, you could

1. gradually improve the code quality by following clippy's suggestions
2. start with a robust codebase from the beginning
3. ship the prototype for early feedback
4. lean into Rust's strong type system to catch errors early and help you refactor later

All without having to switch languages during the project!
It saves you the context switch between languages once you're done with the prototype. You can simply copy over the good parts and rewrite the rest.

Wouldn't it be nice if you could use the same language for prototyping and production?

## Why Rust is great for prototyping


Prototyping is a great tool for teaching concepts. I do this all the time with clients.
I prototype in Rust a lot when I need to explain systems-level concepts to clients or sketch out a prototype for a new project of my own.

If I allow myself to try a few alternatives rapidly, this leads to more idiomatic code in the long run.

It's like sketching out or modeling a design of a physical product: problems become apparent and one can get a feeling for the real thing. 
Unlike a sketch or a model, however, the code can be turned into a fully functional version and often that happens in reality when prototypes make it to production.
That's not necessarily a bad thing if the prototype turned out to be robust, but if it isn't, at least Rust gradually guides us towards a better design.
In a sense it's more like a sketch before the painting.
I can show it to others and they can give me feedback on it.

To me it's super nice to have a single language I know well and can do everything with.
A language that I can learn and understand all the way down to the implementation of the standard library (by going to the source code). Other languages are often written in a different language like C or C++ and it's hard to understand what's going on under the hood.

When you explore a new language or a new domain, it's helpful to start with a prototype and not aim for a full-fledged production-ready solution right away.
Otherwise you get stuck in minor details and due to sunken cost fallacy you don't want to throw away the code you wrote so you end up keeping a suboptimal design.
Rust allows you to do just that.

Perhaps the most important point, however is that at some point management will say "ship it" and you'll have to live with the code you wrote.
In an ideal world, you'd have plenty of time to perfect the code, but in reality, deadlines are tight and you have to make compromises.
If that is the case, a rewrite is often not an option.
Rust allows you to have a solid foundation from the beginning.
With Rust, even the first version is typically good enough for production.

Here are my tips for prototyping in Rust.

## What Rust Prototyping looks like

There's an overlap between prototyping and "easy Rust."

You allow yourself to ignore some of the best practices for production code for a while.
The difference is that you are aware that you are prototyping
It's a different mode of thinking: you are exploring! 

Allow yourself to take some shortcuts.
During this phase, it is fine to throw away a lot of code and ideas.
Fake it before you make it.

We can learn a few things from Python's book:

- fast feedback loop
- changing your mind is easy
- it's also simple to use. you don't have to deal with errors: it throws exceptions
- there is very little boilerplate
- easy to change code, experiment, throw away code, refactor
- you can write a script in a few lines, you don't have to compile it

The goal is to get close to that experience in Rust.
We want to make changes quick and painless and rapidly iterate on your design without painting ourselves into a corner.  

## Tips and tricks for prototyping in Rust

### Start small

Turns out you can model a surprisingly large system with just a few types and functions!
The main idea is to defer all the unnecessary parts to later; by using a "simple Rust" if you will.
It's possbile, but you need to switch off your inner critic who always wants to write perfect code from the beginning
Don't let perfect be the enemy of good.
Rust enables you to comfortably defer perfection.
You can make the rough edges obvious so that you can sort them out later.

One of the biggest mistakes I observe is an instinct to jump on local debt that itches an engineer’s perfectionist side when it doesn’t have a broad enough impact to warrant the effort.
you need to be in a different mode of thinking: you are exploring! Allow yourself to write bad code and fail. Failing is fine if it's fast.
find a lot of ways how not to do it very quickly!
we need to find a way to get fast feedback

### Use simple types

Even while protoyping, the type system is not going away. 
But we can at least make it easier on ourselves.

Use simple types like i32, String, Vec in the beginning.
It will get more robust later

If you can always replace `String` with `&str` and `Vec` with `&[T]` later
in case you'd like to avoid heap allocations and optimize for performance.
Same with replacing a `Box` with `&` or `&mut`. 

### Make use of type inference

Rust has a powerful type inference system, also known as type elision.
You can often omit types and let the compiler figure it out.

```rust
let x = 42;
let y = "hello";
let z = vec![1, 2, 3];
```

This is a great way to get started quickly and defer the decision about types to later.
You can use that in more complex scenarios as well:

```rust
let x: Vec<i32> = vec![1, 2, 3];
let y: Vec<i32> = vec![4, 5, 6];

// Rust can infer the type of z
let z = x.iter().chain(y.iter()).collect::<Vec<_>>();
```

TODO: MORE COMPLEX EXAMPLE

### Use `unwrap` liberally

It's okay to use `unwrap` in the early stages of your project.
An explicit `unwrap` is like a stop sign that tells you "here's something you need to fix later." 
You can easily grep for `unwrap` while I make the code production-ready and replace it with proper error handling.
This way, you get the best of both worlds: you can quickly iterate on your design without forgetting about potential errors.

### Use `cargo-watch` or `bacon` for quick feedback cycles

Rust is not a scripting language.
There is a compile step.
However, for small projects, the compile times are still quite fast.
You can use a tool like [`bacon`](https://github.com/Canop/bacon) to automatically recompile and run your code whenever you make a change. 
This way, you can get almost the same experience as with a REPL in Python or Ruby.

### Use the Rust playground

The [Rust Playground](https://play.rust-lang.org) is great for small snippets.
I find it very useful to quickly test out a function or a type and share it with others.
It doesn't have have auto-complete, but it's great when I'm no the go and don't have access to my development environment.

### `cargo-script` is awesome

Did you know that cargo can run scripts?

Put this into a file called `script.rs`:

```rust
#!/usr/bin/env cargo +nightly -Zscript

fn main() {
    println!("Hello protoyping world");
}
```

You can run this script with `./script.rs` and it will compile and run the code!
It allows you to quickly test out ideas without having to create a new project.
There is support for dependencies as well.

At the moment, it's a nightly feature, but it will be released soon on stable Rust.
You can read more about it in the [RFC](https://rust-lang.github.io/rfcs/3424-cargo-script.html).

### Don't worry about performance

You have to try really hard to write slow code in Rust.
During the prototype phase, build the simplest solution that could possibly work.
You can always optimize later.

I gave a talk titled ["The Four Horsemen of Bad Rust Code"](https://github.com/corrode/four-horsemen-talk)
where I talk about the most common pitfall of overoptimization.

### Use `dbg!` and `println!` for debugging 

Even though there are debuggers, I found that printing values is handy while protoyping.
It's one less context switch to make in comparison to starting a debugger.
Just use [`dbg`](https://doc.rust-lang.org/std/macro.dbg.html) to print whole expressions with their value, file name and line numbers.

TODO: EXAMPLE COMPARISON DBG VS PRINTLN

Here are [more details on how to use that handy `dbg!` macro](https://edgarluque.com/blog/rust-dbg-macro/).

### Play with types

In the beginning, you won't have a good idea of the types in your system.
That's okay.
Try to build up a vocabulary of concepts and group them.
Start with something, even if you don't have the best types yet.
Quickly sketch out a solution and gradually add constraints to match the business requirements.
Don't be afraid to try different ideas until you find something that "clicks."

### The `todo!` macro

I found that I use [`todo`](https://doc.rust-lang.org/std/macro.todo.html) a lot to sketch out the API.
I will just scaffold out the functions or a module and then fill in the blanks later.
It's like sketching: you don't have to fill in all the details right away and you can come back to it later once the composition is clear.

TODO: EXAMPLE OF TODO MACRO IN VARIOUS PLACES

### Avoid generics

Generics are a powerful feature of Rust, but they can make the code harder to read
and write.
In the beginning, you might not know which parts of your application should be generic.
It's better to be conservative and use concrete types instead of generics.

So instead of writing this:

```rust
fn foo<T>(x: T) -> T {
    x
}
```

You can write this:

```rust
fn foo(x: i32) -> i32 {
    x
}
```

If you need the same function for a different type, you can copy stuff freely.
The reason is that you avoid the trap of settling on the wrong type of abstraction too early.
Maybe the two functions only differ by type signature for now, but they might serve a completely different purpose later on.
Easier to to defer that decision and introduce generics when you see the same pattern emerge in multiple places. 

Same goes for "fancy" type signatures:

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

### Ownership

One major blocker for rapid prototyping is Rust's ownership system.
If you play by the rules, it can be a bit cumbersome to pass around references and mutable references.
The compiler is constantly reminding you of ownership and lifetimes and that can break your flow.

A simple way around that is to avoid lifetimes altogetehr.
They are not necessary in the beginning.
Use owned types like `String` and `Vec` and you can always refactor later.
Also, use `.clone()` wherever you need to get around it.

If you have a type that you need to move between threads (`Send`), you can use `Arc<Mutex<T>>` to get around the borrow checker.
If you're worried about performance, remember that other languages like Python or Java make liberal use of heap allocations and cloning and they are still fast enough for most use cases. 

### Scoping

I often find myself "abusing" `main` as the place where I write the entire program in.
That's fine because I can always split it up later.
I try to move things out into separate functions and modules as soon as it becomes "uncomfortable" to work in `main`.
By then, I have a clear vision of what the things should be called and how they should interact.

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


This allows you to quickly move around in the codebase (as it's just one file) and also move code around by just cutting and pasting from one scope to another.
It's very cheap.
It allows me to quickly test module interaction and treat modules like a black box.
I also found that it helps with avoiding long compile times as a single file compiles faster is just one compilation unit.

## Summary

It turns out, even "bad" Rust code is pretty decent in comparison to code I wrote in other languages; it's still safe and fast, covers most cases, and I have an easier time refactoring it later because flaws are more obvious (capital-case types, missing error handling, explicit allocations with `Box` and all)

You can do all of this without sacrificing all the advantages of Rust.
Gradual improvement is very pleasant in Rust.
This way, you get the best of both worlds: you can quickly iterate on your design, but you can also make the code more robust over time

Rust makes for an all-around great language, from prototyping all the way to production.