+++
title = "Understanding Dyn Compatibility"
date = 2025-11-20
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
]
+++

In Rust, not all traits can be used as trait objects with `dyn Trait`.

When a trait can't be used with dynamic dispatch, we say it's "not dyn compatible."

This has an impact on how you can use these traits in your code. 
Dyn compatibility is based on a set of rules that determine whether a trait can be turned into a trait object.

Once you understand why these rules exist, they stop feeling like compiler errors and start revealing design choices.
You'll see the tradeoffs between compile-time generics and runtime polymorphism, and 
get a solid grasp of when each approach fits your problem.
Knowing your options lets you write more deliberate, flexible Rust.

Let's figure out why this happens and how to fix it!

{% info(title="Dyn Compatibility and Object Safety", icon="crab") %}

This concept used to be called "object safety" until Rust 1.84.0.
If you're reading older resources, they mean the same thing.

The name got changed because it was confusing.

"Object safety" suggests that Rust has "objects" in the traditional OOP sense and that the term is about "safety", which is misleading.
The new term "dyn compatibility" does a better job at reflecting that it's about whether a trait can be used with `dyn Trait` for dynamic dispatch. [^personal_note]

[^personal_note]: I personally don't like either of the terms "object safety" or "dyn compatibility" because they sound like some obscure technical jargon.
Certainly, "object safety" is misleading because Rust doesn't have "objects" in the traditional OOP sense -- it lacks classes and inheritance. And it's not about "safety" either, since it's really about whether a trait can be used with dynamic dispatch.
"dyn compatibility" is better, but you have to know a lot of Rust jargon to understand what's going on. 
But to be honest, I also can't think of a better name that is both short and accurate.


{% end %}

## The Problem

Here's an example with code that **won't compile**:

```rust
trait Widget {
    fn draw(&self);
    fn duplicate(&self) -> Self;  // Returns a copy of itself
}

struct Button {
    label: String,
}

impl Widget for Button {
    fn draw(&self) {
        println!("Button: {}", self.label);
    }
    
    fn duplicate(&self) -> Self {
        Button { label: self.label.clone() }
    }
}

fn show_widget(widget: &dyn Widget) {
    widget.draw();
    let copy = widget.duplicate();  // ❌ Error here
    copy.draw();
}
```

If you tried to compile this code, you'd get an error like this:

```
error[E0038]: the trait `Widget` cannot be made into an object
  --> src/main.rs:18:17
   |
18 |     let widget: &dyn Widget = &button;
   |                 ^^^^^^^^^^^ `Widget` is not dyn compatible
   |
   = note: method `duplicate` references the `Self` type in its return type
```

That might sound pretty confusing in the beginning.

- What does "cannot be made into an object" even mean?
- Shouldn't the `dyn` part take care of that?
- What does it have to do with `Self`?

You've just encountered **dyn compatibility**.

## What's going on?

When you use `&dyn Trait`, Rust creates a **trait object**.
Trait objects use **dynamic dispatch** to call methods at runtime.
Dynamic dispatch means that the exact method to call is determined at runtime based on the actual type of the object.

However, for dynamic dispatch to work, you must follow certain rules. 

1. The trait must not have any methods that return `Self`.
2. The trait must not have any static methods (methods without a `self` parameter).
3. The trait must not have any generic type parameters on its methods.

In our example, the `duplicate` method returns `Self`, which means "the same type as the implementor of the trait".
When you use `&dyn Widget`, the compiler doesn't know what `Self` is at runtime because it could be any type that implements `Widget`.
That's a problem, because the compiler needs to know the size of the return type at compile time, and `Self` could be **any size**.

It will become clearer once we look at some fixes.


## How To Fix It

Don't worry, we won't have to refactor all our code!
All fixes use the same `Widget` trait example.
There are multiple ways to make it dyn compatible.

We have a bunch of options:

1. Use Generics Instead
2. Opt Out Problem Methods with `where Self: Sized`
3. Return Boxed Trait Objects Instead of `Self`
4. Split Into Two Traits

Let's look at each of these in detail.


### Fix #1: Use Generics Instead

One common way to fix the problem is to use generics instead of trait objects.
Generics resolve to concrete types *at compile time*, so the compiler knows the size of `Self`.
Basically, the compiler will generate a separate version of the function for each type that implements the trait. Then at runtime, you no longer need to worry about any dynamic dispatch (which means "figuring out the type at runtime").
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
// Use generics:
fn show_widget<W: Widget>(widget: &W) {
    widget.draw();
    let copy = widget.duplicate();
    copy.draw();
}
```

Note how we changed the function signature to use a generic type parameter `W` that implements the `Widget` trait.
Here we tell Rust: "I have some type `W` that implements `Widget`, and I want to use it." and Rust will happily generate all the necessary code for each type used.

That is similar but slightly different from using `&dyn Widget`.
The difference is that with generics, the compiler knows the concrete type at compile time, so it can handle `Self` correctly.
For instance, we might know that `W` is `Button` in this case, so `duplicate` returns a `Button`.
Now the confusion about what `Self` means is gone!

The downside is that you can't fully lean on dynamic dispatch anymore [^why-dynamic-dispatch] and that you might have to refactor a lot of code if you were using trait objects extensively before.

[^why-dynamic-dispatch]: **"What's the benefit of fully leaning on dynamic dispatch"**, you ask? Fair question!

    Dynamic dispatch has a bunch of really nice properties:

    - It's very flexible. You can swap out implementations at runtime, which is great for plugins or when you want to change behavior without recompiling.
    - It allows for polymorphism. You can treat different types that implement the same trait uniformly, which can simplify code that needs to work with various types.
      You could technically do the same with generics, but as I mentioned sometimes you can't afford the increase in code size or compile times that come with monomorphization.
    - It can lead to cleaner and more maintainable code in certain scenarios, especially when dealing with complex hierarchies of types and behaviors.
      For exmaple, take a graphics rendering engine where you have different shapes (circles, squares, triangles) that all implement a `Drawable` trait.
      Using dynamic dispatch, you can store them all in a single collection and call `draw()`. If you were to try the same with generics, you'd end up with a lot of boilerplate code to handle each shape type separately.

### Fix #2: Opt Out Problem Methods with `where Self: Sized`

Another option is to keep using trait objects but change the problematic method to only work with concrete types.

```rust
trait Widget {
    fn draw(&self);
    
