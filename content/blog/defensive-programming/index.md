+++
title = "Patterns for Defensive Programming in Rust"
date = 2025-11-03
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

I have a hobby.

Whenever I see the comment `// this should never happen` in code, I try to find out the exact conditions under which *it could* happen. 
And in 90% of cases, I find a way to do just that. 
More often than not, the developer just hasn't considered all edge cases or future code changes.

In fact, the reason why I like this comment so much is that it often **marks the exact spot** where strong guarantees fall apart.
Often, violating implicit invariants that aren't enforced by the compiler are the root cause.

Yes, the compiler prevents memory safety issues, and the standard library is best-in-class.
But even the standard library [has its warts](/blog/pitfalls-of-safe-rust) and bugs in business logic can still happen.

All we can work with are hard-learned patterns to write more defensive Rust code, learned throughout years of shipping Rust code to production.
I'm not talking about design patterns here, but rather small idioms, which are rarely documented, but make a big difference in the overall code quality.

## Code Smell: Indexing Into a Vector

Here's some innocent-looking code:


```rust
match matching_users.len() {
    1 => {
        let existing_user = &matching_users[0];
        // ...
    }
    _ => Err(RepositoryError::DuplicateUsers)
}
```

This code works for now, but what if you refactor it and forget to keep the length check?
That's our first implicit invariant that's not enforced by the compiler.
The problem is that indexing into a vector is decoupled from checking its length: these are two separate operations, which can be changed independently without the compiler ringing the alarm. 

If we use slice pattern matching, we'll only get access to the element if the `match` arm is executed. 

```rust
match matching_users.as_slice() {
    [existing_user] => {  // Safe! Compiler guarantees exactly one element
        // ...
    }
    [] => Ok(Success::NotFound),
    _ => Err(RepositoryError::DuplicateUsers)
}
```

Note how this automatically uncovered one more edge case: what if the list is empty?
We hadn't considered this case before.
The compiler-enforced pattern matching forces us to think about all possible states!
This is a common pattern throughout robust Rust code, the attempt to put the compiler in charge of enforcing invariants.

## Code Smell: Lazy use of `Default`

When initializing an object with many fields, it's tempting to use `..Default::default()` to fill in the rest.
In practice, this is a common source of bugs.
You might forget to explicitly set a new field later when you add it to the struct (thus using the default value instead, which might not be what you want), or you might not be aware of all the fields that are being set to default values.

Instead of this:

```rust
let foo = Foo {
    field1: value1,
    field2: value2,
    ..Default::default()  // Implicitly sets all other fields
};
```

Do this:

```rust
let foo = Foo {
    field1: value1,
    field2: value2,
    field3: value3, // Explicitly set all fields
    field4: value4,
    // ...
};
```

Yes, it's slightly more verbose, but what you gain is that the compiler will force you to handle all fields explicitly.
Now when you add a new field to `Foo`, the compiler will remind you to set it here as well and reflect on which value makes sense.

If you still prefer to use `Default` but don't want to lose compiler checks, you can also destructure the default instance:

```rust
let Foo { field1, field2, field3, field4 } = Foo::default();
```

This way, you get all the default values assigned to local variables and you can still override what you need:

```rust
let foo = Foo {
    field1: value1,    // Override what you need
    field2: value2,    // Override what you need
    field3,            // Use default value
    field4,            // Use default value
};
```

This pattern gives you the best of both worlds:
- You get default values without duplicating default logic
- The compiler will complain when new fields are added to the struct
- Your code automatically adapts when default values change
- It's clear which fields use defaults and which have custom values

## Code Smell: Fragile Trait Implementations

Completely destructuring a struct into its components can also be a defensive strategy for API adherence.
For example, let's say you're building a pizza ordering system and have an order type like this:

```rust
struct PizzaOrder {
    size: PizzaSize,
    toppings: Vec<Topping>,
    crust_type: CrustType,
    ordered_at: SystemTime,
}
```

For your order tracking system, you want to compare orders based on what's actually on the pizza - the `size`, `toppings`, and `crust_type`. The `ordered_at` timestamp shouldn't affect whether two orders are considered the same.

Here's the problem with the obvious approach:

