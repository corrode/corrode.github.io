+++
title = "Pitfalls of Safe Rust"
date = 2025-02-13
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
   "[The Four Horsemen of Bad Rust Code](https://github.com/corrode/four-horsemen-talk) -- My talk at FOSDEM 2024" 
]
+++

When people say Rust is a "safe language", they often mean memory safety.
And while memory safety is a great start, it's far from all it takes to build robust applications.

**Memory safety is important but not sufficient for overall reliability.**

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
of performance for better safety.

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

- use `From::from()` when you need to guarantee no data loss.
- use `TryFrom` when you need to handle potential data loss gracefully.
- use `as` when you're comfortable with potential truncation or know the values will fit within the target type's range and when performance is absolutely critical.

**If in doubt, prefer `From::from()` and `TryFrom` over `as`.**

*Adapted from [StackOverflow answer by delnan](https://stackoverflow.com/a/28280042/270334) and [additional context](https://stackoverflow.com/a/48795524/270334)*

{% end %}

The `as` operator is **not safe for narrowing conversions**
It will silently truncate the value, leading to unexpected results.

What is a narrowing conversion?
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
let y = i8::try_from(x);

match y {
    Ok(value) => println!("It worked: {}", value),
    Err(_) => println!("Oh no, it didn't work!"),
}
```

## Use Bounded Types for Numeric Values

Bounded types make it easier to express invariants and avoid invalid states.

E.g. if you have a numeric type and 0 is *never* a correct value, use [`std::num::NonZeroUsize`](https://doc.rust-lang.org/std/num/type.NonZeroUsize.html) instead.

You can also create your own bounded types:

```rust
// DON'T: Use raw numeric types for domain values
struct Product {
    price: f64,  // Could be negative!
    quantity: i32, // Could be negative!
}

// DO: Create bounded types
#[derive(Debug, Clone, Copy)]
struct NonNegativePrice(f64);

impl NonNegativePrice {
    pub fn new(value: f64) -> Result<Self, PriceError> {
        if value < 0.0 || !value.is_finite() {
            return Err(PriceError::Invalid);
        }
        Ok(NonNegativePrice(value))
    }
}

struct Product {
    price: NonNegativePrice,
    quantity: NonZeroU32,
}
```

## Don't Index Into Arrays Without Bounds Checking

Whenever I see the following, I get goosebumps 😨:

```rust
let arr = [1, 2, 3];
let elem = arr[3];  // Panic!
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
A typical mistake is to use `split_at`:

```rust
let arr = [1, 2, 3];
let (left, right) = arr.split_at(3);
```

**The above code will panic because the index is out of bounds!**

To handle that more gracefully, use `split_at_checked` instead:

```rust
let arr = [1, 2, 3];
// This returns an Option
match arr.split_at_checked(3) {
    Some((left, right)) => {
        // Do something with left and right
    }
    None => {
        // Handle the error
    }
}
```

Again, this returns an `Option` which allows you to handle the error case.

More info about `split_at_checked` [here](https://doc.rust-lang.org/std/primitive.slice.html#method.split_at_checked).


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
This issue can be detected at compile-time:

Use types to enforce valid states:

```rust
// First, let's define the possible states for the connection
enum ConnectionSecurity {
    Insecure,
    // We can't have an SSL connection
    // without a certificate!
    Ssl { cert_path: String },
}

struct Configuration {
    port: u16,
    host: String,
    // Now we can't have an invalid state!
    // Either we have an SSL connection with a certificate
    // or we don't have SSL at all.
    security: ConnectionSecurity,
}
```

I wrote about an entire blog post on that topic: [Making Invalid States Unrepresentable](/blog/illegal-state/).

## Avoid Primitive Types For Business Logic

It's very tempting to use primitive types for everything.
Especially Rust beginners fall into this trap.

```rust
// DON'T: Use primitive types for IDs
fn get_user(id: u64) {
    // Raw u64 could be any number
}
```

However, do you really accept any number as a valid user ID?
What if 0 is not a valid ID?

You can create a custom type for your domain instead:

```rust
// DO: Create specific ID types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
struct UserId(u64);

impl UserId {
    pub fn new(id: u64) -> Result<Self, IdError> {
        if id == 0 {
            return Err(IdError::Invalid);
        }
        Ok(UserId(id))
    }
}

fn get_user(id: UserId) {
    // We know this is always a valid user ID!
}
```

## Handle Default Values Carefully

It's quite common to add a blanket `Default` implementation to your types.
But that can lead to unforeseen issues.

For example, here's a case where the port is set to 0 by default, which is not a valid port number:

```rust
// DON'T: Implement `Default` without consideration
#[derive(Default)]  // Might create invalid states!
struct ServerConfig {
    port: u16,      // Will be 0, which isn't a valid port!
    max_connections: usize,
    timeout_seconds: u64,
}
```

Instead, consider if a default value makes sense for your type.

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

If you blindly derive `Debug` for your types, you might expose sensitive data.
Instead, implement `Debug` manually for types that contain sensitive information.

```rust
// DON'T: Expose sensitive data in debug output
struct User {
    username: String,
    password: String,  // Will be printed in debug output!
}

// DO: Protect sensitive data
struct Password(String);

impl std::fmt::Debug for Password {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("[REDACTED]")
    }
}

struct User {
    username: String,
    password: Password,
}
```

For production code, use a crate like [`secrecy`](https://crates.io/crates/secrecy). 

However, it's not black and white either:
If you implement `Debug` manually, you might forget to update the implementation when your struct changes.
A common pattern is to destructure the struct in the `Debug` implementation to catch such errors:

```rust
impl fmt::Debug for Settings {  
   fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {  
       // Destructure the struct to catch changes
       // This way, the compiler will warn you if you add a new field
       // and forget to update the Debug implementation
       let Settings { version, base_url, content_dir } = self;  
       f.debug_struct("Settings")  
           .field("version", version)
           .field("base_url", &base_url.as_str())
           .field("content_dir", content_dir)
           .finish()  
   }  
}
```

Thanks to [Wesley Moore (wezm)](https://www.wezm.net) for the hint.

## Careful With Serialization 

Don't blindly derive `Serialize` and `Deserialize` -- especially for sensitive data. 
The values you read/write might not be what you expect!

```rust
// DON'T: Blindly derive Serialize and Deserialize 
#[derive(Serialize, Deserialize)]
struct UserCredentials {
    #[serde(default)]  // ⚠️ Accepts empty strings when deserializing!
    username: String,
    #[serde(default)]
    password: String, // ⚠️ Leaks the password when serialized!
}
```

When deserializing, the fields might be empty.
Empty credentials could potentially pass validation checks if not properly handled

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
TOCTOU is a class of software bugs caused by attackers exploiting the gap between the time a condition is checked and the time it is used. 
Simply put, an attacker could rug-pull the value from under your feet
and you wouldn't notice because it happens exactly between your check and use.

```rust
// DON'T: Check and use in separate operations
fn process_file(path: &Path) -> Result<(), io::Error> {
    if path.exists() {  // Check
        let content = fs::read(path)?;  // Use - file might have changed!
        // Process content
    }
    Ok(())
}
```

Rust supports atomic file operations to prevent this kind of attack.

```rust
// DO: Use atomic operations when possible
fn process_file(path: &Path) -> Result<(), io::Error> {
    let file = fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create_new(true)  // Atomic operation
        .open(path)?;
    // Process file
    Ok(())
}
```

It's a bit more verbose, but it's safer.
I think more Rustaceans should know about this pattern.


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
const MAX_REQUEST_SIZE: usize = 1024 * 1024;  // 1MB

fn process_request(data: &[u8]) -> Result<(), Error> {
    if data.len() > MAX_REQUEST_SIZE {
        return Err(Error::RequestTooLarge);
    }
    
    let decoded = decode_data(data)?;
    
    // For added safety, you can also check the decoded size 
    if decoded.len() > MAX_REQUEST_SIZE * 2 {  
        return Err(Error::DecodedDataTooLarge);
    }
    
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
If a non-sys level crate has a lot of unsafe code, that could be a red flag.

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
If you are aware of these pitfalls, you can avoid them.

That's why testing, fuzzing, and static analysis are still important in Rust.

For maximum robustness, combine Rust's safety guarantees with strict checks and
strong verification methods.

{% info(title="Let an Expert Review Your Rust Code", icon="crab") %}

I hope you found this article helpful!
If you want to take your Rust code to the next level, consider a code review by an expert.
I offer code reviews for Rust projects of all sizes. [Get in touch](/about/) to learn more.

{% end %}
