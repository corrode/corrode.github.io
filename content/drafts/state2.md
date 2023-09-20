+++
title = "Cars, Illegal State, and Rust"
date = 2023-09-13
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = []
+++

Cars have a lot software in them these days.
Did you know that a modern car has over [100 million lines of code](https://medium.com/next-level-german-engineering/porsche-future-of-code-526eb3de3bbe)?
That's more than a Boeing 787 Dreamliner, which has 14 million lines of code.

With so much software, it's no surprise that cars have bugs.
In fact, there are [a lot of bugs](https://www.wired.com/story/uber-self-driving-crash-arizona-ntsb-report/).

That's reassuring, given that [microprocessors are what actually cause your brakes to function](https://blog.passwork.pro/car-hacking/)

In this article, we'll see how we can use Rust's type system to model
the state of a car and prevent illegal states.

## The State of a Car

Let's take one of the most basic security features of a car: the door lock.

A car door can be in one of three states:

- **Locked**: The door is locked and cannot be opened from the inside or outside.
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
For example, we can lock an already locked door:

```rust
let mut door = Door { locked: true };
door.lock();
door.lock();
```

Or you might refactor the code and forget to check for the lock:

```rust
struct Door {
    locked: bool,
}

impl Door {
    fn open(&mut self) {
        println!("Opening door");
    }
}
```

...and what if you want to add support for child locks, in which an unlocked door cannot be opened from the inside?
You'd have to go through all the code and add a check for the new state.

A better approach would be the use of an enum:

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
            DoorState::Locked => {}
            DoorState::Unlocked => {
                println!("Opening door");
            }
        }
    }
}
```

Thanks to Rust's exhaustive pattern matching, we'll be reminded to handle the new state, `ChildLocked`, wherever necessary:

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
                if self.outer_handle.is_pulled() {
                    log::debug!("Opening door");
                }
            }
        }
    }
}
```

That works until you realize that you can still lock a door that's already locked:

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

As a kid, I loved playing Super Mario.

It's everything you could want in a game: intuitive gameplay, precise game
mechanics, and a lot of fun.
But what looked like a simple game on the surface was actually quite complex
under the hood. It's a masterpiece of game design and engineering.

## Game Mechanics

In the original Super Mario Bros, we can collect the following items:

- Coin
- Magic Mushroom
- Fire Flower
- Star
- 1-Up Mushroom

Interacting with these items, Mario can make the following transformations:

- Small Mario
- Super Mario
- Fire Mario
- Invincible Mario

## Glitches in Super Mario Bros

Turns out, managing all of the above transformations can be a difficult task
and so there are quite a few bugs in the original game.

**Did you know that you can you can die and complete a level simultaneously?**

- If Mario touches Bowser while he _also_ touches the axe to complete a level,
  Mario will die _and_ complete the level at the same time.
- If Mario does it with 0 lives, the game will play the
  "Thank you Mario! But our princess is in another castle!" cutscene
  and then show the "Game Over" screen.

There's a [long list of Super Mario glitches](https://www.mariowiki.com/List_of_Super_Mario_Bros._glitches), actually
and here's a [fun demo video](https://www.youtube.com/watch?v=5Tx2lJ4hYCc).

## State Is Hard!

Why didn't the original developers catch these bugs?
Well, it's hard to keep track of all the situations that can happen in a game.

Mario can be in one of 4 states, and there are 5 different items he can collect.
That's 20 different states to keep track of!

On top of that, there are different ways to interact with the environment:

- Being on the ground, in the air, inside water, or in a pipe.
- Getting hit by an enemy or falling into a pit.
- Completing a level by reaching the flagpole or touching the axe in a castle.
- ...

Phew, there's a of things going on. State is hard!
No wonder how some of these issues slipped through the cracks.

On top of that, the game was programmed in 6502 assembly, which isn't helping.

