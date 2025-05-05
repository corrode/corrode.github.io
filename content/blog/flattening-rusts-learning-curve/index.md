+++
title = "Flattening Rust's Learning Curve"
date = 2025-05-05
draft = false
template = "article.html"
[extra]
series = "Rust Insights"
+++

I see people make the same mistakes over and over again when learning Rust.
Here are my thoughts (ordered by importance) on how you can ease the learning process to flatten Rust's learning curve.
My goal is to help you save time and frustration. 

## Stop The Resistance

Let your guard down. That's the most important thing. 

Accept that learning Rust is a completely new skillset.
There are a ton of new concepts to learn like lifetimes, ownership, and the trait system. 
And depending on your background, you'll need to add generics, pattern matching, or macros to the list.

Your learning pace doesn't have much to do with whether you're smart or not or if you have a lot of experience programming.
I have seen junior devs excel at Rust with no prior training and senior engineers struggle for weeks/months.
What matters more is **your attitude** toward the language.

Leave your hubris at home.

Treat the borrow checker as a co-author, not an adversary. This reframes the relationship.
Let the compiler do the teaching. For example, this works great with lifetimes, because the compiler will tell you when a lifetime is ambiguous. 
Then just add it and reason about why the compiler couldn't figure it out itself.
You will learn it after it comes up for the first few times.

Most of the time when fighting the compiler it is actually exposing a design flaw.
Similarly, if your code gets overly verbose or looks ugly, there's probably a better way.
Learn to do it the Rust way.

Accept that Rust has a different way to handle errors.
You might be used to exceptions from other languages, but in Rust, errors are front and center.
Try to learn the correct way with small exercises and gradually increasing complexity.

If you come from a dynamic language like Python, you'll find that Rust is more verbose in general.
Most of it comes from type annotations.
Some people might dismiss Rust as being unelegant or ugly, but this verbosity actually serves a good purpose and is immensely helpful for building large-scale applications. First off, you will read the code more often than you write it,
which means type annotations will give you more local context to reason with.
Second, it helps immensely with refactoring because the compiler can check if you broke any code while you move things around.
If your code turns out to look very ugly, take a step back and ask if there's a simpler solution.
Don't dismiss the language right away.

Use as many code linters as you can to learn the language.
Turn on all clippy lints on day one -- even the pedantic ones.
Follow it religiously. See what it teaches you. Don't skip that step.

Resistance is futile. The longer you refuse to learn, the longer you will suffer.
The moment you let your guard down is the moment you'll start to learn.
Forget what you think you knew about programming and really start to listen to what the compiler, the standard library, and clippy are trying to teach you. 

## Baby Steps

Don't make it too hard on yourself in the beginning.
I certainly tried to run before I could walk.
That alone cost me a lot of precious time.
Here are some examples:

- Use `String` and `clone()` and `unwrap` generously; you can always refactor later -- and refactoring is the best part about Rust!
I wrote an article on saving yourself time during that phase [here](/blog/prototyping).
- Use simple if statements or match statements before starting to learn some of the more idiomatic `.and_then` etc. operators
- Avoid async in week 1. The syntax and lifetimes are a tax on people still learning the core ownership model.

Don't introduce too many new concepts at the same time!
Instead, while you learn about a new concept, have an editor open and write a few examples.
What helped was to just write some code in the Rust playground and try to get it to compile. Write super small snippets (e.g., one `main.rs` for one concept) instead of using one big tutorial repo.
Get into the habit of throwing most of your learning code away.

I still do that and test out ideas in the playground or when I brainstorm with clients.

For instance, one common code snippet to explain the concept of ownership could be:

```rust
fn my_func(v: String) {
    // do something with v
}

fn main() {
    let s = String::from("hello");
    my_func(s);
    my_func(s); // error: value moved
}
```

See if you can fix it.
Ask yourself what would change if `v` was an `i32`.
That sort of thing.

Don't be afraid to throw away a lot of code samples!
Electronic text is really cheap.

If Rust code looks scary to you, break it down.
Write your own, simpler version, then slowly increase the complexity. 
Rust is easier to write than to read.
By writing lots of Rust, you will learn to read it better as well.

## Be Accurate

How you do anything is how you do everything.

You can be sloppy in other languages, but not in Rust.
That means you have to be accurate while you code.
The philosophy is that this approach will save you debugging time in the future.

I found that the people who learn Rust the fasters have great attention to detail.
If you try to just get things done and move on, you will have a much harder time
than if you try to do things properly the first time.
You will have a much better time if you re-read your code to fix stupid typos before pressing "compile."
Also build a habit of automatically thinking about `&` and `mut` as you write function signatures.

