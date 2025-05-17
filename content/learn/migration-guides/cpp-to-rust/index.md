+++
title = "C++ to Rust Cheat-Sheet"
date = 2025-05-17
template = "article.html"
draft = false
[extra]
wide = true
series = "Migration Guides"
icon = "cpp.svg"
resources = [
    "[Rust Vs C++ Beyond Safety - Joseph Cordell - ACCU Cambridge](https://www.youtube.com/watch?v=IvPP5U2wzlE)",
    "[C++ vs Rust Cheat Sheet by MaulingMonkey](https://maulingmonkey.com/guide/cpp-vs-rust/)",
]
+++

Some people learn new programming languages best by looking at examples for how to do the same thing they know in one language is done in the other. 
Below is a syntax comparison table which can serve as a quick reference for common C++ constructs and their equivalents in Rust.
It is not a comprehensive guide, but I hope it helps out a C++ developer looking for a quick reference to Rust syntax. 

## Comparing Idioms in Rust and C++ 

<table>
  <thead>
    <tr>
      <th>Feature</th>
      <th>Rust</th>
      <th>C++</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Variable Declaration</strong></td>
      <td><code>let x: i32 = 5;</code></td>
      <td><code>int x = 5;</code></td>
    </tr>
    <tr>
      <td><strong>Type Inference</strong></td>
      <td><code>let x = 5;</code></td>
      <td><code>auto x = 5;</code></td>
    </tr>
    <tr>
      <td><strong>Mutable Variables</strong></td>
      <td><code>let mut x = 5;</code></td>
      <td><code>int x = 5;</code> (mutable by default)</td>
    </tr>
    <tr>
      <td><strong>Constant Declaration</strong></td>
      <td><code>const MAX: i32 = 100;</code></td>
      <td><code>const int MAX = 100;</code></td>
    </tr>
    <tr>
      <td><strong>Function Declaration</strong></td>
      <td><pre><code class="language-rust">fn add(first: i32, second: i32) -> i32 {
    first + second
}</code></pre></td>
      <td><pre><code class="language-rust">int add(int first, int second) {
    return first + second;
}</code></pre></td>
    </tr>
    <tr>
      <td><strong>Implicit Return</strong></td>
      <td><pre><code class="language-rust">fn add(a: i32, b: i32) -> i32 { a + b }</code></pre></td>
      <td><pre><code class="language-rust">auto add(int a, int b) -> int { return a + b; }</code></pre></td>
    </tr>
    <tr>
      <td><strong>Immutable Reference</strong></td>
      <td><code>&T</code></td>
      <td><code>const T&</code></td>
    </tr>
    <tr>
      <td><strong>Mutable Reference</strong></td>
      <td><code>&mut T</code></td>
      <td><code>T&</code></td>
    </tr>
    <tr>
      <td><strong>Raw Pointer</strong></td>
      <td><code>*const T</code>, <code>*mut T</code></td>
      <td><code>T*</code>, <code>const T*</code></td>
    </tr>
    <tr>
      <td><strong>Struct Declaration</strong></td>
      <td>
        <pre><code class="language-rust">struct Person {
    id: u32,
    health: i32
}</code></pre>
      </td>
      <td>
        <pre><code class="language-cpp">struct Person {
    unsigned int id;
    int health;
};</code></pre>
      </td>
    </tr>
    <tr>
      <td><strong>Struct Initialization</strong></td>
      <td><code>Person { id: uid, health: 100 }</code></td>
      <td><code>Person{uid, 100}</code> or <code>Person{.id = uid, .health = 100}</code></td>
    </tr>
    <tr>
      <td><strong>Struct Field Access</strong></td>
      <td><code>person.id</code></td>
      <td><code>person.id</code></td>
    </tr>
    <tr>
      <td><strong>Class/Method Implementation</strong></td>
      <td>
        <pre><code class="language-rust">impl MyClass {
    fn new(name: &String, data: &Vec<String>) -> Self {
        // ...
    }
}</code></pre>
      </td>
      <td>
        <pre><code class="language-cpp">class MyClass {
public:
    MyClass(const string& name, 
            const vector<string>& data) {
        // ...
    }
};</code></pre>
      </td>
    </tr>
    <tr>
      <td><strong>Method with Self</strong></td>
      <td>
        <pre><code class="language-rust">fn get_name(&self) -> String {
    self.name.clone()
}</code></pre>
      </td>
      <td>
        <pre><code class="language-cpp">string get_name() const {
    return name;
}</code></pre>
      </td>
    </tr>
    <tr>
      <td><strong>Static Method</strong></td>
      <td><code>fn static_method() { /* ... */ }</code></td>
      <td><code>static void static_method() { /* ... */ }</code></td>
    </tr>
    <tr>
      <td><strong>Interface/Trait</strong></td>
      <td>
        <pre><code class="language-rust">trait Shape {
    fn get_area(&self) -> f64;
}</code></pre>
      </td>
      <td>
        <pre><code class="language-cpp">class Shape {
public:
    virtual double get_area() const = 0;
};</code></pre>
      </td>
    </tr>
    <tr>
      <td><strong>Implementing Interface</strong></td>
      <td>
        <pre><code class="language-rust">impl Shape for Circle {
    fn get_area(&self) -> f64 {
        // ...
    }
}</code></pre>
      </td>
      <td>
        <pre><code class="language-cpp">class Circle : public Shape {
public:
    double get_area() const override {
        // ...
    }
};</code></pre>
      </td>
    </tr>
    <tr>
      <td><strong>Generic Function</strong></td>
      <td>
        <pre><code class="language-rust">fn generic_call<T: Shape>(gen_shape: &T) {
    // ...
}</code></pre>
      </td>
      <td>
        <pre><code class="language-cpp">template<typename T>
