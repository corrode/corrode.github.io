+++
title = "Thinking in Expressions"
date = 2025-01-21
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
Code feels more natural to compose once you embrace expressions as a core mechanic in Rust.
I would go as far as to say that expressions shaped the way I think about control flow in general.

"Everything is an expression" is a bit of an exaggeration, but it's a useful mental model while you 
internalize the concept.[^reference]

[^reference]: The [Rust Reference](https://doc.rust-lang.org/reference/statements-and-expressions.html) puts it like this: 
    
    > Rust is primarily an expression language. This means that most forms of value-producing or effect-causing evaluation are directed by the uniform syntax category of expressions. Each kind of expression can typically nest within each other kind of expression, and rules for evaluation of expressions involve specifying both the value produced by the expression and the order in which its sub-expressions are themselves evaluated.

But what's so special about them?

## Expressions produce values, statements do not. 

The difference between expressions and statements can easily be dismissed as a minor detail.
Underneath the surface, though, the fact that expressions return values has a profound impact on the ergonomics of a language.

In Rust, most things produce a value: literals, variables, function calls, blocks, and control flow statements like `if`, `match`, and `loop`. 
Even [`&`](https://doc.rust-lang.org/reference/expressions/operator-expr.html#borrow-operators) and [`*`](https://doc.rust-lang.org/reference/expressions/operator-expr.html#the-dereference-operator) are expressions in Rust. 

## Expressions In Rust vs other languages

Rust inherits expressions from its functional roots in the [ML family of languages](https://en.wikipedia.org/wiki/ML_(programming_language)); they are not so common in other languages. 
Go, C++, Java, and TypeScript have them, but they pale in comparison to Rust.

In Go, for example, an `if` statement is... well, a *statement* and not an expression. This has some surprising side-effects. For example, you can't use `if` statements in a ternary expression like you would in Rust:

```go
// This is not valid Go code!
var x = if condition { 1 } else { 2 };
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

Since `if` is an expression in Rust, using it in a ternary expression is perfectly normal. 

```rust
let x = if condition { 1 } else { 2 };
```

That explains the absence of the ternary operator  in Rust (i.e. there is no syntax like `x = condition ? 1 : 2;`).
No special syntax is needed because `if` is comparably concise.

Also note that in comparison to Go, our variable `x` does not need to be mutable. 
As we will see, Rust's expressions often lead to less mutable code. 

In combination with pattern matching, expressions in Rust become even more powerful:

```rust
let (a, b) = if condition { ("first", true) } else { ("second", false) };
```

Here, the left side of the assignment (a, b) is a pattern that destructures the tuple returned by the `if-else` expression.

What if you deal with more complex control flow? 
That's not a problem. [`match` is an expression](https://doc.rust-lang.org/reference/expressions/match-expr.html), too.
It is common to assign the result of a `match` expression to a variable.

```rust
let color = match duck {
    Duck::Huey => "Red",
    Duck::Dewey => "Blue",
    Duck::Louie => "Green",
};
```


## Combining `match` and `if` Expressions

Let's say you want to return a duck's color, but you want to return the correct color based on the year.
(In the early Disney comics, the nephews were wearing different colors.)

```rust
let color = match duck {
    // In early comic books, the
    // ducks were colored randomly
    _ if year < 1980 => random_color(),
    
    // In the early 80s, Huey's cap was pink
    Duck::Huey if year < 1982 => "Pink",
    
    // Since 1982, the ducks have dedicated colors
    Duck::Huey => "Red",
    Duck::Dewey => "Blue",
    Duck::Louie => "Green",
};
```

Neat, right? You can combine `match` and `if` expressions to create complex logic in a few lines of code.

Note: those `if`s are called [match arm guards](https://doc.rust-lang.org/reference/expressions/match-expr.html), and they really *are* full-fledged `if` expressions.
You can put anything in there just like in a regular `if`. 

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

It's always a good idea to examine `unwrap()` calls and find safer alternatives.
While we "only" have two `unwrap()` calls here, both point at flaws in our design.
Here's the first one:

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

We know that `home` is not `None` when we `unwrap` it, because we checked it right above. 
But what if we refactor the code? We might forget the check and introduce a bug.

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

Or, if we introduce a custom error type:

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

Note how there are no more `mut` keywords after our first refactoring.
This is a typical pattern in Rust: often when we get rid of an `unwrap()`, we can remove a `mut` as well. 

Nevertheless, it is always a good idea to look for all `mut` variables and see if they are really necessary. 

## Tip 3: Remove the explicit return statements

The last expression in a block is implicitly returned
and that `return` is an expression itself, so you can often get rid of explicit `return` statements.
In our case that means:


```rust
return Ok(Self { config_path });
```

becomes

```rust
Ok(Self { config_path })
```

Another simple heuristic is to hunt for `returns` and semicolons in the middle of your code.
These are like "seams" in our program; stop signs, which break the natural data flow.
Almost effortlessly, removing these blockers often improves the flow; it's like magic.

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

Remember when I said "everything is an expression"?
Don't take this too far or people will stop inviting you to dinner parties. 

It's fun to know that you could use `then_some`, `unwrap_or_else`, and `map_or` to chain expressions together, but 
don't use them to show off.

The below code is correct, but the combinators get in the way of readability.
Now it feels more like a Lisp program than Rust code.

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

Keep your friends and colleagues in mind when writing code.
Find a balance between expressiveness and readability.

## Conclusion


If you find that your code doesn't feel idiomatic, see if expressions can help. 
They tend to guide you towards more ergonomic Rust code. 

Once you find the right balance, expressions are a joy to use -- especially in smaller context where data flow is key.
The "trifecta" of iterators, expressions, and pattern matching is the foundation of data transformations in Rust.
I wrote a complementary article about iterators [here](/blog/iterators/).

Of course, it's not forbidden to mix expressions and statements!
For example, I personally like to use `let-else` statements when it makes my code easier to understand.
If you're unsure about whether using an expression is worth it, seek feedback from someone less familiar with Rust.
If they look confused, you probably tried to be too clever. 

Now, try to refactor some code to train that muscle.