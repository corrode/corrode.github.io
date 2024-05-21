+++
title = "Effective Use Of Expressions In Rust"
date = 2024-05-20
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = [
    { name = "Hanno Braun", url = "https://www.hannobraun.com/" },
    { name = "Thomas Zahner",  url = "https://github.com/thomas-zahner"}
]
resources = [
    "Rust By Example: Expressions &mdash; [doc.rust-lang.org](https://doc.rust-lang.org/rust-by-example/expression.html)",
    "Rust Reference: Expressions &mdash; [doc.rust-lang.org](https://doc.rust-lang.org/reference/expressions.html)",
    "[Rust, Ruby, and the Art of Implicit Returns &mdash; Earthly blog](https://earthly.dev/blog/single-expression-functions/)"
]
+++

Rust is an expression-based language, which means that almost everything in Rust is an expression.
Functional programmers are used to the concept, but for those coming from an imperative background, it might be a bit confusing at first.

The alternative to expressions are statements, which you might be familiar with
from other, more imperative languages.

Here is what the Rust Reference has to say about expressions:

> Rust is primarily an expression language. This means that most forms of
> value-producing or effect-causing evaluation are directed by the uniform
> syntax category of expressions. Each kind of expression can typically nest
> within each other kind of expression, and rules for evaluation of expressions
> involve specifying both the value produced by the expression and the order in
> which its sub-expressions are themselves evaluated.
>
> In contrast, statements serve mostly to contain and explicitly sequence expression evaluation.
> &mdash; [Rust Reference](https://doc.rust-lang.org/reference/expressions.html)

Let's see how you can use expressions effectively in Rust and how they can improve your code flow.

## Understanding Expressions

In Rust, an expression is any construct that evaluates to a value. This includes literals, variables, function calls, blocks, and control flow statements like `if`, `match`, and `loop`. 

"Everything is an expression" is a bit of an exaggeration, but it's a useful mental model while you 
internalize the concept.

Expressions return values, so they can be used in all the places where you would expect a value, like function arguments, assignments, and return statements.

```rust
fn main() {
    // 42 is an expression that evaluates to the value 42.
    // Sounds trivial, but it goes to show that even literals are expressions.
    let x = 42; 

    // Here we have a block expression that evaluates to 15
    // The last expression in the block gets returned.
    let y = {
        let z = 10;
        z + 5
    };

    // An `if` expression also evaluates to a value
    // which can be assigned to a variable.
    let z = if y > 10 { 1 } else { 0 };
}
```

These examples hardly capture the full flexibility of expressions.
As with many other concepts in Rust, it's hard to internalize expressions without practice.
Let's look at a real-world example.

## A Practical Refactoring Example

Here's an abstracted version of some code from a recent real-world project I was asked to refactor, keeping the main idea intact:

```rust
use std::path::{PathBuf};
use std::fs::File;
use std::env;

/// Create a configuration file for the application at the given path
fn create_config_file(config_path: Option<PathBuf>) -> Result<File, Box<dyn std::error::Error>> {
    if let Some(path) = config_path {
        return setup_config(&path);
    } else {
        if let Some(home_dir) = env::home_dir() {
            let config_dir = home_dir.join(".config/my_app/");
            return setup_config(&config_dir);
        } else {
            // Fallback to the current directory
            let current_dir = PathBuf::from(".");
            return setup_config(&current_dir);
        }
    }
}

fn setup_config(path: &PathBuf) -> Result<File, Box<dyn std::error::Error>> {
    todo!("demo")
}
```

There are a few issues with this code, but I want you to focus on the return statements
and the duplicate logic.

## Refactoring with Expressions

The first observation is that we have multiple return statements in the middle of the function.
This can make the code harder to follow and reason about.
Let's refactor the code to have a single return statement at the end of the function.

```rust
use std::env;
use std::fs::File;
use std::path::PathBuf;

/// Create a configuration file for the application at the given path
fn create_config_file(config_path: Option<PathBuf>) -> Result<File, Box<dyn std::error::Error>> {
    let config_file = match config_path {
        Some(path) => setup_config(&path),
        None => {
            if let Some(home_dir) = env::home_dir() {
                let config_dir = home_dir.join(".config/my_app/");
                setup_config(&config_dir.to_path_buf())
            } else {
                // Fallback to the current directory
                let current_dir = PathBuf::from(".");
                setup_config(&current_dir)
            }
        }
    };
    Ok(config_file?)
}

fn setup_config(path: &PathBuf) -> Result<File, Box<dyn std::error::Error>> {
    // Implementation details omitted
    unimplemented!()
}
```

This works because the `if` and `match` expressions return the value of the last expression in the block.
(It's expressions all the way down!)
In this case, the value is whatever `setup_config` returns.
This value gets assigned to `config_file`, and we return it at the end of the function.

Let's go one step further and try to call `setup_config` only *once* at the end of the function:

```rust
use std::env;
use std::fs::File;
use std::path::PathBuf;

/// Create a configuration file for the application at the given path
fn create_config_file(config_path: Option<PathBuf>) -> Result<File, Box<dyn std::error::Error>> {
    let path = match config_path {
        Some(path) => path,
        None => {
            if let Some(home_dir) = env::home_dir() {
                let config_dir = home_dir.join(".config/my_app/");
                config_dir.to_path_buf()
            } else {
                PathBuf::from(".")
            }
        }
    };
    Ok(setup_config(&path)?)
}

fn setup_config(path: &PathBuf) -> Result<File, Box<dyn std::error::Error>> {
    // Implementation details omitted
    unimplemented!()
}
```

Better, right? 

The `else` block in the `None` case is just a fallback if all else fails.
It gets way too much attention in the original code.
We can use the `unwrap_or_else` method to make it more concise:

```rust
use std::env;
use std::fs::File;
use std::path::PathBuf;

/// Create a configuration file for the application at the given path
fn create_config_file(config_path: Option<PathBuf>) -> Result<File, Box<dyn std::error::Error>> {
    let path = match config_path {
        Some(path) => path,
        None => {
            env::home_dir()
                .map(|home_dir| home_dir.join(".config/my_app/").to_path_buf())
                .unwrap_or_else(|| PathBuf::from("."))
        }
    };
    Ok(setup_config(&path)?)
}

fn setup_config(path: &PathBuf) -> Result<File, Box<dyn std::error::Error>> {
    // Implementation details omitted
    unimplemented!()
}
```

Now the fallback is just a side note, and the main logic is more prominent.

The `Some(path) => path` match arm looks very simple. Almost too simple? We have already used `unwrap_or_else()` once, let's apply it here as well.

```rust
use std::env;
use std::fs::File;
use std::path::PathBuf;

/// Create a configuration file for the application at the given path
fn create_config_file(config_path: Option<PathBuf>) -> Result<File, Box<dyn std::error::Error>> {
    let path = config_path.unwrap_or_else(|| {
        env::home_dir()
            .map(|home_dir| home_dir.join(".config/my_app/").to_path_buf())
            .unwrap_or_else(|| PathBuf::from("."))
    });
    Ok(setup_config(&path)?)
}

fn setup_config(path: &PathBuf) -> Result<File, Box<dyn std::error::Error>> {
    // Implementation details omitted
    unimplemented!()
}
```

This code could still be improved, but the main point is to show you how expressions can help you refactor your code without a lot of effort. We avoided repetition simply by thinking in terms of expressions.

## Conclusion

Expressions are very powerful. It takes a bit of practice to get acquainted with
them, but they are a joy to use. You go from imperative code to a more
declarative style, expressing the steps of computation without being overly
verbose and using placeholder variables.

When you try to refactor your code, keep expressions in mind.
They tend to guide you towards more ergonomic Rust code.


- match expression
- let else