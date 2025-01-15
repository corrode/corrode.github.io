+++
title = "Using Enums to Represent State"
template = "article.html"
draft = false
date = 2023-08-08
updated = 2024-08-20
[extra]
series = "Idiomatic Rust"
reviews = [ 
    { name = "Maikel", url = "https://mastodon.social/@the@mkl.lol" }
]
+++

Many Rust beginners with a background in systems programming tend to use `bool`
(or even `u8` &ndash; an 8-bit unsigned integer type) to represent *"state"*.

For example, how about a `bool` to indicate whether a user is active or not?

```rust
struct User {
    // ...
    active: bool,
}
```

Initially, this might seem fine, but as your codebase grows,
you'll find that "active" is not a binary state. There are many
different states that a user can be in. For example, a user
might be suspended or deleted. However, extending the user struct
can get problematic, because other parts of the code might
rely on the fact that `active` is a `bool`.

Another problem is that `bool` is not self-documenting. What does
`active = false` mean? Is the user inactive? Or is the user
deleted? Or is the user suspended? We don't know!

Alternatively, you could use an unsigned integer to represent state:

```rust
struct User {
    // ...
    status: u8,
}
```

This is *slightly* better, because we can now use different values
to represent more states:

```rust
const ACTIVE: u8 = 0;
const INACTIVE: u8 = 1;
const SUSPENDED: u8 = 2;
const DELETED: u8 = 3;

let user = User {
    // ...
    status: ACTIVE,
};
```

A common use-case for `u8` is when you interface with C code.
In that case, using `u8` might seemingly be the only option.
However, we could still wrap that `u8` in a
[newtype](https://doc.rust-lang.org/rust-by-example/generics/new_types.html)!

```rust
struct User {
    // ...
    status: UserStatus,
}

struct UserStatus(u8);

const ACTIVE: UserStatus = UserStatus(0);
const INACTIVE: UserStatus = UserStatus(1);
const SUSPENDED: UserStatus = UserStatus(2);
const DELETED: UserStatus = UserStatus(3);

let user = User {
    // ...
    status: ACTIVE,
};
```

This way, we can still use `u8` to represent state, but we can
now also put the type system to work (a common pattern in idiomatic Rust). For
example, we can define methods on `UserStatus`:

```rust
impl UserStatus {
    fn is_active(&self) -> bool {
        self.0 == ACTIVE.0
    }
}
```

And we can even define a constructor that validates the input:

```rust
impl UserStatus {
    fn new(status: u8) -> Result<Self, &'static str> {
        match status {
            ACTIVE.0 => Ok(ACTIVE),
            INACTIVE.0 => Ok(INACTIVE),
            SUSPENDED.0 => Ok(SUSPENDED),
            DELETED.0 => Ok(DELETED),
            _ => Err("Invalid status"),
        }
    }
}
```

It's still not ideal, however! Not even if you interface with C code, as we will
see in a bit. But first, let's look at a common way to represent state in Rust.

## Use Enums Instead!

**Enums are a great way to model state inside your domain.** They allow you to
express your intent in a very concise way. 

```rust
#[derive(Debug)]
pub enum UserStatus {
    /// The user is active and has full access
    /// to their account and any associated features.
    Active,
    
    /// The user's account is inactive.
    /// This state can be reverted to active by
    /// the user or an administrator.
    Inactive,
    
    /// The user's account has been temporarily suspended, 
    /// possibly due to suspicious activity or policy violations.
    /// During this state, the user cannot access their account,
    /// and an administrator's intervention might
    /// be required to restore the account.
    Suspended,
    
    /// The user's account has been permanently 
    /// deleted and cannot be restored.
    /// All associated data with the account might be 
    /// removed, and the user would need to create a new account
    /// to use the service again.
    Deleted,
}
```

We can plug this enum into our `User` struct:

```rust
struct User {
    // ...
    status: UserStatus,
}
```

But that's not all; in Rust, enums are much more powerful than in many other
languages. For example, we can add data to our enum variants:

```rust
#[derive(Debug)]
pub enum UserStatus {
    Active,
    Inactive,
    Suspended { until: DateTime<Utc> },
    Deleted { deleted_at: DateTime<Utc> },
}
```

We can then model our **state transitions**:

```rust
use chrono::{DateTime, Utc};

#[derive(Debug)]
pub enum UserStatus {
    Active,
    Inactive,
    Suspended { until: DateTime<Utc> },
    Deleted { deleted_at: DateTime<Utc> },
}

impl UserStatus {
    /// Suspend the user until the given date.
    fn suspend(&mut self, until: DateTime<Utc>) {
        match self {
            UserStatus::Active => *self = UserStatus::Suspended { until },
            // For all non-active states, do nothing.
            _ => {}
        }
    }

    /// Activate the user.
    fn activate(&mut self) -> Result<(), &'static str> {
        match self {
            // A deleted user can't be activated!
            UserStatus::Deleted { .. } => return Err("can't activate a deleted user"),
            _ => *self = UserStatus::Active
        }
        Ok(())
    }

    /// Delete the user. This is a permanent action!
    fn delete(&mut self) {
        if let UserStatus::Deleted { .. } = self {
            // Already deleted. Don't set the deleted_at field again.
            return;
        }
        *self = UserStatus::Deleted {
            deleted_at: Utc::now(),
        }
    }

    fn is_active(&self) -> bool {
        matches!(self, UserStatus::Active)
    }

    fn is_suspended(&self) -> bool {
        matches!(self, UserStatus::Suspended { .. })
    }

    fn is_deleted(&self) -> bool {
        matches!(self, UserStatus::Deleted { .. })
    }
}

#[cfg(test)]
mod tests {
    use chrono::Duration;
    use super::*;

    #[test]
    fn test_user_status() -> Result<(), &'static str>{
        let mut status = UserStatus::Active;
        assert!(status.is_active());
        // Suspend until tomorrow
        status.suspend(Utc::now() + Duration::days(1));
        assert!(status.is_suspended());
        status.activate()?;
        assert!(status.is_active());
        status.delete();
        assert!(status.is_deleted());
        Ok(())
    }

    #[test]
    fn test_user_status_transition() {
        let mut status = UserStatus::Active;
        assert!(status.is_active());
        status.delete();
        assert!(status.is_deleted());
        // Can't activate a deleted user
        assert!(status.activate().is_err());
    }
}
```

We can extend the application with confidence, knowing that
we can't attempt to delete a user twice (which might have unwanted side effects
like, say, triggering an expensive cleanup job twice) or re-activate a deleted user.

