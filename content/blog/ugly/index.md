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

The goal is to parse the above content from a file called `.env` and return a data structure that contains the key-value pairs.

I invite you to write your own version first.
As a little hint, consider the edge-cases, which could occur.

## A First Attempt

At times I see code like the following to parse a `.env` file:

```rust
use std::collections::HashMap;

fn parse_config_file<'a>(path: &'a str) -> HashMap<&'str, &'str> {
    let p = Path::new(&path);
    let mut file = File::open(&p).unwrap();
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes).unwrap();
    let s = String::from_utf8_lossy(&bytes);
    let lines = s.split('\n').collect::<Vec<&str>>();
    
    let mut idx = 0;
    let mut cfg: HashMap<&'a str, &'a str> = HashMap::new();
    
    while idx < lines.len() {
        let lref = &lines[idx];
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
```

Let's be clear: this is terrifying code with many footguns.
And yet, people use it as an excuse to call Rust an ugly language and give up on it.

However, I would argue that it's not because of Rust's syntax, but rather
because there are way more ergonomic solutions in Rust.
Typically, better semantics lead to easier to read syntax in Rust.
If you feel like you're fighting the language (not just its borrow-checker!),
then there's a chance that the language is trying to tell you that you're working against it.

Immediately, one can make out a few red flags from the code above:
- The code is littered with `unwrap()` calls
- Manual indexing into arrays
- Lifetime annotations -- a sign of premature optimization
- Cryptic variable names

On top of that, there are plenty of business logic bugs in the code,
because the code makes quite a few unjustified assumptions.

It is safe to say that the code is not idiomatic Rust.

Okay, but how can we do better?





Blog post idea: "This can never panic" and other lies we tell ourselves 