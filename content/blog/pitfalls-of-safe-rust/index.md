+++
title = "Pitfalls of Safe Rust"
date = 2025-04-01
updated = 2025-10-09
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = [ 
    { name = "Alex Burka (durka)", url = "https://github.com/durka" },
    { name = "Wesley Moore (wezm)", url = "https://www.wezm.net" },
    { name = "Mo Bitar  (mo8it)", url = "https://mastodon.social/@mo8it@fosstodon.org" },
]
resources = [
   "[The Four Horsemen of Bad Rust Code](https://github.com/corrode/four-horsemen-talk) -- My talk at FOSDEM 2024",
   "[High Assurance Rust](https://highassurance.rs/) -- developing secure and robust software with Rust"
]
+++

When people say Rust is a "safe language", they often mean memory safety.
And while memory safety is a great start, it's far from all it takes to build robust applications.

**Memory safety is necessary but not sufficient for overall reliability.**

In this article, I want to show you a few common gotchas in safe Rust that the compiler doesn't detect and how to avoid them.

## Why Rust Can't Always Help

Even in safe Rust code, you still need to handle various risks and edge cases.
You need to address aspects like input validation and making sure that your business logic is correct.

Here are just a few categories of bugs that Rust **doesn't** protect you from:

- Type casting mistakes (e.g. overflows)
- Logic bugs
- Panics because of using `unwrap` or `expect`
- Malicious or incorrect `build.rs` scripts in third-party crates
- Incorrect unsafe code in third-party libraries
- Race conditions

Let's look at ways to avoid some of the more common problems.
The tips are roughly ordered by how likely you are to encounter them.

## Table of Contents

<details class="toc">
<summary>
Click here to expand the table of contents.
</summary>

