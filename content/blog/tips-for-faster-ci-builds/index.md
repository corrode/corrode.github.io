+++
title = "Tips for Faster Rust CI Builds"
date = 2025-01-18
draft = false
template = "article.html"
[extra]
series = "Rust Insights"
resources = [
    "[Fast Rust Builds by Matklad](https://matklad.github.io/2021/09/04/fast-rust-builds.html#CI-Workflow)"
]
hero = "hero.svg"
+++

I’ve been working with a lot of clients lately who host their Rust projects on GitHub.
CI is typically a bottleneck in the development process, because it's a major stopper for fast feedback loops.
Not all is lost, though! Here's a few tricks to make the most of GitHub Actions.

## Use Swatimem's cache action

This is easily my biggest recommendation on this list.

My friend [Arpad Borsos](https://github.com/swatinem), also known as Swatimem, has created a cache action that is specifically tailored for Rust projects.
It's a very easy way to speed up any Rust CI build and requires no code changes.

```yaml
name: CI

on: 
  - push
  - pull_request

jobs:
  build:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    name: Test `cargo check/test/build` on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}

    env:
      CARGO_TERM_COLOR: always

    steps:
      - uses: actions/checkout@v4

      - run: rustup toolchain install stable --profile minimal --no-self-update

      # The magic sauce
      - uses: Swatinem/rust-cache@v2

      - run: |
          cargo check
          cargo test
          cargo build --release
        working-directory: tests
```

Note that you don't need any additional configuration. It works out of the box.
There is no step needed to store the cache, this is done by an automatic post-action.
This way, it also makes sure not to cache broken builds etc.

For repeated builds, this can save you a lot of time -- many minutes, in fact.

## Use the `--locked` flag

When you run `cargo build`, `cargo test`, or `cargo check`, you can pass the `--locked` flag to make sure that Cargo doesn't update the `Cargo.lock` file.

This is especially useful when you're running `cargo check` or `cargo test`, because you don't need to update the dependencies to run these commands.

```yaml
- run: cargo check --locked
- run: cargo test --locked
```

## Use the new ARM64 runners

Linux arm64 hosted runners now available for free in public repositories. 
[Here's](https://github.blog/changelog/2025-01-16-linux-arm64-hosted-runners-now-available-for-free-in-public-repositories-public-preview/) the announcement.

Switching to ARM64 promises a 40% perf boost and it's super easy to do. Just replace `ubuntu-latest` with `ubuntu-latest-arm64` in your workflow file.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest-arm64
```

## Use `Cargo-Chef` For Docker Builds 

If you're building a Docker image for your Rust application, you can use the [`cargo-chef`](https://github.com/LukeMathWalker/cargo-chef) tool to speed up the build process.

```Dockerfile
FROM lukemathwalker/cargo-chef:latest-rust-1 AS chef
WORKDIR /app

FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

FROM chef AS builder 
COPY --from=planner /app/recipe.json recipe.json
# Build dependencies - this is the caching Docker layer!
RUN cargo chef cook --release --recipe-path recipe.json
# Build application
COPY . .
RUN cargo build --release --bin app

# We do not need the Rust toolchain to run the binary!
FROM debian:bookworm-slim AS runtime
WORKDIR /app
COPY --from=builder /app/target/release/app /usr/local/bin
ENTRYPOINT ["/usr/local/bin/app"]
```

## Environment Flags To Avoid Incremental Compilation 

Rust comes with a set of environment flags that can be used to avoid incremental compilation.
Why would you want to avoid it? 
Incremental compilation is a feature that speeds up local builds, but in CI, the overhead of tracking dependencies can slow down the build process.
It also has a negative impact on caching.

```yaml
name: Build

on:
  pull_request:
  push:
    branches:
      - main

env:
  # Disable incremental compilation for faster from-scratch builds
  CARGO_INCREMENTAL: 0

jobs:
  build:
    runs-on: ... 
    steps:
      ...
```

## Disable debuginfo and warnings

```yaml
env:
  CARGO_PROFILE_TEST_DEBUG: 0
```

Debuginfo is useful for debugging, but it makes the `./target` directory much bigger, again harming caching.


## Use `cargo nextest`

This way, you can run tests in parallel, which can speed up the CI process.
They claim it's 3x faster than `cargo test`, but in CI, I typically see a 40% improvement, which is still a lot.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: taiki-e/install-action@nextest
      - uses: Swatinem/rust-cache@v2
      - name: Compile
        run: cargo check --locked
      - name: Test
        run: cargo nextest 
```

## `Cargo.toml` Settings

```toml
[profile.release]
lto = true
codegen-units = 1
```

## Automate Dependency Updates 

Use a tool like [dependabot](https://docs.github.com/en/code-security/getting-started/dependabot-quickstart-guide) to keep your dependencies up to date. 
This way, you don't have to wait create a PR to update dependencies and wait for CI to finish.
Instead, dependabot will create a PR for you, and you can merge it when you're ready.

## Quick Release Creation 

[`release-plz`](https://release-plz.ieni.dev/) is a GitHub action that automatically creates a release when a PR is merged.
It speeds up the process of creating a release, because you don't have to do it manually.
I highly recommend it.


## Optimize your Rust code

If you did all that and your builds are still slow, it's time to roll up your sleeves and optimize the Rust code itself. I've collected many tips in my other blog post [here](/blog/tips-for-faster-rust-compile-times/).


{% info(title="Need Professional Support?", icon="crab") %}

Your CI builds are still slow? 
You followed all the tips and tricks, but your Rust project needs to be optimized?
Don't waste any more time; let's look at your project together.
[Get in touch for a free consultation](/about).

{% end %}
