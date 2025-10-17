+++
title = "Patterns for Defensive Programming in Rust"
date = 2025-10-17
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

All we can work with are hard-learned patterns to write more defensive Rust code, learned throughout years of shipping Rust code to production,
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
The problem is that indexing into a vector is decoupled from checking its length: these are two separate operations, which can be changed independently without the compiler ringing alarm. 

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

## Code Smell: Lazy Use of `Default`

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

## Code Smell: `From` Impls That Are Really `TryFrom`

Sometimes there's no conversion that will work 100% of the time.
That's fine.
When that's the case, resist the tempatation to offer a `From` implementation out of habit; use `TryFrom` instead.

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
The problem is that you might forget to handle a new case which got added later.

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

## Code Smell: Not Future-Proofing Trait Implementations

Consider this `PartialEq` implementation:

```rust
impl PartialEq for MyType {
    fn eq(&self, other: &Self) -> bool {
        self.field1 == other.field1 && self.field2 == other.field2
    }
}
```

But what if you add a new field later?
The compiler won't warn you that it might need to be added to your `PartialEq` implementation.

You could `derive(PartialEq)` but that's not always possible.
Instead, spell out the fields explicitly by destructuring:

```rust
impl PartialEq for MyType {
    fn eq(&self, other: &Self) -> bool {
        let Self { field1: f1, field2: f2, field3: f3 } = self;
        let Self { field1: o1, field2: o2, field3: o3 } = other;

        f1 == o1 && f2 == o2 && f3 == o3
    }
}
```

Again, the compiler will warn you if you forget to add a new field to the `PartialEq` implementation.

We can still decide to ignore fields from comparison, but we capture the fields so we have to do so explicitly:

```rust
impl PartialEq for MyType {
    fn eq(&self, other: &Self) -> bool {
        let Self { field1: f1, field2: f2, field3: _ } = self; // Explicitly ignore field3
        let Self { field1: o1, field2: o2, field3: _ } = other;

        f1 == o1 && f2 == o2
    }
}
```

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

## Conclusion

Defensive programming in Rust is about leveraging the type system and compiler to catch bugs before they happen.
By following these patterns, you can:

- Make implicit invariants explicit and compiler-checked
- Future-proof your code against refactoring mistakes
- Reduce the surface area for bugs

It's a skill that doesn't come naturally and it's not covered in most Rust books, but knowing these patterns can make the difference between code that works but is brittle, and code that is robust and maintainable for years to come.

Remember: if you find yourself writing `// this should never happen`, take a step back and ask how the compiler could enforce that invariant for you instead.
The best bug is the one that never compiles in the first place.
