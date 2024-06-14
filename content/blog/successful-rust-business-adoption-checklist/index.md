+++
title = "Making Your First Real-World Rust Project a Success"
date = 2024-06-14
template = "article.html"
[extra]
series = "Rust Insights"
hero = "hero.svg"
credits = [ "<a href='http://www.freepik.com'>Hero image designed by upklyak / Freepik</a>" ]
resources = [
  "There's a nice talk by [Ashley Williams](https://github.com/ashleygwilliams) titled [Zen and the Art of Convincing Your Company to Use Rust](https://www.youtube.com/watch?v=Pn-1so-Ibsg) that covers this topic in more detail."
]
reviews = [
  { name = "Julian Didier", url = "https://github.com/theredfish" },
]
+++

Rust has quickly become a popular choice for teams seeking to write safe and efficient systems. Its unique blend of performance, safety, and concurrency makes it an attractive option for various applications, from embedded systems to web development.

However, adopting Rustlang for your first production project requires careful planning and strategy. After all, this is a big deal: betting on a new programming language could be a business decision that you base the next ten years of your company on.

The goal of this guide is to provide you with a comprehensive checklist and actionable advice to make your first real-world Rust project a success.

<h2>Table of Contents</h2>

<details class="toc">
<summary>
Click here to expand the table of contents.
</summary>

