+++
title = "Using Enums to Represent State"
template = "article.html"
date = 2023-08-08
[extra]
series = "Idiomatic Rust"
reviews = [ { link = "https://mastodon.social/@the@mkl.lol", name = "Maikel" } ]
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

Alternatively, you could use a `u8` to represent state:

```rust
struct User {
    // ...
    status: u8,
}
```

This is slightly better, because we can now use different values
to represent different states:

```rust
struct User {
    // ...
    status: u8,
}

const ACTIVE: u8 = 0;
const INACTIVE: u8 = 1;
const SUSPENDED: u8 = 2;
const DELETED: u8 = 3;

let user = User {
    // ...
    status: ACTIVE,
};
```

You might write bindings to existing C code, which uses `u8` to
represent state. In that case, using `u8` might seemingly be the
only option. However, you can still wrap the `u8` in a newtype:

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
also use the type system to our advantage. For example, we can
now define methods on `UserStatus`:

```rust
impl UserStatus {
    fn is_active(&self) -> bool {
        self.0 == ACTIVE.0
    }
}
```

And we can also define a constructor that validates the input:

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

It's still not ideal, however. Not even if you interface with C code, as we will
see in a bit.

## Use Enums Instead!

**Enums are a great way to model state inside your domain.** They allow you to
express your intent in a very concise way. 

```rust
#[derive(Debug)]
pub enum UserStatus {
    /// The user is active and has full access
    // to their account and any associated features.
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

We can now use this enum in our `User` struct:

```rust
struct User {
    // ...
    status: UserStatus,
}
```

In Rust, enums are much more powerful than in many other languages!  
For example, we can add data to our enum variants:

```rust
#[derive(Debug)]
pub enum UserStatus {
    Active,
    Inactive,
    Suspended { until: DateTime<Utc> },
    Deleted { deleted_at: DateTime<Utc> },
}
```

We can even represent state transitions:

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

    /// Delete the user. This is a permanent action.
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

Earlier, I promised that you can still use enums to interact with C code.

Let's say we have a C library that exposes a function to
create a new user:

```c
typedef struct {
    char *name;
    char *email;
    uint8_t status;
} User;

User *create_user(char *name, char *email, uint8_t status);
```

We can write a Rust wrapper around this function:

```rust
use std::convert::{TryFrom, TryInto};
use std::ffi::c_char;
use std::ffi::CString;

// Our UserStatus enum definition, which will automatically
// be converted to a C enum variant.
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

// Our User struct, which will be converted to a C struct.
#[repr(C)]
pub struct User {
    name: *mut c_char,
    email: *mut c_char,
    status: UserStatus,
}

impl User {
    pub fn new(name: &str, email: &str, status: u8) -> Result<Self, &'static str> {
        let name = CString::new(name).map_err(|_| "Invalid name")?;
        let email = CString::new(email).map_err(|_| "Invalid email")?;
        let status = status.try_into().map_err(|_| "Invalid status")?;
        Ok(Self {
            name: name.into_raw(),
            email: email.into_raw(),
            status,
        })
    }
}

impl Drop for User {
    fn drop(&mut self) {
        // Convert the raw pointers back to CStrings (hence taking ownership)
        // and immediately drop them to free the memory.
        unsafe {
            drop(CString::from_raw(self.name));
            drop(CString::from_raw(self.email));
        }
    }
}

extern "C" {
    fn create_user(name: *const c_char, email: *const c_char, status: u8) -> *mut User;
}

// A safe wrapper around the C function.
pub fn create_user_wrapper(name: &str, email: &str, status: UserStatus) -> Result<User, &'static str> {
    let status = status as u8;
    let user = unsafe {
        create_user(
            CString::new(name).map_err(|_| "Invalid name")?.as_ptr(),
            CString::new(email).map_err(|_| "Invalid email")?.as_ptr(),
            status,
        )
    };
    if user.is_null() {
        Err("Failed to create user")
    } else {
        Ok(unsafe { *Box::from_raw(user) })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_user() {
        let user = create_user_wrapper("John Doe", "mail@example.com", UserStatus::Active).unwrap();
        // You can't directly compare `user.name` and `user.email` with strings here,
        // you would need to convert them from raw pointers back to Rust strings.
        assert_eq!(user.status, UserStatus::Active);
    }

    #[test]
    fn test_create_user_invalid_name() {
        assert!(create_user_wrapper("", "mail@example.com", UserStatus::Active).is_err());
    }
}

```

## Conclusion

Enums in Rust are more powerful than in most other languages.
They can be used to elegantly represent state transitions &mdash;
even across language boundaries.

You should consider using enums whenever you need to represent a set of possible
values, like when representing the state of an object.


