+++
title = "Long-term Rust Project Maintenance"
date = 2024-04-14
template = "article.html"
[extra]
series = "Rust Ecoystem"
+++

Rust has reached a level of maturity where it is being used for critical
infrastructure, replacing legacy systems written in C or C++, and needs to be
maintained for years or even decades to come.

By some estimates, the cost of maintaining a product is more than [90% of the
software's total cost](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3610582/). 

Such environments require minimal downtime, high reliability, and low
operational costs, so it is reassuring that the Rust core team highlights its
commitment to these values in their post ["Stability as a
Deliverable."](https://blog.rust-lang.org/2014/10/30/Stability.html)

The following is a guide to long-term Rust project maintenance, based on my
experience helping clients with medium- to large Rust projects which are critical
to their business. A lot of the advice is relevant to other languages as well,
but I will try to point out aspects that are specific to the Rust ecosystem.

The target audience are lead developers and decision-makers
responsible for ensuring the long-term success of Rust projects within their
organization.




## Team Dynamics

Introducing Rust is often a disruptive change
and requires long-term commitment. [It is important to have the backing of both the
team and leadership to make this transition successful.](https://mainmatter.com/blog/2023/12/13/rust-adoption-playbook-for-ctos-and-engineering-managers/)

On top of that, every language comes with its own set of tools,
libraries, and best practices. It takes time for a team to become proficient in
a new environment, and Rust is no exception.

Proficiency in Rust and its ecosystem is the first step towards long-term
maintenance as projects will be set up with the right architecture and best
practices in mind.

Investing in Rust training and team-augmentation is a good way to accelerate
this process. While it higher upfront costs, it will pay off in the long run.

## Project Longevity

### Stable Rust Over Nightly

Rust has a stable release every six weeks, with new features and bug fixes.
The stable release is the most reliable and well-tested version of Rust.
In contrast, the nightly release is a daily snapshot of the Rust compiler,
which includes the latest features and bug fixes, but is less stable and
more likely to break your code.

For long-term maintenance, it's important to stick to the stable release
of Rust. This ensures that your code will continue to compile and run
without modification, even as the language evolves.

There are only very few cases where nightly Rust is necessary, such as when
your project depends on a feature that is only available in nightly.

> If you are writing code that should live for a while, or a library that is
> aimed to be widely used, avoiding nightly features is likely your best bet.
> &mdash; Andre Bogus in [The nightly elephant in the room](https://www.getsynth.com/docs/blog/2021/10/11/nightly)

### Editions

Rust has a strong focus on backward compatibility.

An often underrated feature which is not found in other languages is Rust's [edition
system](https://doc.rust-lang.org/edition-guide/editions/). It ensures
[stability without
stagnation](https://blog.rust-lang.org/2014/10/30/Stability.html#the-plan):
every three years, a new edition is released, which allows the language to
evolve without breaking existing code. For example, the 2018 edition introduced
the `async` and `await` keywords, which are now widely used in Rust codebases;
but code written in the 2015 edition still compiles and runs without
modification. Mixing crates from different editions is
possible as well.

As a result, organizations have time to migrate their codebase to the new
edition at their own pace.

### Conservative use of Rust language features

Rust is a language with a lot of powerful features, such as macros, traits,
generics, and lifetimes. While these features can make code more expressive and
efficient, they can also make code harder to read and maintain.

For long-term maintenance, it's important to be conservative about using
advanced language features. At times, this might come at the cost of
performance or verbosity, but the benefit is code that is easier to understand
by a larger part of the team.

Here are a few rules of thumb to follow:

- **Use macros only for boilerplate code**: Macros can be powerful tools for
  code generation, but can be hard to read and debug and take a toll on
  compile times. Use them sparingly and only for code that is repetitive.
  [Know When to Use Macros vs. Functions](https://earthly.dev/blog/rust-macros/)
- **Avoid complex trait bounds**: Traits are a common way to abstract over types
  in Rust, but complex [trait bounds](https://doc.rust-lang.org/rust-by-example/generics/bounds.html)
  can lead to hard-to-understand error messages and obfuscate business logic.
- **`clone` is fine**: While `clone` can be a performance bottleneck, it is
  often the simplest way to avoid lifetimes and keep code readable. 
  In many cases, the performance overhead is negligible.
- **Conservative use of async/await**: Especially in core libraries, it's
  important to be conservative about exposing async functions in the public API.
  This ensures that the library can be used in both synchronous and asynchronous
  contexts and does not impose a specific runtime on the user. 
  I wrote more about this in [The State of Async Rust](https://corrode.dev/blog/async/).

I discuss these and other antipatterns in my talk [The Four Horsemen of Bad
Rust
Code](https://fosdem.org/2024/schedule/event/fosdem-2024-2434-the-four-horsemen-of-bad-rust-code/).

## Dependencies

### Rust's Philosophy on Dependencies

One of the most important aspects of long-term Rust maintenance is being
conservative about dependencies.

Rust has a very active ecosystem, with thousands of crates available on
[crates.io](https://crates.io/), but there is no guarantee that a crate will be
maintained in the long term; and even if it is, you need to [trust the team
behind it](https://tweedegolf.nl/en/blog/104/dealing-with-dependencies-in-rust).
Security fixes in dependencies could take a long time to be released.

As a consequence, every dependency should be seen as a liability.

Rust has a relatively small standard library.
This is in part to avoid a situation similar to Python's extensive standard library, where
parts of it are discouraged from being used:

> Python’s standard library is piling up with cruft, unnecessary duplication of
> functionality, and dispensable features. &mdash; [PEP 594](https://peps.python.org/pep-0594/) 

In contrast, Rust encourages small, single-purpose modules, similar to
Node.js.

### Limit The Number Of Dependencies

While it's tempting to use many third-party crates to speed up development, it's
important to **keep the number of dependencies to a minimum** for better long-term
maintenance. It will limit your exposure to breaking changes and security
vulnerabilities.

Moreover, each dependency has a compounding effect:

- Longer compile times
- Test times
- Complexity in build scripts and CI
- etc.

### Choosing Dependencies

Now that we've established the importance of limiting dependencies, how do you
choose the right ones? Here are some factors to consider when choosing a crate:

- **Popularity**: The more popular a crate is, the more likely it is to be
  maintained and updated. Check the number of downloads, the number of open
  issues, and the last commit date. Here is a list of [popular Rust
  crates](https://lib.rs/std).
- **License**: Make sure the crate's license is compatible with your project's
  license. The most common licenses in the Rust ecosystem are MIT and Apache 2.0,
  which are both permissive licenses. However, there are crates with more
  restrictive licenses, such as GPL or AGPL, which might not be suitable for
  your project.
- **Maintenance**: Check the crate's GitHub repository for signs of active
  maintenance. Are issues being addressed? Are pull requests being merged?
  Is the crate following best practices?
  Prefer crates from well-known community members or companies, as they are
  more likely to be maintained in the long term.
- **Security**: Security vulnerabilities can be a major headache in the long
  term. Make sure the crate has a good security track record and that the
  maintainers are responsive to security issues.
  Check [RustSec](https://rustsec.org/) for known vulnerabilities in Rust crates
  before adding them to your project.
  Run [cargo-audit](https://crates.io/crates/cargo-audit) for known vulnerabilities in your dependencies.

Take a look at [blessed.rs](https://blessed.rs/) for a list of recommended
crates in the Rust ecosystem.

For a case study on how to reduce the number of dependencies in a real-world
Rust project, read [Sudo-rs dependencies: when less is
better](https://www.memorysafety.org/blog/reducing-dependencies-in-sudo/) by
Ruben Nijveld from Prossimo.



### Keep Dependencies Up-to-Date

A common reaction to hedge the risks of exposing your project to breaking
changes is to pin dependencies to a specific version. While this sounds like a
good idea, it can in fact result in the opposite: a project with outdated
dependencies that are no longer maintained and have known security
vulnerabilities. This is a big maintenance burden.

Instead, it is better to be proactive about keeping dependencies up-to-date:

- **Use [`cargo outdated`](https://github.com/kbknapp/cargo-outdated)**: The `cargo outdated` command shows you which
  dependencies are out of date. Run it regularly to keep track of new versions.
- **Automate dependency updates**: Use tools like [Dependabot](https://dependabot.com/)
  or [Renovate](https://www.mend.io/renovate/) to receive automated pull
  requests for dependency updates.
- **Use `cargo update`**: The `cargo update` command updates your dependencies
  to the latest version that matches the version constraints in your `Cargo.toml`.
  Run it regularly to update your dependencies to the latest versions.
- **Use `cargo tree`**: The `cargo tree` command shows you a tree of your
  dependencies, which can help you find duplicate or outdated dependencies
  &mdash; including transitive dependencies.
- Run [`cargo audit`](https://crates.io/crates/cargo-audit) regularly to check
  for known security vulnerabilities in your dependencies.

Try not to skip any major versions of your dependencies, as this can make it
harder to upgrade in the future. Be proactive about replacing deprecated or
unmaintained dependencies.

For major dependencies (like a web framework or your async runtime) it's a good
idea to follow their release notes or blog posts to stay up-to-date with
upcoming changes.

Keep in mind that it takes time for the broader ecosystem to catch up with new
releases of these major dependencies, so it can take a while before you can
safely upgrade. In such a case, it's a good idea to add regular reminders to
your calendar to handle the upgrade.

### Stick to `std` and `core` where possible

The Rust standard library is well-maintained and has a strong focus on backwards
compatibility. It is a good idea to stick to `std` where possible.

For example, the `std::collections` module provides a wide range of data
structures, such as `HashMap`, `Vec`, and `HashSet`, which are well-tested.
While there are great third-party crates that provide similar data structures,
such as `hashbrown` or `indexmap`, which might be faster or have additional
features, it is often better to stick to the standard
library, as it is used by a wide range of projects and guaranteed to be
maintained in the long term.

### Use stable dependencies 

Crates which follow semver and reach version 1.0.0 are considered stable and
should be preferred over crates that are below version 1.0.0. This is because
crates below version 1.0.0 are allowed to make breaking changes in minor
versions, which can lead to unexpected breakage in your project.


### Reduce the number of features you use in your dependencies

## Guidelines for API design

Software that gets maintained for a long time is often critical and heavily used
by other software. Changing an API can break downstream users and cause churn.
Defensive API design can minimize the risk of breaking changes.

Here are some guidelines:

- **Minimize the public API surface**: 
  It's very hard to remove features once they are public. Only expose what is
  absolutely necessary for users to interact with your library. This sounds
  obvious, but it's easy to expose too much in a public API. Private functions
  and structs prevent implementation details from leaking out of modules, which
  will make refactoring easier in future.
- **Make enums non-exhaustive**: When defining an enum, use the `#[non_exhaustive]`
  attribute to allow adding new variants in the future without breaking
  existing code. (Also see this [discussion in the hyperium/http crate](https://github.com/hyperium/http/issues/188).)
- **Hide implementation details behind own types**: Use the [newtype
  pattern](https://rust-unofficial.github.io/patterns/patterns/behavioural/newtype.html#motivation)
  to hide implementation details and prevent users from relying on them. For
  example, instead of exposing that you depend on a specific crate, wrap it in a
  newtype, so use `pub Request(reqwest::Request)` instead of exposing the
  dependency directly.
- **Use semver**: Follow the [Semantic Versioning](https://semver.org/) guidelines
  to communicate changes to your users. This will help them understand the
  impact of a new release and make it easier to upgrade.

For further information, the Rust team has published a [Rust API Guidelines
Checklist](https://rust-lang.github.io/api-guidelines/checklist.html), which is
well worth reading.


4. Software Architecture
  controversely, maintaining a codebase for a long time doesn't mean you should not touch it.
  quite the opposite, it requires constant effort  and work.
  some of the most robust codebases in the world are constantly being refactored and rewritten

    Principles for durable software design:
        Simplicity and adherence to SOLID principles
        [Study hexagonal architecture](https://alexis-lozano.com/hexagonal-architecture-in-rust-1/) and the onion architecture pattern or ports and adapters pattern
        Domain-driven design and bounded contexts without dependencies. Keep it clean from side-effects.
        Low coupling and high cohesion
        Don't be afraid to take ownership: refactor and rewrite when necessary. Rust makes it easy to refactor with its strong type system and borrow checker.
        Avoiding premature optimization and over-engineering
        Learn about idiomatic Rust patterns in order to write code that is easy to maintain and follows the best practices of the Rust community.
    Strategies for easy code extensibility and refactoring


5. Documentation and Testing
    Importance of thorough documentation and coding standards
    The role of testing:
        Writing extensive tests as a form of documentation
        Setting up continuous integration for regular testing

6. Handling Unsafe Code

    Risks associated with unsafe code in Rust
    Best practices for minimizing and isolating unsafe code

7. Tooling and Infrastructure

    Importance of maintaining and updating development and operational tools
    Testing and monitoring infrastructure to ensure reliability
    The only constant is change: while your codebase may be stable, the tools and infrastructure around it will evolve over time. Be prepared to adapt and update your tooling to keep pace with the changing landscape of software development.

9. Conclusion

    Recap of key points for maintaining Rust applications long-term
    Encouragement to prioritize robustness and simplicity for business-critical functions
    Reference to the 'Rust in production' podcast for further insights on Rust in enterprise applications


Further reading

- [Cost of a Dependency - Lee Campbell](https://www.youtube.com/watch?v=Y7oqumBxWGo)
- [Software Maintenance Costs](https://maddevs.io/customer-university/software-maintenance-costs/)