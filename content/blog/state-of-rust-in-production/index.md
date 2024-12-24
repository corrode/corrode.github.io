+++
title = "The Pragmatic Guide to Rust in Production: Real Stories from the Field"
date = 2024-12-23
template = "article.html"
[extra]
series = "Rust Insights"
+++

## Real-World Benefits of Choosing Rust

Companies adopting Rust consistently report dramatic improvements across multiple dimensions:

### Performance and Resource Usage

PubNub achieved 5x better performance and memory reduction from 1GB to 30MB when replacing their PyPy service

> "When we replace that service with Rust we saw another 5x boost not only in memory but in performance as well. That means you use one-fifth of the memory in Rust compared to PyPy... It's more like 30 megabytes or something like that in Rust versus a gigabyte."
> -- Stephen Blum, PubNub ([18:46](https://corrode.dev/podcast/s01e02-pubnub?t=18%3A46))

Matic achieved such substantial improvements that they've standardized on Rust

> "Easily 95% of what we do is in Rust... We're past the point where we even try to build things in other languages because we've had so much success with Rust."
> -- Eric Seppanen, Matic ([03:13](https://corrode.dev/podcast/s02e04-matic?t=03%3A13))

### Developer Productivity

Teams report significantly improved code maintainability

> "Refactoring stuff is so nice in Rust compared to Ruby or any other language that I've done because you change the one thing... And then it's like, here's the 47 other places that you're going to have a problem with. And you're like, I'll just start going through the list."
> -- Scott Chacon, GitButler ([34:58](https://corrode.dev/podcast/s03e04-gitbutler?t=34%3A58))

The ecosystem enables faster development compared to traditional systems languages

> "The Rust-created ecosystem in general has been such a boon to us from a productivity perspective, compared to the C++ world where using dependencies is so challenging."
> -- Micah Wylde, Arroyo ([25:14](https://corrode.dev/podcast/s01e04-arroyo?t=25%3A14))

### Quality and Reliability

Companies report near-elimination of entire classes of runtime bugs

> "Once your code builds, you're sure that you have a certain standard in terms of safety, in terms of quality, and that you have a nice and more maintainable and less error-prone code."
> -- Brendan Abolivier, Thunderbird ([57:24](https://corrode.dev/podcast/s02e03-thunderbird?t=57%3A24))

The type system enforces correctness by design

> "Having actual types and very very strong types... I feel like at Oxide people were coming up with the world's weirdest types but they were like very very readable and they made the whole thing readable."
> -- Jessie Frazelle, Zoo ([1:02:25](https://corrode.dev/podcast/s03e05-zoo?t=1%3A02%3A25))

### Business Impact

Companies are making Rust their default choice for new services

> "Right now Rust is the most popular language at PubNub by far. All of our new services are typically elected to be written in Rust. Everything going forward will be Rust."
> -- Stephen Blum, PubNub ([17:15](https://corrode.dev/podcast/s01e02-pubnub?t=17%3A15))

Teams report increased confidence in tackling complex problems

> "We have enough confidence in our Rust abilities that we're willing to choose the best hardware and just trust that we will figure out a way to make it work."
> -- Eric Seppanen, Matic ([06:50](https://corrode.dev/podcast/s02e04-matic?t=06%3A50))

## Look Beyond Raw Performance When Choosing Rust

The decision to adopt Rust rarely comes down to performance alone. The language offers a unique combination of safety, maintainability, and reliability.

> "The language lends itself really well for maintainability and really exactness. There is no time that I'm like, 'oh, is this going to fail with some random input?' It's like, no, you directly define what the input is going to be."
> -- Jessie Frazelle, Zoo ([59:36](https://corrode.dev/podcast/s03e05-zoo?t=59%3A36))

At AMP Robotics, the focus was on eliminating entire classes of runtime errors:

> "With Rust's memory safety, with the borrow checker, there was fundamentally an entire class of bug that I am used to dealing with that we solve at compile time instead of solving at runtime."
> -- Carter Schultz, AMP ([54:13](https://corrode.dev/podcast/s02e02-amp?t=54%3A13))

## Set Realistic Learning Expectations

Recognize that mastery takes time, but basic productivity comes surprisingly quickly:

> "Nobody on the team had Rust experience. We started working on this with zero Rust background... There are really different levels of competence. Like you can get started with messing things up very quickly, but to be truly productive and to truly know what you're doing, maybe like a month or something."
> -- Kiril Videlov, GitButler ([23:24](https://corrode.dev/podcast/s03e04-gitbutler?t=23%3A24))

Early mistakes are part of the journey:

> "Steve Klabnik works at Oxide and like in the early days of Oxide, I remember it was my first Rust project and I asked him to review it... he was like 'you don't have to panic everywhere, like all these unwraps you could return errors'."
> -- Jessie Frazelle, Zoo ([43:45](https://corrode.dev/podcast/s03e05-zoo?t=43%3A45))

But the payoff is worth it:

"There's kind of three main phases [of Rust developer experience]. The first phase where you're starting out, you're still a bit confused by the borrow checker... Then there's a point when you start to be comfortable... And then there's a third phase when you start to have mastery." - Nicolas Moutschen, Apollo ([24:26](https://letscast.fm/sites/rust-in-production-82281512/episode/apollo-with-nicolas-moutschen?t=24%3A26))

## Start Small and Focused

System76's experience demonstrates the power of incremental adoption:

> "We took System76 and we started. We had a little project. Me and my fellow engineers, we had the firmware updater, started in Rust, finished in Rust, and then we go to other projects. Then it was Pop!_OS and it was the distribution installer."
> -- Jeremy Soller, System76 ([1:02:30](https://corrode.dev/podcast/s02e07-system76?t=1%3A02%3A30))

Avoid ambitious rewrites:

> "If you start with a very big, well, we have to rewrite this project in Rust. It's going to get a bad reaction and it deserves a bad reaction because... there are also massive costs."
> -- Jeremy Soller, System76 ([1:03:03](https://corrode.dev/podcast/s02e07-system76?t=1%3A03%3A03))

## Standardize on Battle-Tested Libraries

For async programming, rely on proven solutions:

> "We are pretty big on async because we are wanting to support all of these services async... It's a hard problem to solve but async standard and tokio has worked out pretty well for us."
> -- Deb Roy Chowdhury, InfinyOn ([25:14](https://corrode.dev/podcast/s03e02-infinyon?t=25%3A14))

Choose your error handling strategy wisely:

> "Now, I understand that there is the anyhow camp, and then there is the camp of using typed errors. For applications, anyhow just works. For libraries, you want typed errors."
> -- Kiril Videlov, GitButler ([29:13](https://corrode.dev/podcast/s03e04-gitbutler?t=29%3A13))

## Manage Your Async Tasks Carefully

Don't just spawn tasks blindly:

> "Instead of just raw spawning something, assign it a variable and then keep that variable around to either abort it if you have to... if you have a long running service, like a server, you really need to keep track of them and abort them when they're done."
> -- Jessie Frazelle, Zoo ([53:40](https://corrode.dev/podcast/s03e05-zoo?t=53%3A40))

## Structure Your Code for Fast Compilation

Think about compile times from the start:

> "The primary input to the crate structure is compile time because 500,000 lines of Rust takes a long time to compile... really the question is like what code gets recompiled a lot and how do reduce the amount of it."
> -- Conrad Irwin, Zed ([38:37](https://corrode.dev/podcast/s03e01-zed?t=38%3A37))

## Turn the Hiring Challenge Into an Advantage

Use Rust as a recruiting tool:

> "We haven't had a hard time finding Rust engineers... it actually helps you out to be that company that's doing stuff in Rust... the folks using Rust today are like a cut above the rest because you have to have that willpower to go use something that no one else is."
> -- Jessie Frazelle, Zoo ([58:36](https://corrode.dev/podcast/s03e05-zoo?t=58%3A36))

## Keep Dependencies Minimal and Intentional

Be strategic about dependencies:

> "We are very deliberately minimalistic because we don't want to become yet another iteration of what looked like the big data ecosystem. So we are trying to be very deliberate about what is the most necessary."
> -- Deb Roy Chowdhury, InfinyOn ([37:36](https://corrode.dev/podcast/s03e02-infinyon?t=37%3A36))

