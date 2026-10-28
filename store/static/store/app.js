// Mobile menu
const navToggle = document.querySelector(".nav-toogle");
const siteNav = document.querySelector(".site-nav");

if (navToggle) {
  navToggle.addEventListener("click", () => {
    const open = siteNav.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", String(open));
  });
}

// Feedback dialog
const feedbackDialog = document.querySelector(".feedback-dialog");
const feedbackForm = document.querySelector(".feedback-form");
const feedbackStatus = document.querySelector(".feedback-status");

document.querySelector(".feedback-button").addEventListener("click", () => {
  feedbackStatus.textContent = "";
  feedbackDialog.showModal();
});

document.querySelector(".feedback-cancel").addEventListener("click", () => feedbackDialog.close());

feedbackForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  feedbackForm.page_url.value = window.location.href;
  feedbackForm.browser.value = navigator.userAgent;
  feedbackForm.viewport_width.value = window.innerWidth;
  feedbackForm.viewport_height.value = window.innerHeight;

  feedbackStatus.textContent = "Sending…";
  try {
    const response = await fetch(feedbackForm.action, {
      method: "POST",
      body: new FormData(feedbackForm),
      headers: { "X-Requested-With": "fetch" },
    });
    const result = await response.json();
    if (result.ok) {
      feedbackForm.reset();
      feedbackStatus.textContent = "Thanks! Your feedback was sent.";
      setTimeout(() => feedbackDialog.close(), 1500);
    } else {
      feedbackStatus.textContent = result.error || "Please check your message and try again.";
    }
  } catch {
    feedbackStatus.textContent = "We couldn't send your feedback. Please try again later.";
  }
});
