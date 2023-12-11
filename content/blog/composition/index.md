+++
title = "Composition over Inheritance"
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

## The Case for Composition

Imagine you're the owner of Crustacean Candy, an online store offering
Rust-themed candy bars and other treats. Customers love your delights
ranging from "Ferris' Fudgy Feast" to "Rusty ICE-cream."

#### Converting CSV to JSON

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
    let mut reader = csv::Reader::from_path("products.csv")?;
    let candies: Vec<Candy> = reader.deserialize().filter_map(Result::ok).collect();

    // Convert to JSON
    let json = serde_json::to_string(&candies)?;

    // Write to file
    fs::write("products.json", json)?;

    Ok(())
}
```

This code works just fine. Soon you're happily serving customers from your brand
new online store.

#### Adding XML Support

After a while, you get a call from a retail chain that wants to sell your
products in their stores. That's good news! The only problem is that
their system needs your product catalog as XML.

"No problemo!", you say, "you'll get the file faster than you can say 'Cargo
Cotton Candy!'."

```rust
/// New! An XML wrapper struct to define the root tag
/// This is required by the XML serializer
#[derive(Debug, Serialize, Deserialize)]
struct Candies {
    #[serde(rename = "candy")]
    candies: Vec<Candy>,
}

fn main() -> Result<()> {
    // Take the output file as a command line argument
    let output_file = std::env::args().nth(1).expect("missing output file");

    // Like before, read the CSV file and filter out the invalid rows
    let mut rdr = csv::Reader::from_path("products.csv")?;
    let candies: Vec<Candy> = rdr.deserialize().filter_map(Result::ok).collect();

    if output_file.ends_with(".json") {
        let json = serde_json::to_string(&candies)?;
        fs::write(output_file, json)?;
    } else if output_file.ends_with(".xml") {
        // Wrap the vector in a struct to define the root tag
        let wrapper = Candies { candies };
        let xml = quick_xml::se::to_string(&wrapper)?;
        fs::write(output_file, xml)?;
    } else {
        // Other file types are currently not supported
        unimplemented!("unknown output file type")
    }

    Ok(())
}
```

Hold on, this is getting kind of messy.
Hastily, you refactor the code a bit to improve readability.

```rust
fn main() -> Result<()> {
    let output_file = std::env::args().nth(1).expect("missing output file");
    let mut rdr = csv::Reader::from_path("products.csv")?;
    let candies: Vec<Candy> = rdr.deserialize().filter_map(Result::ok).collect();

    if output_file.ends_with(".json") {
        write_json(output_file, &candies)?;
    } else if output_file.ends_with(".xml") {
        write_xml(output_file, &candies)?;
    } else {
        unimplemented!("unknown output file type")
    }

    Ok(())
}
```

And in fact, you go one step further and extract the file type from the
output file name.

```rust
fn main() -> Result<()> {
    let output_file = std::env::args().nth(1).expect("missing output file");
    let mut rdr = csv::Reader::from_path("products.csv")?;
    let candies: Vec<Candy> = rdr.deserialize().filter_map(Result::ok).collect();

    match output_file.split('.').last() {
        Some("json") => write_json(output_file, &candies)?,
        Some("xml") => write_xml(output_file, &candies)?,
        _ => unimplemented!("unknown output file type"),
    }

    Ok(())
}
```

You commit the code and move on, but you can't shake the feeling that something
is off. You've heard that Rust is a language that favors composition over
inheritance, but the code looks eerily imperative.

#### Writing the Output to the Console

While you wait for a delivery of "Rustic Raspberry Rock Candy" to arrive, you
decide to add a feature to your program that prints the output to the console.

```rust
fn main() -> Result<()> {
    let format = std::env::args().nth(1).expect("missing format");
    let output_file = std::env::args().nth(2).expect("missing output file");

    let mut rdr = csv::Reader::from_path("products.csv")?;
    let candies: Vec<Candy> = rdr.deserialize().filter_map(Result::ok).collect();

    // If the output file is "-" write to stdout
    let mut writer: Box<dyn Write> = if output_file == "-" {
        Box::new(std::io::stdout())
    } else {
        Box::new(fs::File::create(&output_file)?)
    };

    match format.as_str() {
        "json" => write_json(&mut writer, candies)?,
        "xml" => write_xml(&mut writer, candies)?,
        _ => unimplemented!("unknown output file type"),
    }

    Ok(())
}
```

Note the  `Box<dyn Write>` that abstracts over the output. This allows to write
to a file or to stdout depending on the value of `output_file`. The `format`
variable holds the output format (JSON or XML).

The two functions, `write_json` and `write_xml`, are defined as follows:

```rs
fn write_json<W: Write>(writer: &mut W, candies: Vec<Candy>) -> Result<()> {
    let json = serde_json::to_string(&candies)?;
    writer.write_all(json.as_bytes())?;
    Ok(())
}

fn write_xml<W: Write>(writer: &mut W, candies: Vec<Candy>) -> Result<()> {
    let products = Candies { candies };
    let xml = quick_xml::se::to_string(&products)?;
    writer.write_all(xml.as_bytes())?;
    Ok(())
}
```

This allows to reuse the same code for writing to a file or to stdout.
Here are some examples of how to use the program:

```sh
# Store the output as JSON in a file
cargo run -- json products.json

