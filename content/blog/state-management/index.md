+++
title = "Managing State in Rust"
date = 2024-05-20
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = [
    { name = "Dorota (dcz)", url = "https://dorotac.eu/" },
    { name = "Thomas Zahner", url = "https://github.com/thomas-zahner" },
]
resources = [
    "[Pretty State Machine Patterns in Rust &mdash; Ana Hobden](https://hoverbear.org/blog/rust-state-machine-pattern/)"
]
+++

Cars have a lot software in them these days.

Did you know that a modern car has over [100 million lines of
code](https://medium.com/next-level-german-engineering/porsche-future-of-code-526eb3de3bbe)?
That's an order of magnitude more than the [6.5 million lines of code found in a
Boeing 787
Dreamliner](https://web.archive.org/web/20100209084931/http://news.discovery.com/tech/toyota-recall-software-code.html).

With so much software, it's no surprise that cars have bugs. [A lot of
bugs](https://www.wired.com/story/uber-self-driving-crash-arizona-ntsb-report/).
That's very reassuring given that [microprocessors are responsible for
critical functions like braking](https://blog.passwork.pro/car-hacking/)
nowadays.

Even seemingly simple things can be quite complex when you consider all the edge cases and interactions with other systems. These interactions are often modeled as states and transitions within software, making state management one of the most common and vital operations in any application.

When state handling goes wrong, it can cause serious issues.
Let's look at the different ways to manage state in Rust by means of a software
component for managing car doors to drive this point home (I'm really good at
puns).

## The State of a Car Door

Somewhat naively, one could think that a car door can be in one of two states:
locked or unlocked.

That's not really true, though! For example, some car doors have a "child lock"
feature that allows the door to be opened from the outside but not from the inside.

There are many other states to consider. What should happen when you try to
lock the car while the windows are down or the engine is running?
Can you open the door from the outside if the car is moving?

Modeling this complexity requires careful consideration of the
states, transitions, and invariants that govern the behavior of a door.

Without proper handling, we could end up in an illegal state, leading to
unexpected behavior or even accidents: a passenger might be locked inside
or you can't open the door from the outside in an emergency.

For now, let's keep it simple and consider the two basic states: locked and unlocked.
Here's a state diagram to visualize the possible states and transitions:

![Door state diagram](door.svg)


## Basic Door State Implementation

Suppose a car manufacturer decided to implement the door logic in Rust (a great
choice, I dare say). A naive implementation could look like this:

```rust
struct Door {
    /// Whether the door is locked or unlocked.
    locked: bool,
    /// ...
}

impl Door {
    /// A passenger tries to open the door
    /// by pulling the handle or pushing a button.
    fn open(&mut self) {
        if !self.locked {
            println!("Opening door");
        }
    }

    /// Locks the door.
    fn lock(&mut self) {
        self.locked = true;
    }

    /// Unlocks the door so it can be opened.
    fn unlock(&mut self) {
        self.locked = false;
    }
}
```

This works, but the implementation is problematic because we might refactor the
code and forget to keep the check for the door's state before opening it.
This is a common issue with mutable state:

- It's easy to forget to check the state before performing an action.
  The state only gets represented as a value, not a type.
- It's hard to reason about the code because there are no clearly defined transitions
  between states; the logic is spread out and imperative.

## Using Enums And Pattern Matching to Model State

A slightly better approach would be to use an enum to represent the door's state:

```rust
/// Represents the state a door is in.
enum DoorState {
    Locked,
    Unlocked,
}

struct Door {
    state: DoorState,
}

impl Door {
    fn open(&mut self) {
        match self.state {
            DoorState::Locked => {
                println!("Door is locked");
            }
            DoorState::Unlocked => {
                println!("Opening door");
            }
        }
    }

    fn lock(&mut self) {
        self.state = DoorState::Locked;
    }

    fn unlock(&mut self) {
        self.state = DoorState::Unlocked;
    }
}
```

- The **advantage** is that we can't forget to handle the `Locked` state, as the
  code will not compile if we do. That's because Rust's exhaustive pattern
  matching ensures that all possible cases get handled; a significant
  improvement over the previous implementation. An enum also serves as a concise
  way to enumerate (hence the name) all possible states the door can be in.
- The **disadvantage** is that enums don't enforce state invariants, which means
  that illegal transitions (like locking an already locked door) are still
  possible.

{% info(headline="What is a State Invariant?") %}

A state invariant is a condition that must always hold true for a given state in a system. In the context of a car door, a state invariant ensures that certain transitions between states are valid and others are not. For example, a car door cannot be locked if it is already in a locked state, and it cannot be opened if it is already open. These rules help maintain the integrity of the state transitions, preventing illegal or illogical actions.

{% end %}

As a result, the following code compiles and runs without any issues:

```rust
let mut door = Door { state: DoorState::Locked };
door.lock();
door.lock();
```

It may seem harmless, but can lead to unexpected behavior, such as wear on
the lock's internal components or unnecessary activation of the car's lights and
horn.

What if it could prevent a call to `lock` on a locked door?
And what if you weren't able to call `open` on a locked door in the first place?
This way, you wouldn't have to worry about forgetting to check the state before
performing an action. You could refactor fearlessly, knowing that the compiler
has your back.

Could the compiler help us avoid such issues? There is a way!


## Using Traits to Build a State Machine

The typestate pattern uses the type system to ensure correct state transitions
at compile time. Here’s how to implement it in Rust:

```rust
trait DoorState {
    fn open(&self) -> Box<dyn DoorState>;
    fn lock(&self) -> Box<dyn DoorState>;
    fn unlock(&self) -> Box<dyn DoorState>;
}

struct Locked;
struct Unlocked;

impl DoorState for Locked {
    fn open(&self) -> Box<dyn DoorState> {
        println!("Door is locked, can't open");
        Box::new(Locked)
    }

    fn lock(&self) -> Box<dyn DoorState> {
        println!("Door is already locked");
        Box::new(Locked)
    }

    fn unlock(&self) -> Box<dyn DoorState> {
        println!("Unlocking door");
        Box::new(Unlocked)
    }
}

impl DoorState for Unlocked {
    fn open(&self) -> Box<dyn DoorState> {
        println!("Opening door");
        Box::new(Unlocked)
    }

    fn lock(&self) -> Box<dyn DoorState> {
        println!("Locking door");
        Box::new(Locked)
    }

    fn unlock(&self) -> Box<dyn DoorState> {
        println!("Door is already unlocked");
        Box::new(Unlocked)
    }
}

struct Door {
    state: Box<dyn DoorState>,
}

impl Door {
    fn new() -> Self {
        Door {
            state: Box::new(Unlocked),
        }
    }

    fn open(&mut self) {
        self.state = self.state.open();
    }

    fn lock(&mut self) {
        self.state = self.state.lock();
    }

    fn unlock(&mut self) {
        self.state = self.state.unlock();
    }
}
```

([Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=d79c8789d0222f215b6d5fa4b43f0691))

The state machine pattern encapsulates the behavior associated with each state within that state's implementation, offering several advantages:

- Illegal states or transitions are pevented at compile-time. The Rust
  compiler will produce an error if a required behavior for a state is not
  implemented. This is because the **state is represented as a type, not just a
  value**, which allows the compiler to provide way stronger guarantees about
  the code's correctness.
- Adding a new state is simple and does not require modifying existing ones. (To
  be fair, adding a new method on the trait requires updating all states,
  violating the open/closed principle.)
- However, this solution makes use of dynamic dispatch (via `Box<dyn
  DoorState>`), which means the method calls get resolved at runtime. In
  embedded systems or performance-critical applications, dynamic dispatch can be
  prohibited because of its runtime overhead.

## Typestate Pattern with Static Dispatch

Here's a version with static dispatch:

```rust
/// A marker trait for the door's state.
/// This gets implemented by the concrete state types.
trait DoorState {}

// Define the possible states of the door
struct Locked;
struct Unlocked;
// You can add more states here, like:
// struct ChildLocked; 

// Implement the DoorState trait for each state
impl DoorState for Locked {}
impl DoorState for Unlocked {}

// Define methods for the Locked state
impl Locked {
    fn unlock(self) -> Unlocked {
        println!("Unlocking door");
        Unlocked
    }

    fn status(&self) {
        println!("The door is locked");
    }
}

// Define methods for the Unlocked state
impl Unlocked {
    fn open(self) -> Self {
        println!("Opening door");
        self
    }

    fn lock(self) -> Locked {
        println!("Locking door");
        Locked
    }

    fn status(&self) {
        println!("The door is unlocked");
    }
}

// Define a Door struct that is generic over its state
struct Door<S: DoorState> {
    state: S,
}

// Implement methods for a Door in the Unlocked state
impl Door<Unlocked> {
    fn open(self) -> Door<Unlocked> {
        Door {
            state: self.state.open(),
        }
    }

    fn lock(self) -> Door<Locked> {
        Door {
            state: self.state.lock(),
        }
    }

    fn status(&self) {
        self.state.status();
    }
}

// Implement methods for a Door in the Locked state
impl Door<Locked> {
    fn unlock(self) -> Door<Unlocked> {
        Door {
            state: self.state.unlock(),
        }
    }

    fn status(&self) {
        self.state.status();
    }
}

fn main() {
    // Start with a door in the Unlocked state
    let door = Door { state: Unlocked };
    door.status(); // The door is unlocked

    // Lock the door, transitioning it to the Locked state
    let door = door.lock();
    door.status(); // The door is locked

    // The following would result in a compile-time error:
    // no method named `lock` found for struct `Door<Locked>`
    // This way, you can't accidentally lock a door twice
    // door.lock();

    // Unlock the door, transitioning it back to the Unlocked state
    let door = door.unlock();
    door.status(); // The door is unlocked
}
```

([Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=8c64b914e88d6d1188eb869a7e3b7b86))

`Door<Locked>` and `Door<Unlocked>` are two different types, which are recognized as distinct by all parts of the type system.

- Guarantees valid states and transitions at compile time, no runtime overhead from dynamic dispatch.
- Makes the `impl` blocks easier to read, because they are broken down by state.
- Can be verbose and still requires updating all states when adding a new method to the trait.

## Conclusion

As we have seen, there are several ways to manage state in Rust, each with its
own trade-offs. I tend to prefer the typestate pattern with static dispatch
for critical applications, as it provides the strongest guarantees about the
code's correctness at compile time. For less critical applications, using enums
and pattern matching can be a good balance between safety and simplicity.

Here's a quick summary of the different state management approaches in Rust:

1. **Naive Implementation**:
    - **Pros**: Simple, easy to understand.
    - **Cons**: Allows illegal states and transitions, harder to maintain as complexity grows.

2. **Enum-Based Implementation**:
    - **Pros**: Ensures all states are handled, prevents illegal transitions.
    - **Cons**: Less scalable, requires manual handling of state transitions, enums don't enforce invariants.

3. **State Machine Pattern**:
    - **Pros**: Encapsulates state-specific behavior, adheres to the Single Responsibility Principle, easy to extend with new states or behaviors.
    - **Cons**: More complex, uses dynamic dispatch which might be unsuitable for performance-critical applications.

4. **Typestate Pattern with Static Dispatch**:
    - **Pros**: Ensures compile-time guarantees for valid states and transitions, no runtime overhead from dynamic dispatch.
    - **Cons**: Can be verbose, adding new actions requires updating all states, losing some open/closed principle benefits.
