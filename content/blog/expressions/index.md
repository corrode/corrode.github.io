+++
title = "Using Expressions Effectively in Rust"
date = 2024-05-16
template = "article.html"
[extra]
series = "Idiomatic Rust"
resources = [
    "[Rust, Ruby, and the Art of Implicit Returns &mdash; Earthly blog](https://earthly.dev/blog/single-expression-functions/)"
]
+++

Rust is an expression-based language, which means that almost everything in Rust is an expression.
Functional programmers are used to the concept, but for those coming from an imperative background, it might be a bit confusing at first.

Let's see how you can use expressions effectively in Rust and how they can improve your code flow.

## Understanding Expressions

In Rust, an expression is any construct that evaluates to a value. This includes literals, variables, function calls, blocks, and control flow statements like `if`, `match`, and `loop`. 

"Everything is an expression" is a bit of an exaggeration, but it's a useful mental model while you 
internalize the concept.

Expressions return values, so they can be used in all the places where you would expect a value, like function arguments, assignments, and return statements.

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

Expressions are very powerful. It takes a bit of practice to get used to them, 
but once you get acquainted with them, they are a joy to work with.
You go from imperative code to a more declarative style, expressing
the steps of computation without being overly verbose and using placeholder variables.

When you try to refactor your code, keep expressions in mind.
They tend to guide you towards more ergonomic Rust code.