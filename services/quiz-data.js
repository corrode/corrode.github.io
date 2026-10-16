var questions = [
  {
    type: "radio",
    question: "What's your role in the team?",
    direction: "column",
    id: "role",
    options: [
      "Team Lead/Engineering Manager",
      "Technical Lead/Architect",
      "Developer",
      "Product Manager/Owner",
      "Other"
    ]
  },
  {
    type: "multipleChoice",
    question: "Which languages are primarily used in your codebase?",
    id: "currentStack",
    options: [
      "Python",
      "TypeScript",
      "JavaScript",
      "Java",
      "C/C++",
      "Go",
      "C#",
      "Other"
    ]
  },
  {
    type: "radio",
    question: "What's your team's current experience with Rust?",
    id: "rustExperience",
    direction: "column",
    options: [
      "No experience yet",
      "Learning/Prototyping",
      "First production project",
      "Multiple production services"
    ]
  },
  {
    type: "radio",
    question: "How many developers are on your team?",
    id: "teamSize",
    options: ["1-2", "3-5", "6-10", "10+"]
  },
  {
    type: "multipleChoice",
    question: "What type of support are you looking for?",
    id: "supportType",
    direction: "column",
    options: [
      "Code reviews and best practices",
      "Architecture guidance",
      "Team training/workshops",
      "Project audit",
      "Implementation support",
      "Production readiness assessment",
      "Performance optimization",
      "CI/CD setup and DevOps"
    ]
  },
  {
    type: "multipleChoice",
    question: "What are your main challenges with Rust adoption?",
    id: "challenges",
    direction: "column",
    options: [
      "Developer productivity",
      "Knowledge gaps in systems programming",
      "Project structure and architecture",
      "Testing and deployment practices",
      "Integration with existing systems",
      "Build times and tooling",
      "Team buy-in",
      "Production readiness"
    ]
  },
  {
    type: "radio",
    question: "What's your preferred engagement model?",
    id: "engagementModel",
    direction: "column",
    options: [
      "Regular weekly sessions",
      "Project-based consulting",
      "On-demand support",
      "Intensive training/workshop",
      "Not sure yet"
    ]
  },
  {
    type: "radio",
    question: "When would you like to start?",
    id: "timeline",
    options: [
      "As soon as possible",
      "Next 4-6 weeks",
      "Next quarter",
      "Still exploring"
    ]
  },
  {
    type: "input",
    question: "Any specific requirements or concerns you'd like to discuss?",
    id: "additionalInfo",
    placeholder: "Share your thoughts...",
    optional: true
  },
  {
    type: "email",
    question: "What's your email? I'll send you a detailed overview of how I can help.",
    id: "email",
    placeholder: "your@email.com"
  }
];

var formUrl = "https://submit-form.com/r7PT0RxiL";
