+++
title = "Sharp Edges In The Rust Standard Library"
date = 2025-05-21
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
reviews = [ 
    { name = "Wesley Moore (wezm)", url = "https://www.wezm.net" },
    { name = "Eshed Schacham", url = "https://ashdnazg.github.io/" },
    { name = "LoeniePhiline", url = "https://github.com/LeoniePhiline" },
]
resources = [
    "[Pitfalls of Safe Rust](/blog/pitfalls-of-safe-rust/#surprising-behavior-of-path-join-with-absolute-paths)",
    "[Programming Language Warts on Reddit](https://www.reddit.com/r/rust/comments/f7vimo/programming_language_warts/)"
]
+++

The [Rust standard library](https://doc.rust-lang.org/std/), affectionately called `std`, is exceptionally well-designed, but that doesn't mean it's perfect.
More experienced Rust developers tend to navigate around some of its sharper parts.

In this article, I want to highlight the areas in `std` that I personally avoid.
Keep in mind that this list is subjective, so take it with a grain of salt. 
My intention is to point out some pitfalls and suggest alternatives where appropriate.

## Threading

Rust's threading library is quite solid.
That said, managing threads can be a bit of a footgun.
In particular, forgetting to *join* a thread can have some unexpected side effects.

```rust
use std::thread;
use std::time::Duration;

struct Resource;

impl Drop for Resource {
    fn drop(&mut self) {
        // This never gets called
        println!("CRITICAL CLEANUP: Resource dropped");
    }
}

fn main() {
    let handle = thread::spawn(|| {
        let resource = Resource;
        // Do some work... 
        thread::sleep(Duration::from_secs(60));
        // Resource should be dropped here when thread ends
    });
    
    // Main thread exits immediately.
    // But! We forgot to join the spawned thread!
    // handle.join().unwrap();
}
```

In the above scenario, cleanup tasks (such as flushing caches or closing files) might not get executed.
So, even if you do nothing with the handle, it is still a best practice to `join()` it.
For more details on the topic, check out matklad's article: ["Join Your Threads"](https://matklad.github.io/2019/08/23/join-your-threads.html).

In fact, there was a proposal to make [`std::thread::JoinHandle`](https://doc.rust-lang.org/std/thread/struct.JoinHandle.html) be `#[must_use]`, but it was ultimately [declined](https://github.com/rust-lang/rust/pull/48830) because it would produce too many warnings.

[This comment summarized the situation pretty well](https://github.com/rust-lang/rust/pull/48830#issuecomment-371649213):

> I'd say the key issue here is that `thread::spawn` is the easiest way of spawning threads, but not the best one for casual use. Manually calling `.join().unwrap()` is a chore and easy to forget, which makes `thread::spawn` a potential footgun.

For new code, **I recommend using [`thread::scope`](https://doc.rust-lang.org/std/thread/fn.scope.html)** instead, which is a much better API in every conceivable way.
The documentation addresses the above issue directly:

> Unlike non-scoped threads, scoped threads can borrow non-`'static` data, as the scope guarantees **all threads will be joined at the end of the scope**.
> All threads spawned within the scope that **haven't been manually joined will be automatically joined** before this function returns.

Alternatively, you could use a thread pool library or [rayon](https://github.com/rayon-rs/rayon), in case you have an iterator you want to parallelize without manually managing threads.

## `std::collections::LinkedList`

Implementing a linked list in Rust is [not easy](https://rust-unofficial.github.io/too-many-lists/).
That's because Rust's ownership model is detrimental to self-referential data structures. 

Some people might not know that the standard library ships an implementation of a linked list at [`std::collections::LinkedList`](https://doc.rust-lang.org/std/collections/struct.LinkedList.html).
In all those years, I never felt the urge to use it. 
It might even be the least-used collection type in the standard library overall.

For all ordinary use cases, a `Vec` is superior and straightforward to use.
Vectors also have better cache locality and performance characteristics: all items are stored in contiguous memory, which is much better for fast memory access.
On the other side, elements in a linked list can be scattered all over the heap.
If you want to learn more, you can read [this paper](https://arxiv.org/pdf/2306.06942), which contains some benchmarks.

You might be wondering why linked lists get used at all.
They have their place as a very specialized data structure that is only really helpful in some resource-constrained or low-level environments like a kernel. The Linux kernel, for example, uses a lot of linked lists.
The reason is that the kernel's intrusive linked list implementation embeds list nodes directly within data structures which is very memory efficient and allows objects to be in multiple lists simultaneously without additional allocations. [^linux]

[^linux]: For a more in-depth discussion on why the Linux kernel uses linked lists, see [this article](https://www.data-structures-in-practice.com/intrusive-linked-lists/).

As for normal, everyday code, just use a `Vec`.
Even [the documentation of `LinkedList`](https://doc.rust-lang.org/nightly/std/collections/struct.LinkedList.html) itself agrees:

> NOTE: It is almost always better to use `Vec` or `VecDeque` because array-based
> containers are generally faster, more memory efficient, and make better use of
> CPU cache.

I believe the LinkedList should not have been included in the standard library in the first place.
[Even its original author agrees](https://rust-unofficial.github.io/too-many-lists/sixth.html).

There are some surprising gaps in the API; for instance, [`LinkedList::remove`](https://doc.rust-lang.org/std/collections/struct.LinkedList.html#method.remove) is still a nightly-only feature[^ll-remove]: 

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

Even if you wanted a linked list, it probably would not be `std::collections::LinkedList`:

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

There's a thing to be said about `BTreeMap` as well, but I leave it at that. [^btreemap]

[^btreemap]:  "Hold on, what's wrong with BTreeMap?" you might ask.
    <details><summary>
    This is just a mild observation rather than a strong criticism.
    If you're truly interested, expand the details here.</summary>

    As you know, Rust has two map implementations in the standard library:
    `BTreeMap`, which guarantees insertion ordering, while `HashMap` is unordered, but more commonly used. 
    For a long time, a ["performance trick"](https://users.rust-lang.org/t/hashmap-vs-btreemap/13804/2) was to use `BTreeMap` if you needed a faster hash map implementation.

    Since then, the performance of `HashMap` has improved significantly.
    One reason is that the implementation of `HashMap` has [changed to use a "siphash" algorithm](https://doc.rust-lang.org/book/ch08-03-hash-maps.html#hashing-functions) and is now [based on Google's SwissTable](https://doc.rust-lang.org/std/collections/struct.HashMap.html).
    The combination of these changes has made `HashMap` much more performant than before, so there is no good reason to use `BTreeMap` anymore, other than the ordering guarantee.

    One important distinction to note: iteration order over a `HashMap` is random, while `BTreeMap`'s iteration order is always sorted by the key's `Ord` implementation (not by insertion order). This makes `BTreeMap` useful when you need to iterate over keys in a sorted manner. If you're aggregating data in a `HashMap` but need a sorted list, you'll need to collect into a vector and sort it manually. In contrast, `BTreeMap` gives you sorted iteration for free. So while `HashMap` is better for random access operations, `BTreeMap` is still helpful when sorted iteration is required.
    I would argue that it's a bit of a niche use case, however.

    In ["Smolderingly fast b-trees"](https://www.scattered-thoughts.net/writing/smolderingly-fast-btrees/), Jamie Brandon compares the performance of Rust's `BTreeMap` and `HashMap`. Here are the key takeaways:

    - When comparing performance, btrees were found to be significantly slower than hashmaps in most scenarios,
    especially for lookups. In the worst case with random-ish strings that share common prefixes, btrees performed dramatically worse.
    - Hashmaps benefit more from speculative execution between multiple lookups, while btrees don't.
    - btrees have performance "cliffs" when comparisons get more expensive and touch more memory
    - For space usage, the author estimates that btrees would use >60% more memory than hashmaps for random keys.

    I'd argue that a normal HashMap is almost always the better choice and having two map implementations in the standard library can be confusing. 

    On top of that, if the hash map is your bottleneck, you're doing pretty well already.
    If you need anything faster, there are plenty of great external crates like [indexmap](https://github.com/indexmap-rs/indexmap) for insertion-order preservation and [dashmap](https://github.com/xacrimon/dashmap) for concurrent access.
    </details>

## Path Handling

`Path` does a decent job of abstracting away the underlying file system.
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

These `path.as_os_str().to_str()` operations must be repeated everywhere.
It makes path manipulation every so slightly annoying. 

There are a few more issues with paths in Rust:

- `Path`/`OsStr` lacks common string manipulation methods (like `find()`, `replace()`, etc.), which makes many common operations on paths quite tedious
- The design creates a poor experience for Windows users, with inefficient `Path`/`OsStr` handling that doesn't fit the platform well. It's a cross-platform compromise, but it creates some real problems.

Of course, for everyday use, `Path` is perfectly okay, but if path handling is a core part of your application, you might want to consider using an external crate instead.
[`camino`](https://github.com/camino-rs/camino) is a good alternative crate, which just assumes that paths are UTF-8 (which, in 2025, is a fair assumption).
This way, operations have much better ergonomics.

## Platform-Specific Date and Time Handling

In my opinion, it's actually great to have some basic time functionality right in the standard library.
However, just be aware that `std::time::SystemTime` is platform dependent, which [causes some headaches](https://github.com/rust-lang/rust/issues/44394).
[Same for `Instant`](https://github.com/rust-lang/rust/issues/48980), which is a wrapper around the most precise time source on each OS. 

Since time is such a thin wrapper around whatever the operating system provides, you can run into some nasty behavior.
For example, **this does not always result in "1 nanosecond" on Windows**:

```rust
use std::time::{Duration, SystemTime};

fn main() {
let now = SystemTime::now();
dbg!((now + Duration::from_nanos(1)).duration_since(now));
}
```

The documentation does not specify the clock's accuracy or how it handles leap seconds, except to note that `SystemTime` does not account for them.

If you depend on proper control over time, such as managing leap seconds or cross-platform support, you're better off using an external crate.
For a great overview, see this survey in the Rust forum, titled: ['The state of time in Rust: leaps and bounds'](https://users.rust-lang.org/t/the-state-of-time-in-rust-leaps-and-bounds/107620).

In general, I believe `std::time` works well in combination with the rest of the standard library, such as for `sleep`:

```rust
use std::thread;
use std::time::Duration;

thread::sleep(Duration::from_secs(1));
```

...but apart from that, I don't use it for much else. If I had to touch any sort of date calculations, I would defer to an external crate
such as [`chrono`](https://github.com/chronotope/chrono) or [`time`](https://github.com/time-rs/time).

## Summary

As you can see, my list of warts in the Rust standard library is quite short.
Given that Rust 1.0 was released more than a decade ago, the standard library has held up *really* well.
That said, I reserve the right to update this article in case I become aware of additional sharp edges in the future. 

In general, I like that Rust has a relatively small standard library because once a feature is in there it stays there forever. [^forever]

[^forever]: Yes, you *can* deprecate functionality, but this is a very timid and [laborious process](https://rust-lang.github.io/rfcs/1270-deprecation.html) and that still doesn't mean functionality gets removed. For example, `std::env::home_dir()` has been deprecated for years and is now not getting removed, but instead will be [fixed with a bugfix release and un-deprecated](https://releases.rs/docs/1.85.0/#compatibility-notes).
