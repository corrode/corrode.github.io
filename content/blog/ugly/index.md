+++
title = "When Rust Gets Ugly"
date = 2026-06-19
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

In workshops I often see people getting frustrated with Rust.

Here's some of the feedback I hear:

- "The borrow checker rules make it hard to write code that compiles."
- "It's overwhelming! The syntax is complex with too many symbols and operators. [^keywords]"
- "It's difficult to transition to Rust from <this other language I know>."
- "The code is not satisfying to read, it feels clunky and verbose."

[^keywords]: It turns out that all 48 Rust keywords can [fit into 300 characters](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=c1c8e31332776002d7030e2e242ebcee), so there isn't a crazy amount to begin with.

From these frustrations, people often conclude that Rust is not for them and quit.

But after programming in Rust for 10 years, I think that **your coding style has the biggest impact on how your Rust code will look and feel**.

People often say Rust's syntax is ugly, but I'd argue the syntax is the least interesting thing about Rust. The **semantics** (the bits and pieces the language provides to express your ideas and how those bits combine to build interesting things) are much more important.

The "ugliness" is only skin-deep; Rust's beauty lies underneath the surface!
And with better semantics comes better syntax.

If you feel like you're fighting the language, then there's a chance that **the language is speaking to you**.
It tries to push you into a healthier direction, but if you resist, it will patiently wait until you give in.
The moment you start to listen to what Rust is trying to teach you, everything snaps into place; writing Rust feels effortless.

**Better semantics unlock nicer syntax.**
That means, the more you lean into the core mechanics behind Rust (traits, pattern matching, expressions, composition over inheritance, etc.), the more you can build on these concepts to write code that is readable and extensible.
The syntax takes a backseat. It gives way to semantics, which are much more important.

If you write Rust like you would write idiomatic code in another language, it will *never feel right*.
You have to embrace how Rust wants you to structure your code.
"You can write bad Java code in any language," is a common saying, and I think it applies here as well.

Good Rust can tick all the boxes: it's correct, readable, *and* maintainable.
Heck, I'd say it's pretty, too!

## Parsing Things

Let's consider a simple example: parsing an `.env` file in Rust. How hard can it be?

```sh
DB_HOST=localhost
DB_PORT=5432

API_KEY=my_api_key
LOG_FILE=app.log
```

The goal is to parse the above content from a file called `.env` and return a data structure that contains the key-value pairs.
Child's play.

I invite you to write your own version first.
Or at least take a second to think about the problem.

Then we'll refactor a deliberately clunky first attempt into more idiomatic Rust and use that process to extract a general approach: read the standard library, lean on inference and types, handle errors explicitly, and split the problem into smaller parts.

## A Painful First Attempt

A Rust learner will sit down and attempt to parse the above file.
They might come up with a solution like the one below, which is not too far from what I've seen recently.

```rust
use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use std::path::Path;

// Parse .env file into a HashMap
fn parse_config_file<'a>(path: &'a str) -> HashMap<String, String> {
    let p = Path::new(&path);
    let mut file = File::open(&p).unwrap();
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes).unwrap();

    let s = String::from_utf8_lossy(&bytes).to_string();

    let lines_with_refs: Vec<&'_ str> = s.split('\n').collect();

    let mut idx = 0;
    let mut cfg: HashMap<String, String> = HashMap::new();

    // Iter lines
    while idx < lines_with_refs.len() {
        // Get the line reference and trim it
        let lref = &lines_with_refs[idx];
        let mut l = *lref;
        l = l.trim();

        // Skip empty lines
        if l.len() == 0 {
            idx += 1;
            continue;
        }

        // Skip comments
        if l.chars().next() == Some('#') {
            idx += 1;
            continue;
        }

        // Actual string splitting and trimming
        let parts = l.split('=').collect::<Vec<&str>>();
        let k: &str = parts[0].trim();

        // Check if key is empty
        if k.len() > 0 {
            // We found a valid key. Insert into config
            let v: &str = parts[1].trim();
            cfg.insert(k.to_string(), v.to_string());
        } else {
            // This only happens if the line is malformed, so skip
            println!("Error in line {:?}", parts);
        }

        // Process next line
        idx += 1;
    }

    return cfg;
}

fn main() {
    // Parse a `.env` file in the current directory.
    let config = parse_config_file(".env");
    println!("{config:#?}");
}
```

