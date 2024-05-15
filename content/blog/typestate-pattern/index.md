+++
title = "The Typestate Pattern in Rust"
date = 2024-05-16
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = []
+++

Cars have a lot software in them these days.
Did you know that a modern car has over [100 million lines of code](https://medium.com/next-level-german-engineering/porsche-future-of-code-526eb3de3bbe)?
That's an order of magnitude more than a Boeing 787 Dreamliner, which has 14 million lines of code.

With so much software, it's no surprise that cars have bugs.
In fact, there are [a lot of bugs](https://www.wired.com/story/uber-self-driving-crash-arizona-ntsb-report/).

That's reassuring, given that [microprocessors are what actually cause your brakes to function](https://blog.passwork.pro/car-hacking/)

In this article, we'll see how we can use Rust's type system to model
the state of a car and prevent illegal states.

As a disclaimer, I have no idea how car electronics actually work.
This article is exclusively about using Rust's type system to model states and prevent illegal states.

## The State of a Car

Let's take one of the most basic security features of a car: the door lock.

A car door can be in one of two states:

- **Locked**: The door is locked and cannot be opened.
- **Unlocked**: The door is unlocked and can be opened from the inside or outside.

## Representing States in Rust

If you pull the handle and the door is locked, it should not open.
It sounds almost foolish, but every modern car has to handle this logic
in software thanks to keyless entry.

Let's hypothetically assume that [a car manufacturer decided to implement this logic in Rust](https://medium.com/volvo-cars-engineering/why-volvo-thinks-you-should-have-rust-in-your-car-4320bd639e09), how would they use Rust's type system to prevent illegal states?

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

This implementation is problematic because it allows for illegal states.
For example, we can lock a car door that's already locked:

```rust
let mut door = Door { locked: true };
door.lock();
door.lock();
```

This is probably a no-op, but it could also lead to unexpected behavior.
The pins inside the lock cylinder are made of soft metal like brass, and repeated use can wear them down.
Also, the lights might flash, and the horn might honk, which is annoying.

What's worse is that you might refactor the code and forget to check for the lock:

```rust
struct Door {
    locked: bool,
}

impl Door {
    fn open(&mut self) {
        println!("Opening door!");
    }
}
```

Starting to think about safety, a better approach would be the use of an enum:

```rust
enum DoorState {
    Locked,
    Unlocked,
}

struct Door {
    door_state: DoorState,
    // ...
}

impl Door {
    fn open(&mut self) {
        match self.door_state {
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

Thanks to Rust's exhaustive pattern matching, we'll be reminded to handle 
all possible cases.

```rust
enum DoorState {
    Locked,
    Unlocked,
    ChildLocked,
}

struct Door {
    door_state: DoorState,
    outer_handle: Handle,
    inner_handle: Handle,
}

impl Door {
    fn open(&mut self) {
        match self.door_state {
            DoorState::Locked => {
                log::debug!("Door is locked");
            }
            DoorState::Unlocked => {
                log::debug!("Opening door");
            }
            DoorState::ChildLocked => {
                // Only open from the outside
                if self.outer_handle.is_pulled() {
                    log::debug!("Opening door");
                }
            }
        }
    }
}
```

That works until you realize that you can *still* lock a door that's already locked:

```rust
enum DoorState {
    Locked,
    Unlocked,
    ChildLocked,
}

struct Door {
    door_state: DoorState,
    outer_handle: Handle,
    inner_handle: Handle,
}

impl Door {
    fn lock(&mut self) {
        match self.door_state {
            DoorState::Locked => {
                log::debug!("Door is already locked");
            }
            DoorState::Unlocked => {
                log::debug!("Locking door");
            }
            DoorState::ChildLocked => {
                log::debug!("Locking door");
            }
        }
    }
}
```

## The Problem with Enums

Enums are great for modeling states, but they have a few problems:

- They don't scale well. As you add more states, you have to update all the
  code that uses the enum.
- They don't compose well. If you have a `Car` struct that contains a `Door`
  struct, you have to manually handle the state of the door in the `Car` struct.
- They don't enforce invariants. For example, you can lock a door that's already locked.

## The State Machine Pattern

A better approach would be to use the [state machine pattern](https://en.wikipedia.org/wiki/State_pattern).

A state machine is a mathematical model of computation.
It consists of a set of states, a set of events, and a set of transitions.
When an event occurs, the state machine transitions from one state to another.

Let's model the state of a car door as a state machine:

![Car Door State Machine](https://raw.githubusercontent.com/pretzelhammer/rust-blog/master/images/car_door_state_machine.png)

```rust
trait DoorState {
    fn open(&self) -> Box<dyn DoorState>;
    fn lock(&self) -> Box<dyn DoorState>;
}

struct Locked;
struct Unlocked;
struct ChildLocked;

impl DoorState for Locked {
    fn open(&self) -> Box<dyn DoorState> {
        debug!("Door is locked, can't open");
        Box::new(Locked)
    }

    fn lock(&self) -> Box<dyn DoorState> {
        debug!("Door is already locked");
        Box::new(Locked)
    }
}

impl DoorState for Unlocked {
    fn open(&self) -> Box<dyn DoorState> {
        debug!("Opening door");
        Box::new(Unlocked)
    }

    fn lock(&self) -> Box<dyn DoorState> {
        debug!("Locking door");
        Box::new(Locked)
    }
}

impl DoorState for ChildLocked {
    fn open(&self) -> Box<dyn DoorState> {
        debug!("Opening door from the outside only");
        Box::new(ChildLocked)
    }

    fn lock(&self) -> Box<dyn DoorState> {
        debug!("Locking door");
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

The state machine pattern allows you to encapsulate the behavior associated with a particular state within that state's implementation. This leads to several advantages:

1. Single Responsibility Principle: Each state handles its own logic, making the code easier to understand and maintain.
2. Open/Closed Principle: Adding a new state or behavior becomes easier. We just need to implement a new state without modifying the existing ones.
3. Strong Type Guarantees: Illegal states or transitions are handled at compile-time. If you forget to implement a behavior for a state, the Rust compiler will give an error.

The solution has one wrinkle: dynamic dispatch (`Box<dyn DoorState>`).  
Here's a version that uses static dispatch:

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
        debug!("Door is locked, can't open");
        Locked
    }

    fn lock(self) -> Self {
        debug!("Door is already locked");
        Locked
    }
}

impl DoorState for Unlocked {
    fn open(self) -> Self {
        debug!("Opening door");
        Unlocked
    }

    fn lock(self) -> Self {
        debug!("Locking door");
        Locked
    }
}

impl DoorState for ChildLocked {
    fn open(self) -> Self {
        debug!("Opening door from the outside only");
        ChildLocked
    }

    fn lock(self) -> Self {
        debug!("Locking door");
        Locked
    }
}

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

([Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=8b5b0b0b0b0b0b0b0b0b0b0b0b0b0b0b))

Turns out, Rust is actually good for your car.
