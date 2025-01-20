+++
title = "Hubstaff - From Rails to Rust"
date = 2025-01-20
template = "article.html"
draft = false
[extra]
hero = "hero.png"
series = "Case Studies"
+++

It's 2019, and Hubstaff's engineering team is sketching out plans for their new webhook system.
The new system needs to handle millions of events and work reliably at scale.
The safe choice would be to stick with their trusty Ruby on Rails stack – after all, it had served them well so far.
But that's not the path they chose. 

## The Fork in the Road 

When I sat down with Alex, Hubstaff's Server Team Lead, he painted a vivid picture of that moment. "Our entire application stack was powered by Ruby and JavaScript," he told me. "It worked, but we knew we needed something different for this new challenge."

The team stood at a crossroads. Go, with its simplicity and familiar patterns, felt like as a safe harbor.
But there was another path – one less traveled at the time:

> "We chose to proceed with Rust," Alex recalled. "Not just because it was efficient, but because it would push us to **think in fundamentally different ways**."

[VISUALIZATION: Timeline showing the fork in the road - the safe path vs. the path they chose]

## Into the Unknown

Of course, there were moments of doubt.
Adding a new language to an already complex tech stack isn't a decision teams make lightly.

"There was skepticism," Artur Jakubiec, their Desktop Team Lead, admitted. "Not about Rust itself, but about balancing our ecosystem."

But instead of letting doubt win, Artur took action. He spent weeks building prototypes, gathering data, and crafting a vision of what could be. It wasn't just about convincing management – it was about showing his team a glimpse of the future they could build together.

[PHOTO PLACEHOLDER: The team Hubstaff team]

## The First Victory

Fast forward to today.

The webhook system is processing ten times the initial load without breaking a sweat.
Of course, the team had to make adjustments along the way, but not to their Rust code, but to their SQL queries.

> "Since its launch, we've had to optimize SQL queries multiple times to keep up with demand," Alex shared, "but we've never faced any issues with the app's memory or CPU consumption. Not once."

[GRAPH: Show the exponential growth in webhook processing with a flat line for resource usage]

## Finding Balance 

Instead of going all-in on Rust, Hubstaff found wisdom in balance. 

Here's their reasoning:

1. High-Load Operations → Rust
2. Lightweight APIs and Dashboard Backend → Rails
3. Communication through standardized APIs and message queues

But what about Rust's infamous learning curve? 

"Once developers are up to speed," Alex noted, "there's no noticeable slowdown in development. The Rust ecosystem has matured to the point where we're not constantly reinventing the wheel."

## Adopting Rust in more areas of the business 

Once the team gained enough confidence in Rust, they started rewriting their desktop application.
The easy path would have been Electron – the tried-and-true choice for web companies.
But Hubstaff had learned to trust that Rust would get the job done. 

> "Electron simply wasn't an option," Artur stated firmly. "We needed something lightweight, something that could bridge our future with our past. That's why we chose Tauri."

## Gaining Confidence in the codebase 

Was it all worth it? 
Let's look at the results:

- Desktop developers now contribute to backend services, breaking down old silos
- Five years without a single memory-related issue in production
- Their C++ developers are on-board with Rust's safety guarantees as well 
- Infrastructure costs stayed flat despite 10x growth

But perhaps the most profound change was invisible to monitoring tools.

> "With C++, there's a constant sense of paranoia about every line you write," Artur revealed. "Rust transformed that fear into confidence. It changed not just how we code, but how we feel about coding."

[TEAM PHOTO]

## A New Chapter Begins

Today, Hubstaff's journey continues.
Their Rust footprint grows steadily: 4,200 lines of mission-critical server code, 2,000 lines in their desktop app, and a team of passionate Rustaceans that's still growing.

But when I asked Alex and Artur what they're most proud of, it wasn't the technical achievements that topped their list. It was how they got there: thoughtfully, methodically, and together as a team.

[TIMELINE OF MILESTONES:
- 2019: The first brave step into Rust
- 2020: Webhook system proves its worth
- 2022: The desktop revolution begins
- 2023: Tauri transforms the desktop experience
- 2024: The journey continues...]

## Lessons for Fellow Adventurers

I asked what Alex and Artur would tell teams standing at their own crossroads. Their answer was simple:

1. Start with a clear mission, not just a technical preference
2. Invest in your team's journey through learning and support
3. Let data light your path forward
4. Build bridges between the old and the new
5. Look for opportunities where different paths converge

## The Journey Continues

As I wrapped up my conversation with the Hubstaff team, one thing became clear: this isn't just a story about adopting a new programming language. It's about having the courage to choose the path that feels right, even when it's not the obvious choice. It's about building something that lasts, not just something that "works for now."