Out of the box, enums don't prevent us from making invalid state transitions. We
can still write code that transitions from `Active` to `Suspended` without
checking if the user is already suspended. A simple fix is to return a `Result` from the transition methods (as we did above) to indicate if the transition was successful. This way, we can handle errors gracefully at compile-time without too much ceremony.
It's a simple and effective way towards avoiding [illegal state](/blog/illegal-state).

Another often mentioned drawback is that you need pattern matching to handle state transitions.

For example, we wrote this code to suspend a user:

```rust
match self {
    UserStatus::Active => *self = UserStatus::Suspended { until },
    // For all non-active states, do nothing.
    _ => {}
}
```

This can become a bit verbose, especially if you have many state transitions.
In practice, I rarely found this to be a problem, though.
Pattern matching is very ergonomic in Rust, and it's often the most readable way to describe state transitions. On top of that, the compiler will error if you forget to handle a state transition, which is a strong safety net. 

Enums offer another key benefit: efficiency. The compiler optimizes them well, often matching the performance of direct integer use. This makes enums ideal for state machines and performance-critical code.
In our example, the UserStatus enum's size equals that of its largest variant (plus a small tag) [^1]

[^1]: In our case, this means that the `UserStatus` enum is as large as a `DateTime<Utc>`.

Overall, while not perfect, the simplicity, readability, and memory efficiency of enums often outweigh their drawback in practice.

## Using Enums to Interact with C Code

Actually, there's one more advantage! Earlier, I promised that you can still use enums, even if you have to interact with C code.

Suppose you have a C library with a user status type (I've omitted the other
fields for brevity).

```c
typedef struct {
    uint8_t status;
} User;

User *create_user(uint8_t status);
```

You can write a Rust enum to represent the status:

```rust
#[repr(u8)]
#[derive(Debug, PartialEq)]
pub enum UserStatus {
    Active = 0,
    Inactive,
    Suspended,
    Deleted,
}

impl TryFrom<u8> for UserStatus {
    type Error = ();

    fn try_from(value: u8) -> Result<Self, Self::Error> {
        match value {
            0 => Ok(UserStatus::Active),
            1 => Ok(UserStatus::Inactive),
            2 => Ok(UserStatus::Suspended),
            3 => Ok(UserStatus::Deleted),
            _ => Err(()),
        }
    }
}
```

Noticed that `#[repr(u8)]` attribute? It tells the compiler to represent this
enum as an unsigned 8-bit integer. This is crucial for compatibility with C
code.

Now, let's wrap that C function in a safe Rust wrapper:

```rust
extern "C" {
    fn create_user(status: u8) -> *mut User;
}

pub fn create_user_wrapper(status: UserStatus) -> Result<User, &'static str> {
    let user = unsafe { create_user(status as u8) };
    if user.is_null() {
        Err("Failed to create user")
    } else {
        Ok(unsafe { *Box::from_raw(user) })
    }
}
```

The Rust code now communicates with the C code using a rich enum type, which is both expressive and type-safe.

If you want, you can play around with the code on the [Rust
playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=8973e5e655c92c725f0b2b00f7830385).

