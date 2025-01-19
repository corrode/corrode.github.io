+++
title = "Migrating from Python to Rust"
date = 2024-12-13
updated = 2024-01-19
template = "article.html"
draft = false
[extra]
series = "Guides"
+++

<div class="quiz-container">
  <div class="quiz-progress-container">
    <div class="progress-bar" id="progress-bar" style="width: 0%"></div>
  </div>
  <div id="quiz-question-container"></div>

  <div id="quiz-navigation-container">
    <button class="quiz-navbutton" id="quiz-prev-question" style="display: none">
      Previous
    </button>
    <button class="quiz-navbutton" id="quiz-next-question">Next</button>
  </div>
</div>

<script>
const languageOptions = [
  "Python",
  "Java",
  "C++",
  "Go",
  "TypeScript",
  "JavaScript",
  "C#",
  "Ruby",
  "PHP",
  "Swift",
  "Kotlin",
  "Other"
];

const questions = [
  {
    type: "multipleChoice",
    question: "Which languages are currently used in your codebase?",
    id: "currentLanguages",
    options: languageOptions,
  },
  {
    type: "multipleChoice",
    question: "Which types of applications are you looking to migrate?",
    id: "applicationType",
    direction: "column",
    options: [
      "Web services/APIs",
      "CLI tools",
      "Embedded systems",
      "Desktop applications",
      "WebAssembly modules",
      "Data processing pipelines",
      "Machine learning systems",
      "Other"
    ],
  },
  {
    type: "radio",
    question: "What's the size of your codebase?",
    id: "codebaseSize",
    options: ["< 10k lines", "< 100k lines", "> 100k lines"],
  },
  {
    type: "radio",
    question: "What's your team's experience with Rust?",
    id: "rustExperience",
    direction: "column",
    options: [
      "No experience yet",
      "Some team members have experimented with it",
      "We have one or more small projects in production",
      "We have significant production experience"
    ],
  },
  {
    type: "multipleChoice",
    question: "What are your main motivations for migrating to Rust?", 
    direction: "column",
    id: "motivations",
    options: [
      "Performance improvements",
      "Better type safety",
      "Memory efficiency",
      "Production reliability",
      "Cross-platform deployment",
      "WebAssembly support",
      "Embedded systems development",
      "Microservices migration",
      "Other"
    ],
  },
  {
    type: "multipleChoice",
    question: "What are your main concerns about migrating to Rust?",
    id: "concerns",
    direction: "column",
    options: [
      "Learning curve for the team",
      "Migration complexity",
      "Maintaining productivity during transition",
      "Finding Rust developers",
      "Integration with existing Python code",
      "Third-party library availability",
      "Build times",
      "Testing and deployment changes",
      "None/Other"
    ],
  },
  {
    type: "radio",
    question: "What's your timeline for the migration?", 
    id: "timeline",
    options: [
      "Immediate (next 3 months)",
      "Medium-term (3-12 months)",
      "Long-term (12+ months)"
    ],
  },
  {
    type: "multipleChoice",
    question: "What kind of support is most important for your team?", 
    id: "supportNeeded",
    direction: "column",
    options: [
      "Planning and strategy",
      "Project audit",
      "Training and workshops",
      "Code reviews and mentoring",
      "PyO3 integration support",
      "Performance optimization",
      "Architecture design",
      "Best practices guidance",
      "Team hiring support"
    ],
  },
  {
    type: "radio",
    question: "How many developers would be involved in the migration?",
    options: ["1", "2-3", "4-9", "10+"],
    id: "teamSize",
  },
  {
    type: "input",
    question: "Anything else you'd like to share about your migration plans?",
    id: "additionalComments",
    placeholder: "Share your thoughts...",
    optional: true,
  },
  {
    type: "email",
    question: "What's your email? I'll send you a customized migration strategy based on your responses.",
    id: "email",
  },
];

  let answers = {};
  const progressBar = document.getElementById("progress-bar");
  let totalQuestions = questions.length;
  let currentQuestionIndex = 1;

  document.getElementById("quiz-next-question").addEventListener("click", () => {
    nextQuestion();
  });

  function nextQuestion() {
    // Get the quiz container and store the user's answers
    const quizContainer = document.getElementById("quiz-question-container");
    const inputs = quizContainer.querySelectorAll(
      "input[type='text'], input[type='email'], input[type='radio'], input[type='checkbox']"
    );

    inputs.forEach((input) => {
      if (input.type === "radio" || input.type === "email") {
        if (input.checked) {
          answers[input.name] = input.value;
        }
      } else if (input.type === "checkbox") {
        if (input.checked) {
          if (!answers[input.name]) {
            answers[input.name] = [];
          }
          answers[input.name].push(input.value);
        }
      } else {
        answers[input.id] = input.value;
      }
    });

    console.log(answers);

    if (currentQuestionIndex < questions.length) {
        displayQuestion(currentQuestionIndex++);
    } else {
    // All questions have been answered
    submitQuiz(); 
    }
  }

  function previousQuestion() {
    if (currentQuestionIndex > 0) {
        displayQuestion(--currentQuestionIndex -1);
    }
  }

  document.getElementById("quiz-prev-question").addEventListener("click", () => {
    previousQuestion();
  });

  function updateProgressBar() {
    const progressPercentage = (currentQuestionIndex / totalQuestions) * 100;
    progressBar.style.width = `${progressPercentage}%`;
  }

