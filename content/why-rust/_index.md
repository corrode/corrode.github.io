+++
title = "Why Rust in Production?"
template = "page.html"
sort_by = "date"
+++


<img src="/why-rust/hero.svg" alt="Why Rust?">

Interest in Rust has risen sharply in recent years, however, there is little
information on why large organizations really use Rust in production. 

Much of the dialogue about Rust is driven by those who have not leveraged Rust
in a significant production capacity, or have only done so for non-critical
systems. Moreover, organizations heavily invested in Rust typically lack
motivation to share their insights publicly. This results in a distorted
understanding of Rust's application in production settings, with commentary
frequently highlighting its performance benefits, but omitting other important
factors driving its adoption.

Drawing from my consultations with companies that use Rust in production, I've
gained insight into the true motivations for their use of Rust. 
I found that companies value productivity, stability, and long-term
maintainability over performance.
This overview distills key insights, offering a resource for businesses to
assess whether Rust is the right tool for their use-case or not.

The intent is to provide an honest look at Rust's practicality for production
to help decision-makers understand its benefits and challenges.

## Reasons For Using Rust In Production

### Reliability and Stability

From experience, the majority of companies care less about uncompromising
performance and more about [reliability and
stability](https://talks.osfc.io/osfc2021/talk/JTWYEH/) of their services. More
predictable and stable services are easier to maintain and cheaper to operate.
Less time is spent on debugging and on-call, and more time on building new
features. Scaling services is also easier when you know how systems behave under
load. 

> Given our small team size, infrastructure reliability is crucial, otherwise,
> maintenance starves innovation. Rust provides us with confidence that any code
> modification or refactor is likely to produce working programs that will run for
> months with minimal supervision. - [xAI (formerly Twitter)](https://x.ai/)

This results in real cost savings for companies.

As requirements grow, Rust is a great language for building larger applications
that are maintained by a bigger team over a long period of time. This is due to
its strong type system, its focus on memory safety, its powerful tooling (cargo,
rustfmt, clippy, etc.) and its stability guarantees (backwards compatibility)
due to its edition system. All of that makes large-scale refactoring easier.

> We always talk about the performance gains [...] when using Rust but honestly I
> much more look for the stability gains. - [Stefan Baumgartner, Senior Product Architect at Dynatrace](https://www.youtube.com/watch?v=KTJIsicwW5s)

### Predictable Runtime Behavior

Predictable runtime behavior is closely related to reliability and stability.
It means that services run smoothly without any hiccups. This is especially
important for latency-sensitive services like games, chat applications, or
services that need to act on real-time data.

Discord has a [great
article](https://discord.com/blog/why-discord-is-switching-from-go-to-rust)
about why they switched from Go to Rust. They mention that Go's garbage
collector was a source of unpredictable latency spikes. After switching to Rust,
they were able to fully get rid of garbage collection and have a more
predictable runtime behavior.

> When we started load testing, we were instantly pleased with the results. The
latency of the Rust version was just as good as Go’s and had no latency spikes!

Here is a diagram from the above article by Discord.
Notice how the latency spikes in the Go version are gone in the Rust version
and how that impacts the 95th percentile response time, making it much more
predictable and smooth.

<img src="/why-rust/discord.png" alt="Discord Go vs Rust">

Another example is
[Cloudflare](https://blog.cloudflare.com/big-pineapple-intro/),
which uses Rust to power their DNS service, [1.1.1.1](https://1.1.1.1/). They
mention that Rust's predictable runtime behavior is a big reason for using it:

> One of the things we’ve learned with the previous implementations is that, for
a service open to the public, a peak performance of the I/O matters less than
the ability to pace clients fairly.

Furthermore, Rust shows excellent runtime behavior when handling network requests.
In a [benchmark by Eugene Retunsky](https://medium.com/star-gazers/benchmarking-low-level-i-o-c-c-rust-golang-java-python-9a0d505f85f), Rust had the lowest tail latency and maximum throughput next to C and C++. 

Here is the diagram from the benchmark, showing the p99.9 latency for each
language under test. As the requests per second increase, the latency for Rust
stays low and stable. Go and Java on the other hand have a higher baseline
latency while Python shows latency spikes at a certain point.

<img src="/why-rust/runtime.png" alt="Rust Runtime behavior">

The author concludes:

> In conclusion, Rust has a much lower latency variance than Golang, Python, and especially Java. 
> [...] Rust might be a better alternative to Golang, Java, or Python if predictable performance is crucial for your service. Also, before starting to write a new service in C or C++, it’s worth considering Rust. - [Eugene Retunsky](https://medium.com/star-gazers/benchmarking-low-level-i-o-c-c-rust-golang-java-python-9a0d505f85f7)


### Cost Savings

Rust has a low runtime overhead. This is especially important for services that
need to scale to handle a large number of requests.
It can save a lot of money on cloud infrastructure costs.

For example, AWS has a service called
[Firecracker](https://aws.amazon.com/blogs/aws/firecracker-lightweight-virtualization-for-serverless-computing/),
which runs virtual machines with very low overhead. It powers AWS Lambda functions and AWS Fargate containers.

> Firecracker consumes about 5 MiB of memory per microVM. You can run thousands
of secure VMs with widely varying vCPU and memory configurations on the same
instance.

The better hardware utilization translates to lower costs for companies.

Firecracker allowed AWS to improve the efficiency of Fargate and help us pass on cost savings to customers.
As a result, we are reducing the price of Fargate by up to 50%. 
([Image source](https://shahbhargav.medium.com/firecracker-secure-and-fast-microvms-628e6043b572) and
[AWS announcement](https://aws.amazon.com/blogs/compute/aws-fargate-price-reduction-up-to-50/))

<img src="/why-rust/fargate.png" alt="Firecracker" />


### Ergonomics

Rust has a great developer experience. Its type system is very powerful and
allows you to encode complex invariants about your system in the type system.
This allows you to catch bugs at compile-time instead of at runtime.

Furthermore, concepts like pattern matching, enums, `Result` and `Option` types
allow for concise and expressive code.

> Rust has been a force multiplier for our team, and betting on Rust was one of
> the best decisions we made. More than performance, its ergonomics and focus on
> correctness has helped us tame sync’s complexity. We can encode complex
> invariants about our system in the type system and have the compiler check them
> for us. - [Dropbox](https://dropbox.tech/infrastructure/rewriting-the-heart-of-our-sync-engine)

### Focus on Long-Term Sustainability

Companies rarely rewrite their services in another language. It incurs a lot of costs
and risks. Only if a rewrite promises a *significant* upside, companies will
consider it.

One well-known company that started to heavily invest in Rust is Microsoft.

> Microsoft is going big on Rust and spending $10 million to make it 1st class
> language in our engineering systems + $1 million @rustlang foundation. - [David Weston, Vice President of OS Security and Enterprise at Microsoft](https://twitter.com/dwizzzleMSFT/status/1720134540822520268)

Microsoft even [integrated Rust into the Windows kernel](https://twitter.com/markrussinovich/status/1656416376125538304).
The fact that they take big bets on Rust shows that they are in it
for the long run. This is a good sign for the Rust ecosystem, as the backing of
a large company can help Rust to become more mainstream and ensure
long-term sustainability.

Similarly, [the Linux kernel now supports Rust](https://www.kernel.org/doc/html/next/rust/index.html)
as well.
The Kernel incorporating Rust is a major endorsement of the language. Notably,
the Linux Kernel maintainers have previously [refused to integrate C++ in the Kernel](http://harmful.cat-v.org/software/c++/linus).

For another take on this, watch ["In It for the Long
Haul"](https://www.youtube.com/watch?v=WnIWRks35Fk) by [Carol
Nichols](https://twitter.com/carols10cents).

### Productivity And Developer Happiness

Many developers enjoy working with Rust. It is the most admired language for the
6th year in a row according to the [StackOverflow Developer Survey](https://survey.stackoverflow.co/2023/#section-admired-and-desired-programming-scripting-and-markup-languages).
More than 80% of developers that use it want to use it again next year.

For teams that are looking to hire and retain talent, Rust is a great choice
because developer happiness is a big factor in job satisfaction and has a positive
impact on productivity.

### Performance

As stated earlier, performance often gets mentioned as a main reason for using Rust.
Rust also has great support for multi-threaded workloads. Libraries like
[rayon](https://github.com/rayon-rs/rayon) and [Tokio](https://tokio.rs/) are considered
best-in-class for writing high-performance applications.

Making efficient use of compute resources has much deeper implications for
companies than just raw execution speed. One important aspect is energy efficiency.

In the below benchmark, taken from ["Energy Efficiency across Programming Languages"](https://greenlab.di.uminho.pt/wp-content/uploads/2017/10/sleFinal.pdf)
by Pereira et al., Rust has superior runtime performance on par with C and C++
and faster than Go by a factor of 2-3x as well as Python by a factor of 70x.

| Lang        | Time (Normalized) |
|-------------|-------------------|
| C           | 1.00              |
| Rust        | 1.04              |
| C++         | 1.56              |
| Java        | 1.89              |
| Go          | 2.83              |
| JavaScript  | 6.52              |
| PHP         | 27.64             |
| Ruby        | 59.34             |
| Python      | 71.90             |

This translates to lower energy consumption as well. 
Energy is an important cost factor for companies at scale.

<img src="/why-rust/energy-consumption.svg" class="invert" alt="Energy Efficiency across Programming Languages" />

## Reasons Against Using Rust In Production

### Immature ecosystem

Rust is a relatively young language. Version 1.0 was first released in 2015.
This means that the ecosystem is still maturing. Many important libraries [did not see their 1.0 release yet](https://www.reddit.com/r/rust/comments/11byl6u/why_is_every_crate_pre10/).

This phenomenon has been [brought up as a reason to be cautious when using Rust in production](https://www.reddit.com/r/rust/comments/11byl6u/why_is_every_crate_pre10/ja3auop/).

In practice, it might be hard to find production-grade libraries for specific
needs. Your team might be required to write custom crates or improve existing
ones. Furthermore, [sponsoring open source maintainers](https://github.com/sponsors/explore?ecosystem=RUST) to work on critical
dependencies is a good way to ensure that the long-term sustainability of the
ecosystem.

That said, libraries for common tasks like JSON parsing or network handling are
very robust and stable and considered best-in-class. Breaking changes are rare
and important crates like `serde` or `tokio` are already past their 1.0 release.

### Lack Of Developers

Related to the previous point, the Rust community is still relatively small.
It is hard to find developers with professional Rust experience. 

From talking to companies that use Rust in production, I found that they are
mostly training their developers on the job.
Moreover, Rust is noted for enabling a smooth onboarding process for engineers
already proficient in languages like C++ or Java.

On the other hand, Rust developers are generally very passionate about their
craft and are actively seeking out jobs that allow them to use Rust,
so the market for Rust developers is growing. (Also see
the previous section about developer happiness.)

> Rust has more than tripled the size of its community over the past two years
> and currently has 3.7M users, of which 0.6M joined in the last six months
> alone.[...] Furthermore, Rust has built a loyal community of developers who care
> about memory safety and security. - [State of the Developer Nation 24th Edition - Q1 2023 report](https://www.developernation.net/resources/reports/state-of-the-developer-nation-24th-edition-q1-2023)

<a href="https://www.developernation.net/resources/reports/state-of-the-developer-nation-24th-edition-q1-2023" target="_blank">
<img src="/why-rust/communities.svg" class="invert" alt="Programming Language Communities Size">
</a>

### Tooling

Cargo, rustfmt, clippy, and rust-analyzer
are all great tools that make Rust development a joy. 
However, [debugging support is still lacking](https://rustc-dev-guide.rust-lang.org/debugging-support-in-rustc.html).
[The story for profiling support is similar.](https://www.jetbrains.com/lp/devecosystem-2021/rust/)

Recently, [JetBrains announced RustRover](https://www.jetbrains.com/rust/),
a new IDE for Rust which is based on IntelliJ.
This is a strong signal that JetBrains sees it as a good investment to build
tooling for Rust developers and that they expect Rust to become more mainstream.

### Learning Curve

Rust has a famously steep learning curve. It is a complex language with many
advanced features. 

When asked why they don't use Rust, participants of the [2022 Annual Rust Survey](https://blog.rust-lang.org/2023/08/07/Rust-Survey-2023-Results.html#rust-usage)
mentioned the learning curve as the main reason:

<img src="/why-rust/why-not-rust.svg" class="invert" alt="Why not Rust?">

In the [Rust 2020
survey](https://blog.rust-lang.org/2020/12/16/rust-survey-2020.html#improved-learnability),
participants were asked to rate the difficulty of various Rust concepts. Here
are the results:

<img src="/why-rust/topic-difficulty-ratings.svg" class="invert" alt="Difficulty by topic">

Lifetime annotations, ownership, and borrowing are the most difficult topics to
grasp for learners. These are important concepts, which need to be understood to
become proficient in Rust.

It is important to set clear expectations for your team when adopting Rust: Rust
is not a language that you can learn in a few days. It requires practice to internalize
the concepts around ownership and borrowing to become productive with it.
Typically, it takes a few months to become productive with Rust:

> Based on our studies, more than 2/3 of respondents are confident in
> contributing to a Rust codebase within two months or less when learning Rust.
> Further, a third of respondents become as productive using Rust as other
> languages in two months or less. **Within four months, that number increased to
> over 50%.** - [Google](https://opensource.googleblog.com/2023/06/rust-fact-vs-fiction-5-insights-from-googles-rust-journey-2022.html)

Depending on your immediate needs, this might be a deal-breaker for your team.
Other languages like Go or Python have a much lower learning curve and are
a better fit for rapid prototyping.

### Compile Times

Rust has a reputation for having long compile times. This is especially true for
large projects with many dependencies.

> Slow build speeds were by far the #1 reported challenge that developers have
> when using Rust, with only a little more than 40% of respondents finding the
> speed acceptable. - [Google](https://opensource.googleblog.com/2023/06/rust-fact-vs-fiction-5-insights-from-googles-rust-journey-2022.html)

Rapid iteration is important for developers. Long compile times can be a
productivity killer. This is especially true for developers that are used to
languages like Go or Python, where the feedback loop is much faster.

Compile times are a known issue and the Rust team is [working on improving them](https://nnethercote.github.io/2023/03/24/how-to-speed-up-the-rust-compiler-in-march-2023.html).
For advice on how to improve compile times, see [my article on this topic](https://endler.dev/2020/rust-compile-times/) with many practical tips.
For medium-sized projects, compile times are less of an issue. 
[Modern hardware can also mitigate the issue to some extent.](https://www.reddit.com/r/rust/comments/qgi421/doing_m1_macbook_pro_m1_max_64gb_compile/)

## Conclusion

Rust is a great language for building large-scale, reliable, and stable
applications. It is a good fit for companies that value productivity and
developer happiness and see it as a long-term investment.

On the other side, Rust is still a young language and the ecosystem is still
maturing. It has a steep learning curve and long compile times.

These challenges are not insurmountable, however. They require a commitment to
Rust and a willingness to invest in training and tooling.

Navigating the decision to integrate Rust into your technology stack is pivotal
and requires thoughtful consideration. Should you find yourself weighing its
benefits against your specific requirements, professional guidance can prove
invaluable. Equally, if you are ready to embrace Rust and are seeking expertise
in training or consulting to ensure a smooth transition, specialized support is
essential.

[Get in touch with me](/about/) to explore how Rust can contribute to your long-term success. 

## Further Reading

* <a href="https://opensource.googleblog.com/2023/06/rust-fact-vs-fiction-5-insights-from-googles-rust-journey-2022.html" target="_blank">Rust Fact vs. Fiction: 5 Insights from Google’s Rust Journey</a>
* <a href="https://survey.stackoverflow.co/" target="_blank">StackOverflow Developer Surveys</a>
* <a href="https://blog.rust-lang.org/2023/08/07/Rust-Survey-2023-Results.html" target="_blank">Annual Rust Survey Results</a>

---

<small>
Title image modified from
<a href="https://www.freepik.com/free-vector/metallurgical-industry-company-isometric-vector-web-banner-with-pouring-molten-metal-from-steel-ladl_4015233.htm#page=2&query=rust%20in%20production&position=28&from_view=search&track=ais" target="_blank" rel="noopener noreferrer">vectorpouch</a> on Freepik
</small>