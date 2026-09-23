+++
title = "We Have Named Arguments At Home"
date = 2026-09-23
draft = false
template = "article.html"
[extra]
series = "Idiomatic Rust"
+++

Steve Klabnik recently wrote [“Arguing about arguments”](https://steveklabnik.com/writing/arguing-about-arguments/), about named arguments, optional arguments, default arguments, function overloading, and why most of that design space has historically made him nervous in Rust. It's a wonderful read, and I recommend it. 

I agree with Steve. In fact, I think I agree slightly more strongly than Steve does. :)

Steve has warmed to named arguments, but I think we can get most of what we want without adding language features. Instead, we can lean into what Rust already provides. That goes for named arguments, defaults, function overloading, and, regrettably or otherwise, variadic arguments.

None of these substitutes is *quite* the feature you get in Python, Ruby, C++, or Kotlin. But that’s the point. You get most of the ergonomics without adding magic to function calls.

The recurring pattern is that Rust takes something another language puts into **function-call semantics** and represents it with a **familiar piece of the type system** instead. I think that’s often the better trade. 

## Named arguments at home

Steve uses this example from the `image` crate:

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

The problem is obvious. Four consecutive `u32`s are not an API you can reliably read without knowing the signature.

With hypothetical named arguments:

```rust
let cropped = image::imageops::crop_imm(
    image: &img,
    x: 10,
    y: 20,
    width: 200,
    height: 100,
);
```

Yep. Better. But stable Rust has another syntax which looks suspiciously familiar:

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

That is named arguments with one extra type name.

We also get arbitrary field order:

```rust
Crop {
    width: 200,
    height: 100,
    x: 10,
    y: 20,
}
```

We get typo checking, autocomplete, and documentation attached to each field. We can put invariants on the type and pass the arguments around as a value.

And, importantly, the names belong to the **type**, rather than becoming part of every function’s calling convention.

That last property neatly dodges several problems Steve raises about real named arguments. Consider function pointers:

```rust
fn resize(width: u32, height: u32) {}
fn offset(dx: u32, dy: u32) {}

let f: fn(u32, u32) =
    if resizing { resize } else { offset };
```

What would the parameter names of `f` be?

With an argument struct, the question simply doesn’t arise:

```rust
struct Size {
    width: u32,
    height: u32,
}

fn resize(size: Size) {}

let f: fn(Size) = resize;
```

If names are semantically important, give the names a type. If they aren’t, don’t.

There is another cute advantage here. Steve brings up evaluation order:

```rust
consume(length: data.len(), data: data);
```

Should this evaluate in call-site order or declaration order? Rust already answered this question for structs:

```rust
let args = Args {
    length: data.len(),
    data,
};
```

Expressions are evaluated where you wrote them. No new rule required.

This feels extremely Rusty to me: rather than teaching function calls a second field-like syntax with subtly different semantics, use the field syntax that already exists.

### The lightweight version

Of course, declaring a bespoke argument type for every two-argument function would be ridiculous. I would not write:

```rust
struct PushArgs<T> {
    value: T,
}

vec.push(PushArgs { value: 42 });
```

The trick is to notice that named arguments are most useful exactly where an argument bundle becomes conceptually meaningful.

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

The “named argument” transformation forced us to discover some actual domain concepts. I’ll take that.

## Optional arguments at home

An optional argument is, at some level, an argument which may or may not exist. Rust has a type for that.

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

But it has a useful property: the optionality appears in the function’s type. There isn’t a hidden second calling convention for `connect`. There is one function:

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

Nobody wants this. But that is the point where the arguments have stopped being a parameter list and started being configuration. So:

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

We have traded optional arguments for ordinary data. And that gives the API something nice: there is no special distinction between “arguments supplied syntactically to this invocation” and “options I calculated somewhere else.”

```rust
let options = RequestOptions {
    timeout: config.request_timeout,
    proxy: detect_proxy(),
    redirect: None,
};

request(url, options);
```

It composes because it is just a value.

## Default arguments at home

Now the obvious objection: writing all those `None`s is terrible. Correct. So don’t. Rust has `Default` and struct update syntax:

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

```text
request(url, timeout: 5s)
```

The syntactic tax is:

```rust
RequestOptions {
    ...
    ..Default::default()
}
```

That is not nothing. But look at what we *didn’t* have to add: rules for which arguments may be omitted, how positional and named arguments interact, or whether you can omit something in the middle.

There’s no special syntax for declaring parameter defaults, no question about whether default expressions run at declaration time or invocation time, and no special representation in `fn` types.

`Default` is just a trait. Struct update is just struct update. Function calls remain function calls.

And defaults are now usable independently of the function:

```rust
let defaults = RequestOptions::default();
```

That is frequently useful in its own right. For library APIs, I often like being slightly more deliberate:

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

This is default arguments at home, and I think it gets most of the important bit right.

## The builder pattern is the deluxe version

Sometimes even the options struct is too noisy, especially when construction requires validation or conversion.

