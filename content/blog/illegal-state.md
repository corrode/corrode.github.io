+++
title = "Making Illegal States Unrepresentable"
date = 2023-08-06
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

If you've worked with Rust for a while, you've probably heard the phrase "making
illegal states unrepresentable". It's a phrase that's often used when people
praise Rust's type system. But what exactly does it mean? And how can you apply
it to your own code?

## What is illegal state?

Imagine we're writing a application that manages a list of users. 

```rust
struct User {
    name: String,
    birthdate: chrono::NaiveDate,
}
```

Looks simple enough, but is it correct?

What happens if we create a user with an empty name?

```rust
let user = User {
    name: String::new(),
    birthdate: chrono::NaiveDate::from_ymd(1990, 1, 1),
};
```

Intuitively, we know that this is **not** what we want, but the compiler can't help us.
We did not give it enough information about user names.
Already, with this simple example, we managed to introduce illegal state.

Now, how can we fix this?

## The Type System Is Your Friend

Consider the `String` type. It's a type that represents 
an arbitrary sequence of unicode characters. In our case, we need much stricter
constraints. For a start, we want to make sure that the name is *not
empty*.

Whenever you're uncertain how to model something in Rust,
start by defining your basic types &mdash; your domain.
That takes some practice, but your code will be much better for it.

In our case, we want to define a type that represents a name.

```rust
struct Name(String);

impl Name {
    fn new(name: String) -> Result<Self, &'static str> {
        if name.is_empty() {
            Err("Name cannot be empty")
        } else {
            Ok(Self(name))
        }
    }
}
```

Note how the constructor returns a `Result`.   
We can now use this type in our `User` struct.

```rust
struct User {
    name: Name,
    birthdate: chrono::NaiveDate,
}

impl User {
    fn new(name: Name, birthdate: chrono::NaiveDate) -> Self {
        Self { name, birthdate }
    }
}
```

Note how the compiler now guides us towards idiomatic Rust code?
It's subtle, but `name` is now of type `Name` instead of `String`.
This means that we can't accidentally create a user with an empty name.
The name has to be constructed before:

```rust
let name = Name::new("John Doe".to_string())?;
let birthdate = NaiveDate::from_ymd(1990, 1, 1);
let user = User::new(name, birthdate);
```

## Side Note: How do we get rid of <code>to_string()</code>?

You could implement `TryFrom`:

```rust
use std::convert::TryFrom;

impl<'a> TryFrom<&'a str> for Name {
    type Error = &'static str;

    fn try_from(value: &'a str) -> Result<Self, Self::Error> {
        Self::new(value.into())
    }
}

let user = User::new("John Doe".try_into()?, birthdate);
```

## What About the Birthdate?

A new user that is 1000 years old is probably not a valid user.
Let's add some constraints.

```rust
struct Birthdate(chrono::NaiveDate);

impl Birthdate {
    #[must_use]
    fn new(birthdate: chrono::NaiveDate) -> Result<Self, &'static str> {
        let today = chrono::Utc::today().naive_utc();
        if birthdate > today {
            return Err("Birthdate cannot be in the future")
        }
        if today.year() - birthdate.year() > 150 {
            return Err("How are you not dead yet?")
        }
        if today.year() - birthdate.year() < 12 {
            return Err("Not old enough")
        }

        Ok(Self(birthdate))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_birthdate() {
        let today = chrono::Utc::today().naive_utc();
        assert!(Birthdate::new(today).is_ok());
        // Birthdate cannot be in the future
        assert!(Birthdate::new(today + Duration::days(1)).is_err());
        // Excuse me, how old are you?
        assert!(Birthdate::new(today - Duration::days(365 * 150)).is_err());
        // Not old enough
        assert!(Birthdate::new(today - Duration::days(365 * 12)).is_err());
    }
}
```

No mocking, no complicated setup, testing is a breeze.

Our `User` struct now looks like this:

```rust
struct User {
    name: Name,
    birthdate: Birthdate,
}
```

## Adding More Constraints

It might sound simple, trivial even, but this is a very powerful technique.
What's important is that you're handling errors at the lowest possible level. In
this case when you create the `Name` object &mdash; and not when you insert it
into your database for example.

This will make your code much more robust and easier to reason about and it's
quick to add more constraints as you go along. For example, we might want
to make sure that the name is not longer than 100 characters and that
it doesn't contain any special characters or numbers:

```rust
struct Name(String);

impl Name {
    /// Represents a user's name.
    ///
    /// # Errors
    ///
    /// Returns an error if
    /// - the name is empty
    /// - the name is longer than 100 characters
    /// - the name contains non-alphabetic characters
    ///
    /// # Examples
    ///
    /// ```rust
    /// # use yourcrate::name::Name;
    /// assert!(Name::new(String::new()).is_err());
    /// assert!(Name::new("123".into()).is_err());
    /// assert!(Name::new("".into()).is_err());
    /// assert!(Name::new("John Doe".into()).is_ok());
    /// ```
    #[must_use]
    fn new(name: String) -> Result<Self> {
        if name.is_empty() {
            return Err("name must not be empty");
        }
        if name.len() > 100 {
            return Err("name must not be longer than 100 characters");
        }
        if name.chars().any(|c| !c.is_alphabetic()) {
            return Err("name must only contain alphabetic characters");
        }
        Ok(Self(name))
    }
}
```

I've added some documentation and examples, which will be shown in the
documentation of the `Name` struct. This is a great way to document your
constraints and to show how to use your types! As an added bonus, you can run
these examples as tests by using `cargo test --doc`.


## Library Support

I personally prefer to write my own validation functions as shown above
but, you might want to consider using a validation library like
[validator](https://crates.io/crates/validator).

## Conclusion

This was just a small example to demonstrate what it means to make illegal
states unrepresentable. 

If possible, use self-contained, custom types to model your domain.
It will make your code more robust, easier to test and reason about.
Happy coding!