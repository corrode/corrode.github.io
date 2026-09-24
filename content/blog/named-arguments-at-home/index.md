+++
title = "We Have Named Arguments at Home"
date = 2026-09-24
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
resources = [
    "[Steve Klabnik on our 'Rust in Production' podcast](/podcast/s03e03-oxide/)",
]
+++

Steve Klabnik recently [wrote about](https://steveklabnik.com/writing/arguing-about-arguments/) named arguments, optional arguments, default arguments, function overloading, and why most of that design space has historically made him nervous in Rust.

I agree with Steve.
In fact, I think I agree slightly more strongly than Steve does. :)

I actually think we can get most of what we want without adding any new language features.
Instead, we can lean into what Rust already provides.

None of these is an exact substitute for what you get in Python, Ruby, C++, or Kotlin, but that's sort of the point.
Instead, you can get 80% of the ergonomics without adding any magic to function calls at all.

The recurring pattern is that Rust takes something another language puts into **function-call semantics** and represents it as a normal part of its type system, elegantly sidestepping the mentioned design problems.

## Named Arguments at Home

Let's revisit Steve's example from the `image` crate:

```rust
pub fn crop_imm<I: GenericImageView>(
    image: &I,
    x: u32,
    y: u32,
    width: u32,
    height: u32,
) -> SubImage<&I> {
    // ...
}

let cropped = image::imageops::crop_imm(&img, 10, 20, 200, 100);
```

The obvious problem is that four consecutive `u32`s are not a great API that you can reliably use without reading the docs. 

Let's assume for a moment that we had named arguments:

```rust
let cropped = image::imageops::crop_imm(
    image: &img,
    x: 10,
    y: 20,
    width: 200,
    height: 100,
);
```

That's clearly better, but stable Rust has another syntax in its place: structs. 

```rust
struct Crop {
    x: u32,
    y: u32,
    width: u32,
    height: u32,
}

fn crop_imm<I: GenericImageView>(
    image: &I,
    crop: Crop,
) -> SubImage<&I> {
    // ...
}

let cropped = image::imageops::crop_imm(
    &img,
    Crop {
        x: 10,
        y: 20,
        width: 200,
        height: 100,
    },
);
```

A struct is a named argument with one extra type name.
On top of that, we also get arbitrary field order:

```rust
Crop {
    width: 200,
    height: 100,
    x: 10,
    y: 20,
}
```

We also get typo checking, autocomplete, and per-field documentation for free!
And we can [put invariants on the type](/blog/compile-time-invariants/) and pass the arguments around as values.

And, perhaps most importantly, **the names belong to the type**, rather than becoming part of every function's calling convention.

That last property neatly avoids several problems with actual named arguments.
Consider function pointers:

```rust
fn resize(width: u32, height: u32) {}
fn offset(dx: u32, dy: u32) {}

let f: fn(u32, u32) = if resizing { resize } else { offset };
```

What would the parameter names of `f` be?
With an argument struct, the question simply wouldn't come up: 

```rust
struct Size {
    width: u32,
    height: u32,
}

fn resize(size: Size) {}

// No more arguing about arguments
let f: fn(Size) = resize;
```

If names are semantically important, give the names a type.
If they aren't, then... don't.

There is another delightful benefit here.
Steve brings up evaluation order:

```rust
consume(length: data.len(), data: data);
```

I.e., should arguments be evaluated in the order they appear at the call site, or in the order the parameters appear in the declaration?
Here, does that mean computing `data.len()` before moving `data` or after? 

Rust already answered this question for structs:

```rust
let args = Args {
    length: data.len(),
    data,
};
```

Expressions are evaluated where you wrote them.
No new rules required.

This feels extremely idiomatic to me: rather than teaching function calls a second field-like syntax with subtly different semantics, just use the field syntax that already exists.

### Arguments Are Part of Your Domain

Of course, declaring a bespoke argument type for every two-argument function would be ridiculous.
I would not write:

```rust
struct PushArgs<T> {
    value: T,
}

vec.push(PushArgs { value: 42 });
```