Then yes, there is the builder:

```rust
let request = Request::builder(url)
    .timeout(Duration::from_secs(5))
    .follow_redirects(false)
    .build()?;
```

Steve is right that builders should not automatically be celebrated. They can become their own tiny programming language. But a small builder has a very useful property: each “argument” is an ordinary method call. That means we can do things like:

```rust
let mut request = Request::builder(url);

if let Some(timeout) = config.timeout {
    request = request.timeout(timeout);
}

let request = request.build()?;
```

Doing that with language-level keyword arguments generally requires constructing a map, splatting something, or adding some other mechanism.

In Rust, the boring desugaring is sitting right there. It’s methods. The price is verbosity, but the semantic budget stays tiny.

## Function overloading at home

Steve’s Java example is roughly:

```java
void connect(String url, int timeout) { ... }
void connect(String url) { ... }
```

Rust doesn’t let you define both:

```rust
fn connect(url: &str) {}
fn connect(url: &str, timeout: Duration) {}
```

I am very happy about this. But there are several different things people mean when they say they want overloading, and Rust already covers most of them separately.

### “I want one convenience form and one configurable form”

Give them different names:

```rust
fn connect(url: &str) {
    connect_with_timeout(url, DEFAULT_TIMEOUT)
}

fn connect_with_timeout(url: &str, timeout: Duration) {
    // ...
}
```

`Vec::new()` and `Vec::with_capacity()` are the canonical version of this.

This costs the library author one additional name and saves every reader from doing overload resolution in their head. Seems like a bargain.

### “I want several input types”

Use a trait. The standard library does this constantly with traits like `Into`, `AsRef`, and `Borrow`. For example:

```rust
fn greet(name: impl AsRef<str>) {
    println!("Hello, {}", name.as_ref());
}

greet("Ferris");
greet(String::from("Ferris"));
```

This gives us a useful part of overload-like behavior: different source types accepted by one API.

For owned conversion:

```rust
fn set_name(name: impl Into<String>) {
    let name = name.into();
    // ...
}
```

Again, one function. One parameter list. Ordinary trait dispatch. And unlike unrestricted overloading, the relationship between accepted types is explicit: they must satisfy the bound.

### “Different types need different behavior”

That’s a trait too:

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

We got ad-hoc polymorphism. We just put it in the trait system instead of in name resolution. That is a theme.

## Flexible argument types at home

Steve’s Ruby example has this delightful/terrifying quality:

```ruby
redirect_to "http://www.rubyonrails.org"
redirect_to @post
redirect_to action: "show", id: 5
```

These calls look like they’re invoking one conceptual operation, but they mean wildly different things.

Rust can model that directly:

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

More verbose? Absolutely. But I can ask my editor, “what can I redirect to?” and the answer is the variants of `Redirect`. That’s a much stronger property than “read the docs and discover which keys and values this hash accepts.”

If we really care about smoothing the edges, add conversions:

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

That is pretty good! Importantly, the weirdness has a name. It is called `Redirect`.

## Options hashes at home

An options hash is basically a dynamically typed anonymous struct. So the extremely boring Rust translation is: use a statically typed named struct.

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

Yes, the Rust version is considerably louder. It is also difficult to misspell `status`, impossible to pass a string where a status code belongs, and straightforward to enumerate every supported option.

I don’t think Rust should optimize for winning this particular code-golf competition.

There is an interesting middle ground, though. If a set of options is common enough to deserve convenient syntax, it is probably common enough to deserve a type. That type then becomes part of your API vocabulary:

```rust
fn redirect_to(target: Url, options: RedirectOptions)
```

instead of:

```text
redirect_to(thing, bag_of_stuff)
```

That feels like exactly the kind of pressure Rust generally likes to apply.

## Variadic arguments at home

Rust does not have general-purpose variadic Rust functions. But once again, it already has several ways of expressing the underlying use cases.

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

That is arguably *more* composable than:

```text
sum(1, 2, 3, 4)
```

because the caller can naturally pass an existing collection.

If the arguments are heterogeneous and syntax really matters, we have macros.

You might have encountered one:

```rust
println!("{} + {} = {}", 1, 2, 3);
```

Or:

```rust
vec![1, 2, 3, 4]
```

`macro_rules!` is stable Rust.

I would not reach for a macro just to fake variadic functions. But when an API needs syntax that the function-call grammar does not provide, Rust already has an explicit mechanism for saying:

> This is syntax, not an ordinary function.

I like that honesty. A macro invocation looks like a macro invocation. It doesn’t silently make functions more complicated.

## Keyword-looking syntax at home

There is one tiny feature hidden in all of these examples that I think deserves more credit: field-init shorthand.

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

This directly addresses one of Steve’s complaints about keyword arguments:

```python
response_model=response_model,
status_code=status_code,
tags=tags,
dependencies=dependencies,
```

Rust’s answer is effectively:

```rust
Options {
    response_model,
    status_code,
    tags,
    dependencies,
}
```

