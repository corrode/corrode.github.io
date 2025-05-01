+++
title = "When Rust Gets Ugly"
date = 2025-04-14
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

Its clear that Rust has a readability problem -- or at least that's what people say on a regular basis.
But after programming in Rust for 10 years, I think that your coding style has the biggest impact on how your Rust code will look and feel.

Let's take at a simple example: parsing a `.env` file in Rust. How hard can it be?

```sh
DB_HOST=localhost
DB_PORT=5432

API_KEY=my_api_key
LOG_FILE=app.log
```

The goal is to parse the above content from a file called `.env` and return a data structure that contains the key-value pairs.
Easy!

I invite you to write your own version first.
Or at least take a second to consider all the edge-cases, that may occur...

## A Painful First Attempt

At times I see code like this:

```rust
use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use std::path::Path;

fn parse_config_file<'a>(path: &'a str) -> HashMap<String, String> {
    let p = Path::new(&path);
    let mut file = File::open(&p).unwrap();
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes).unwrap();

    let s = String::from_utf8_lossy(&bytes).to_string();

    let lines_with_refs: Vec<&'_ str> = s.split('\n').collect();

    let mut idx = 0;
    let mut cfg: HashMap<String, String> = HashMap::new();

    while idx < lines_with_refs.len() {
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

        let parts = l.split('=').collect::<Vec<&str>>();

        let k: &str = parts[0].trim();
        if k.len() > 0 {
            let v: &str = parts[1].trim();
            cfg.insert(k.to_string(), v.to_string());
        } else {
            println!("Error in line {:?}", parts);
        }

        idx += 1;
    }

    return cfg;
}

fn main() {
    // Test with a string literal instead of a file for demonstration
    let config_content = r#"
        # This is a config file
        host = localhost
        port = 8080
        user = admin

        # This line is empty on purpose

        password= secret
        
        # Edge cases
          indented_key = indented_value
        	tab_key	=	tab_value
        key with spaces = value with spaces
        quotes="quoted value"
        escaped\=key = escaped value
        # = in comments shouldn't be processed
        empty_value=
        =empty_key
        duplicate=first
        duplicate=second
        trailing_whitespace = value with spaces   
        spaced==double_equals
        key=value#not_a_comment
        "quoted key" = should_fail
        multi\
        line\
        key=multiline_value
        
        # Invalid lines
        justkey
    "#;

    // Write the content to a temporary file
    std::fs::write("temp_config.env", config_content).unwrap();

    // Parse the file
    let config = parse_config_file("temp_config.env");

    // Print the results
    println!("\nParsed config entries:");
    let mut keys: Vec<String> = config.keys().cloned().collect();
    keys.sort();

    for key in keys {
        println!("{} = {}", key, config.get(&key).unwrap());
    }

    // Display some test results
    println!("\nTest results:");

    // Test 1: Check if basic keys are parsed correctly
    if let Some(host) = config.get("host") {
        println!("PASS: Basic key 'host' parsed correctly: {}", host);
    } else {
        println!("FAIL: Basic key 'host' not found");
    }

    // Test 2: Check if indentation is handled correctly
    if let Some(value) = config.get("indented_key") {
        println!("PASS: Indented key parsed correctly: {}", value);
    } else {
        println!("FAIL: Indented key not found");
    }

    // Test 3: Check if spaces in keys are preserved (bug)
    if let Some(value) = config.get("key with spaces") {
        println!("PASS: Key with spaces parsed correctly: {}", value);
    } else {
        println!("FAIL: Key with spaces not found (as expected with simple parser)");
    }

    // Test 4: Check for duplicate key behavior
    if let Some(value) = config.get("duplicate") {
        println!("NOTE: For duplicate keys, last value wins: {}", value);
    }

    // Test 5: Check if escaped equals sign is handled (it's not)
    if let Some(value) = config.get("escaped\\=key") {
        println!("PASS: Escaped equals in key handled correctly");
    } else {
        println!("FAIL: Escaped equals not handled correctly (expected with simple parser)");
    }

    // Test 6: Check comment character in value (will fail)
    if let Some(value) = config.get("key") {
        if value == "value#not_a_comment" {
            println!("PASS: Comment character in value preserved");
        } else {
            println!("FAIL: Comment character in value not preserved: {}", value);
        }
    } else {
        println!("FAIL: Key with comment in value not found");
    }

    // Test 7: Check multiline key handling (will fail)
    if let Some(value) = config.get("multi\\") {
        println!("PASS: Multiline key handled");
    } else {
        println!("FAIL: Multiline key not handled (expected with simple parser)");
    }

    // Clean up the temporary file
    std::fs::remove_file("temp_config.env").unwrap_or_default();
}
```

Let's be clear: there are many, many antipatterns in the above code.

