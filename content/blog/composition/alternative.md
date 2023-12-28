+++
title = "Composition in Rust"
date = 2023-12-07
template = "article.html"
draft = false
[extra]
series = "Idiomatic Rust"
reviews = [
]
+++

In languages like Java or C++, inheritance is a common pattern for
code reuse. When learning Rust, however, one of the first things you'll notice
is that does not have a concept of inheritance and instead favors trait-based
composition. 

Mastery of composition is one of the cornerstones of writing idiomatic Rust code.
It allows you to build reusable components that can be tested in isolation and
combined to create robust, flexible systems.

Unfortunately, there are few actionable resources on how to write
composable code in Rust, which is why it is the topic of this article.

## Welcome to Crustacean Candy

Imagine you're the owner of Crustacean Candy, an online store offering
Rust-themed candy bars and other treats. Customers love your delights
ranging from "Ferris' Fudgy Feast" to "Rusty ICE-cream."

## The Order Processing System

As every true Rustacean, you've written your shop system in Rust. 
It has an `order` endpoint that takes a JSON payload and stores it in a database
as well as writing it to the console.

Here is the data model for an order:

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
struct Order {
    id: String,
    customer_id: String,
    products: Vec<Product>,
}

#[derive(Debug, Deserialize, Serialize)]
struct Product {
    name: String,
    quantity: u32,
    price: f32,
}
```

And here is how we process an order:

```rust
/// Stores the order in the database and writes it to the console.
fn process_order(order: Order) {
    // Store the order in the database.
    let db = Database::new();
    db.store_order(&order);

    // Write the order to the console.
    println!("Order processed: {:?}", order);
}
```

## The Order Processing System Grows

Your business is booming, and you're getting more and more orders.
To keep up with the demand, you hire a new developer, Alice, who is
in charge of improving the order processing system.

Alice's first task is to add a new feature: sending an email to the customer
when their order has been processed. She adds a new `EmailSender` struct

```rust
struct EmailSender {
    // ...
}

impl EmailSender {
    fn new() -> Self {
        // ...
    }

    fn send_email(&self, order: &Order) {
        // ...
    }
}
```

and adds a call to `EmailSender::send_email` to the `process_order` function:

```rust
fn process_order(order: Order) {
    // Store the order in the database.
    let db = Database::new();
    db.store_order(&order);

    // Send an email to the customer.
    let email_sender = EmailSender::new();
    email_sender.send_email(&order);

    // Write the order to the console.
    println!("Order processed: {:?}", order);
}
```


