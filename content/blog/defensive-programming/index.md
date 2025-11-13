+++
title = "Patterns for Defensive Programming in Rust"
date = 2025-11-08
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = [
    { name = "Tyler Stevens", url = "https://www.linkedin.com/in/tpstevens/" },
    { name = "kat", url = "https://www.sakurakat.systems/" },
]
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
if !matching_users.is_empty() {
    let existing_user = &matching_users[0];
    // ...
}
```

What if you refactor it and forget to keep the `is_empty()` check? 
The problem is that the vector indexing is decoupled from checking the length.
So `matching_users[0]` can panic at runtime if the vector is empty.

Checking the length and indexing are two separate operations, which can be changed independently.
That's our first implicit invariant that's not enforced by the compiler.

If we use slice pattern matching instead, we'll only get access to the element if the correct `match` arm is executed. 

```rust
match matching_users.as_slice() {
    [] => todo!("What to do if no users found!?"),
    [existing_user] => {  // Safe! Compiler guarantees exactly one element
        // No need to index into the vector,
        // we can directly use `existing_user` here 
    }
    _ => Err(RepositoryError::DuplicateUsers)
}
```

Note how this automatically uncovered one more edge case: what if the list is empty?
We hadn't explicitly considered this case before.
The compiler-enforced pattern matching requires us to think about all possible states!
This is a common pattern in all robust Rust code: putting the compiler in charge of enforcing invariants.

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

This is especially useful when you have multiple temporary variables during initialization that you don't want accessible in the rest of the function.
The scope makes it crystal clear that these variables are only meant for initialization.

## Pattern: Defensively Handle Constructors

{% info(title="Tip for libraries", icon="crab") %}

The following pattern is only truly helpful for libraries and APIs that need to be robust against future changes.
In such a case, you want to ensure that all instances of a type are created through a constructor function that enforces validation logic.
Because without that, future refactorings can easily lead to invalid states.

For application code, it's probably best to keep things simple.
You typically have all the call sites under control and can ensure that validation logic is always called.

{% end %}

Let's say you have a simple type like the following:

```rust
pub struct S {
    pub field1: String,
    pub field2: u32,
}
```

Now you want to add validation logic to ensure invalid states are never created.
One pattern is to return a `Result` from the constructor:

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

But nothing stops someone from bypassing your validation by creating an instance directly:

```rust
let s = S {
    field1: "".to_string(),
    field2: 0,
};
```

This should not be possible!
It is our implicit invariant that's not enforced by the compiler: the validation logic is decoupled from struct construction.
These are two separate operations, which can be changed independently and the compiler won't complain. 

To force **external code** to go through your constructor, add a private field:

```rust
pub struct S {
    pub field1: String,
    pub field2: u32,
    _private: (), // This prevents external construction 
}

impl S {
    pub fn new(field1: String, field2: u32) -> Result<Self, String> {
        if field1.is_empty() {
            return Err("field1 cannot be empty".to_string());
        }
        if field2 == 0 {
            return Err("field2 cannot be zero".to_string());
        }
        Ok(Self { field1, field2, _private: () })
    }
}
```

Now code outside your module cannot construct `S` directly because it cannot access the `_private` field.
The compiler enforces that all construction must go through your `new()` method, which includes your validation logic!

{% info(title="Why the underscore in `_private`?", icon="info") %}

Note that the underscore prefix is just a **naming convention** to indicate the field is intentionally unused; it's the lack of `pub` that makes it private and prevents external construction.

{% end %}

For libraries that need to evolve over time, you can also use the `#[non_exhaustive]` attribute instead:

```rust
#[non_exhaustive]
pub struct S {
    pub field1: String,
    pub field2: u32,
}
```

This has the same effect of preventing construction outside your crate, but also signals to users that you might add more fields in the future.
The compiler will prevent them from using struct literal syntax, forcing them to use your constructor.

{% info(title="`Should you use #[non_exhaustive]` or `_private`?", icon="info") %}

There's a big difference between these two approaches:

- `#[non_exhaustive]` only works across crate boundaries. **It prevents construction outside your crate.**
- `_private` works at the module boundary. **It prevents construction outside the module**, but within the same crate.

