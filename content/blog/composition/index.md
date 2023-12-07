+++
title = "Composition over Inheritance"
date = 2023-12-02
template = "article.html"
draft = true
[extra]
series = "Idiomatic Rust"
reviews = [
]
+++

In languages like Java or C++, inheritance is a common pattern for
code reuse. When learning Rust, however, one of the first things you'll notice
is that does not have a concept of inheritance and instead favors trait-based
composition. 

Mastery of composition is one of the key steps to writing idiomatic Rust code.
It allows you to build reusable components that can be tested in isolation and
combined to create robust, flexible systems.

Unfortunately, there are few actionable resources on how to write
composable code in Rust, which is why it's the topic of this article.

## The Case for Composition

Imagine you're the owner of Crustacean Candy, an online store for
Rust-themed candy bars and other treats. Customers love your delights
ranging from "Ferris' Fudgy Feast" to "Rusty ICE-cream."

To migrate to a new store platform, you need to convert your product catalog
from CSV to JSON.

```csv
name,kind,flavor,weight,price
Ferris' Fudgy Feast,Candy Bar,Chocolate,50,1.99
Corrode Caramel Crunch,Chocolate Bar,Caramel & Nuts,45,2.49
Mutable Mint Munchies,Mints,Mint,20,0.50
Trait Tongue Twisters,Candy Strips,Strawberry,30,1.00
...
```

You decide to write a small Rust program to do the conversion.

```rust
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Debug, Serialize, Deserialize)]
struct Candy {
    name: String,
    kind: String,
    flavor: String,
    weight: u32,
    price: f32,
}

fn main() -> Result<()> {
    // Read CSV file and filter out the invalid rows
    let mut rdr = csv::Reader::from_path("products.csv")?;
    let candies: Vec<Candy> = rdr.deserialize().filter_map(Result::ok).collect();

    // Convert to JSON
    let json = serde_json::to_string(&candies)?;

    // Write to file
    fs::write("products.json", json)?;

    Ok(())
}
```

This code works fine and soon you're happily serving customers through your new
online store.

After a while, you get a call from a retail chain that wants to sell your
products in their stores. That's good news! The only problem is that they
need the product catalog in XML format.

"No problemo!", you say, "you'll get the file faster than you can say "Trait Tongue Twisters!"

```rust

