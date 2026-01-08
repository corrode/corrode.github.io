+++
title = "Radar"
date = 2026-01-08
template = "episode.html"
draft = false
aliases = ["/p/s05e08"]
[extra]
guest = "Jeff Kao"
role = "Staff Engineer"
season = "05"
episode = "08"
series = "Podcast"
+++

<div><script id="letscast-player-7e84c99d" src="https://letscast.fm/podcasts/rust-in-production-82281512/episodes/radar-with-jeff-kao/player.js?size=s"></script></div>

Radar processes billions of location events daily, powering geofencing and location APIs for companies like Uber, Lyft, and thousands of other apps.
When their existing infrastructure started hitting performance and cost limits, they built HorizonDB, a specialized database which replaced both Elasticsearch and MongoDB with a custom single binary written in Rust and backed by RocksDB.

In this episode, we dive deep into the technical journey from prototype to production. We talk about RocksDB internals, finite-state transducers, the intricacies of geospatial indexing with Hilbert curves, and why Rust's type system and performance characteristics made it the perfect choice for rewriting critical infrastructure that processes location data at massive scale.

{{ codecrafters() }}

## Show Notes

### About Radar

Radar is the leading geofencing and location platform, trusted by companies like Uber, Lyft, and thousands of apps to power location-based experiences. Processing billions of location events daily, Radar provides geofencing APIs, geocoding, and location tracking that enables developers to build powerful location-aware applications. Their infrastructure handles massive scale with a focus on accuracy, performance, and reliability.

### About Jeff Kao

Jeff Kao is a Staff Engineer at Radar, where he led the development of HorizonDB, Radar's geospatial database written in Rust. His work replaced Elasticsearch and MongoDB with a custom Rust stack built on RocksDB, achieving dramatic improvements in performance and cost efficiency. Jeff has deep experience with geospatial systems and previously open-sourced Node.js TypeScript bindings for Google's S2 library. He holds a degree from the University of Waterloo.

### Links From The Episode

- [Radar Blog: High-Performance Geocoding in Rust](https://radar.com/blog/high-performance-geocoding-in-rust) - The blog post, which describes Radar's migration from Elasticsearch and MongoDB to Rust and RocksDB
- [FourSquare](https://foursquare.com/) - The compay Jeff worked at before
- [Ruby](https://www.ruby-lang.org/) - The basis for Rails
- [PagerDuty)](https://www.pagerduty.com/) - Another company Jeff worked at. Hes' been around!
- [CoffeeScript](https://coffeescript.org/) - The first big JavaScript alternative before TypeScript
- [Scala](https://www.scala-lang.org/) - A functional JVM based language
- [Wikipedia: MapReduce](https://en.wikipedia.org/wiki/MapReduce) - Distributed application of functional programming
- [Wikipedia: Algebraic Data Types](https://en.wikipedia.org/wiki/Algebraic_data_type) - The concept behind Rust's Enums, also present in e.g. Scala
- [Kotlin](https://kotlinlang.org/) - Easier than Scala, better than Java
- [Apache Lucene](https://lucene.apache.org/) - The core of ElasticSearch
- [Discord Blog: Why Discord is switching from Go to Rust](https://discord.com/blog/why-discord-is-switching-from-go-to-rust) - Always the #1 result in searches for Rust migrations
- [Radar Blog: Introducing HorizonDB](https://radar.com/blog/introducing-horizondb) - A really nice write up of Horizon's architecture
- [RocksDB](https://rocksdb.org/) - The primary storage layer used in HorizonDB
- [MyRocks](https://github.com/facebook/mysql-5.6) - A MySQL Storage Engine using RocksDB, written by Facebook
- [MongoRocks](https://github.com/mongodb-partners/mongo-rocks) - A MongoDB Storage Layer using RocksDB
- [CockroachDB](https://www.cockroachlabs.com/) - PostgreSQL compatible, distributed, SQL Database
- [InfluxDB](https://www.influxdata.com/) - A timeseries database that used RocksDB at one point, and our very first guest in this Podcast!
- [sled](https://github.com/spacejam/sled) - An embedded database written in Rust
- [rocksdb](https://github.com/rust-rocksdb/rust-rocksdb) - Rust bindings for RocksDB
- [H3](https://h3geo.org/) - Uber's Geo Hashing using hexagons
- [S2](https://s2geometry.io/) - Google's Geo Hashing library
- [Wikipedia: Hilbert Curve](https://en.wikipedia.org/wiki/Hilbert_curve) - A way to map 2 dimensions onto 1 while retaining proximity
- [Wikipedia: Finite-State Transducer](https://en.wikipedia.org/wiki/Finite-state_transducer) - A state machine used for efficiently looking up if a word exists in the data set
- [Rust in Production: Astral](/podcast/s04e03-astral/) - Our episode with Charlie Marsh about tooling for the Python ecosystem
- [burntsushi](https://github.com/BurntSushi) - A very prolific Rust developer, now working at Astral
- [fst](https://github.com/BurntSushi/fst) - FST crate from burntsushi
- [Wikipedia: Trie](https://en.wikipedia.org/wiki/Trie) - A tree-structure using common prefixes
- [Wikipedia: Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance) - The number of letters you have to change, add, or remove to turn word a into word b
- [tantivy](https://github.com/quickwit-oss/tantivy) - A full-text search engine, written in Rust, inspired by Lucene
- [LightGBM](https://github.com/microsoft/LightGBM) - A gradient boosted tree, similar to a decision tree
- [fastText](https://fasttext.cc/) - A text classification library from Meta
- [Wikipedia: Inverted Index](https://en.wikipedia.org/wiki/Inverted_index) - An index used for e.g. full text search
- [Wikipedia: Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25) - The ranking algorithm used in tantivy
- [Wikipedia: tf-idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) - A classic and simple ranking algorithm
- [Roaring Bitmaps](https://github.com/RoaringBitmap/roaring-rs) - A very fast bitset library used in many places
- [corrode.dev: Be Simple](https://corrode.dev/blog/be-simple/) - A sentiment right down Matthias' alley
- [loco-rs](https://loco.rs/) - Rust on Rails

### Official Links

- [Radar](https://radar.com/)
- [Radar Blog](https://radar.com/blog)
- [Radar Documentation](https://radar.com/documentation)
- [Jeff Kao on LinkedIn](https://www.linkedin.com/in/jeff-kao/)
