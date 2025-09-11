+++
title = "Be Simple"
date = 2025-09-11
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = [
    { name = "Theodor-Alexandru Irimia", url = "https://github.com/tirimia" },
    { name = "Thomas Zahner",  url = "https://github.com/thomas-zahner"}
]
+++

**The phone buzzes at 3 AM.**

You roll out of bed, open your laptop, and see this in the logs:

```rust
thread 'tokio-runtime-worker' panicked at 'called `Result::unwrap()` on an `Err` value: 
Error("data did not match any variant of untagged enum Customer at line 1 column 15")', 
src/parsers/universal.rs:47:23
```

You open the codebase and find this:

```rust
pub struct UniversalParser<T: DeserializeOwned> {
    format: Box<dyn DataFormat>,
    _marker: std::marker::PhantomData<T>,
}

impl<T: DeserializeOwned> UniversalParser<T> {
    pub fn parse(&self, content: &str) -> Result<Vec<T>, Box<dyn std::error::Error>> {
        self.format.parse(content)
    }
}
```

A few thoughts rush through your head: 

"What the hell is a PhantomData?"  
"Why is there a trait object?"  
"This is going to be a long night."

The error must be buried *somewhere* in the interaction between that `DataFormat` trait, the generic parser, and serde deserialization.
You scroll through 200 lines of trait implementations and generic constraints.
Each layer adds another level of indirection.
The stack trace is 15 levels deep.
It's like peeling an onion... it makes you cry.

You run `git blame` and curse the colleague who wrote this code.
Whoops, it was you a few months ago.

**Quick rewind. The phone buzzes at 3 AM.**

You roll out of bed, open your laptop, and see this in the logs:

```
Error: CSV parse error at line 847: invalid UTF-8 sequence at byte index 23
```

You find this code:

```rust
#[derive(Debug, Deserialize)]
pub struct Customer {
    pub name: String,
    pub email: String, 
    pub phone: String,
}

pub fn parse_customers(csv_content: &str) -> Result<Vec<Customer>, csv::Error> {
    let mut reader = csv::Reader::from_reader(csv_content.as_bytes());
    reader.deserialize().collect()
}
```

All right, we seem to be parsing some customer data from a CSV file.

You look at line 847 of the input file and see corrupted character encoding.
You remove the bad line, deploy a fix, and go back to sleep. 

## Don't Be Clever

Rust programmers tend to be very clever.
Too clever for their own good at times.
Let me be the first to admit that I'm guilty of this myself.

We love to stretch Rust to its limits.
After all, this is Rust! 
An empowering playground of infinite possibility.
Shouldn't we use the language to its full extent?

Nothing in Rust forces us to get fancy. 
You can write straightforward code in Rust just like in any other language.
But in code reviews, I often see people trying to outsmart themselves and stumble over their own shoelaces.
They use all the advanced features at their disposal without thinking much about maintainability.

