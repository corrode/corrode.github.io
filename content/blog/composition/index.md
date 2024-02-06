+++
title = "Composition over Inheritance"
date = 2023-01-21
template = "article.html"
draft = false
[extra]
series = "Idiomatic Rust"
reviews = [
]
+++

In languages like Java or C++, inheritance is a common pattern for
code reuse. When learning Rust, however, one of the first things you'll notice
is that it does not have a concept of inheritance and instead favors trait-based
composition. 

Mastery of composition is one of the cornerstones of writing idiomatic Rust code.
It allows you to build reusable components that can be tested in isolation and
combined like Lego blocks to create robust, flexible systems.

Unfortunately, there are few *actionable* resources on how to write
composable code in Rust, which is why it is the topic of this article.

## Welcome to Crustacean Candy 

Imagine you're the owner of *Crustacean Candy*, an online store offering
Rust-themed candy bars and other treats. Customers love your delights
ranging from "Ferris' Fudgy Feast" to "Rusty ICE-cream."

## The Order Processing System

Initially, the only order type you have is a one-time order. 

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
struct Order {
    id: String,
    customer_id: String,
    date: DateTime<Utc>
    items: Vec<Product>,
    total_price: f64,
    status: OrderStatus, // e.g., pending, shipped, or delivered
}
```

To process orders, you store them in a database and write them to the console.

```rust
fn process_order(order: Order) {
    println!("A new order was placed! {:?}", order);

    // Store the order in the database
    // ...

}
```

## Adding Subscriptions

Next to one-time orders, you would also like to offer a subscription service,
which allows customers to receive a box of candy every month. So you get to
work.

```rust
#[derive(Debug, Deserialize, Serialize)]
struct Order {
    id: String,
    customer_id: String,
    date: DateTime<Utc>
    items: Vec<Product>,
    total_price: f64,
    status: OrderStatus,
    subscription_details: Option<Subscription>, // new!
}

struct Subscription {
    start_date: DateTime<Utc>,
    last_processed: DateTime<Utc>,
    status: SubscriptionStatus, // e.g., active, paused, or canceled
    interval_days: u32, // Number of days between each delivery, e.g. 30
}
```

Every day you'd run a query to process all subscriptions that are due for that day.

```sql
SELECT o.*
FROM orders o
WHERE o.subscription_status = 'active'
  -- The order is due if the last processed date is further in the past than the interval days
  AND DATE_ADD(o.last_processed, INTERVAL o.interval_days DAY) <= CURRENT_DATE();
```

## Payments

The other part of order processing is handling payments. You decide to add a
`payment_method` field to the `Order` struct.

```rust
#[derive(Debug, Deserialize, Serialize)]
enum PaymentMethod {
    // You probably don't want to store the actual credit card details in the database
    CreditCard { card_number: String, expiry_date: String, cvv: String },
    PayPal { account_id: String },
    RustCoin { address: String },
    GiftCard { code: String },
}
```

You add the `payment_method` field to the `Order` struct.

```rust
#[derive(Debug, Deserialize, Serialize)]
struct Order {
    id: String,
    customer_id: String,
    date: DateTime<Utc>
    items: Vec<Product>,
    total_price: f64,
    status: OrderStatus,
    subscription_details: Option<Subscription>,
    payment_method: PaymentMethod, // new!
}
```

Our struct is getting longer and longer. It's starting to feel like a
kitchen sink.

And we haven't even covered

- Shipping methods
- Discounts
- Taxes
- Refunds

You get a feeling that the order processing system is getting harder and harder
to maintain and extend. Suddenly, the joy of adding new features is gone, and
you're spending more and more time fixing bugs. There are also more and more
edge cases that you need to consider and customers who are unhappy with your
service because incorrect orders.

One day you sit down to refactor the order processing system. You realize that
one core problem with the current solution was a lack of separation of concerns.
The `Order` struct has too many responsibilities. How would a more composable
solution look like?

Starting out, you have a few goals in mind:

- Handling one-time orders should be trivial.
- The `process_order` function should be straightforward to implement.
- Adding extra functionality should not impact existing code.
- Lastly, the system should be easy to test.
















## Summary

Traits are the building blocks of composable Rust code. They allow you to
describe *behaviors*. 