function displayQuestion(index) {
    history.pushState(
      { index: index },
      `Question ${index}`,
      `?question=${index}`
    );

    updateProgressBar();

    const questionContainer = document.getElementById("quiz-question-container");
    questionContainer.innerHTML = ""; // Clear existing content

    const question = questions[index];
    const questionElement = document.createElement("div");
    questionElement.className = "question";

    if (question.optional) {
      questionElement.innerHTML = `<h2>${question.question} (Optional)</h2>`;
    } else {
      questionElement.innerHTML = `<h2>${question.question}</h2>`;
    }

    // Initially hide the navigation buttons for 'radio' type questions
    const navContainer = document.getElementById("quiz-navigation-container");

    // Hide navContainer for first question
    // if (index === 0) {
    //   navContainer.style.display = "none";
    // } else {
      navContainer.style.display = "flex";
    // }

    document.getElementById("quiz-next-question").disabled = !question.optional;

    let inputElement;

    switch (question.type) {
      case "multipleChoice":
        const gridContainer = document.createElement("div");

        // Set the direction if specified
        if (question.direction) {
          gridContainer.style.display = "flex";
          gridContainer.style.flexDirection = question.direction;
        } else {
          gridContainer.className = "checkbox-grid";
        }

        question.options.forEach((option) => {
          const optionElement = document.createElement("label");
          optionElement.className = "checkbox-label"; // Use this class for checkbox labels
          const inputElement = document.createElement("input");
          inputElement.type = "checkbox";
          inputElement.name = question.id;
          inputElement.value = option;

          optionElement.appendChild(inputElement);
          optionElement.append(" " + option);

          gridContainer.appendChild(optionElement);
        });

        questionElement.appendChild(gridContainer);
        break;

      case "checkbox":
        question.options.forEach((option) => {
          inputElement = document.createElement("input");
          inputElement.type = "checkbox";
          inputElement.id = option;
          inputElement.value = option;
          questionElement.appendChild(inputElement);
          questionElement.appendChild(document.createTextNode(option));
        });
        break;

      case "input":
      case "email":
        inputElement = document.createElement("input");
        inputElement.type = question.type === "email" ? "email" : "text";
        inputElement.id = question.id;
        if (question.placeholder) {
          inputElement.placeholder = question.placeholder;
        }
        questionElement.appendChild(inputElement);
        break;

      case "radio":
        const flexContainer = document.createElement("div");
        flexContainer.className = "quiz-flex-container";

        // Set the direction of the flex container if specified
        if (question.direction) {
          flexContainer.style.flexDirection = question.direction;
        }

        question.options.forEach((option) => {
          const optionLabel = document.createElement("label");
          optionLabel.className = "quiz-button";
          optionLabel.textContent = option;

          const inputElement = document.createElement("input");
          inputElement.type = "radio";
          inputElement.name = question.id;
          inputElement.value = option;
          inputElement.onchange = () => {
            // Automatically move to the next question on selecting a radio option
            nextQuestion();
          };

          optionLabel.appendChild(inputElement);
          flexContainer.appendChild(optionLabel);
        });

        questionElement.appendChild(flexContainer);
        break;
    }

    // Append the fully constructed questionElement to the questionContainer
    questionContainer.appendChild(questionElement);

    if (currentQuestionIndex > 1) {
      document.getElementById("quiz-prev-question").style.display = "";
    } else {
      document.getElementById("quiz-prev-question").style.display = "none";
    }

    // Handle button enabling based on input and optional status
    const inputs = questionContainer.querySelectorAll(
      "input[type='text'], input[type='email'], input[type='radio'], input[type='checkbox']"
    );
    
    inputs.forEach((input) => {
      input.addEventListener("input", () => {
        // For text and email fields
        if (question.optional || input.value.trim().length > 0) {
          document.getElementById("quiz-next-question").disabled = false;
        } else {
          document.getElementById("quiz-next-question").disabled = true;
        }
      });
      
      input.addEventListener("change", () => {
        // For radio buttons and checkboxes
        if (question.type === "multipleChoice") {
          // Enable next if at least one checkbox is checked or if optional
          const anyChecked = Array.from(inputs).some(inp => inp.checked);
          document.getElementById("quiz-next-question").disabled = !(anyChecked || question.optional);
        } else {
          document.getElementById("quiz-next-question").disabled = false;
        }
      });
    });
}

   function submitQuiz() {
   // Create an object to store all answers
   const finalAnswers = {};

   // Go through each question and collect its answer
   questions.forEach(question => {
      switch (question.type) {
         case "radio":
         const radioValue = document.querySelector(`input[name="${question.id}"]:checked`)?.value;
         if (radioValue) {
            finalAnswers[question.id] = radioValue;
         }
         break;

         case "multipleChoice":
         const checkboxes = document.querySelectorAll(`input[name="${question.id}"]:checked`);
         finalAnswers[question.id] = Array.from(checkboxes).map(cb => cb.value);
         break;

         case "input":
         case "email":
         const inputValue = document.getElementById(question.id)?.value;
         if (inputValue) {
            finalAnswers[question.id] = inputValue;
         }
         break;
      }
   });

   // Add any answers stored in the global answers object that might have been missed
   Object.assign(finalAnswers, answers);

   console.log("Quiz completed! Answers:");
   console.log(JSON.stringify(finalAnswers, null, 2));

   // Here you can add code to submit the answers to your backend
   // For example:
   // fetch('/api/submit-quiz', {
   //   method: 'POST',
   //   headers: {
   //     'Content-Type': 'application/json',
   //   },
   //   body: JSON.stringify(finalAnswers)
   // });
   }

  displayQuestion(0); // Initialize with the first question

  window.addEventListener("popstate", function (event) {
    if (event.state) {
      displayQuestion(event.state.index);
    } else {
      // If there is no state, reset to the first question
      displayQuestion(0);
    }
  });