That would be silly.
The trick is to notice that named arguments are most useful exactly where an argument bundle becomes conceptually meaningful, which is the same point at which you reach for a struct anyway.

These are bad:

```rust
draw(x1, y1, x2, y2, width, opacity);
connect(host, port, timeout, retries, tls);
```

And these are often better APIs *anyway*:

```rust
draw(Line {
    start: Point { x: x1, y: y1 },
    end: Point { x: x2, y: y2 },
    width,
    opacity,
});

connect(ConnectionOptions {
    host,
    port,
    timeout,
    retries,
    tls,
});
```

The design pressure forced us to uncover missing domain concepts.

## Optional Arguments at Home

An optional argument is, to some extent, an argument which may or may not exist.
Rust has a type for that.

```rust
fn connect(url: &str, timeout: Option<Duration>) {
    // ...
}

connect("https://example.com", None);

connect(
    "https://example.com",
    Some(Duration::from_secs(5)),
);
```

This is not as pleasant as:

```text
connect("https://example.com")
connect("https://example.com", timeout: 5s)
```

But it has a useful property: the optionality appears in the function's type.
There isn't a hidden second calling convention for `connect`.
There is but one function:

```rust
fn(&str, Option<Duration>)
```

and every caller supplies both arguments.

This is obviously not what you want once you have six optional arguments:

```rust
request(
    url,
    None,
    None,
    Some(timeout),
    None,
    None,
    None,
);
```

I've personally been found guilty of this pattern in the past.
The problem is that the arguments have stopped being a parameter list and started being configuration.
So:

```rust
struct RequestOptions {
    timeout: Option<Duration>,
    proxy: Option<Proxy>,
    redirect: Option<RedirectPolicy>,
    // ...
}

request(
    url,
    RequestOptions {
        timeout: Some(Duration::from_secs(5)),
        proxy: None,
        redirect: None,
    },
);
```

Instead of optional arguments, we deal with data.
And that adds a nice property: there is no special distinction between "arguments supplied syntactically to this invocation" and "options I calculated elsewhere."

```rust
let options = RequestOptions {
    timeout: config.request_timeout,
    proxy: detect_proxy(),
    redirect: None,
};

request(url, options);
```

It composes nicely because it's just a value.

## Default Arguments at Home

Now the obvious objection: writing all those `None`s is terrible.

Correct.
So don't.

That's why we have `Default` and struct update syntax:

```rust
#[derive(Default)]
struct RequestOptions {
    timeout: Option<Duration>,
    proxy: Option<Proxy>,
    follow_redirects: bool,
}

request(
    url,
    RequestOptions {
        timeout: Some(Duration::from_secs(5)),
        ..Default::default()
    },
);
```

That is getting awfully close to:

```ruby
request(url, timeout: 5s)
```

with one minor wrinkle:

```rust
RequestOptions {
    ...
    ..Default::default()
}
```

That is not nothing.
But look at what we *didn't* have to add: rules for which arguments may be omitted, how positional and named arguments interact, or whether you can omit something in the middle.

There's no special syntax for declaring parameter defaults, no question about whether default expressions run at declaration time or invocation time, and no special representation in `fn` types.

`Default` is just a trait, and function calls remain untouched.

Defaults are now usable independently of the function:

```rust
let defaults = RequestOptions::default();
```

That is frequently useful in its own right.
For library APIs, I often like being slightly more explicit:

```rust
struct RequestOptions {
    timeout: Duration,
    follow_redirects: bool,
}

impl Default for RequestOptions {
    fn default() -> Self {
        Self {
            timeout: Duration::from_secs(30),
            follow_redirects: true,
        }
    }
}
```

Then:

```rust
request(
    url,
    RequestOptions {
        timeout: Duration::from_secs(5),
        ..Default::default()
    },
);
```

I think this gets most of the important bits right.

## Builder Pattern for the Really Complex Cases

Sometimes even the options struct is too noisy, often when construction requires validation or conversion.

Then, yes, there is the builder:

```rust
let request = Request::builder(url)
    .timeout(Duration::from_secs(5))
    .follow_redirects(false)
    .build()?;
```