void generic_call(const T& gen_shape) {
    // ...
}</code></pre>
      </td>
    </tr>
    <tr>
      <td><strong>Associated Types</strong></td>
      <td>
        <pre><code class="language-rust">trait Shape {
    type InnerType;
    fn make_inner(&self) -> Self::InnerType;
}</code></pre>
      </td>
      <td>
        <pre><code class="language-cpp">template<typename T>
concept Shape = requires(T t) {
    typename T::InnerType;
    { t.make_inner() } -> 
        std::convertible_to<typename T::InnerType>;
};</code></pre>
      </td>
    </tr>
    <tr>
      <td><strong>Enums (Tagged Union)</strong></td>
      <td>
        <pre><code class="language-rust">enum MyShape {
    Circle(f64),
    Rectangle(f64, f64)
}</code></pre>
      </td>
      <td>
        <pre><code class="language-cpp">std::variant<Circle, Rectangle> my_shape;</code></pre>
      </td>
    </tr>
    <tr>
      <td><strong>Pattern Matching</strong></td>
      <td>
        <pre><code class="language-rust">match shape {
    MyShape::Circle(r) => // ...,
    MyShape::Rectangle(w, h) => // ...
}</code></pre>
      </td>
      <td>
        <pre><code class="language-cpp">std::visit(overloaded {
    [](const Circle& c) { /* ... */ },
    [](const Rectangle& r) { /* ... */ }
}, my_shape);</code></pre>
      </td>
    </tr>
    <tr>
      <td><strong>Optional Types</strong></td>
      <td><code>Option&lt;T&gt;</code> (Some(T) or None)</td>
      <td><code>std::optional&lt;T&gt;</code></td>
    </tr>
    <tr>
      <td><strong>Error Handling</strong></td>
      <td><code>Result&lt;T, E&gt;</code> (Ok(T) or Err(E))</td>
      <td><code>std::expected&lt;T, E&gt;</code> (C++23)</td>
    </tr>
    <tr>
      <td><strong>Error Propagation</strong></td>
      <td><code>let file = File::open("file.txt")?;</code></td>
      <td>No direct equivalent; uses exceptions or return codes</td>
    </tr>
    <tr>
      <td><strong>Automatic Trait Implementation</strong></td>
      <td><code>#[derive(Debug, Clone, PartialEq)]</code></td>
      <td>No direct equivalent</td>
    </tr>
    <tr>
      <td><strong>Memory Allocation</strong></td>
      <td>Explicit: <code>String::from("text")</code>, <code>.to_owned()</code>, <code>.clone()</code></td>
      <td>Often implicit when passing by value</td>
    </tr>
    <tr>
      <td><strong>Destructors</strong></td>
      <td>
        <pre><code class="language-rust">impl Drop for MyType {
    fn drop(&mut self) {
        // cleanup
    }
}</code></pre>
      </td>
      <td>
        <pre><code class="language-cpp">~MyType() {
    // cleanup
}</code></pre>
      </td>
    </tr>
    <tr>
      <td><strong>Serialization</strong></td>
      <td><code>#[derive(Serialize, Deserialize)]</code></td>
      <td>Requires manual implementation or code generation</td>
    </tr>
    <tr>
      <td><strong>Print to Console</strong></td>
      <td><code>println!("Hello, {}", name);</code></td>
      <td><code>std::cout << "Hello, " << name << std::endl;</code></td>
    </tr>
    <tr>
      <td><strong>Debug Output</strong></td>
      <td><code>println!("{:?}", object);</code></td>
      <td>No direct equivalent; requires custom implementation</td>
    </tr>
    <tr>
      <td><strong>Pretty Debug Output</strong></td>
      <td><code>println!("{:#?}", object);</code></td>
      <td>No direct equivalent</td>
    </tr>
  </tbody>
</table>