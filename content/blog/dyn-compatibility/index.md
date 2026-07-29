+++
title = "Understanding Dyn Compatibility"
date = 2026-07-29
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = [
    { name = "Theodor-Alexandru Irimia", url = "https://github.com/tirimia" },
]
resources = [
"[The Rust Reference: Dyn Compatibility](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility)",
"[The Rust Reference: Trait Objects](https://doc.rust-lang.org/reference/types/trait-object.html)",
"[Rust error E0038: dyn compatibility](https://doc.rust-lang.org/error_codes/E0038.html)",
"[Two Ways To Do Dynamic Dispatch](https://www.youtube.com/watch?v=wU8hQvU8aKM) - Video by Logan Smith, which explains dyn dispatch from first principles"
]
+++


In Rust, some traits can't be used as trait objects with `dyn Trait`.

When a trait can't be used with dynamic dispatch, we say it's "not dyn compatible." [^object-safety]
This has an impact on how you can use these traits in your code. 

[^object-safety]: The concept used to be called "object safety" until Rust 1.84.0. If you're reading older resources, they mean the same thing. The name got changed because it was confusing.

    "Object safety" suggests that Rust has "objects" in the traditional OOP sense and that the term is about "safety", which is misleading.
    The new term "dyn compatibility" does a better job of saying that it's about whether a trait can be used with `dyn Trait` for dynamic dispatch, although I personally don't like either of the terms, but to be honest, I also can't think of a better name that is both short and accurate.
  
I think that's one are where the Rust compiler could print a more helpful error message.
  
Fixing the issue is mostly about tradeoffs between compile-time generics and runtime polymorphism and learning when each one fits.
Once you understand the concept, you'll know how to get around the issues by choosing a better design for your trait.

{% info(title="Quick Help", icon="crab") %}

If the compiler told you a trait is **"not dyn compatible"** your trait can't be used as `dyn Trait` because it has a method that can't go through dynamic dispatch, usually one that returns `Self`, takes no `self`, or is generic.

To fix it, pick one:

- add `where Self: Sized` to the offending method
- return `Box<dyn Trait>` instead of `Self`, or
- use generics instead of `&dyn Trait`
- split the trait in two

Continue reading to understand the tradeoffs between each approach.

{% end %}



## The Error Message

Here's an example with code that **won't compile**.

Say you have a trait `Widget` which has a method that returns a copy of itself:

```rust
trait Widget {
    fn draw(&self);
    fn duplicate(&self) -> Self;  // Returns a copy of itself
}
```

...and there's a button, which implements `Widget`:

```rust
struct Button {
    label: String,
}

impl Widget for Button {
    fn draw(&self) {
        // ...
    }
    
    fn duplicate(&self) -> Self {
        Button { label: self.label.clone() }
    }
}

fn show_widget(widget: &dyn Widget) {
    // This works
    widget.draw();

    // This produces an error because duplicate returns `Self`
    let copy = widget.duplicate();
    copy.draw();
}
```

If you tried to compile this code, you'd get an error like this:

```rust
error[E0038]: the trait `Widget` is not dyn compatible
  --> src/main.rs:20:25
   |
20 | fn show_widget(widget: &dyn Widget) {
   |                         ^^^^^^^^^^ `Widget` is not dyn compatible
   |
note: for a trait to be dyn compatible it needs to allow building a vtable
      for more information, visit <https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility>
  --> src/main.rs:3:28
   |
 1 | trait Widget {
   |       ------ this trait is not dyn compatible...
 2 |     fn draw(&self);
 3 |     fn duplicate(&self) -> Self;  // Returns a copy of itself
   |                            ^^^^ ...because method `duplicate` references the `Self` type in its return type
   = help: consider moving `duplicate` to another trait
   = help: only type `Button` implements `Widget`; consider using it directly instead.
```

That all sounds sounds pretty confusing.

- What does "not dyn compatible" mean?
- Shouldn't the `dyn` part take care of it?
- What's a "vtable", and why does the trait need to "allow building" one?
- What does it have to do with `Self`?

## What's going on?