Steve is right that builders should not be the default. 
They can become their own tiny programming language.
But a small builder has a very useful property: each "argument" is an ordinary method call.
That means we can do things like:

```rust
let mut request = Request::builder(url);

if let Some(timeout) = config.timeout {
    request = request.timeout(timeout);
}

let request = request.build()?;
```

Doing that with language-level keyword arguments generally requires constructing a map, splatting things, or some other mechanism.

In Rust, it's method calls.
I personally find this very pleasing to read. 

## Function Overloading at Home

In Java, you can write: 

```java
void connect(String url, int timeout) { ... }
void connect(String url) { ... }
```

Rust doesn't let you define both:

```rust
fn connect(url: &str) {}
fn connect(url: &str, timeout: Duration) {}
```

I am very happy about this.
But there are several different things people mean when they say they want overloading, and Rust already covers most of them separately.

### "I Want One Convenience Form and One Configurable Form"

Give them different names:

```rust
fn connect(url: &str) {
    connect_with_timeout(url, DEFAULT_TIMEOUT)
}

fn connect_with_timeout(url: &str, timeout: Duration) {
    // ...
}
```

The standard library does this often.
See [`Vec::new()`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.new) and [`Vec::with_capacity()`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.with_capacity), for example.

This costs the library author one additional name (often just `with_...`) and saves every user from doing overload resolution in their head.

### "I Want Several Input Types"

Use a trait.
The standard library does this all the time with traits like `Into`, `AsRef`, and `Borrow`.
For example:

```rust
fn greet(name: impl AsRef<str>) {
    println!("Hello, {}", name.as_ref());
}

greet("Ferris");
greet(String::from("Ferris"));
```

This gives us another useful part of overload-like behavior: one API can accept different input types.

For owned conversion:

```rust
fn set_name(name: impl Into<String>) {
    let name = name.into();
    // ...
}
```

That's just a single function with one parameter list and trait dispatch.
And unlike unrestricted overloading, the relationship between accepted types is explicit: they work as long as they satisfy the bound.

### "Different Types Need Different Behavior"

That's a trait, too:

```rust
trait Render {
    fn render(self, out: &mut Output);
}

impl Render for &str {
    fn render(self, out: &mut Output) {
        // ...
    }
}

impl Render for Image {
    fn render(self, out: &mut Output) {
        // ...
    }
}

fn render(value: impl Render, out: &mut Output) {
    value.render(out);
}
```

That's polymorphism; we just put it in the trait system instead of in name resolution.

## Flexible Argument Types at Home

Steve's Ruby example has this equally lovely and terrifying quality:

```ruby
redirect_to "http://www.rubyonrails.org"
redirect_to @post
redirect_to action: "show", id: 5
```

These calls look like they're invoking one conceptual operation, but they mean wildly different things.

In Rust, we can model that directly:

```rust
enum Redirect {
    Url(Url),
    Post(Post),
    Action {
        action: String,
        id: u64,
    },
}

fn redirect_to(target: Redirect) {
    // ...
}
```

Then:

```rust
redirect_to(Redirect::Url(url));

redirect_to(Redirect::Post(post));

redirect_to(Redirect::Action {
    action: "show".into(),
    id: 5,
});
```

That's more verbose, but in a good way.
And I can ask, "Hey editor, what can I redirect to?" and the editor replies with the variants of `Redirect`.
That's more helpful than "read the docs and discover which keys and values this hash accepts."

If we really cared about smoothing down the edges, we could add `From` conversions: 

```rust
impl From<Url> for Redirect {
    fn from(url: Url) -> Self {
        Self::Url(url)
    }
}

impl From<Post> for Redirect {
    fn from(post: Post) -> Self {
        Self::Post(post)
    }
}

fn redirect_to(target: impl Into<Redirect>) {
    let target = target.into();
    // ...
}
```

Now:

```rust
redirect_to(url);
redirect_to(post);
```

And for the structurally interesting case:

```rust
redirect_to(Redirect::Action {
    action: "show".into(),
    id: 5,
});
```

Remember that this has no runtime cost and is fully type-safe.
Not bad for a compiled language.

