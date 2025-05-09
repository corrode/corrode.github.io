+++
title = "Sharp Edges In The Rust Standard Library"
date = 2025-05-09
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

The [Rust standard library](https://doc.rust-lang.org/std/), affectionately called `std`, is exceptionally well-designed, but that doesn't mean it's perfect.
More experienced Rust developers tend to navigate around some of its sharper parts, but I haven't seen these parts explicitly listed anywhere.

In this article, I want to highlight the areas in `std` that I personally avoid to raise awareness.
Keep in mind that I'm opinionated, so take this list with a grain of salt. 

## Threading

Rust's threading library is quite solid.
That said, managing threads can be a bit of a footgun.
In particular, forgetting to join a thread can have some unexpected side effects.

```rust
use std::thread;
use std::time::Duration;

struct Resource;

impl Drop for Resource {
    fn drop(&mut self) {
        println!("CRITICAL CLEANUP: Resource dropped");
    }
}

fn main() {
    let handle = thread::spawn(|| {
        let resource = Resource;
        // Simulate work
        thread::sleep(Duration::from_millis(100));
        // Thread ends, resource should be dropped
    });
    
    // Main thread exits immediately
    // Uncomment to fix:
    // handle.join().unwrap();
    
    println!("Main thread exiting");
}
```

In the above scenario, cleanup tasks (such as flushing caches, closing files) might not get executed.
So, even if you do nothing with the handle, it is still a best practice to `join()` it.
For more details on the topic, check out matklad's article: ["Join Your Threads"](https://matklad.github.io/2019/08/23/join-your-threads.html).

In fact, there was a proposal to make [`std::thread::JoinHandle`](https://doc.rust-lang.org/std/thread/struct.JoinHandle.html) be `#[must_use]`, but it was ultimately [declined](https://github.com/rust-lang/rust/pull/48830) because it would produce too many warnings.

[This comment summarized it pretty well](https://github.com/rust-lang/rust/pull/48830#issuecomment-371649213):

> I'd say the key issue here is that thread::spawn is the easiest way of spawning threads, but not the best one for casual use. Manually calling .join().unwrap() is a chore and easy to forget, which makes thread::spawn a potential footgun.

For new code, I recommend using [`thread::scope`](https://doc.rust-lang.org/std/thread/fn.scope.html) instead, which is a much better API in every conceivable way.
The documentation addresses the above issue directly:

> Unlike non-scoped threads, scoped threads can borrow non-`'static` data, as the scope guarantees **all threads will be joined at the end of the scope**.
> All threads spawned within the scope that **haven't been manually joined will be automatically joined** before this function returns.

Alternatively, you can use a thread pool library or [rayon](https://github.com/rayon-rs/rayon), in case you have an iterator you want to parallelize to many threads.

## `std::collections::LinkedList`

Implementing a linked list in Rust is [not easy](https://rust-unofficial.github.io/too-many-lists/).
That's because Rust's ownership model is detrimental to self-referential data structures. 
Some people might not know that the standard library ships with an implementation of a linked list at [`std::collections::LinkedList`](https://doc.rust-lang.org/std/collections/struct.LinkedList.html).

In all those years, I never felt the urge to use it. 
It might even be the least-used collection type in the standard library overall.

One reason might be that for all ordinary use cases, a `Vec` is sufficient and straightforward to use.
Vectors also have better cache locality and performance characteristics: all items are stored in contiguous memory, which is much better for fast memory access.
On the other side, elements in a linked list can be scattered all over the heap.
If you want to learn more, you can read this paper titled ["RIP Linked List - Empirical Study to Discourage You from Using Linked Lists Any Further"](https://arxiv.org/pdf/2306.06942), which contains some benchmarks.

You might be wondering why linked lists get used at all.
They have their place as a very specialized data structure that is only really helpful in some very low-level environments like a kernel. The Linux kernel uses a lot of linked lists, for example. The reason is that they are very efficient for inserting and deleting elements at arbitrary positions, which is great when you write things like a kernel scheduler.

As for normal, everyday code, just use a `Vec`.
Even [the documentation of `LinkedList`](https://doc.rust-lang.org/nightly/std/collections/struct.LinkedList.html) itself agrees:

> NOTE: It is almost always better to use `Vec` or `VecDeque` because array-based
> containers are generally faster, more memory efficient, and make better use of
> CPU cache.

I believe the LinkedList should not have been included in the standard library in the first place.

There are some surprising papercuts in the API; for instance, [`LinkedList::remove`](https://doc.rust-lang.org/std/collections/struct.LinkedList.html#method.remove) is still a nightly-only feature[^ll-remove]: 

[^ll-remove]: Perhaps this is a little surprising if you mostly use vectors, but removing an element from a list is an `O(n)` operation.

```rust
use std::collections::LinkedList;

fn main() {
    let mut list = LinkedList::from([1,2,3]);
    dbg!(list);
    
    // This is still unstable!
    // https://github.com/rust-lang/rust/issues/69210
    // The operation should compute in O(n) time.
    // Panics if out of range...
    // list.remove(0);
}
```

Even if you wanted a linked list, it would probably not be `std::collections::LinkedList`:

- It doesn't support O(1) splice, O(1) node erasure, or O(1) node insertion - only O(1) operations at the list ends
- It has all the disadvantages of a doubly-linked list but none of its advantages
- Custom implementations are often needed anyway. For example, many real-world use cases require an [intrusive linked list](https://www.data-structures-in-practice.com/intrusive-linked-lists/) implementation, not provided by `std`.
  An intrusive list is what the [Linux kernel provides](https://elixir.bootlin.com/linux/v6.14.5/source/include/linux/list.h)
  and even Rust for Linux has [its own implementation](https://rust-for-linux.github.io/docs/rust/src/kernel/linked_list.rs.html) of an intrusive list.
- Arena-based linked lists are often needed for better performance.

There is a [longer discussion in the Rust forum](https://internals.rust-lang.org/t/whats-the-status-of-std-linkedlist-maybe-deprecate-in-rust-2018/8068).

Better implementations exist that provide more of the missing operations expected from a proper linked list implementation:

- [contain-rs/linked-list](https://github.com/contain-rs/linked-list) 
- [intrusive-collections](https://github.com/Amanieu/intrusive-rs) 

## `std::collections::BTreeMap`

That one's a bit controversial.

Rust has two hash map implementations in the standard library:
`BTreeMap`, which guarantees insertion ordering, while `HashMap` is unordered, but more commonly used. 
For a long time, a "performance trick" was to use `BTreeMap` if you needed a faster hash map implementation.
Nowadays, this is no longer the case.
That's because `HashMap` has improved significantly in performance and is now the default choice for most use cases.
One reason is that the implementation of `HashMap` has [changed to use a "siphash" algorithm](https://doc.rust-lang.org/book/ch08-03-hash-maps.html#hashing-functions) and is now [based on Google's SwissTable](https://doc.rust-lang.org/std/collections/struct.HashMap.html).
The combination of these changes has made `HashMap` much more performant than before, so there is no good reason to use `BTreeMap` anymore, other than the ordering guarantee.

In ["Smolderingly fast b-trees"](https://www.scattered-thoughts.net/writing/smolderingly-fast-btrees/), Jamie Brandon compares the performance of Rust's `BTreeMap` and `HashMap`. Here are my key takeaways:

- When comparing performance, btrees were found to be significantly slower than hashmaps in most scenarios, especially for lookups.
  In the worst case with random-ish strings that share common prefixes, btrees performed dramatically worse.
- One more insight was that hashmaps benefit more from speculative execution between multiple lookups, while btrees don't.
- btrees have performance "cliffs" when comparisons get more expensive and touch more memory
- For space usage, the author estimates that btrees would use >60% more memory than hashmaps for random keys.

I'd argue that a normal HashMap is fast enough nowadays.
If the hash map is your bottleneck, you should probably look at your algorithm.

If you need anything faster than that, there are plenty of external crates like [indexmap](https://github.com/indexmap-rs/indexmap) crate for insertion-order preservation and [dashmap](https://github.com/xacrimon/dashmap) for concurrent access.

## `std::path::Path`

I think `Path` does a decent job of abstracting away the underlying file system.
One thing I always disliked was that `Path::join` returns a `PathBuf` instead of a `Result<PathBuf, Error>`.
I mentioned in my ['Pitfalls of Safe Rust'](/blog/pitfalls-of-safe-rust/#surprising-behavior-of-path-join-with-absolute-paths) article
that `Path::join` joining a relative path with an absolute path results in the absolute path being returned.

```rust
use std::path::Path;

fn main() {
    let relative_path = Path::new("relative/path");
    let absolute_path = Path::new("/absolute/path");

    // This will return "/absolute/path"
    let result = relative_path.join(absolute_path);
    assert_eq!(result, absolute_path); 
}
```

I think that's pretty counterintuitive and a potential source of bugs. 
On top of that, many programs assume paths are UTF-8 encoded and frequently convert them to `str`.
That's always a fun dance:

```rust
use std::path::Path;

fn main() {
   let path = Path::new("/path/to/file.txt");
   
   // The awkward dance with multiple conversions
   match path.as_os_str().to_str() {
       Some(s) => {
           // Yay! We can use string operations
       },
       None => {
           // Oh well, it's not UTF-8.
           // Many developers just use lossy conversion to avoid dealing with this
           // Which might _silently_ corrupt path data but keeps the code moving...
           let lossy = path.to_string_lossy();
           
       }
   }
}
```

These `path.as_os_str().to_str()` operations must be repeated everywhere, making path manipulation cumbersome.

There are a few more issues with paths in Rust:

- `Path`/`OsStr` lacks common string manipulation methods (like `find()`, `replace()`, etc.), which makes many common operations on paths quite tedious
- The design creates a poor experience for Windows users, with inefficient `Path`/`OsStr` handling that doesn't fit the platform well. It's a cross-platform compromise, but it creates some real problems.

Of course, for everyday use, `Path` is perfectly fine.
If path handling is a core part of your application, you might want to consider using an external crate instead.
[`camino`](https://github.com/camino-rs/camino) is a good alternative crate, which just assumes that paths are UTF-8 (which, in 2025, is a fair assumption).
This way, operations have much better ergonomics.

## `std::time`

In my opinion, it's actually great to have some basic time functionality right in the standard library.
However, just be aware that `std::time::SystemTime` is platform dependent, which [causes some headaches](https://github.com/rust-lang/rust/issues/44394).
[Same for `Instant`](https://github.com/rust-lang/rust/issues/48980), which is a wrapper around the most precise time source on each OS. 

Since time is such a thin wrapper around whatever the operating system provides, you can run into some nasty behavior.
For example, this does not always result in "1 nanosecond" on Windows:

```rust
use std::time::{Duration, SystemTime};

fn main() {
let now = SystemTime::now();
dbg!((now + Duration::from_nanos(1)).duration_since(now));
}
```

The documentation does not specify the clock's accuracy or how it handles leap seconds, except to note that `SystemTime` does not account for them.

That means if you depend on proper control over time, such as managing leap seconds or cross-platform support, you're better off using an external crate.
For an overview, see this great survey in the Rust forum, titled: ['The state of time in Rust: leaps and bounds'](https://users.rust-lang.org/t/the-state-of-time-in-rust-leaps-and-bounds/107620).

I suggest looking into [`chrono`](https://github.com/chronotope/chrono) or [`time`](https://github.com/time-rs/time).

## Summary

As you can see, it's really not a lot.
Given that Rust 1.0 was released over a decade ago, the standard library stood the test of time.
Apart from the mentioned issues, the Rust standard library is very well designed and thoroughly documented.
There are also very few deprecations, which is a testament to the good overall structure and foresight.