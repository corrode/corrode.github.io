+++
title = "Be Simple"
date = 2025-08-26
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

Rust developers tend to be clever. Too clever for their own good. 
In code reviews, I often see people trying to outsmart themselves. 

We love to stretch Rust to its limits. You might think you're an imposter. After all, this is Rust. Shouldn't you know? Shouldn't you use it to its full extent? Will people find out you're an imposter? There is a tendency in the Rust community to be correct. Especially in Rust, there is a tendency to overcomplicate things. That is not a limitation with the language, but a mindset. Nothing in Rust forces you to make things harder than they should be.



## What Simple Really Means

 Good code is mostly boring; especially for production use. Be clear, not clever. Write Code for Humans, Not Computers. Software engineering is all about managing complexity. Simple is obvious. Simple is predictable, predictable is good.

> "Simplicity is prerequisite for reliability."

I don't always agree with Edsger W. Dijkstra, but in this case, I think he was spot-on.

Advanced features are like salt: a little bit can enhance the flavor, but too much can ruin the dish. As in life, complexity creeps in when you're not looking.

## Why Simplicity is Hard Work

But make no mistake: Being simple is hard work! It doesn't always come naturally. "Simplicity and elegance are unpopular because they require hard work and discipline to achieve" — Edsger Dijkstra. "simplicity is also not the first attempt but the hardest revision". It takes effort to build simple systems. It takes effort to *keep* them simple. Going from simple to more complex is much easier than the reverse.

## The Hidden Costs

The path to complexity is paved with good intentions. "fight entropy. a series of individually completely rational and reasonable decisions can lead to a completely unreasonable, overly complex, and unmaintainable system". "Abstractions are never zero cost." - NASA - The Power of Ten. Complexity has a cost. At some point, complexity will slow you down. Cognitive load is what matters.

## The Rust Challenge

We forget how Rust beginners feel. It's the curse of knowledge. More experienced developers tend to use more abstractions because they get excited about the possibilities. Learning is addictive, so I can relate to that. The people who are starting with Rust are often overwhelmed by the complexity of the language. Keep that in mind. If you fail to do that, you might alienate the team members who are not as experienced as you are and they might give up on the project or Rust altogether. Furthermore, if you leave the company and you leave behind a complex codebase, the team will have a hard time maintaining it and onboarding new team members. The biggest holdup is how quickly people will be able to get up to speed with Rust. Don't make it even harder on them.

## How to Fight Complexity

### Start Simple

Start with the easiest solution possible. Switch off the inner critic. Gerry Seinfeld had two writing modes. It's always crucial to know which one you're in. One way to avoid complexity is to write a draft about what you're doing.

### Resist the Temptation

It can be tempting to use all of these fine, sharp tools you have at your disposal. But sharp tools they are. You might see an optimization opportunity. I advice you to keep protocols simple. Time and again, I saw people overengineer their code for no reason and without prior measurements. To master Rust is to say no to these tools more often than you say yes.

### Are Generics Worth It?

Generics are a liability. Not only do they make the code harder to understand, they can also have a real cost on compile times (monomorphization). Only make generic what you need to switch out. Think: "this is generic functionality" instead of "I could make this generic". Abstractions have an impact on the style of the entire codebase. So if you use a lot of abstractions, you will have to use them everywhere. So be careful with abstractions. They have a cost.

### Performance Crimes Are OK

Rust is super fast, so you can literally make all the performance crimes you want. Clone freely, iterate multiple times, use a vector if a hashmap is tedious. 

It. Simply. Doesn't. Matter.

Hardware is fast. Put the hardware to work.

## Where Complexity Hides

### String Parameters

Say you are working on a public API. A function that will be used a lot will need to take some string based data from the user. You are confused if you should take a `&str` or a `String` or something else as an input to my functions and why?

```rust
fn process_user_input(input: &str) {
    // do something with input
}
```

That's quite simple and doesn't allocate. But what if the caller wants to pass a String?

```rust
fn process_user_input(input: String) {
    // do something with input
}
```

We take ownership of the input. But what if we don't need ownership and we want to support both?

```rust
fn process_user_input(input: impl AsRef<str>) {
    // do something with input
}
```

That works. But in the background it monomorphizes the function for each type that implements AsRef<str>.

That means that if we pass a `String` and a `&str`, we get two copies of the function.

That means longer compile times and larger binaries.

See how the complexity creeps in?

All we wanted was a simple function that takes a string and does something with it.

Stay simple. Don't overthink it.

### Vec or Iterator?

Say we're writing a link checker and we want to build a bunch of requests to check the links. We could use a function that returns a `Vec<Result<Request>>`.

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

Alternatively, we could return an iterator:

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

The iterator doesn't look too bad. The vec is simpler. What to do? The caller likely needs to collect the results anyway since we're processing a finite set of URLs, the link checker needs all results to report successes/failures, and the results will probably be iterated multiple times. Memory usage isn't a big concern since the number of URLs in a document is typically small, we've already allocated for the input Vec, and the original HashSet was allocating anyway. But if neither applies, the Vec is the simpler and more idiomatic choice.

## Refactoring Simple Code

