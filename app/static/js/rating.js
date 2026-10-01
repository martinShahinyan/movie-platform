document.addEventListener("DOMContentLoaded", () => {
  const ratingBar = document.getElementById("movie-rating-bar");
  const movieElem = document.querySelector("article.movie");
  const statusMsg = document.getElementById("user-rating-status");
  const communityDisplay = document.getElementById("community-rating-display");

  if (!ratingBar || !movieElem) return;

  const movieId = movieElem.dataset.movieId;

  ratingBar.querySelectorAll(".rate-num-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const val = parseInt(btn.dataset.value);
      if (!val || val < 1 || val > 10) return;

      // Optimistic UI update
      ratingBar.querySelectorAll(".rate-num-btn").forEach(b => b.classList.remove("is-selected"));
      btn.classList.add("is-selected");
      if (statusMsg) {
        statusMsg.innerHTML = `Saving your rating: <strong>${val}/10</strong>...`;
      }

      try {
        const resp = await fetch(`/api/movies/${movieId}/rating`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ value: val })
        });

        if (!resp.ok) {
          throw new Error("Failed to save rating");
        }

        const data = await resp.json();
        if (statusMsg) {
          statusMsg.innerHTML = `Your rating: <strong>${val}/10</strong> <small>(Click a number to update)</small>`;
        }

        // Also update log modal's hidden rating field if present
        const logRatingInput = document.getElementById("log-rating");
        if (logRatingInput) logRatingInput.value = val;
        const logRatingBtns = document.querySelectorAll("#log-rating-select .rating-btn");
        logRatingBtns.forEach(b => {
          if (parseInt(b.dataset.value) === val) b.classList.add("is-active");
          else b.classList.remove("is-active");
        });

        // Update community rating text if available
        if (communityDisplay) {
          // Fetch updated stats
          const statsResp = await fetch(`/api/movies/${movieId}/rating`);
          if (statsResp.ok) {
            const stats = await statsResp.json();
            communityDisplay.innerHTML = `★ ${stats.community_rating.toFixed(1)}<small id="community-vote-count"> (${stats.vote_count.toLocaleString()} ratings)</small>`;
          }
        }
      } catch (err) {
        if (statusMsg) {
          statusMsg.innerHTML = `<span style="color:#e50914">Error saving rating. Please try again.</span>`;
        }
      }
    });
  });
});