## Options Hashes at Home

An "options hash" is basically a dynamically typed anonymous struct.
So the extremely boring Rust translation is: use a statically typed, named struct.

Ruby:

```ruby
redirect_to post_url(@post),
  status: 301,
  flash: { updated_post_id: @post.id }
```

Rust:

```rust
redirect_to(
    post_url(&post),
    RedirectOptions {
        status: StatusCode::MOVED_PERMANENTLY,
        flash: Some(Flash {
            updated_post_id: Some(post.id),
            ..Default::default()
        }),
        ..Default::default()
    },
);
```

Yes, the Rust version is noisier, but it also detects when we misspell `status`.
It's impossible to pass a string where the status code goes, and it's straightforward to list every supported option.

I don't think Rust should optimize for making the syntax as dense as possible. 
Instead, if a set of options is common enough to deserve convenient syntax, it is probably common enough to justify a type.

```rust
fn redirect_to(target: Url, options: RedirectOptions)
```

Now, options have a name and the fields can be documented in one place.

## Variadic Arguments at Home

Rust does not have general-purpose variadic Rust functions.
But once again, it already has several ways of expressing the same concept. 

If all arguments have the same type, take a slice:

```rust
fn sum(values: &[i32]) -> i32 {
    values.iter().sum()
}

sum(&[1, 2, 3, 4]);
```

Or accept an iterator:

```rust
fn sum(values: impl IntoIterator<Item = i32>) -> i32 {
    values.into_iter().sum()
}

sum([1, 2, 3, 4]);
sum(vec![1, 2, 3, 4]);
```

That is arguably more composable than:

```ruby
sum(1, 2, 3, 4)
```

because the caller can naturally pass an existing collection.
(All type-safe, of course, and with zero indirection at runtime.)

If the arguments are heterogeneous, the last resort is to write a custom macro.
To be clear, I would not use macros just to fake variadic functions, but I do like how macros can be used in stable Rust, and how the exclamation mark stands out from normal function calls. 

## Keyword-Looking Syntax at Home

There is one tiny affordance in all of these examples that I think deserves more credit: field-init shorthand.

Rust lets you turn this:

```rust
let options = RequestOptions {
    timeout: timeout,
    proxy: proxy,
    retries: retries,
};
```

into this:

```rust
let options = RequestOptions {
    timeout,
    proxy,
    retries,
};
```

This directly addresses one of Steve's complaints about keyword arguments:

```
response_model=response_model,
status_code=status_code,
tags=tags,
dependencies=dependencies,
```

Rust's answer is effectively:

```rust
Options {
    response_model,
    status_code,
    tags,
    dependencies,
}
```

In my opinion, that's even better than keyword arguments.
That's because the labels are still present, the duplication disappears, and nothing needs to change in how we call functions.

## Composition Is a Superpower

The thing I like the most about Rust is how each concept nicely interacts with the others.
That is not an easy task, and Rust deserves a lot of credit for that.

For example, suppose we want a complex HTTP request API with:

* a required URL,
* several accepted URL-like input types,
* named options,
* defaults,
* optional timeout,
* configurable redirects,
* and a variable number of headers.

We could imagine a pile of language features that lets us write:

```ruby
request(
    "/hello",
    timeout: 5s,
    redirects: false,
    headers: [
        ("Accept", "application/json"),
        ("X-Foo", "bar"),
    ],
)
```

Now wouldn't that be nice?
However, we can already do this in stable Rust with a combination of already existing, composable features:

```rust
request(
    "/hello",
    RequestOptions {
        timeout: Some(Duration::from_secs(5)),
        redirects: false,
        headers: vec![
            Header::new("Accept", "application/json"),
            Header::new("X-Foo", "bar"),
        ],
    },
)?;
```

And all we had to do was write the code we'd likely write anyway: 

```rust
#[derive(Default)]
struct RequestOptions {
    timeout: Option<Duration>,
    redirects: bool,
    headers: Vec<Header>,
}

fn request(
    url: impl Into<Url>,
    options: RequestOptions,
) -> Result<Response> {
    // ...
}
```

Or maybe you prefer a builder?

