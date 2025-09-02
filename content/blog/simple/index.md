+++
title = "Be Simple"
date = 2025-08-26
draft = true
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

Rust developers tend to be clever.
Too clever for their own good.
In code reviews, I often see people trying to outsmart themselves.

We love to stretch Rust to its limits.
After all, this is Rust.
Shouldn't you use it to its full extent?
Advanced features are like salt: a little bit can enhance the flavor, but too much can ruin the dish.
And advanced features have a tendency to overcomplicate things.

Nothing in Rust forces you to make things harder than they should be.
That is not a trait of the language, but a mindset.
Software engineering is all about managing complexity.
As in life, complexity creeps in when you're not looking.

## What Simple Really Means

Good code is mostly boring; especially for production use.
Simple is obvious.
Simple is predictable, predictable is good.
Be clear, not clever.
Write Code for Humans, Not Computers.

> Simplicity is prerequisite for reliability.

I don't always agree with Edsger W. Dijkstra, but in this case, I think he was spot-on.

## Why Simplicity is Hard Work

Make no mistake: Being simple is hard work!
It doesn't always come naturally.

> Simplicity and elegance are unpopular because they require hard work and discipline to achieve

You said it best, Edsger.

Simplicity is typically not the first attempt but the last revision.
It takes effort to build simple systems.

The path to complexity is paved with good intentions.
A series of individually perfectly reasonable decisions can lead to an overly complex, unmaintainable system.
It takes effort to *keep* things simple.
You constantly have to fight entropy. 
Going from simple to more complex is much easier than the opposite.

## Looking At Rust Through Beginner's Eyes

After a while we forget how Rust beginners feel: it's the curse of knowledge.
More experienced developers tend to use more abstractions because they get excited about the possibilities.
The people who are starting with Rust are often overwhelmed by the complexity of the language.
Keep that in mind.
If you fail to do that, you might alienate the team members who are not as experienced as you are and they might give up on the project or Rust altogether.
Furthermore, if you leave the company and you leave behind a complex codebase, the team will have a hard time maintaining it and onboarding new team members.
The biggest holdup is how quickly people will be able to get up to speed with Rust.
Don't make it even harder on them.

## How to Fight Complexity

### Start Simple

Start with the easiest possible solution.
Switch off your inner critic.
Jerry Seinfeld had two writing modes: creating and editing.
He would never edit while creating because it would kill the creative flow.
When you're in creation mode, you're exploring possibilities and letting ideas flow freely.
When you're in editing mode, you're refining, cutting, and polishing. These modes require different mindsets and trying to do both simultaneously leads to paralysis.

The same principle applies to coding.
Don't try to architect the perfect solution on your first attempt. Write the naive implementation first, then refine it.

### Resist the Temptation

It can be tempting to use all of these fine, sharp tools you have at your disposal.
But sharp tools they are.
To master Rust is to say no to these tools more often than you say yes.

You might see an optimization opportunity but time and again, I saw people overengineer their code for no reason and without prior measurements.
Measure first, optimize later.

### Case Study: Generics 

I believe generics are a liability.
It might be a controversial opinion, but I think not only do they make the code harder to understand, they can also have a real cost on compile times (monomorphization).
Only make generic what you need to switch out the implementation *right now*.
If you can defer the decision, it's often better to do so.
Ask yourself: "this is generic functionality?" instead of "I could make this generic?"

Abstractions have an impact on the style, the "feel", of the entire codebase.
So if you use a lot of abstractions, you will have to deal with the consequences everywhere. 
So be careful with abstractions.
They have a cost.

> Abstractions are never zero cost. - NASA - The Power of Ten.

Abstractions cause complexity. 
Complexity has a cost.
At some point, complexity will slow you down.
Cognitive load is what matters.

### Performance Crimes Are OK

Rust is super fast, so you can literally make all the performance crimes you want.
Clone freely, iterate multiple times, use a vector if a hashmap is tedious.

It. Simply. Doesn't. Matter.

Hardware is fast and cheap!
So put it to work.

### How Complexity Creeps In 

Let's say you are working on a public API.
A function that will be used a lot will need to take some string based data from the user.
You are confused if you should take a `&str` or a `String` or something else as an input to my functions and why?

```rust
fn process_user_input(input: &str) {
    // do something with input
}
```

That's quite simple and doesn't allocate.
But what if the caller wants to pass a String?

