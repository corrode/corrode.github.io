+++
title = "When Rust Gets Ugly"
date = 2025-04-14
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

It's clear that Rust has a readability problem -- or at least that's what people claim on a regular basis.
After programming in Rust for 10 years, I think that your coding style has the biggest impact on how your Rust code will look and feel.

In workshops I find people getting frustrated with Rust.
They write Rust like they would write idiomatic code in other languages, but it doesn't feel right.
"You can write bad Java code in any language," is a common saying, and I think it applies here as well.

**Idiomatic Rust ticks all the boxes: it feels right, is correct, and readable.**


Let's take a simple example: parsing a `.env` file in Rust. How hard can it be?

```sh
DB_HOST=localhost
DB_PORT=5432

API_KEY=my_api_key
LOG_FILE=app.log
```

The goal is to parse the above content from a file called `.env` and return a data structure that contains the key-value pairs.
Sounds simple enough!

I invite you to write your own version first.
Or at least take a second to consider all the edge-cases that may occur...

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
Most of them have nothing to do with Rust, but with software engineering in general.

The code carries all the hallmarks of a beginner Rust programmer -- possibly with a C/C++ background -- who has not yet fully embraced the ergonomics Rust provides.

## Better semantics enable nicer syntax in Rust

If you feel like you're fighting the language (not just its borrow-checker!),
then there's a chance that **the language is trying to push you into a different direction**.

It bears repeating: the above code is terrifying and contains many footguns.
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

Whenever I see people struggle with Rust syntax, I'm reminded of...

## The five stages of grief 

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

## Let Go Of Old Bad Habits

Okay, you (or your team-member) reached acceptance, how can you do better?

The first step is to acknowledge that the code goes against Rust's design principles.
Based on this realization, we can systematically improve the code.

Ugly code is a band-aid around bad habits.
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

This is a hands-on exercise.
Feel free to paste the above code into your editor and practice refactoring it. 
Here's the [link to the Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=2510df77c1c8c6a227680ea49407fe18).
I'll wait here.

{% end %}

### Read the Standard Library Documentation

Many common patterns are beautifully handled by the standard library.
It is worth your time to read the documentation.
For instance, you will find that you can get rid of all of of this boilerplate:

```rust
let p = Path::new(&path);
let mut file = File::open(&p).unwrap();
let mut bytes = Vec::new();
file.read_to_end(&mut bytes).unwrap();
let s = String::from_utf8_lossy(&bytes).to_string();
```

and instead call [`std::fs::read_to_string`](https://doc.rust-lang.org/std/fs/fn.read_to_string.html):

```rust
use std::fs::read_to_string;

let s = read_to_string(path).unwrap();
```

### Use Type Inference

[Rust is really good at inferring types.](https://rustc-dev-guide.rust-lang.org/type-inference.html) That's why we don't need to specify the type of
our `HashMap` explicitly.

```rust
let mut config = HashMap::new();
```

### Lean Into the Typesystem

Manual string splitting is not necessary and very much discouraged.
The reason is that strings are, in fact, very complicated.
There is a perception that it's just an array of "characters", but that is ill-defined
and a dangerous assumption.

```rust
let lines_with_refs: Vec<&'a str> = s.split('\n').collect();
```

This line expects that lines are separated by `\n`.
That's not true on Windows, where lines are separated by `\r\n`.

The following line does the correct thing on all platforms:

```rust
let lines = s.lines();
```

This returns an [iterator over the lines of a string](https://doc.rust-lang.org/std/primitive.str.html#method.lines).

Knowing that, we can instead iterate over each line:

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

Instead of `line.len() == 0`, we use `line.is_empty()` now.
And `line.starts_with("#")` is easier to read than checking with `l.chars().next() == Some('#')`.

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
Fortunately, we don't have to do all this if we lean into the typesystem a little more and use pattern matching to destructure the result of `split_once`:

```rust
match line.split_once('=') {
    Some((k, v)) => {
        let k = k.trim();
        if !k.is_empty() {
            let v = v.trim();
            config.insert(k.to_string(), v.to_string());
        } else {
            println!("Error in line with empty key");
        }
    }
    None => println!("Error in line: no '=' found"),
}
```

With that, we end up with a greatly improved version of the code:

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
                if !k.is_empty() {
                    let v = v.trim();
                    config.insert(k.to_string(), v.to_string());
                } else {
                    println!("Error in line with empty key");
                }
            }
            None => println!("Error in line: no '=' found"),
        }
    }

    config
}
```

You'd be forgiven if you called it a day at this point. 
However, to truly embrace Rust, it helps to a step back and think about our problem for a little longer. 

### Use Proper Error Handling

One obvious next step is to introduce proper error handling.
It depends on the business logic how you want to handle invalid lines, but I prefer to implement proper parsing
and have complete freedom over the output on the callsite.

```rust
use std::collections::HashMap;
use std::fs::read_to_string;
use std::fmt;
use std::error::Error;

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

The code is still quite "stringy-typed," which usually is a sign of a missing abstraction.
How about we introduce an enum to represent a parsed line?

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

We could even go one step further and express more of our invariants in the type system.
For example, we can make use of the fact that parsing a key-value pair only depends on a single line.
Since parsing is a fallible operation, we can implement `TryFrom` for our `KeyValue` struct:

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

It might look like we made the problem more complicated than it is.
However, we can now simplify our parser even more and also test key-value parsing in isolation.
On top of that, errors get handled much closer to the source of the problem.

Our `parse_config_file` function now becomes much simpler:

```rust
fn parse_config_file(path: &str) -> Result<HashMap<String, String>, ParseError> {
    let content = read_to_string(path)?;
    
    let mut config = HashMap::new();
    
    for line in content.lines() {
        match KeyValue::try_from(line) {
            Ok(kv) => {
                config.insert(kv.key, kv.value);
            },
            Err(ParseError::InvalidLine(_)) => continue, // Skip invalid lines
            Err(e) => return Err(e),
        }
    }
    
    Ok(config)
}
```


All we do is creating a map of key-value pairs from some input.
At this stage we might as well convert `parse_config_file` into an `EnvParser` struct.
And while we're at it, let's lift the requirement of passing a file path to the parser
and instead accept any type that implements `Read`.

```rust
use std::collections::HashMap;
use std::io::{BufRead, BufReader, Read};
use std::fs::File;
use std::fmt;
use std::error::Error;
use std::convert::TryFrom;

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

// Example usage
fn main() -> Result<(), Box<dyn Error>> {
    let env_content = "
        DB_HOST=localhost
        DB_PORT=5432
        
        API_KEY=my_api_key
        LOG_FILE=app.log
    ";
    
    let config = EnvParser::parse_str(env_content)?;
    
    println!("Parsed config entries:");
    for (key, value) in &config.inner {
        println!("{} = {}", key, value);
    }
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;
    use std::io::Write;
    
    // Tests for KeyValue struct
    #[test]
    fn test_keyvalue_valid() {
        let kv = KeyValue::try_from("key=value".to_string()).unwrap();
        assert_eq!(kv.key, "key");
        assert_eq!(kv.value, "value");
    }
    
    #[test]
    fn test_keyvalue_with_spaces() {
        let kv = KeyValue::try_from("  key  =  value  ".to_string()).unwrap();
        assert_eq!(kv.key, "key");
        assert_eq!(kv.value, "value");
    }
    
    #[test]
    fn test_keyvalue_empty_value() {
        let kv = KeyValue::try_from("key=".to_string()).unwrap();
        assert_eq!(kv.key, "key");
        assert_eq!(kv.value, "");
    }
    
    #[test]
    fn test_parser_duplicate_keys() {
        let input = "
            key=value1
            key=value2
        ";
        
        let config = EnvParser::parse_str(input).unwrap();
        assert_eq!(config.len(), 1);
        // Last value should win for duplicate keys
        assert_eq!(config.get("key"), Some("value2"));
    }
    
    #[test]
    fn test_parser_all_edge_cases() {
        let input = "
            # Comments should be ignored
            simple=value
              indented_key = indented_value
            empty_value=
            key_with_equals=value=with=equals
            duplicate=first
            duplicate=second
            trailing_whitespace = value with spaces   
        ";
        
        let config = EnvParser::parse_str(input).unwrap();
        
        assert_eq!(config.len(), 6);
        assert_eq!(config.get("simple"), Some("value"));
        assert_eq!(config.get("indented_key"), Some("indented_value"));
        assert_eq!(config.get("empty_value"), Some(""));
        assert_eq!(config.get("key_with_equals"), Some("value=with=equals"));
        assert_eq!(config.get("duplicate"), Some("second"));
        assert_eq!(config.get("trailing_whitespace"), Some("value with spaces"));
    }
}
```

Without much effort, we decoupled the code.
Now, every part has one clearly defined responsibility:

- `KeyValue` is responsible for parsing a single line 
- `EnvParser` is responsible for parsing the entire input
- `EnvConfig` stores the parsed key-value pairs

I skipped a few intermediate steps, but the idea is always the same: continuously
look for wrinkles in the code and move more and more logic into the type system.

## Did You Find All The Edge Cases?

Parsing environment files sounds simple on the surface, but that is not the case.
How many of these cases did you catch in your implementation?

- **Empty lines** - Should be skipped
- **Comment lines** - Lines starting with `#` should be skipped
- **Whitespace in keys/values** - Leading and trailing whitespace should be trimmed
- **Empty keys** - Lines like `=value` should be rejected
- **Empty values** - Lines like `key=` should be allowed! (With empty string value)
- **Missing equals sign** - Lines without an equals sign should be rejected
- **Multiple equals signs** - How do you handle `key=value=more`? On Unix, this is valid and everything after the first `=` is part of the value
- **Indented lines** - Lines with leading whitespace should be parsed normally
- **Duplicate keys** - Later values should overwrite earlier ones
- **Quoted values** - How do you handle `key="value"`? Our solution preserves the quotes
- **Escaping** - How do you handle `key=value\nwith\nnewlines` or `key=value#notacomment`?
- **Line continuations** - What about multi-line values with backslash? I don't handle them right now.
- **Unicode characters** - How does your parser handle non-ASCII content?
- **Invalid UTF-8** - How do you handle files with encoding errors?

A robust parser would need to handle all these cases, with clear behavior defined for each.
Our improved implementation handles many of these cases, but not all.
This just goes to show that it's easy to gloss over details.

## Summary

What I find interesting in these exercises is that the benefits of looking for better abstractions are not about memory safety.
Instead, it Rust makes testing easier, which meant that the developers in the experiment were able to find bugs that had remain completely hidden otherwise. 

If there is anything that makes Rust "ugly", it isn't its syntax but the fact that it doesn't hide the complexity of the underlying system.
Rust values explicitness and you have to deal with the harsh reality that computing is messy.

Turns out our assumptions about a program's execution are often wrong and our mental models are flawed.
Fortunately, we can encapsulate a lot of the complexity behind ergonomic abstractions; it just takes some practice.
Don't worry: once you start to confront your bad habits and look around for better abstractions, greener pastures are right around the corner.

Rust, after all is said and done, is still a systems programming language in the end.
It competes with the likes of C/C++ and for that it has pretty good ergonomics.