When you use `&dyn Trait`, Rust creates a **trait object**.
Trait objects use **dynamic dispatch** to call methods at runtime.
Dynamic dispatch just means that the exact method to call is determined at runtime based on the actual type of the object.

For dynamic dispatch to work, the trait's dispatchable API must follow certain rules.

1. Dispatchable methods **must not** return `Self`.
2. Dispatchable methods **must have an allowed receiver** (`&self`, `&mut self`, `Box<Self>`, and a few related pointer forms). Plain static methods don't have one.
3. Dispatchable methods **must not** have generic type parameters.

These are simplifications: each method-level rule is really "...unless that method opts out with `where Self: Sized`", which we'll see in a moment. Traits also have a few item-level restrictions, such as no associated constants; we'll summarize the fuller list later. For now, the rough version is enough to build intuition.

In our example, we violate the first rule: the `duplicate` method returns `Self`, which means "the same type as the implementor of the trait".
When you use `&dyn Widget`, the concrete implementor is hidden behind the trait-object interface.
The vtable still points to the right concrete implementation, but the call site has no single concrete return type it can name for `duplicate`.
That's a problem, because the compiler needs to know the size of the return value at compile time, and `Self` could be **any size**.
It needs to know the size, because the returned value has to live *somewhere*: the caller sets aside exactly the right amount of space (usually on the stack) before the call even happens. With a `&dyn Widget`, the concrete type is erased from the caller's static type, so there's no single size the compiler could reserve for it.

It will become clearer once we look at some fixes.

## How To Fix It

Don't worry, we won't have to refactor all our code!
All fixes use the same `Widget` trait example.
There are multiple ways to make it dyn compatible.

We have a bunch of options:

1. Use generics instead
2. Opt out problematic methods with `where Self: Sized`
3. Return boxed trait objects instead of `Self`
4. Split into two traits

Each approach comes with different tradeoffs.
Depending on the kind of dyn-compatibility issue, one might fit better than the others, or you might combine a few.
Let's look at each of these in detail.

### Fix #1: Use Generics Instead

One common way to fix the problem is to use generics instead of trait objects.
Generics resolve to concrete types *at compile time*, so the compiler knows the size of `Self`.
Basically, the compiler will generate a separate copy of the function for each concrete type that implements the trait.
Then, at runtime, you no longer need to worry about any dynamic dispatch (which means "figuring out the type at runtime").
The compiler always knows which type it is dealing with, so it can pick the right method to call.

Our trait stays the same:

```rust
trait Widget {
    fn draw(&self);
    fn duplicate(&self) -> Self;
}
```

But now we change the function which uses the trait to use generics instead of `dyn`:

```rust
// Instead of: fn show_widget(widget: &dyn Widget)
// use generics:
fn show_widget<W: Widget>(widget: &W) {
    widget.draw();
    let copy = widget.duplicate();
    copy.draw();
}
```

Note how we changed the function signature to use a generic type parameter `W` that implements the `Widget` trait.
Here we tell Rust: "I have some type `W` that implements `Widget`, and I want to use it." and Rust will happily generate all the necessary code for each type used.

That's close to using `&dyn Widget`, but not quite the same.
The difference is that with generics, the compiler knows the concrete type at compile time, so it can handle `Self` correctly.
For instance, we might know that `W` is `Button` in this case, so `duplicate` returns a `Button`.
Now the confusion about what `Self` means is gone!

The downside is that you can't fully lean on dynamic dispatch anymore and that you might have to refactor a lot of code if you were using trait objects extensively before. Your binary size might also grow because of all the copies of the function that the compiler generates for each concrete type.

{% info(title="What's the benefit of fully leaning on dynamic dispatch?", icon="crab") %}

Fair question! Dynamic dispatch has a bunch of really nice properties:

- It's very flexible. You can swap out implementations at runtime, which is great for plugins or when you want to change behavior without recompiling.
- It allows for polymorphism. You can treat different types that implement the same trait uniformly, which can simplify code that needs to work with various types.
  You could technically do the same with generics, but sometimes you can't afford the increase in code size or compile times that come with monomorphization.