These days, we can make use of [an elegant weapon for a more civilized
age](https://www.youtube.com/watch?v=vQA5aLctA0I): Rust.

In this article, we'll see how we can use Rust's type system to model
the different states of Mario and the different items he can collect.
We'll see how we can use the type system to prevent illegal states from
happening in the first place.
No more Mario dying and completing a level at the same time!

## Prior Art

This article is inspired by a YouTube video titled [Rust Data Modelling WITHOUT CLASSES](https://www.youtube.com/watch?v=z-0-bbc80JM)
by [No Boilerplate](https://www.youtube.com/@NoBoilerplate).

In the video, the following code is presented (slightly modified):

```rust
#[derive(Debug)]
struct Mario {
    state: State,
}

impl Mario {
    fn new() -> Self {
        Self {
            state: State::Small,
        }
    }

    fn collect(&mut self, item: Item) {
        match (&self.state, item) {
            (State::Small, Item::Mushroom) => self.state = State::Super,
            (_, Item::Mushroom) => {} // No change, already big
            (_, Item::FireFlower) => self.state = State::Fire,
            (_, Item::Star) => self.state = State::Invincible,
            (_, Item::OneUp) => {} // No change, 1up!
        }
    }
}
```

It can be used like so:

```rust

fn main() {
    let mut mario = Mario::new();
    mario.collect(Item::Mushroom);
    assert_eq!(mario.state, State::Super);
    mario.collect(Item::FireFlower);
    assert_eq!(mario.state, State::Fire);
    mario.collect(Item::Mushroom);
    assert_eq!(mario.state, State::Fire);
    mario.collect(Item::Star);
    assert_eq!(mario.state, State::Invincible);
}
```

([Rust Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=8cb8999270467eefbda8d3d55d8d08f3))

## The Problem With This Code

The code is simple and elegant, but there is a flaw:
_Mario's actions aren't tied to his state._

With every action we want to perform, we have to check if Mario is in the
correct state to perform that action. This can lead to bugs.

```rust
impl Mario {
    fn shoot_fireball(&self) {
        if self.state == State::Fire {
            println!("Fireball!");
        }
    }
}
```

All of the actions that Mario can perform are accessible from any state!
We're running with scissors here.

```rust
let mut mario = Mario::new();
mario.collect(Item::Mushroom);
mario.shoot_fireball(); // Mario is small. Let's hope we check the state!
```

Wouldn't it be nice if we could only call `shoot_fireball` if Mario is in the
`Fire` state? Also, can we put the compiler to work and make sure that we
never perform any illegal actions even before we run the code?

I think you already know the answer...

## Make Illegal States Unrepresentable

We need to tie Mario's available actions to his current state.

This is where
[`PhantomData`](https://doc.rust-lang.org/stable/std/marker/struct.PhantomData.html) comes in handy. It allows us to associate generic type
parameters with structs without actually storing any data.

```rust
use std::marker::PhantomData;

// Each state is a marker type.
struct Small;
struct Super;
struct Fire;

#[derive(Debug)]
struct Mario<S> {
    state: PhantomData<S>,
}

impl Mario<Small> {
    // We always start as small Mario.
    fn new() -> Self {
        Self { state: PhantomData, invincible: false }
    }

    fn mushroom(self) -> Mario<Super> {
        Mario::<Super> { state: PhantomData }
    }

    // If you're Super Mario and find a Fire Flower,
    // but take damage before collecting it, you can still
    // collect it as small Mario to become Fire Mario!
    fn fire_flower(self) -> Mario<Fire> {
        Mario::<Fire> { state: PhantomData }
    }
}

impl Mario<Super> {
    fn fire_flower(self) -> Mario<Fire> {
        Mario::<Fire> { state: PhantomData }
    }
}

impl Mario<Fire> {
    fn shoot_fireball(&self) {
        println!("Fireball!");
    }
}

fn main() {
    let mario = Mario::<Small>::new();
    let mario = mario.mushroom();
    // mario.shoot_fireball(); // Compile error!
    let mario = mario.fire_flower();
    mario.shoot_fireball(); // Fireball!
}
```

Note how `invinicible` is not a state. This is because Mario can be
invincible in any state.

There's different ways to model being invincible.
The simplest way is to add a `bool` field to the `Mario` struct:

```rust
struct Mario<S> {
    state: PhantomData<S>,
    invincible: bool,
}
```

However, we'd have to manually reset `invincible` to `false` from the outside after a certain amount of time.

Another way is to add an `Instant` field to the `Mario` struct, which is set to
the current time plus the duration of invincibility:

```rust
struct Mario<S> {
    state: PhantomData<S>,
    invincible_until: Instant,
}

impl<S> Mario<S> {
    fn new() -> Self {
        Self {
            state: PhantomData,
            invincible_until: Instant::now(),
        }
    }

    fn invincible(self) -> Mario<S> {
        Mario::<S> {
            state: PhantomData,
            invincible_until: Instant::now() + Duration::from_secs(10),
        }
    }

    fn is_invincible(&self) -> bool {
        self.invincible_until > Instant::now()
    }
}
```

This way, we can check if Mario is invincible by calling `is_invincible`
without having to worry about resetting `invincible` to `false`.

## Conclusion

Maybe you didn't immediately think about Super Mario when we talk about
making illegal states unrepresentable. Turns out, it's a fun way to learn
about the concept.

Of course, no design is perfect.
The code might look unfamiliar to people without any experience with
type-driven design. On the other hand, this approach will help make your code
more robust and less error-prone.

As an exercise, try to implement the state transitions when Mario takes damage.
