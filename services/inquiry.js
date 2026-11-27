(() => {
  const form = document.getElementById("inquiry-form");
  if (!form) return;

  const button = form.querySelector('button[type="submit"]');
  const status = document.getElementById("inquiry-status");
  const success = document.getElementById("inquiry-success");
  let pending = false;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (pending || !form.reportValidity()) return;

    pending = true;
    button.disabled = true;
    form.setAttribute("aria-busy", "true");
    status.textContent = "Sending your inquiry…";
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);

    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(Object.fromEntries(new FormData(form))),
        signal: controller.signal,
      });
      if (!response.ok) throw new Error("Submission not accepted");

      form.hidden = true;
      status.textContent = "";
      success.hidden = false;
      success.focus();
    } catch (error) {
      status.textContent = "I couldn't confirm that your inquiry was sent. Your details are still here. Please try again, or email hi@corrode.dev.";
      status.focus();
    } finally {
      clearTimeout(timeout);
      pending = false;
      button.disabled = false;
      form.removeAttribute("aria-busy");
    }
  });
})();