Many antipatterns in the code have nothing to do with Rust, but with software engineering in general.
And yet, people take a quick look and use it as an excuse to call Rust an "ugly language" and give up on it.

I would argue that this code is ugly less because of Rust's syntax, but rather
because the author is unaware or ignorant of the ergonomics Rust provides.
The code carries all the hallmarks of a beginner Rust programmer -- possibly with a C/C++ background -- who  
has not yet fully embraced what Rust brings to the table.

In my experience, **better semantics brings nicer syntax in Rust**; many people get that backwards.

If you feel like you're fighting the language (not just its borrow-checker!),
then there's a chance that **the language is trying to push you in a different direction**.

It bears repeating: this is terrifying code with many footguns.
Without much effort, one can make out the red flags:

- The code is littered with `unwrap()` calls
- Unnecessary mutability 
- Manual indexing into arrays
- Unnecessary lifetime annotations
- Cryptic variable names
- Very imperative coding style

This not just makes the code harder to read. 
What is worse is that it leads to business logic bugs in the code, because the code makes quite a few unsound assumptions about its input.
This makes it hard for Rust to help you out.

Whenever I see people struggle with Rust syntax, I'm reminded of the five stages of grief:

#### Stage 1: Denial

"There's nothing wrong with my code - it works perfectly fine! The syntax is just Rust's problem, not mine."

In this stage, developers continue writing C-style code with Rust syntax and ignoring compiler warnings. They often blame the language for being "overly complex" while refusing to learn the fundamentals.

#### Stage 2: Anger

"Why does Rust need all these `mut` keywords and explicit ownership? C++ never made me deal with this nonsense!"

Frustration builds as developers encounter repeated compiler errors. They begin to resent the borrow checker and might abandon half-finished projects in favor of "more practical" languages. At this stage they might post a snarky comment about Rust's design decisions on social media. 

#### Stage 3: Bargaining

"Maybe if I just use more `.unwrap()` calls and sprinkle in some `unsafe` blocks, I can write Rust the way I want to."

Desperate to make progress, developers start making dangerous compromises. They liberally use `.clone()` to silence ownership errors, wrap simple operations in `unsafe` blocks, and litter code with `.unwrap()` calls, effectively bypassing Rust's safety guarantees while keeping all of its verbosity.

#### Stage 4: Depression

"I'll never get used to this language. My code is a mess of references, clones, and unnecessary mutations that even I can't read anymore."

Reality sets in. Code becomes increasingly convoluted with superfluous mutable variables and overly complex data structures. What started as a promising project now feels like an unreadable jumble of syntax.

#### Stage 5: Acceptance

"I see now that these idioms exist for a reason - my code is not only safer but actually more readable when I embrace Rust's patterns instead of fighting them."

Finally, developers begin embracing idiomatic patterns and the design philosophy behind Rust. They refactor their spaghetti code and leverage the type system rather than fight it. Code becomes more maintainable, and they wonder how they ever wrote memory-unsafe code with confidence.

Okay, you (or your team-member) reached acceptance, how can you do better?

## Let Go Of Old Bad Habits

The first step is to acknowledge that the code goes against Rust's design principles.
Based on this realization, we can systematically improve the code.

Ugly code is band-aid around bad habits.
Learn to do it the "Rustic way."

We have seen plenty of ways to write better Rust code in previous articles:

- Read the standard library documentation
- [Think in expressions](/blog/expressions)
- [Immutability by default](/blog/immutability)
- [Leaning into the typesystem](/blog/illegal-state)
- [Iterator patterns instead of manual iteration](/blog/iterators)
- Proper error handling
- Split up the problem into smaller parts

Even just applying these basic techniques, we can get our code into a much better shape.

{% info(title="Try It Out Yourself!") %}

Feel free to use the above code as a refactoring exercise to practice these techniques.
Here's the [link to the Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=2510df77c1c8c6a227680ea49407fe18).
I'll wait here while you experiment with the code.

{% end %}

### Read the Standard Library Documentation

After reading the standard library documentation, we can remove this boilerplate 

```rust
let p = Path::new(&path);
let mut file = File::open(&p).unwrap();
let mut bytes = Vec::new();
file.read_to_end(&mut bytes).unwrap();
let s = String::from_utf8_lossy(&bytes).to_string();
```