- [Protect Against Integer Overflow](#protect-against-integer-overflow)
- [Avoid `as` For Numeric Conversions](#avoid-as-for-numeric-conversions)
- [Use Bounded Types for Numeric Values](#use-bounded-types-for-numeric-values)
- [Don't Index Into Arrays Without Bounds Checking](#don-t-index-into-arrays-without-bounds-checking)
- [Use `split_at_checked` Instead Of `split_at`](#use-split-at-checked-instead-of-split-at)
- [Make Invalid States Unrepresentable](#make-invalid-states-unrepresentable)
- [Avoid Primitive Types For Business Logic](#avoid-primitive-types-for-business-logic)
- [Handle Default Values Carefully](#handle-default-values-carefully)
- [Implement `Debug` Safely](#implement-debug-safely)
- [Careful With Serialization](#careful-with-serialization)
- [Protect Against Time-of-Check to Time-of-Use (TOCTOU)](#protect-against-time-of-check-to-time-of-use-toctou)
- [Use Constant-Time Comparison for Sensitive Data](#use-constant-time-comparison-for-sensitive-data)
- [Don't Accept Unbounded Input](#don-t-accept-unbounded-input)
- [Surprising Behavior of `Path::join` With Absolute Paths](#surprising-behavior-of-path-join-with-absolute-paths)
- [Check For Unsafe Code In Your Dependencies With `cargo-geiger`](#check-for-unsafe-code-in-your-dependencies-with-cargo-geiger)
- [Conclusion](#conclusion)

</details>

## Protect Against Integer Overflow

Overflow errors can happen pretty easily:

```rust
// DON'T: Use unchecked arithmetic
fn calculate_total(price: u32, quantity: u32) -> u32 {
    price * quantity  // Could overflow!
}
```

If `price` and `quantity` are large enough, the result will overflow.
Rust will panic in debug mode, but in release mode, it will silently wrap around.

To avoid this, use checked arithmetic operations:

```rust
// DO: Use checked arithmetic operations
fn calculate_total(price: u32, quantity: u32) -> Result<u32, ArithmeticError> {
    price.checked_mul(quantity)
        .ok_or(ArithmeticError::Overflow)
}
```

Static checks are not removed since they don't affect the performance of generated code.
So if the compiler is able to detect the problem at compile time, it will do so:

```rust
fn main() {
    let x: u8 = 2;
    let y: u8 = 128;
    let z = x * y;  // Compile-time error!
}
```

The error message will be:

```rust
error: this arithmetic operation will overflow
 --> src/main.rs:4:13
  |
4 |     let z = x * y;  // Compile-time error!
  |             ^^^^^ attempt to compute `2_u8 * 128_u8`, which would overflow
  |
  = note: `#[deny(arithmetic_overflow)]` on by default
```

For all other cases, use [`checked_add`](https://docs.rs/num/latest/num/trait.CheckedAdd.html), [`checked_sub`](https://docs.rs/num/latest/num/trait.CheckedSub.html), [`checked_mul`](https://docs.rs/num/latest/num/trait.CheckedMul.html), and [`checked_div`](https://docs.rs/num/latest/num/trait.CheckedDiv.html), which return `None` instead of wrapping around on underflow or overflow. [^intrinsics_docs]

[^intrinsics_docs]: There's also methods for wrapping and saturating arithmetic, which might be useful in some cases.
It's worth it to check out the [`std::intrinsics`](https://doc.rust-lang.org/std/intrinsics/index.html) documentation to learn more.

{% info(title="Quick Tip: Enable Overflow Checks In Release Mode", icon="info") %}

Rust carefully balances performance and safety.
In scenarios where a performance hit is acceptable, memory safety takes precedence. [^memory_safety]

[^memory_safety]: One example where Rust accepts a performance cost for safety would be checked array indexing, which prevents buffer overflows at runtime. Another is when the Rust maintainers [fixed float casting](https://internals.rust-lang.org/t/help-us-benchmark-saturating-float-casts/6231) because the previous implementation could cause undefined behavior when casting certain floating point values to integers.

Integer overflows can lead to unexpected results, but they are not inherently unsafe.
On top of that, overflow checks can be expensive, which is why Rust disables them in release mode. [^overflow]

[^overflow]: According to some benchmarks, overflow checks cost a few percent of performance on typical integer-heavy workloads. See Dan Luu's analysis [here](https://danluu.com/integer-overflow/)

However, you can re-enable them in case your application can trade the last 1%
of performance for better overflow detection.

Put this into your `Cargo.toml`:

```toml
[profile.release]
overflow-checks = true # Enable integer overflow checks in release mode
```

This will enable overflow checks in release mode. As a consequence, 
the code will panic if an overflow occurs.

See [the docs](https://doc.rust-lang.org/cargo/reference/profiles.html#release)
for more details.

{% end %}


## Avoid `as` For Numeric Conversions

While we're on the topic of integer arithmetic, let's talk about type conversions.
Casting values with `as` is convenient but risky unless you know exactly what you are doing.

```rust
let x: i32 = 42;
let y: i8 = x as i8;  // Can overflow!
```

There are three main ways to convert between numeric types in Rust:

1. ⚠️ Using the `as` keyword: This approach works for both lossless and lossy conversions. In cases where data loss might occur (like converting from `i64` to `i32`), **it will simply truncate the value**. 

2. Using [`From::from()`](https://doc.rust-lang.org/std/convert/trait.From.html): This method only allows **lossless conversions**. For example, you can convert from `i32` to `i64` since all 32-bit integers can fit within 64 bits. However, you cannot convert from `i64` to `i32` using this method since it could potentially lose data.

3. Using [`TryFrom`](https://doc.rust-lang.org/std/convert/trait.TryFrom.html): This method is similar to `From::from()` but returns a `Result` instead of panicking. This is useful when you want to handle potential data loss gracefully.


{% info(title="Quick Tip: Safe Numeric Conversions", icon="info") %}

**If in doubt, prefer `From::from()` and `TryFrom` over `as`.**

1. use `From::from()` when you can guarantee no data loss.
2. use `TryFrom` when you need to handle potential data loss gracefully.
3. only use `as` when you're comfortable with potential truncation or know the values will fit within the target type's range and when performance is absolutely critical.

(*Adapted from [StackOverflow answer by delnan](https://stackoverflow.com/a/28280042/270334) and [additional context](https://stackoverflow.com/a/48795524/270334).*)

{% end %}

The `as` operator is **not safe for narrowing conversions**.
It will silently truncate the value, leading to unexpected results.

What is a "narrowing conversion"?
It's when you convert a larger type to a smaller type, e.g. `i32` to `i8`.

For example, see how `as` chops off the high bits from our value:

```rust
fn main() {
    let a: u16 = 0x1234;
    let b: u8 = a as u8;
    println!("0x{:04x}, 0x{:02x}", a, b); // 0x1234, 0x34
}
```

So, coming back to our first example above, instead of writing

```rust
let x: i32 = 42;
let y: i8 = x as i8;  // Can overflow!
```

use `TryFrom` instead and handle the error gracefully:

```rust
let y = i8::try_from(x).ok_or("Number is too big to be used here")?;
```

## Use Bounded Types for Numeric Values

Bounded types make it easier to express invariants and avoid invalid states.
E.g. if you have a numeric type and 0 is *never* a correct value, use [`std::num::NonZeroUsize`](https://doc.rust-lang.org/std/num/type.NonZeroUsize.html) instead.

You can also create your own bounded types:

```rust
// DON'T: Use raw numeric types for domain values
struct Measurement {
    distance: f64,  // Could be negative!
}

// DO: Create bounded types
#[derive(Debug, Clone, Copy)]
struct Distance(f64);

impl Distance {
    pub fn new(value: f64) -> Result<Self, DistanceError> {
        if value < 0.0 || !value.is_finite() {
            return Err(DistanceError::Invalid);
        }
        Ok(Distance(value))
    }
}

struct Measurement {
    distance: Distance,
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=a9157c58ada88e85b82d835a5eceac66))

## Don't Index Into Arrays Without Bounds Checking

Whenever I see the following, I get goosebumps 😨:

```rust
let arr = [1, 2, 3];
let elem = arr[3];  // uh-oh!
```

That's a common source of bugs.
Unlike C, Rust *does* check array bounds and prevents a security vulnerability,
but **it still panics at runtime**.

Instead, use the `get` method:

```rust
let elem = arr.get(3);
```

It returns an `Option` which you can now handle gracefully.
See [this blog post](https://shnatsel.medium.com/how-to-avoid-bounds-checks-in-rust-without-unsafe-f65e618b4c1e) for more info on the topic.

## Use `split_at_checked` Instead Of `split_at`

This issue is related to the previous one. 
Say you have a slice and you want to split it at a certain index.

```rust
let mid = 4;
let arr = [1, 2, 3];
let (left, right) = arr.split_at(mid);
```

You might expect that this returns a tuple of slices where the first slice contains all elements
and the second slice is empty.

⚠️ **Instead, the above code will panic because the mid index is out of bounds!**

To handle that more gracefully, use `split_at_checked` instead:

```rust
let arr = [1, 2, 3];
// This returns an Option
match arr.split_at_checked(mid) {
    Some((left, right)) => {
        // Do something with left and right
    }
    None => {
        // Handle the error
    }
}
```

This returns an `Option` which allows you to handle the error case.
([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=8208b1a16e73e63d37799fed27cd1e49))

More info about `split_at_checked` [here](https://doc.rust-lang.org/std/primitive.slice.html#method.split_at_checked).

## Avoid Primitive Types For Business Logic

It's very tempting to use primitive types for everything.
Especially Rust beginners fall into this trap.

```rust
// DON'T: Use primitive types for usernames
fn authenticate_user(username: String) {
    // Raw String could be anything - empty, too long, or contain invalid characters
}
```

However, do you really accept *any* string as a valid username?
What if it's empty? What if it contains emojis or special characters?
That would likely be unexpected.

Instead, you can create a custom type for your domain:

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct Username(String);

impl Username {
    pub fn new(name: &str) -> Result<Self, UsernameError> {
        // Check for empty username
        if name.is_empty() {
            return Err(UsernameError::Empty);
        }

        // Check length (for example, max 30 characters)
        if name.len() > 30 {
            return Err(UsernameError::TooLong);
        }

        // Only allow alphanumeric characters and underscores
        if !name.chars().all(|c| c.is_alphanumeric() || c == '_') {
            return Err(UsernameError::InvalidCharacters);
        }

        Ok(Username(name.to_string()))
    }

    /// Allow to get a reference to the inner string
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

fn authenticate_user(username: Username) {
    // We know this is always a valid username!
    // No empty strings, no emojis, no spaces, etc.
}
```

([Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=fe47108e246366718d7759eb7abf02f3))

## Make Invalid States Unrepresentable

Can you spot the bug in the following code?

```rust
// DON'T: Allow invalid combinations
struct Configuration {
    port: u16,
    host: String,
    ssl: bool,
    ssl_cert: Option<String>, 
}
```

The problem is that you can have `ssl` set to `true` but `ssl_cert` set to `None`.
That's an invalid state! If you try to use the SSL connection, you can't because there's no certificate.

This issue can be detected at compile-time by using types to enforce valid states.
First, let's define the possible states for the connection:

```rust
enum ConnectionSecurity {
    Insecure,
    // We can't have an SSL connection
    // without a certificate!
    Ssl { cert_path: String },
}
```

Now we can't have an invalid state!
Either we have an SSL connection with a certificate or we don't have SSL at all.

```rust
struct Configuration {
    port: u16,
    host: String,
    security: ConnectionSecurity, // All possible states are valid! 
}
```

In comparison to the previous section, the bug was caused by an *invalid combination of closely related fields*.
To prevent that, clearly map out all possible states and transitions between them.
A simple way is to define an enum with optional metadata for each state.

The learning here is that Rust can't protect you from logic bugs.
If you're curious to learn more, here is a more in-depth [blog post on the topic](/blog/illegal-state/).

## Handle Default Values Carefully

It's quite common to add a blanket `Default` implementation to your types without thinking twice about it.
But that can lead to unforeseen issues.

For example, here's a case where the port is set to 0 by default, which is not a valid port number.[^port]

[^port]: Port 0 usually means that the OS will assign a random port for you.
So, `TcpListener::bind("127.0.0.1:0").unwrap()` is valid, but it might not be supported on all operating systems or it might not be what you expect. See the [`TcpListener::bind`](https://doc.rust-lang.org/std/net/struct.TcpListener.html#method.bind) docs for more info.

```rust
// DON'T: Implement `Default` without consideration
#[derive(Default)]  // Might create invalid states!
struct ServerConfig {
    port: u16,      // Will be 0, which might be unexpected 
    max_connections: usize,
    timeout_seconds: u64,
}
```

Instead, consider if a default value makes sense for your type.
If there is no sane default, don't implement `Default` at all and let the user be explicit.

```rust
// DO: Make Default meaningful or don't implement it
struct ServerConfig {
    port: Port,
    max_connections: NonZeroUsize,
    timeout_seconds: Duration,
}

impl ServerConfig {
    pub fn new(port: Port) -> Self {
        Self {
            port,
            max_connections: NonZeroUsize::new(100).unwrap(),
            timeout_seconds: Duration::from_secs(30),
        }
    }
}
```

## Implement `Debug` Safely

A related issue is the `Debug` trait.
One might assume that `Debug` is only used for "debugging purposes" and is therefore harmless, but if you blindly derive `Debug` for all types, you might expose sensitive data.
That's because `Debug` is often used in logging and error messages, even in production code.
Instead, implement `Debug` manually for types that contain sensitive information.

```rust
// This would expose sensitive data in logs!
#[derive(Debug)]
struct User {
    username: String,
    password: String,  // Will be printed as plain text!
}
```

Instead, you could write:

```rust
#[derive(Debug)]
struct User {
    username: String,
    password: Password,
}

struct Password(String);

// Here we implement Debug manually to redact the password
impl std::fmt::Debug for Password {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("[REDACTED]")
    }
}
```

Let's say we were to print a `User` instance:

```rust
let user = User {
    username: String::from("ferris"),
    password: Password(String::from("supersecret")),
};
println!("{user:#?}");
```

The output would be:

```rust
User {
    username: "ferris",
    password: [REDACTED],
}
```

([Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=8fd18d9e13f60193bc14e97ea258707e))

For production code, use a crate like [`secrecy`](https://crates.io/crates/secrecy). 

However, it's not black and white either:
If you implement `Debug` manually, you might forget to update the implementation when your struct changes.
A common pattern is to destructure the struct in the `Debug` implementation to catch such errors.

Instead of this:

```rust
// don't
impl std::fmt::Debug for DatabaseURI {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}://{}:[REDACTED]@{}/{}", self.scheme, self.user, self.host, self.database)
    }
}
```

How about destructuring the struct to catch changes?

```rust
// do
impl std::fmt::Debug for DatabaseURI {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
       // Destructure the struct to catch changes
       // This way, the compiler will warn you if you add a new field
       // and forget to update the Debug implementation
        let DatabaseURI { scheme, user, password: _, host, database, } = self;
        write!(f, "{scheme}://{user}:[REDACTED]@{host}/{database}")?;
        // -- or --
        // f.debug_struct("DatabaseURI")
        //     .field("scheme", scheme)
        //     .field("user", user)
        //     .field("password", &"***")
        //     .field("host", host)
        //     .field("database", database)
        //     .finish()

        Ok(())
    }
}
```

([Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=a2facbaa5290f9518072ac214df370aa))

Thanks to [Wesley Moore (wezm)](https://www.wezm.net) for the hint and to [Simon Brüggen (m3t0r)](https://github.com/M3t0r) for the example.

## Careful With Serialization 

Don't blindly derive `Serialize` and `Deserialize` either, especially for sensitive data. 
The values you read/write might not be what you expect!

```rust
#[derive(Serialize, Deserialize)]
struct UserCredentials {
    #[serde(default)]  // ⚠️ Accepts empty strings when deserializing!
    username: String,
    #[serde(default)]
    password: String, // ⚠️ Leaks the password when serialized!
}
```

When deserializing, the fields might be empty.
Empty credentials could potentially pass validation checks if not properly handled.

On top of that, the serialization behavior could also leak sensitive data.
By default, `Serialize` will include the password field in the serialized output, which could expose sensitive credentials in logs, API responses, or debug output.

A common fix is to implement your own custom serialization and deserialization methods by using `impl<'de> Deserialize<'de> for UserCredentials`.

The advantage is that you have full control over input validation.
However, the disadvantage is that you need to implement all the logic yourself.

An alternative strategy is to use the `#[serde(try_from = "FromType")]` attribute.

Let's take the `Password` field as an example.
Start by using the newtype pattern to wrap the standard types and add custom validation:

```rust
#[derive(Deserialize)]
// Tell serde to call `Password::try_from` with a `String`
#[serde(try_from = "String")]
pub struct Password(String);
```

Now implement `TryFrom` for `Password`:

```rust
impl TryFrom<String> for Password {
    type Error = PasswordError;

    /// Create a new password
    ///
    /// Throws an error if the password is too short.
    /// You can add more checks here.
    fn try_from(value: String) -> Result<Self, Self::Error> {
        // Validate the password
        if value.len() < 8 {
            return Err(PasswordError::TooShort);
        }
        Ok(Password(value))
    }
}
```

With this trick, you can no longer deserialize invalid passwords:

```rust
// Panic: password too short!
let password: Password = serde_json::from_str(r#""pass""#).unwrap();
```

(Try it on the [Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=ba0f1a45d5ac982b00a5b5f68a1a0d9e))

Credits go to [EqualMa's article on dev.to](https://dev.to/equalma/validate-fields-and-types-in-serde-with-tryfrom-c2n) and to [Alex Burka (durka)](https://github.com/durka) for the hint.


## Protect Against Time-of-Check to Time-of-Use (TOCTOU)

This is a more advanced topic, but it's important to be aware of it.
TOCTOU (time-of-check to time-of-use) is a class of software bugs caused by changes that happen between when you check a condition and when you use a resource.

```rust
// DON'T: Vulnerable approach with separate check and use
fn remove_dir(path: &Path) -> io::Result<()> {
    // First check if it's a directory
    if !path.is_dir() {
        return Err(io::Error::new(
            io::ErrorKind::NotADirectory,
            "not a directory"
        ));
    }
    
    // TOCTOU vulnerability: Between the check above and the use below,
    // the path could be replaced with a symlink to a directory we shouldn't access!
    remove_dir_impl(path)
}
```

([Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=fb208eb58e49ce70bde77a48b9b102d1))

The safer approach opens the directory first, ensuring we operate on what we checked:

```rust
// DO: Safer approach that opens first, then checks
fn remove_dir(path: &Path) -> io::Result<()> {
    // Open the directory WITHOUT following symlinks
    let handle = OpenOptions::new()
        .read(true)
        // Fails if not a directory or is a symlink
        .custom_flags(O_NOFOLLOW | O_DIRECTORY) 
        .open(path)?;
    
    // We can now safely remove the directory contents using the open handle
    remove_dir_impl(&handle)
}
```

([Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=08a3a0a030a1878171e7eb76adb6ffb8))

Here's why it's safer:
while we hold the handle, the directory can't be replaced with a symlink.
This way, the directory we're working with is the same as the one we checked.
Any attempt to replace it won't affect us because the handle is already open.

You'd be forgiven if you overlooked this issue before.
In fact, even the Rust core team missed it in the standard library.
What you saw is a simplified version of an actual bug in the [`std::fs::remove_dir_all`](https://doc.rust-lang.org/std/fs/fn.remove_dir_all.html) function.
Read more about it in [this blog post about CVE-2022-21658](https://blog.rust-lang.org/2022/01/20/cve-2022-21658.html).

## Use Constant-Time Comparison for Sensitive Data

Timing attacks are a nifty way to extract information from your application.
The idea is that the time it takes to compare two values can leak information about them.
For example, the time it takes to compare two strings can reveal how many characters are correct.
Therefore, for production code, be careful with regular equality checks when handling sensitive data like passwords.

```rust
// DON'T: Use regular equality for sensitive comparisons
fn verify_password(stored: &[u8], provided: &[u8]) -> bool {
    stored == provided  // Vulnerable to timing attacks!
}

// DO: Use constant-time comparison
use subtle::{ConstantTimeEq, Choice};

fn verify_password(stored: &[u8], provided: &[u8]) -> bool {
    stored.ct_eq(provided).unwrap_u8() == 1
}
```

## Don't Accept Unbounded Input

Protect Against Denial-of-Service Attacks with Resource Limits.
These happen when you accept unbounded input, e.g. a huge request body
which might not fit into memory.

```rust
// DON'T: Accept unbounded input
fn process_request(data: &[u8]) -> Result<(), Error> {
    let decoded = decode_data(data)?;  // Could be enormous!
    // Process decoded data
    Ok(())
}
```

Instead, set explicit limits for your accepted payloads:

```rust
const MAX_REQUEST_SIZE: usize = 1024 * 1024;  // 1MiB

fn process_request(data: &[u8]) -> Result<(), Error> {
    if data.len() > MAX_REQUEST_SIZE {
        return Err(Error::RequestTooLarge);
    }
    
    let decoded = decode_data(data)?;
    // Process decoded data
    Ok(())
}
```

## Surprising Behavior of `Path::join` With Absolute Paths 

If you use `Path::join` to join a relative path with an absolute path, it will silently replace the relative path with the absolute path.

```rust
use std::path::Path;

fn main() {
    let path = Path::new("/usr").join("/local/bin");
    println!("{path:?}"); // Prints "/local/bin" 
}
```

This is because `Path::join` will return the second path if it is absolute.

I was not the only one who was confused by this behavior.
Here's a [thread on the topic](https://users.rust-lang.org/t/rationale-behind-replacing-paths-while-joining/104288), which also includes an answer by [Johannes Dahlström](https://users.rust-lang.org/u/jdahlstrom/summary):

> The behavior is useful because a caller [...] can choose whether it wants to
> use a relative or absolute path, and the callee can then simply absolutize it by
> adding its own prefix and the absolute path is unaffected which is probably what
> the caller wanted. The callee doesn't have to separately check whether the path
> is absolute or not.

And yet, I still think it's a footgun.
It's easy to overlook this behavior when you use user-provided paths.
Perhaps `join` should return a `Result` instead?
In any case, be aware of this behavior.


## Check For Unsafe Code In Your Dependencies With `cargo-geiger`

So far, we've only covered issues with your own code.
For production code, you also need to check your dependencies.
Especially unsafe code would be a concern.
This can be quite challenging, especially if you have a lot of dependencies.

[cargo-geiger](https://github.com/geiger-rs/cargo-geiger) is a neat tool that checks your dependencies for unsafe code.
It can help you identify potential security risks in your project.

```bash
cargo install cargo-geiger
cargo geiger
```

This will give you a report of how many unsafe functions are in your dependencies.
Based on this, you can decide if you want to keep a dependency or not.


## Clippy Can Prevent Many Of These Issues

Here is a set of clippy lints that can help you catch these issues at compile time.
See for yourself in the [Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2024&gist=26fffd0b9c89822295c4225182238c8c).

Here's the gist:

- `cargo check` will **not** report any issues. 
- `cargo run` will **panic** or silently fail at runtime.
- `cargo clippy` will **catch** all issues at _compile time_ (!) 😎

```rust
// Arithmetic
#![deny(arithmetic_overflow)] // Prevent operations that would cause integer overflow
#![deny(clippy::checked_conversions)] // Suggest using checked conversions between numeric types
#![deny(clippy::cast_possible_truncation)] // Detect when casting might truncate a value
#![deny(clippy::cast_sign_loss)] // Detect when casting might lose sign information
#![deny(clippy::cast_possible_wrap)] // Detect when casting might cause value to wrap around
#![deny(clippy::cast_precision_loss)] // Detect when casting might lose precision
#![deny(clippy::integer_division)] // Highlight potential bugs from integer division truncation
#![deny(clippy::arithmetic_side_effects)] // Detect arithmetic operations with potential side effects
#![deny(clippy::unchecked_duration_subtraction)] // Ensure duration subtraction won't cause underflow

// Unwraps
#![warn(clippy::unwrap_used)] // Discourage using .unwrap() which can cause panics
#![warn(clippy::expect_used)] // Discourage using .expect() which can cause panics
#![deny(clippy::panicking_unwrap)] // Prevent unwrap on values known to cause panics
#![deny(clippy::option_env_unwrap)] // Prevent unwrapping environment variables which might be absent

// Array indexing
#![deny(clippy::indexing_slicing)] // Avoid direct array indexing and use safer methods like .get()

// Path handling
#![deny(clippy::join_absolute_paths)] // Prevent issues when joining paths with absolute paths

// Serialization issues
#![deny(clippy::serde_api_misuse)] // Prevent incorrect usage of Serde's serialization/deserialization API

// Unbounded input
#![deny(clippy::uninit_vec)] // Prevent creating uninitialized vectors which is unsafe

// Unsafe code detection
#![deny(clippy::transmute_int_to_char)] // Prevent unsafe transmutation from integers to characters
#![deny(clippy::transmute_int_to_float)] // Prevent unsafe transmutation from integers to floats
#![deny(clippy::transmute_ptr_to_ref)] // Prevent unsafe transmutation from pointers to references
#![deny(clippy::transmute_undefined_repr)] // Detect transmutes with potentially undefined representations

use std::path::Path;
use std::time::Duration;

fn main() {
    // ARITHMETIC ISSUES

    // Integer overflow: This would panic in debug mode and silently wrap in release
    let a: u8 = 255;
    let _b = a + 1;

    // Unsafe casting: Could truncate the value
    let large_number: i64 = 1_000_000_000_000;
    let _small_number: i32 = large_number as i32;

    // Sign loss when casting
    let negative: i32 = -5;
    let _unsigned: u32 = negative as u32;

    // Integer division can truncate results
    let _result = 5 / 2; // Results in 2, not 2.5

    // Duration subtraction can underflow
    let short = Duration::from_secs(1);
    let long = Duration::from_secs(2);
    let _negative = short - long; // This would underflow

    // UNWRAP ISSUES

    // Using unwrap on Option that could be None
    let data: Option<i32> = None;
    let _value = data.unwrap();

    // Using expect on Result that could be Err
    let result: Result<i32, &str> = Err("error occurred");
    let _value = result.expect("This will panic");

    // Trying to get environment variable that might not exist
    let _api_key = std::env::var("API_KEY").unwrap();

    // ARRAY INDEXING ISSUES

    // Direct indexing without bounds checking
    let numbers = vec![1, 2, 3];
    let _fourth = numbers[3]; // This would panic

    // Safe alternative with .get()
    if let Some(fourth) = numbers.get(3) {
        println!("{fourth}");
    }

    // PATH HANDLING ISSUES

    // Joining with absolute path discards the base path
    let base = Path::new("/home/user");
    let _full_path = base.join("/etc/config"); // Results in "/etc/config", base is ignored

    // Safe alternative
    let base = Path::new("/home/user");
    let relative = Path::new("config");
    let full_path = base.join(relative);
    println!("Safe path joining: {:?}", full_path);

    // UNSAFE CODE ISSUES

    // Creating uninitialized vectors (could cause undefined behavior)
    let mut vec: Vec<String> = Vec::with_capacity(10);
    unsafe {
        vec.set_len(10); // This is UB as Strings aren't initialized
    }
}
```

## Conclusion

Phew, that was a lot of pitfalls!
How many of them did you know about?

Even if Rust is a great language for writing safe, reliable code, developers still need to be disciplined to avoid bugs.

A lot of the common mistakes we saw have to do with Rust being a systems programming language:
In computing systems, a lot of operations are performance critical and inherently unsafe. 
We are dealing with external systems outside of our control, such as the operating system, hardware, or the network.
The goal is to build safe abstractions on top of an unsafe world.

Rust shares an FFI interface with C, which means that it can do anything C can do.
So, while some operations that Rust allows are theoretically possible, they might lead to unexpected results.

But not all is lost!
If you are aware of these pitfalls, you can avoid them, and with the above clippy lints, you can catch most of them at compile time.

That's why testing, linting, and fuzzing are still important in Rust.

For maximum robustness, combine Rust's safety guarantees with strict checks and
strong verification methods.

{% info(title="Let an Expert Review Your Rust Code", icon="crab") %}

I hope you found this article helpful!
If you want to take your Rust code to the next level, consider a code review by an expert.
I offer code reviews for Rust projects of all sizes. [Get in touch](/about/) to learn more.

{% end %}