- It can lead to cleaner and more maintainable code in certain scenarios, especially when dealing with complex hierarchies of types and behaviors.
  For example, take a graphics rendering engine where you have different shapes (circles, squares, triangles) that all implement a `Drawable` trait.
  Using dynamic dispatch, you can store them all in a single collection and call `draw()`. If you were to try the same with generics, you'd end up with a lot of boilerplate code to handle each shape type separately.

{% end %}

### Fix #2: Opt Out Problematic Methods with `where Self: Sized`

Another option is to keep using trait objects but change the problematic method to only work with concrete types.

```rust
trait Widget {
    fn draw(&self);
    
    // Only available when the concrete type is known
    fn duplicate(&self) -> Self where Self: Sized;
}
```

This means "this method can only be called when `Self` has a known size at compile time", which is true for concrete types but not for trait objects.
It's more explicit, since you control how the trait can be used.
The catch is that it limits the trait further down the line: some methods won't be callable on every trait object, and changing the trait later becomes a breaking change.

You won't be able to call `duplicate` on `&dyn Widget`, but you can still call it on concrete types like `Button`.

```rust
fn main() {
    let button = Button { label: "Click me".to_string() };
    
    // Can use as trait object now!
    let widget: &dyn Widget = &button;
    widget.draw();  // ✅ Works
 
    // ❌ Can't call this on trait objects
    // widget.duplicate(); 
    
    // ✅ But duplicate still works on concrete types:
    let button2 = button.duplicate();
}
```

So you keep most of the flexibility of trait objects (unlike with generics), as long as you remember that some methods won't be available through `dyn Trait`.

### Fix #3: Return Boxed Trait Objects Instead of `Self`

We can change the return type of the problematic method to return a boxed trait object instead of `Self`.

This works because `Box<dyn Widget>` has a known size at compile time. It's a pointer to an object on the heap. It's actually a *fat pointer*: two words wide, or 16 bytes on a 64-bit system, because it also stores a pointer to the vtable; more on that later. What matters is that this size is fixed and known at compile time, unlike `Self`, which varies based on the concrete type.

```rust
trait Widget {
    fn draw(&self);
    fn duplicate(&self) -> Box<dyn Widget>;  // Returns trait object instead of Self
}
```

```rust
struct Button {
    label: String,
}

impl Widget for Button {
    fn draw(&self) {
        println!("Button: {}", self.label);
    }
    
    fn duplicate(&self) -> Box<dyn Widget> {
        Box::new(Button { label: self.label.clone() })
    }
}

fn main() {
    // Now we can use trait objects!
    let widgets: Vec<Box<dyn Widget>> = vec![
        Box::new(Button { label: "Click me".to_string() }),
        Box::new(Button { label: "Submit".to_string() }),
    ];
    
    for widget in &widgets {
        widget.draw();
        let copy = widget.duplicate();
        copy.draw();
    }
}
```

The downside is that `Box<dyn>` tends to be viral in your codebase. You'll end up writing `Box<dyn Widget>` more often than you'd like, which gets noisy.

On top of that, this fix only works for methods that return `Self`.
If your trait also has static methods or generic methods, you'll need to combine this approach with one of the other fixes.

### Fix #4: Split Into Two Traits

Sometimes the best solution is to separate the dyn-compatible methods from the problematic ones into different traits.

Maybe your code is silently trying to tell you that you are mixing up two different responsibilities and that they should be untangled. 

In general, prefer smaller, focused traits over large, monolithic ones.
Traits are not interfaces!
Instead, we lean on composition and focus on behavior rather than mangling multiple ideas into a single trait.

Here's a more realistic example: separating rendering from widget creation. Factory methods are often static (no `self` parameter), which makes them incompatible with `dyn`. So we split them off into a separate trait.

