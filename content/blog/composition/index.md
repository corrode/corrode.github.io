+++
title = "Composition over Inheritance"
date = 2024-02-15
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

## Products

Initially, the only type of product you have is candy.

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
struct Product {
    id: Id,
    name: ProductName,
    price: Price,
    weight: Weight,
}
```

where

```rust
struct Id {
    // The actual type is an implementation detail
    // and subject to change.
    id: uuid::Uuid,
}

struct ProductName {
    // This will be validated to be non-empty etc.
    name: String,
}

struct Price {
    amount: usize, // in cents
    currency: Currency, // e.g., USD, EUR, GBP
}

struct Weight {
    amount: usize, // in grams
    unit: WeightUnit, // e.g., g, kg, oz, lb
}
```

With that, you can create a `Product` like this:

```rust
let product = Product {
    id: Id::new(),
    name: ProductName::new("Ferris' Fudgy Feast".to_string()),
    price: Price::new(100, Currency::USD),
    weight: Weight::new(100, WeightUnit::Gram),
};
```

## Logging Orders

Every time a user opens a product page, you want to log that event.
You can do this by implementing the `Debug` trait for `Product`.

```rust
impl std::fmt::Debug for Product {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Product {{ id: {:?}, name: {:?}, price: {:?}, weight: {:?} }}",
            self.id, self.name, self.price, self.weight
        )
    }
}
```

And with that, you can log the product like this:

```rust
fn log_product_view(product: &Product) {
    println!("Product viewed: {:?}", product);
}
```

You might not have noticed, but this is a form of composition. 

The fact that `Product` implements `Debug` means that you can use it 
whenever a function, method, or macro expects a type that is `Debug`.

For instance, you can log other events like orders, payments, and shipments
using the same `log` function.

```rust
fn log_event(event: impl std::fmt::Debug) {
    println!("New Event: {:?}", event);
}
```

There are many other helpful traits in the standard library that you 
can use to compose your types. For example, you can implement `Display` to
format your product for the user interface, `Clone` to create a copy of the
product, and `PartialEq` to compare products. 
There's `Iterator` to iterate over the products, `From` and `Into` to convert
to and from other types, and `Error` to handle errors.
[Here's the entire list.](https://doc.rust-lang.org/std/all.html#traits) It
really isn't that long.

Lesson: **The trait system leads you towards composition.**

## Storing Products in a CSV File

Your small shop system requires the list of products to be stored in a CSV file.

That's why your `Product` struct and all its fields implement the `serde` traits
`Serialize` and `Deserialize`.

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
struct Product {
    id: Id,
    name: ProductName,
    price: Price,
    weight: Weight,
}
```

This way, you can easily write the list of products to a CSV file.

```rust
use std::fs::File;

fn write_products_to_csv(products: &[Product]) -> Result<(), Box<dyn std::error::Error>> {
    let mut wtr = Writer::from_path("products.csv")?;
    for product in products {
        wtr.serialize(product)?;
    }
    wtr.flush()?;
    Ok(())
}
```

## The New Shop System

Your shop is quite successful, and you decide to move to a different 
shop system, which requires the products to be loaded from XML files.

Since you already implemented the `Serialize` and `Deserialize` traits for
`Product`, you can swiftly use the `serde_xml_rs` crate to create the file.

```rust

fn write_products_to_xml(products: &[Product]) -> Result<(), Box<dyn std::error::Error>> {
    let xml = serde_xml_rs::so_string(products)?;
    std::fs::write("products.xml", xml)?;
    Ok(())
}
```

This took no time at all, since we already did the hard work of thinking about
the product structure and how to serialize and deserialize it before.

If in the future we need to support a different format or store the products in a
database, we can do so without changing the `Product` struct!

Here we used traits that another crate thankfully provided. Some popular crates
define their own traits, which we can implement for our types. This is very
powerful: It allows us to focus on the business logic while other crates take care of the
integration with the rest of the ecosystem.

**Composition is Separation of Concerns.**

## New Product Categories

