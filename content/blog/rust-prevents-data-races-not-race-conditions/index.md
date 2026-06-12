+++
title = "Rust Prevents Data Races, Not Race Conditions"
date = 2026-06-12
draft = false
template = "article.html"
aliases = ["/blog/rust-prevents-data-races-not-all-race-conditions/"]
[extra]
series = "Rust Insights"
hero = "hero.svg"
hero_classes = "compact"
credits = [
    "Designed by <a href='https://www.magnific.com'>Magnific</a>"
]
resources = [
    "[The Rustonomicon: Data Races and Race Conditions](https://doc.rust-lang.org/nomicon/races.html): the canonical definition this post is built on",
    "[Migrating from Go to Rust](/learn/migration-guides/go-to-rust/): where the footnote that started this post lives",
    "[Bugs Rust Won't Catch](/blog/bugs-rust-wont-catch/): more on where Rust's safety guarantees end",
    "[Rust Atomics and Locks](https://mara.nl/atomics/) by Mara Bos: the best deep dive on the topic",
]
+++

Safe Rust eliminates all data races. What it does **not** do is prevent race conditions in the broader sense: deadlocks, livelocks, and logic bugs in your synchronization.

What's the difference?

These two terms get used interchangeably all the time, even by experienced developers, so it's worth writing down exactly what Rust promises and what it does not.

## What Is a Data Race?

