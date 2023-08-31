+++
title = "Making Illegal States Unrepresentable"
date = 2023-08-06
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = [ { link = "https://www.wezm.net", name = "Wesley Moore" }, { link = "https://github.com/nicokosi", name = "Nicolas Kosinski" }, { link = "https://mastodon.social/@TheAlgorythm@chaos.social", name = "zSchön" }, { link = "https://mastodon.social/@mo8it@fosstodon.org", name = "mo8it" },
{ link = "https://www.andreaskroepelin.de", name = "Andreas Kröpelin" } ]
+++

If you've worked with Rust for a while, you've probably heard the phrase "making
illegal states unrepresentable". It's a phrase that's often used when people
praise Rust's type system. But what exactly does it mean? And how can you apply
it to your own code?

## What is illegal state?

Imagine we're writing an application that manages a list of users. 

```rust
struct User {
    username: String,
    birthdate: chrono::NaiveDate,
}
```

Looks simple enough, but is it correct?

What happens if we create a user with an empty username?

```rust
let user = User {
    username: String::new(),
    birthdate: chrono::NaiveDate::from_ymd(1990, 1, 1),
};
```

Intuitively, we know that this is **not** what we want, but the compiler can't help us.
We did not give it enough information about usernames.
Already, with this simple example, we managed to introduce illegal state.

Now, how can we fix this?

## The Type System Is Your Friend

Consider the `String` type. It's a type that represents 
an arbitrary sequence of unicode characters. In our case, we need much stricter
constraints. For a start, we want to make sure that the username is *not
empty*.

Whenever you're uncertain how to model something in Rust,
start by defining your basic types &mdash; your domain.
That takes some practice, but your code will be much better for it.

In our case, we want to define a type that represents a username.

```rust
struct Username(String);

impl Username {
    fn new(username: String) -> Result<Self, &'static str> {
        if username.is_empty() {
            return Err("Username cannot be empty");
        }
        Ok(Self(username))
    }
}
```

Note how the constructor now returns a `Result`.   
Also note, that wrapping the `String` in a struct is a zero-cost abstraction.
The compiler will optimize it away, so there's no performance penalty!

We can now use this type in our `User` struct.

```rust
struct User {
    username: Username,
    birthdate: chrono::NaiveDate,
}
```

See how the compiler now guides us towards idiomatic Rust code?
It's subtle, but `username` is now of type `Username` instead of `String`.
This means we have much stronger guarantees around our own type as we can't accidentally create a user with an empty username.
The username has to be constructed before:

```rust
let username = Username::new("johndoe".to_string())?;
let birthdate = NaiveDate::from_ymd(1990, 1, 1);
let user = User { username, birthdate };
```

## Side Note: How do we get rid of <code>Name::new</code>?

You could implement `TryFrom`:

```rust
use std::convert::TryFrom;

impl<'a> TryFrom<&'a str> for Name {
    type Error = &'static str;

    fn try_from(value: &'a str) -> Result<Self, Self::Error> {
        Self::new(value.into())
    }
}

let user =  User {
    username: "johndoe123".try_into()?,
    birthdate: NaiveDate::from_ymd(1990, 1, 1),
};
```

## What About the Birthdate?

A new user that is 1000 years old is probably not a valid user.
Let's add some constraints.

```rust
use chrono::Datelike;

struct Birthdate(chrono::NaiveDate);

impl Birthdate {
    #[must_use]
    fn new(birthdate: chrono::NaiveDate) -> Result<Self, &'static str> {
        let today = chrono::Utc::today().naive_utc();
        if birthdate > today {
            return Err("Birthdate cannot be in the future")
        }

        // Note, this age calculation is not 100% accurate, but you get the
        // idea. Here's a more robust implementation:
        // https://gist.github.com/mre/ee7a59491e2aee46d767bd3b5372c5c2
        let age = today.year() - birthdate.year();
        if age < 12 {
            return Err("Not old enough to register")
        }
        if age >= 150 {
            return Err("How are you not dead yet?")
        }

        Ok(Self(birthdate))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Duration;

    #[test]
    fn test_birthdate() {
        let today = chrono::Utc::today().naive_utc();
        // Birthdate cannot be in the future
        assert!(Birthdate::new(today + Duration::days(1)).is_err());
        // Excuse me, how old are you?
        assert!(Birthdate::new(today - Duration::days(365 * 150)).is_err());
        // Not old enough
        assert!(Birthdate::new(today - Duration::days(365 * 11)).is_err());
        // Ok
        assert!(Birthdate::new(today - Duration::days(365 * 15)).is_ok());
    }
}
```

