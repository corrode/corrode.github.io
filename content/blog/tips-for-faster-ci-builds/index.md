+++
title = "Tips for Faster Rust CI Builds"
date = 2025-01-28
updated = 2025-06-12
draft = false
template = "article.html"
[extra]
series = "Rust Insights"
resources = [
  "[Tips for faster compile times](/blog/tips-for-faster-rust-compile-times/) - A general article on speeding up Rust compile times", 
  "[Fast Rust Builds by Matklad](https://matklad.github.io/2021/09/04/fast-rust-builds.html#CI-Workflow)"
]
hero = "hero.svg"
+++

I've been working with many clients lately who host their Rust projects on GitHub.
CI is typically a bottleneck in the development process since it can significantly slow down feedback loops.
However, there are several effective ways to speed up your GitHub Actions workflows!

{% info(title="Want a Real-World Example?", icon="crab") %}

Check out this production-ready GitHub Actions workflow that implements all the tips from this article:
[click here](https://github.com/lycheeverse/lychee/blob/master/.github/workflows/ci.yml).

Also see Arpad Borsos' [workflow templates](https://github.com/Swatinem/rust-gha-workflows) for Rust projects.

{% end %}

## Use Swatinem's cache action

This is easily my most important recommendation on this list.

My friend [Arpad Borsos](https://github.com/swatinem), also known as Swatinem, has created a cache action specifically tailored for Rust projects.
It's an excellent way to speed up any Rust CI build and requires no code changes to your project.

```yaml
name: CI

on: 
  push:
    branches:
      - main
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest-arm64

    env:
      CARGO_TERM_COLOR: always

    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable

      # The secret sauce!
      - uses: Swatinem/rust-cache@v2

      - run: |
          cargo check
          cargo test
          cargo build --release
```

The action requires no additional configuration and works out of the box.
There's no need for a separate step to store the cache — this happens automatically through a post-action.
This approach ensures that broken builds aren't cached, and for subsequent builds, you can save several minutes of build time.

Here's the [documentation](https://github.com/Swatinem/rust-cache) where you can learn more. 

## Use the `--locked` flag

When running `cargo build`, `cargo test`, or `cargo check`, you can pass the `--locked` flag to prevent Cargo from updating the `Cargo.lock` file.

This is particularly useful for CI operations since you save the time to update dependencies.
Typically you want to test the exact dependency versions specified in your lock file anyway.

On top of that, it ensures reproducible builds, which is crucial for CI.
From the [Cargo documentation](https://doc.rust-lang.org/cargo/commands/cargo-install.html):

> The `--locked` flag can be used to force Cargo to use the packaged `Cargo.lock` file if it is available. This may be useful for ensuring reproducible builds, to use the exact same set of dependencies that were available when the package was published. 

Here's how you can use it in your GitHub Actions workflow: 

```yaml
- run: cargo check --locked
- run: cargo test --locked
```

## Use `cargo-chef` For Docker Builds 

For Rust Docker images, [`cargo-chef`](https://github.com/LukeMathWalker/cargo-chef) can significantly speed up the build process by leveraging Docker's layer caching:

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

Alternatively, if you don't mind a little extra typing, you can write your own Dockerfile without `cargo-chef`:

<details>
<summary>Click to expand</summary>

```Dockerfile
FROM rust:1.81-slim-bookworm AS builder

WORKDIR /usr/src/app

# Copy the Cargo files to cache dependencies
COPY Cargo.toml Cargo.lock ./

# Create a dummy main.rs to build dependencies
RUN mkdir src && \
    echo 'fn main() { println!("Dummy") }' > src/main.rs && \
    cargo build --release && \
    rm src/main.rs

# Now copy the actual source code
COPY src ./src

# Build for release
RUN touch src/main.rs && cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy the build artifact from the build stage
COPY --from=builder /usr/src/app/target/release/your-app /usr/local/bin/

# Set the startup command to run our binary
CMD ["your-app"]
``` 

</details>

## Environment Flags To Disable Incremental Compilation 

Rust provides environment flags to disable incremental compilation.
While incremental compilation speeds up local development builds, in CI it can actually slow down the process due to dependency tracking overhead and negatively impact caching.
So it's better to switch it off:

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

## Disable Debug Info

While debug info is valuable for debugging, it significantly increases the size of the `./target` directory, which can harm caching efficiency.
It's easy to switch off:

```yaml
env:
  CARGO_PROFILE_TEST_DEBUG: 0
```

## Use `cargo nextest`

`cargo nextest` enables parallel test execution, which can substantially speed up your CI process.
While they claim a 3x speedup over `cargo test`, in CI environments I typically observe around 40%
because the runners don't have as many cores as a developer machine.
It's still a nice speedup.

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

These release profile settings can significantly improve build times and binary size:

```toml
[profile.release]
lto = true
codegen-units = 1
```

- LTO (Link Time Optimization) performs optimizations across module boundaries, which can reduce binary size and improve runtime performance.
- Setting `codegen-units = 1` trades parallel compilation for better optimization opportunities. While this might make local builds slower, it often speeds up CI builds by reducing memory pressure on resource-constrained runners.

If you only want to apply these settings in CI, you can use the `CARGO_PROFILE_RELEASE_LTO` and `CARGO_PROFILE_RELEASE_CODEGEN_UNITS` environment variables:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      CARGO_PROFILE_RELEASE_LTO: true
      CARGO_PROFILE_RELEASE_CODEGEN_UNITS: 1
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: cargo build --release --locked
```

## Use Beefier Runners

GitHub Actions has recently announced that
Linux ARM64 hosted runners are now available for free in public repositories. 
[Here's](https://github.blog/changelog/2025-01-16-linux-arm64-hosted-runners-now-available-for-free-in-public-repositories-public-preview/) the announcement.

Switching to ARM64 provides up to 40% performance improvement and is straightforward. Simply replace `ubuntu-latest` with `ubuntu-latest-arm64` in your workflow file:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest-arm64
```

However, in my [tests](https://github.com/lycheeverse/lychee/pull/1614), the downside was that it took a long time until a runner was allocated to the job. The waiting time dwarfed the actual build time. I assume GitHub will add more runners in the future to mitigate this issue.

If you are using Rust for production workloads, it's worth looking into dedicated VMs.
These are not free, but in comparison to the small GitHub runners, you can get a significant uplift on build times.

Any provider will do, as long as you get a VM with a decent amount of CPU cores (16+ is recommended)
and a good amount of RAM (32GB+).
Hetzner Cloud is a popular choice for this purpose because of its competitive pricing.
[Spot instances](https://cloud.google.com/solutions/spot-vms) or [server auctions](https://www.hetzner.com/sb/) can be a good way to save money.
Here are some setup resources to get you started:

- [Awesome Runners](https://github.com/jonico/awesome-runners)
- [Using Hetzner Cloud GitHub Runners for Your Repository](https://altinity.com/blog/slash-ci-cd-bills-part-2-using-hetzner-cloud-github-runners-for-your-repository)
- [Runs-on, a Github Actions hoster](https://runs-on.com/)
- [Awesome HCloud Repo](https://github.com/hetznercloud/awesome-hcloud)
- [HCloud Runner](https://github.com/Cyclenerd/hcloud-github-runner)

There are services like [Depot](https://depot.dev/), which host runners for you.
They promise large speedups for Rust builds, but I haven't tested them myself.

## Automate Dependency Updates 

Implement [dependabot](https://docs.github.com/en/code-security/getting-started/dependabot-quickstart-guide) or [Renovate](https://docs.renovatebot.com/)
to automate dependency updates.
Instead of manually creating PRs for updates and waiting for CI, these bots handle this automatically, creating PRs that you can merge when ready.

Renovate has a bit of an edge over dependabot in terms of configurability and features. 

## Streamline Release Creation 

[`release-plz`](https://release-plz.ieni.dev/) automates release creation when PRs are merged.
This GitHub action eliminates the manual work of creating releases and is highly recommended for maintaining a smooth workflow.

![release-plz website screenshot](release-plz.jpg)

## Optimize Your Rust Code

If you've implemented all these optimizations and your builds are still slow, it's time to optimize the Rust code itself. I've compiled many tips in my other blog post [here](/blog/tips-for-faster-rust-compile-times/).

## Conclusion

Remember that each project is unique.
Start with the easier wins like Swatinem's cache action and `--locked` flag, then progressively implement more advanced optimizations as needed. Monitor your CI metrics to ensure the changes are having the desired effect.

{% info(title="Need Professional Support?", icon="crab") %}

Is your Rust CI still too slow despite implementing these optimizations?
I can help you identify and fix performance bottlenecks in your build pipeline.
[Book a free consultation](/about) to discuss your specific needs.

{% end %}