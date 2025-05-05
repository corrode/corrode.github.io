+++
title = "Flattening Rust's Learning Curve"
date = 2025-05-05
draft = false
template = "article.html"
[extra]
series = "Rust Insights"
+++

I see people make the same mistakes over and over again when learning Rust.
Here are my thoughts (ordered by importance) on how you can ease the learning process.
My goal is to help you save time and frustration. 

## Let Your Guard Down

Stop resisting. That's the most important lesson. 

Accept that learning Rust requires adopting a completely different mental model than what you're used to.
There are a ton of new concepts to learn like lifetimes, ownership, and the trait system. 
And depending on your background, you'll need to add generics, pattern matching, or macros to the list.

Your learning pace doesn't have much to do with whether you're smart or not or if you have a lot of programming experience.
Instead, what matters more is **your attitude toward the language**.

I have seen junior devs excel at Rust with no prior training and senior engineers struggle for weeks/months or even give up entirely. Leave your hubris at home.

Treat the borrow checker as a co-author, not an adversary. This reframes the relationship.
Let the compiler do the teaching: for example, this works great with lifetimes, because the compiler will tell you when a lifetime is ambiguous. 
Then just add it but take the time to reason about *why* the compiler couldn't figure it out itself.

```rust
fn longest(x: &str, y: &str) -> &str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

If you try to compile this, the compiler will ask you to add a lifetime parameter.
It provides this helpful suggestion:

```rust
1 | fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
  |           ++++     ++          ++          ++
```

So you don't have to guess what the compiler wants and can follow its instructions.
But also sit down and wonder *why* the compiler couldn't figure it out itself.

Most of the time when fighting the compiler it is actually exposing a design flaw.
Similarly, if your code gets overly verbose or looks ugly, there's probably a better way.
Declare defeat and learn to do it the Rust way.

If you come from a dynamic language like Python, you'll find that Rust is more verbose in general.
Most of it just comes from type annotations, though.
Some people might dismiss Rust as being "unelegant" or "ugly", but the verbosity actually serves a good purpose and is immensely helpful for building large-scale applications:

- First off, you will read the code more often than you write it,
which means type annotations will give you more local context to reason with.
- Second, it helps immensely with refactoring because the compiler can check if you broke any code while you move things around.
If your code turns out to look very ugly, take a step back and ask if there's a simpler solution.
Don't dismiss the language right away.

Turn on all [clippy lints](https://doc.rust-lang.org/clippy/) on day one -- even the pedantic ones.
Run the linter and follow the suggestions religiously.
Don't skip that step once your program compiles.

Resistance is futile.
The longer you refuse to learn, the longer you will suffer;
but the moment you let your guard down is the moment you'll start to learn.
Forget what you think you knew about programming and really start to listen to what the compiler, the standard library, and clippy are trying to tell you. 

## Baby Steps

I certainly tried to run before I could walk.
That alone cost me a lot of precious time.

Don't make it too hard on yourself in the beginning.
Here are some tips:

- Use `String` and `clone()` and `unwrap` generously; you can always refactor later -- and refactoring is the best part about Rust!
I wrote an article on saving yourself time during that phase [here](/blog/prototyping).
- Use simple if or match statements before starting to learn some of the more idiomatic `.and_then` etc. combinators
- Avoid async Rust in week 1. The additional rules are a tax on people still learning the core ownership model.

Don't introduce too many new concepts at the same time!
Instead, while you learn about a new concept, have an editor open and write out a few examples.
What helped was to just write some code in the [Rust playground](https://play.rust-lang.org/) and try to get it to compile. Write super small snippets (e.g., one `main.rs` for one concept) instead of using one big "tutorial" repo.
Get into the habit of throwing most of your code away.

I still do that and test out ideas in the playground or when I brainstorm with clients.

For instance, here's one of my favorite code snippets to explain the concept of ownership:

```rust
fn my_func(v: String) {
    // do something with v
}

