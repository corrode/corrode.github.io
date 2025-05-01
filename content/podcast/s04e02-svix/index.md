+++
title = "Svix"
date = 2025-05-01
template = "episode.html"
draft = false
aliases = ["/p/s04e02"]
[extra]
guest = "Tom Hacohen"
role = "CEO"
season = "04"
episode = "02"
series = "Podcast"
+++

We don't usually think much about Webhooks -- at least I don't.
It's just web requests after all, right? 
In reality, there is a lot of complexity behind routing webhook requests through the internet.

What if a webhook request gets lost?
How do you know it was received in the first place?
Can it be a security issue if a webhook gets handled twice? (Spoiler alert: yes)

<!-- more -->

Today I sit down with Tom from Svix to talk about what it takes to build an enterprise-ready 
webhook service. Of course it's written in Rust.

{{ codecrafters() }}

## Show Notes

### About Svix

Svix provides webhooks as a service.
They build a secure, reliable, and scalable webhook sending and receiving system using Rust. 
The company handles billions of webhooks a year, so they know a thing or two about the complexities involved.

### About Tom Hacohen 

Tom is an entrepreneur and open source maintainer from Tel-Aviv (Israel) and based in the US.
He's worked with people from all around the globe (excluding Antarctica).
Prior to Svix, he worked as an Engineer at Samsung's Open Source Group on the Enlightenment Foundation Libraries (EFL) 
that are used by the Samsung backed Tizen mobile operating system.

### Links From The Episode


### Official Links

- [Svix](https://www.svix.com/)
- [Tom Hacohen's Blog](https://stosb.com/)
- [Tom on GitHub](https://github.com/tasn/)
- [Tom on Mastodon](https://mastodon.social/@tasn)