```rust
// This trait can be used with dyn
trait Widget {
    fn draw(&self);
}

// Separate trait for creating widgets. Can't be used with `dyn`
trait WidgetFactory {
    fn create(label: String) -> Self;  // No self parameter!
}

struct Button {
    label: String,
}

impl Widget for Button {
    fn draw(&self) {
        println!("Button: {}", self.label);
    }
}

impl WidgetFactory for Button {
    fn create(label: String) -> Self {
        Button { label }
    }
}

fn main() {
    // Use the factory to create widgets
    let button = Button::create("Click me".to_string());

    // Use as trait object for drawing
    let widget: &dyn Widget = &button;
    widget.draw();  // ✅ Works

    // Can't do this: let factory: &dyn WidgetFactory = ...
    // But that's fine - factories work at compile time
}
```

## What's Going On Under the Hood?

When you write `&dyn Trait`, you're creating a **trait object**.
It's a special kind of value that consists of two pointers (a "fat pointer"):

```
┌─────────────────┐
│  Data Pointer   │ --> points to actual data (String, i32, etc.)
├─────────────────┤
│ VTable Pointer  │ --> points to virtual method table
└─────────────────┘
```

As you can see, a trait object has:
1. A **data pointer** that points to the actual data (the concrete type implementing the trait)
2. A **vtable pointer** that points to a table of function pointers for the methods