```rust
fn process_user_input(input: String) {
    // do something with input
}
```

We take ownership of the input.
But hold on, what if we don't need ownership and we want to support both?

```rust
fn process_user_input(input: impl AsRef<str>) {
    // do something with input
}
```

That works.

But in the background it monomorphizes the function for each type that implements `AsRef<str>`.

That means that if we pass a `String` and a `&str`, we get two copies of that function.
That means longer compile times and larger binaries.

The problem is so simple, so how did that complexity creep in?
The problem is that we are trying to be clever.
We are trying to make the function "better" by making it more generic.
But is it really better?

All we wanted was a simple function that takes a string and does something with it.

Stay simple.
Don't overthink it.

### Vec or Iterator?

Say we're writing a link checker and we want to build a bunch of requests to check the links.
We could use a function that returns a `Vec<Result<Request>>`.

```rust
pub(crate) fn create(
  uris: Vec<RawUri>,
  source: &InputSource,
  root_dir: Option<&PathBuf>,
  base: Option<&Base>,
  extractor: Option<&BasicAuthExtractor>,
) -> Vec<Result<Request>> {
    let base = base.cloned().or_else(|| Base::from_source(source));
    uris.into_iter()
        .map(|raw_uri| create_request(&raw_uri, source, root_dir, base.as_ref(), extractor))
        .collect()
}
```

Or, we could return an iterator instead:

```rust
pub(crate) fn create(
    uris: Vec<RawUri>,
    source: &InputSource,
    root_dir: Option<&PathBuf>,
    base: Option<&Base>,
    extractor: Option<&BasicAuthExtractor>,
) -> impl Iterator<Item = Result<Request>> {
    let base = base.cloned().or_else(|| Base::from_source(source));
    uris.into_iter().map(move |raw_uri| create_request(&raw_uri, source, root_dir, base.as_ref(), extractor))
}
```

The iterator doesn't look too bad.
The vec is simpler.
What to do?
The caller likely needs to collect the results anyway since we're processing a finite set of URLs, the link checker needs all results to report successes/failures, and the results will probably be iterated multiple times.
Memory usage isn't a big concern since the number of URLs in a document is typically small, we've already allocated for the input `Vec`, and the original `HashSet` was allocating anyway.
But if neither applies, the Vec is the simpler and more idiomatic choice.

## Refactoring Simple Code

Refactoring a simple program is way easier than doing the same for a complex one. 
Everyone can do the former, while I can count the one who can do the latter.
Preserve the opportunity to refactor your code.
It might look like the clever thing to do at the time, but if you allow the simple code to just stick around for a while, you'll eventually see the right opportunity for the refactor.

Just like premature optimization, premature refactoring can get in your way.
Not every possible abstraction is worth adding.
But if an abstraction is worth adding, you'll know.
Like a sore thumb, it will be obvious once you see it.
A good time to reflect is when your code starts to feel repetitive. 
That's a sign that there's a hidden pattern in your data.
The right abstraction is trying to talk to you, to reveal itself.
It's fine to do multiple attempts at an abstraction.
See what feels right!
If none of it does, just go back to the simple version.

## How Do You Know It's Good?

Watching experienced developers write code feels like they have a constant interaction with the data and the building blocks they are working with.
It "clicks" once it fits.
It just feels like there's no overlap between the abstractions and no extra work or conversions needed.
The next step always feels obvious.
Testing works without much mocking, your documentation for your structs almost writes itself.
There's no "this struct does X and Y" in your documentation.
It's just X or Y.
Explaining the parts to a fellow developer is straightforward.
This is when you know you have a winner.
Getting there is not easy.
It takes many iterations.
All of that is easier if the code is simple in the beginning.

## DRY is Overrated

On that note, DRY is also overrated.
Feel free to repeat yourself.
Don't try to avoid repetition at all costs.
It usually leads to dense, hyper-optimized code that is hard to decipher.
It is a fool's errand to try to avoid repetition at all costs.
It's better to have a bit of repetition than to have a complex abstraction that is hard to undo.
Developer experience suffers when you have to deal with complex abstractions.
"Greppability" is a good metric for code quality.

## Clear Over Clever

Clear is better than clever.

```rust
fn strip_type_name(name: Option<&str>) -> Option<&str> {
    name.and_then(|s| s.split_once(':').map(|(_, after)| after.trim()))
}
```

vs

