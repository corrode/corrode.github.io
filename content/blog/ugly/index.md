+++
title = "When Rust Gets Ugly"
date = 2025-04-14
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

Its clear that Rust has a readability problem.
At least that's what I hear on a regular basis.
After programming in Rust for 10 years, I think you have to dedicate some time to learn it properly
and that your background will inform how your Rust code looks.

Let's look at a simple example: parsing a `.env` file in Rust. After all, how hard could it be?

```sh
APP_ENV=production
API_KEY=my_api_key

LOG_FILE=app.log

DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=myuser
DB_PASSWORD=mypassword
DB_NAME=mydb
```

The goal is to parse the above content from a file called `.env` and return a data structure that contains the key-value pairs.

I invite you to write your own version first.
As a little hint, consider the edge-cases, which could occur.

## A Painful First Attempt

At times I see code like the following:

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
    
    let lines_with_refs: Vec<&'a str> = s.split('\n').collect();
    
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
        if l.starts_with("#") {
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

Let's be clear: there are many antipatterns in the above code.
Many of them have nothing to do with Rust, but with software engineering in general.
And yet, people use it as an excuse to call Rust an ugly language and give up on it.

I would argue that this code is ugly less because of Rust's syntax, but rather
because the author is unaware or ignorant of the ergonomics Rust provides.

Typically, **better semantics lead to nicer syntax in Rust**.
Many people get that backwards.

If you feel like you're fighting the language (not just its borrow-checker!),
then there's a chance that the language is trying to **tell you something**. 

It bears repeating: this is terrifying code with many footguns.
Without much effort, one can make out a few red flags from the code above:

- The code is littered with `unwrap()` calls
- Unnecessary mutability 
- Manual indexing into arrays
- Unnecessary lifetime annotations
- Cryptic variable names
- Very imperative coding style

The above not just makes the code harder to read. 
What is worse is that it leads to business logic bugs in the code, because the code makes quite a few unjustified assumptions
and the way the code is written makes it hard for Rust to help you out.

I think we can all agree that the code is not idiomatic Rust.

## The Five Stages of Grief About Rust Syntax

Whenever I see people struggle with Rust syntax, I'm reminded of the five stages of grief:

### Denial

> "There's nothing wrong with my code - it works perfectly fine! The syntax is just Rust's problem, not mine."

In this stage, developers continue writing C-style code with Rust syntax, ignoring compiler warnings and adding unnecessary lifetime annotations everywhere. They often blame the language for being "too complex" while refusing to revisit fundamental concepts.

### Anger

> "Why does Rust need all these lifetime annotations and explicit ownership? C++ never made me deal with this nonsense!"

Frustration builds as developers encounter repeated compiler errors. They begin to resent the borrow checker and might abandon half-finished projects in favor of "more practical" languages. Excessive code comments containing rants about Rust's design decisions become common.

### Bargaining

> "Maybe if I just use more `.unwrap()` calls and sprinkle in some `unsafe` blocks, I can write Rust the way I want to."

Desperate to make progress, developers start making dangerous compromises. They liberally use `.clone()` to silence ownership errors, wrap simple operations in `unsafe` blocks, and litter code with `.unwrap()` calls, effectively bypassing Rust's safety guarantees while keeping all of its verbosity.

### Depression

> "I'll never get used to this language. My code is a mess of references, clones, and unnecessary mutations that even I can't read anymore."

Reality sets in as technical debt accumulates. Code becomes increasingly convoluted with superfluous mutable variables and overly complex data structures. Performance suffers from unnecessary allocations, and what started as a promising project now feels like an unreadable jumble of syntax.

### Acceptance

> "I see now that these idioms exist for a reason - my code is not only safer but actually more readable when I embrace Rust's patterns instead of fighting them."

Finally, developers begin embracing idiomatic patterns and the design philosophy behind Rust. They refactor their spaghetti code into clean, expressive modules that leverage the type system rather than fight it. Performance improves, code becomes more maintainable, and they wonder how they ever wrote memory-unsafe code with confidence.

Okay, you (or your team-member) reached acceptance, how can you do better?

## Let Go Of Old Bad Habits


The first step is to acknowledge that the code goes against Rust's design principles.
Based on this, we can systematically improve the code.

Ugly code is band-aid around bad habits.
Learn to do it the "Rustic way."

We have seen plenty of ways to write better Rust code in previous articles:

- Think in expressions
- Immutability by default
- Leaning into the typesystem 
- Iterator patterns instead of manual iteration
- Proper error handling

Even just following this basic advice, we can get it into a much better shape.




Blog post idea: "This can never panic" and other lies we tell ourselves 
The language doesn't get more ugly beyond a certain point of complexity.
I can't say the same about C++.

what makes Rust "ugly" isn't just syntax but exposing complex concepts.
Physics over optics, not everything is about cosmetics.

"I don't want ugly Rust-like typing in my favorite language. It may look good in Rust, but it looks horrible in Python."

It's also pretty easy to go into the other extreme and make everything generic. That's also hard to read.

People don't confront their bad habits and find workarounds. That's the origin of ugly code.


Assumptions about the program’s execution order are often wrong