That is arguably *better* than keyword arguments for the forwarding case.

The labels are still present. The duplication disappears. And no new function-call feature was required.

This is one of my favorite small pieces of Rust syntax because it is exactly the kind of ergonomic feature I want: local sugar over an already-simple semantic model.

## And all of these compose

Here is where I think the “at home” versions become more compelling than they initially appear.

Suppose we want an HTTP request API with:

* a required URL,
* several accepted URL-like input types,
* named options,
* defaults,
* optional timeout,
* configurable redirects,
* and a variable number of headers.

We could imagine a language feature pile that lets us write:

```text
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

Stable Rust can instead say:

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

Maybe you prefer a builder:

```rust
Request::new("/hello")
    .timeout(Duration::from_secs(5))
    .redirects(false)
    .header("Accept", "application/json")
    .header("X-Foo", "bar")
    .send()?;
```

Neither one is as concise as the imaginary version.

But look at the mechanisms involved:

* structs,
* enums,
* `Option`,
* `Default`,
* struct update syntax,
* field-init shorthand,
* traits,
* generics,
* iterators,
* methods,
* macros when you need custom syntax.

Those mechanisms are all useful far beyond argument passing. Rust doesn’t need a separate version of each concept specifically for functions.

## The missing 20% is doing work

This is the part that makes me agree with Steve’s larger point. The obvious response to everything above is:

> Come on. These aren't actually named/default/overloaded/variadic arguments. They're workarounds.

Correct. That is why I called this “named arguments at home,” not “Rust secretly has named arguments.” The distinction matters.

Actual named arguments might let me turn:

```rust
crop_imm(&img, 10, 20, 200, 100);
```

into:

```rust
crop_imm(
    image: &img,
    x: 10,
    y: 20,
    width: 200,
    height: 100,
);
```

without defining anything else.

That is undeniably nicer at the call site.

Actual default arguments might let me write:

```rust
request(url, timeout: timeout);
```

instead of introducing `RequestOptions`.

Actual overloading might let two functions share the same name instead of forcing me to invent `with_timeout`.

That last 20% is real.

But the friction in the Rust versions often pushes APIs toward things that turn out to be useful anyway.

Four coordinates become a `Rect`. Seven configuration parameters become `RequestOptions`. A grab bag of dynamically accepted values becomes an enum.

A family of related operations becomes a trait. A repeated sequence becomes an iterator. Custom call syntax becomes an explicit macro invocation.

The workaround frequently turns accidental API structure into explicit type structure. That seems valuable.

## Types are Rust’s options hashes

There is a broader design instinct here that I’ve come to appreciate.

Dynamic languages often accumulate power by allowing a function call to describe increasingly elaborate things:

```text
foo(x)
foo(x, y)
foo(x, timeout: 3)
foo(path: x, timeout: 3)
foo(x, **options)
foo(*args, **options)
```

Rust tends to move that complexity one level outward:

```rust
foo(FooOptions { ... })
```

and then lets the type system do the work.

The API becomes slightly more ceremonial. But the *function call* remains incredibly boring: you name a function, pass one value for each parameter, and the arguments evaluate in order. The types have to match. Done.

Like Steve, I think there is substantial value in preserving that boringness, especially in Rust, where there are already enough places for sophisticated language semantics to live.

## What about agents?

Steve’s new openness to named arguments comes partly from coding agents. The argument makes sense: if a machine is doing the typing, verbosity becomes cheaper, while redundant labels may make a call easier to understand locally.

I agree with the premise. I’m less sure it changes the conclusion.

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

`timeout` is not merely an optional syntactic argument to this particular invocation. It is one field in the `RequestOptions` concept.

And if agents really do make typing cost increasingly irrelevant, then the principal downside of these slightly-more-verbose Rust idioms gets cheaper too.

The robots can type `RequestOptions` for me. Great.

## Keep the functions boring

I’m not philosophically opposed to Rust ever gaining named arguments.

There may be a proposal that finds a tiny, coherent design which handles patterns, function pointers, traits, evaluation order, compatibility, and all the other sharp edges Steve describes. Language design is full of features that initially look impossible and eventually acquire a satisfying formulation.

But I don’t feel much urgency.

Stable Rust already gives me:

* named arguments: **struct fields**
* optional arguments: **`Option`**
* default arguments: **`Default` + struct update syntax**
* overloads for convenience: **differently named functions**
* overloads across input types: **traits / `Into` / `AsRef`**
* heterogeneous alternatives: **enums**
* options hashes: **options structs**
* repeated homogeneous arguments: **slices and iterators**
* variable arguments with custom syntax: **macros**
* `foo=foo` forwarding noise: **field-init shorthand**

None is a perfect substitute. Collectively, though, they cover a remarkable amount of the territory. And they do it by reusing features Rust already needs rather than teaching function calls how to become a little programming language of their own.

Maybe Rust eventually gets named arguments. Until then, we have named arguments at home.

I kind of like them.