fn main() {
    let s = String::from("hello");
    my_func(s);
    my_func(s); // error, but why?
}
```

Can you fix it?
Can you explain it?
Ask yourself what would change if `v` was an `i32`.

If Rust code looks scary to you, **break it down**.
Write your own, simpler version, then slowly increase the complexity. 
Rust is easier to write than to read.
By writing lots of Rust, you will also learn how to read it better as well.

## Be Accurate

> How you do anything is how you do everything.
> -- An ancient Rust proverb

You can be sloppy in other languages, but not in Rust.
That means you have to be accurate while you code or the code just won't compile.
The expectation is that this approach will save you debugging time in the future.

I found that the people who learn Rust the fastest all have great attention to detail.
If you try to just get things done and move on, you will have a harder time than if you aim to do things right on your first try.
You will have a much better time if you re-read your code to fix stupid typos before pressing "compile."
Also build a habit of automatically adding `&` and `mut` where necessary as you go. 

A good example of someone who thinks about these details while coding is
Tsoding. For example, watch [this stream where he builds a search engine in Rust from scratch](https://www.youtube.com/watch?v=b0KIDIOL_i4) to see what I mean.
I think you can learn this skill as long as you're putting in your best effort and give it some time.

## Don't Cheat

With today's tooling it is very easy to offload the bulk of the work to the computer.
Initially, it will feel like you're making quick progress, but in reality, you just strengthen bad habits in your workflow.
If you can't explain what you wrote to someone else or if you don't know about the tradeoffs/assumptions a part of your code makes,
you took it too far.

Often, this approach stems from a fear that you're not making progress fast enough.
But you don't have to prove to someone else that you're clever enough to pick up Rust very quickly.

#### Walk the Walk

To properly learn Rust you actually have to write a lot of code by hand.
Don't be a lurker on Reddit, reading through other people's success stories.
Have some skin in the game!
Put in the hours because there is no silver bullet.
Once it works, consider open sourcing your code even if you know it's not perfect.

#### Don't Go on Auto-Pilot

LLMs are like driving a car on auto-pilot.
It's comfortable at first, but you won't feel in control and slowly, that uneasy feeling will creep in.
Turn off the autopilot while learning.

A quick way to set you up for success is to learn by writing code in the Rust Playground first.
Don't use LLMs or code completion. Just type it out!
If you can't, that means you haven't fully internalized a concept yet.
That's fine!
Go to the standard library and read the docs.
Take however long it takes and then come back and try again.

Slow is steady and steady is fast.

#### Build Muscle Memory

Muscle memory in programming is highly underrated.
People will tell you that this is what code completion is for, but I believe it's a requirement to reach a state of flow:
if you constantly blunder over syntax errors or, worse, just wait for the next auto-completion to make progress,
that is a terrible developer experience.

When writing manually, you will make more mistakes.
Embrace them!
These mistakes will help you learn to understand the compiler output.
You will get a "feeling" for how the output looks in different error scenarios.
Don't gloss over these errors.
Over time you will develop an intuition about what feels "rustic."
 
#### Predict The Output

Another thing I like to do is to run "prediction exercises" where I guess if code will compile before running it.
This builds intuition.
Try to make every program free of syntax errors before you run it.
Don't be sloppy.
Of course, you won't always succeed, but you will get much better at it over time.

#### Try To Solve Problems Yourself, Only *Then* Look Up The Solution.

Read lots of other people's code. I recommend [`ripgrep`](https://github.com/BurntSushi/ripgrep), for example,
which is some of the best Rust code out there.

#### Develop A Healthy Share Of Reading/Writing Code.

Don't be afraid to get your hands dirty.
Which areas of Rust do you avoid?
What do you run away from?
Focus on that.
Tackle your blind spots.
Track your common "escape hatches" (unsafe, clone, etc.) to identify your current weaknesses.
For example, if you are scared of proc macros, write a bunch of them.

#### Break Your Code

After you're done with an exercise, break it! See what the compiler says. 
See if you can explain what happens.

#### Don't Use Other People's Crates While Learning

A poor personal version is better than a perfect external crate (at least while learning).
Write some small library code yourself as an exercise.
Notable exceptions are probably `serde` and `anyhow`, which can save you time dealing with JSON inputs and setting up error handling that you can spend on other tasks
as long as you know how they work.

## Build Good Intuitions

Concepts like lifetimes are hard to grasp.
Sometimes it helps to draw how data moves through your system.
Develop a habit to explain concepts to yourself and others through drawing.
I'm not sure, but I think this works best for "visual"/creative people (in comparison to highly analytical people).

I personally use [excalidraw](https://excalidraw.com/) for drawing.
It has a "comicy" feel, which takes the edge off a bit.
The implication is that it doesn't feel highly accurate, but rather serves as a rough sketch. 
Many good engineers (as well as great Mathematicians and Physicists) are able to visualize concepts with sketches. 

In Rust, sketches can help to visualize lifetimes and ownership of data or for architecture diagrams.

## Build On Top Of What You Already Know

Earlier I said you should forget everything you know about programming.
How can I claim now that you should build on top of what you already know?

What I meant is that Rust is the most different in familiar areas like control flow handling and value passing.
E.g., mutability is very explicit in Rust and calling a function typically "moves" its arguments. 
That's where you have to accept that Rust is just *different* and learn from *first principles*.

However, it is okay to map Rust concepts to other languages you already know.
For instance, "a trait is a bit like an interface" is wrong, but it is a good starting point
to understand the concept.

Here are a few more examples:

- "A struct is like a class (minus the inheritance)" 
- "A closure is like a lambda function (but it can capture variables)"
- "A module is like a namespace (but more powerful)"
- "A borrow is like a pointer (but with single owner)."

And if you have a functional background, it might be:

- "`Option` is like the `Maybe` monad"
- "Traits are like type-classes"
- "Enums are algebraic data types"

The idea is that mapping concepts helps fill in the gaps more quickly.

Map what you already know from another language (e.g., Python, TypeScript) to Rust concepts.
As long as you know that there are subtle differences, I think it's helpful.

I don't see people mention this a lot, but I believe that [Rosetta Code](https://rosettacode.org/wiki/Rosetta_Code) is a great resource for that.
You basically browse their list of tasks, pick one you like and start comparing the Rust solution with the language you're strongest in.

Also, port code from a language you know to Rust. 
This way, you don't have to learn a new domain at the same time as you learn Rust.
You can build on your existing knowledge and experience.

- Translate common language idioms from your strongest language to Rust. E.g., how would you convert a list comprehension from Python to Rust?
  Try it first, then look for resources, which explain the concept in Rust. For instance, [I wrote one](/blog/iterators) on this topic specifically.
- I know people who have a few standard exercises that they port to every new language they learn.
For example, that could be a ray-tracer, a sorting algorithm, or a small web app.

Finally, find other people who come from the same background as you.
Read their blogs where they talk about their experiences learning Rust.
Write down your experiences as well.

## Don't Guess

I find that people who tend to *guess* their way through challenges
often have the hardest time learning Rust. 

In Rust, the details are everything.
Don't gloss over details, because they always reveal some wisdom about the task at hand.
Even if you don't care about the details, they will come back to bite you later.

For instance, why do you have to call `to_string()` on a thing that's already a string?

```rust
my_func("hello".to_string())
```

Those stumbling blocks are learning opportunities.
It might look like a waste of time to ask these questions and means that it will take longer to finish a task,
but it will pay off in the long run.

Reeeeeally read the error messages the compiler prints.
Everyone thinks they do this, but time and again I see people look confused while the solution is right there in their terminal.
There are `hints` as well; don't ignore those.
This alone will save you sooo much time.
Thank me later.

You might say that is true for every language, and you'd be right.
But in Rust, the error messages are actually worth your time.
Some of them are like small meditations: opportunities to think about the problem at a deeper level.

If you get any borrow-checker errors, refuse the urge to guess what's going on.
Instead of guessing, *walk through the data flow by hand* (who owns what and when).
Try to think it through for yourself and only try to compile again once you understand the problem.

## Learn on Type-Driven Development

The key to good Rust code is through its type system.

It's **all** in the type system.
Everything you need is hidden in plain sight.
But often, people skip too much of the documentation and just look at the examples.

What few people do is *read the actual function documentation*. 
You can even click through the standard library all the way to the source code to read the thing they are using.
There is no magic (and that's what's so magical about it).

You can do that in Rust much better than in most other languages.
That's because Python for example is written in C, which requires you to cross that language boundary to learn what's going on.
Similarly, the C++ standard library isn't a single, standardized implementation, but rather has several different implementations maintained by different organizations. 
That makes it super hard to know *what exactly is going on*.
In Rust, the source code is available right inside the documentation. Make good use of that!

Function signatures tell a lot!
The sooner you will embrace this additional information, the quicker you will be off to the races with Rust.
If you have the time, read interesting parts of the standard library docs.
Even after years, I always learn something when I do.

Try to model your own projects with types first.
This is when you start to have way more fun with the language.
It feels like you have a conversation with the compiler about the problem you're trying to solve. 

For example, once you learn how concepts like expressions, iterators and traits fit together,
you can write more concise, readable code.

Once you learn how to encode invariants in types, you can write more correct code
that you don't have to run to test. Instead, you can't compile incorrect code in the first place.

Learn Rust through "type-driven development" and let the compiler errors guide your design.

## Invest Time In Finding Good Learning Resources

Before you start, shop around for resources that fit your personal learning style.
To be honest, there is not that much good stuff out there yet.
On the plus side, it doesn't take too long to go through the list of resources
*before* settling on one specific platform/book/course.
The right resource depends on what learner you are.
In the long run, finding the right resource saves you time because you will learn quicker. 

I personally don't like doing toy exercises that others have built out for me.
That's why I don't like Rustlings too much; the exercises are not "fun" and too theoretical. I want more practical exercises.
I found that [Project Euler](https://projecteuler.net/) or [Advent of Code](https://adventofcode.com/) work way better for me.
The question comes up quite often, so I wrote a blog post about [my favorite Rust learning resources](/blog/rust-learning-resources-2025).

#### Don't Just Watch YouTube

I like to watch YouTube, but exclusively for recreational purposes. 
In my opinion, watching [ThePrimeagen](https://www.youtube.com/c/theprimeagen) is for entertainment only.
He's an amazing programmer, but trying to learn how to program by watching someone else do it is like trying to learn how to become a great athlete by watching the Olympics.
Similarly, I think we all can agree that [Jon Gjengset](https://www.youtube.com/c/JonGjengset) is an exceptional programmer and teacher, but watching him might be overwhelming
if you're just starting out. (Love the content though!)

Same goes for conference talks or podcasts: they are great for context, and for soft-skills, but not for learning Rust.

Instead, invest in a good book if you can.
Books are not yet outdated and you can read them offline, add personal notes, type out the code yourself and get a 
"spatial overview" of the depth of the content by flipping through the pages.

Similarly, if you're serious about using Rust professionally, buy a course or get your boss to invest in a trainer.
Of course, I'm super biased here as I run a Rust consultancy, but I truly believe that it will save you and your company countless
hours and will set you up for long-term success. Think about it: you will work with this codebase for years to come. Better make that experience a pleasant one.
A good trainer, just like a good teacher, will not go through the Rust book with you, but watch you program Rust in the wild and give you personalized feedback about your weak spots.

## Find A Coding Buddy

"Shadow" more experienced team members or friends.

Don't be afraid to ask for a code review on Mastodon or the [Rust forum](https://users.rust-lang.org/) and return the favor and do code reviews there yourself.
Take on opportunities for pair programming.

#### Explain Rust Code To Non-Rust Developers

This is such a great way to see if you truly understood a concept.
Don't be afraid to say "I don't know."
Then go and explore the answer together by going straight to the docs. 
It's way more rewarding and honest.

Help out with OSS code that is abandoned.
If you put in a solid effort to fix an unmaintained codebase, you will help others while learning how to work with other people's Rust code.

Read code out loud and explain it.
There's no shame in that!
It helps you "serialize" your thoughts and avoid skipping important details.

Take notes.
Write your own little "Rust glossary" that maps Rust terminology to concepts in your business domain.
It doesn't have to be complete and just has to serve your needs.

Write down things you found hard and things you learned.
If you find a great learning resource, share it!

## Believe In The Long-Term Benefit

If you learn Rust because you want to put it on your CV, stop.
Learn something else instead.

I think you have to actually *like* programming (and not just the idea of it) to enjoy Rust.

If you want to be successful with Rust, you have to be in it for the long run.
Set realistic expectations: You won't be a "Rust grandmaster" in a week but you can achieve a lot in a month of focused effort.
There is no silver bullet, but if you avoid the most common ways to shoot yourself in the foot, you pick up the language much faster.
Rust is a day 2 language. You won't "feel" as productive as in your first week of Go or Python, but stick it out and it will pay off.
Good luck and have fun!
