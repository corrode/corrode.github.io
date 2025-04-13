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

Let's look at a simple task: parsing a `.env` file.
After all, how hard could it be?

```sh
DATABASE_URL=postgres://user:password@localhost:5432/mydb
API_KEY=12345-abcde-67890-fghij
```

The goal is to parse the above file and return a data structure that contains the key-value pairs.

I invite you to write your own version first.
As a little hint, consider the edge-cases, which could occur.

## A First Attempt

At times I see code like the following to parse a `.env` file:

```rust
use std::collections::HashMap;

struct ParsedLine<'a> {
    key: &'a str,
    value: &'a str,
}

fn parse_line<'a>(line: &'a str) -> Option<ParsedLine<'a>> {
    // Split on '=' and convert directly to array
    let parts: Vec<&str> = line.split('=').collect();
    
    // Dangerous direct indexing without bounds checking
    if parts.len() < 2 {
        return None;
    }
    
    let key = parts[0].trim();
    
    // Could have multiple '=' characters, just use the first split
    let value = parts[1].trim();
    
    // Return sentinel for empty key
    if key.len() == 0 {
        return Some(ParsedLine { key: "SENTINEL_EMPTY_KEY", value: "SENTINEL_EMPTY_VALUE" });
    }

    Some(ParsedLine { key, value })
}

fn parse_config_file<'a>(src: &'a str) -> HashMap<String, String> {
    let lines = src.lines().collect::<Vec<&str>>();
    let mut idx = 0;
    let mut cfg: HashMap<String, String> = HashMap::new();
    
    while idx < lines.len() {
        let lref = &lines[idx];
        let mut l = *lref;
        l = l.trim();
        
        if l.len() == 0 || l.starts_with("#") {
            idx += 1;
            continue;
        }

        if l.contains('=') {
            let maybe_parsed = parse_line(l);
            if maybe_parsed.is_some() {
                let parsed = maybe_parsed.unwrap();

                let k = parsed.key.to_string();
                let mut v = parsed.value.to_string();
                
                cfg.insert(k, v);
            } else {
                println!("Error parsing line: {}", l);
            }
        } else {
            println!("Line is missing '=' but was allowed through: {}", l);
        }

        idx += 1;
    }

    cfg
}
```

I've seen way worse, but I would agree that this code looks quite ugly.
However, I would argue that it's not because of the syntax, but rather the semantics
and that there are way more ergonomic solutions in Rust.

Immediately, one can make out a few red flags:
- The code is littered with `unwrap()` calls
- The code uses a sentinel value for empty values 
- Manual indexing into arrays
- Lifetime annotations -- a sign of premature optimization
- Cryptic variable names

It is safe to say that the code is not idiomatic Rust.





Blog post idea: "This can never panic" and other lies we tell ourselves 