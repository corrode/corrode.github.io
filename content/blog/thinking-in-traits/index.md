+++
title = "Thinking in Traits"
date = 2026-11-02
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
resources = [
    "[Iteration patterns for Result & Option](http://xion.io/post/code/rust-iter-patterns.html) - Karol Kuczmarski's post that introduced me to collecting results in different ways",
    "[FromIterator](https://doc.rust-lang.org/std/iter/trait.FromIterator.html) - How collections construct themselves from iterators",
    "[Trait Implementation Coherence](https://doc.rust-lang.org/reference/items/implementations.html#trait-implementation-coherence) - The rules for implementing traits",
    "[Using Enums to Represent State](/blog/enums/) - Modeling a closed set of possibilities",
    "[Understanding Dyn Compatibility](/blog/dyn-compatibility/) - When traits can be used with dynamic dispatch",
]
+++

Rust favors composition over inheritance.
I'm sure you've heard that before, but rarely does anyone take the time to explain what it means in practice.
Also, why is this model the right choice for Rust?

Let's take a step back and look at an example: have you ever asked yourself why `collect()` works the way it does?

```rust
let doubled: Vec<_> = numbers.iter().map(|x| x * 2).collect();
```

How does `collect` know to produce a `Vec` here?
To answer that, let's first look at the signature of `Iterator::collect`:

```rust
fn collect<B: FromIterator<Self::Item>>(self) -> B
where
    Self: Sized,
{
    FromIterator::from_iter(self)
}
```

Note how it doesn't mention `Vec` at all.

In fact, it doesn't "know" about any collection type or any other type, for that matter.
The thing it *does* know is that whatever type you want must be capable of constructing itself from an iterator.
And `Vec<_>` happens to be a type that does.
Further note that we didn't specify the element type of the vector.
The compiler is clever enough to infer that from the context!

The mechanism is the same for any other supported type, like hash maps, strings, or any custom collection type of your choosing as long as it implements `FromIterator` for the iterator's item type.

And what "collecting" means is also defined by the type itself.
A `String`, for example, has the ability to collect characters:

```rust
let chars = ['a', 'b', 'c'];
let string: String = chars.iter().collect(); // "abc"
```

And a `HashMap` can collect key-value pairs:

```rust
let pairs = [("a", 1), ("b", 2), ("c", 3)];

// {"a": 1, "b": 2, "c": 3}
let map: HashMap<_, _> = pairs.iter().cloned().collect();
```

It's only fair to mention that interfaces can also express shared contracts.
Here, two independently defined implementations connect through a shared item type.
This is "composition through contracts":

<figure>
  <img src="collect-contracts.svg" alt="Ranges, slice iterators, and custom iterators connect through collect() to Vec, HashSet, or a custom collection. Both traits share the item type T." width="720" height="270" style="display: block; margin: 1em auto; max-width: 100%; height: auto;">
  <figcaption>Any of these iterators can feed into any of these collections as long as the bounds are satisfied. For example, <code>HashSet&lt;T&gt;</code> also requires <code>T: Eq + Hash</code>.</figcaption>
</figure>

Here, a producer yields values of some type `T` through the `Iterator` trait.
On the other side, a collection implements `FromIterator<T>` to describe how it can build itself from those values.
The shared item type `T` connects the two contracts, and `collect()` is the bridge between them.
It requires only that the destination can be constructed from the items the iterator yields.

In our first example, the `Vec<_>` annotation selects the destination type.
Because `Vec<T>` implements `FromIterator<T>`, the compiler knows how to connect that destination to our iterator.
`collect()` is the glue that passes the iterator to that implementation, which creates and fills the vector.

Note how neither side needs to know the concrete type on the other side.
The iterator doesn't need to know how a vector stores its elements.
And the vector doesn't need to know where the items came from, only how to iterate over them.

**That means we can extend either side independently.**
A new iterator can feed existing collections, and a new collection implementing `FromIterator<T>` can accept existing iterators yielding `T`.
We don't need a separate conversion for every producer–collection pair.
All we need is one implementation, and `collect()` is the glue that brings it all together.

In simple Rust pseudocode, we can expand the calls step by step:

```rust
// We call:
iterator.collect::<Vec<T>>()

// collect() delegates to:
Vec::<T>::from_iter(iterator)

// Which conceptually expands to:
let mut vector = Vec::new();
while let Some(item) = iterator.next() {
    vector.push(item);
}
vector
```

The value of an abstraction is the code that no longer needs to exist between its users.

## Boulevard of Broken Hierarchies

Class inheritance models **"is-a"** relationships.
In Java, for example, an [`SSLSocket`](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/javax/net/ssl/SSLSocket.html) is a subclass of [`Socket`](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/net/Socket.html).
An encrypted socket is still a socket, after all.
But does every socket operation make sense for it?

`Socket.shutdownOutput()` lets a TCP connection stop sending while continuing to receive, a feature called "half-closing."
Code using a socket might therefore do this:

```java
void finishSending(Socket socket) throws IOException {
    socket.shutdownOutput();
}
```

On Android API levels 21 through 23, the platform's `SSLSocket` implementations [rejected this operation](https://android.googlesource.com/platform/libcore/+/android-6.0.0_r1/luni/src/main/java/javax/net/ssl/SSLSocket.java#847) with `UnsupportedOperationException`.
This caused [a real crash in OkHttp 5.2.0](https://github.com/square/okhttp/issues/9123).
Modern OpenJDK [supports TLS-aware shutdown](https://bugs.openjdk.org/browse/JDK-8207009), so this is a historical mismatch, not a universal limitation of TLS.
Still, the `Socket` type exposed an operation without telling callers whether that implementation supported it.

With composition, a TLS connection can hold a socket internally without exposing every operation on it.
It can provide reading and writing, with a separate capability for half-closing where supported.
We can reuse the transport without inheriting its entire interface.

Simply replacing inheritance with interfaces—or traits—doesn't fix a poorly chosen contract.
What's important is that **the contract matches the capabilities of its implementations**.

## Capability, Not Taxonomy

Rust makes trait-based composition central to code reuse.
In Rust, we ask what a type can **do**, not what it **is**.
In other words, traits describe capabilities, not taxonomies.

Here are simplified versions of two central I/O traits from the standard library:

```rust
trait Read {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize>;
}
```

```rust
trait Write {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize>;
}
```

Note how these are two independent traits.
A type can implement `Read`, or `Write`, or both, or neither.
You're declaring which operations a type supports, without inheriting a bunch of unrelated methods.
The capabilities are orthogonal.

For example:

- A byte slice (`&[u8]`) implements `Read` but not `Write`.
- The `Sink` returned by `std::io::sink()` implements `Write` but not `Read`.
- A `TcpStream` implements both.

The trait implementation belongs to the *type*, not to a concrete value.
Take `std::fs::File`, for example.
It implements both `Read` and `Write`, but a file opened in read-only mode will still fail at runtime if you try to write to it.
Even a file opened for writing can fail when the disk fills up.
The trait implementation is a promise that the type supports those operations, but what it can't do is guarantee that every operation will succeed at runtime.

If you want to distinguish read-only and writable handles at compile time, you could define a `ReadOnlyFile` and a `WritableFile` and only implement the appropriate traits for each.
That rules out unsupported operations in your API, but it still doesn't make I/O infallible.

## Same Type, Different Capabilities

Rust can express that a container has a capability only when its contents do.
For example, `Vec<T>` implements `Clone` when `T` implements `Clone`.
Thanks to this trick, we don't end up with two different `Vec` types, one cloneable and one not.

Here's the same pattern for a small wrapper you could define yourself:

```rust
struct Batch<T> {
    items: Vec<T>,
}

impl<T: Clone> Clone for Batch<T> {
    fn clone(&self) -> Self {
        Self {
            items: self.items.clone(),
        }
    }
}
```

A `Batch<String>` is cloneable because `String` is cloneable.
A `Batch<std::net::TcpStream>` is not, since `TcpStream` does not implement `Clone`.
If you were to call `.clone()` on that batch, the code wouldn't compile.
You can store non-cloneable items in a batch; you just can't clone that batch.

For this wrapper, you can use `#[derive(Clone)]` to generate the conditional implementation automatically.
Note that the bound belongs on the **implementation**, not on `Batch` itself.
Making your type cloneable requires `T: Clone`, but apart from that, `Batch<T>` is still a perfectly valid type for non-cloneable elements.
The compiler works out which operations are available from the **capabilities of the component types**.

A conditional implementation can also apply to every type that satisfies a trait bound as opposed to one particular wrapper.
This is called a *blanket implementation*.
For example, the standard library implements [`ToString` for every type that implements `Display`](https://doc.rust-lang.org/std/string/trait.ToString.html):

```rust
impl<T: std::fmt::Display + ?Sized> ToString for T {
    // Implementation omitted.
}
```

All you have to do to get a `.to_string()` method is implement `Display` for your type.
The compiler automatically generates the `ToString` implementation for you.

The rule applies even to types written long after the standard library itself.
This is an elegant way to express a reusable implication between capabilities: "If a type can be displayed, it can be turned into a string."

The same idea appears in conversions.
You might know that implementing [`From<T> for U`](https://doc.rust-lang.org/std/convert/trait.From.html) automatically provides `Into<U> for T` through a blanket implementation.
That's why you normally implement `From` rather than writing the corresponding `Into` implementation yourself.

## Building Blocks From Building Blocks

Conditional implementations also let us add behavior by wrapping one value in another.
This is a different type of composition: "composition of values."
A wrapper holds another value and builds on its capabilities.
Take our `Read` trait from earlier:

- A `File` implements `Read`.
- Wrapping it in a `BufReader` adds buffering, and the result still implements `Read`.
- Calling `.take(limit)` on that reader limits how many bytes it yields, and the result *still* implements `Read`.

```text
File
  → BufReader<File>
    → Take<BufReader<File>>
```

So a parser accepting `R: Read` doesn't need separate support for files, buffered files, and length-limited buffered files.
It just reads bytes!

We can add buffering and a byte limit without teaching the parser about either.
The parser doesn't need to understand how its input was assembled.

This works because each wrapper preserves the contract that the next piece needs.
A `BufReader<R>` implements `Read` when `R` does, and so does `Take<R>`.
The result of one composition becomes a building block for the next.

You can see the same idea in iterator chains.

- `.map()` produces a `Map<I, F>` iterator that applies a function to each item of the underlying iterator `I`.
- `.filter()` produces a `Filter<I, P>` iterator that yields only the items of `I` that satisfy the predicate `P`.
- `.take()` produces a `Take<I>` iterator that yields at most the first `n` items of `I`.

Each type implements `Iterator`, so you can chain them.

Writing your own iterator connects your type to this vast ecosystem of adapters.
All you need is to provide the associated `Item` type and the [`next()` method](https://doc.rust-lang.org/std/iter/trait.Iterator.html).
`map`, `filter`, `fold`, and `collect` already have default implementations, available when their additional bounds are satisfied.
This is how you reuse code without a base class.
Default methods provide behavior within a trait you implement; blanket implementations can make another trait apply automatically.

But adapters don't have to be limited to a single, rigid contract either.
They can provide rich, additional capabilities, too.

For example, [`Map<I, F>` implements `DoubleEndedIterator`](https://doc.rust-lang.org/std/iter/struct.Map.html#impl-DoubleEndedIterator-for-Map%3CI,+F%3E) when its input iterator does, and it does so with an appropriate trait bound on the mapping function:

```rust
let values: Vec<_> = (0..5)
    .map(|n| n * 2)
    .rev()
    .collect();

assert_eq!(values, [8, 6, 4, 2, 0]);
```

So because the `map` adapter has a conditional implementation for `DoubleEndedIterator`, it preserves the ability to iterate backward through the input.
We're not limited to basic iteration.

And since we know the concrete iterator types, the compiler can optimize and inline the entire chain of adapters into a single loop.
Optimized iterator code can [perform comparably to a hand-written loop](https://doc.rust-lang.org/book/ch13-04-performance.html).
So [fully embracing iterator patterns](/blog/iterators) has no runtime cost.

## To Enum Or To Trait?

Hold on, Rust has another way to express "different kinds of things that are related": enums!
These are useful in situations where you know the full list of possibilities in advance.

```rust
enum InputSource {
    File { path: PathBuf },
    Http { url: String, timeout: Duration },
    Stdin,
}
```

Enums are great if you almost always want to handle all of the variants in one place.
Traits are the better model if different types implement the same behavior and you don't know all of the types right now.
In other words, enums are a closed set of variants while traits are an open set of implementations.

You can't add new variants to an enum without changing the enum definition.
But traits enable the open/closed principle: you can add new implementations without modifying existing code.
This allows other crates to extend your library without needing to modify your code.

Imagine your library defines the `Record` and `FetchError` types, and you want to provide a way for users to fetch records from different sources.

```rust
pub trait DataSource {
    fn fetch(&self) -> Result<Vec<Record>, FetchError>;
}
```

In your library, you implement `DataSource` for a `PostgresSource` and a `RedisSource`.

But now, users can implement it for their own `CsvFileSource` or a `CustomApiSource`.
Heck, you don't even need to know these types exist.
And yet, your contract still holds: any type that implements `DataSource` can be used to fetch records.

The reverse is also true: an external contributor can define an extension trait and implement it for **your** type without you knowing about it.
You can even do that with types from the standard library:

```rust
trait ScreamingCase {
    fn screaming_case(&self) -> String;
}

impl ScreamingCase for String {
    fn screaming_case(&self) -> String {
        self.to_uppercase()
    }
}
```

As long as the trait is in scope, you can call the method on a `String`:

```rust
let text = String::from("hello");
assert_eq!(text.screaming_case(), "HELLO");
```

No need to modify `String` or derive a `ScreamingString` subclass.
This implementation is allowed because we define `ScreamingCase` in our crate.
Rust's [coherence rules](https://doc.rust-lang.org/reference/items/implementations.html#trait-implementation-coherence) restrict implementations involving foreign traits **and** types.
For example, we couldn't implement the standard library's `Display` trait directly for `Vec<String>`, since neither the trait nor the type is ours.

This is **composition at the level of behavior**: we combine an existing type with an independently defined capability.
The type and the trait don't need to know about each other.
The same type can implement other, unrelated traits, and each function can ask for just the capabilities it needs by means of trait bounds:

```rust
// This works for any type that implements `ScreamingCase`.
// E.g. why not implement it for `Vec<String>`, or `char` as well?
fn scream<T: ScreamingCase>(value: &T) {
    println!("{}", value.screaming_case());
}
```

This open-set/closed-set principle is a good way to think about when to use enums and when to use traits.
But to be fair, the lines can blur a bit.
An enum can also implement traits, and a library can restrict who implements a trait through a technique called a "sealed trait."

In application code, exhaustive enum checking can make refactoring easier because the compiler will tell you which `match` statements need to be updated when you add a new variant.
Introduce a trait instead when you have a good reason to share a contract **across types**.

## Smaller Traits, Better Contracts

The more unrelated responsibilities a trait combines, the harder it becomes to implement and reuse.
Every implementer has to account for operations it may not need.

Consider this application context:

```rust
trait Context {
    fn fetch(&self, key: &str) -> Result<Record, Error>;
    fn store(&mut self, key: &str, record: &Record) -> Result<(), Error>;
    fn run(&mut self) -> Result<(), Error>;
}
```

Ask yourself: what concept does this trait capture?
What contract does it enforce?
It combines reading records, writing records, and running the application.

Perhaps your application really needs one type to provide it all, but a function that copies records shouldn't require its inputs to run an application.
Let's split the capabilities:

```rust
trait Fetch {
    fn fetch(&self, key: &str) -> Result<Record, Error>;
}

trait Store {
    fn store(&mut self, key: &str, record: &Record) -> Result<(), Error>;
}
```

Now a read-only source can implement `Fetch`, a write-only destination can implement `Store`, and the execution runtime is left out.
Your functions don't need to know about the runtime either, and you can compose the exact capabilities you need:

```rust
fn copy_record<S: Fetch, D: Store>(
    source: &S,
    destination: &mut D,
    key: &str,
) -> Result<(), Error> {
    let record = source.fetch(key)?;
    destination.store(key, &record)
}
```

Each of your types can implement either trait. Or both.

This also explains how independent crates work with your types.
Serde defines `Serialize` and `Deserialize`; your types implement them, often through derive macros.
Serde's serializers don't need to know about your application's structs in advance.
They just use the shared contract: a type that implements `Serialize` can be serialized.
Code becomes more composable as a consequence.
If Serde decided to couple serialization and deserialization into a single trait, some use cases would be impossible to express.

All of that is great for testing, too.
We can test `copy_record` with a fake `Fetch` implementation and a fake `Store` implementation, without creating a runtime.

The goal isn't to make every trait contain exactly one method.
`Iterator` has many methods, but they are all strictly related to the task of iterating over a sequence of values, and all but one (`next()`) have a default implementation.
It's fine to keep methods together when they describe the same contract, but if you're unsure if callers need the independent capabilities, split your traits.

## Rules For Designing Traits 

Below are a couple of concrete tips around trait design.

- When you approach a problem, ask what your code needs a type to be able to do.
  Often, an existing trait already expresses that. Check the standard library
  and popular crates first. And sometimes a concrete type or an enum is enough.

- Write the code concretely first. If you find yourself copying similar
  implementations across different types, look for a shared contract. By then,
  you'll have concrete examples to test your abstraction against. And when you
  do need a new trait, give it a contract you can explain in a single sentence.

- Abstraction has a cost for readers. They may need to follow bounds and
  implementations across several files to understand a call. Sometimes that
  indirection hides details they shouldn't need to care about. Sometimes it
  hides an important detail they should.

- Trait-based abstractions in Rust often incur zero additional runtime overhead,
  but there is a compilation cost as well. The costs depend on how you use the trait. Generic
  code is usually monomorphized: the compiler generates code for the concrete
  types that use it. That permits static dispatch and inlining, but many
  instantiations can still increase compile time and binary size. For
  [dyn-compatible traits](/blog/dyn-compatibility/), dynamic dispatch through
  `dyn Trait` lets the same caller operate on different implementations, but
  introduces indirection and can limit inlining. Not every trait supports this:
  `FromIterator`, for example, is not dyn-compatible.

Keep these trade-offs in mind when you introduce a trait.
There is no free lunch.

## Think Beyond the Parts

Let's come back to our `collect()` once more.
So far, we've used the destination type to choose a collection.
But it can also determine control flow.
For example, we can decide to stop iterating on the first error or keep going and collect every result, including errors.

I first learned about this from Karol Kuczmarski's [Iteration patterns for Result & Option](http://xion.io/post/code/rust-iter-patterns.html), still one of my favorite Rust posts.

Here it is in action:

```rust
let input = ["10", "oops", "30"];

let every_result: Vec<Result<u32, _>> =
    input.iter().map(|s| s.parse()).collect();

let all_or_error: Result<Vec<u32>, _> =
    input.iter().map(|s| s.parse()).collect();
```

Note that in both cases, the iterator expressions are **identical**.
The only thing that changes is the destination type:

- `Vec<Result<u32, _>>` collects every parse result.
- `Result<Vec<u32>, _>` returns the first error and stops advancing the iterator immediately.

In the second case, `"30"` is never parsed.
If every parse succeeds, the second version returns `Ok` containing the vector of values.
This behavior comes from [the standard library's `FromIterator` implementation for `Result`](https://doc.rust-lang.org/std/result/enum.Result.html#impl-FromIterator%3CResult%3CA,+E%3E%3E-for-Result%3CV,+E%3E).
Here's a stub of that implementation:

```rust
impl<A, E, V> FromIterator<Result<A, E>> for Result<V, E>
where
    V: FromIterator<A>,
{
    // Implementation omitted.
}
```

What this says is:

> An iterator of `Result<A, E>` values can be collected into a `Result<V, E>`, as long as `V` can collect values of type `A`.

The `V: FromIterator<A>` bound means that `V` could be a `Vec<A>` or any other type that can collect those values.
`collect()` itself doesn't need to know any of this: it just calls the destination type's `FromIterator` implementation.

See how all of those pieces fit together?
That's the real payoff when you think in traits.
A single implementation can connect a type to an entire ecosystem of algorithms, adapters, and collections.

A few carefully crafted capabilities can combine in ways their authors never imagined. 
That makes the whole greater than the sum of its parts.
And that's just great API design.