</script>

<style>
  .quiz-container {
    max-width: 600px;
    margin: 0 auto;
    overflow: hidden;
  }

  .quiz-progress-container {
    width: 100%;
    background-color: #ddd;
    height: 5px;
    margin-bottom: 20px;
  }

  .progress-bar {
    height: 100%;
    background-color: #ee3856;
    transition: width 0.5s ease-in-out;
  }

  #quiz-navigation-container {
    width: 100%;
    margin-top: 10px;
    display: flex;
    justify-content: space-between;
  }

  .quiz-navbutton {
    padding: 10px 20px;
    background-color: #111; /*$brightPrim */
    color: white;
    cursor: pointer;
    border: none;
  }

  .quiz-flex-container {
    display: flex;
    gap: 10px; /* Adjust based on your preference */
    flex-wrap: wrap; /* Allow items to wrap if they can't fit in a single line */
  }

  .quiz-button {
    padding: 50px 15px;
    border-radius: 4px;
    background-color: #111; /*$brightPrim */
    color: white;
    white-space: nowrap;
    cursor: pointer;
    flex: 1; /* Makes buttons take up equal space */
    text-align: center;
    cursor: pointer;
    font-size: large;
  }

  .quiz-button:hover {
    background-color: #ee3856;
  }

  /* Convert to hand cursor on hover over the buttons or labels */
  input,
  .checkbox-label,
  .quiz-button:hover {
    cursor: pointer;
  }

  /* If the next button is disabled, change the cursor to not-allowed */
  #quiz-next-question:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }

  .quiz-button input[type="radio"] {
    display: none; /* Hide the actual radio button */
  }

  .quiz-container input[type="text"],
  .quiz-container input[type="email"] {
    font-size: larger;
    width: 100%; /* Fill the entire width */
    padding: 15px; /* Comfortable padding */
    border: 1px solid #000; /* 1px black border */
    box-sizing: border-box; /* Padding and border included in the width */
    margin-bottom: 20px; /* Space below each input */
  }

  /* Placeholder styling */
  .quiz-container input::placeholder {
    color: #ccc; /* Light grey placeholder text */
  }

  .question h2 {
    margin: 0;
  }

  /* Grid layout for checkboxes */
  .question .checkbox-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
  }

  /* Custom larger checkbox style */
  .question input[type="checkbox"] {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    margin-right: 10px;
    width: 20px;
    height: 20px;
    border: 2px solid #111;
    border-radius: 4px;
    vertical-align: middle;
  }

  .question input[type="checkbox"]:checked {
    border: 2px solid #111;
    background-color: #ee3856;
  }

  /* Ensure inputs do not exceed the container's width on smaller screens */
  @media (max-width: 600px) {
    .quiz-container input[type="text"],
    .quiz-container input[type="email"] {
      width: calc(100% - 30px); /* Adjust width to account for padding */
    }
  }

  /* Dark mode styles */
  @media (prefers-color-scheme: dark) {
    .quiz-button {
      background-color: #fab71c;
      color: #111; /* Dark text */
    }

    .question input[type="checkbox"] {
      border-color: #fff; /* Light border */
    }

    .question input[type="checkbox"]:checked {
      border: 2px solid #fff;
      background-color: #ee3856;
    }
  }