The [vtable](https://en.wikipedia.org/wiki/Virtual_method_table) is created at compile time and contains pointers to the methods for the specific type.
It is a concept that is common in many programming languages that support dynamic dispatch, such as C++, C#, or D. 
When you call a method on a trait object, Rust uses the vtable to look up the correct function to call based on the actual type of the data.

For dynamic dispatch to be sound, the vtable-facing methods need stable, concrete function signatures:
- every dispatchable method needs a receiver that leads to the object and its vtable
- argument and return types must be expressible without knowing the hidden concrete `Self`
- the vtable must contain a finite set of function pointers, known at compile time

If a trait has dispatchable methods that return `Self` or have generic parameters, there is no single vtable entry with one concrete signature that can represent all possible calls.

That is the root cause of dyn compatibility issues.

A trait is **dyn compatible** if it follows [a list of rules](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility). 

<details>
<summary>
Click here for the full list.
</summary>

| Rule | Why? |
|------|------|
| All supertraits must also be dyn compatible | A `dyn Subtrait` also exposes the supertrait API, so those inherited methods must be dispatchable too |
| No `Self: Sized` supertrait | The trait object type `dyn Trait` is unsized, so the trait itself must not require `Self: Sized` |
| No associated constants | Associated constants are not entries in the method vtable |
| No generic associated types | The Reference currently forbids associated types with generics on dyn-compatible traits |
| Dispatchable methods must have an allowed receiver | Methods need a receiver: `&self`, `&mut self`, or pointer receivers like `Box<Self>`, `Rc<Self>`, `Arc<Self>`, or `Pin<P>` where `P` is one of those pointer forms. Static methods (no receiver) can't be dispatched through a trait object |
| No generic type parameters on dispatchable methods | The vtable is a finite structure created at compile time. Generic methods are monomorphized at compile time (one copy per concrete instantiation), but a trait object erases the concrete receiver type |
| No `Self` in dispatchable method parameters except the receiver | `other: &Self` means "the same concrete type as `self`", but with trait objects we only know both are `dyn Comparable`; they could hide different underlying types |
| No `Self` return type on dispatchable methods | The caller needs to know the return value's size and type, but `Self` could be any implementor |
| No opaque return type on dispatchable methods | `async fn` and return-position `impl Trait` hide a concrete return type that must be known statically |
| Non-dispatchable methods must opt out | A method that violates the dispatch rules can still live on the trait if it has `where Self: Sized`, making it unavailable through `dyn Trait` |
</details>

The rules boil down to the same core issue:
**the `dyn Trait` interface must have a finite, statically-known shape even though the concrete implementor behind it is hidden.**

{% info(title="A Modern Gotcha: `async fn` in Traits", icon="crab") %}

Since [Rust 1.75](https://blog.rust-lang.org/2023/12/28/Rust-1.75.0/), you can write `async fn` directly in a trait.
But there's a catch: a trait with an `async fn` is **not dyn compatible**.

An `async fn` desugars to a regular method that returns `impl Future<...>`, a hidden return-position `impl Trait`.
The type is called "opaque", because we don't know what it is, and the compiler doesn't expose it to us.
Opaque return types aren't dispatchable (which means we can't put them in a vtable of functions), so the trait can't be used behind `dyn`.

If you need dynamic dispatch with async methods today, you have a few options:

- Box the future yourself and return `Pin<Box<dyn Future<Output = ...>>>`.
- Use the [`async-trait`](https://crates.io/crates/async-trait) crate, which does that boxing for you.
- Use the [`dynosaur`](https://crates.io/crates/dynosaur) crate, which generates a dyn-compatible wrapper for traits with `async fn`.

{% end %}

## Summary

**Dyn compatibility** determines if a trait can be used with `dyn Trait`. The rules exist because:

1. Trait objects use dynamic dispatch via vtables
2. Vtables are static, compile-time structures, which hold method pointers
3. Type information is erased at runtime to allow polymorphism
4. The compiler must guarantee type safety at all times, even if it can't see the concrete type

If your trait is not dyn compatible, don't worry! Many standard library traits (`Clone`, `Default`, etc.) are also not dyn compatible.
As we've seen, there are ways to work around these limitations with type erasure, generics, or more fine-grained traits. 

Which fix to reach for depends on what your trait needs and what you're willing to give up:

| Fix | Reach for it when... | The tradeoff |
|-----|----------------------|--------------|
| **#1 Generics** (`<W: Widget>`) | You don't actually need trait objects (the concrete type is known at each call site) and you won't mix different types in one collection | Static dispatch only; monomorphization can grow code size and compile times and generic parameters need to be passed around in your API |
| **#2 `where Self: Sized`** | You want to keep using `dyn Widget`, and the problematic method only ever needs to be called on concrete types | That method isn't callable through `dyn`; tightening the bound later is a breaking change |
| **#3 Return `Box<dyn Widget>`** | The method returns `Self` and you really need it through a trait object (e.g. a heterogeneous `Vec<Box<dyn Widget>>`) | A heap allocation per call, and `Box<dyn>` tends to spread through your API |
| **#4 Split into two traits** | The trait mixes dispatchable behavior with non-dispatchable bits, like static factory methods | More traits to keep track of, though that separation often helps |
| **`async-trait` / `dynosaur`** | Your trait has `async fn`s and you need to call them through `dyn` | Wrapper types and usually boxed futures/extra indirection until native `dyn` async improves |

In practice you'll often combine these. For example, splitting a trait and boxing a return value.

### Historical Notes

I find it interesting to see how dyn compatibility evolved over time in Rust.
If you do, too, here are some resources to dig deeper:

- 2014-09-22: [RFC 255](https://rust-lang.github.io/rfcs/0255-object-safety.html) - Introduced object safety (2014, before Rust 1.0)
- 2014-11-03: [Issue #428](https://github.com/rust-lang/rfcs/issues/428) - Object-safety and static methods
- 2015-01-03: [RFC 546](https://rust-lang.github.io/rfcs/0546-Self-not-sized-by-default.html) - Removed implied `Sized` bound on traits
- 2023-08-24: [Rust 1.72](https://blog.rust-lang.org/2023/08/24/Rust-1.72.0.html) - GATs can be opted out with `where Self: Sized`
- 2023-12-28: [Rust 1.75.0](https://blog.rust-lang.org/2023/12/28/Rust-1.75.0/) - Stabilized `async fn` and return-position `impl Trait` in traits (though such traits still aren't dyn compatible)
- 2025-01-09: [Rust 1.84.0](https://blog.rust-lang.org/2025/01/09/Rust-1.84.0/) - The docs had moved from "object safety" to "dyn compatibility" around this release cycle; the [tracking issue](https://github.com/rust-lang/rust/issues/130852#issuecomment-2947417189) notes that the rename unfortunately missed the release notes.

The lang team also wants a "practical path" to call `async fn`s through `dyn Trait` natively. It's on the [2026 project goals](https://github.com/rust-lang/rfcs/blob/master/text/3935-Project-Goals-2026.md), so the async gotcha above should ease over time.
