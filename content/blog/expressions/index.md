+++
title = "Thinking in Expressions"
date = 2025-01-16
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

Rust's focus on expressions is an underrated aspect of the language.
Ideas flow more naturally once you embrace expressions as a core mechanic in Rust.
I would go as far as to say that expressions shaped the way I think about control flow in general. 

"Everything is an expression" is a bit of an exaggeration, but it's a useful mental model while you 
internalize the concept.

But what's so special about them?

## Expressions produce values, statements do not. 

The difference between expressions and statements can easily be dismissed as a minor detail. Underneath the surface, though, expressions have a deep impact on the ergonomics of a language. 

In Rust, most things produce a value: literals, variables, function calls, blocks, and control flow statements like `if`, `match`, and `loop`. 
Even [`&`](https://doc.rust-lang.org/reference/expressions/operator-expr.html#borrow-operators) and [`*`](https://doc.rust-lang.org/reference/expressions/operator-expr.html#the-dereference-operator) are expressions in Rust. 

## Expressions In Rust vs other languages

Rust inherits expressions from its functional roots in the [ML family of languages](https://en.wikipedia.org/wiki/ML_(programming_language)); they are not so common in other languages. 

Go, C++, Java, and TypeScript have expressions, too, but they pale in comparison to Rust.

In Go, for example, an `if` statement is... well, a statement and not an expression. This has some surprising side-effects. For example, you can't use an `if` statement in a ternary expression like you would in Rust. 

```go
// This is not valid Go code!
let x = if condition { 1 } else { 2 };
```

Instead, you'd have to write a full-blown `if` statement
along with a slightly unfortunate upfront variable declaration:

```go
var x int
if condition {
	x = 1
} else {
	x = 2
}
```

While this works, but it requires a conscious effort to memorize when you can use expressions and when not.

Since `if` is an expression in Rust, using it in a ternary expression is perfectly normal. 

```rust
let x = if condition { 1 } else { 2 };
```

This explains the absence of the ternary operator  in Rust (there is no `x = condition ? 1 : 2;`).
It's simply not needed because `if` is equally concise but more versatile. 

Also note that in comparison to Go, our variable `x` does not need to be mutable. 

In combination with pattern matching, expressions in Rust become even more powerful:

```rust
let (a, b) = if condition { ("first", true) } else { ("second", false) };
```

Here, the left side of the assignment (a, b) is a pattern that destructures the tuple returned by the `if-else` expression.

What if you deal with more complex control flow? 
That's not a problem. [`match` is an expression](https://doc.rust-lang.org/reference/expressions/match-expr.html), too:

```rust
let color = match duck {
    Duck::Huey => "Red",
    Duck::Dewey => "Blue",
    Duck::Louie => "Green",
};
```

It is common to assign the result of a `match` expression to a variable.

## Combining `match` and `if` Expressions

In Rust, you can combine `match` and `if` expressions to create complex logic in a few lines of code.
Let's say you want to return a duck's color, but you want to return the correct color based on the year.
(In the early Disney comics, the nephews were wearing different colors.)

```rust
let color = match duck {
    // In early comic books, the ducks
    // were colored randomly
    _ if year < 1980 => random_color(),
    
    // In the early 80s, Huey's cap was pink
    Duck::Huey if year < 1982 => "Pink",
    
    // Since 1982, the ducks have dedicated colors
    Duck::Huey => "Red",
    Duck::Dewey => "Blue",
    Duck::Louie => "Green",
};
```

Neat, right? You can cover a lot of ground in a few lines of code.

Note: those `if`s are called match arm guards, and they really *are* full-fledged `if` expressions.
You can put anything in there that you could put in a regular `if` statement! Check the [language reference](https://doc.rust-lang.org/reference/expressions/match-expr.html) for details.

## Lesser known facts about expressions

### `break` is an expression

You can return a value from a loop with `break`:

```rust
let foo = loop { break 1 };
// foo is 1
```

More commonly, you'd use it like this:

```rust
let result = loop {
    counter += 1;
    if counter == 10 {
        break counter * 2;
    }
};
// result is 20
```

### `dbg!()` returns the value of the inner expression
  
You can wrap any expression with `dbg!()` without changing the behavior of your code (aside from the debug output).

```rust
let x = dbg!(compute_complex_value());
```
  
## A Practical Refactoring Example

So far, I showed you some fancy expression tricks, but how do you apply this in practice? 

To illustrate this, imagine you have a `Config` struct that reads a configuration file from a given path:

```rust
/// Configuration for the application
pub struct Config {
    config_path: PathBuf,
}

/// Creates a new Config with the given path
///
/// The path is resolved against the home directory if relative.
/// Validates that the path exists and has the correct extension.
impl Config {
    pub fn with_config_path(path: PathBuf) -> Result<Self, std::io::Error> {
        todo!()
    }
}
```

Here's how you might implement the `with_config_path` method in an imperative style:

```rust
impl Config {
    pub fn with_config_path(path: PathBuf) -> Result<Self, std::io::Error> {
        // First determine the base path
        let mut config_path;
        if path.is_absolute() {
            config_path = path;
        } else {
            let home = get_home_dir();
            if home.is_none() {
                return Err(io::Error::new(
                    io::ErrorKind::NotFound,
                    "Home directory not found",
                ));
            }
            config_path = home.unwrap().join(path);
        }

        // Do validation
        if !config_path.exists() {
            return Err(io::Error::new(
                io::ErrorKind::NotFound,
                "Config path does not exist",
            ));
        }

        if config_path.is_file() {
            let ext = config_path.extension();
            if ext.is_none() {
                return Err(io::Error::new(
                    io::ErrorKind::InvalidInput,
                    "Config file must have .conf extension",
                ));
            }
            if ext.unwrap().to_str() != Some("conf") {
                return Err(io::Error::new(
                    io::ErrorKind::InvalidInput,
                    "Config file must have .conf extension",
                ));
            }
        }

        return Ok(Self { config_path });
    }
}
```

There are a few things we can improve here:

- The code is quite imperative 
- Lots of temporary variables
- Explicit mutation with `mut`
- Nested if statements
- Manual unwrapping with `is_none()`/`unwrap()`

## Tip 1: Remove the unwraps

It's always a good idea to critically look at `unwrap()` calls and see if there's a better way.
While we "only" have two `unwrap()` calls here, both point at flaws in our design.

```rust
let mut config_path;
if path.is_absolute() {
    config_path = path;
} else {
    let home = get_home_dir();
    if home.is_none() {
        return Err(io::Error::new(
            io::ErrorKind::NotFound,
            "Home directory not found",
        ));
    }
    config_path = home.unwrap().join(path);
}
```

We know that `home` is not `None` when we `unwrap` it, because we checked it before.
But what if we refactor the code? We might forget about this check and introduce a bug.

This can be rewritten as:

```rust
let config_path = if path.is_absolute() {
    path
} else {
    let home = get_home_dir().ok_or_else(|| io::Error::new(
        io::ErrorKind::NotFound,
        "Home directory not found",
    ))?;
    home.join(path)
};
```

Or, if you introduced a custom error type:

```rust
let config_path = if path.is_absolute() {
    path
} else {
    let home = get_home_dir().ok_or_else(|| ConfigError::HomeDirNotFound)?;
    home.join(path)
};
```

The other `unwrap` is also unnecessary and makes the happy path harder to read.
Here is the original code: 

```rust
if config_path.is_file() {
    let ext = config_path.extension();
    if ext.is_none() {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Config file must have .conf extension",
        ));
    }
    if ext.unwrap().to_str() != Some("conf") {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Config file must have .conf extension",
        ));
    }
}
```

We can rewrite this as:

```rust
if config_path.is_file() {
    let Some(ext) = config_path.extension() else {
        return Err(...);
    }
    if ext != "conf" {
        return Err(...);
    }
}
```

Or we return early to avoid the nested `if`:

```rust
if !config_path.is_file() {
    return Err(...);
}

let Some(ext) = config_path.extension() else {
    return Err(...);
}

if ext != "conf" {
    return Err(io::Error::new(...));
}
```

([Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=f852d031661536d4cac9f8ac3c9d7317))

## Tip 2: Remove the `mut`s 

Usually, my next step is to get rid of as many `mut` variables as possible.

However, after our refactor, there are no more `mut` keywords in the function!
This is a typical pattern in Rust: often when we get rid of an `unwrap()`, we can remove a `mut` as well. 

Nevertheless, it is always a good idea to look for `mut` variables and see if they are really necessary. 

## Tip 3: Remove the explicit return statements

The last expression in a block is implicitly returned
and that `return` is an expression itself, so you can often get rid of explicit `return` statements.

For example, we can remove the `return` in the last line of the function:

```rust
return Ok(Self { config_path });
```

becomes

```rust
Ok(Self { config_path })
```

Another simple heuristic is to hunt for `returns` and semicolons in the middle of your code.
These are like "seams" in our program; stop signs, which break the natural flow of data.
Almost effortlessly, removing those blockers / stop signs often improves the code flow; it's like magic. 

For example, the above validation code can also be written without returns:

```rust
match config_path {
    path if !path.is_file() => Err(io::Error::new(
        io::ErrorKind::InvalidInput,
        "Config path is not a file",
    )),
    path if path.extension() != Some(OsStr::new("conf")) => Err(io::Error::new(
        io::ErrorKind::InvalidInput,
        "Config file must have .conf extension",
    )),
    _ => Ok(())
}
```

I like that, because we avoid one error message duplication and all conditions start on the left.
Whether you prefer that over `let-else` is a matter of taste. [^let-else-statement]

[^let-else-statement]: By the way, `let-else` is not an expression, but a statement. That's because the `else` branch doesn't produce a value. Instead, it moves the "failure" case into the body block, while allowing the "success" case to continue in the surrounding context without additional nesting.  I recommend reading the [RFC](https://rust-lang.github.io/rfcs/3137-let-else.html) for more details.

## Don't take it too far

Remember that I said "everything is an expression"?
Don't take this too far or people will quickly think you're a goofball.

It's fun to know that you could use `then_some`, `unwrap_or_else`, and `map_or` to chain expressions together, but please
don't stretch it too far.

```rust
impl Config {
    pub fn with_config_path(path: PathBuf) -> Result<Self, io::Error> {
        (if path.is_absolute() {
            Ok(path)
        } else {
            get_home_dir()
                .ok_or_else(/* error */)
                .map(|home| home.join(path))
        })
        .and_then(|config_path| {
            (!config_path.exists())
                .then_some(Err(/* error */))
                .unwrap_or_else(|| {
                    config_path
                        .is_file()
                        .then(|| {
                            (!config_path
                                .extension()
                                .map_or(false, |ext| ext == "conf"))
                                .then_some(Err(/* error */))
                                .unwrap_or(Ok(()))
                        })
                        .unwrap_or(Ok(()))
                        .map(|_| config_path)
                })
        })
        .map(|config_path| Self { config_path })
    }
}
```

This code is correct, but the combinators get in the way of readability.
It feels more like a Lisp program than Rust code.
Keep your friends and colleagues in mind when writing code.
Find a balance between expressiveness and readability.

## Conclusion

Expressions tend to guide you towards more ergonomic Rust code. 

If you find that your code doesn't feel idiomatic, see if expressions can help. 
Once you find the right balance, they are a joy to use -- especially in smaller context where data flow is key.

The "trifecta" of iterators, expressions, and pattern matching is the foundation of data transformations in Rust.
I also wrote an article about iterators [here](/blog/iterators/).

Of course, it's not forbidden to mix expressions and statements!
For example, I personally like to use `let-else` statements when it makes my code easier to understand.
If you're unsure about whether using an expression is worth it, seek feedback from someone less familiar with Rust.
If they look confused, you probably tried to be too clever. 

There are other languages which have a similar focus on expressions, but it's less common in a systems programming context. 

Now, try to refactor some code to train that muscle.