No mocking, no complicated setup, testing becomes a breeze.

Our `User` struct now looks like this:

```rust
struct User {
    username: Username,
    birthdate: Birthdate,
}
```

## Adding More Constraints

It might sound simple, trivial even, but this is a very powerful technique.
What's important is that you're handling errors at the lowest possible level. In
this case, when you create the `Username` object &mdash; and not when you insert it into your database for example.

This will make your code much more robust and easier to reason about, and it's
quick to add more constraints as you go along. For example, we might want to
make sure that the username is not shorter than 3 characters, not longer than
256 characters, and that it contains only alphanumeric characters or dashes and
underscores:

```rust
struct Username(String);

impl Username {
    /// Represents a user's login name.
    ///
    /// # Errors
    ///
    /// Returns an error if
    /// - the username is shorter than 3 characters
    /// - the username is longer than 256 characters
    /// - the username contains characters other than 
    ///   alphanumeric characters, dashes, or underscores
    ///
    /// # Examples
    ///
    /// ```rust
    /// # use yourcrate::username::Username;
    /// assert!(Username::new("1".into()).is_err());
    /// assert!(Username::new("".into()).is_err());
    /// assert!(Username::new("user_name-123".into()).is_ok());
    /// ```
    #[must_use]
    fn new(username: String) -> Result<Self, &'static str> {
        if username.len() < 3 {
            return Err("username must be at least 3 characters long");
        }
        if username.len() > 256 {
            return Err("username must not be longer than 256 characters");
        }
        if username.chars().any(|c| !c.is_alphanumeric() && c != '-' && c != '_') {
            return Err("username must only contain alphanumeric characters, dashes, and underscores");
        }
        Ok(Self(username))
    }
}
```

I've added some documentation and examples, which will be shown in the
documentation of the `Username` struct. This is a great way to document your
constraints and to show how to use your types! As an added bonus, you can run
these examples as tests by using `cargo test --doc`.

## Does This Really Prevent Illegal States?

The keen reader might have noticed that we could still create invalid objects
manually:

```rust
let username = Username("".to_string()); // uh oh
```

In any real-world scenario, we would probably encapsulate our logic in a module and only expose a constructor function to the outside world:

```rust
mod user {
    pub struct Username(String);

    impl Username {
        #[must_use]
        pub fn new(username: String) -> Result<Self, &'static str> {
            // ...
        }
    }
}
```

If we now tried to create a `Username` object from the outside, we'd get a compiler error:

```rust
let username = user::Username("".to_string());

error[E0603]: tuple struct constructor `Username` is private
  --> src/main.rs:45:26
   |
2  |     pub struct Username(String);
   |                         ------ a constructor is private if any of the fields is private
```

With that, the only way to create a `Username` object is by using our `new` function:

```rust
let username = user::Username::new("mre".to_string());
```

**This means, illegal states are avoided for users of our module.  
In a way, we only made them "unconstructable", though.**

If we really wanted, we could model our struct to avoid illegal states at compile time, but it would be rather tedious to work with.

```rust
struct Username {
    // At least 3 characters required
    prefix: [char; 3]
    rest: String
}
```

We get the benefit of compile-time safety, but at the cost of ergonomics.
However, this pattern can be useful in some cases, as we will see in a 
[future article](/blog/compile-time-invariants/).

## Library Support

I personally prefer to write my own validation functions as shown above
but, you might want to consider using a validation library like
[validator](https://crates.io/crates/validator).

## Conclusion

If possible, use self-contained, custom types to model your domain.
It will make your code more robust, easier to test and reason about.
Happy coding!