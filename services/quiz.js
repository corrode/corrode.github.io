  var languageOptions = [
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
    "Other",
  ];

  // Quiz state
  let answers = {};
  let currentQuestionIndex = 0;
  let totalQuestions;

  // DOM elements
  const progressBar = document.getElementById("progress-bar");
  const questionContainer = document.getElementById("quiz-question-container");
  const prevButton = document.getElementById("quiz-prev-question");
  const nextButton = document.getElementById("quiz-next-question");

  function initQuiz() {
    totalQuestions = questions.length;
    nextButton.addEventListener("click", nextQuestion);
    prevButton.addEventListener("click", previousQuestion);

    // Handle browser back/forward buttons
    window.addEventListener("popstate", (event) => {
      if (event.state) {
        currentQuestionIndex = event.state.index;
        answers = event.state.answers || {};
        displayQuestion(currentQuestionIndex);
      } else {
        resetQuiz();
      }
    });

    displayQuestion(0);
  }

  function resetQuiz() {
    answers = {};
    currentQuestionIndex = 0;
    displayQuestion(0);
  }

  function updateProgressBar() {
    const progressPercentage =
      ((currentQuestionIndex + 1) / totalQuestions) * 100;
    progressBar.style.width = `${progressPercentage}%`;
  }

  function createQuestionElement(question) {
    const element = document.createElement("div");
    element.className = "question";
    element.innerHTML = `<h3>${question.question}${
      question.optional ? " (Optional)" : ""
    }</h3>`;

    let inputContainer;

    switch (question.type) {
      case "multipleChoice":
        inputContainer = document.createElement("div");
        if (question.direction) {
          inputContainer.style.display = "flex";
          inputContainer.style.flexDirection = question.direction;
        } else {
          inputContainer.className = "checkbox-grid";
        }

        question.options.forEach((option) => {
          const label = document.createElement("label");
          label.className = "checkbox-label";

          const input = document.createElement("input");
          input.type = "checkbox";
          input.name = question.id;
          input.value = option;

          label.appendChild(input);
          label.append(` ${option}`);
          inputContainer.appendChild(label);
        });
        break;

      case "radio":
        inputContainer = document.createElement("div");
        inputContainer.className = "quiz-flex-container";
        if (question.direction) {
          inputContainer.style.flexDirection = question.direction;
        }

        question.options.forEach((option) => {
          const label = document.createElement("label");
          label.className = "quiz-button";
          label.textContent = option;

          const input = document.createElement("input");
          input.type = "radio";
          input.name = question.id;
          input.value = option;

          input.addEventListener("change", () => {
            saveCurrentAnswers();
            nextButton.disabled = false;
            // Auto-advance
            if (currentQuestionIndex < totalQuestions - 1) {
              nextQuestion();
            }
          });

          label.appendChild(input);
          inputContainer.appendChild(label);
        });
        break;

      case "input":
      case "email":
        inputContainer = document.createElement("input");
        inputContainer.type = question.type;
        inputContainer.id = question.id;
        inputContainer.name = question.id;
        inputContainer.placeholder = question.placeholder || "";
        if (question.type === "email") {
          inputContainer.required = true;
        }
        if (!question.optional) {
          inputContainer.required = true;
        }
        break;
    }

    element.appendChild(inputContainer);
    return { element, inputContainer };
  }

  function saveCurrentAnswers() {
    const inputs = questionContainer.querySelectorAll("input");
    const questionId = questions[currentQuestionIndex].id;

    delete answers[questionId];

    inputs.forEach((input) => {
      if (input.type === "checkbox") {
        if (input.checked) {
          answers[questionId] = answers[questionId] || [];
          answers[questionId].push(input.value);
        }
      } else if (
        (input.type === "radio" && input.checked) ||
        input.type === "text" ||
        input.type === "email"
      ) {
        if (input.value.trim()) {
          answers[questionId] = input.value;
        }
      }
    });
  }

  function restorePreviousAnswers(question, container) {
    const previousAnswer = answers[question.id];
    if (!previousAnswer) return;

    const inputs = container.querySelectorAll("input");
    inputs.forEach((input) => {
      if (input.type === "checkbox") {
        input.checked = previousAnswer.includes(input.value);
      } else if (input.type === "radio") {
        input.checked = input.value === previousAnswer;
      } else {
        input.value = previousAnswer;
      }
    });
  }

  function updateNavigationState() {
    prevButton.style.display = currentQuestionIndex > 0 ? "" : "none";
    const question = questions[currentQuestionIndex];
    nextButton.disabled = !isQuestionAnswered(question);
  }

  function isQuestionAnswered(question) {
    if (question.optional) return true;
    const answer = answers[question.id];
    if (!answer) return false;
    if (Array.isArray(answer)) return answer.length > 0;

    if (question.type === "email") {
      const input = document.getElementById(question.id);
      return input && input.checkValidity() && answer.trim().length > 0;
    }

    return answer.trim().length > 0;
  }

  function nextQuestion() {
    if (currentQuestionIndex < totalQuestions - 1) {
      saveCurrentAnswers();
      currentQuestionIndex++;
      displayQuestion(currentQuestionIndex);
    } else {
      submitQuiz();
    }
  }

  function previousQuestion() {
    if (currentQuestionIndex > 0) {
      saveCurrentAnswers();
      currentQuestionIndex--;
      displayQuestion(currentQuestionIndex);
    }
  }

  function displayQuestion(index) {
    const question = questions[index];
    if (!question) return;

    history.pushState(
      { index, answers: { ...answers } },
      `Question ${index + 1}`,
      `?question=${index + 1}`
    );

    questionContainer.innerHTML = "";
    const { element, inputContainer } = createQuestionElement(question);
    questionContainer.appendChild(element);

    restorePreviousAnswers(question, inputContainer);
    updateProgressBar();
    updateNavigationState();

    if (question.type === "input" || question.type === "email") {
      const input = inputContainer;
      input.addEventListener("input", () => {
        if (question.type === "email") {
          nextButton.disabled = !input.checkValidity() && !question.optional;
        } else {
          nextButton.disabled = !input.value.trim() && !question.optional;
        }
      });
    } else if (question.type === "multipleChoice") {
      const inputs = inputContainer.querySelectorAll("input");
      inputs.forEach((input) => {
        input.addEventListener("change", () => {
          const anyChecked = Array.from(inputs).some((i) => i.checked);
          nextButton.disabled = !anyChecked && !question.optional;
        });
      });
    }

    if (question.type === "radio") {
      nextButton.disabled = !answers[question.id] && !question.optional;
    }
  }

  async function submitQuiz() {
    saveCurrentAnswers();

    // Hide the quiz
    questionContainer.innerHTML = "";
    document.getElementById("quiz-navigation-container").style.display = "none";

    // Show the thank you message
    const resultsContainer = document.getElementById("quiz-results");
    resultsContainer.style.display = "block";

    try {
      // Using Formspark as an example
      const response = await fetch(
        typeof formUrl === "undefined" ? formURL : formUrl,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify(answers),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to submit");
      }
    } catch (error) {
      console.error("Failed to submit form:", error);
      // Optionally show an error message to the user
    }
  }

  document.addEventListener("DOMContentLoaded", initQuiz);