But here's the problem: [Writing code is easy. Reading it isn't.](https://idiallo.com/blog/writing-code-is-easy-reading-is-hard)
These advanced features are like salt: a little bit can enhance the flavor, but too much can ruin the dish.
And advanced features have a tendency to overcomplicate things and make readability harder.

Software engineering is all about managing complexity, and complexity creeps in when we're not looking.
We should focus on keeping complexity down.

Good code is mostly boring; especially for production use.
Simple is obvious.
Simple is predictable.
Predictable is good.

And simplicity also makes systems more reliable:

> Simplicity is prerequisite for reliability.

I don't always agree with Edsger W. Dijkstra, but in this case, he was spot-on.
Without simplicity, reliability is impossible (or at least hard to achieve).
That's because simple systems have fewer moving parts to reason about. 

## Why Simple is Hard 

But if simplicity is so obviously "better," why isn't it the norm?
Because achieving simplicity is hard!
It doesn't come naturally.
Simplicity is typically not the *first attempt* but the *last revision*. [^pascal]

[^pascal]: I think there's a similarity to writing here, where elegance (which is correlated with simplicity, in my opinion) requires an iterative process of constant improvement. The editing process is what makes most writing great. In 1657, Blaise Pascal famously wrote: "I have only made this letter longer because I have not had the time to make it shorter." I think about that a lot when I write.

> Simplicity and elegance are unpopular because they require hard work and discipline to achieve.

Well put, Edsger.

It takes *effort* to build simple systems.
It takes even more effort to *keep* them simple.
That's because you constantly have to fight [entropy](https://en.wikipedia.org/wiki/Entropy). 
Going from simple to more complex is much easier than the reverse.

Let's come back to our 3 AM phone call.

The first version of the code was built by an engineer who wanted to make the system "flexible and extensible."
The second was written by a developer who just solved the problem at hand and tried to parse a CSV file.
Turns out there was never once a need to parse anything other than CSV files.

One lesson here is that the path to complexity is paved with good intentions.
**A series of individually perfectly reasonable decisions can lead to an overly complex, unmaintainable system.**

More experienced developers tend to use more abstractions because they get excited about the possibilities.
And I can't blame them, really.
Writing simple code is oftentimes pretty boring.
It's much more fun to test out that new feature we just learned.
But after a while we forget how Rust beginners feel about our code: it's the [curse of knowledge](https://en.wikipedia.org/wiki/Curse_of_knowledge).

Remember: **abstractions are never zero cost.** [^nasa]
[^nasa]: For reference, see ["The Power of 10 Rules"](https://web.eecs.umich.edu/~imarkov/10rules.pdf) by Gerard J. Holzmann of the NASA/JPL Laboratory for Reliable Software.

> Not all abstractions are created equal.  
>
> In fact, many are not abstractions at all — they're just thin veneers, layers of
> indirection that add complexity without adding real value.
>
> -- [Fernando Hurtado Cardenas](https://fhur.me/posts/2024/thats-not-an-abstraction)

Abstractions cause complexity, and complexity has a very real cost.
At some point, complexity will slow you down because it causes cognitive load.
And cognitive load matters a lot.

The people who are starting with Rust are often overwhelmed by the complexity of the language.
Try to keep that in mind as you get more proficient with Rust.
If you fail to do that, you might alienate team members who are not as experienced as you, and they might give up on the project or Rust altogether.

Furthermore, if you leave the company and leave behind a complex codebase, the team will have a hard time maintaining it and onboarding new team members.
The biggest holdup is [how quickly people will be able to get up to speed with Rust](/blog/flattening-rusts-learning-curve).
Don't make it even harder on them.
From time to time, look at Rust through beginner's eyes.

## Generics Are A Liability

For some reason I feel compelled to talk about generics for a moment...

Not only do they make the code harder to understand, they can also have a real cost on compile times.
Each generic gets monomorphized, i.e. a separate copy of the code is generated for each type that is used with that generic at compile time.

My advice is to only make something generic if you need to switch out the implementation *right now*.
Resist premature generalization!
(Which is related -- but not identical to -- premature optimization.)

"We might need it in the future" is a dangerous statement.
Be careful with that assumption because it's hard to predict the future. [^future]
[^future]: I should know because I passed on a few very risky but lucrative investment opportunities because I lacked the ability to accurately predict the future.

Your beautiful abstraction might become your biggest nemesis.
If you can defer the decision for just a little longer, it's often better to do so.

Generics have an impact on the "feel" of the entire codebase.
If you use a lot of generics, you will have to deal with the consequences everywhere.
You will have to understand the signatures of functions and structs as well as the error messages that come with them.
The hidden compilation cost of generics is hard to measure and optimize for.

Be careful with generics.
They have a real cost!
The thinking should be "this is generic functionality" instead of "I could make this generic."

Let's say you are working on a public API.
A function that will be used a lot will need to take some string-based data from the user.
You wonder whether you should take a `&str` or a `String` or something else as an input to your functions and why.

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
But do you see how the complexity goes up?

Behind the scenes, it monomorphizes the function for each type that implements `AsRef<str>`.

That means that if we pass a `String` and a `&str`, we get two copies of that function.
That means longer compile times and larger binaries.

The problem is so simple, so how did that complexity creep in?
We're trying to be clever.
We are trying to make the function "better" by making it more generic.
But is it really "better"?

All we wanted was a simple function that takes a string and does something with it.

Stay simple.
Don't overthink it!

Say we're writing a [link checker](https://github.com/lycheeverse/lychee) and we want to build a bunch of requests to check the links.
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

The iterator doesn't look too bad, but the vec is simpler.
What to do?
The caller likely needs to collect the results anyway.
Since we're processing a finite set of URLs, the link checker needs all results to report successes/failures, and the results will probably be iterated multiple times.
Memory usage isn't a big concern here since the number of URLs in a document is typically small.
All else being equal, the vec is probably the simpler choice. 

## Simple Code Is Often Fast Code 

There's a prejudice that simple code is slow. 
Quite the contrary!
It turns out many effective algorithms are surprisingly simple.
In fact, some of the simplest algorithms we've discovered are also the most efficient.

Take quicksort or path tracing, for example.
Both can be written down in a handful of lines and described in a few sentences.

Here's an ad-hoc version of quicksort in Rust:

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

1. If the list is empty or has one element, it's already sorted and we're done.
2. If not, pick a random element as the pivot. (For simplicity, we pick the first element here.)
3. Split the list into two sublists: elements smaller than the pivot and elements larger than or equal to the pivot.
4. Sort each sublist recursively.
5. By combining the sorted smaller list, the pivot, and the sorted larger list, you get the fully sorted list!

The implementation is not too far off from the description of the algorithm.

Yes, my simple version only supports `usize` right now, but my point is that simple algorithms pack a punch.
This is an O(n log n) algorithm.
It's as fast as it gets for a comparison-based sort and it's just a few lines of code. [^optimization]

[^optimization]: Of course, this is not the most efficient implementation of quicksort. It allocates a lot of intermediate vectors and has O(n^2) worst-case performance. There are optimizations for partially sorted data, better pivot selection strategies, and in-place partitioning. But they are just that: optimizations. The core idea remains the same.

Often, simple code can be optimized by the compiler more easily and runs faster on CPUs.
That's because CPUs are optimized for basic data structures and predictable access patterns.
And parallelizing work is also easier when that is the case.
All of that works in our favor when our code is simple.

Somewhat counterintuitively, especially when you're doing something complicated, you should be extra careful to keep it simple.
Simplicity is a sign of deep insight, of great understanding, of clarity—and clarity has a positive effect on the way a system functions.
And since complicated systems are, well, complicated, that extra clarity helps keep things under control.

What I appreciate about Rust is how it balances high-level and low-level programming.
Most of the time, I write Rust code in a straightforward manner, and when that extra bit of performance becomes critical, Rust always lets me go back and optimize. 

## Keep Your Fellow Developers in Mind 

Most of the code you'll write for companies will be application code, not library code.
That's because most companies don't make money writing libraries, but business logic.
There's no need to get fancy here.
Application code should be straightforward.

Library code can be a slightly different story.
It can get complicated if it ends up being an important building block for other code. 
For example, in hot code paths, avoiding allocations might make sense, at which point you might have to deal with [lifetimes](/blog/lifetimes).
This uncertainty about how code might get used by others can lead to overabstraction.
Try to make the common case straightforward.
The correct path should be the obvious path users take.

Say you're building a base64 encoder.
It's safe to assume that most people will want to encode a string (probably a unicode string like a `&str`) and that they want to use a "canonical" or "standard" base64 encoding.
Don't expect your users to jump through hoops to do the *most common thing*.
Unless you have a *really* good reason, your API should have a function like this somewhere:

```rust
/// Encode input as Base64 string
fn base64_encode(input: &str) -> String;
```

Yes, you could make it generic over `AsRef<[u8]>` or support multiple alphabets:

```rust
/// Generic base64 encoder supporting multiple alphabets
fn base64_encode<T: AsRef<[u8]>>(input: T, alphabet: Base64Alphabet) -> String;
```

...and you might even offer a builder pattern for maximum flexibility:

```rust
let encoded = Base64Encoder::new()
    .with_alphabet(Base64Alphabet::UrlSafe) // What is UrlSafe?
    .with_decode_allow_trailing_bits(true) // Huh?
    .with_decode_padding_mode(engine::DecodePaddingMode::RequireNone); // I don't even...
    .encode("Hello, world!");
```

But all that most users want is to get an encoded string:

```rust
let encoded = base64_encode("Hello, world!");
```

You could call the function above `base64_encode_simple` or `base64_encode_standard` to make it clear that it's a simplified version of a more generic algorithm.
It's fine to offer additional functionality, but don't make the easy thing hard in the process.

Simplicity is especially important when working with other developers because code is a way to communicate ideas, and you should strive to express your ideas clearly.

## Tips For Fighting Complexity

### Start Small

Jerry Seinfeld had two writing modes: [creating mode and editing mode](https://perell.com/note/the-jerry-seinfeld-guide-to-writing/).
- When in creation mode, he's exploring possibilities and letting ideas flow freely.
- When in editing mode, he's refining, cutting, and polishing.

These modes require different mindsets, and trying to do both simultaneously leads to paralysis.
As a consequence, Seinfeld would never edit while creating because it would kill the creative flow.

The same principle applies to coding.
Don't try to architect the perfect solution on your first attempt.
Write the naive implementation first, then let your inner editor refine it. 
Switch off that inner critic.
Who knows?
You might just come up with a simpler design.

### Resist the Temptation To Optimize Early

It can be tempting to use all of these fine, sharp tools you have at your disposal.
But sharp tools they are!
To master Rust is to say "no" to these tools more often than you say "yes."

You might see an optimization opportunity and feel the urge to jump at it. 
But time and again, I see people make that optimization without prior validation.
Measure twice, cut once. 

### Delay Refactoring 

That might sound counterintuitive.
After all, shouldn't constant refactoring make our code better as we go?

The problem is that we have limited information at the time of writing our first prototype.
If we refactor too early, we might end up in a worse place than where we started.

Take the CSV exporter from the beginning as an example: a smart engineer saw an opportunity to refactor the code in order to support multiple input formats.
That locked us into a place where we had a generic exporter, which became a huge debugging burden while preventing us from seeing a better abstraction had we deferred the refactoring.
Maybe we would have noticed that we're always dealing with CSV data, but we could decouple data validation from data exportation.
If we had seen that, it would have led to better error messages like:

```
Error: Customer 123 has invalid address field: invalid UTF-8 sequence at byte index 23: Address: "123 M\xE9n St."
```

This opportunity was lost because we jumped the gun and refactored too early.

I propose solving the problem at hand first and refactoring afterward. 
That's because refactoring a simple program is way easier than doing the same for a complex one. 
Everyone can do the former, while I can count on one hand those who can do the latter.
Preserve the opportunity to refactor your code.
Refactoring might look like the smart thing to do at the time, but if you allow the simple code to just stick around for a little longer, the right opportunity for the refactor will present itself.

A good time to reflect is when your code starts to feel repetitive. 
That's a sign that there's a hidden pattern in your data.
The right abstraction is trying to talk to you and reveal itself!
It's fine to do multiple attempts at an abstraction.
See what feels right.
If none of it does, just go back to the simple version and document your findings.

### Performance Crimes Are "OK"

Rust is super fast, so you can literally make all the performance crimes you want.
Clone liberally, iterate over the same data structure multiple times, use a vector if a hashmap is too daunting.

It simply doesn't matter.
Hardware is fast and cheap, so put it to work.

### Be Curious But Conservative 

All of the above doesn't mean you should not learn about all of these abstractions.
It's fun to learn and to be knowledgeable. 

But you can focus on learning new concepts without hurting yourself.
Understanding macros, lifetimes, interior mutability, etc. is very helpful, but in everyday "normal" Rust code you almost never make use of these concepts, so don't worry about them too much.

Use all the features you need and none that you don't.

## How to Recognize The Right Level of Abstraction 

One litmus test I like to use is "Does it feel good to add new functionality?"

Good abstractions tend to "click" together. 
It just feels like there's no overlap between the abstractions and no grunt work or extra conversions needed.
The next step always feels obvious.
Testing works without much mocking, your documentation for your structs almost writes itself.
There's no "this struct does X and Y" in your documentation.
It's either X **or** Y.
Explaining the design to a fellow developer is straightforward.
This is when you know you have a winner.
Getting there is not easy.
It can take many iterations.
What you see in popular libraries is often the result of that process.

The right abstractions guide you to do the right thing: to find the obvious place to add new functionality, the right place to look for a bug, the right spot to make that database query. 

All of that is easier if the code is simple.
That's why experienced developers always have simplicity in mind when they build out abstractions.

It's possible that the most common error of a smart engineer is to optimize a thing that should not exist in the first place.
Cross that bridge when you get there.

## Write Code for Humans

Be clear, not clever.
Write code for humans, not computers.

Simplicity is clarity.
Simplicity is to succinctly express the essence of a thing.
Simplicity is about removing the unnecessary, the irrelevant, the noise.
Simple is good.
Be simple.