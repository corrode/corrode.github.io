+++
title = "Guide to Rust in Production"
date = 2024-05-23
template = "article.html"
[extra]
series = "Rust Insights"
hero = "hero.svg"
credits = [ "<a href='http://www.freepik.com'>Hero image designed by upklyak / Freepik</a>" ]
+++

Rust has quickly become a popular choice for teams seeking to write safe and efficient systems. Its unique blend of performance, safety, and concurrency makes it an attractive option for various applications, from embedded systems to web development.

However, adopting Rust for your first production project requires careful planning and strategy.
The goal of this guide is to provide you with a comprehensive checklist and actionable advice to make your first real-world Rust project a success. 

<h2>Table of Contents</h2>

<details class="toc">
<summary>
Click here to expand the table of contents.
</summary>

- [Know Why You Are Considering Rust](#know-why-you-are-considering-rust)
- [Get The Buy-In From Stakeholders](#get-the-buy-in-from-stakeholders)
  - [Your Team Must Be On Board](#your-team-must-be-on-board)
  - [Find a Rust Champion](#find-a-rust-champion)
  - [Run a Survey to Gauge Interest and Concerns](#run-a-survey-to-gauge-interest-and-concerns)
  - [Address Concerns and Answer Questions in a Relaxed Setting](#address-concerns-and-answer-questions-in-a-relaxed-setting)
- [Project Planning](#project-planning)
  - [Finding The Right Project](#finding-the-right-project)
  - [Ways to Integrate Rust](#ways-to-integrate-rust)
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
- [Ongoing Maintenance](#ongoing-maintenance)
  - [Emphasize Code Reviews and Pair Programming](#emphasize-code-reviews-and-pair-programming)
  - [Encourage Refactoring](#encourage-refactoring)
  - [Regularly Review Progress and Adjust Strategies](#regularly-review-progress-and-adjust-strategies)
- [Next Steps](#next-steps)

</details>



## Know Why You Are Considering Rust

Understanding *why* you are considering to adopt Rust is crucial.

- Define clear goals and expectations for the project &mdash; this is a good
  idea, no matter if you decide on Rust or another language in the end.
- Set out to compare all the available options by fairly evaluating the pros and cons
  of each language in a table or a document. Share this document with your team
  and stakeholders to fill in the gaps and ensure transparency.
- Focus on business value and long-term benefits, not personal preferences.
- Rust needs a catalyst for success, i.e. a clear benefit, which will be the
  driving force behind the adoption. Good catalysts are higher service stability,
  reducing operational costs, better security. Don't focus on performance
  alone.
- Write down your success criteria, such as improved robustness (lower number of bugs), developer
  productivity, and better scalability.

## Get The Buy-In From Stakeholders

### Your Team Must Be On Board

Introducing Rust will be a disruptive change, and it's vital to have the backing
of both the team and leadership. One side is not enough. Make sure everyone
understands the [benefits and challenges of using Rust](/blog/why-rust).

Rust is an organization-wide commitment, and it's vital to have a long-term
mindset. If you need to get something done quickly and can afford tech debt,
consider using another language. However, for long-term projects, Rust's
benefits will offset the initial learning curve.

### Find a Rust Champion

I advise you to find a Rust champion within your team who is passionate about
Rust, good at teaching, and willing to lead the adoption effort. They will serve
as the cornerstone for your Rust adoption process and can significantly ease the
learning process for the rest of the team. Ideally, a good champion already has
some experience with Rust in production or has built a few larger side-projects
with it.

If there is nobody willing to take on that role, reconsider if Rust is the right
choice; perhaps the team is not ready for the transition yet or is satisfied
with the current technology stack. An external consultant cannot replace an
internal champion (if anything, they work in tandem). The initial motivation has to come from within.

### Run a Survey to Gauge Interest and Concerns

I recommend running a survey to gauge the team's initial interest in Rust. Ask questions like:

- What is your current language of choice?
- On a scale from 1 to 5, how interested are you in learning Rust?
- What are your concerns about adopting Rust?
- Which other languages would you consider for the project?
- What are the main benefits of choosing Rust for this project?
- Would you be willing to take on a Rust project? If so, in what capacity?

### Address Concerns and Answer Questions in a Relaxed Setting

If you get mixed results, consider holding a Rust Q&A session with the team on a
Friday afternoon. This way, you can address concerns and answer questions in a
relaxed environment.

## Project Planning

### Finding The Right Project

My number one rule is: start small, but not too small.

Begin with a project that is close to your core business but not
mission-critical. This approach allows your team to gain experience with Rust
with less disruption to the business.

### Ways to Integrate Rust

There are various ways to integrate Rust into your existing infrastructure:

- **CLI Tools**: Develop command-line tools in Rust.
- **FFI Layer**: Use Rust to call functions in other languages.
- **Microservices / Network Layer**: Implement microservices in Rust.
- **WebAssembly for Frontend**: Use Rust to compile to WebAssembly for frontend development.
- **Embedded Systems**: Develop embedded systems in Rust.

Pick the integration method which best aligns with your project's requirements and team's expertise. Choose a method that allows you to leverage Rust's strengths while minimizing risks. Rust can be a great fit for performance-critical parts of your application, such as networking and data processing. Once the team sees the benefits of Rust, they will be more open to using it in other parts of the business. Pick a project with a huge upside and one that is easy to replace if things go wrong. A microservice is a good candidate for this. In the worst case, you can rewrite it in another language. You can gradually shift over traffic to the Rust service and see how it performs in production.

I personally would not start with a CLI tool because it is often not close to the core business, and the team might not see the benefits of Rust. Similarly, I would not start with WebAssembly because it is a complex topic, and the team might get frustrated with the tooling and the ecosystem. There might also not be any immediate upside, such as faster performance, and the team could get the wrong impression about Rust.

I saw some great results with Rust for embedded systems, where the tooling is excellent, and there is a clear project boundary.

The FFI layer is a good choice if you have a large codebase in another language and want to gradually replace parts of it with Rust. For example, some teams rewrite a performance-critical section of their Java monolith in Rust for 2-3x performance improvements.

### Check the Ecosystem

Before starting a Rust project, check the ecosystem for libraries, tools, and
resources which you will need. Make sure that the libraries are available and well-maintained. 
Look at the issues and documentation of critical crates for your project.
Get familiar with the maintainers. Join the Discord or Matrix channels of the
main crates you plan to use. This will give you a good idea of the health of the
ecosystem and the community.

### Set Standards for Crates

Some companies are fine with using any crate from crates.io, while others are
more conservative and only use crates that have been around for a while and have
a good reputation. I find [blessed.rs](https://blessed.rs/) to be a good
resource for finding high-quality crates.

Choosing the right crates can have a big impact on the [long-term maintainability](/blog/long-term-rust-maintenance/) of your project.

Run [cargo-audit](https://docs.rs/cargo-audit/latest/cargo_audit/) regularly to
check for security vulnerabilities in your dependencies.

### Establish a Policy on Async Rust

Async Rust requires proficiency in the language and can be challenging for beginners.
[Navigating the space is hard.](/blog/async)

Establish early on if you want to use async Rust in your project, because it can
have a big impact on your project. Some companies are fine with using async Rust
everywhere, while others use it only when necessary. For the rest of the
application (such as their domain model), they stick to synchronous code. Either
way, establish a policy early on and make sure everyone is on the same page.

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

If you're starting to get serious about Rust, don't stand on the sidelines!
Engage with the Rust community through [forums](https://users.rust-lang.org/),
and share your insights on your developer blog. Subscribe to [This Week in
Rust](https://this-week-in-rust.org/) to stay up-to-date on the latest news and
developments in the Rust ecosystem. Keep an eye on the announcements on the
[Rust blog](https://blog.rust-lang.org/) as well as the [Rust
Foundation](https://foundation.rust-lang.org/). Being an active community member
can provide valuable support and keep you updated on best practices.

## Team Building

### Start With a Small Team

Start with a small team of 2-3 developers who are excited about Rust. They will
be the pioneers and can help spread the word about Rust within the organization.
Once the team has gained experience and confidence and has delivered a minimum
viable product (MVP), you can expand the Rust team.

### Start a Team Channel

Create a dedicated channel for the Rust team on your company's communication
platform (e.g., Slack, Discord, or Microsoft Teams). This channel can be used to
share resources, ask questions, and discuss Rust-related topics. It's a great
way to build a sense of community and encourage knowledge sharing among team
members.

### Consider Expert Mentorship

Many companies wait too long to get professional help for their Rust projects. Some may have been burned in the past by hiring consultants who didn't deliver what they promised. Others think they can do it all by themselves, but this often leads to a poor developer experience, frustration, and in the worst case, the abandonment of Rust in the organization.

On the other side, a good instructor can be an accelerator. They can help avoid costly mistakes, ask the hard questions around Rust adoption, and set the team up for success. Hiring consultants can accelerate the exploration process and mitigate risks. Experts can scaffold the project architecture, implement best practices like testing and CI/CD, and train the team, ensuring a smooth transition for everyone involved.

Most importantly, bringing in a consultant early in the project can elmintate the "unknown unknowns" for your team and back up your decisions with expert advice. 

Many companies fear the cost of hiring consultants. However, clarifying things early on and avoiding costly mistakes can be more economical in the long run. The team will benefit the most early on, starting with a solid foundation.

Think of it like this: if you were to climb a mountain, would you rather have a guide who has climbed it many times before or try to figure it out on your own? The guide can help you avoid dangerous paths, plan ahead, and make the journey much more pleasant to everyone involved.

### Allocate Time for Learning

Once an initial prototype is in place, it's time to bring on the rest of the team.

The biggest concern about Rust that I hear from engineers is that they are
worried they won't have enough time to properly learn Rust. Set aside dedicated learning time
for your team to get up to speed with Rust. Encourage your team to
work on small Rust projects or contribute to open-source projects to gain
practical experience.

This might be a good time to compare Rust workshops and training programs. Some
companies (like corrode) offer dedicated Rust trainings for teams and provide
discounts for larger groups. An on-site training can be a great way to kick off
your Rust project and get everyone excited about the opportunity to work
on the project.
Remember to plan in some time to schedule the training and to get the budget
approved, so reach out to the training provider early.


### Learning Resources

No matter how you plan to integrate Rust into your project, make sure to read up on the language and its ecosystem. Here are the best resources I know of right now:

- [The Rust Book](https://doc.rust-lang.org/book/): A must-read for every developer on the team. Make sure that everyone on the team gets a copy or reads it online.
- [Rustlings](https://github.com/rust-lang/rustlings): Fun, short exercises to get started with Rust.

Once you're done with those, get more specific knowledge by looking through the books on this [Rust books list](https://github.com/sger/RustBooks) and the resources for [idiomatic Rust](https://corrode.dev/blog/idiomatic-rust-resources/).




## Budgeting

Be aware of the (hidden) costs associated with adopting Rust.
Here is a checklist of costs to consider ordered by the stages of the project:

1. **Initial Setup and Planning**
   - Rust exploration and evaluation (surveys, research)
   - Alignment between stakeholders (meetings, design documents)
   - Feasibility study (proof of concept for your domain)
   - Planning and architecture
   - Transition management (project management resources)
   
2. **Training and Team Preparation**
   - Training (4 months, dedicated time)
   - Rust training and resources (books, online courses, conferences)
   - Hiring consultants (expert guidance)
   - Team building and retention activities
   - Community contributions (encourage team participation)

3. **Hiring and Team Expansion**
   - Hiring Rust developers
   - Hiring people in infrastructure roles (for scalability, networking, on-call support)

4. **Setup Costs**
   - CI/CD pipelines
   - IDE configuration
   - Project structure

5. **Development and Implementation**
   - Development costs (coding, testing, debugging)
   - Documentation
   - Code reviews and pair programming (to ensure code quality and knowledge sharing)
   - Performance tuning (rarely needed, but consider it)
   - Security audits
   - Compliance and legal reviews (regulations and standards, e.g. GDPR or software licenses)

6. **Infrastructure and Tooling**
   - Licensing for proprietary tools (rarely needed, but consider it)
   - Hardware costs (fast development machines; [the Rust compilation process is hardware-intensive](/blog/tips-for-faster-rust-compile-times/))
   - Additional hardware for migration (a separate set of infrastructure for the new system)

7. **Ongoing Maintenance and Support**
   - Ongoing maintenance costs (monitoring, logging, on-call, CI/CD pipelines)
   - Refactoring and cleaning up technical debt
   
8. **Communication and Marketing**
   - Internal communication (newsletters, blog posts, presentations)
   - External communication (press releases, blog posts, conference talks)

9. **Risk Management**
    - Account for the cost of failure
    - Consider costs of rollback mechanisms (if applicable)
    - Costs of rollback if the migration fails (if applicable)

## On Hiring Talent

Finding and hiring the right talent is crucial for the success of any project. This section provides insights into hiring strategies and what to look for in candidates
for Rust projects specifically.

### People with Production Experience Are Hard to Find and Expensive

It's challenging to find developers with Rust production experience. Competing with the crypto industry, which heavily uses Rust, makes it even harder. Salaries for Rust developers in crypto can be 2-3 times higher than in other industries, and the pool of talent is small.

Unless you are a hot new startup or have a big budget, finding people with Rust production experience can be challenging and costly.

### Source Talent From Your Existing Teams Instead

Instead of focusing solely on experience, consider finding junior- to mid-level developers who are smart, curious, and eager to learn. From my experience, good candidates often have experience in related areas (like Kotlin or TypeScript) and are known for being quick learners.
With trust and mentorship from the Rust champion, they can quickly become key team members.

People in infrastructure roles are also a great fit. Those who tend to have an interest in
scalability, performance, and networking can also be great additions to your
team. Look for those with previous admin roles, who have worked close to the
metal and have a good understanding of how things work under the hood. Find
people who can read documentation and are not afraid to dive into the source
code.

## Ongoing Maintenance

### Emphasize Code Reviews and Pair Programming

Code reviews and pair programming are essential for maintaining code quality and
ensuring that the team is on the same page. They are also a great way to share
knowledge and best practices among team members. Make sure that code reviews are
a regular part of your development process and that everyone on the team
understands the importance of them.

Consider strategies like [mob programming](https://en.wikipedia.org/wiki/Mob_programming) to get the team up to speed quickly. This can be especially helpful for new team members who are still learning Rust
and might be too shy to ask questions in a code review.

### Encourage Refactoring

Refactoring is an essential part of maintaining a healthy codebase. Encourage
your team to refactor code regularly to keep it clean and maintainable. Make sure
it is a regular part of your development process and that everyone on the team
can change the codebase without fear.

### Regularly Review Progress and Adjust Strategies

Regularly review the progress of your Rust project and adjust your strategies as
needed. Make sure that you are meeting your goals (as defined above) and that the team 
feels productive. Keep an eye on documentation and readability of the codebase.
Some projects have the tendency to become overly complex, so 
regularly ask newcomers to review the codebase and give feedback what they find
confusing.

I wrote a [blog post](/blog/long-term-rust-maintenance/) on long-term Rust maintenance, which might be helpful for you.

## Next Steps

By following these strategies, you can ensure a successful Rust adoption for
your first production project. With careful planning, a supportive team, and the
right resources, Rust can become a valuable asset for your organization.

{% info(headline="Need Help with Your Rust Project?") %}

[Reach out for a free consultation](/#contact) if you need help with your Rust project. I'm
happy to help you get the most out of Rust and guide you through the process.

{% end %}