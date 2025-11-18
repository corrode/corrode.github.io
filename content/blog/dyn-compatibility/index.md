+++
title = "Fixing Dyn Compatibility Issues in Rust"
date = 2025-11-18
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
resources = [
"[The Rust Reference: Dyn Compatibility](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility)",
"[The Rust Reference: Trait Objects](https://doc.rust-lang.org/reference/types/trait-object.html)",
"[RFC 255: Object Safety](https://rust-lang.github.io/rfcs/0255-object-safety.html)",
"[RFC 817: Where Self Meets Sized](https://rust-lang.github.io/rfcs/0817-dyn-compatibility.html)"
]
+++

In Rust, not all traits can be used with `dyn Trait`. 

That is, you can't make "trait objects" from them.
This is called *dyn compatibility*, which means "a trait is not compatible with dynamic dispatch via `dyn`."

Let's figure out the problem and how to fix it!

**Note**: This concept used to be called "object safety" until Rust 1.84.0. If you're reading older resources, they mean the same thing.

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

fn main() {
    let button = Button { label: "Click me".to_string() };
    let widget: &dyn Widget = &button;  // Error!
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

### Fix #1: Use Generics Instead

One common way to fix the problem is to use generics instead of trait objects.
Generics resolve to concrete types *at compile time*, so the compiler learns about the size of `Self`.
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

### Fix #2: Opt Out Problem Methods with `where Self: Sized`

Another option is to keep using trait objects but change the problematic method to only work with concrete types.

```rust
trait Widget {
    fn draw(&self);
    
    // Only available when the concrete type is known
    fn duplicate(&self) -> Self where Self: Sized;
}
```

The above says "this method can only be called when `Self` has a known size at compile time", which is true for concrete types but not for trait objects.
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

### Fix #3: Return Boxed Trait Objects Instead of `Self`

In this case, we can change the return type of the problematic method to return a boxed trait object instead of `Self`.

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

### Fix #4: Split Into Two Traits

Sometimes the best solution is to separate the dyn-compatible methods from the problematic ones into different traits.

Maybe your code is silently trying to tell you that you are mixing up two different concepts and that they should be untangled. 

In general, prefer smaller, focused traits over large, monolithic ones.
Traits are not interfaces!

It's a bit of a silly example, but perhaps you have a `Widget` trait for drawing and a `Duplicatable` trait for duplication.

```rust
// This trait that can be used with dyn
trait Widget {
    fn draw(&self);
}

// Separate trait for duplication, which can't be used with dyn
trait Duplicatable: Widget {
    fn duplicate(&self) -> Self where Self: Sized;
}

struct Button {
    label: String,
}

impl Widget for Button {
    fn draw(&self) {
        println!("Button: {}", self.label);
    }
}

impl Duplicatable for Button {
    fn duplicate(&self) -> Self {
        Button { label: self.label.clone() }
    }
}

fn main() {
    let button = Button { label: "Click me".to_string() };
    
    // Use as trait object for drawing
    let widget: &dyn Widget = &button;
    widget.draw();  // ✅ Works
    
    // Use concrete type for duplication
    let button2 = button.duplicate();  // ✅ Works
}
```

## Understanding the Rules

A trait is **dyn compatible** if it follows these rules:

- No `Self: Sized` Supertrait, i.e. the trait itself must not require `Self: Sized`
- Methods Must Have a Receiver, e.g. `&self` or `&mut self`
- No Generic Type Parameters on Methods, e.g. `fn process<T>(&self, item: T);`
  The reason is that the vtable is a static struct created at compile time. It can't have infinite entries. Generic methods are **monomorphized** at compile time (one copy per type), but trait objects work at **runtime** when the type is erased.
- No `Self` in Method Parameters (Except Receiver), e.g. no `fn compare(&self, other: &Self);`
  That's because `other: &Self` means "the same type as `self`", but with trait objects, we only know both are "`dyn Comparable`". They could be different underlying types!
- No `Self` Return Type
  The compiler needs to know the size of the return value, but `Self` could be any size. With trait objects, the type is erased.
- No `impl Trait` in Return Position

That's quite a lot of exceptions, but they all boil down to the same core issue: **the compiler needs to know sizes and types at compile time, but with trait objects, that information is erased at runtime.**

To understand why that is so important, we have to look at how trait objects work under the hood.

### What is a Trait Object?

When you write `&dyn Trait`, you're creating a **trait object**.
It's a special kind of value that consists of two pointers (a "fat pointer"):

```
┌─────────────────┐
│  Data Pointer   │ ──→ points to actual data (String, i32, etc.)
├─────────────────┤
│ VTable Pointer  │ ──→ points to virtual method table
└─────────────────┘
```

As you can see, a trait object has:
1. A **data pointer** that points to the actual data (the concrete type implementing the trait)
2. A **vtable pointer** that points to a table of function pointers for the methods

The vtable is created at compile time and contains pointers to the methods for the specific type.
When you call a method on a trait object, Rust uses the vtable to look up the correct function to call based on the actual type of the data.

In order to create a vtable, the compiler needs to know:
- The size of the type (to allocate memory)
- The exact method signatures (to create function pointers)

If a trait has methods that return `Self` or have generic parameters, the compiler can't create a proper vtable because it doesn't know what `Self` is or how to handle generics at runtime.

That is the root cause of dyn compatibility issues.

## Summary

**Dyn compatibility** determines if a trait can be used with `dyn Trait`. The rules exist because:

1. Trait objects use dynamic dispatch via vtables
2. Vtables are static, compile-time structures, which hold method pointers
3. Type information is erased at runtime in order to allow polymorphism
4. The compiler must guarantee type safety at all times, even if it can't see the concrete type

Many standard library traits (Clone, Iterator, etc.) are also not dyn compatible, so don't worry.
As seen above, you can work around limitations with type erasure.




### When to use what

- Use **generics** when you know types at compile time and want maximum performance
- Use **trait objects** when you need runtime polymorphism or heterogeneous collections

Generics lead to larger binaries and longer compile times, but they are fast at runtime.
Trait objects lead to smaller binaries and faster compile times.They allow for maximum flexibility, but come with a small runtime cost due to dynamic dispatch.

### A Personal Note on Terminology

I personally don't like either of the terms "object safety" or "dyn compatibility" because they sound like some obscure technical jargon.
Certainly, "object safety" is misleading because Rust doesn't have "objects" in the traditional OOP sense because it lacks classes and inheritance. And it's not about "safety" either, because it's really about whether a trait can be used with dynamic dispatch.
"dyn compatibility" is better, but you have to know a lot of Rust jargon to understand what's going on. 
But to be honest, I also can't think of a better name that is both short and accurate.

### Historical Notes

- RFC 255: Introduced object safety (2014, before Rust 1.0)
- RFC 546: Removed implied `Sized` bound on traits
- RFC 428: Fixed edge cases in object safety
- RFC 817: Added `where Self: Sized` for fine-grained control
- Rust 1.72: GATs can be opted out with `where Self: Sized`
- Rust 1.84.0: Renamed "object safety" to "dyn compatibility"