and instead call [`std::fs::read_to_string`](https://doc.rust-lang.org/std/fs/fn.read_to_string.html):

```rust
let s = read_to_string(path).unwrap();
```

### Use Type Inference

[Rust is really good at inferring types.](https://rustc-dev-guide.rust-lang.org/type-inference.html) That's why we don't need to specify the type of
our `HashMap` explicitly.

```rust
let mut config = HashMap::new();
```

### Lean Into the Typesystem

Next, manual string splitting is also unnecessary.

```rust
let lines_with_refs: Vec<&'a str> = s.split('\n').collect();
```

The above can be replaced with:

```rust
let lines = s.lines();
```

This returns an [iterator over the lines of a string](https://doc.rust-lang.org/std/primitive.str.html#method.lines).

With that, we can simply iterate over each line:

```rust
for line in s.lines() {
    let line = line.trim();

    if line.is_empty() || line.starts_with("#") {
        continue;
    }

    // ...
}
```

Note that we shadow `line` with `line.trim()`.
That is a common practice in Rust.
This way we don't have to come up with a new name for the trimmed line
and we also don't have to fall back to cryptic names like `lref` or `l` anymore.

Instead of `line.len() == 0`, we can use `line.is_empty()`.

We can also use `line.starts_with("#")` instead of checking for `l.chars().next() == Some('#')`.

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
Let's lean into the typesystem a little more and use pattern matching to destructure the result of `split`:

```rust
match l.split_once('=') {
    Some((k, v)) => {
        let k = k.trim();
        if !k.is_empty() {
            let v = v.trim();
            config.insert(k.to_string(), v.to_string());
        } else {
            println!("Error in line {:?}", parts);
        }
    }
    None => println!("Error in line {:?}", parts),
}
```

With that, we end up with a greatly improved version of the code:

```rust
use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use std::path::Path;

fn parse_config_file<'a>(path: &'a str) -> HashMap<String, String> {
    let s = read_to_string(path).unwrap();

    let mut config = HashMap::new();
    for line in s.lines() {
        let line = line.trim();

        if line.is_empty() || line.starts_with("#") {
            continue;
        }

        match l.split_once('=') {
            Some((k, v)) => {
                let k = k.trim();
                if !k.is_empty() {
                    let v = v.trim();
                    config.insert(k.to_string(), v.to_string());
                } else {
                    println!("Error in line {:?}", parts);
                }
            }
            None => println!("Error in line {:?}", parts),
        }
        
    }

    return config;
}
```

### Use Proper Error Handling

We can go one step further with proper error handling.
It depends on the business logic how you want to handle invalid lines.
Here's a version, which returns an error in the case:

```rust
fn parse_config_file<'a>(path: &'a str) -> Result<HashMap<String, String>, ParseError> {
    let s = read_to_string(path)?;

    let mut config = HashMap::new();
    for line in s.lines() {
        let line = line.trim();

        if line.is_empty() || line.starts_with("#") {
            continue;
        }

        match l.split_once('=') {
            Some((k, v)) => {
                let k = k.trim();
                if !k.is_empty() {
                    let v = v.trim();
                    config.insert(k.to_string(), v.to_string());
                } else {
                    return Err(ParseError::InvalidLine(line.to_string()));
                }
            }
            None => return Err(ParseError::InvalidLine(line.to_string())),
        }
        
    }

    Ok(config)
}
```

Next, let's write a function for parsing individual lines. 

```rust
fn parse_line(line: &str) -> Result<Option<(String, String)>, ParseError> {
    let line = line.trim();

    if line.is_empty() || line.starts_with("#") {
        return Ok(None);
    }

    match line.split_once('=') {
        Some((k, v)) => {
            let k = k.trim();
            if !k.is_empty() {
                let v = v.trim();
                Ok(Some((k.to_string(), v.to_string())))
            } else {
                Err(ParseError::InvalidLine(line.to_string()))
            }
        }
        None => Err(ParseError::InvalidLine(line.to_string())),
    }
}
```

The code is still quite "stringy-typed."
That's usually a sign of a missing abstraction.
To tackle that, we could introduce an enum to represent a parsed line for example:

```rust
#[derive(Debug)]
struct KeyValue {
    key: String,
    value: String,
}

#[derive(Debug)]
enum ParsedLine {
    KeyValue(KeyValue),
    Comment(String),
    Empty,
}
```

And we'd use it like so:

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
            if !k.is_empty() {
                let v = v.trim();
                Ok(ParsedLine::KeyValue(KeyValue {
                    key: k.to_string(),
                    value: v.to_string(),
                }))
            } else {
                Err(ParseError::InvalidLine(line.to_string()))
            }
        }
        None => Err(ParseError::InvalidLine(line.to_string())),
    }
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=7a5e34cdac522dd8eb60759cc89de5a4))

We could even go one step further and express more of our invariants in the type system.
For example, we can make use of the fact that parsing a key-value pair only depends on a single line.
Since parsing is a fallible operation, we can implement `TryFrom` for our `KeyValue` struct.