</style>



{% info(title="A Practical Guide for Decision Makers" ) %}
This guide is written for technical leaders and developers considering moving their teams from Python to Rust.
I used to be a Python developer myself, and I know how daunting it can be to switch to a new language.
Base on years of experience helping teams make this transition, I'll share practical insights on what works, what doesn't, and how to ensure a successful migration.
{% end %}

Python is an incredibly versatile language that powers everything from web applications to data science pipelines. However, as organizations scale, they often encounter limitations around performance, type safety, and robustness. While Rust isn't a direct replacement for Python, it has some answers to these challenges.

But is Rust the right choice for your team? 

In this article, you'll learn:
- How to evaluate whether Rust is the right choice for your Python codebase
- Practical strategies for Python-to-Rust migration
- Common pitfalls and how to avoid them
- Ways to maintain productivity during the transition
- How to leverage Python's strengths alongside Rust

## Key Differences Between Python and Rust

| Aspect            | Python                       | Rust                                |
| ----------------- | ---------------------------- | ----------------------------------- |
| Type System       | Dynamic, optional type hints | Static, strong type system          |
| Memory Management | Garbage collected            | No GC, ownership and borrowing      |
| Performance       | Moderate                     | High performance, low-level control |
| Deployment        | Runtime required             | Single binary, minimal runtime      |
| Package Manager   | Multiple (pip, conda, uv)    | cargo (built-in, consistent)        |
| Error Handling    | Exceptions                   | Result type                         |
| Concurrency       | Limited by GIL               | zero-cost abstractions, no GIL      |
| Learning Curve    | Gentle                       | Steep                               |
| Ecosystem Size    | Vast (500,000+ packages)     | Growing (160,000+ crates)           |


