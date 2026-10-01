// "Find my movie" form: max 3 moods, clean URLs (blank selects are not submitted).
(() => {
  const MAX_MOODS = 3;
  document.querySelectorAll("[data-finder]").forEach((form) => {
    const boxes = [...form.querySelectorAll("input[name=mood]")];
    const selects = [...form.querySelectorAll("select")];

    const syncMoods = () => {
      const chosen = boxes.filter((b) => b.checked).length;
      boxes.forEach((b) => {
        b.disabled = !b.checked && chosen >= MAX_MOODS;
        b.closest(".pill").classList.toggle("is-disabled", b.disabled);
      });
    };
    boxes.forEach((b) => b.addEventListener("change", syncMoods));
    syncMoods();

    form.addEventListener("submit", () => selects.forEach((s) => { if (!s.value) s.disabled = true; }));
    // Coming back with the browser's Back button must not leave selects disabled.
    window.addEventListener("pageshow", () => { selects.forEach((s) => { s.disabled = false; }); syncMoods(); });
  });
})();
