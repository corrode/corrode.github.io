+++
title = "Thinking in Traits"
date = 2025-11-05
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

Consider this utterly mundane line of Rust:

```rust
let doubled: Vec<_> = numbers.iter().map(|x| x * 2).collect();
```

Why does `collect()` work here? How does it know to produce a `Vec`? The answer reveals something essential about Rust's design philosophy.

Here's the signature of `collect`:

```rust
fn collect<B: FromIterator<Self::Item>>(self) -> B
where
    Self: Sized,
{
    FromIterator::from_iter(self)
}
```

The method doesn't know what type you're collecting into. It doesn't need to. It only knows that whatever type you want must be capable of constructing itself from an iterator. This is why the same `collect()` works for `Vec`, `HashSet`, `String`, `HashMap`, or any custom collection you define—as long as it implements `FromIterator`.

This is not a convenience feature. This is how Rust works.

The language is governed by traits. Iteration exists because of the `Iterator` trait. Conversion exists because of `From` and `TryFrom`. Comparison exists because of `PartialEq` and `Ord`. Formatting exists because of `Display` and `Debug`. These aren't just standard library utilities. They're the vocabulary of the language itself.

Once you see this—really see it—Rust stops feeling like a language with arbitrary rules and starts feeling like a language with a coherent philosophy. The question isn't "should I use traits?" The question is "how do I think in terms of capabilities instead of hierarchies?"

## Capability, Not Taxonomy

If you're coming from an object-oriented language, your instinct is to model the world as a hierarchy of types. You create base classes and derive from them. You think in terms of "is-a" relationships. A `Dog` is-a `Mammal` is-a `Animal`.

This breaks down quickly.

Consider error handling. You might create an `Error` base class. Network errors inherit from it. Parse errors inherit from it. Database errors inherit from it. Then you need an error that's both a network error and a database error—a connection timeout to a remote database. Your hierarchy fractures.

Or consider file operations. You create a `File` class with `read()` and `write()` methods. Then you need read-only files. Do you make `write()` panic? Return an error? You've encoded a runtime concept (permissions) into a compile-time hierarchy, and now every `write()` call carries the possibility of failure even when you know statically that it can't fail.

The problem is fundamental: inheritance forces you to choose a single axis of classification. But real-world concepts don't arrange themselves into neat trees. They have multiple, orthogonal properties.

Rust asks you to think differently. Not "what is this thing?" but "what can this thing do?"

```rust
trait Read {
    fn read(&mut self, buf: &mut [u8]) -> Result<usize>;
}

trait Write {
    fn write(&mut self, buf: &[u8]) -> Result<usize>;
}
```

A type can implement `Read`, or `Write`, or both, or neither. The capabilities are independent. A `TcpStream` implements both. A `File` opened in read-only mode implements only `Read`. A `/dev/null` sink implements only `Write`. The type system enforces what each type can actually do.

This is surgical precision. You're not inheriting a bundle of methods you may or may not need. You're declaring exactly what a type is capable of.

## Bounded vs Unbounded: Enums and Traits

Here's a guideline that takes time to internalize: enums are for bounded sets, traits are for unbounded sets.

If you statically know all possible variants—every type that will ever exist in your program—use an enum:

```rust
enum PaymentMethod {
    CreditCard { number: String, cvv: String },
    BankTransfer { account: String, routing: String },
    Cryptocurrency { wallet: String },
}

fn process(payment: PaymentMethod) -> Result<Receipt> {
    match payment {
        PaymentMethod::CreditCard { number, cvv } => { /* ... */ }
        PaymentMethod::BankTransfer { account, routing } => { /* ... */ }
        PaymentMethod::Cryptocurrency { wallet } => { /* ... */ }
    }
}
```

The compiler enforces exhaustiveness. Add a new payment method, and every `match` that handles payments will fail to compile until you update it. This is not a limitation—it's a guarantee. You cannot forget a case.

Traits are for when you can't know all the types. When third parties need to extend your system. When the set is open:

```rust
trait DataSource {
    fn fetch(&self) -> Result<Vec<Record>>;
}

// Your library defines some sources
impl DataSource for PostgresSource { /* ... */ }
impl DataSource for RedisSource { /* ... */ }

// Users define their own
impl DataSource for CustomApiSource { /* ... */ }
impl DataSource for CsvFileSource { /* ... */ }
```

Coming from OOP, this feels backward. We're trained to reach for polymorphism early, to design for extension from the start. In Rust, you should default to concrete types—to enums—until you need extensibility.

Why? Because concrete types are clearer, faster to compile, easier to refactor, and give you exhaustiveness checking. Traits are powerful, but power has a cost. Use them deliberately, not reflexively.

## Small Traits, Clear Contracts

The bigger the interface, the weaker the abstraction. This is true in any language, but Rust's trait system makes it particularly visible.

Consider this trait:

```rust
trait Context: Send + Sync + Debug {
    fn open_source(&self, name: &str) -> BoxStream<'static, Result<Item>>;
    fn open_sink(&self, name: &str) -> BoxSink<'static, Item>;
    fn graph(&self) -> MutexGuard<'static, Graph>;
    fn run(&self, block: bool) -> Result<()>;
    fn subscriber(&self) -> Arc<dyn Subscriber + Send + Sync>;
}
```

Try to document this trait. Not the individual methods—document what the trait represents, what concept it captures, what contract it enforces.

You can't. It has no unified purpose. It's a grab-bag of unrelated capabilities: source management, sink management, graph access, runtime execution, observability. Implementing this trait means implementing all of it, even if you only need one piece.

The trait is optimized for the convenience of the trait author, not the trait implementer. That's backwards.

Break it apart:

```rust
trait SourceManager {
    fn open_source(&self, name: &str) -> Result<Box<dyn Source>>;
}

trait SinkManager {
    fn open_sink(&self, name: &str) -> Result<Box<dyn Sink>>;
}

trait GraphAccess {
    fn graph(&self) -> &Graph;
}
```

Now each trait has a single responsibility. A type can implement one, some, or all of them. Generic code can declare precisely what it needs:

```rust
fn process_data<S, T>(source: &S, sink: &T) -> Result<()>
where
    S: SourceManager,
    T: SinkManager,
{
    // Only requires source and sink management, nothing else
}
```

This is composition. You're not locked into implementing a monolithic interface. You're not forced to provide functionality you don't have. The type system enforces that callers only use capabilities you've declared.

Small traits are easier to implement, easier to test, easier to understand, and easier to compose. They make your contracts explicit and your dependencies clear.

## Conditional Implementation: The Hidden Power

Here's something you cannot do with interfaces or abstract classes:

```rust
impl<T: Clone> Clone for Vec<T> {
    fn clone(&self) -> Self {
        // Vec is cloneable if T is cloneable
    }
}
```

This says: "`Vec<T>` implements `Clone` if and only if `T` implements `Clone`."

The capability propagates automatically. A `Vec<String>` is cloneable because `String` is cloneable. A `Vec<TcpStream>` is not, because `TcpStream` isn't. The compiler enforces this at compile time. You cannot call `.clone()` on a vector of non-cloneable things. The code won't compile.

This is profoundly powerful. Complex types automatically derive capabilities from their components. The trait system composes, and the compiler tracks it all.

You also can't implement a trait separately from a type definition in most OOP languages. The interface must be declared when the class is defined. In Rust, you can implement traits for types you didn't write:

```rust
use external_crate::TheirType;

impl Display for TheirType {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "custom formatting")
    }
}
```

This unlocks a different way of organizing code. Behavior doesn't have to live with the type definition. It can be defined where it makes sense, when it makes sense, by whoever needs it.

The Orphan Rule prevents chaos—you can only implement a trait for a type if you own either the trait or the type—but within those constraints, you have remarkable flexibility. You can extend types from other crates. You can add capabilities as you discover you need them. The type system stays coherent, but the code stays flexible.

