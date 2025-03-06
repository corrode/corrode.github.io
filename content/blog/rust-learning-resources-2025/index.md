+++
title = "Rust Learning Resources 2025"
date = 2025-03-05
template = "article.html"
[extra]
series = "Rust Insights"
+++

When I ask developers how they learn best, I tend to get the same answers:

- It should be **hands-on**.
- It should be **applicable to their work**. 
- The content should be **up-to-date** and created by **experienced developers**.
- People want to use **their own development environment**.

All of the above are valid points and they also apply to learning Rust. 

If you've been thinking about learning Rust for a while now and perhaps you've even started dabbling with it,
it's time to finally put that plan into action.
To save you some time, I've compiled a list of my favorite resources for learning Rust in 2025 below.

## CodeCrafters

- Level: Intermediate to Advanced
- Focus: Real-world projects / Systems programming 
- Time-commitment: a few days to a few weeks per project (depending on your experience)

CodeCrafters' claim to fame was their focus on teaching programming through real-world projects.
They now have a Rust track that features projects which excite developers interested in systems programming.

Some of their projects include building your own Shell, grep, Interpreter, HTTP server, Redis, Kafka, Git, SQLite, and DNS server.

Within a few days of concentrated effort, you'll be able to build some of these projects from scratch.
At the end, you'll have a solid understanding of Rust and a system that you know from work.
Also, you can use these projects as a reference for your work or show them off to your friends.
 
If you already know how to code in another language, I believe that CodeCrafters is the best resource for learning advanced Rust concepts and systems programming at the moment. 

## Rustlings

- Level: Beginner to Intermediate 
- Focus: Small exercises / Rust basics 
- Time-commitment: a few minutes to a few hours 

The classic Rust learning resource.
If it was a cocktail, it would be an [Old Fashioned](https://en.wikipedia.org/wiki/Old_fashioned_(cocktail)).
It's great for beginners and people who want some focused refresher on specific Rust concepts.

You can run Rustlings from the command-line and it will guide you through a series of exercises.

Getting started, is as easy as running the following commands:

```sh
cargo install rustlings
rustlings init
cd rustlings/
rustlings
```

Go [here](https://github.com/rust-lang/rustlings) to learn more.

## Rustfinity

- Level: Beginner to Intermediate 
- Focus: Small exercises / Rust basics 
- Time-commitment: a few minutes to a few hours 

Rustfinity is a bit like Rustlings, but more structured.
It has an interactive browser-based interface that guides you through each exercise and provides unit tests to verify your solutions.

You start with "Hello, World!" and work your way up to more complex exercises.
It's a relatively new resource, but I did some of the exercises myself and I enjoyed working with the platform.

They also hosted an "Adevnt of Rust" event with some more gnarly challenges [here](https://www.rustfinity.com/advent-of-rust).

Learn more at the [Rustfinity website](https://www.rustfinity.com/).

## 100 Exercises To Learn Rust

- Level: Beginner to Intermediate 
- Focus: Small exercises / Rust basics 
- Time-commitment: a few minutes to a few hours 

This is a relatively new resource by Luca Palmieri.
It's a collection of 100 exercises that you can solve to learn Rust.
This course is based on the "learn by doing" principle.
It has been designed to be interactive and hands-on.
You can go through the course material in the browser or download it as a PDF file, for offline reading.

There is a local CLI tool called `wr`, which will verify the solutions to the exercises.

You can find the course [here](https://rust-exercises.com/100-exercises/).

## Workshops

- Level: Beginner to Intermediate 
- Focus: Focused exercises and small projects 
- Time-commitment: a few days of focused effort 

If you prefer learning in a group setting and you have some budget, I recommend
looking for Rust workshops. I'm biased here, but I think it's worth the effort to get quality training
from an experienced Rust developer, especially if you are considering using Rust at work.

My workshops are hands-on and tailored to the needs of the participants.

The course material is open source and available on GitHub:

- [Write Yourself a Web App](https://github.com/corrode/write-yourself-a-web-app) - Build a small web app which shows weather data. 
- [Write Yourself a CLI](https://github.com/corrode/write-yourself-a-cli) - Build a small CLI app for finding files on your system. 
- [Write Yourself a Shell](https://github.com/corrode/write-yourself-a-shell) - Build a small, but fully functional shell from scratch in Rust

You can go through the material on your own and see if it's a good fit for you and your team. 
Once you're ready, feel free to reach out for tailoring the material to your needs.

{% info(title="Speed Up Your Learning Process", icon="crab") %}

Is your company considering to to Rust? 

Rust is known for its steep learning curve, but with the right resources and guidance, you can become proficient in Rust in a matter of weeks.
I offer hands-on workshops and training for teams and individuals who want accelerate the learning process. 
Check out my [services page](/services) or [send me an email](mailto://hi@corrode.dev) to learn more. 

{% end %}