A good example of someone who thinks about these details while coding is
Tsoding. For example, watch [this stream where he builds a search engine in Rust from scratch](https://www.youtube.com/watch?v=b0KIDIOL_i4) to see what I mean.
I think you can learn this skill as long as you're putting in your best effort and give it some time.

## Don't Cheat

With today's tooling it is very easy to offload the bulk of the work to the computer.
Initially, it will feel like you're making progress, but in reality, this is how you incorporate bad habits
into your workflow.
If you can't explain what you wrote to someone else or if you don't know about the tradeoffs/assumptions a part of the code makes 
you took it too far.

Often, this stems from a fear that you're not making progress fast enough.
You don't have to prove to someone else that you're clever enough to learn Rust.

#### Walk the Walk

To properly learn Rust you actually have to write a lot of code yourself.
Don't be a lurker on Reddit, reading through other people's success stories.
Have some skin in the game.

#### Don't Go on Auto-Pilot

LLMs are like driving on auto-pilot.
It can be comfortable at first, but you won't feel in control and slowly, that uneasy feeling will creep in.
Turn off the autopilot while learning.

A quick way to set you up for success is to learn by writing code in the Rust Playground first.
Don't use LLMs or code completion. Just type it out!
If you can't, that means you haven't fully internalized a concept yet.
That's fine.
Go to the standard library and read the docs.
Take however long it takes.
Then come back and try again.
Slow is steady and steady is fast.

#### Build Muscle Memory

Muscle memory is highly underrated.
I think it's super important to get into the flow. 
Otherwise, I just wait for the next auto-completion to make progress.

When writing manually, you will make mistakes.
Mistakes are good at this stage! Embrace them!
These mistakes will help you learn to read the compiler output.
You will get a feeling for how the output looks in different error scenarios.
Don't gloss over these errors.
Over time you will develop an intuition about what feels "rustic."
 
#### Predict The Output

Another thing I like to do is to run "prediction exercises" where you guess if code will compile before running it.
This builds intuition.
Try to make every program free of syntax errors before you run it.
Don't be sloppy.
Of course, you won't always succeed, but you will get much better at it.
Eventually, you'll avoid the error in the first place.

#### Try to solve problems yourself, only *then* look up the solution.

Read lots of other people's code. I recommend [`ripgrep`](https://github.com/BurntSushi/ripgrep), for example,
which is some of the best Rust code out there.

#### Develop a healthy share of reading/writing code.

Don't be afraid to get your hands dirty.
What do you avoid? What do you run away from? Focus on that. Tackle your blind spots.
Track your common "escape hatches" (unsafe, clone, etc.) to identify your current weaknesses.
For example, if you are scared of proc macros, write a few of them.

#### Break your code

After you're done with an exercise, break your code. See what the compiler does. 
See if you can explain what happens.

#### Don't use other people's crates while learning

A shitty personal version is better than a perfect external crate.
Exception is probably serde and anyhow.
Write the rest yourself as an exercise.

## Build Good Intuitions

Concepts like lifetimes are hard to grasp.
Sometimes it helps to draw how data moves through your system.
Develop a habit to explain concepts to yourself and others through drawing.
I'm not sure, but I think this works best for "visual"/creative people (in comparison to highly analytical people).

I personally use excalidraw for drawing.
It has a "comicy" feel, which takes the edge off a bit.
The implication is that it doesn't feel highly accurate, but rather like a rough sketch. 

It can help to draw diagrams to visualize lifetimes and ownership and the path data takes through your application.

## Build On Top Of What You Already Know

Earlier I said you should forget everything you know about programming.
How can I claim now that you should build on top of what you already know?

What I meant was that there are similar concepts such as variables and control flow
in all languages.
That's where Rust is different. 
E.g., when mutability is explicit or when calling a function "moves" a value.
That's where you have to accept that Rust is just different and learn from first principles.

However, it is fine to map Rust concepts to other languages you already know.
For instance, "a trait is a bit like an interface" is wrong, but it is a good starting point
to understand the concept.

Here are a few more examples:

- "A struct is like a class (but without inheritance)" 
- "A closure is like a lambda function (but it can capture variables)"
- "A module is like a namespace"
- "A reference is like a pointer (but it has a lifetime)."

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

### Find Your People

Find other people who come from the same background as you.
Read their blogs/experiences.
Write down your experiences from your background as well.

## Don't Guess

In Rust, the details are everything.
Don't gloss over details, because they always reveal some wisdom about the task at hand.
For instance, why do you have to call `to_string()` on a thing that's already a string?

```rust
my_func("hello".to_string())
```

Those stumbling blocks are learning opportunities.
It might look like a waste of time to ask these questions and means that it will take longer to finish a task,
but it will pay off in the long run.

Reeeeeally read the error messages the compiler prints.
Everyone thinks they do this, but time and again I see people look confused while the solution is right there
including a helpful explanation.
There are `hints`. Don't ignore those.
This alone will save you sooo much time.

You might say that is true for every language, and you'd be right.
But in Rust, the error messages are actually worth your time.
Some of them are like small meditations: opportunities to think about the problem at a deeper level.

If you get any borrow-checker errors, refuse the urge to guess what's going on.
Instead of guessing, walk through the data *flow directionally* (who owns what and when).
Try to solve it yourself, then try to compile again.

## Learn on Type-Driven Development

The key to good Rust code is through its type system.
It's all in the type system.
The information is hidden in plain sight.
What few people do is click through the standard library all the way to the source code 
to read the thing they are using.
There is no magic!
You can do that in Rust much better than in most other languages.
That's because Python for example is written in C, which requires you to cross that language boundary to learn what's going on.
Similarly, the C++ standard library isn't a single, standardized implementation, but rather has several different implementations maintained by different organizations. 
That makes it super hard to know *what exactly is going on*.
In Rust, the source code is available right inside the documentation. Make good use of that!

Function signatures tell a lot!
The sooner you will embrace this, the quicker you will be up to speed.
If you have the time, read interesting parts of the standard library docs.
Even after years, I always learn something when I do.

Try to model your own projects as types first.
This is where you start to have way more fun with the language when you
start to have conversations with the compiler about what correct code looks like.

For example, once you learn how concepts like expressions, iterators and traits fit together,
you can write more concise, readable code.

Once you learn how to encode invariants in types, you can write more correct code
that you don't have to run to test. Instead, you can't compile incorrect code in the first place.

Learn Rust through "type-driven development" - let the compiler errors guide your design.

## Invest Time In Finding Good Learning Resources

Shop around for resources that fit your personal learning style.
To be honest, there is not that much good stuff out there yet.
On the plus side, it doesn't take too long to go through the list of resources
*before* settling on one specific platform/book/course.
The right resource depends on what learner you are.
In the long run, finding the right resource saves you time because you will learn quicker. 

I personally don't like doing toy exercises that others have built out for me.
That's why I don't like Rustlings too much; the exercises are not "fun" and too theoretical. I want more practical exercises.
I found that Project Euler or Advent of Code works way better for me.
Once you get the basics down, Codecrafters is another excellent resource to learn how to build larger Rust applications.

I wrote a blog post about my favorite learning resources [here](/blog/rust-learning-resources-2025).


#### Don't just learn from YouTube.

I like to watch YouTube, but exclusively for motivation/inspiration.
Watching The Primeagen is for entertainment only.
He's an amazing programmer, but trying to learn how to program by watching someone else do it is like
trying to learn how to become a great athlete by watching the Olympics.
Similarly, I think we all can agree that Jon Gjengset is an exceptional programmer and teacher, but watching him might be overwhelming
if you're just starting out. (Love the content though!)

Same goes for conference talks or podcasts: they are great for context and for soft-skills, but not for learning Rust.

Instead, invest in a good book if you can.
Books are not yet outdated and you can read them online, add personal notes, type out the code yourself and get a 
"spatial overview" of the depth of the content.

Similarly, if you're serious about using Rust professionally, buy a course or get your boss to invest in a trainer.
Of course, I'm super biased here as I run a Rust consultancy, but I truly believe that it will save you and your company countless
hours and will set you up for long-term success. Think about it: you will work with this codebase for years to come. Better make that experience a pleasant one.
A good trainer, just like a good teacher, will not go through the Rust book with you, but watch you program Rust in the wild and give you personalized feedback about your weak spots.


## Find A Coding Buddy

"Shadow" more experienced team members or friends.

Don't be afraid to ask for a code review on Mastodon or the [Rust forum](https://users.rust-lang.org/) and return the favor and do code reviews there yourself.
Take on opportunities for pair programming. When you get stuck, ask: *"What would this look like in your favorite language?"* then translate together.

#### Explain Rust code to a non-Rust developer

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

## Believe in the Long-Term Benefit

If you learn Rust because you want to put it on your CV, stop.
Learn something else instead.

I think you have to actually *like* programming to enjoy Rust (and not just like the idea of it).

If you don't see yourself writing Rust code in the future, your time might better be invested elsewhere.
That's not a bad thing, just well-intentioned advice.

If you want to be successful with Rust, you have to be in it for the long run.
Set realistic expectations: You won't be a Rust master in 1 week but you can achieve a lot in a month of focused effort.
Rust is a day 2 language. You won't "feel" as productive as in your first week of Go or Python, but stick it out and it will pay off.
Good luck.
