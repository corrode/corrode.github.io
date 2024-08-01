+++
title = "Rust vs C++: A Real-World Perspective"
date = 2024-08-01
template = "article.html"
[extra]
hero = "hero.svg"
series = "Rust Insights"
credits = [
  "<a href='https://www.freepik.com'>Image by vectorpouch on Freepik</a>"
]
+++

The real-world implications of choosing one language over the other are often more nuanced and practical.
This is especially true for the ongoing debate between Rust and C++.
It's easy to get lost in theoretical arguments about safety, performance, and language features. 

I recently sat down with [Tyler Weaver](https://tylerjw.dev), a software engineer with a decade of C++ experience and several years of Rust under his belt. He shared some great insights on the practical aspects of working with both languages in production, which I thought would be valuable to share.

While Tyler's perspective is based on his personal experience, I believe his insights are quite valuable for anyone looking for hands-on experiences with both languages.

## Rust is a Force Multiplier

One of Tyler's most striking observations is that "Rust is a force multiplier." In C++ projects, developers often find themselves barely having time to get things working, let alone optimizing or improving their code. Rust, on the other hand, handles many low-level details by design, allowing developers to focus on higher-level concerns instead.
As Tyler puts it, you can "spend more time on useful things because Rust handles the details for you."

This effect extends to code reviews as well. Tyler estimates that "code reviews take half the time" in Rust compared to C++. This efficiency gain is not just about saving time; it allows for more thorough reviews and potentially catches more issues before they make it into production.

This aligns well with an [observation by Google](https://youtu.be/6mZRWFQRvmw?t=27012) on re-writing C++ into Rust:

> In every case, we've seen a decrease by more than 2x in the amount of effort required to both 
> build the services written in Rust, as well as maintain and update those services. [...]
> C++ is very expensive for us to maintain.

## Painless Refactoring

Perhaps one of the most significant advantages Rust offers is in the realm of refactoring. Tyler emphasizes that "Rust makes refactoring painless" and allows developers to "trust your refactors." This "worry-free refactoring" is a stark contrast to C++, where making significant changes can be risky and time-consuming.

"In C++, removing things is so expensive," both in terms of development time and the potential for introducing bugs. Rust's ownership system and compiler checks make it much easier to make sweeping changes with confidence. This capability is particularly valuable for large-scale projects where regular refactoring is essential for maintaining code quality and adapting to changing requirements.

For example, Mozilla had been trying to parallelize the CSS layout engine in Firefox twice in C++. 
Both attempts were abandoned.  Eventually, they succeeded on the third attempt using Rust in the Servo project, which was later integrated into Firefox as part of [Project Quantum](https://hacks.mozilla.org/2017/08/inside-a-super-fast-css-engine-quantum-css-aka-stylo/).
The team credited Rust's safety guarantees as the reason why they were able to be successful on the third attempt. Here's the section from the [talk](https://www.youtube.com/watch?v=Y6SSTRr2mFU) by Josh Matthews from the Servo team.

Jeremy Soller from System76 recently [shared a similar sentiment in the Rust in Production podcast](https://corrode.dev/podcast/s02e07-system76/?t=1%3A13%3A18):

> Rust [has] capability [of] doing extremely, extremely concurrent things safely. There was no way to write this kind of code in C or C++ without considerable time planning beforehand.

## The Cost of Complexity

Tyler points out that "accidental complexity is quite high in C++." This complexity often manifests in subtle ways that can accumulate over time, making codebases increasingly difficult to maintain. In contrast, Rust's design encourages simplicity and clarity, allowing developers to "focus on the right things."

Tyler emphasizes that "none of our software projects are as simple as they could be." Rust's approach to memory management and its emphasis on explicit handling of side effects can lead to simpler, more maintainable code structures.

If you are curious to learn more about maintaining large C++ codebases and migrating to Rust, listen to [this interview with Brendan Abolivier from Thunderbird](https://corrode.dev/podcast/s02e03-thunderbird) for our "Rust in Production" podcast series.

## The Tooling Advantage

Better tooling leads to better projects, and Rust has a significant edge in this area. From cargo, Rust's package manager and build tool, to the language server protocol implementation, Rust's tooling ecosystem is modern and integrated. This cohesive tooling environment contributes to more efficient development workflows and higher-quality output.

## Addressing the Criticisms

While Tyler's perspective paints a very positive picture of Rust, it's important to address some common criticisms of the language:

1. **Learning Curve**: Rust is known for having a steeper learning curve than C++, particularly for developers accustomed to more traditional programming paradigms. The borrow checker, while powerful, can be frustrating for newcomers.
However, according to Google's experience, more than 2/3 of respondents are confident in contributing to a Rust codebase within two months or less when learning Rust. Further, a third of respondents become as productive using Rust as other languages in two months or less. Within four months, that number increased to over 50%.
 Read more about the learning curve in [Why Rust](https://corrode.dev/blog/why-rust/).

2. **Ecosystem Maturity**: While growing rapidly, Rust's ecosystem is still not as mature as C++'s in some domains. Certain specialized libraries or frameworks may not be available or as feature-complete in Rust.

3. **Industry Adoption**: Despite growing interest, Rust has not yet achieved the same level of industry-wide adoption as C++, which may be a consideration for some projects or companies. C++ is still dominant in domains like game development, high-performance computing, and embedded systems.


## Balancing Act: C++ and Rust Interoperability

Recognizing that a complete switch from C++ to Rust is not always feasible or desirable, Tyler suggests that "dumb interop is the best strategy for C++ and Rust to work together." This approach allows teams to gradually introduce Rust into existing C++ codebases, leveraging the strengths of both languages.

Tyler wrote a series of blog posts on [Rust and C++ interop](https://tylerjw.dev/posts/rust-cpp-interop/) that provide practical guidance on integrating Rust into C++ projects, which covers FFI bindings, CMake (a build system generator for C++ projects), Cxx (a code generation tool), Conan (a C++ package manager), and more.

It is recommended to start with the most safety-critical parts of your codebase:

> What you have to do is think about how important security is at each level of the stack and how to address it in small incremental ways. - [Jeremy Soller in the Rust in Production podcast](https://corrode.dev/podcast/s02e07-system76/?t=47%3A52)

## Conclusion

While C++ remains a powerful and widely-used language, Rust offers significant advantages in terms of developer productivity, code maintainability, and long-term project health. As Tyler's experiences illustrate, the benefits of Rust often become most apparent in the day-to-day work of software development – in code reviews, refactoring, and managing complexity.

However, the choice between Rust and C++ is not a one-size-fits-all decision. It depends on factors such as project requirements, team expertise, existing codebases, and industry-specific considerations. What's clear is that Rust is providing developers with powerful tools to build more reliable and maintainable software, and its influence is likely to grow in the coming years.

{% info(headline="Make the most of Rust", icon="crab") %}

Is your company considering to migrate from C++ to Rust? 
I offer consulting services to get you up to speed with your Rust projects, from training your team to code reviews and architecture consulting. 
Check out my [services page](/services) to learn more.

{% end %}

## Recommended Reading

For those interested in diving deeper into the topics discussed in this article, here are a few book recommendations:

- ["Grokking Simplicity"](https://www.manning.com/books/grokking-simplicity) by Eric Normand. Published by Manning.
- ["Programming Rust"](https://www.oreilly.com/library/view/programming-rust-2nd/9781492052586/) by Jim Blandy and Jason Orendorff. Published by O'Reilly.
- ["Effective Modern C++"](https://www.oreilly.com/library/view/effective-modern-c/9781491908419/) by Scott Meyers. Published by O'Reilly.

These three books teach you how to write clean, maintainable code no matter if you are using Rust or C++.

If you like to learn more about Tyler's work, check out his [blog](https://tylerjw.dev/) and GitHub [profile](https://github.com/tylerjw).