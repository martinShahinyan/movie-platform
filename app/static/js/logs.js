document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("log-modal");
  const openBtns = [document.getElementById("open-log-modal"), document.getElementById("open-log-modal-2")].filter(Boolean);
  const closeBtn = document.getElementById("modal-log-close");
  const cancelBtn = document.getElementById("modal-log-cancel");
  const logForm = document.getElementById("log-form");
  const logsContainer = document.getElementById("logs-container");
  const noLogsMsg = document.getElementById("no-logs-msg");
  const dateInput = document.getElementById("log-date");

  if (!modal || !logForm) return;

  // Set default date to today
  if (dateInput && !dateInput.value) {
    const today = new Date().toISOString().split("T")[0];
    dateInput.value = today;
  }

  function openModal() {
    modal.classList.add("is-visible");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modal.classList.remove("is-visible");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  openBtns.forEach(btn => btn.addEventListener("click", openModal));
  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("is-visible")) {
      closeModal();
    }
  });

  // Rating buttons in modal
  const ratingBtns = document.querySelectorAll("#log-rating-select .rating-btn");
  const hiddenRating = document.getElementById("log-rating");

  ratingBtns.forEach(b => {
    b.addEventListener("click", () => {
      const val = b.dataset.value;
      if (hiddenRating.value === val) {
        hiddenRating.value = "";
        b.classList.remove("is-active");
      } else {
        hiddenRating.value = val;
        ratingBtns.forEach(x => x.classList.remove("is-active"));
        b.classList.add("is-active");
      }
    });
  });

  // Submit log form
  logForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const movieId = logForm.dataset.movieId;
    const textVal = document.getElementById("log-text").value.trim();
    const ratingVal = hiddenRating.value ? parseInt(hiddenRating.value) : null;
    const watchedVal = dateInput.value || null;

    if (!textVal) return;

    const submitBtn = document.getElementById("log-submit-btn");
    submitBtn.disabled = true;
    submitBtn.textContent = "Saving...";

    try {
      const resp = await fetch(`/api/movies/${movieId}/log`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: textVal,
          rating: ratingVal,
          watched_at: watchedVal
        })
      });

      if (!resp.ok) {
        throw new Error("Failed to save log");
      }

      const logData = await resp.json();

      // Create new log card DOM element
      const article = document.createElement("article");
      article.className = "log-card log-card--new";
      article.innerHTML = `
        <div class="log-card__header">
          <div class="log-card__meta">
            <span class="log-card__author">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 1 0-16 0"/></svg>
              Anonymous viewer
            </span>
            ${logData.rating ? `<span class="log-card__rating">★ ${logData.rating}/10</span>` : ''}
            <span class="log-card__date">${logData.watched_at}</span>
          </div>
        </div>
        <p class="log-card__text">${escapeHtml(logData.text)}</p>
      `;

      if (noLogsMsg) noLogsMsg.remove();
      if (logsContainer) {
        logsContainer.prepend(article);
      }

      closeModal();
      logForm.reset();
      if (dateInput) dateInput.value = new Date().toISOString().split("T")[0];
      ratingBtns.forEach(x => x.classList.remove("is-active"));

      // Also sync rating buttons on the main page if rating was included
      if (ratingVal) {
        const rateBtns = document.querySelectorAll("#movie-rating-bar .rate-num-btn");
        rateBtns.forEach(b => {
          if (parseInt(b.dataset.value) === ratingVal) b.classList.add("is-selected");
          else b.classList.remove("is-selected");
        });
        const statusMsg = document.getElementById("user-rating-status");
        if (statusMsg) {
          statusMsg.innerHTML = `Your rating: <strong>${ratingVal}/10</strong> <small>(Click a number to update)</small>`;
        }
      }
    } catch (err) {
      alert("Failed to submit log. Please try again.");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Save Log";
    }
  });

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
});