```rust
struct KeyValue {
    key: String,
    value: String,
}

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
                if !k.is_empty() {
                    let v = v.trim();
                    Ok(KeyValue {
                        key: k.to_string(),
                        value: v.to_string(),
                    })
                } else {
                    Err(ParseError::InvalidLine(line.to_string()))
                }
            }
            None => Err(ParseError::InvalidLine(line.to_string())),
        }
    }
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=722eb6136fe3da50e3a17326a6702ede))

It might look like we made the problem more complicated than it is.
However, we can now simplify our parser even more and also test key-value parsing in isolation.
On top of that, errors get handled much closer to the source of the problem.

Our `parse_config_file` function now gets much simpler: 

```rust
fn parse_config_file(path: &str) -> Result<HashMap<String, String>, ParseError> {
    let content = std::fs::read_to_string(path)?;
    
    let mut config = HashMap::new();
    
    for result in content.lines().map(parse_line) {
        if let ParsedLine::KeyValue(kv) = result? {
            config.insert(kv.key, kv.value);
        }
    }
    
    Ok(config)
}
```

At this stage -- assuming we can still change the public API of our parser --
we can convert `parse_config_file` into an `EnvParser` struct.
That's because all we do is creating a map of key-value pairs from some input.
While we're at it, we can lift the requirement of passing a file path to the parser
and instead accept any type that implements `Read`.

```rust    
#[derive(Debug)]
enum ParseError {
    InvalidLine(String),
    IoError(std::io::Error),
}

impl Error for ParseError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            ParseError::IoError(err) => Some(err),
            _ => None,
        }
    }
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ParseError::InvalidLine(line) => write!(f, "Invalid line format: {}", line),
            ParseError::IoError(err) => write!(f, "I/O error: {}", err),
        }
    }
}

impl From<std::io::Error> for ParseError {
    fn from(err: std::io::Error) -> Self {
        ParseError::IoError(err)
    }
}

#[derive(Debug, Clone)]
struct KeyValue {
    key: String,
    value: String,
}

impl TryFrom<String> for KeyValue {
    type Error = ParseError;

    fn try_from(line: String) -> Result<Self, Self::Error> {
        let line = line.trim();

        if line.is_empty() || line.starts_with('#') {
            return Err(ParseError::InvalidLine(line.to_string()));
        }

        match line.split_once('=') {
            Some((k, v)) => {
                let k = k.trim();
                if !k.is_empty() {
                    let v = v.trim();
                    Ok(KeyValue {
                        key: k.to_string(),
                        value: v.to_string(),
                    })
                } else {
                    Err(ParseError::InvalidLine(line.to_string()))
                }
            }
            None => Err(ParseError::InvalidLine(line.to_string())),
        }
    }
}

#[derive(Debug)]
struct EnvConfig {
    inner: HashMap<String, String>,
}

impl EnvConfig {
    fn new() -> Self {
        EnvConfig {
            inner: HashMap::new(),
        }
    }

    fn insert(&mut self, keyvalue: KeyValue) {
        self.inner.insert(keyvalue.key, keyvalue.value);
    }

    fn get(&self, key: &str) -> Option<&str> {
        self.inner.get(key).map(|v| v.as_str())
    }

    fn len(&self) -> usize {
        self.inner.len()
    }
}

struct EnvParser;

impl EnvParser {
    fn parse<R: Read>(reader: R) -> Result<EnvConfig, ParseError> {
        let reader = BufReader::new(reader);
        let mut config = EnvConfig::new();

        for line in reader.lines() {
            match line {
                Ok(line_str) => {
                    match KeyValue::try_from(line_str) {
                        Ok(kv) => config.insert(kv),
                        Err(ParseError::InvalidLine(_)) => continue, // Skip invalid lines
                        Err(e) => return Err(e),
                    }
                }
                Err(e) => return Err(ParseError::IoError(e)),
            }
        }

        Ok(config)
    }

    fn parse_str(input: &str) -> Result<EnvConfig, ParseError> {
        Self::parse(input.as_bytes())
    }

    fn parse_file(path: &str) -> Result<EnvConfig, ParseError> {
        let file = File::open(path)?;
        Self::parse(file)
    }
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=4fb0dbbab6d8242feb7e4f28b51a1d08))

I skipped a few intermediate steps, but the idea is always the same: continuously
look for wrinkles in the code and move more and more logic into the type system.

# Summary

If there is anything that makes Rust "ugly", it isn't its syntax but the fact that it doesn't hide the complexity of the underlying system.
Rust values explicitness and you have to deal with the harsh reality that computing is messy.


Turns out our assumptions about a program’s execution are often wrong and our mental models are flawed.
Fortunately, we can encapsulate a lot of the complexity behind ergonomic abstractions; it just takes some practice.
Don't worry: once you start to confront your bad habits and look around for better abstractions, greener pastures are right around the corner.

Rust, after all is said and done, is still a systems programming language in the end.
It competes with the likes of C/C++ and for that it has pretty good ergonomics. 