```rust
impl PartialEq for PizzaOrder {
    fn eq(&self, other: &Self) -> bool {
        self.size == other.size 
            && self.toppings == other.toppings 
            && self.crust_type == other.crust_type
            // Oops! What happens when we add extra_cheese or delivery_address later?
    }
}
```

Now imagine your team adds a field for customization options:

```rust
struct PizzaOrder {
    size: PizzaSize,
    toppings: Vec<Topping>,
    crust_type: CrustType,
    ordered_at: SystemTime,
    extra_cheese: bool, // New field added
}
```

Your `PartialEq` implementation still compiles, but is it correct?
Should `extra_cheese` be part of the equality check?
Probably yes - a pizza with extra cheese is a different order!
But you'll never know because the compiler won't remind you to think about it.

Here's the defensive approach using destructuring:

```rust
impl PartialEq for PizzaOrder {
    fn eq(&self, other: &Self) -> bool {
        let Self {
            size,
            toppings,
            crust_type,
            ordered_at: _,
        } = self;
        let Self {
            size: other_size,
            toppings: other_toppings,
            crust_type: other_crust,
            ordered_at: _,
        } = other;

        size == other_size && toppings == other_toppings && crust_type == other_crust
    }
}
```

Now when someone adds the `extra_cheese` field, this code won't compile anymore.
The compiler forces you to decide: should `extra_cheese` be included in the comparison or explicitly ignored with `extra_cheese: _`?

This pattern works for any trait implementation where you need to handle struct fields: `Hash`, `Debug`, `Clone`, etc.
It's especially valuable in codebases where structs evolve frequently as requirements change.

## Code Smell: `From` Impls That Are Really `TryFrom`

Sometimes there's no conversion that will work 100% of the time.
That's fine.
When that's the case, resist the temptation to offer a `From` implementation out of habit; use `TryFrom` instead.

Here's an example of `TryFrom` in disguise:

```rust
impl From<&DetectorStartupErrorReport> for DetectorStartupErrorSubject {
    fn from(report: &DetectorStartupErrorReport) -> Self {
        let postfix = report
            .get_identifier()
            .or_else(get_binary_name)
            .unwrap_or_else(|| UNKNOWN_DETECTOR_SUBJECT.to_string());

        Self(StreamSubject::from(
            format!("apps.errors.detectors.startup.{postfix}").as_str(),
        ))
    }
}
```

The `unwrap_or_else` is a hint that this conversion can fail in some way.
We set a default value instead, but is it really the right thing to do for all callers?
This should be a `TryFrom` implementation instead, making the fallible nature explicit.
We fail fast instead of continuing with a potentially flawed business logic.

## Code Smell: Non-Exhaustive Matches

It's tempting to use `match` in combination with a catch-all pattern like `_ => {}`, but this can haunt you later.
The problem is that you might forget to handle a new case that was added later.

Instead of:

```rust
match self {
    Self::Variant1 => { /* ... */ }
    Self::Variant2 => { /* ... */ }
    _ => { /* catch-all */ }
}
```

Use:

```rust
match self {
    Self::Variant1 => { /* ... */ }
    Self::Variant2 => { /* ... */ }
    Self::Variant3 => { /* ... */ }
    Self::Variant4 => { /* ... */ }
}
```

By spelling out all variants explicitly, the compiler will warn you when a new variant is added, forcing you to handle it.
Another case of putting the compiler to work.

If the code for two variants is the same, you can group them:

```rust
match self {
    Self::Variant1 => { /* ... */ }
    Self::Variant2 => { /* ... */ }
    Self::Variant3 | Self::Variant4 => { /* shared logic */ }
}
```

## Code Smell: `_` Placeholders for Unused Variables

Using `_` as a placeholder for unused variables can lead to confusion.
For example, you might get confused about which variable was skipped.
That's especially true for boolean flags:

```rust
match self {
    Self::Rocket { _, _, .. } => { /* ... */ }
}
```

In the above example, it's not clear which variables were skipped and why.
Better to use descriptive names for the variables that are not used:

```rust
match self {
    Self::Rocket { has_fuel: _, has_crew: _, .. } => { /* ... */ }
}
```

