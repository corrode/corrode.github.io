+++
title = "Effective Use Of Expressions In Rust"
date = 2024-08-07
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

Rust's emphasis on expressions is an underrated aspect of the language.

Expressions produce a value, statements do not. 

In Rust, this includes literals, variables, function calls, blocks, and even control flow statements like `if`, `match`, and `loop`. 
Rust inherits expressions from its functional roots in the [ML family of languages](https://en.wikipedia.org/wiki/ML_(programming_language)); they are not so common in languages like C, Java, or Go.

Expressions can easily be dismissed as a minor detail, a nuance in Rust's syntax. Underneath the surface, though, expressions have a deep impact on the ergonomics of writing Rust.

"Everything is an expression" is a bit of an exaggeration, but it's a useful mental model while you 
internalize the concept.

Rust becomes way more accessible once you embrace expressions as the core building block of the language. I would go as far as to say that they shaped the way I think about code in *any* language.

## Expressions In Rust vs other languages

Languages like Go, C++, Java, TypeScript have expressions, too!
They pale in comparison to Rust, though.

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

You get used to that, but you have to memorize when you can use expressions. It also breaks the flow of your code, as you have to introduce a new variable. Switching between statements and expressions requires a mental context switch.

Since `if` is an expression in Rust, using it in a ternary expression is perfectly normal. 

```rust
let x = if condition { 1 } else { 2 };
```

Also note that in comparison to Go, our variable `x` does not need to be mutable. 

In combination with pattern matching, expressions in Rust are even more powerful:

```rust
let (a, b) = if condition { ("first", true) } else { ("second", false) };
```

Here, the left side of the assignment (a, b) is a pattern that destructures the tuple returned by the if-else expression.

What if you deal with an optional value which gets returned by a function?
That's not a problem. [`match` is an expression](https://doc.rust-lang.org/reference/expressions/match-expr.html), too:

```rust
let x = match foo() {
    Some(x) => x,
    None => return,
};
```

In many other languages, `match` is a statement. 
Python is an example of that and they even [decided against changing that](https://peps.python.org/pep-0622/#make-it-an-expression) for consistency reasons. In Rust, it's just another building block that fits everywhere.

In languages like C, you'd write a switch statement instead:

```c
int x;
switch (foo()) {
    case Some:
        x = foo();
        break;
    case None:
        return;
}
```

Since switch statements are just statements, you can't assign their result to a variable. You have to introduce a new variable and assign it inside the case block.

Rust doesn't have this limitation. You can assign the result of a `match` expression to a variable, just like any other expression.

The Rust `match` expression above might look quite verbose for what it does. Thankfully, there's `let-else`:

```rust
let Some(x) = foo() else { return };
```

Strictly speaking, `let-else` is **not** an expression, but a statement.
That might surprise you, given that I dwelled on expressions so much. In reality, this is an important special case which is
by design, because the "failure" variant of a `let-else` statement must return 
`!` (a.k.a. the "never" type), which represents the type of computations which *never* resolve to any value at all. For example, `return` and `break` are such computations. [^1]

So the `else` branch doesn't yield a value, which is why `let-else` cannot be an expression.

[^1]: You can read up on the details in the [RFC](https://rust-lang.github.io/rfcs/3137-let-else.html)

Nevertheless, `let-else` works well in combination with expressions: 

```rust
let result = {
    let Some(x) = foo() else { return };
    x * 2
};
```

Here, the block returns the value of `x * 2`, which gets assigned to `result`.

## A Practical Refactoring Example

So far, these examples hardly capture the full elegance of expressions.
As with many other concepts in Rust, it's hard to internalize expressions without practice. Let's make it more tangible.

We hunt for `returns` and semicolons in the middle of the code. These are like "seams" in our program; stop signs, which break the natural flow of data. Almost effortlessly, removing those blockers / stop signs will lead to better code; it's like magic. 

Here's an abstracted version of a function, which returns the correct path to a configuration file.

Imagine, that the following rules apply:

- If a path is provided, create the config file at that path. 
- If no path is provided:
  - If $HOME is set, use `$HOME/.config/my_app/`
  - Use the current directory otherwise

```rust
use std::path::PathBuf;
use std::env;

fn config_file_path(config_path: Option<PathBuf>) -> PathBuf {
    if let Some(path) = config_path {
        return path;
    } else {
        // Note: don't use `home_dir` in production code as it's deprecated
        // Use the `dirs` or `directories` crates instead
        if let Some(home_dir) = env::home_dir() {
            let config_dir = home_dir.join(".config/my_app/");
            return config_dir;
        } else {
            // Fallback to the current directory
            return PathBuf::from(".");
        }
    }
}
```

There are some issues with this code, but for now let's focus our attention solely on expressions vs. statements.

## Refactoring with Expressions In Mind

The first observation is that we have multiple return statements in the middle of our function.
This can make the code harder to follow and reason about.

As discussed earlier, let's try to remove the extra `return` statements in the middle of the code.
Let's refactor the code to have a single return statement at the end by assigning the result of the entire `match` expression to a variable:

```rust
use std::path::PathBuf;
use std::env;

fn config_file_path(config_path: Option<PathBuf>) -> PathBuf {
    let path = match config_path {
        Some(path) => path,
        None => match env::home_dir() {
            Some(home_dir) => home_dir.join(".config/my_app/"),
            None => PathBuf::from("."),
        },
    };
    return path;
}
```

We removed the `returns`, but note that we also got rid of many semicolons in the process.
That's usually a good sign that we're on the right track: we don't need temporary variables anymore, so we can get rid of the semicolons. 

It works because the `if` and `match` expressions return the value of the last expression in the block. (It's expressions all the way down!)

The `let foo = match ...` pattern is a common idiom which Rustaceans use quite frequently.

Let's focus on this part, which tries to find the correct config directory:

```rust
if let Some(home_dir) = env::home_dir() {
    let config_dir = home_dir.join(".config/my_app/");
    config_dir.to_path_buf()
} else {
    PathBuf::from(".")
}
```

Note the semicolon here. It blocks the flow and forces us to introduce a temporary variable, `config_dir`.
Could we rewrite this into a single expression?

Sure thing:

```rust
if let Some(home_dir) = env::home_dir() {
    home_dir.join(".config/my_app/").to_path_buf()
} else {
    PathBuf::from(".")
};
```

This avoids the temporary variable. We could even go one step further and use a monadic style with `map` and `unwrap_or_else`:

```rust
let path = env::home_dir()
    .map(|home_dir| home_dir.join(".config/my_app/"))
    .unwrap_or_else(|| PathBuf::from("."));
```

Take a moment to reflect on this: which version do you prefer? Why?
Which version is easier to read and understand? &ndash; not just for you, but for your fellow engineers?

There is no right or wrong answer here. It's a matter of taste.

The new version is definitely concise, but it can also reduce readability. The `unwrap_or_else` method ends with the case where `config_path` is `None`, which isn't immediately clear. It feels backwards. The closure code seems like a refinement rather than a distinct next step.

The `.map` and `.unwrap_or_else` combination requires understanding that the first line might fail, forcing the reader to juggle the context and jump between the lines. Depending on your background, this might be okay, but it could be a problem for others and a source of logic bugs.

As with every design decision, there are trade-offs.

Let's take a step back and try a completely different approach for our original function.
An imperative approach, with clear steps.

```rust
/// Get the path for the configuration file
fn config_file_path(config_path: Option<PathBuf>) -> PathBuf {
    // Check if a path was provided
    if let Some(path) = config_path {
        return path; 
    }

    // Check if the home directory is set
    if let Some(home_dir) = env::home_dir() {
        return home_dir.join(".config/my_app/");
    }

    // Fallback to the current directory
    PathBuf::from(".")
}
```

The semicolons and returns are back, but the code is easier to understand.
We're almost back to where we started, but with early returns.

Which version do you prefer now?
Sometimes, it's helpful to try a few different approaches and see which one feels best.

If it's hard to explain, it's probably too complex.

## Mixing Expressions and Statements

Another variant is to use `let-else`, which is a nice way to handle the case where `env::home_dir()` returns `None`:

```rust
let Some(home_dir) = env::home_dir() else {
    // Fallback to the current directory
    return PathBuf::from(".")
};

home_dir.join(".config/my_app/")
```

Now that the logic got moved to a separate function, we can easily return that.

Which variant you prefer is a matter of taste and readability.

I like the fact that expressions are so versatile and that they don't stand in
conflict with imperative code. You can mix and match them as you see fit.

## Fluent Error handling in expressions

Another great thing about expressions is that they integrate well with Rust's error handling story.

For example, what if we want to return an error if the home directory is not found?
We can use the `?` operator to propagate the error:

```rust
use std::path::PathBuf;
use std::env;
use std::io;

fn get_config_path(config_path: Option<PathBuf>) -> Result<PathBuf, std::io::Error> {
    // Check if a path was provided
    if let Some(path) = config_path {
        return Ok(path); 
    }

    // Check if the home directory is set
    let home_dir = env::home_dir().ok_or_else(|| io::Error::new(io::ErrorKind::NotFound, "Home directory not found"))?;

    Ok(home_dir.join(".config/my_app/"))
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=54a36a1dbf0b02ffb6df353bc7c568cd))

The line starting with `let home_dir = ...` is a single expression which immediately returns an error if the home directory is not found. There's no need to break the data flow with multiple statements, temporary variables, or explicit error handling.

You could even introduce your own error type to make it more concise:

```rust
use std::path::PathBuf;
use std::env;

#[derive(Debug)]
enum ConfigError {
    HomeDirNotFound,
}

fn get_config_path(config_path: Option<PathBuf>) -> Result<PathBuf, ConfigError> {
    // Check if a path was provided
    if let Some(path) = config_path {
        return Ok(path); 
    }

    // Check if the home directory is set
    let home_dir = env::home_dir().ok_or(ConfigError::HomeDirNotFound)?;

    Ok(home_dir.join(".config/my_app/"))
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=011d5a28fd5c9fed616e7af762b4f682))

In this example, errors still get handled properly, but the code is more concise and the data flow does not get interrupted.
There's no need for a separate error handling block as in Go, which takes the attention away from the main logic.

```go
// That old error handling dance in Go
if err != nil {
	return nil, err
}
```

Unlike Go, Rust's error handling integrates naturally into the code flow. It works really well with expressions.
In most cases we don't have to annotate our expressions with types either, because Rust can infer them from the context.
By leaning into expressions, the core logic stays in the foreground while errors are still handled correctly.
This is one of my favorite aspects of Rust.

There are other languages like Ruby which [have a similar focus on expressions](https://ruby-doc.com/docs/ProgrammingRuby/html/tut_expressions.html), but it's very impressive that this expressiveness is available in a systems programming language.

## Conclusion

When you try to refactor your code, keep expressions in mind.

Almost naturally and without force you go from imperative code to a more
declarative style, expressing the steps of computation removing overly
verbose sections and temporary variables.

Expressions tend to guide you towards more ergonomic &ndash; shall I say economic &ndash; Rust code and avoid repetition. 

You might have been aware of expressions in Rust before, but maybe you didn't fully catch on to the significance of them.

If you find that your code doesn't feel idiomatic, look for expressions. Remove redundant semicolons, temporary variables, and unnecessary return statements. They are like stop signs to go and reflect on.
Once you get rid of them, you'll find that your code becomes more data-focused and fluent. 

Of course, it's fine to mix expressions and statements.
The core idea is the combination/concatentaion of "small ideas" into bigger programs. Like lego blocks. Simple and to the point, but not convoluted. If you're unsure about whether using an expression is worth it, get feedback from a Rust beginner. If they look confused, you probably tried to be too clever. 

Expressions are very... expressive. It takes a bit of practice to get acquainted with
them and to find the right balance, but then they are a joy to use.
Especially in smaller context where data flow is key. Iterators and expressions go well together and together with pattern matching they build the foundation with how I do small-scale data transformations in Rust.
Ideally, you want to go from input to output with small, easy steps.

Now, try to refactor some code to train that muscle.