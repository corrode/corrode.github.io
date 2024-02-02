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
    products: Vec<Product>,
}
```

To process orders, you store them in a database and write them to the console.

```rust
/// Stores the order in the database and writes it to the console.
fn process_order(order: Order) {
    // Store the order in the database.
    // ...

    // Write the order to the console.
    println!("New order! {:?}", order);
}
```

## Adding Subscriptions

Next to one-time orders, you would also like to offer a subscription service, which allows customers to receive a box of candy every month. So you get to work.

The most pragmatic way might be to add an `is_subscription` field to the `Order` struct.

```rust
#[derive(Debug, Deserialize, Serialize)]
struct Order {
    id: String,
    customer_id: String,
    products: Vec<Product>,
    is_subscription: bool,
}
```

Once per month, a periodic job goes through the database to process all subscriptions.

```sql
SELECT * FROM orders WHERE is_subscription = true;
```

So far so good! The system is simple and a joy to work with.

## Adding Subscription Intervals

One day you get an email from a customer who wants a different subscription
interval.

Instead of receiving a box of candy every month, they want to receive
one every two weeks, which is good news because it's twice the revenue for you.

The only question is how you would at this to your system. 

Again, deciding on the most pragmatic solution, you quickly replace the `is_subscription` field with an optional `subscription_interval` in the `Order` struct.

```rust
#[derive(Debug, Deserialize, Serialize)]
struct Order {
    id: String,
    customer_id: String,
    products: Vec<Product>,
    start_date: DateTime,
    subscription_interval: Option<Duration>,
}
```

Every day you run a query to process all subscriptions that are due for that day.

```sql
SELECT *
FROM orders
WHERE subscription_interval != null
  AND DATE_ADD(last_processed, INTERVAL subscription_interval DAY) <= CURRENT_DATE();
```

## One-time discounts, and gifts

Your business is booming, and you're getting more and more orders.

One day you have the idea to add a special discount for customers who order
more than 10 candy bars. You add a `discount` field to the `Order` struct.
You also add the option to wrap orders as gifts.

```rust
#[derive(Debug, Deserialize, Serialize)]
struct Order {
    id: String,
    customer_id: String,
    products: Vec<Product>,
    subscription_interval: Option<Duration>,
    discount: Option<f32>,
    is_gift: bool,
}
```

You can see how your system now needs to handle orders that are vastly different
in nature (one-time purchases, subscriptions, gifts, etc.), making the logic in
functions like `process_order` convoluted and error-prone.


```rust
fn process_order(order: Order) {
    // Store the order in the database.
    // ...

    // Write the order to the console.
    println!("New order! {:?}", order);

    // Process the order.
    if order.subscription_interval.is_some() {
        // Process the subscription.
        update_subscription_details(&order);
        apply_subscription_discounts(&order);

        // Handle recurring billing
        if let Some(billing_info) = get_billing_info(order.customer_id) {
            process_recurring_payment(billing_info);
        }
    } else {
        // Process the one-time order.
        // ...
    }

    // Send an email to the customer.
    if order.is_gift {
        // Send a gift email.
        // ...
    } else {
        // Send a regular email.
        // ...
    }
}
```

Especially, simple one-time orders are now tiresome to handle.

```rust
let order = Order {
    id: "123".to_string(),
    customer_id: "456".to_string(),
    products: vec![Product {
        name: "Ferris' Fudgy Feast".to_string(),
        quantity: 1,
        price: 2.99,
    }],
    subscription_interval: None
    discount: None,
    is_gift: false,
};
```

You get a feeling that the order processing system is getting harder and harder
to maintain and extend. Suddenly, the joy of adding new features is gone, and
you're spending more and more time fixing bugs. There are also more and more
edge cases that you need to consider and customers who are unhappy with your
service because incorrect orders.

One day you sit down to refactor the order processing system.
You realize that one core problem with the current solution was a lack of separation of concerns. The Order struct has too many responsibilities.
How would a more composable solution look like?

Starting out, you have a few goals in mind:

- Handling one-time orders should be trivial.
- The `process_order` function should be straightforward to implement.
- Adding extra functionality should not impact existing code.
- Lastly, the system should be easy to test.
















## Summary

Traits are the building blocks of composable Rust code. They allow you to
describe *behaviors*. 