Refactoring a simple program is way easier than making a complex program simple. Everyone can do the former, while I can count the one who can do the latter. Preserve the opportunity to refactor your code. Just like premature optimization, premature refactoring can get in your way. Not every possible abstraction is worth adding. It might look like the clever thing to do at the time, but if you allow the simple code to just stick around for a while, you'll eventually see the right opportunity for the refactor. Like a sore thumb, it will be obvious once you see it. A good time to reflect is when your code starts repeating a lot. There's a hidden pattern in your data. It's trying to talk to you, to reveal itself. It's fine to do multiple attempts at an abstractions. See what feels right. If none of it does, just go back to the simple version.

## How Do You Know It's Good?

Watching experienced developers write code feels like they have a constant interaction with the data and the building blocks they are working with. It "clicks" once it fits. It just feels like there's no overlap between the abstraction and no extra work or conversions needed. The next step feels obvious. Testing works without much mocking, your documentation for your structs almost writes itself. There's no "this struct does X and Y" in your documentation. It's just X and Y separated. Explaining the parts to a fellow developer is straightforward. This is when you know you have a winner. Getting there is not easy. It takes many iterations. It is easier if the code is simple in the beginning.

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

This also applies to variable names. Don't be too clever. Be explicit. The broader the scope, the more explicit you should be. Meaningful variable names are one of the easiest way to document intent and purpose. We are no longer constrained by the length of variable names and autocomplete fixes typing mostly, so don't be too greedy.

## DRY is Overrated

On that note, DRY is also overrated. Feel free to repeat yourself. Don't try to avoid repetition at all costs. It usually leads to dense, hyper-optimized code that is hard to decipher. It is a fool's errand to try to avoid repetition at all costs. It's better to have a bit of repetition than to have a complex abstraction that is hard to undo. Developer experience suffers when you have to deal with complex abstractions. "Greppability" is a good metric for code quality.

## But What About Performance?

But isn't simple code bad for performance? Turns out many simple algorithms are surprisingly effective. Take quicksort or path tracing for example. Both can be written down in a handful of lines.

Even selection sort is plenty fast.

```rust
fn sort(input: &mut [usize]) {
    let length = input.len();
    for i in 0..length {
        for j in i + 1..length {
            if input[i] > input[j] {
                input.swap(i, j);
            }
        }
    }
}
```

This is an O(n^2) algorithm, but did you know that this can sort 100,000 integers in 30 milliseconds on my laptop? 
Yes, it's not it only works for small inputs and only supports `usize` right now, but my point is that simple algorithms pack a punch.

Of course, there are optimizations like timsort or radiosity, but these are more complex and add only incremental perf improvements. Simple algorithms are also often trivial to parallelize. Complex algorithms have edge-cases that make that harder. "The thing I really like about Rust is it feels like both a high and low level language. 95% of the time I write Rust code in very simple, smooth brain, procedural ways. But 5% of the time where I really need to crank out performance, I have the option to crack open godbolt and do some low level analysis."



## Build for Teams

Clarity is really important if you work in a team. Make life easier for your colleagues. Application code should be simple but library code can be complicated if it typically is a bottleneck. But don't overdo it. Say you're building a base64 encoder. Keep that simple. Make the common case simple to use. For example, if you're writing a base64 encoder, it's safe to assume that most people will want to encode a string (i.e. a unicode string, `&str`) and that they want to use a "canonical" or "standard" base64 encoding. Don't expect your users to jump through hoops to do the most common thing.

```rust
/// Simple base64 encoder using standard alphabet
fn base64_encode(data: &str) -> String;
```

No need to make it generic over `AsRef<[u8]>` or support multiple alphabets. 

```rust
/// Generic base64 encoder supporting multiple alphabets
fn base64_encode<T: AsRef<[u8]>>(data: T, alphabet: Base64Alphabet) -> String;
``` 

## Keep Learning

All of the above doesn't mean you should not learn about all of these abstractions. It's fun to be competent. Really what I mean is: don't add any additional complexity. When teaching Rust: `unwrap()` and `clone()` are like training wheels for bikes. People can focus on learning new concepts without hurting themselves. Understanding lifetimes, interior mutability, etc. is great, but in "normal" code you almost never make use of these concepts, so don't worry about them too much. Use all the features you need and none that you don't.

## Moving Forward

Start simple and do smaller iterations. Invest time in exploratory analysis. You might come up with a simpler design. Be careful with assumptions. Put your assumptions to the test. "We might need it in the future" is a dangerous assumption. "Be even more careful to keep it simple when you're doing something complicated." It's possibly the most common error of a smart engineer to optimize a thing that should not exist. Cross that bridge when you get there.

## The Courage to Be Simple

It takes courage to be simple. What shall your colleagues think when they review your code? What about the internet if you make it open source? It's hard to predict the future. Your beautiful abstraction might become the biggest hurdle. Ignore that inner critic for now. "For the simplicity on this side of complexity, I wouldn't give you a fig. But for the simplicity on the other side of complexity, for that I would give you anything I have." Simple is good. Be simple. Simplicity is about removing clutter - the unnecessary, the irrelevant, the noise. Simplicity is to succinctly express the essence of a thing. Simplicity is clarity. Clarity affects the way a system functions.
