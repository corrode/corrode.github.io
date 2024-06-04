+++
title = "Learning Material for Idiomatic Rust"
date = 2024-01-28
draft = false
template = "article.html"
aliases = ["idiomatic-rust"]
[extra]
wide = true
updated = 2024-05-15
series = "Idiomatic Rust"
excerpt = "A curated list of resources to help you write ergonomic and idiomatic Rust code. Includes tutorials, workshops, and articles by Rust experts."
+++

Here's a curated list of resources to **help you write ergonomic and idiomatic Rust code**.

The list is open source and [maintained on GitHub](https://github.com/mre/idiomatic-rust), and contributions are always welcome!

Discover a wealth of tutorials, workshops, and articles created by Rust experts, all aimed at helping you become a better Rust programmer. Each resource is peer-reviewed to ensure adherence to Rust best practices. Plus, you can easily filter, sort, and search by tags, year, and difficulty level to find exactly what you need.

<script src="//ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script src="//cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
<script src="dataTables.checkboxes.min.js"></script>
<script src="table.js"></script>

<div style="margin-bottom: 20px">
    <button class="reset-filter">Reset filters</button>
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

<link rel="stylesheet" type="text/css" href="//cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css" />

<style>
.dataTables_wrapper .dataTables_filter {
    margin: 20px 0 40px;
}

.dataTables_filter input[type="search"] {
    font-size: 18px;
    margin: 0 0 0 10px;
    padding: 8px;
    width: 350px;
    color: #111;
    border: 1px solid #111;
    background: rgb(255, 255, 255, 0.2);
}

.dataTables_wrapper code {
    cursor: pointer;
}

code {
    border-radius: 4px;
    padding: 5px;
    margin: 5px;
    font-size: 14px;
    font-family: monospace;
    color: #111;
    cursor: pointer;
}

code.active {
    color: white;
    background-color: #111;
}

.reset-filter {
    padding: 10px;
    display: none;
    margin-bottom: 20px;
    color: white;
    background-color: #111;
    border: none;
}

.toggle-vis {
    cursor: pointer;
}

.toggle-vis.active {
    font-weight: bold;
}

.dt-control {
    font-family: Arial, sans-serif;
}

table.dataTable td.dt-control::before {
  color: #111;
}

/* If prefers color scheme is bright, change background color of code tags and filter input */
@media (prefers-color-scheme: dark) {

    .reset-filter {
        background-color: #ee3856;
    }

    /* border white with 20% opacity */
    .dataTables_filter input[type="search"] {
        border: 1px solid rgb(255, 255, 255, 0.6);
    }

    table.dataTable td.dt-control::before {
      color: white;
    }

    .difficultyLevel {
      color: transparent;  
      text-shadow: 0 0 0 #ee3856;
    }
}

table.dataTable.dt-checkboxes-select tbody tr,
table.dataTable thead th.dt-checkboxes-select-all,
table.dataTable tbody td.dt-checkboxes-cell {
  cursor: pointer;
}

table.dataTable thead th.dt-checkboxes-select-all,
table.dataTable tbody td.dt-checkboxes-cell {
  text-align: center;
}

div.dataTables_wrapper span.select-info,
div.dataTables_wrapper span.select-item {
  margin-left: 0.5em;
}

@media screen and (max-width: 640px) {
  div.dataTables_wrapper span.select-info,
  div.dataTables_wrapper span.select-item {
    margin-left: 0;
    display: block;
  }
}

</style>