You decide to expand your product range to include &mdash; of all things &mdash;
vegetables. (Well, I'm not here to judge.)

Your first thought is to extend the existing `Product` struct:

```rust
#[derive(Debug, Deserialize, Serialize)]
struct Product {
    id: Id,
    name: ProductName,
    price: Price,
    price_per_kg: Price, // New!
    weight: Weight,
    category: Category, // New! Category of the vegetable
    organic: bool, // New! Whether the vegetable is organic or not
}
```

where

```rust
#[derive(Debug, Deserialize, Serialize)]
enum Category {
    Leafy,
    Root,
    // Did you know that some vegetables are technically fruits?
    Fruit, 
    Stem,
    Flower,
}
```

Something feels off about this. The extra fields are only relevant for
vegetables. Worse, if you add more product types, you'll have to add even more fields.
(Have fun adding those Rust-themed T-shirt sizes!)

What would be the value of these extra fields for your candy products?
Of course, you could use an `Option` for each field, but that would make it even less
appealing.

It won't take long before you realize that the answer is right in front of you:
**Traits**.

## Traits to the Rescue

You can define a trait for the common fields of all products:

```rust
trait Product {
    fn id(&self) -> &Id;
    fn name(&self) -> &ProductName;
    fn price(&self) -> &Price;
    // Note: weight is not always relevant for all products (e.g., digital products)
}
```

Now both `Candy` and `Vegetable` can both implement `Product`:

```rust
#[derive(Debug, Deserialize, Serialize)]
struct Candy {
    id: Id,
    name: ProductName,
    price: Price,
    weight: Weight,
}

impl Product for Candy {
    fn id(&self) -> &Id {
        &self.id
    }

    fn name(&self) -> &ProductName {
        &self.name
    }

    fn price(&self) -> &Price {
        &self.price
    }
}

#[derive(Debug, Deserialize, Serialize)]
struct Vegetable {
    id: Id,
    name: ProductName,
    price: Price,
    price_per_kg: Price,
    weight: Weight,
    category: Category,
    organic: bool,
}

impl Product for Vegetable {
    fn id(&self) -> &Id {
        &self.id
    }

    fn name(&self) -> &ProductName {
        &self.name
    }

    fn price(&self) -> &Price {
        &self.price
    }
}
```

Now you can write functions that take *any* product:

```rust
fn log_product_view(product: &impl Product) {
    println!("Product viewed: {:?}", product);
}
```

This is syntactic sugar for a trait bound:

```rust
fn log_product_view<T: Product>(product: &T) {
    println!("Product viewed: {:?}", product);
}
```

However, this is not quite enough. We also need to guarantee that the
`product` implements `Debug`. We can do this by adding another trait bound:

```rust
fn log_product_view(product: &(impl Product + std::fmt::Debug)) {
    println!("Product viewed: {:?}", product);
}
```

Here, we require that `product` implements both `Product` and `Debug`.
This is a form of trait-based composition: both constraints must be satisfied.

As for our product catalog, we can now also be more specific and not only
require `Serialize`, but also `Product`:

```rust
fn write_products_to_csv(products: &[impl Product + Serialize]) -> Result<(), Box<dyn std::error::Error>> {
    let mut wtr = Writer::from_path("products.csv")?;
    for product in products {
        wtr.serialize(product)?;
    }
    wtr.flush()?;
    Ok(())
}
```

Neat! We introduced a notion of a `Product` and started to use that in our
system.
We could have done something similar with inheritance, but just imagine the
headache of adding more product types and the fields they would require. 
Especially when we start to introduce multiple inheritance for things like
`OrganicCandy`.
Inheritance is a rigid: idea: it can back your code into a corner.

## Summary

Composition unlocks new use cases

Traits are the building blocks of composable Rust code. They allow you to
describe *behaviors*. 

* Inheritance describes what something *is*.
* Composition describes what something *does*.

* Inheritance: mountain bike is a special bike. "Is a mountain bike"
* Composition: A bike is composed from different parts. Like Lego bricks.
  The sum of tiny blocks. "Has many mountain bike parts"

It's a change of mindset. Different way of thinking

fighting the concept of composition. doesn't feel natural
(could be a good intro line)

Resist the urge to side-step the type system. Try to understand the constraints
the compiler is enforcing. This will lead to better designs.

## Further reading

* [Rust Book: Traits](https://doc.rust-lang.org/book/ch10-02-traits.html)
* [Rust Book: Using Trait Objects That Allow for Values of Different Types](https://doc.rust-lang.org/book/ch17-02-trait-objects.html#using-trait-objects-that-allow-for-values-of-different-types)
* [Possible Rust: 3 Things to Try When You Can't Make a Trait Object](https://www.possiblerust.com/pattern/3-things-to-try-when-you-can-t-make-a-trait-object)


## Code

Here is the entire, documented code (without any skipped parts)
for the full shop system we built in this article.
It is idiomatic and will just work when you paste it into a Rust file
or the Rust Playground:

```rust
use serde::{Deserialize, Serialize};
use csv::Writer;

#[derive(Debug)]
enum Error {
    EmptyName,
    InvalidPrice,
    InvalidWeight,
}

impl std::error::Error for Error {
    fn description(&self) -> &str {
        match self {
            Error::EmptyName => "Name must not be empty",
            Error::InvalidPrice => "Price must be greater than zero",
        }
    }
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.description())
    }
}

/// A unique identifier for a product.
#[derive(Debug, Deserialize, Serialize)]
struct Id {
    // The actual type is an implementation detail
    id: uuid::Uuid,
}

impl Id {
    fn new() -> Self {
        Self {
            id: uuid::Uuid::new_v4(),
        }
    }
}

/// The name of a product.
#[derive(Debug, Deserialize, Serialize)]
struct ProductName {
    // This will be validated to be non-empty etc.
    name: String,
}

impl ProductName {
    fn new(name: String) -> Result<Self, Error> {
        if name.is_empty() {
            return Err(Error::EmptyName);
        }
        Ok(Self { name })
    }
}

/// The price of a product.
#[derive(Debug, Deserialize, Serialize)]
struct Price {
    amount: usize, // in cents
    currency: Currency, // e.g., USD, EUR, GBP
}

impl Price {
    fn new(amount: usize, currency: Currency) -> Result<Self, Error> { 
        // Price can not be negative or zero
        if amount <= 0 {
            return Err(Error::InvalidPrice);
        }
        Ok(Self { amount, currency })
    }
}

/// The weight of a product.
#[derive(Debug, Deserialize, Serialize)]
struct Weight {
    amount: usize, // in grams
    unit: WeightUnit, // e.g., g, kg, oz, lb
}

impl Weight {
    fn new(amount: usize, unit: WeightUnit) -> Result<Self, Error> {
        // Weight can not be negative or zero
        if amount <= 0 {
            return Err(Error::InvalidWeight);
        }
        Ok(Self { amount, unit })
    }
}

/// The currency of a price.
#[derive(Debug, Deserialize, Serialize)]
enum Currency {
    USD,
    EUR,
    GBP,
}

/// The unit of a weight.
#[derive(Debug, Deserialize, Serialize)]
enum WeightUnit {
    Gram,
    Kilogram,
    Ounce,
    Pound,
}

/// A candy
#[derive(Debug, Deserialize, Serialize)]
struct Candy {
    id: Id,
    name: ProductName,
    price: Price,
    weight: Weight,
}

impl Candy {
    fn new(
        name: ProductName,
        price: Price,
        weight: Weight,

    ) -> Result<Self, Error> {
        Ok(Self {
            id: Id::new(),
            name,
            price,
            weight,
        })
    }
}

/// A vegetable product category.
#[derive(Debug, Deserialize, Serialize)]
enum Category {
    Leafy,
    Root,
    Fruit,
    Stem,
    Flower,
}

/// A vegetable product.
#[derive(Debug, Deserialize, Serialize)]
struct Vegetable {
    id: Id,
    name: ProductName,
    price: Price,
    price_per_kg: Price,
    weight: Weight,
    category: Category,
    organic: bool,
}

impl Vegetable {
    fn new(
        name: ProductName,
        price: Price,
        price_per_kg: Price,
        weight: Weight,
        category: Category,
        organic: bool,
    ) -> Result<Self, Error> {
        Ok(Self {
            id: Id::new(),
            name,
            price,
            price_per_kg,
            weight,
            category,
            organic,
        })
    }
}

/// A product.
trait Product {
    fn id(&self) -> &Id;
    fn name(&self) -> &ProductName;
    fn price(&self) -> &Price;
}

impl Product for Candy {
    fn id(&self) -> &Id {
        &self.id
    }

    fn name(&self) -> &ProductName {
        &self.name
    }

    fn price(&self) -> &Price {
        &self.price
    }
}

impl Product for Vegetable {
    fn id(&self) -> &Id {
        &self.id
    }

    fn name(&self) -> &ProductName {
        &self.name
    }

    fn price(&self) -> &Price {
        &self.price
    }
}

fn log_product_view(product: &impl Product) {
    println!("Product viewed: {:?}", product);
}

fn log_event(event: impl std::fmt::Debug) {
    println!("New Event: {:?}", event);
}

fn write_products_to_csv(products: &[impl Product + Serialize]) -> Result<(), Box<dyn std::error::Error>> {
    let mut wtr = Writer::from_path("products.csv")?;
    for product in products {
        wtr.serialize(product)?;
    }
    wtr.flush()?;
    Ok(())
}

fn write_products_to_xml(products: &[impl Product + Serialize]) -> Result<(), Box<dyn std::error::Error>> {
    let xml = serde_xml_rs::so_string(products)?;
    std::fs::write("products.xml", xml)?;
    Ok(())
}

fn main() {
    let candy = Candy::new(
        ProductName::new("Ferris' Fudgy Feast".to_string()).unwrap(),
        Price::new(100, Currency::USD).unwrap(),
        Weight::new(100, WeightUnit::Gram).unwrap(),
    ).unwrap();

    let vegetable = Vegetable::new(
        ProductName::new("Rusty Radish".to_string()).unwrap(),
        Price::new(50, Currency::USD).unwrap(),
        Price::new(10, Currency::USD).unwrap(),
        Weight::new(200, WeightUnit::Gram).unwrap(),
        Category::Root,
        true,
    ).unwrap();

    log_product_view(&candy);
    log_product_view(&vegetable);

    log_event(candy);
    log_event(vegetable);

    write_products_to_csv(&[candy, vegetable]).unwrap();
    write_products_to_xml(&[candy, vegetable]).unwrap();
}
```