## Traits as the Language's Foundation

Many Rust developers initially focus on ownership, borrowing, and lifetimes—the low-level mechanics that make Rust memory-safe. These are important, but they're not where the power lies for writing high-level code.

Traits are severely underrated. They're the mechanism that makes Rust's standard library feel magical:

```rust
let numbers = vec![1, 2, 3, 4, 5];
let doubled: Vec<_> = numbers.iter().map(|x| x * 2).collect();
```

Why does `collect()` work? Because `Vec<T>` implements `FromIterator<T>`:

```rust
fn collect<B: FromIterator<Self::Item>>(self) -> B
where
    Self: Sized,
{
    FromIterator::from_iter(self)
}
```

The method doesn't know what type you're collecting into. It just knows that the target type can construct itself from an iterator. This is why you can collect into a `Vec`, a `HashSet`, a `String`, or any custom type that implements the trait.

The language is governed by traits. Once you start seeing them—really seeing them—Rust stops feeling like a language with a steep learning curve and starts feeling like a language with a coherent philosophy. Traits like `Iterator`, `From`, `TryFrom`, `Display`, `Debug`, `Clone`, and `Default` aren't just standard library features. They're the vocabulary of idiomatic Rust.

## When Abstraction Earns Its Keep

A practical guideline: repeat yourself three times before abstracting.

Write the code concretely first. If you find yourself copying similar implementations across different types, that's your signal. Not before.

This goes against everything you learned in OOP. Design for extension. Program to interfaces. Depend on abstractions, not concretions. These maxims don't translate to Rust, at least not in application code.

Premature abstraction is genuinely costly here:
- Traits slow down compilation
- They obscure control flow
- They make error messages harder to parse
- They make code harder to navigate

But when you do need them—when you're genuinely sharing behavior across multiple types, when you need extensibility, when you're building a library—traits are the right tool. They compile to zero-cost abstractions. They enable fearless refactoring. You can always add a trait layer later without breaking existing code.

The type system gives you the confidence to start concrete and refactor to abstract when the need becomes clear. This is unusual. In most languages, refactoring from concrete to abstract is risky, so we abstract early to avoid the risk. In Rust, the compiler catches breaking changes, so we can afford to wait.

Traits are not a default. They're a tool you reach for deliberately.

## Thinking in Capabilities

Traits force isolated programming. Each trait is a focused contract. Types implement only what they need. Generic code declares only the capabilities it requires.

This has cascading effects:
- You stop modeling hierarchies and start modeling capabilities
- You compose small, focused abstractions instead of inheriting large, monolithic ones
- You write code that declares its requirements explicitly

This is why Rust integrates seamlessly with external crates. Serde can serialize your types. Diesel can query databases with your models. Axum can handle HTTP requests with your handlers. Each crate defines traits that express what it needs. Your types implement those traits. The boundaries are clear. The contracts are explicit. The compiler enforces everything.

It's also why testing becomes simpler. You don't need elaborate mocking frameworks. You define a trait for the behavior you need to fake, implement it for your test doubles, and pass them to your code. The type system ensures the mock satisfies the contract.

This is not just about technical capability. It's about how you think. When you approach a problem, you ask: "What does this type need to be able to do?" not "What kind of thing is this type?"

That shift—from taxonomy to capability—is what makes Rust feel different.

## The Threshold

Many developers learning Rust focus on ownership, borrowing, and lifetimes. These are the mechanics that make Rust memory-safe, and they demand attention because they're unfamiliar and the compiler is strict about them.

But they're not where the power lies for writing clear, maintainable code.

Traits are severely underrated. They're what make the standard library feel coherent. They're what make external crates compose seamlessly. They're what enable you to write generic, reusable code without sacrificing type safety or performance.

When you start reaching for traits naturally—when you see a problem and instinctively think "this needs a trait" or "this should be an enum"—you've crossed a threshold. Rust stops being a language you translate your OOP thinking into. It becomes a language you think in directly.

That's when writing Rust feels natural. That's when it clicks.