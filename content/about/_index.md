+++
title = "About"
template = "page.html"
sort_by = "date"
+++

<style>
.img-stack {
    position: relative;
}

.img-stack img {
    border-radius: 4px;
}

.img-stack-hue {
    filter: hue-rotate(180deg);
}

@media (prefers-color-scheme: dark) {
    .img-stack-hue {
        filter: hue-rotate(335deg);
    }
}
</style>

<div class="img-stack">
  <img class="img-stack-hue" src="/about/endler-bg.jpg" alt="Background">
  <img src="/about/endler-fg.png" alt="Foreground" style="position: absolute; top: 0; left: 0;">
</div>

Hi, I'm <strong>Matthias Endler</strong>, a Rust developer and open source maintainer.

I support my clients around the world to get the most out of Rust through
training, consulting, and contracting with no-frills, easy-to-follow, [idiomatic
Rust](https://github.com/mre/idiomatic-rust) code.

Some popular Rust crates that I built are [tinysearch](https://github.com/tinysearch/tinysearch),
[hyperjson](https://github.com/mre/hyperjson), and
[lychee](https://github.com/lycheeverse/lychee).
I'm a Rustacean since 2015 and I've been working with Rust professionally since 2019.

You might have seen me speaking at conferences such as
[FOSDEM](https://www.youtube.com/watch?v=ePiWBGh35q0) in Brussels,
[Cod{e}motion](https://www.youtube.com/watch?v=imtejBNbm0o) in Amsterdam, and
[BrisTech](https://www.youtube.com/watch?v=sEcbTYLtLSM) in Bristol. I've also
given workshops at [emBO++](https://github.com/rust-embedded/wg/issues/235) in
Bochum,
[RustBeltRust](https://speakerdeck.com/mre/workshop-write-your-own-shell-in-rust)
in Columbus, OH and [RustFest](https://hackmd.io/ru4intliRlyJ9t8pU2F29A)
Barcelona.

Feel free to [get in contact](mailto:hi@corrode.dev) with me, I'm always up for
a chat!
