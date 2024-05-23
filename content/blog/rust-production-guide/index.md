+++
title = "Guide to Rust in Production"
date = 2024-05-23
template = "article.html"
[extra]
series = "Rust Insights"
+++

Rust has quickly become a popular choice for developers seeking to write safe
and efficient systems. Its unique blend of performance, safety, and concurrency
makes it an attractive option for various applications, from embedded systems to
web development.

However, adopting Rust for your first production project requires careful
planning and strategy.

The goal of this guide is to provide you with a comprehensive checklist and
actionable advice to ensure your first real-world Rust project a success. 

### Know Why You Are Using Rust

Understanding why you are adopting Rust is crucial. Rule out other languages
first and define clear goals. Rust needs a catalyst for success, such as safety,
stability, reducing operational costs, or developer happiness.

#### Performance Is Not a Good Catalyst

While Rust offers excellent performance, it's not the sole reason to adopt it.
Focus on safety, stability, and other long-term benefits.

#### How Will You Measure Success?

Define clear metrics for success, such as performance improvements, number of
bugs, developer happiness, productivity, robustness, and scalability.

### You Need a Long-Term Mindset

Rust is a long-term investment. If you need to get something done quickly and
can afford tech debt, consider using another language initially. However, for
long-term projects, Rust's benefits will outweigh the initial learning curve.

### Your Team Must Be On Board

Introducing Rust can be a disruptive change, and it's vital to have the backing
of both the team and leadership. Make sure everyone understands the benefits and
challenges of using Rust.

#### Find a Rust Champion

It is adivsed to have a Rust champion within your team who is passionate about
Rust and willing to lead the adoption effort. They will serve as the cornerstone 
for your Rust adoption process and can make a big difference by flattening the
learning curve for the rest of the team.
Ideally, a good champion already has some experience with Rust in production
or at least built a few larger projects with it.

If there is nobody who is willing to take over that role, start questioning if
Rust is the right choice. Perhaps the team is not ready for Rust yet or 
it is happy with the current technology stack.
An external consultant can not replace an internal champion.  

#### Run a Survey to Gauge Interest and Concerns

I like to run a survey to gauge the team's interest in Rust.
In there, I ask questions like:

- What is your current language of choice?
- On a scale from 1 to 5, how interested are you in learning Rust?
- What are your concerns about adopting Rust?
- Which other languages would you consider using instead of Rust for the project?
- In your opinion, what are the main benefits for choosing Rust for this project?
- Would you be willing to take on a Rust project? If so, in what capacity?

#### Address Concerns and Answer Questions in a Relaxed Setting

If you get mixed results, it might be a good idea to do a Rust Q&A session with
the team on a Friday afternoon. This way, you can address concerns and answer
questions in a relaxed setting.

#### Get External Help (Consultants, Training)

Many companies wait too long to get professional help for their Rust projects.
I think some of them got burned in the past by hiring consultants who didn't
deliver what they promised. 
Other companies think they can do it all by themselves, but this often leads to 
bad developer experience, frustration, and in the worst case, the
abandonment of Rust in the organization. 

I am biased of course, but a good instructor can be an accelerator.
They can help avoid costly mistakes, lead the company's discussion about Rust, and set the team up for success.

Hiring consultants can accelerate the exploration process and mitigate risks.
Experts can scaffold the project architecture, put best practices like testing
and CI/CD in place, and train the team, ensuring a smooth transition for
everyone involved.

I think many companies are afraid of hiring consultants because they think it
is expensive. But in the long run, it is often cheaper to clarify things early
on and avoid costly mistakes. On top of that, the team will benefit the most
early on and start with a solid foundation. It's similar to a running coach
who helps you avoid injuries and improve your running technique.

### About Hiring Talent

Finding and hiring the right talent is crucial for the success of your Rust
project. This section will provide insights into hiring strategies and what to
look for in candidates.

#### People with Production Experience Are Hard to Find and Expensive

It's challenging to find developers with Rust production experience. Competing
with the crypto industry, which heavily uses Rust, makes it even harder.
The salaries for Rust developers in crypto can be 2-3 times higher than in other
industries and the pool of talent is small.

Unless you are a hot new startup or have a big budget, finding people with Rust
production experience can be challenging and costly.

Instead of focusing solely on experience, consider finding junior- to mid-level developers who are smart, curious,
and eager to learn Rust. Good candidates often have experience
in related areas (like Kotlin or TypeScript) and are interested about ways to grow.
With trust and mentorship by the Rust champion and a lead engineer, it won't take long until the can carry their weight in the team.

#### People in Infrastructure Roles Are Also a Great Fit

