+++
title = "How to Hire Rust Developers"
date = 2024-07-22
template = "article.html"
[extra]
hero = "hero.svg"
series = "Rust Insights"
credits = [
  "<a href='https://www.freepik.com/free-vector/brainstorm-isometric-landing-page-online-service_5603461.htm'>Image by vectorpouch on Freepik</a>"
]
+++

There's a curious mismatch in the Rust hiring market where some companies 
believe there are not enough Rust developers to start projects, while many Rust-enthusiast developers struggle to find jobs. Why is that?

Most Rust jobs are for senior roles, leaving newcomers and mid-level devs out in the cold. Many of whom would be a great fit for these roles with a little bit of training.
The crypto industry is a notable exception, where Rust developers are in high demand, but not everyone wants to work in that space.

Companies want unicorns with years of Rust experience in an industry where that's rare. Meanwhile, eager developers worldwide are ready to work but face barriers like location restrictions (US only), job security concerns (contract work only), or lack of "professional" Rust experience. It's a classic case of supply and demand completely missing each other, with both sides frustrated and opportunities lost.

In order to bridge this gap, I wrote a checklist to help companies find and onboard Rust talent, because I saw many organizations make the same mistakes 
over and over again.

If you are a hiring manager or a team lead looking to hire Rust developers, this guide is for you.

## Setting Expectations

#### Avoid Unrealistic Demands

Don't expect 10 years of Rust experience, as Rust is a relatively new language. (Rust 1.0 was released in 2015.)
Such exaggerated expectations can significantly (and unnecessarily) narrow your pool of potential candidates. Experienced developers might consider this a red flag as it shows a lack of understanding of the Rust ecosystem.

Instead, it might be enough to look for the *willingness* to learn Rust or, at most, non-production experience with the language.

#### Clearly Specify Tasks and Responsibilities

Many candidates are interested in a pure Rust role. Don't just add 'Rust' as a keyword to attract more candidates. It will reflect poorly on your company and waste the time of both the candidate and the hiring team.

Will the candidate have to work with other languages or technologies?
Outline the specific tasks and responsibilities that involve Rust.
Ideally, even mention the specific Rust libraries or frameworks you are using.
This helps candidates understand what is expected of them and which other ecosystems they might need to interact with. 

## Finding Candidates

The Rust job market is still relatively small compared to languages like Python or JavaScript.

I found that most companies are only looking for senior Rust developers, which is a mistake. With some training, you can save a lot of time and money by hiring mid-level developers or smart juniors who are eager to learn Rust.

Currently, the best way to find Rust devs is 

1. in your company (if you have a training program)
2. through your network (ask around)

From experience, you probably won't have a lot of trouble finding interested candidates as many developers are trying to move into Rust.
However, constraints like location, salary, and job security can be a deal-breaker for many.

For more experienced Rust developers, perks like remote work, flexible hours, and a focus on work-life balance are often as important as the salary. 
Being able to work on open source or attend conferences can also be a big bonus. 
These folks are in high demand and can afford to be picky.

If you're looking for senior people or require a bigger pool of candidates, you might also want to consider sponsoring Rust events, conferences, or [podcasts](/podcast).

You can post job listings on Rust-specific job boards like [RustJobs.dev](https://rustjobs.dev/) and [RustJobs.fyi](https://www.rustjobs.fyi/), and boards with a dedicated Rust section,
like [Filtra.io](https://filtra.io/rust) and [RemoteOK](https://remoteok.com/remote-rust-jobs).
Also check out the regular "who is hiring" threads on [Hacker News](https://news.ycombinator.com/) or [Reddit](https://www.reddit.com/r/rust/comments/182f6dv/official_rrust_whos_hiring_thread_for_jobseekers/).

## Evaluating Candidates

Don't just look at raw Rust experience!

There are many indicators that can help you identify candidates who are a good fit for Rust, even if they currently don't have much experience with the language.

* **Systems Understanding:** A strong grasp of fundamental concepts such as stack vs heap, threading, and data structures is a good indicator of a candidate who hits the ground running with Rust.

* **Rust Reasoning:** For those without Rust experience, test their ability to reason about Rust code. Provide sample Rust code and ask them to explain what it does. Looking up documentation is allowed. Ask clarifying questions to gauge their interest and to see how quickly they can learn.

* **Adaptability:** Look for candidates who have a proven track record to quickly adapt and learn new technologies. For example, if they worked with many different languages and know more than one programming paradigm, they might be a good fit. 

* **Related Languages:** Be open to candidates transitioning from C++, Java, Kotlin, or TypeScript, which have an equally strong emphasis on enterprise-grade software development. Haskell, OCaml, and other functional programming languages can also be a good fit, because of their focus on the type system and correctness. Rust has [functional aspects](/blog/paradigms/), which are similar to these languages. 

* **Open Source Contributions:** Some candidates might have a strong background in open source work. That's usually a big bonus. Go through their contributions to assess code quality and communication style. 

* **Industry and Domain Knowledge:** Consider candidates with experience in Rust's key domains, such as backend development, infrastructure, real-time data processing, and systems programming. Depending on your niche, assess their expertise in these areas.

* **Evaluate Troubleshooting Skills:** A good proxy for Rust knowledge is the ability to debug and reason about code in general. Assess a candidates' ability to understand and resolve compile errors in Rust, focusing on common issues with ownership and borrowing. Provide scenarios that require light debugging and refactoring of Rust code.

* **Ask to use the Rust documentation** Rust takes documentation seriously. Show candidates some Rust documentation and ask follow-up questions to gauge their ability to understand basic concepts. Ask them to document a piece of code themselves or explain it in their own words.

Good luck with your Rust hiring process!

{% info(headline="Is your company adopting Rust?", icon="crab") %}

Let me help you make the most of Rust.
I offer consulting services to get you up to speed with your Rust projects, from training your team to code reviews and architecture consulting. [Get in touch](/services) to learn more.

{% end %}


