+++
title = "Learning Material for Idiomatic Rust"
date = 2024-01-28
updated = 2026-01-01
draft = false
template = "article.html"
aliases = ["idiomatic-rust"]
[extra]
wide = true
series = "Idiomatic Rust"
excerpt = "A curated list of resources to help you write ergonomic and idiomatic Rust code. Includes tutorials, workshops, and articles by Rust experts."
+++

Here's a curated list of resources to **help you write ergonomic and idiomatic Rust code**.

The list is open source and [maintained on GitHub](https://github.com/mre/idiomatic-rust), and contributions are always welcome!

Discover a wealth of tutorials, workshops, and articles created by Rust experts, all aimed at helping you become a better Rust programmer. Each resource is peer-reviewed to ensure adherence to Rust best practices. Plus, you can easily filter, sort, and search by tags, year, and difficulty level to find exactly what you need.

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
<script src="dataTables.checkboxes.min.js"></script>
<script src="table.js"></script>

<div style="margin-bottom: 20px">
    <button class="button reset-filter">Reset filters</button>
</div>

<div>
    Extra columns: 
    <a class="toggle-vis" data-column="6">Official</a> - 
    <a class="toggle-vis" data-column="7">Year</a> - 
    <a class="toggle-vis" data-column="9">Duration</a> - 
    <a class="toggle-vis" data-column="11">Free/Commercial</a>
</div>

<div>
  Click on the triangle <span style="font-family: Arial, sans-serif">▶</span> to show more details for
  each entry.
</div>

<table id="data-table" class="compact order-column hover stripe" style="width:100%">
</table>

<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css" />

<link rel="stylesheet" href="styles.css">