    // Only available when the concrete type is known
    fn duplicate(&self) -> Self where Self: Sized;
}
```

This means "this method can only be called when `Self` has a known size at compile time", which is true for concrete types but not for trait objects.
It is more explicit because you're in control over how the trait can be used.
The downside is that this limits the usability of trait further down the line because some methods won't be callable on all trait objects and changing the trait will cause breaking changes.

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

This means you don't lose all the flexibility of trait objects (in contrast to generics), but you have to be aware that some methods won't be available when using `dyn Trait`.

### Fix #3: Return Boxed Trait Objects Instead of `Self`

We can change the return type of the problematic method to return a boxed trait object instead of `Self`.

This works because `Box<dyn Widget>` has a known size at compile time -- it's a pointer to an object on the heap! Pointers have a known size (usually 8 bytes on 64-bit systems), 
so the compiler knows how much space to allocate for it, unlike `Self` which varies based on the concrete type.

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

The downside is that `Box<dyn>` is often viral in your codebase: 
you'll end up writing out the concrete type as `Box<dyn Widget>` more often than you'd like, which can lead to noisy code.

### Fix #4: Split Into Two Traits

Sometimes the best solution is to separate the dyn-compatible methods from the problematic ones into different traits.

Maybe your code is silently trying to tell you that you are mixing up two different concepts and that they should be untangled. 

In general, prefer smaller, focused traits over large, monolithic ones.
Traits are not interfaces!
Instead, we lean on composition and focus on behavior instead of mangling multiple responsibilities into a single trait.

Here's a more realistic example: separating rendering from widget creation. Factory methods are often static (no `self` parameter), which makes them incompatible with `dyn`. So we split them into separate traits.

```rust
// This trait can be used with dyn
trait Widget {
    fn draw(&self);
}

// Separate trait for creating widgets - can't be used with dyn
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

But in order to create a vtable, the compiler needs to know:
- The size of the type (to allocate memory)
- The exact method signatures (to create function pointers)

If a trait has methods that return `Self` or have generic parameters, the compiler can't create a proper vtable because it doesn't know what `Self` is or how to handle generics at runtime.

That is the root cause of dyn compatibility issues.

In summary, a trait is **dyn compatible** if it follows [these rules](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility):

| Rule | Why? |
|------|------|
| No `Self: Sized` supertrait | The trait itself must not require `Self: Sized`, otherwise it can never be used as a trait object |
| Methods must have a receiver | All methods need `&self`, `&mut self`, or similar. Static methods (no receiver) can't be called through a vtable |
| No generic type parameters on methods | The vtable is a static struct created at compile time and can't have infinite entries. Generic methods are monomorphized at compile time (one copy per type), but trait objects work at runtime when the type is erased |
| No `Self` in method parameters (except receiver) | `other: &Self` means "the same type as `self`", but with trait objects, we only know both are "`dyn Comparable`". They could be different underlying types! |
| No `Self` return type | The compiler needs to know the size of the return value, but `Self` could be any size. With trait objects, the type is erased |
| No `impl Trait` in return position | Similar to `Self` - the actual type needs to be known at compile time, but it's erased with trait objects |

That's quite a lot of rules, but they all boil down to the same core issue:
**the compiler needs to know sizes and types at compile time, but with trait objects, that information is erased at runtime.**

## Summary

**Dyn compatibility** determines if a trait can be used with `dyn Trait`. The rules exist because:

1. Trait objects use dynamic dispatch via vtables
2. Vtables are static, compile-time structures, which hold method pointers
3. Type information is erased at runtime in order to allow polymorphism
4. The compiler must guarantee type safety at all times, even if it can't see the concrete type

If your trait is not dyn compatible, don't worry! Many standard library traits (`Clone`, `Iterator`, etc.) are also not dyn compatible.
As we've seen, there are ways to work around these limitations with type erasure, generics, or more fine-grained traits. 

### Historical Notes

I find it interesting to see how dyn compatibility evolved over time in Rust.
If you do, too, here are some resources to dig deeper:

- 2014-09-22: [RFC 255](https://rust-lang.github.io/rfcs/0255-object-safety.html) - Introduced object safety (2014, before Rust 1.0)
- 2014-11-03: [Issue #428](https://github.com/rust-lang/rfcs/issues/428) - Object-safety and static methods
- 2015-01-03: [RFC 546](https://rust-lang.github.io/rfcs/0546-Self-not-sized-by-default.html) - Removed implied `Sized` bound on traits
- 2023-08-24: [Rust 1.72](https://blog.rust-lang.org/2023/08/24/Rust-1.72.0.html) - GATs can be opted out with `where Self: Sized`
- 2025-01-09: [Rust 1.84.0](https://blog.rust-lang.org/2025/01/09/Rust-1.84.0/) - Silently renamed "object safety" to "dyn compatibility" (tragically, not mentioned in the release notes!)