```rust
Request::new("/hello")
    .timeout(Duration::from_secs(5))
    .redirects(false)
    .header("Accept", "application/json")
    .header("X-Foo", "bar")
    .send()?;
```

We combined standard Rust concepts: structs, enums, `Option`, `Default`, struct update syntax, field-init shorthand, traits, generics, iterators, and methods.
Those mechanisms are all useful far beyond argument passing.

Basic Rust syntax is all the machinery required to build ergonomic APIs.
[Keeping things simple](/blog/simple/) doesn't mean worse ergonomics.

## Friction Produces Better APIs

The obvious response to everything above is:

> Come on.
> These aren't actually named/default/overloaded/variadic arguments.
> They're workarounds.

Correct.

- Actual named arguments might let me turn `crop_imm(&img, 10, 20, 200, 100)` into:
  ```rust
  crop_imm(
      image: &img,
      x: 10,
      y: 20,
      width: 200,
      height: 100,
  );
  ```
  That surely is nicer at the call site.
- Actual default arguments might let me write `request(url, timeout: timeout);` instead of introducing `RequestOptions`.
- Actual overloading might let two functions share the same name instead of forcing me to invent `with_timeout`.

All of the above might be useful, though localized, syntax improvements.
But the hidden tax is that the language becomes more complex, for arguably little gain.

Friction in APIs often pushes us toward solutions that turn out to be useful beyond the original problem:

- These four coordinates become a `Rect`.
- Seven random config parameters become `RequestOptions`.
- A bunch of dynamically accepted values turn into an enum.
- A family of related operations becomes a trait.

In a sense, the concrete issue points to a broader design problem, and resolving it opens up completely new ways to solve similar problems.
That's great systems design.

## Rust's Answer to Almost Everything Is: Better Types

I think there's a broader design principle behind all of this.

A common design philosophy in dynamic languages is to make familiar constructs more powerful by overloading them with additional semantics.
After all, that is one affordance which dynamic typing allows: the ability to decide the meaning of an object at runtime. 

```ruby
foo(x)
foo(x, y)
foo(x, timeout: 3)
foo(path: x, timeout: 3)
foo(x, **options)
foo(*args, **options)
```

Rust, however, tends to move complexity *outward* and [let the type system do all the work](/blog/illegal-state/).

```rust
foo(FooOptions { ... })
```

## What about Agents?

One might ask: "In the age of agentic development, doesn't verbosity become cheaper while redundant labels may make a call easier to understand locally?"

I agree with the premise.
I'm less sure it changes the conclusion.

An agent looking at:

```rust
crop_imm(
    &img,
    Crop {
        x: 10,
        y: 20,
        width: 200,
        height: 100,
    },
);
```

gets essentially the same local information.

Arguably it gets more: `Crop` gives the bundle a semantic identity which the function parameter list alone does not.

Similarly:

```rust
request(
    url,
    RequestOptions {
        timeout,
        ..Default::default()
    },
);
```

says something useful to both humans and agents.
`timeout` is not merely an optional syntactic argument to this particular invocation; it is a way to configure a request. 

And if agents really do make typing cost increasingly irrelevant, then the principal downside of these slightly-more-verbose Rust idioms gets cheaper too.
The robots can type `RequestOptions` for me.

## Keep the Functions Boring

I'm not opposed to Rust ever gaining named arguments.
There may be a proposal that finds a tiny, coherent design which handles patterns, function pointers, traits, evaluation order, compatibility, and all the other sharp edges described.
But I don't feel much urgency.

Stable Rust already gives me structs for named options, `Option` and `Default` for optional values and defaults, traits and enums for varied inputs, and slices and iterators for repeated arguments.

Collectively, they cover a lot of ground.
And they do it by reusing features Rust already needs.
And I think that's a core part of Rust's design philosophy: finding the smallest, composable, orthogonal set of abstractions, which, when combined, can solve many problems in elegant ways.
The whole is greater than the sum of its parts.

{{ <next_steps context="Want a second opinion on your team's Rust APIs? Let's review the types and abstractions together." source="named-arguments-at-home" /> }}