On top of that, some developers find `_private: ()` more explicit about intent: "this struct has a private field that prevents construction."

With `#[non_exhaustive]`, the primary intent is signaling that fields might be added in the future, and preventing construction is more of a side effect.

{% end %}

But what about code within the **same module**?
With the patterns above, code in the same module can still bypass your validation:

```rust
// Still compiles in the same module!
let s = S {
    field1: "".to_string(),
    field2: 0,
    _private: (),
};
```

Rust's privacy works at the module level, not the type level.
Anything in the same module can access private items.

If you need to enforce constructor usage even within your own module, you need a more defensive approach using nested private modules:

```rust
mod inner {
    pub struct S {
        pub field1: String,
        pub field2: u32,
        _seal: Seal,
    }
    
    // This type is private to the inner module
    struct Seal;
    
    impl S {
        pub fn new(field1: String, field2: u32) -> Result<Self, String> {
            if field1.is_empty() {
                return Err("field1 cannot be empty".to_string());
            }
            if field2 == 0 {
                return Err("field2 cannot be zero".to_string());
            }
            Ok(Self { field1, field2, _seal: Seal })
        }
    }
}

// Re-export for public use
pub use inner::S;
```

Now even code in your outer module cannot construct `S` directly because `Seal` is trapped in the private `inner` module.
Only the `new()` method, which lives in the same module as `Seal`, can construct it.
The compiler guarantees that all construction, even internal construction, goes through your validation logic.

You could still access the public fields directly, though.

```rust
let s = S::new("valid".to_string(), 42).unwrap();
s.field1 = "".to_string(); // Still possible to mutate fields directly
```

To prevent that, you can make the fields private and provide getter methods instead:

```rust
mod inner {
    pub struct S {
        field1: String,
        field2: u32,
        _seal: Seal,
    }
    
    struct Seal;
    
    impl S {
        pub fn new(field1: String, field2: u32) -> Result<Self, String> {
            if field1.is_empty() {
                return Err("field1 cannot be empty".to_string());
            }
            if field2 == 0 {
                return Err("field2 cannot be zero".to_string());
            }
            Ok(Self { field1, field2, _seal: Seal })
        }

        pub fn field1(&self) -> &str {
            &self.field1
        }

        pub fn field2(&self) -> u32 {
            self.field2
        }
    }
}
```

Now the only way to create an instance of `S` is through the `new()` method, and the only way to access its fields is through the getter methods.

### When to Use Each

To enforce validation through constructors:

- **For external code**: Add a private field like `_private: ()` or use `#[non_exhaustive]`
- **For internal code**: Use nested private modules with a private "seal" type
- **Choose based on your needs**: Most code only needs to prevent external construction; forcing internal construction is more defensive but also more complex

The key insight is that by making construction impossible without access to a private type, you turn your validation logic from a convention into a guarantee enforced by the compiler. 
So let's put that compiler to work!

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

Now if someone creates a `Config` but forgets to use it, the compiler will warn them
(even with a custom message!):

```rust
let config = Config::new();
// Warning: Configuration must be applied to take effect
config.with_timeout(Duration::from_secs(30)); 

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
| [`clippy::must_use_candidate`](https://rust-lang.github.io/rust-clippy/master/index.html#must_use_candidate) | Suggests adding `#[must_use]` to types that are good candidates for it. |

You can enable these in your project by adding them at the top of your crate, e.g.

```rust
#![deny(clippy::indexing_slicing)]
#![deny(clippy::fallible_impl_from)]
#![deny(clippy::wildcard_enum_match_arm)]
#![deny(clippy::unneeded_field_pattern)]
#![deny(clippy::fn_params_excessive_bools)]
#![deny(clippy::must_use_candidate)]
```

Or in your `Cargo.toml`:

```toml
[lints.clippy]
indexing_slicing = "deny"
fallible_impl_from = "deny"
wildcard_enum_match_arm = "deny"
unneeded_field_pattern = "deny"
fn_params_excessive_bools = "deny"
must_use_candidate = "deny"
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