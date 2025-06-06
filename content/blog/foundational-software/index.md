+++
title = "Rust For Foundational Software"
date = 2025-05-18
draft = false
template = "article.html"
[extra]
series = "Rust Insights"
+++

Ten years of stable Rust; writing this feels surreal. 

It's only been *yesterday* that we all celebrated the 1.0 release of this incredible language.

I was at Rust Week where Niko Matsakis gave his talk "Our Vision for Rust" in which he made a profound and insightful statement:

> Rust is a language for building *foundational software*.

That deeply struck me.

I highly recommend you read his blog post titled ["Rust in 2025: Targeting foundational software"](https://smallcultfollowing.com/babysteps/blog/2025/03/10/rust-2025-intro/), which is a great summary on the topic.
I wanted to expand on the idea and share what this means to corrode (and perhaps to a wider extent to Rust in the industry).

## The Issue With "Systems Programming"

First off, do we really need another different term?
After all, many people still think of Rust as a systems programming language first and foremost, so why can't we just stick to "systems programming"?

I believe the framing is all wrong.
From the outside, the term might establish that it is about "building systems," but systems programming is a term loaded with historical baggage that feels limiting and prohibitive.
It creates an artificial distinction between systems programming and "other types of programming."

The mindset "We are not a systems programming company so we don't need Rust" is common, but limiting.

If I may be candid for a moment, I believe well-known systems-programming domains have a tendency to be toxic.
Even the best developers in the world have had that experience.
> The first contribution that I had to the Linux kernel was some fix for the ext3 file system. It was a very emotional moment for me. I sent a patch to the Linux Kernel and then I saw an email response from Al Viro - one of those developers I'd only heard about and dreamed of meeting someday.
> He responded, **'I've never seen code this bad in my life. You managed to introduce three new bugs in two new lines of code. People like you should never be allowed to get close to a keyboard again.'**
> That was my introduction to Linux.

-- Glauber Costa, co-founder of Torso, on the [Top Shelf Podcast](https://www.youtube.com/watch?v=biBLEKm2dtY&t=307s)

Glauber previously worked at Red Hat, Parallels, ScyllaDB, and Datadog on schedulers, databases, and performance optimizations. He knows what he's doing.

Just imagine how many capable developers got discouraged by similar feedback or never even tried to contribute to the Linux kernel in the first place because of such comments.

I find that ironic because people once dismissed Linux itself as just a toy project.
The Linux kernel wasn't built in a day.
**People need time to learn.**

The whole idea of Rust is to enable **everyone** to build reliable and efficient software.
To me, it's about breaking down the barriers to entry and making larger parts of the software stack accessible to more people. 

> We are committed to providing a friendly, safe and welcoming environment for all
> -- [The Rust Code of Conduct](https://www.rust-lang.org/policies/code-of-conduct)

That is also where the idea for corrode comes from:
To cut through red tape in the industry.
The goal is to gradually chip away at the crust of our legacy software with all its flaws and limitations and establish a better foundation for the future of infrastructure.
To [try and defy the 'common wisdom' about what the tradeoffs have to be](https://smallcultfollowing.com/babysteps/blog/2025/05/15/10-years-of-rust/).
The term corrode is Latin for ["to gnaw to bits, wear away."](https://www.etymonline.com/search?q=corrode) [^corrode]

[^corrode]: Conveniently, it also has a 'C' and an 'R' in the name, which bridges both languages. 

## Where Rust Shines

Graydon put it this way:

> "I think 'infrastructure' is a more useful way of thinking about Rust's niche than arguing over the exact boundary that defines 'systems programming'."
>
> "This is the essence of the systems Rust is best for writing: not flashy, not attention-grabbing, often entirely unnoticed. Just the robust and reliable necessities that enable us to get our work done, to attend to other things, confident that the system will keep humming along unattended."
> 
> -- From [10 Years of Stable Rust: An Infrastructure Story](https://rustfoundation.org/media/10-years-of-stable-rust-an-infrastructure-story/)

In conversations with potential customers, one key aspect that comes up with Rust a lot is this perception that Rust is merely a systems programming language.
They see the benefit of reliable software, but often face headwinds from people dismissing Rust as "yet another systems level language that is slightly safer."

People keep asking me how Rust could help them.
After all, Rust is just a "systems programming language."
I used to reply along the lines of Rust's mantra: "empowering everyone to build reliable and efficient software" -- and while I love this mission, it didn't always "click" with people. 

My clients use Rust for a much broader range of software, not just low-level systems programming.
They use Rust for writing software that **underpins other software**.

Then I used to tell my own story:
I did some C++ in the past, but I wouldn't call myself a systems programmer.
And yet, I help a lot of clients with really interesting and complex pieces of software. 
I ship code that is used by many people and companies like Google, Microsoft, AWS, and NVIDIA.
Rust is a great enabler, a superpower, a [fireflower](https://web.archive.org/web/20230603070738/https://thefeedbackloop.xyz/safety-is-rusts-fireflower/).

## Rust Is A Great Enabler

I found that my clients often don't use Rust as a C++ replacement.
Many clients don't even have any C++ in production in the first place.
They also don't need to work on the hardware-software interface or spend their time in low-level code.

What they all have in common, however, is that the services they build with Rust are **foundational to their core business**.
Rust is used for building platforms: systems which enable building other systems on top.

These services need to be robust and reliable and serve as platforms for other code that might or might not be written in Rust.
This is, in my opinion, the core value proposition of Rust: to build things that form the bedrock of critical infrastructure and must operate reliably for years.

Rust is a day-2-language: All of the problems that you have during the lifecycle of your application surface early in development.
Once a service hits production, maintaining it is boring.
There is very little on-call work.

The focus should be on what Rust enables: a way to express very complicated ideas on a type-system level, which will help build complex abstractions through simple core mechanics: ownership, borrowing, lifetimes, and its trait system.

This mindset takes away the focus from Rust as a C++ replacement and also explains why so many teams which use languages like Python, TypeScript, and Kotlin are attracted by Rust.

What is less often talked about is that Rust is a language that enables people to move across domain boundaries: from embedded to cloud, from data science to developer tooling. 
I don't know any other language that's so versatile. 
If you know Rust, you can program simple things in all of these domains.

## Why Focus On Foundational Software?

But don't we just replace "Systems Programming" with "Foundational Software"?
Does using the term "Foundational Software" simply create a new limiting category?

Crucially, foundational software is different from low-level software and systems software.
For my clients, it's all foundational.
For example, building a data plane is foundational.
Processing media is foundational.

Rust serves as a catalyst: companies start using it for critical software but then, as they get more comfortable with the language, expand into using it in other areas of their business:

> I've seen it play out as we built Aurora DSQL - we chose Rust for the new dataplane components, and started off developing other components with other tools. The control plane in Kotlin, operations tools in Typescript, etc. Standard "right tool for the job" stuff. But, as the team has become more and more familiar and comfortable with Rust, it's become the way everything is built. A lot of this is because we've seen the benefits of Rust, but at least some is because the team just enjoys writing Rust.
>
> -- [Marc Brooker, engineer at Amazon Web Services in Seattle on lobste.rs](https://smallcultfollowing.com/babysteps/blog/2025/05/15/10-years-of-rust/)

That fully aligns with my experience: I find that teams become ambitious after a while.
They reach for loftier goals because they can.
The fact they don't have to deal with security issues anymore enables better affordances.
From my conversations with other Rustaceans, we all made the same observation: suddenly we can build more ambitious projects that we never dared tackling before, such as writing a CPU emulator because we can.
For fun.

It feels to me as if this direction is more promising: starting with the foundational tech and growing into application-level/business-level code if needed/helpful.
That's better than the other way around, which often feels unnecessarily clunky.
Once the foundations are in Rust, other systems can be built on top of it.

Just because we focus on foundational software doesn't mean we can't do other things.
But the focus is to make sure that Rust stays true to its roots.

## Systems That You Plan To Maintain For Years To Come

So, what *is* foundational software?

It's software that organizations deem critical for their success. 
It might be:

- a robust web backend
- a package manager
- a platform for robotics
- a storage layer
- a satellite control system 
- an SDK for multiple languages 
- a real time notification service

and many, many more.

All of these things power organizations and *must not fail* or at least do so *gracefully*.
My clients and the companies listed on our [podcast page](/podcast) all have one thing in common: 
They work on Rust projects that are not on the sideline, but front and center, and they shape the future of their infrastructure.

Rust is useful in situations where the ["worse is better" philosophy falls apart](https://dreamsongs.com/Files/worse-is-worse.pdf): it's a language for building the "right thing":

> With the right thing, designers are equally concerned with simplicity, correctness, consistency, and completeness.

I think many companies will choose Rust to build their future platforms on.
As such, it competes with C++ as much as it does with Kotlin or Python.

I believe that we should shift the focus away from memory safety (which these languages also have) and instead focus on the explicitness, expressiveness, and ecosystem of Rust that is highly competitive with these languages.
It is a language for teams which want to build things right and are at odds with the "move fast and break things" philosophy of the past.
Rust is future-looking. 
Backwards-compatibility is enforced by the compiler and many people work on the robustness aspect of the language.

Dropbox was one of the first production users of Rust.
They built their storage layer on top of it.
At no point did they think about using Rust as a C++ replacement.
Instead, they saw the potential of Rust as a language for building scalable and reliable systems.
Many more companies followed: 
Amazon, Google, Microsoft, Meta, Discord, Cloudflare, and many more.
These organizations build platforms.
Rust is a tool for professional programmers, developed by world experts over more than a decade of hard work.

## Rust Is A Tool For Professionals

Is Rust used for real?

Graydon Hoare says:

> "At this point, we now know the answer: yes, Rust is used a lot. It's used for real, critical projects to do actual work by some of the largest companies in our industry. We did good."
>
> "[Rust is] not a great hobby language but it is a fantastic professional language, precisely because of the ease of refactors and speed of development that comes with the type system and borrow checker."
> 
> -- [10 Years of Stable Rust: An Infrastructure Story](https://rustfoundation.org/media/10-years-of-stable-rust-an-infrastructure-story/)

To build a truly industrial-strength ecosystem, we need to remember the professional software lifecycle, which is decades long.
Stability plays a big role in that.
The fact that Rust has stable editions and a language specification is a big part of that.

But Rust is not just a compiler and its standard library.
The tooling and wider ecosystem are equally important.
To build foundational software, you need guarantees that vulnerabilities get fixed and that the ecosystem evolves and adapts to the customer's needs.
The ecosystem is still mostly driven by volunteers who work on important parts of the ecosystem in their free time.
There is more to be said about supply-chain security and sustainability in the ecosystem.

## A Language For Professionals

Building foundational systems is rooted in the profound belief that the efforts will pay off in the long run because organizations and society will benefit from them for decades.
We are building systems that will be used by people who may not even know they are using them, but who will depend on them every day.
Critical infrastructure.

And Rust allows us to do so with great ergonomics.
Rust inherits pragmatism from C++ and purism from Haskell.

Rust enables us to build sustainable software that stays within its means and is concerned about low resource usage.
Systems where precision and correctness matter.
Solutions that work across language boundaries and up and down the stack.

Rust is a language for decades and my mission is to be a part of this shift.

On to the next 10 years!