Even if you don't use the variables, it's clear what they represent and the code becomes more readable and easier to review without inline type hints.

## Pattern: Temporary Mutability

If you only want your data to be mutable temporarily, make that explicit.

```rust
let mut data = get_vec();
data.sort();
let data = data;  // Shadow to make immutable

// Here `data` is immutable.
```

This pattern is often called "temporary mutability" and helps prevent accidental modifications after initialization.
See the [Rust unofficial patterns book](https://rust-unofficial.github.io/patterns/idioms/temporary-mutability.html) for more details.

You can go one step further and do the initialization part in a scope block:

```rust
let data = {
    let mut data = get_vec();
    data.sort();
    data  // Return the final value
};
// Here `data` is immutable
```

This way, the mutable variable is confined to the inner scope, making it clear that it's only used for initialization.
In case you use any temporary variables during initialization, they won't leak into the outer scope.
In our case above, there were none, but imagine if we had a temporary vector to hold intermediate results:

```rust
let data = {
    let mut data = get_vec();
    let temp = compute_something();
    data.extend(temp);
    data.sort();
    data  // Return the final value
};
```

Here, `temp` is only accessible within the inner scope, which prevents it from accidental use later on.

### Scoped Temporary Mutability

You can take this further by wrapping the initialization in a scope block to ensure temporary variables don't leak:

```rust
let data = {
    let mut data = get_vec();
    let temp = compute_something();
    data.extend(temp);
    data.sort();
    data  // Return the final value
};

// Here `data` is immutable and `temp` is out of scope
```

This is especially useful when you have multiple temporary variables during initialization that you don't want accessible in the rest of the function.
The scope makes it crystal clear that these variables are only meant for initialization.

## Pattern: Defensively Handle Constructors

Let's say you had a simple type like the following:

```rust
pub struct S {
    field1: String,
    field2: u32,
}
```

Now you want to make invalid states unrepresentable.
One pattern is to return a `Result` from the constructor.

```rust
impl S {
    pub fn new(field1: String, field2: u32) -> Result<Self, String> {
        if field1.is_empty() {
            return Err("field1 cannot be empty".to_string());
        }
        if field2 == 0 {
            return Err("field2 cannot be zero".to_string());
        }
        Ok(Self { field1, field2 })
    }
}
```

But nothing stops someone from creating an instance of `S` directly:

```rust
let s = S {
    field1: "".to_string(),
    field2: 0,
};
```

This should not be possible!
One way to prevent this is to make the struct non-exhaustive:

```rust
#[non_exhaustive]
pub struct S {
    field1: String,
    field2: u32,
}
```

Now the struct cannot be instantiated directly outside of the module.
However, what about the module itself?

One way to prevent this is to add a hidden field:

```rust
pub struct S {
    field1: String,
    field2: u32,
    _private: (),
}
```

Now the struct cannot be instantiated directly even inside the module.
You have to go through the constructor, which enforces the validation logic.

## Pattern: Use `#[must_use]` on Important Types

The `#[must_use]` attribute is often neglected.
That's sad, because it's such a simple yet powerful mechanism to prevent callers from accidentally ignoring important return values.

```rust
#[must_use = "Configuration must be applied to take effect"]
pub struct Config {
    // ...
}

impl Config {
    pub fn new() -> Self {
        // ...
    }

    pub fn with_timeout(mut self, timeout: Duration) -> Self {
        self.timeout = timeout;
        self
    }
}
```

Now if someone creates a `Config` but forgets to use it, the compiler will warn them:

```rust
let config = Config::new();
config.with_timeout(Duration::from_secs(30)); // Warning: unused `Config` that must be used

// Correct usage:
let config = Config::new()
    .with_timeout(Duration::from_secs(30));
apply_config(config);
```

This is especially useful for guard types that need to be held for their lifetime and results from operations that must be checked.
The standard library uses this extensively.
For example, `Result` is marked with `#[must_use]`, which is why you get warnings if you don't handle errors.

## Code Smell: Boolean Parameters

Boolean parameters make code hard to read at the call site and are error-prone.
We all know the scenario where we're sure this will be the last boolean parameter we'll ever add to a function.

```rust
// Too many boolean parameters
fn process_data(data: &[u8], compress: bool, encrypt: bool, validate: bool) {
    // ...
}

// At the call site, what do these booleans mean?
process_data(&data, true, false, true);  // What does this do?
```

It's impossible to understand what this code does without looking at the function signature.
Even worse, it's easy to accidentally swap the boolean values.

Instead, use enums to make the intent explicit:

```rust
enum Compression {
    Strong,
    Medium,
    None,
}

enum Encryption {
    AES,
    ChaCha20,
    None,
}

enum Validation {
    Enabled,
    Disabled,
}

fn process_data(
    data: &[u8],
    compression: Compression,
    encryption: Encryption,
    validation: Validation,
) {
    // ...
}

// Now the call site is self-documenting
process_data(
    &data,
    Compression::Strong,
    Encryption::None,
    Validation::Enabled
);
```

This is much more readable and the compiler will catch mistakes if you pass the wrong enum type.
You will notice that the enum variants can be more descriptive than just `true` or `false`.
And more often than not, there are more than two meaningful options; especially for programs which grow over time.

For functions with many options, you can configure them using a parameter struct:

```rust
struct ProcessDataParams {
    compression: Compression,
    encryption: Encryption,
    validation: Validation,
}

impl ProcessDataParams {
    // Common configurations as constructor methods
    pub fn production() -> Self {
        Self {
            compression: Compression::Strong,
            encryption: Encryption::AES,
            validation: Validation::Enabled,
        }
    }

    pub fn development() -> Self {
        Self {
            compression: Compression::None,
            encryption: Encryption::None,
            validation: Validation::Enabled,
        }
    }
}

fn process_data(data: &[u8], params: ProcessDataParams) {
    // ...
}

// Usage with preset configurations
process_data(&data, ProcessDataParams::production());

// Or customize for specific needs
process_data(&data, ProcessDataParams {
    compression: Compression::Medium,
    encryption: Encryption::ChaCha20,
    validation: Validation::Enabled, 
});
```

This approach scales much better as your function evolves.
Adding new parameters doesn't break existing call sites, and you can easily add defaults or make certain fields optional.
The preset methods also document common use cases and make it easy to use the right configuration for different scenarios.

Rust is often criticized for not having named parameters, but using a parameter struct is arguably even better for larger functions with many options.

## Clippy Lints for Defensive Programming

Many of these patterns can be enforced automatically using Clippy lints.
Here are the most relevant ones:

| Lint | Description |
|------|-------------|
| [`clippy::indexing_slicing`](https://rust-lang.github.io/rust-clippy/master/index.html#indexing_slicing) | Prevents direct indexing into slices and vectors |
| [`clippy::fallible_impl_from`](https://rust-lang.github.io/rust-clippy/master/index.html#fallible_impl_from) | Warns about `From` implementations that can panic and should be `TryFrom` instead. |
| [`clippy::wildcard_enum_match_arm`](https://rust-lang.github.io/rust-clippy/master/index.html#wildcard_enum_match_arm) | Disallows wildcard `_` patterns. |
| [`clippy::unneeded_field_pattern`](https://rust-lang.github.io/rust-clippy/master/index.html#unneeded_field_pattern) | Identifies when you're ignoring too many struct fields with `..` unnecessarily. |
| [`clippy::fn_params_excessive_bools`](https://rust-lang.github.io/rust-clippy/master/index.html#fn_params_excessive_bools) | Warns when a function has too many boolean parameters (4 or more by default). |

You can enable these in your project by adding them to your `Cargo.toml` or at the top of your crate, e.g.

```rust
#![deny(clippy::indexing_slicing)]
```

## Conclusion

Defensive programming in Rust is about leveraging the type system and compiler to catch bugs before they happen.
By following these patterns, you can:

- Make implicit invariants explicit and compiler-checked
- Future-proof your code against refactoring mistakes
- Reduce the surface area for bugs

It's a skill that doesn't come naturally and it's not covered in most Rust books, but knowing these patterns can make the difference between code that works but is brittle, and code that is robust and maintainable for years to come.

Remember: if you find yourself writing `// this should never happen`, take a step back and ask how the compiler could enforce that invariant for you instead.
The best bug is the one that never compiles in the first place.