# Write the output as XML to stdout
cargo run -- xml -
```

#### New Input Formats

Working on your little converter makes you happy. 
Just for fun, you open source the code and soon you get a pull request from a user who
adds support for writing YAML files and another one for reading from JSON.

```rust
fn main() -> Result<()> {
    let input_file = std::env::args().nth(1).expect("missing input file");
    let format = std::env::args().nth(2).expect("missing format");
    let output_file = std::env::args().nth(3).expect("missing output file");

    // Read the input file
    let candies = match input_file.split('.').last() {
        Some("csv") => read_csv(&input_file)?,
        Some("json") => read_json(&input_file)?,
        _ => unimplemented!("unknown input file type"),
    };

    let mut writer: Box<dyn Write> = if output_file == "-" {
        Box::new(std::io::stdout())
    } else {
        Box::new(fs::File::create(&output_file)?)
    };

    match format.as_str() {
        "json" => write_json(&mut writer, candies)?,
        "xml" => write_xml(&mut writer, candies)?,
        "yaml" => write_yaml(&mut writer, candies)?,
        _ => unimplemented!("unknown output file type"),
    }

    Ok(())
}
```

Here's how to read from CSV, convert to YAML, and write to `stdout`:

```sh
cargo run products.csv yaml -
```

#### Taking a step back

Undoubtedly, our little program has grown quite a bit. 
There are a few problems with it:

* It's hard to test. The functions are tightly coupled to the file system.
* It's hard to extend. Adding support for new input or output formats requires
  changing the `main` function.
* The code still feels very imperative.
* The code is not very reusable. For example, we can't use the `read_csv`
  function in other programs.

While your shop is humming along nicely, you decide to take a step back and
refactor the code. What is the best way to do that?

You soon realize that the problem is that the code is not very composable.

That is, the code is not made up of small, reusable components that can be
combined to create larger systems.

There are a few ways to make the code more composable, but you decide to
write the code again from bottom up.

Essentially, there are a few responsibilities that need to be handled:

- Reading from a file or stdin
- Parsing the input to a vector of `Candy` structs
- Converting to the desired output format
- Writing to a file or stdout

So the chain of responsibility looks like this:

```
Read -> Parse -> Convert -> Write
```

Let's start with the `Read` part.

#### Reading from a file or stdin

Reading the input is already covered by Rust's standard library through the
`Read` trait:

```rust
use std::io::{self, Read};

fn read<R: Read>(reader: &mut R) -> Result<String, io::Error> {
    let mut buffer = String::new();
    reader.read_to_string(&mut buffer)?;
    Ok(buffer)
}
```

We can use this function to read from a file or stdin:

```rust
fn main() -> Result<()> {
    let input_file = std::env::args().nth(1).expect("missing input file");

    let mut reader: Box<dyn Read> = if input_file == "-" {
        Box::new(std::io::stdin())
    } else {
        Box::new(fs::File::open(&input_file)?)
    };

    let input = read(&mut reader)?;
    // Use the input here...

    Ok(())
}
```

However, we could also introduce an `Input` struct
that abstracts over the input source:

```rust
fn main() -> Result<()> {
    let input_file = std::env::args().nth(1).expect("missing input file");
    let input = Input::new(&input_file);
    // ...

    Ok(())
}
```

In order to achieve this, we need to implement the `Read` trait for `Input`:

```rust
use std::io::{self, Read};

struct Input {
    /// We only gurantee that the source implements the `Read` trait,
    /// e.g. that it can be read from.
    source: Box<dyn Read>,
}

impl Input {
    fn new(source: &str) -> Result<Self> {
        let source: Box<dyn Read> = match source {
            "-" => Box::new(std::io::stdin()),
            _ => Box::new(fs::File::open(source)?),
        };

        Ok(Self { source })
    }
}

/// Implement the `Read` trait for `Input`
impl Read for Input {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
        self.source.read(buf)
    }
}
```

Our readers now take the generic `Read` type and look like this:

```rust
fn read_csv<R: Read>(reader: R) -> Result<Vec<Candy>> {
    let mut candies = Vec::new();
    let mut reader = csv::Reader::from_reader(reader);
    for result in reader.deserialize() {
        let candy: Candy = result?;
        candies.push(candy);
    }
    Ok(candies)
}

fn read_json<R: Read>(reader: R) -> Result<Vec<Candy>> {
    let candies: Vec<Candy> = serde_json::from_reader(reader)?;
    Ok(candies)
}
```

In fact, they are parsers that take a `Read` type and return a `Vec<Candy>`.
We should treat them as such.
The contraint that they return a `Vec<Candy>` is unnecessary.
We can change the return type to an iterator:

```rust
struct XmlParser<R: Read> {
    reader: R,
}

impl<R: Read> XmlParser<R> {
    fn new(reader: R) -> Self {
        Self { reader }
    }
}

impl<R: Read> Iterator for XmlParser<R> {
    type Item = Result<Candy>;

    fn next(&mut self) -> Option<Self::Item> {
        // Parse the next item
        // ...
    }
}
```