To make these conversions easier, there are crates like
[`num_enum`](https://crates.io/crates/num_enum), which provides great ergonomics
to convert enums to and from primitive types.

```rs
use num_enum::IntoPrimitive;

#[derive(IntoPrimitive)]
#[repr(u8)]
enum Number {
    Zero,
    One,
}

fn main() {
    let zero: u8 = Number::Zero.into();
    assert_eq!(zero, 0u8);
}
```

Here, the `IntoPrimitive` derive macro generates a `From` implementation for
`Number` to `u8`. This makes converting between the enum and the primitive type
as simple as calling `into()`.

## The Typestate Pattern

At this point, many experienced Rust developers would mention another way to safely handle state transitions: the typestate pattern. The idea is pretty neat &ndash; encode the state of an object in its type as a generic parameter.
The current state becomes *part* of your type.

```rust
/// Our trait for user states
trait UserState {}

/// Each state is a separate struct
struct Active;
struct Inactive;
struct Suspended;
struct Deleted;

/// Implement the trait for each state
impl UserState for Active {}
impl UserState for Inactive {}
impl UserState for Suspended {}
impl UserState for Deleted {}

/// The User struct is generic over the state
struct User<S: UserState> {
    // Generic over the state
    id: u64,
    name: String,
    
    // The state is encoded in the type
    state: S,
}

/// Implement methods for each state separately
/// Note how the return type changes based on the state.
/// That's the trick!
impl User<Active> {
    fn suspend(self, until: DateTime<Utc>) -> User<Suspended> {
        User { id: self.id, name: self.name, state: Suspended }
    }

    fn deactivate(self) -> User<Inactive> {
        User { id: self.id, name: self.name, state: Inactive }
    }
}

impl User<Inactive> {
    fn activate(self) -> User<Active> {
        User { id: self.id, name: self.name, state: Active }
    }
}

impl User<Suspended> {
    fn activate(self) -> User<Active> {
        User { id: self.id, name: self.name, state: Active }
    }
}

/// Deleted users can't be reactivated or suspended
/// Once we reach this state, the user is gone for good.
impl<S: UserState> User<S> {
    fn delete(self) -> User<Deleted> {
        User { id: self.id, name: self.name, state: Deleted }
    }
}
```

This pattern provides even stronger guarantees than enums, as it makes illegal state transitions impossible at compile-time. For instance, you can't deactivate a suspended user or reactivate a deleted user even if you wanted to:
there simply isn't a method for that.

```rust
fn main() {
    let user = User { id: 1, name: "Alice".to_string(), state: Active };
    let user = user.suspend(Utc::now() + Duration::days(1));
    
    // Error: no method named `deactivate` found for type `User<Suspended>`
    user.deactivate(); 
}
```

(You can play around with this code on the [Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=ded18a44c5f32d488eb5ea387ddd1eb8))

However, it's worth noting that there's some pushback against overusing the typestate pattern.

* The additional generic parameter can make the code more complex and harder to understand, especially for developers who aren't familiar with the pattern.
* The documentation and error messages can also be less clear, as the compiler will often mention the generic type parameter and that can distract from the main logic. 
* When you need to work with collections of items that could be in different states, the typestate pattern could be harder to work with.

The last point is often overlooked, so let's dive into it a bit more.
Say you have a list of users, each in a different state, then you'd need to use a trait object to store them:

```rust
let users: Vec<Box<dyn UserState>> = vec![
    Box::new(User { id: 1, name: "Alice".to_string(), state: Active }),
    Box::new(User { id: 2, name: "Bob".to_string(), state: Inactive }),
    Box::new(User { id: 3, name: "Charlie".to_string(), state: Suspended }),
];
```

This triggers a heap allocation and dynamic dispatch (the correct method to call is determined at runtime), which is less efficient than the same code using enums, but more importantly, by using trait objects, you're losing the ability to statically know which specific state each user is in. This means you can't directly call state-specific methods on the users in the collection without first downcasting again or by using dynamic dispatch. 

It can be tempting to verify everything at compile-time, but sometimes the trade-offs aren't worth it.
I'd recommend using the typestate pattern only when you need the strongest possible compile-time guarantees at the cost of worse developer experience.
For simpler scenarios, enums get you 80% of the way at very little cost.

## Conclusion

State management in Rust is more nuanced than in most other languages.

Here's a quick summary of the different state management approaches in Rust:

1. **Simple bool/integer**: Easy to understand but prone to errors and not self-documenting.
2. **Enums**: Provide type-safety and self-documentation, suitable for most cases. They even work well with C code.
3. **Typestate Pattern**: Offers the strongest compile-time guarantees, ideal for critical systems but can be more verbose.

Remember, the goal is to write code that is not only correct but also maintainable and understandable by your team.

My recommendation is to use enums whenever you need to represent a set of possible values, like when representing the state of an object. For even stronger guarantees, consider the typestate pattern, especially in safety-critical applications.

