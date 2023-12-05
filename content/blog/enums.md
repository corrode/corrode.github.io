+++
title = "Using Enums to Represent State"
template = "article.html"
draft = false
date = 2023-08-08
[extra]
series = "Idiomatic Rust"
reviews = [ 
    { name = "Maikel", url = "https://mastodon.social/@the@mkl.lol" }
]
+++

Many Rust beginners with a background in systems programming tend to use `bool`
(or even `u8` &mdash; an 8-bit unsigned integer type) to represent *"state"*.

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
see in a bit. But first, let's look at the recommended way to represent state in Rust.

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

We can even represent **state transitions**:

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

Look how much ground we've covered with just a few lines of code!
We can extend the application with confidence, knowing that
we can't accidentally delete a user twice or re-activate a deleted user.
[Illegal state transitions are now impossible!](/blog/illegal-state)

## Using Enums to Interact with C Code

Earlier, I promised that you can still use enums, even if you have to interact
with C code.

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
enum as an unsigned 8-bit integer. This is critical for compatibility with the C
code.

Now, let's wrap the C function in a safe Rust wrapper:

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

The Rust code now communicates with the C code using a rich enum type, allowing
for more expressive and type-safe code.

If you want, you can play around with the code on the [Rust
playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=8973e5e655c92c725f0b2b00f7830385).

## Conclusion

Enums in Rust are more powerful than in most other languages.
They can be used to elegantly represent state transitions &mdash;
even across language boundaries.

You should consider using enums whenever you need to represent a set of possible
values, like when representing the state of an object.