The code carries all the hallmarks of a beginner Rust programmer, possibly with a C/C++ background.

- Littered with `unwrap()` calls
- Unnecessary mutability
- Manual indexing into arrays[^panic]
- Lifetime annotations
- Cryptic variable names
- Imperative coding style

[^panic]: That manual indexing hides a latent bug: `parts[1]` is accessed without checking the length, so the parser happily panics at runtime on any line that doesn't contain an `=` (a stray `justkey`, say). The compiler can't save you here; you have to remember to handle it yourself.

Let's be clear: there are many, many antipatterns in the above code,
but the most important observation is that these antipatterns have nothing to do with Rust itself.
They are bad coding practices in general.

The learner has not yet fully embraced the ergonomics Rust provides and might be skeptical about performance implications of higher-level abstractions.

We will get back to this code later, but note how Rust makes all of these problems painfully explicit.
It looks painful, because it is: the abstractions are too low level for the problem at hand.

Refusal to rethink your coding style in light of Rust's design principles not only makes your code harder to read; worse, it slows down your learning process.

Down the road, it also leads to business logic bugs in the code, because the compiler can't help you catch them.

## Let Go Of Old Bad Habits

So how can you do better?

The first step is to acknowledge that your existing code goes against Rust's design principles.
It's a band-aid around outdated ideas from the past still haunting you and holding back your progress.
**Ugly Rust code is a symptom of old, bad habits.**

Based on this realization, we can systematically improve the code.
While we go through the refactoring, keep in mind that there is no single "right" way to improve the code, but that it all depends on the context and your goals.

There are a few techniques that can help you write better Rust, some of which we've discussed before:

- [Think in expressions](/blog/expressions)
- [Immutability by default](/blog/immutability)
- [Lean into the typesystem](/blog/illegal-state)
- [Use iterator patterns](/blog/iterators)
- [Read the standard library documentation](https://doc.rust-lang.org/std/)
- Use proper error handling
- Split up the problem into smaller parts

Even just applying these basic techniques, we can get our code into a much better shape.

{% info(title="Before You Continue: Try It Out Yourself!") %}

This is a hands-on exercise.
Feel free to paste the above code into your editor and practice refactoring it. 
Here's the [link to the Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=2510df77c1c8c6a227680ea49407fe18).
At the end, there will be a little quiz to see if you found all the edge-cases.
I'll wait here.

{% end %}

## Tip #1: Read the Standard Library Documentation

Many common patterns are beautifully handled by the standard library.
It is absolutely worth your time to [read the documentation](https://doc.rust-lang.org/std/) and even its source code.
For example, you will find that you can get rid of all of this boilerplate:

```rust
let p = Path::new(&path);
let mut file = File::open(&p).unwrap();
let mut bytes = Vec::new();
file.read_to_end(&mut bytes).unwrap();
let s = String::from_utf8_lossy(&bytes).to_string();
```

and instead just call [`read_to_string`](https://doc.rust-lang.org/std/fs/fn.read_to_string.html):

```rust
let s = std::fs::read_to_string(path).unwrap();
```

## Tip #2: Use Type Inference

[Rust is really good at inferring types.](https://rustc-dev-guide.rust-lang.org/type-inference.html) That's why we don't need to specify the type of
our `HashMap` explicitly.

```rust
let mut cfg: HashMap<String, String> = HashMap::new(); 
```

becomes

```rust
let mut cfg = HashMap::new();
```

## Tip #3: Lean Into the Typesystem

Manual string splitting is error-prone and very much discouraged.
The reason is that strings are, in fact, really complicated!
There is an outdated assumption that strings are just an array of bytes, but that assumption is ill-defined and dangerous.
It is not true for all modern operating systems, including Windows, macOS, and Linux and you should stop thinking about strings that way.

Even in our simple example code from above, string splitting turns out to be a common source of bugs: 

```rust
let lines_with_refs: Vec<&'a str> = s.split('\n').collect();
```

This line expects that lines are separated by `\n`.
That's not true on Windows, where lines are separated by `\r\n`.

The following line does the right thing on all platforms:

```rust
let lines = s.lines();
```

This returns an [iterator over the lines of a string](https://doc.rust-lang.org/std/primitive.str.html#method.lines).
Knowing that, we can instead iterate over each line:

```rust
for line in s.lines() {
    let line = line.trim();

    // ...
}
```

Note that we shadow `line` with `line.trim()`.
That is a common practice in Rust and very useful to keep the code clean.

It means we don't have to come up with a fancy new name for the trimmed line
and we also don't have to fall back to cryptic names like `lref` or `l` instead.

By reading the standard library documentation (see tip 1), we learn about some useful methods on strings.
So instead of `line.len() == 0`, we write `line.is_empty()` now.
And `line.starts_with("#")` is easier on the eye than checking with `l.chars().next() == Some('#')`.

```rust
for line in s.lines() {
    let line = line.trim();
    if line.is_empty() || line.starts_with("#") {
        continue;
    }
    // ...
}
```

Next, let's tackle this part:

```rust
let parts = l.split('=').collect::<Vec<&str>>();

let k: &str = parts[0].trim();
if k.len() > 0 {
    let v: &str = parts[1].trim();
    cfg.insert(k.to_string(), v.to_string());
} else {
    println!("Error in line {:?}", parts);
}
```

Note how we access `parts[0]` and `parts[1]` without checking if these are valid indices. 
The code only coincidentally works for well-formed inputs. 
We could add a check to make sure that `parts` has at least two elements:

```rust
if parts.len() >= 2 {
    let k: &str = parts[0].trim();
    if k.len() > 0 {
        let v: &str = parts[1].trim();
        // insert into config
    } else {
        // handle empty key
    }
} else {
    // handle line error
}
```

But that's equally clunky and verbose.
Fortunately, we don't have to do any of that if we lean into the typesystem a little more and use pattern matching to destructure the result of `split_once`:

```rust
match line.split_once('=') {
    Some((k, v)) => {
        let k = k.trim();
        if k.is_empty() {
            println!("Error in line with empty key");
        } else {
            let v = v.trim();
            config.insert(k.to_string(), v.to_string());
        }
    }
    None => println!("Error in line: no '=' found"),
}
```

With that, we end up with an already greatly simplified (but equally performant!) version of the code:

```rust
use std::collections::HashMap;
use std::fs::read_to_string;

fn parse_config_file(path: &str) -> HashMap<String, String> {
    let s = read_to_string(path).unwrap();

    let mut config = HashMap::new();
    for line in s.lines() {
        let line = line.trim();

        if line.is_empty() || line.starts_with("#") {
            continue;
        }

        match line.split_once('=') {
            Some((k, v)) => {
                let k = k.trim();
                if k.is_empty() {
                    println!("Error in line with empty key");
                } else {
                    let v = v.trim();
                    config.insert(k.to_string(), v.to_string());
                }
            }
            None => println!("Error in line: no '=' found"),
        }
    }

    config
}
```

Much nicer.
However, to truly embrace Rust, it always helps to take a step back and think about the root of the problem.
This is where you can really grow as a programmer.

## Tip #4: Don't Gloss Over Error Handling

We left a few things on the table so far; one obvious one is error handling.
How you want to handle invalid lines depends on the business logic, but let's assume we want to immediately return an error if the file is malformed.

The function itself stays close to what we had; it just returns a `Result` now and uses `?` to bubble up I/O errors:

```rust
use std::collections::HashMap;
use std::fs::read_to_string;

fn parse_config_file(path: &str) -> Result<HashMap<String, String>, ParseError> {
    let s = read_to_string(path)?;

    let mut config = HashMap::new();
    for line in s.lines() {
        let line = line.trim();

        if line.is_empty() || line.starts_with("#") {
            continue;
        }

        match line.split_once('=') {
            Some((k, v)) => {
                let k = k.trim();
                if k.is_empty() {
                    return Err(ParseError::InvalidLine(line.to_string()));
                } else {
                    let v = v.trim();
                    config.insert(k.to_string(), v.to_string());
                }
            }
            None => return Err(ParseError::InvalidLine(line.to_string())),
        }
    }

    Ok(config)
}
```

The supporting `ParseError` type is mostly mechanical. We implement `Display` and
`Error` so it plays nicely with the rest of the error ecosystem, and a `From<std::io::Error>`
so that the `?` on `read_to_string` just works:

```rust
use std::fmt;
use std::error::Error;

#[derive(Debug)]
enum ParseError {
    InvalidLine(String),
    IoError(std::io::Error),
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ParseError::InvalidLine(line) => write!(f, "Invalid line format: {line}"),
            ParseError::IoError(err) => write!(f, "I/O error: {err}"),
        }
    }
}

// An empty body is fine here; we lean on the default `source()`.
impl Error for ParseError {}

impl From<std::io::Error> for ParseError {
    fn from(err: std::io::Error) -> Self {
        ParseError::IoError(err)
    }
}
```

In real projects, I often reach for [`thiserror`](https://docs.rs/thiserror/latest/thiserror/) to remove most of that boilerplate without hiding the important part: which errors can happen.
The same error type becomes:

```rust
use thiserror::Error;

#[derive(Debug, Error)]
enum ParseError {
    #[error("Invalid line format: {0}")]
    InvalidLine(String),
    #[error("I/O error: {0}")]
    IoError(#[from] std::io::Error),
}
```

Granted, our code has gotten quite a bit more verbose again.
But in comparison to the original code, the verbosity has a purpose: it marks the various bits and pieces of our code that can go wrong.
We have agency to decide how to handle these errors gracefully on the call site rather than silently ignoring them.

Some errors are harder to handle than others.
For example, we can choose to skip invalid lines, or we could decide to return a collection of all the errors we encountered while parsing the file. 
This and more we can express in code now.

## Tip #5: Break Up The Problem

The "meat" of the parser is the part that parses individual lines.
This is still buried in the single `parse_config_file` function, which has quite a lot of responsibilities
such as reading the file, iterating over lines, and parsing each line.
That causes a bunch of problems.
For one, we can't test the line parsing logic in isolation.

Since parsing lines is such a core part of the business logic, let's make sure it gets the attention it deserves.
For starters, let's move the line parsing logic into its own function. 

```rust
fn parse_line(line: &str) -> Result<Option<(String, String)>, ParseError> {
    let line = line.trim();

    if line.is_empty() || line.starts_with("#") {
        return Ok(None);
    }

    match line.split_once('=') {
        Some((k, v)) => {
            let k = k.trim();
            if k.is_empty() {
                Err(ParseError::InvalidLine(line.to_string()))
            } else {
                let v = v.trim();
                Ok(Some((k.to_string(), v.to_string())))
            }
        }
        None => Err(ParseError::InvalidLine(line.to_string())),
    }
}
```

Don't worry about the ugly function signature for now; we get back to that in a second.
In fact, it is a tell-tale sign that we're still not quite done yet.

**In Rust, code that feels "stringy-typed" is usually a sign of a missing abstraction.**

In our case, the `Result<Option<(String, String)>>` type indicates that we are trying to parse a line that may or may not contain a key-value pair, and that parsing can fail.
That is a good start for thinking about our missing abstraction.

We need to represent a few different outcomes of parsing a line:

- An invalid line, represented by the `Result`
- An empty line
- A comment line
- Finally, a valid key-value pair

Most likely, you would ignore empty lines and comments in your parser, but it's still a valid outcome of parsing a line.
The key insight is that these outcomes are now much more visible and that we have a *choice* of how to handle these outcomes in our code (in comparison to ignoring them like we did before).

With that in mind, we can define a new enum to represent the different outcomes of parsing a line:

```rust
#[derive(Debug)]
enum ParsedLine {
    // This is a valid key-value pair
    KeyValue(KeyValue),
    // A comment line
    Comment(String),
    // An empty line
    Empty,
}

#[derive(Debug)]
struct KeyValue {
    key: String,
    value: String,
}
```

We'd use it like so:

```rust
fn parse_line(line: &str) -> Result<ParsedLine, ParseError> {
    let line = line.trim();

    if line.is_empty() {
        return Ok(ParsedLine::Empty);
    }

    if line.starts_with("#") {
        return Ok(ParsedLine::Comment(line.to_string()));
    }

    match line.split_once('=') {
        Some((k, v)) => {
            let k = k.trim();
            if k.is_empty() {
                Err(ParseError::InvalidLine(line.to_string()))
            } else {
                let v = v.trim();
                Ok(ParsedLine::KeyValue(KeyValue {
                    key: k.to_string(),
                    value: v.to_string(),
                }))
            }
        }
        None => Err(ParseError::InvalidLine(line.to_string())),
    }
}
```

We could even go one step further and express more of our invariants in the type system.
For example, we can make use of the fact that parsing a key-value pair only depends on a single line.

{% info(title="Note", icon="warning") %}

Multiline environment variables exist, so instead of "parsing a single line," we should say "parsing a single key-value pair."
For now, we will ignore multiline key-value pairs and assume that each line contains at most one key-value pair.
However, the solution we are building here is extensible enough to handle multiline key-value pairs in the future. 

{% end %}

Since parsing is a fallible operation, we can implement [`TryFrom`](https://doc.rust-lang.org/std/convert/trait.TryFrom.html) for our `KeyValue` struct:

```rust
use std::convert::TryFrom;

impl TryFrom<&str> for KeyValue {
    type Error = ParseError;

    fn try_from(line: &str) -> Result<Self, Self::Error> {
        let line = line.trim();

        if line.is_empty() || line.starts_with("#") {
            return Err(ParseError::InvalidLine(line.to_string()));
        }

        match line.split_once('=') {
            Some((k, v)) => {
                let k = k.trim();
                if k.is_empty() {
                    Err(ParseError::InvalidLine(line.to_string()))
                } else {
                    let v = v.trim();
                    Ok(KeyValue {
                        key: k.to_string(),
                        value: v.to_string(),
                    })
                }
            }
            None => Err(ParseError::InvalidLine(line.to_string())),
        }
    }
}
```

A natural reaction is to say "this is way too much work for such a simple problem."
And yes, taken in isolation, we are heavily yakshaving here.

Think of it this way: we can now reason about all edge-cases in isolation and errors get handled much closer to the source of the problem.
We turned our big ball of mud into a smaller thing that is easier to work with.

The entire Rust standard library is full of abstractions that build on top of each other to help solve bigger problems.
I encourage you to embrace that mindset shift.
Your code will be more maintainable and extensible.

Our `parse_config_file` function now becomes much simpler:

```rust
fn parse_config_file(path: &str) -> Result<HashMap<String, String>, ParseError> {
    let content = read_to_string(path)?;
    
    let mut config = HashMap::new();
    for line in content.lines() {
        match KeyValue::try_from(line) {
            Ok(kv) => { config.insert(kv.key, kv.value); },
            Err(ParseError::InvalidLine(_)) => continue, // Skip invalid lines
            Err(e) => return Err(e), // Fail on any other error
        }
    }
    
    Ok(config)
}
```

All we do is create a map of key-value pairs from some input.

## Tip #6: Introduce Ergonomic Abstractions

At this stage we might as well convert `parse_config_file` into a proper struct.
And while we're at it, let's lift the requirement of passing a file path to the parser
and instead accept any type that implements `BufRead`.
This keeps the parser focused on lines instead of bytes. Files, strings, network streams, and test fixtures can all be wrapped in a buffered reader.
It makes testing much easier.

```rust
use std::collections::HashMap;
use std::convert::TryFrom;
use std::error::Error;
use std::fs::File;
use std::io::{BufRead, BufReader, Cursor};

// `ParseError` is unchanged: the enum plus its
// `Error`, `Display`, and `From<std::io::Error>` impls.
#[derive(Debug)]
enum ParseError {
    InvalidLine(String),
    IoError(std::io::Error),
}
// ...

#[derive(Debug, Clone)]
struct KeyValue {
    key: String,
    value: String,
}

// Same logic as the `TryFrom<&str>` impl above, but taking an owned
// `String` (that's what `BufRead::lines()` yields).
impl TryFrom<String> for KeyValue {
    type Error = ParseError;

    fn try_from(line: String) -> Result<Self, Self::Error> {
        // trim, skip empty/comment lines, then `split_once('=')`
        // ...
    }
}

/// A configuration struct that holds the parsed key-value pairs.
//
// A newtype wrapper around `HashMap<String, String>` so we can change the
// internal representation later without breaking `EnvConfig`'s public API.
#[derive(Debug)]
struct EnvConfig(HashMap<String, String>);

impl EnvConfig {
    // Methods like `new`, `insert`, `get`, `len`,...
}

struct EnvParser;

impl EnvParser {
    fn parse<R: BufRead>(reader: R) -> Result<EnvConfig, ParseError> {
        let mut config = EnvConfig::new(); 

        for line in reader.lines() {
            match line {
                Ok(line_str) => {
                    match KeyValue::try_from(line_str) {
                        Ok(kv) => config.insert(kv),
                        // Skip invalid lines...
                        Err(ParseError::InvalidLine(_)) => continue,
                        // ...but return other errors
                        Err(e) => return Err(e),
                    }
                }
                Err(e) => return Err(ParseError::IoError(e)),
            }
        }

        Ok(config)
    }
    
    // Examples of parsing from different sources
    fn parse_str(input: &str) -> Result<EnvConfig, ParseError> {
        Self::parse(Cursor::new(input))
    }
    
    fn parse_file(path: &str) -> Result<EnvConfig, ParseError> {
        let file = File::open(path)?;
        Self::parse(BufReader::new(file))
    }
}
```

Example usage:

```rust
fn main() -> Result<(), Box<dyn Error>> {
    let env_content = "
        DB_HOST=localhost
        DB_PORT=5432
        
        API_KEY=my_api_key
        LOG_FILE=app.log
    ";
    
    let config = EnvParser::parse_str(env_content)?;
    
    println!("Parsed config entries:");
    for (key, value) in &config.0 {
        println!("{} = {}", key, value);
    }
    
    Ok(())
}
```

Phew, that was a lot of code, but look how much more maintainable and extensible it is now!
We could even go one step further and make the `EnvParser` struct implement [`Iterator`](https://doc.rust-lang.org/std/iter/trait.Iterator.html) so that you can iterate over the parsed key-value pairs,
but let's stop here.

## What We Achieved

By just following a few key principles, we have transformed our initial parser into a more idiomatic Rust implementation.
Now, every part has one clearly defined responsibility:

- `KeyValue` is responsible for parsing a single line 
- `EnvParser` is responsible for parsing the entire input
- `EnvConfig` stores the parsed key-value pairs

Sorry that I had to drag you through all of that, but it's much easier to show than to tell.

I skipped a few intermediate steps, but the idea is always the same: continuously
look for wrinkles in the code and move more and more logic into the type system.

## Did You Find All The Edge Cases?

Lastly, I'd like to come back to my initial question about edge cases.

Parsing environment files sounds simple on the surface, but that is absolutely not the case!
If you haven't already, I encourage you to write your own implementation of an environment file parser.

And once you're done, answer the following question:
How many of these cases do you handle in your own implementation?

- Empty lines should be skipped
- Comment lines starting with `#` should be skipped
- Leading and trailing whitespace in keys and values should be trimmed
- Empty keys like `=value` should be rejected
- Empty values like `key=` should be allowed (with empty string value)
- Lines without an equals sign should be rejected
- On Unix, `key=value=more` is valid and everything after the first `=` is part of the value
- Indented lines with leading whitespace should be parsed normally
- Duplicate keys should overwrite earlier ones with later values
- Quoted values like `key="value"` should not include the quotes in the value
- Escape sequences like `key=value\nwith\nnewlines` or `key=value#notacomment` need careful handling
- Line continuations with backslash for multi-line values are not handled right now
- The parser should handle non-ASCII Unicode content
- Files with invalid UTF-8 encoding errors should be handled gracefully

A correct parser would need to handle all these cases.
Our improved implementation handles many of these cases, but not all.
This just goes to show how easy it is to gloss over details.

## Summary

Rust's beauty is in its semantics and the core mechanics it provides: ownership, borrowing, pattern matching, traits, and so on.
If you merely look at its (admittedly foreign) syntax, you overlook the real elegance of the language.

If there is anything that makes Rust "ugly", it isn't its syntax but the fact that it doesn't hide the complexity underneath. 
Rust values explicitness and you have to deal with the harsh reality that computing is messy.
Turns out our assumptions about a program's execution are often wrong and our mental models are flawed.

Fortunately, we can encapsulate a lot of the complexity behind ergonomic abstractions; it just takes some effort!
So don't worry: once you start to confront your bad habits and look around for better abstractions, Rust stops being ugly.