To quote the [Rustonomicon](https://doc.rust-lang.org/nomicon/races.html):

> Safe Rust guarantees an absence of data races, which are defined as:
> - two or more threads concurrently accessing a location of memory
> - one or more of them is a write
> - one or more of them is unsynchronized

All three conditions have to hold at once. If every access is a read, there's no data race. If the accesses are synchronized (say, behind a lock), there's no data race. A data race is specifically *unsynchronized* concurrent access where at least one side writes.

This matters because a data race is [Undefined Behavior](https://doc.rust-lang.org/reference/behavior-considered-undefined.html)!
A data race does not mean you might read a "stale" value.
It means the compiler is allowed to do anything like tear a write in half and reorder it.

And you can't wave this away as a harmless race that happens to work out. As Raph Levien notes in [With undefined behavior, anything is possible](https://raphlinus.github.io/programming/rust/2018/08/17/undefined-behavior.html):

> It used to be thought that data races could be classified into "benign" and dangerous categories, but research strongly suggests that the former category doesn't exist.

In other words, every data race is a real bug!
And because it's Undefined Behavior, the symptom can show up far away from the cause and much later,
in the form of a corrupted value, a crash, or a security hole that only appears under heavy load.

For example, here are two threads incrementing the same counter:

```rust
use std::thread;

fn main() {
    let mut counter = 0;

    thread::scope(|s| {
        for _ in 0..2 {
            s.spawn(|| {
                counter += 1; // unsynchronized write to shared memory
            });
        }
    });
}
```

In many languages, the equivalent compiles and runs, and two threads writing to `counter` at the same time can corrupt it. The result depends on timing, so the bug may not show up until the code runs under load.

In Rust, it doesn't compile at all:

```rust
error[E0499]: cannot borrow `counter` as mutable more than once at a time
  --> ex1_data_race.rs:8:21
   |
 8 |             s.spawn(|| {
   |             -       ^^ `counter` was mutably borrowed here
   |                        in the previous iteration of the loop
 9 |                 counter += 1;
   |                 ------- borrows occur due to use of `counter` in closure
```

The borrow checker stops you before the program can exist. Two threads both want a mutable reference to `counter`, and Rust's core rule is that you can never have two mutable references to the same data at the same time. The data race is impossible because the *aliasing* it requires is impossible.

This is the point the Nomicon makes:

> Data races are prevented _mostly_ through Rust's ownership system alone: it's impossible to alias a mutable reference, so it's impossible to perform a data race.

{% info(title="Key takeaways") %}

- A data race is a specific thing: concurrent access, at least one write, no synchronization. All three at once.
- A data race is Undefined Behavior, not just a wrong answer.
- In purely safe Rust, **data races are impossible**, because they require aliasing a mutable reference, which the borrow checker forbids.

{% end %}

## How Rust Lets You Share State Safely

So how *do* you increment a counter from two threads correctly? You make the access synchronized, which removes the third condition from the data race definition. Wrap the value in a [`Mutex`](https://doc.rust-lang.org/std/sync/struct.Mutex.html), which lets only one thread touch it at a time:

```rust
use std::sync::Mutex;
use std::thread;

fn main() {
    let counter = Mutex::new(0);

    thread::scope(|s| {
        for _ in 0..2 {
            s.spawn(|| {
                *counter.lock().unwrap() += 1;
            });
        }
    });

    println!("{}", counter.into_inner().unwrap());
}
```

This compiles, and it **always** prints `2`.

The compiler enforces this through two marker traits, [`Send`](https://doc.rust-lang.org/std/marker/trait.Send.html) and [`Sync`](https://doc.rust-lang.org/std/marker/trait.Sync.html). Roughly: `Send` means a value can be moved to another thread, and `Sync` means it can be shared between threads by reference.

A plain `i32` can't be mutated through a shared reference, and a mutable reference can't be copied across threads. To share and mutate it, you need a type that provides interior mutability while remaining thread-safe (`Sync`), which is exactly what `Mutex<i32>` does.

Try to share something that *isn't* `Sync`, like an [`Rc<T>`](https://doc.rust-lang.org/std/rc/struct.Rc.html) or a [`RefCell<T>`](https://doc.rust-lang.org/std/cell/struct.RefCell.html), and you get a compile error.

(Here the threads can't outlive `counter`, so they borrow it directly. If they needed to outlive the scope, say with `thread::spawn`, you'd wrap it in an [`Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html) to share ownership: `Arc<Mutex<T>>` is the workhorse for that.)

That's the whole idea. Rust pushes many concurrency-safety checks from runtime into the type system.

{% info(title="Key takeaways") %}

- Synchronized access is not a data race, so it's allowed.
- A `Mutex` is the standard way to share mutable state across threads (an `Arc<Mutex<T>>` when threads outlive their spawning scope).
- The `Send` and `Sync` traits are how the compiler decides what's safe to move or share between threads. Non-thread-safe types won't compile in a multi-threaded context.

{% end %}

## Race Conditions Are Still Possible

So far we've made data races impossible. But a data race is only one kind of concurrency bug.
The broader category is a *race condition*: any bug where the result depends on the timing or interleaving of threads. Rust does not protect you from those.

In the following example, the code moves money out of a shared bank account.
That sounds quite scary, but we make sure to lock the `Mutex` on every access, so there is no data race anywhere in it.

```rust
use std::sync::Mutex;
use std::thread;

fn main() {
    // A shared account with $100 in it
    let balance = Mutex::new(100);

    thread::scope(|s| {
        for _ in 0..2 {
            s.spawn(|| {
                // Is there enough money?
                let can_withdraw = *balance.lock().unwrap() >= 100;
                // ...

                // withdraw the money, with a fresh, separate lock.
                if can_withdraw {
                    *balance.lock().unwrap() -= 100;
                }
            });
        }
    });

    println!("final balance: {}", balance.into_inner().unwrap());
}
```

One possible output is:

```
final balance: -100
```

but the output varies per run. 

Both threads locked the mutex and checked the balance before, so how is that final balance negative? 

There's a subtle issue: both threads correctly locked the mutex, but they released the lock before they acted on the result of the check. The threads didn't hold the lock for the entire time. 
So both threads can check the balance interleaved, seeing $100 before either thread has actually executed the withdrawal, leading both to decide they are cleared to proceed.
*Then* both went ahead and withdrew. The account went negative.

Every individual access was synchronized, so the borrow checker is perfectly happy. The bug is that the *check* and the *act* are two separate critical sections. Between them, the world can change. This is a **race condition** (specifically a [TOCTOU](/blog/pitfalls-of-safe-rust/#protect-against-time-of-check-to-time-of-use-toctou), time-of-check-to-time-of-use bug), and no type system can catch it for you, because the correctness depends on what you intended the locking to *mean*.

Once you understand this, the fix is simply to make the check and the act one atomic operation, holding the lock across both:

```rust
let mut balance = balance.lock().unwrap();
if *balance >= 100 {
    *balance -= 100;
}
```

You might think that this code is identical to the original, but it's not.
`lock()` returns a [`MutexGuard`](https://doc.rust-lang.org/std/sync/struct.MutexGuard.html), and here we keep it in the `balance` binding instead of dropping it right away. The lock stays held for as long as that guard is alive, which (like any other value in Rust) means until the end of its scope. So the check and the withdrawal now happen inside one critical section, and no other thread can squeeze in between them. When `balance` goes out of scope, its `Drop` implementation releases the lock automatically.

In the original code, each `*balance.lock().unwrap()` produced a temporary guard that was dropped immediately at the end of that statement, so the lock was released the instant each access finished, leaving a gap for a race condition. 

The compiler can't know which behavior you wanted. As the Nomicon puts it:

> It is considered "safe" for Rust to get deadlocked or do something nonsensical with incorrect synchronization.

{% info(title="Key takeaways") %}

- A **race condition** is a logic bug where the outcome depends on timing or thread interleaving.
- You can have a race condition with zero data races. The withdrawal code locks correctly everywhere and still corrupts its own state.
- Holding a lock per-access is not enough. **The critical section has to cover the whole logical operation**, or the invariant can break in the gap.

{% end %}

## Deadlocks Also Compile Just Fine

If incorrect locking is "safe," then so is locking that never finishes. The simplest example: lock the same mutex twice on one thread. Rust's standard `Mutex` is not reentrant, so the second `lock()` waits for a guard that will never be released.

```rust
use std::sync::Mutex;

fn main() {
    let data = Mutex::new(0);

    let _first = data.lock().unwrap();
    println!("got the first lock");

    // std's Mutex is not reentrant: this second lock waits
    // forever for a guard that will never be dropped.
    let _second = data.lock().unwrap();
    println!("got the second lock"); // never reached
}
```

This compiles without a single warning. Running it:

```
got the first lock
[hangs forever]
```

It prints the first line and then waits indefinitely. The borrow checker has nothing to say, because nothing here is unsafe in the memory sense. A deadlocked program isn't reading bad memory; it's just not making progress.

{% info(title="Why isn't `Mutex` reentrant in the first place?") %}

A reentrant mutex would let you lock it again while you already hold it. The trouble is that Rust's `Mutex::lock` hands you a `&mut T` to the protected data. If re-locking were allowed, you could call `lock()` a second time and get a *second* `&mut T` to the same value while the first is still live, which is exactly the aliasing the borrow checker exists to prevent.

So a reentrant mutex in Rust can only safely hand out a shared `&T`, not `&mut T`. That's much less useful, since you usually want a `Mutex` precisely to *mutate* the value inside. (There might also be a historical reason: `std`'s `Mutex` started life as a thin wrapper over OS primitives, and some of those aren't reentrant either.)

If you actually need reentrancy, [`parking_lot::ReentrantMutex`](https://docs.rs/parking_lot/latest/parking_lot/type.ReentrantMutex.html) provides it, and it gives out `&T` only. You pair it with `Cell` or `RefCell` for the actual mutation. See [this forum thread](https://users.rust-lang.org/t/reentrant-mutexes-in-rust/35653) for more info.

{% end %}

Real deadlocks are usually subtler than this. The textbook version is two threads that grab two locks in opposite orders, each waiting on the lock the other holds. But the general problem is that **liveness** (the program keeps making progress) is not something Rust's safety guarantees cover. Safety is about not doing the wrong thing; it says nothing about eventually doing the right thing.

{% info(title="Key takeaways") %}

- A **deadlock** is a race condition where threads wait on each other (or themselves) forever.
- `std::sync::Mutex` is not reentrant. Locking it twice on the same thread deadlocks.
- Rust guarantees memory safety, not liveness. A program that hangs is still a "safe" program as far as the compiler is concerned.

{% end %}

## Atomics Are Not a Magic Bullet Either

You might think the bank-account bug was really about `Mutex`: drop the lock, reach for lock-free atomics, and the problem goes away.
It doesn't. The check-then-act trap has nothing to do with locks. It's about composing operations, and atomics compose just as badly.

Atomics are synchronized by definition, so each *individual* operation is data-race-free. But "each operation is atomic" is not the same as "my *sequence* of operations is atomic", which is exactly the gap we just saw with the mutex.

Here four threads each do 100,000 increments, but the increment is split into a separate `load` and `store`:

```rust
use std::sync::atomic::{AtomicU64, Ordering};
use std::thread;

fn main() {
    let counter = AtomicU64::new(0);

    thread::scope(|s| {
        for _ in 0..4 {
            s.spawn(|| {
                for _ in 0..100_000 {
                    // Two independent atomic operations are not atomic together! 
                    let current = counter.load(Ordering::SeqCst);
                    counter.store(current + 1, Ordering::SeqCst);
                }
            });
        }
    });

    println!("expected: 400000");
    println!("got:      {}", counter.into_inner());
}
```

Two example runs with two different (wrong) answers:

```
expected: 400000
got:      305352
```

```
expected: 400000
got:      168582
```

Every `load` and every `store` was a properly synchronized atomic operation.
No data race occurred.
But two threads can both `load` the same value, both add one, and both `store` it back, and one of the increments vanishes. It's the bank account again: the gap this time sits *between* two atomic operations instead of between two locked sections. This is a [lost update](https://en.wikipedia.org/wiki/Concurrency_control), which is, once again, a race condition. [^fun_fact]

[^fun_fact]: Fun fact: the count indicates how many increments were lost,i.e., the total number of individual increments that vanished because threads interleaved, read a stale value, and overwrote each other's progress. So in the first run, 94,648 increments were lost, and in the second run, 231,418 were lost; that's a percentage of 23.66% and 57.85%, respectively, which is a huge difference just from the timing of how the threads interleaved.

Notice that we're using `SeqCst`, the strongest memory ordering Rust provides. The bug still occurs because the problem isn't memory ordering; it's that the increment is split into two separate operations.

The fix is to collapse the two steps into a single indivisible operation. With a lock, that meant holding the guard across both. With atomics, it means a single read-modify-write operation, [`fetch_add`](https://doc.rust-lang.org/std/sync/atomic/struct.AtomicU64.html#method.fetch_add), which does the load-add-store in one step:

```rust
counter.fetch_add(1, Ordering::SeqCst);
```

With that one change, the program prints `400000` every time.

This is the same check-then-act trap as the bank account, with no lock in sight; the problem was never about `Mutex`.

{% info(title="Key takeaways") %}

- Atomicity has a *scope*. The hardware guarantees the individual operation is
  atomic; making your logical operation atomic is still your job.
- Atomic operations are individually data-race-free, but composing several of
  them is not automatically atomic. `load` then `store` is two operations, and
  another thread can slip in between them.
- The fix mirrors the lock case: make the whole logical operation indivisible.
  Reach for `fetch_add` and friends instead of a separate load and store.

{% end %}

## So What Does Rust Actually Guarantee? 

Safe Rust eliminates data races by design. A program with a data race does not compile. It's a stronger guarantee than what runtime detectors like Go's `-race` or C/C++'s ThreadSanitizer give you, because those only catch races that *actually execute* during a test run.

Safe Rust does not prevent race conditions in general. Deadlocks, livelocks, lost updates, and check-then-act bugs all compile cleanly and can still produce wrong answers or hang.[^overlap]

[^overlap]: In the context of this article, I treat "data race" and "race condition" as two separate things, which is a useful simplification but not the full picture. The two concepts overlap heavily (many race conditions are caused by data races), yet neither is contained in the other: you can have a race condition with no data race (the bank-balance example above locks every access correctly and still loses money). Under some definitions, you can even construct examples where a data race exists but no observable program behavior depends on it (two threads racing to set an "account was touched" flag that nothing depends on). I recommend reading John Regehr post titled [Race Condition vs. Data Race](https://blog.regehr.org/archives/490).

Geo-ant, writing up a [comparison of common C++ bugs against Rust](https://geo-ant.github.io/blog/2022/common-cpp-errors-vs-rust/), sums up the whole distinction in one line:

> Rust does prevent data races and on the other hand you can still deadlock all you want.

The reason this distinction matters, and not just pedantically, is that it tells you where to spend your attention. You can stop worrying about torn reads and forgotten locks corrupting memory; the compiler has that. What's left is the hard part of concurrency: making sure your critical sections cover your invariants, that your lock ordering is consistent, and that your logical operations are as atomic as you think they are.

Rust holds an enormous amount for you, and what remains is the part that lives in your *intent*, which no type system can read.

If you want to go deeper on the concurrency side of this, read [Rust Atomics and Locks](https://mara.nl/atomics/) by Mara Bos. It's free online.

{% info(title="Want to get concurrency right in your Rust codebase?", icon="crab") %}

I offer Rust consulting, from code reviews and audits to training your team on the patterns the compiler won't enforce for you, including the concurrency traps in this post.
[Get in touch](/#contact) to learn more.

{% end %}
