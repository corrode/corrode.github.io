document.addEventListener("DOMContentLoaded", function () {
  // Find all <pre> elements containing <code> blocks
  const codeBlocks = document.querySelectorAll("pre > code");

  // Add copy button to each code block
  codeBlocks.forEach(function (codeBlock) {
    // Create container for positioning the button
    const container = document.createElement("div");
    container.className = "code-block-container";

    // Create the copy button
    const copyButton = document.createElement("button");
    copyButton.className = "copy-code-button";

    // Place the container
    const pre = codeBlock.parentNode;
    pre.parentNode.insertBefore(container, pre);
    container.appendChild(pre);
    container.appendChild(copyButton);

    // Add click event to copy code
    copyButton.addEventListener("click", function () {
      const code = codeBlock.textContent;
      navigator.clipboard
        .writeText(code)
        .then(() => {
          // Success feedback
          copyButton.classList.add("copied");
          setTimeout(function () {
            copyButton.classList.remove("copied");
          }, 2000);
        })
        .catch((err) => {
          console.error("Failed to copy: ", err);
          setTimeout(function () {
            copyButton.classList.remove("copied");
          }, 2000);
        });
    });
  });
});