```rust
fn strip_type_name2(name: &str) -> Option<&str> {
    let (_, after) = name.split_once(':') else {
        return None;
    };
    Some(after.trim())
}
```

This also applies to variable names.
Don't be too clever.
Be explicit.
The broader the scope, the more explicit you should be.
Meaningful variable names are one of the easiest way to document intent and purpose.
We are no longer constrained by the length of variable names and autocomplete fixes typing mostly, so don't be too greedy.

## But What About Performance?

But isn't simple code bad for performance?
Turns out many simple algorithms are surprisingly effective.
Take quicksort or path tracing for example.
Both can be written down in a handful of lines.

```rust
fn quicksort(mut v: Vec<usize>) -> Vec<usize> {
    if v.len() <= 1 {
        return v;
    }

    let pivot = v.remove(0);

    let (smaller, larger) = v.into_iter().partition(|x| x < &pivot);

    quicksort(smaller)
        .into_iter()
        .chain(std::iter::once(pivot))
        .chain(quicksort(larger))
        .collect()
}
```

The idea is pretty simple and can fit on a napkin:

1. If the list is empty or has one element, it's already sorted.
2. Pick a random element as the pivot (for simplicity, we pick the first element).
3. Split the list into two sublists: elements smaller than the pivot and elements larger than or equal to the pivot.
4. Sort each sublist recursively.
5. If you combine the sorted smaller list, the pivot, and the sorted larger list, you get a fully sorted list.

Yes, only supports `usize` right now, but my point is that simple algorithms pack a punch.
This is an O(n log n) algorithm. It's as fast as it gets for a comparison-based sort and it's just a few lines of code.

The implementation is not too far away from the description of the algorithm.

Especially when you're doing something complicated, you should be extra careful to keep it simple.
Simplicity is a sign of deep insight, of great understanding, of clarity.
Clarity affects the way a system functions.

What I appreciate about Rust is how it balances high-level and low-level programming.
Most of the time, I write Rust code in a straightforward manner.
When performance becomes critical, I can always do some low-level analysis.

## Build for Teams

Clarity is especially important if you work in a team.
Make life easier for your colleagues by writing code you want to maintain.
Most of the code you'll write for companies will be application code, not library code.
That's because most companies don't make money writing libraries, but business logic.
Application code should be straightforward but library code can be complicated if it ends up being a bottleneck.
But just don't overdo it.
Make the common case simple to use.

Say you're building a base64 encoder.
It's safe to assume that most people will want to encode a string (i.e. a unicode string, `&str`) and that they want to use a "canonical" or "standard" base64 encoding.
Don't expect your users to jump through hoops to do the most common thing.
Unless you have a really good reason, your API should have a function like this somewhere:

```rust
/// Simple base64 encoder using standard alphabet
fn base64_encode(data: &str) -> String;
```

No need to make it generic over `AsRef<[u8]>` or support multiple alphabets.

```rust
/// Generic base64 encoder supporting multiple alphabets
fn base64_encode<T: AsRef<[u8]>>(data: T, alphabet: Base64Alphabet) -> String;
```

You could offer that as additional functionality, but don't make the easy thing hard.

## Keep Learning

All of the above doesn't mean you should not learn about all of these abstractions.
It's fun to be competent.

People can focus on learning new concepts without hurting themselves.
Understanding macros, lifetimes, interior mutability, etc. is great, but in "normal" code you almost never make use of these concepts, so don't worry about them too much.
Use all the features you need and none that you don't.

## Moving Forward

Start simple and make small improvements. 
Invest time in exploratory analysis.
You might come up with a simpler design.

Resist premature optimization.
"We might need it in the future" is a dangerous assumption.
Be careful with that assumption because it's hard to predict the future.
Your beautiful abstraction might become the biggest hurdle.

## The Courage to Be Simple

It's possible that the most common error of a smart engineer is to optimize a thing that should not exist in the first place.
Cross that bridge when you get there.
It takes courage to be simple.
What shall your colleagues think when they review your code?
What about the internet if you make it open source?
Ignore that inner critic for now.

Simplicity is about removing clutter - the unnecessary, the irrelevant, the noise.
Simplicity is to succinctly express the essence of a thing.
Simplicity is clarity.
Simple is good.
Be simple.

> For the simplicity on this side of complexity, I wouldn't give you a fig. But for the simplicity on the other side of complexity, for that I would give you anything I have.

Oliver Wendell Holmes 