## Why Python Teams Consider Rust

Python developers often want to transition to Rust for several reasons:

1. Developers interested in Rust are likely willing to understand systems programming concepts.
   They grew out of Python's limitations and are looking for more control over performance and memory management.

2. Python developers often long for stronger type guarantees.
   They appreciate Rust's static type system and the safety it provides.

3. Developers with a Python background often work on data processing or web applications.
   These are areas where Rust's performance benefits are most pronounced.

While Python excels at readability and rapid development, teams often hit scaling challenges as their applications grow. Below, I've listed a few common pain points that get mentioned in consultations with teams considering a migration. 

### Performance Bottlenecks

Python's Global Interpreter Lock (GIL) limits true parallelism, making it challenging to fully utilize modern multi-core processors.
There is a version of Python without the GIL, but it [doesn't solve the performance issues](https://news.ycombinator.com/item?id=41677131). 

While tools like asyncio help with I/O-bound tasks, CPU-intensive operations remain constrained. Teams often resort to complex workarounds involving multiple processes or C extensions.

### Type Safety Concerns

Despite Python's type hints, runtime type errors still occur.
Types are optional in Python. 
Developers need the discipline to add and maintain type hints consistently, which can be challenging in large codebases.
Furthermore, adoption is inconsistent across the Python ecosyste (e.g., third-party libraries).
Large Python applications can become difficult to maintain and refactor confidently.

From experience, there is a breaking point around the 10-100k lines of code mark where the lack of type safety becomes a significant liability.[^1]

[^1]: See discussions on large-scale Python applications on [Reddit](https://www.reddit.com/r/Python/comments/a7zrjn/why_do_people_say_that_python_is_not_good_for/) and [HN](https://news.ycombinator.com/item?id=25073308).

### Deployment Complexity

Python applications require managing runtime environments, dependencies, and potential version conflicts. 
A lot of the issues can be mitigated with containerization.
However, bundling Python applications for deployment is not an easy task, especially when targeting platforms with different architectures.

### Resource Usage

Python has a relatively manageable memory profile, but it can be inefficient for certain workloads.
For example, Python's memory overhead can be significant for large-scale data processing or long-running services.
CPU-bound tasks often get offloaded to C extensions or to worker processes, adding complexity and overhead.

## Key Challenges in Transitioning to Rust

The transition from Python to Rust presents unique challenges:

### Syntax

Python is very syntax-light, which makes it easy to read and write.
By comparison, Rust is full of "symbols" and keywords that can be intimidating at first.

Developers need to see through the syntax and understand the underlying semantics to become productive.
This is a critical step in the transition process.

Here is an example of a simple list comprehension in Python:

```python
# A list of bands
bands = [
    "Metallica",
    "Iron Maiden",
    "AC/DC",
    "Judas Priest",
    "Megadeth"
]

# A list comprehension to filter for bands that start with "M"
m_bands = [band for band in bands if band.startswith("M")]

# A list comprehension to uppercase the bands
uppercased = [band.upper() for band in m_bands]

# We get ["METALLICA", "MEGADETH"] 
```

Rust does not have a direct equivalent to list comprehensions.
Instead, [iterator patterns](/blog/iterators) are used to achieve the same result:

```rust
let bands = vec![
    "Metallica",
    "Iron Maiden",
    "AC/DC",
    "Judas Priest",
    "Megadeth",
];

let uppercased: Vec<_> = bands.iter()
                    .filter(|band| band.starts_with("M"))
                    .map(|band| band.to_uppercase())
                    .collect();

// uppercased = vec!["METALLICA", "MEGADETH"]
```

### Ownership and Borrowing

Python developers need to adjust to start "thinking in Rust" to avoid common pitfalls. 
Plan for a 3-4 month learning period where developers will need to understand concepts like:

- Stack vs heap
- Borrowing and move semantics
- Trait-based composition (instead of Python's OOP model)

These are fundamental concepts in Rust and it's important to get them right to become really effective.

Lifetimes are another concept that can be challenging to grasp initially, but you can get a long way without fully understanding them. [Don't worry about lifetimes](/blog/lifetimes) when you're just starting out.

Pointer handling and boxing is another area where Python developers need to adjust. However, beginners can often get by without understanding this in detail.

### Type System Adaptation

Moving from Python's dynamic typing to Rust's static typing requires another mindset shift.
Developers suddenly need to:

- Think about types upfront
- Understand generics and traits
- Lean into `Option<T>` and `Result<T, E>` for error handling
- Use enums for modeling complex states

This can feel intimidating at first, but it's actually a lot of fun once you get the hang of it.
The compiler is helpfully guiding you along the way, and you can start without a deep understanding of all the concepts.

The pattern matching syntax in Rust can be a game-changer for developers coming from Python
and is often cited as one of the most enjoyable features of Rust.

## Integration Strategies

There are several ways to integrate Rust into your Python codebase:

### 1. PyO3 (Python-Rust Bindings) 

[PyO3](https://pyo3.rs/) lets you write Python extensions in Rust or call Rust functions from Python. 

This is ideal for:

- Optimizing performance-critical components
- Gradually introducing Rust while maintaining Python interfaces
- Creating Python packages with Rust internals

### 2. Microservices

For distributed systems, you can:

- Build new services in Rust
- Migrate existing services one at a time
- Use REST or gRPC for inter-service communication

If you already have a microservices architecture, this can be a great way to start.
You can build new services in Rust and gradually replace old Python services as needed.
The new services can be deployed alongside the old ones, and you can ensure that the APIs are compatible.

### 3. CLI Tools and Utilities

If you're just staring out, I recommend to write a command-line tool, which is an excellent candidate for
getting your feet wet. 

They have all the positive indicators for a successful first project: 

- They are self-contained, so you don't have to worry about integrating with the rest of the codebase 
- The deployment is simple, as you can just ship a single binary 
- Rust shines in this area, as it's very convenient to write command-line tools in Rust
- There is no "startup cost" when a CLI tool runs with Rust (as opposed to Python where the interpreter needs to start up) 

### 4. Worker Processes

Let's say you have a web application that needs to do some heavy lifting.
One common way is to offload the work to a worker queue.
That's a great place to test out Rust, as you can directly compare the performance and developer experience with Python.

You can use a message queue like RabbitMQ or Kafka to communicate between the Python web application and the Rust worker. 

### Data Processing Pipelines

Are you using Python for data science or ETL tasks?
For example, you might be using Pandas or Dask for data processing.

Rust has some excellent libraries for data processing, like [Polars](https://pola.rs/) and [Apache Arrow](https://arrow.apache.org/).
A lot of teams start by moving the data preprocessing and ETL tasks to Rust, and they like it so much that they move more and more of the business logic over. 

That worked extremely well for a few clients I worked with, as they could leverage Rust's performance and reliability for the most critical parts of their data processing pipeline.
After a short learning period, the team was as productive in Rust as they were in Python.

## Planning Your Migration

A successful migration requires careful planning:

1. **Start Small**

   - Choose non-critical components first
   - Focus on areas where Rust's benefits are most valuable
   - Build team confidence through early wins

2. **Invest in Training**

   - Allocate time for learning Rust fundamentals
   - Consider bringing in [external expertise](/about) for guidance
   - Set realistic expectations for the learning curve

3. **Measure Success**

   - Define clear metrics (performance, resource usage, development velocity)
   - Document improvements and challenges
   - Adjust strategy based on results

## Common Pitfalls to Avoid 

Rust's ecosystem is smaller than Python's.

On top of that, Rust has a much smaller standard library compared to Python. 
This means you'll commonly rely on third-party crates for functionality that's built into Python.

Depending on your use case, here are some key differences to consider: 

### Data Science

Python dominates data science with libraries like [NumPy](https://numpy.org/) and [Pandas](https://pandas.pydata.org/).
However, Rust is making inroads with libraries like [Polars](https://pola.rs/) and [Apache's Arrow](https://arrow.apache.org/).

You don't have to migrate your entire data science stack to Rust.
Chances are, you have experts on your team who are comfortable with doing data analysis in Python. 
You can start by using the Rust libraries for data preprocessing and ETL tasks.
They have Python bindings, so you get a lot of the benefits of Rust without having to do a full migration.

### Backend Services

Rust wasn't initially planned to be a strong contender in the web development space.
This has changed in recent years with the rise of frameworks like [Axum](https://axum.rs/) and [Loco](https://loco.rs/).
Now, Rust is a viable option for building high-performance APIs and web applications.
It is one key are the Rust team is investing in, and the ecosystem is maturing rapidly.

In combination with [sqlx](https://github.com/launchbadge/sqlx) for database access and [serde](https://serde.rs/) for serialization, Rust is a very effective choice for web backends. 
What surprises many Python developers is how similar it is to working with other web frameworks like Flask or FastAPI.
Another surprise is how robust the final product is, as it catches many bugs at compile time and scales extremely well.
Production Rust web applications are extremely robust.
This lifts a lot of the burden from the operations team.
I expect more backend services to be written in Rust in the future -- especially for high-performance applications.

## Keeping Python's Strengths

Not everything needs to be migrated! Python excels at:

- I personally [prototype in Rust](/blog/protoyping), but Python is still a fine choice for prototyping. 
- Data analysis and visualization are great in Python (e.g., Pandas, Matplotlib)
- Machine learning workflows (e.g., TensorFlow, PyTorch)
- Admin interfaces and tools (e.g., Django admin)

Consider a hybrid approach where each language handles what it does best.

One winning strategy is to explore a space in Python and moving production-workloads to Rust once the requirements are clear
and the project can benefit from performance and scale.
Speaking of which...

## Expected Big Performance Improvements

Actual performance numbers vary significantly based on workload and implementation,
so take these numbers with a grain of salt.

Based on my experience helping teams migrate, here are typical improvements:

- **CPU Usage**: 2-10x reduction in CPU utilization
- **Memory Usage**: 30-70% reduction in memory footprint
- **Latency**: 50-90% improvement in response times
- **Throughput**: 2-5x increase in requests/second

Especially the P90 latency improvements are often surprising to teams.
**There are very few outliers and things tend to run smoothly, no matter the load.**
In Python, this is a common source of frustration, where a single request can take significantly longer than the rest.
Production payloads are extremely boring in Rust. The DevOps team will thank you.

## Conclusion

Migrating to a different programming language is a significant undertaking that requires careful planning and execution.
The step from Python to Rust is no exception.

While the learning curve is steep, the benefits in terms of performance, reliability, and maintainability can be substantial. 

Success depends on:

- Realistic timeline expectations
- Strong team support and training
- Clear understanding of migration goals
- A pragmatic approach to choosing what to migrate

Remember that this isn't an all-or-nothing decision!
Many organizations successfully use Python and Rust together, leveraging each language's strengths.
Write down your reasoning for the migration.
Many issues can be solved in Python, and the migration might not be necessary.
However, if you're hitting the limits of Python, Rust is a strong replacement.

{% info(title="Ready to Make the Move to Rust?", icon="crab") %}

I help teams make successful transitions from Python to Rust.
My clients moved critical workloads to Rust and saw significant improvements in performance and reliability.
Whether you need training, architecture guidance, or migration planning, [let's talk about your needs](/about).

{% end %}