+++
title = "The Typestate Pattern in Rust"
date = 2024-05-16
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = []
+++

Modern cars are essentially computers on wheels, containing a staggering amount of software. Did you know that a modern car has over [100 million lines of code](https://medium.com/next-level-german-engineering/porsche-future-of-code-526eb3de3bbe)? That's an order of magnitude more than the 14 million lines of code found in a Boeing 787 Dreamliner.

With so much software, it's no surprise that cars have bugs. In fact, there are [a lot of bugs](https://www.wired.com/story/uber-self-driving-crash-arizona-ntsb-report/), which is very reassuring given that [microprocessors are responsible for critical functions like braking](https://blog.passwork.pro/car-hacking/).

Now, I know nothing about car software, but at the end of the day, it's just software. And there are patterns and techniques that can be applied to make software more reliable and secure. One such pattern is the typestate pattern, which I'll be exploring in this article.

## The State of a Car

One of the most fundamental security features of a car is the door lock. A car door can be in one of two states:

- **Locked**: The door is locked and cannot be opened.
- **Unlocked**: The door is unlocked and can be opened from the inside or outside.

## Representing States in Rust

Consider the following scenario: if you pull the handle and the door is locked, it should not open. This logic, though simple, must be handled correctly in software, at least since all cars come with keyless entry systems by now. Suppose a car manufacturer decided to implement this logic in Rust (an in fact, a few might). How could they use Rust's type system to the fullest to prevent illegal states?

A naive implementation might look like this:

```rust
struct Door {
    locked: bool,
}

impl Door {
    fn open(&mut self) {
        if !self.locked {
            println!("Opening door");
        }
    }
}
```

This implementation is problematic because it allows for illegal states. For example, you can lock a car door that's already locked:

```rust
let mut door = Door { locked: true };
door.lock();
door.lock();
```

This may seem harmless, but it can lead to unexpected behavior, such as wear on the lock's internal components or unnecessary activation of the car's lights and horn.

A better approach would be to use an enum to represent the door's state:

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
    /// A passenger tries to open the door
    /// by pulling the handle or pushing a button.
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
}
```

Using Rust's exhaustive pattern matching ensures that all possible cases are
handled. We can't forget to handle the `Locked` state, as the code will not
compile if we do. This is a significant improvement over the previous
implementation.

## The Problem with Enums

While enums are great for modeling states, they have limitations:

- **Scalability**: As more states are added, all the code that uses the enum must be updated.
- **Composition**: Managing the state of a `Door` within a `Car` struct requires manual handling.
- **Invariants**: Enums don't enforce state invariants, allowing illegal transitions like locking an already locked door.

## The State Machine Pattern

A more robust solution is the [state machine pattern](https://en.wikipedia.org/wiki/State_pattern). A state machine consists of a set of states, events, and transitions. When an event occurs, the state machine transitions from one state to another.

Let's model the state of a car door as a state machine:

```rust
// TODO: Should I split this into two separate traits, `Openable` and `Lockable`?
trait DoorState {
    fn open(&self) -> Box<dyn DoorState>;
    fn lock(&self) -> Box<dyn DoorState>;
}

struct Locked;
struct Unlocked;
struct ChildLocked;

impl DoorState for Locked {
    fn open(&self) -> Box<dyn DoorState> {
        println!("Door is locked, can't open");
        Box::new(Locked)
    }

    fn lock(&self) -> Box<dyn DoorState> {
        println!("Door is already locked");
        Box::new(Locked)
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
}

impl DoorState for ChildLocked {
    fn open(&self) -> Box<dyn DoorState> {
        println!("Opening door from the outside only");
        Box::new(ChildLocked)
    }

    fn lock(&self) -> Box<dyn DoorState> {
        println!("Locking door");
        Box::new(Locked)
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
}
```

([Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=1490dd0c410160e0b88f0e4b307ae898))

The state machine pattern encapsulates the behavior associated with each state within that state's implementation, offering several advantages:

1. **Single Responsibility Principle**: Each state handles its own logic, making
   the code easier to understand and maintain.
2. **Open/Closed Principle**: Adding a new state or behavior is simple.
   Implementing a new state does not require modifying existing ones.
3. **Strong Type Guarantees**: Illegal states or transitions are managed at
   compile-time. The Rust compiler will produce an error if a required behavior
   for a state is not implemented.

However, this solution uses dynamic dispatch (`Box<dyn DoorState>`),
which means that the method calls are resolved at runtime.
In embedded systems or performance-critical applications, dynamic dispatch can
be forbidden due to its runtime overhead.

Here's a version with static dispatch:

```rust
trait DoorState {
    fn open(self) -> Self;
    fn lock(self) -> Self;
}

struct Locked;
struct Unlocked;
struct ChildLocked;

impl DoorState for Locked {
    fn open(self) -> Self {
        println!("Door is locked, can't open");
        Locked
    }

    fn lock(self) -> Self {
        println!("Door is already locked");
        Locked
    }
}

impl DoorState for Unlocked {
    fn open(self) -> Self {
        println!("Opening door");
        Unlocked
    }

    fn lock(self) -> Self {
        println!("Locking door");
        Locked
    }
}

impl DoorState for ChildLocked {
    fn open(self) -> Self {
        println!("Opening door from the outside only");
        ChildLocked
    }

    fn lock(self) -> Self {
        println!("Locking door");
        Locked
    }
}

// The Door struct is now generic over the state.
// This allows the state to be statically dispatched.
struct Door<S: DoorState> {
    state: S,
}

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
}

impl Door<Locked> {
    fn open(self) -> Door<Locked> {
        Door {
            state: self.state.open(),
        }
    }

    fn lock(self) -> Door<Locked> {
        Door {
            state: self.state.lock(),
        }
    }
}

impl Door<ChildLocked> {
    fn open(self) -> Door<ChildLocked> {
        Door {
            state: self.state.open(),
        }
    }

    fn lock(self) -> Door<Locked> {
        Door {
            state: self.state.lock(),
        }
    }
}
```

([Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=8b5b0b0b0b0b0b0b0b0b0b0b0b0b0b))


Here's how to use it:

```rust
let door = Door { state: Unlocked };
let door = door.lock();
// This will not compile
// Error: method not found in `Locked`
// A locked door cannot be opened by pulling the handle
let door = door.open(); 
```

And that's the typestate pattern in Rust!
If it compiles, it works. 

## Conclusion

As it turns out, Rust is not just good for systems programming but also for
ensuring your car’s software is robust and reliable.