Candidates from infrastructure roles interested in scalability, performance, and
networking can also be great additions to your team. Look for those with previous
admin roles, which worked close to the metal and have a good understanding of
how things work under the hood. Find people who can read documentation and are
not afraid to dive into the source code.

### On Finding The Right Project

Start Small, But Not Too Small.

Begin with a project that is close to your core business but not
mission-critical. This approach allows your team to gain experience with Rust
without risking significant disruption.

### Ways to Integrate Rust

There are various ways to integrate Rust into your existing infrastructure:

- **CLI Tools**: Develop command-line tools in Rust.
- **FFI Layer**: Use Rust to call functions in other languages.
- **Microservices / Network Layer**: Implement microservices in Rust.
- **WebAssembly for Frontend**: Use Rust to compile to WebAssembly for frontend
  development.
- **Embedded Systems**: Develop embedded systems in Rust.

Pick the integration method that aligns with your project's requirements and
team's expertise. Choose a method that allows you to leverage Rust's strengths
while minimizing risks. Rust can be a great fit for performance-critical parts
of your application, such as networking and data processing.
Once the team sees the benefits of Rust, they will be more open to using it in
other parts of the business, so pick a project with a huge upside and
is easy to replace if things go wrong. A microservice is a good candidate for
this. In the worst case, you can rewrite it in another language. You can gradually
shift over traffic to the Rust service and see how it performs in production.

I personally would not start with a CLI tool, because it is often not close to
the core business and the team might not see the benefits of Rust.
Similarly, I would not start with WebAssembly, because it is a complex topic
and the team might get frustrated with the tooling and the ecosystem. There might
also not be any immediate upside, such as faster performance and the team might
get the wrong impression about Rust.

I saw some some great results with Rust for embedded systems, where 
the tooling is excellent and there is a clear project boundary. 

The FFI layer is a good choice if you have a large codebase in another language
and want to gradually replace parts of it with Rust. For example,
some teams write a performance-critical section of their Java monolith in Rust
for 2-3x performance improvements.

### Read Up On Rust Before You Start

No matter how you plan to integrate Rust into your project, make sure to read up
on the language and its ecosystem. Here are the best resources I know of right now:

- [The Rust Book](https://doc.rust-lang.org/book/): A must-read for every developer on the team.
  Make sure that everyone on the team gets a copy or reads it online.
- [Rustlings](https://github.com/rust-lang/rustlings): Fun, short exercises to get started with Rust.

Once your done with those, get more specific knowledge by looking through the
books on this [Rust books list](https://github.com/sger/RustBooks)
and the resources for [idiomatic Rust](https://corrode.dev/blog/idiomatic-rust-resources/).

### Become An Active Part Of The Community

If you're starting to get serious about Rust, don't stand on the sidelines. Engage with the Rust community through [forums](https://users.rust-lang.org/), and by sharing
your insights on your developer blog.
Subscribe to the [This Week in Rust](https://this-week-in-rust.org/) newsletter to stay up-to-date on the latest news and developments in the Rust ecosystem.
Being an active community member can provide valuable support and keep you updated on best practices.

### Have a Policy for Async Rust and Accepted Crates

What is your companies position on async Rust?
You should establish that early on, because it can have a big impact on your
project. Some companies are fine with using async Rust everywhere, while others
use it only when necessary. For the rest of the application (such as their domain model), they stick to
synchronous code.
Either way, establish a policy early on and make sure everyone is on the same page.

Same goes for third-party crates. Some companies are fine with using any crate
from crates.io, while others are more conservative and only use crates that have
been around for a while and have a good reputation.
I find [blessed.rs](https://blessed.rs/) to be a good resource for finding high-quality crates.

Choosing the right crates can have a big impact on the [long-term maintainability](/blog/long-term-rust-maintenance/) of your project.
of your project.


### Have a Migration Strategy

Answer the following questions before starting the migration:

- What are the milestones for the migration?
- How will you handle the transition period? E.g. will you run both systems in parallel?
- How will you ensure that the team is productive during the migration?
- What is your fallback plan if the migration fails? Can you roll back to the old system?
- How will you measure the success of the migration? What are the key metrics?
- How will you ensure that the team is productive with the new technology?

Document your position on these questions for future reference and to ensure
that everyone is on the same page.

### Eliminate the Unknown Unknowns

Don't wait too long to ask for help. Many companies try to do everything
themselves and get stuck. Bringing in a consultant early in the project can set
you up for success by eliminating unknowns and providing expert guidance.

By following these strategies, you can ensure a successful Rust adoption for
your first production project. With careful planning, a supportive team, and the
right resources, Rust can become a valuable asset for your organization.