- [Know Why You Are Considering Rust](#know-why-you-are-considering-rust)
- [Get The Buy-In From Stakeholders](#get-the-buy-in-from-stakeholders)
  - [Your Team Must Be On Board](#your-team-must-be-on-board)
  - [Keep an Eye on The Bus Factor](#keep-an-eye-on-the-bus-factor)
  - [Find a Rust Champion](#find-a-rust-champion)
  - [Run a Survey to Gauge Interest and Concerns](#run-a-survey-to-gauge-interest-and-concerns)
  - [Address Concerns and Answer Questions in a Relaxed Setting](#address-concerns-and-answer-questions-in-a-relaxed-setting)
- [Project Planning](#project-planning)
  - [Finding The Right Project](#finding-the-right-project)
  - [Choose The Right Integration Method](#choose-the-right-integration-method)
  - [Check the Ecosystem](#check-the-ecosystem)
  - [Set Standards for Crates](#set-standards-for-crates)
  - [Establish a Policy on Async Rust](#establish-a-policy-on-async-rust)
  - [Have a Migration Strategy](#have-a-migration-strategy)
  - [Become An Active Member Of The Community](#become-an-active-member-of-the-community)
- [Team Building](#team-building)
  - [Start With a Small Team](#start-with-a-small-team)
  - [Start a Team Channel](#start-a-team-channel)
  - [Consider Expert Mentorship](#consider-expert-mentorship)
  - [Allocate Time for Learning](#allocate-time-for-learning)
  - [Learning Resources](#learning-resources)
- [Budgeting](#budgeting)
- [On Hiring Talent](#on-hiring-talent)
  - [People with Production Experience Are Hard to Find and Expensive](#people-with-production-experience-are-hard-to-find-and-expensive)
  - [Source Talent From Your Existing Teams Instead](#source-talent-from-your-existing-teams-instead)
  - [Scaling The Team](#scaling-the-team)
- [Ongoing Maintenance](#ongoing-maintenance)
  - [Emphasize Code Reviews and Pair Programming](#emphasize-code-reviews-and-pair-programming)
  - [Encourage Refactoring](#encourage-refactoring)
  - [Regularly Review Progress and Adjust Strategies](#regularly-review-progress-and-adjust-strategies)
- [Next Steps](#next-steps)

</details>

## Know Why You Are Considering Rust

Understanding *why* you are considering adopting Rust is crucial.

- Define clear goals and expectations for the project &mdash; this is a good idea, no matter if you decide on Rust or another language in the end.
- Set out to [compare all the available options by fairly evaluating the pros and cons of each language](https://www.youtube.com/watch?v=DnT-LUQgc7s) in a table or a document. Share this document with your team and stakeholders to fill in the gaps and ensure transparency.
- Focus on business value and long-term benefits, not personal preferences.
- Rust needs a catalyst for success, i.e., a clear benefit, which will be the driving force behind the adoption. Good catalysts are higher service stability, reduced operational costs, and better security. Don't focus on performance alone.
- Write down your success criteria, such as improved robustness (lower number of bugs), developer productivity, and better scalability.

## Get The Buy-In From Stakeholders

### Your Team Must Be On Board

Introducing Rust will be a disruptive change, and it's vital to have the backing from both the team and leadership. One side is not enough. Make sure everyone understands the [benefits and challenges of using Rust](/blog/why-rust).

Rust is an organization-wide commitment, and it's vital to have a long-term mindset. If you need to get something done quickly and can afford tech debt, consider using another language. However, for long-term projects, Rust's benefits will offset the initial learning curve.

Management should understand the benefits of Rust and be willing to invest in training, hiring, and tooling. They should also be aware of the potential challenges (e.g., delayed project timelines, increased costs, etc.) and have a clear understanding of the trade-offs involved.

The magnitude of this decision should not be underestimated. Therefore, at the beginning of your adoption journey, consider bringing in a consultancy ([like corrode](/)) to help decision-makers fully understand the costs and benefits of Rust. This can be crucial for assessing risks and avoiding major surprises down the road. While this means a higher upfront cost, it ultimately provides clarity and allows your team to focus on the technical aspects, setting the project up for success.

### Keep an Eye on The Bus Factor

The [bus factor](https://en.wikipedia.org/wiki/Bus_factor) is the number of people on your team who need to be hit by a bus before your project is in trouble. Make sure this bus factor is bigger than 1.

Rust adoption should not be driven by ego or your CV but by business needs.
If you love Rust, but your organization is not ready for it, don't force it on them &mdash; it will fall back on you. There should always be more than one person who knows the system well enough to maintain it.

Similarly, if you are the manager who has merely heard about the benefits of Rust, but your team is perfectly happy with the current technology stack, there might be no need to switch. Don't choose Rust because of the hype; listen to your team.

### Find a Rust Champion

Find a Rust champion within your team who is passionate about Rust, good at teaching, and willing to lead the adoption effort. They will serve as the cornerstone for your Rust adoption process and can significantly ease the learning process for the rest of the team.

They don't have to be a Rust expert, but ideally, a good champion already has some experience with Rust in production or has built a few larger side projects with it.

If there is nobody willing to take on that role, reconsider if Rust is the right choice; perhaps the team is not ready for the transition yet or is satisfied with the current technology stack. An external consultant cannot replace an internal champion (if anything, they work in tandem). The initial motivation has to come from within.

### Run a Survey to Gauge Interest and Concerns

Run a survey to gauge the team's initial interest in Rust. Ask questions like:

- What is your current language of choice?
- On a scale from 1 to 5, how interested are you in learning Rust?
- What are your main concerns about adopting Rust?
- Which other languages would you consider for the project?
- What are the main benefits of choosing Rust for this project?
- Would you be willing to take on a Rust project? If so, in what capacity?

If you need a comprehensive survey template to get started, feel free to [reach out to me](/about). The template includes detailed questions that can help uncover your team’s readiness and potential challenges for adopting Rust.

### Address Concerns and Answer Questions in a Relaxed Setting

If you get mixed results, consider holding a Rust Q&A session with the team on a Friday afternoon. This way, you can address concerns and answer questions in a relaxed environment.

## Project Planning

### Finding The Right Project

My number one rule is: start small, but not too small.

Begin with a project that is close to your core business but not mission-critical. This approach allows your team to gain experience with Rust with less disruption to the business.

Choose a project in a domain you know very well. This way, you can focus on learning Rust and not on understanding the domain. On top of that, you can compare the performance of Rust with the existing system and see if it lives up to the expectations. It will be easier to onboard new team members if they are already familiar with the domain.

### Choose The Right Integration Method

There are various ways to integrate Rust into your existing infrastructure:

- **CLI Tool**: Develop a command-line tool in Rust.
- **FFI Layer**: Call Rust code from another language using the Foreign Function Interface.
- **Microservice / Network Layer**: Implement a microservice in Rust.
- **WebAssembly**: Use Rust to compile to WebAssembly (e.g. for frontend).
- **Embedded System**: Develop an embedded system in Rust.

Pick the integration method which best aligns with your project's requirements and team's expertise. Choose a method that allows you to leverage Rust's strengths while minimizing risks. Rust can be a great fit for performance-critical parts of your application, such as networking and data processing. Once the team sees the benefits of Rust, they will be more open to using it in other parts of the business. Pick a project with a huge upside and one that is easy to replace if things go wrong.

**A microservice** is a good candidate for this. In the worst case, you can rewrite it in another language. You can gradually shift over traffic to the Rust service and see how it performs in production.

However, starting with a **CLI tool** might be easier for the team to manage and understand, even if it is not central to the core business. It can be a quick win and a manageable way to introduce Rust without significant risk, helping the team to see its potential.

Beginning with **WebAssembly** can be challenging due to its complexity. The team might get frustrated with the tooling and ecosystem, and there might not be any immediate benefits, such as faster performance. This could lead to a negative impression of Rust.

I saw some great results with Rust for **embedded systems**, where the tooling is excellent, and there is a clear project boundary. Tools like [probe-rs](https://probe.rs/) are often considered best-in-class.

The **FFI layer** is a good choice if you have a large codebase in another language and want to gradually replace parts of it with Rust. For example, some teams rewrite a performance-critical section of their Java monolith in Rust for 2-3x performance improvements. The [jni crate](https://docs.rs/jni) allows you to create a compatible library.

### Check the Ecosystem

Before starting a Rust project, check the ecosystem for libraries, tools, and resources you will need. Make sure that the libraries are available and well-maintained. Look at the issues and documentation of critical crates for your project. Get familiar with the maintainers. Join the Discord or Matrix channels of the main crates you plan to use. This will give you a good idea of the health of the ecosystem and the community.

### Set Standards for Crates

Some companies are fine with using any crate from crates.io, while others are more conservative and only use crates that have been around for a while and have a good reputation. I find [blessed.rs](https://blessed.rs/) to be a good resource for finding high-quality crates.

Choosing the right crates can have a big impact on the [long-term maintainability](/blog/long-term-rust-maintenance/) of your project.

Run [cargo-audit](https://docs.rs/cargo-audit/latest/cargo_audit/) regularly to check for security vulnerabilities in your dependencies.

### Establish a Policy on Async Rust

Async Rust requires proficiency in the language and can be challenging for beginners. [Navigating the space is hard.](/blog/async)

Establish early on if you want to use async Rust in your project because it can have a big impact on your project. Some companies are fine with using async Rust everywhere, while others use it only when there is no other choice (e.g. the ecosystem does not provide a synchronous alternative). 
I saw success in keeping the core of the application synchronous while using async for I/O-bound tasks. For example, you could have a lib, which is synchronous and a wrapper around it that is async. This makes testing easier and allows you to use the synchronous lib in other projects.

Either way, establish a policy early on and make sure everyone is on the same page.

### Have a Migration Strategy

Answer the following questions before starting the migration:

- What are the milestones for the migration?
- How will you handle the transition period? E.g., will you run both systems in parallel?
- How will you ensure that the team is productive during the migration?
- What is your fallback plan if the migration fails? Can you roll back to the old system?
- How will you measure the success of the migration? What are the key metrics?
- How will you ensure that the team is productive with the new technology?

Document your position on these questions for future reference and to ensure that everyone is on the same page.

### Become An Active Member Of The Community

If you're starting to get serious about Rust, don't stand on the sidelines! Engage with the Rust community through [forums](https://users.rust-lang.org/), and share your insights on your developer blog. Subscribe to [This Week in Rust](https://this-week-in-rust.org/) to stay up-to-date on the latest news and developments in the Rust ecosystem. Keep an eye on the announcements on the [Rust blog](https://blog.rust-lang.org/) as well as the [Rust Foundation](https://foundation.rust-lang.org/). Being an active community member can provide valuable support and keep you updated on best practices.

## Project Setup

### Fully Embrace Rust Tooling

Rust has some of the best tooling in the industry. Make good use of it! Use `cargo fmt` to format your code, `cargo clippy` to catch common mistakes, and `cargo test` or `cargo nextest` to test your project.

Use `rust-analyzer` for code completion and `rustup` to manage your Rust toolchain. There are also many other tools available, such as `cargo-watch` for automatically recompiling your code when it changes.

For CI/CD, consider using GitHub Actions, GitLab CI, or Azure Pipelines. They all have good support for Rust. For GitHub Actions in particular, take a look at [dtolnay/rust-toolchain](https://github.com/dtolnay/rust-toolchain).
Enforce `cargo fmt --check` and `cargo clippy` in your CI pipeline.

Have these tools in place from the start and encourage all team members to
routinely use them while developing. There should be no exceptions.

### Consider An Internal Styleguide

You can get pretty far with the above-mentioned tools. 
However, one often overlooked aspect is the social side of Rust.
In languages like Python or Go, there typically is one idiomatic way to do things. That makes it easier to work in a group as the code looks coherent between authors and style discussions are reduced to a minimum.

In Rust, that is not the case as there tend to be multiple ways to 
solve a problem, which all end up being valid. This can lead to
style discussions and code reviews that are more about personal preference than actual issues. Ultimately, these discussions end up not creating business value
and can be a source of frustration for the team.

Typical areas of churn are:

* Zero-cost abstractions vs. explicitness: are `.clone()`s okay or should you introduce lifetimes instead?
* Generics: when does it make sense to introduce them? How many type parameters are too many?
* Static vs dynamic dispatch: is it okay to use `Box<dyn Trait>` or should you always use `impl Trait`? 
* Macros: when are they okay and when should you avoid them? How complex can they get?
* Functional vs. imperative style: e.g. when is it okay to use `for` loops and when should you use iterators?

It's better to be upfront about these decisions and make them explicit.

As the project evolves, try to document your standpoints 
on these topics in an internal style guide. This can be as simple as a markdown file in your repository. It will help new team members to get up to speed faster and reduce the amount of churn in code reviews.

Here is my take on the above topics:

* Prefer explicitness over zero-cost abstractions. Only introduce lifetimes when necessary. `.clone()` is okay most of the time. If not, consider `Rc` or `Arc`. Always measure the performance impact before introducing lifetimes.
In general, beginners [worry about lifetimes too much](/blog/lifetimes/)
* Generics are okay, but don't overdo it. If you have more than 3 type parameters, consider if you can reduce them. If not, it might be a sign that your function is doing too much.
* Prefer `impl Trait` over `Box<dyn Trait>`, but don't be religious about it.
  If a trait object reduces complexity, it's okay to use it.
* Macros are okay for repetitive tasks (such as writing out an `impl` block for 
a long list of types), but avoid them for complex logic. Macros are hard to debug and can lead to cryptic error messages. They are almost like a language within a language.   
* Use OOP/iterative style for global control flow and functional style for local transformations. Get acquainted with iterator patterns, but don't overdo it. Sometimes a simple `for` loop is more readable than a chain of iterators.
Read my post on [thinking in iterators](/blog/iterators) to learn more.

In general, resist the urge to be clever.
Don't expect everyone on the team to know every Rust feature like higher-level trait bounds or non-trivial lifetimes.
Stuff like `impl <T, U, V> SomeTrait for YourType<T, U, V> where T: ....`
is challenging to read and understand for most people.

If you have to use advanced features, try to hide them behind a simple interface for the rest of the team.

Don't underestimate documentation. Perhaps you have a rule that you should always document public structs and functions and you enforce this in your CI pipeline. You can do so by adding `#![deny(missing_docs)]` at the top of your `lib.rs` or `main.rs` and the compiler will refuse to compile code if there is any public item without documentation.

## Team Building

### Start With a Small Team

Start with a small team of 2-3 developers who are excited about Rust. They will be the pioneers and can help spread the word about Rust within the organization. Once the team has gained experience and confidence and has delivered a minimum viable product (MVP), you can expand the Rust team.

### Start a Team Channel

Create a dedicated channel for the Rust team on your company's communication platform (e.g., Slack, Discord, or Microsoft Teams). This channel can be used to share resources, ask questions, and discuss Rust-related topics. It's a great way to build a sense of community and encourage knowledge sharing among team members.

### Consider Expert Mentorship

Many companies wait too long to get professional help for their Rust projects. Some may have been burned in the past by hiring consultants who didn't deliver what they promised. Other organizations think they can do it all by themselves, but this often leads to a hard-to-maintain codebase, poor developer experience, frustration, and in the worst case, the discontinuation of the project. 

On the other hand, a good instructor can be an accelerator. They can help avoid costly mistakes, ask the hard questions around Rust adoption, and set the team up for success. Hiring consultants can accelerate the exploration process and mitigate risks. Experts can scaffold the project architecture, implement best practices like testing and CI/CD, and train the team, ensuring a smooth transition for everyone involved.

Most importantly, bringing in a consultant early in the project can eliminate the "unknown unknowns" for your team and back up your decisions with expert advice.

Many companies fear the cost of hiring consultants. However, clarifying things early on and avoiding costly mistakes can be more economical in the long run. The team will benefit the most early on, starting with a solid foundation.

<div style="display: flex; justify-content: space-evenly; align-items: stretch; gap: 20px;">
  <p style="flex: 1; margin: 0; display: flex; align-items: center;">
    Think of it like this: if you were to go rock climbing for the first time, would
    you rather have a seasoned climbing partner or go it alone? The guide can
    help you avoid dangerous routes, give you some tips, and make the experience much more
    pleasant for everyone involved.
  </p>
  <img src="climb.svg" alt="A good consultant is like a climbing partner or belayer" style="height: auto; max-height: 300px;">
</div>


### Allocate Time for Learning

Once an initial prototype is in place, it's time to bring on the rest of the team.

The biggest concern about Rust that I hear from engineers is that they are worried they won't have enough time to properly learn Rust. Set aside dedicated learning time for your team to get up to speed with Rust. Encourage your team to work on small Rust projects or contribute to open-source projects to gain practical experience. It takes around [4 months to get comfortable with Rust](https://opensource.googleblog.com/2023/06/rust-fact-vs-fiction-5-insights-from-googles-rust-journey-2022.html), so plan accordingly.

This might be a good time to compare Rust workshops and training programs. Some consultancies (like [corrode](/)) offer dedicated Rust training for teams and provide discounts for larger groups. An on-site training can be a great way to kick off your Rust project and get everyone excited about the opportunity to work on the project. Remember to plan some time to schedule the training and to get the budget approved, so reach out to the training provider early.

### Learning Resources

No matter how you plan to integrate Rust into your project, make sure to read up on the language and its ecosystem. Here are the best resources I know of right now:

- [The Rust Book](https://doc.rust-lang.org/book/): A must-read for every developer on the team. Make sure that everyone on the team gets a copy or reads it online.
- [Rustlings](https://github.com/rust-lang/rustlings): Fun, short exercises to get started with Rust.

Which resources I would recommend after that depends on the team's background and the project's requirements.
Take a look at this [Rust books list](https://github.com/sger/RustBooks) and my resources for [idiomatic Rust](https://corrode.dev/blog/idiomatic-rust-resources/).

## Budgeting

To avoid any surprises, it's essential to plan your budget carefully.
Be aware of the (hidden) costs associated with adopting Rust. 
Here is a checklist of costs to consider, roughly ordered by the stages of a project:

1. **Initial Setup and Planning**
   - Rust exploration and evaluation (conducting surveys, research)
   - Alignment between stakeholders (meetings, design documents)
   - Planning and architecture
   - Feasibility study (proof of concept for your domain)
   - Transition management (project management resources)

2. **Opportunity costs** 
   - Costs of delaying other projects and features: time spent on Rust could
     be devoted to other projects.
   
3. **Training and Team Preparation**
   - Training (4 months of dedicated time)
   - Rust training and resources (books, online courses, conferences)
   - Mentorship and coaching
   - Team building activities (team lunches, offsites)

4. **Hiring and Team Expansion**
   - Staffing costs for Rust developers (recruiting, job postings, onboarding)
   - Hiring people in infrastructure roles (SREs, DevOps)

5. **Setup Costs**
   - Project structure
   - Workflows and tools (IDEs, linters, formatters)
   - Tooling setup (initial configuration of development environments)
   - CI/CD pipelines

6. **Development and Implementation**
   - Costs of fast development machines ([Rust builds are hardware-intensive](/blog/tips-for-faster-rust-compile-times/))
   - Development costs (coding, testing, debugging)
   - Documentation
   - Code reviews and pair programming (to ensure code quality and knowledge sharing)
   - Performance tuning (if needed)
   - Security audits
   - Compliance and legal reviews (regulations and standards, e.g. GDPR or software licenses)

7. **Infrastructure and Tooling**
   - Licensing for proprietary tools (rarely needed, but consider it)
   - Additional hardware during migration (a separate set of infrastructure 
     for the new system)
   - Monitoring and alerting tools (tools for monitoring performance 
     and reliability)

8. **Ongoing Maintenance and Support**
   - Cloud costs (compute, storage, networking)
   - Ongoing maintenance costs (monitoring, logging, on-call, CI/CD pipelines)
   - Refactoring and cleaning up technical debt
   
9.  **Communication and Marketing**
    - Internal communication (presentations)
    - External communication (blog posts, conference talks)

10. **Risk Management**
    - Account for the cost of failure
    - Consider costs of rollback mechanisms
    - Costs of rollback if the migration fails
    - Contingency funds (allocating a budget for unforeseen expenses)

## On Hiring Talent

Hiring Rust talent takes time and effort.
This section provides insights into hiring strategies and what to look for in candidates for Rust projects specifically.

### People with Production Experience Are Hard to Find and Expensive

It's challenging to find developers with Rust *production* experience. Competing with the crypto industry, which heavily uses Rust, makes it even harder. Salaries for Rust developers in crypto can be 2-3 times higher than in other industries, and the pool of talent is small.

Unless you are a hot new startup or have a big budget, finding people with Rust production experience can be challenging and costly. Consider training your own team instead.

### Source Talent From Your Existing Teams Instead

Instead of focusing solely on experience, consider finding junior- to mid-level developers who are smart, curious, and eager to learn. From my experience, good candidates often have experience in related areas (like Kotlin or TypeScript) and are known for being quick learners. Place them near your Rust champion or an expert mentor to help them get up to speed quickly.

People in infrastructure roles are also a great fit. Those who tend to have an interest in scalability, performance, and networking can also be great additions to your team. Look for those with previous admin roles, who have worked close to the metal and have a good understanding of how things work under the hood. 
These people are often excited to pick up Rust as their background aligns well with the language's strengths.

### Scaling The Team

Once your project reaches a certain level of maturity, you can start hiring Rust developers to scale your team and maintain the project.

Using Rust can be a competitive advantage for smaller companies, as it attracts developers who are excited about the language's potential. Companies like InfluxData have seen a notable increase in interest from developers after announcing projects involving Rust:

> I announced that we're working on this new core of the database in November of
> 2020 in a talk I did. And I said we were hiring and we got a bunch
> of inbound interest because of the fact that it was written in Rust.
> &mdash; Paul Dix, InfluxData

If you're interested in learning more about hiring Rust developers, don't miss the season finale of 'Rust in Production.' Paul Dix from InfluxData and Micah Wylde from Arroyo share insights on why smaller companies find hiring Rust talent a competitive advantage while larger companies face unique challenges.

Find the section from the episode about hiring Rust engineers [here](/podcast/s01e07-season-finale/?t=23%3A06).

## Ongoing Maintenance

I wrote a separate [blog post on long-term Rust maintenance](/blog/long-term-rust-maintenance/), which might be helpful for you, but here are some specific tips for your first Rust project:

### Emphasize Code Reviews and Pair Programming

Code reviews and pair programming are a great way to share knowledge and best practices among team members. Make sure that code reviews are a regular part of your development process and that everyone on the team understands the importance of them.

Consider strategies like [mob programming](https://en.wikipedia.org/wiki/Mob_programming) to get the team up to speed quickly. This can be especially helpful for new team members who are still learning Rust and might be too shy to ask questions in a code review or on a team channel.

### Encourage Refactoring

Encourage your team to refactor code regularly to keep it clean and maintainable. Make sure it is a regular part of your development process and that everyone on the team can change the codebase without fear. Unless you work in a safety-critical environment, everyone should be able to make changes to the codebase without asking for permission.

### Regularly Review Progress and Adjust Strategies

As you go, adjust your strategies as needed. Make sure that you are hitting your milestones and that the team feels productive.

Some projects have the tendency to become overly complex, so regularly ask newcomers to review the codebase and give feedback on what they find confusing.
Keep the code straightforward and fight abstractions. Focus on being readable, not clever.

## Next Steps

By acknowledging the challenges and following these strategies, you can ensure a successful Rust adoption for your first production project. With careful planning and a dedicated team, Rust can drive significant improvements in your organization. 

Check out our ['Rust in Production' podcast](/podcast/) for insights from industry experts on how their teams successfully adopted Rust in production. 

{% info(headline="Need Help with Your Rust Project?") %}

If you're considering adopting Rust for your next project, I can help you get started.
[Reach out for a free consultation](/#contact) if you need help with your Rust project. I'm happy to help you get the most out of Rust and guide you through the process.

{% end %}