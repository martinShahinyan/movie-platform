// Autocomplete for every [data-search] form. DOM is built with textContent only (no innerHTML).
(() => {
  const DEBOUNCE_MS = 180;

  document.querySelectorAll("[data-search]").forEach((form) => {
    const input = form.querySelector("input[name=q]");
    const list = form.querySelector(".suggest");
    let options = [];
    let active = -1;
    let timer = null;
    let controller = null;

    const open = () => { list.hidden = false; input.setAttribute("aria-expanded", "true"); };
    const close = () => {
      list.hidden = true; active = -1;
      input.setAttribute("aria-expanded", "false");
      input.removeAttribute("aria-activedescendant");
    };

    const showSkeleton = () => {
      list.replaceChildren(...[0, 1, 2].map(() => {
        const li = document.createElement("li");
        li.className = "suggest__skeleton";
        li.setAttribute("role", "presentation");
        return li;
      }));
      options = [];
      open();
    };

    const showMessage = (text) => {
      const li = document.createElement("li");
      li.className = "suggest__empty";
      li.setAttribute("role", "presentation");
      li.textContent = text;
      list.replaceChildren(li);
      options = [];
      open();
    };

    const render = (hits) => {
      list.replaceChildren(...hits.map((hit, i) => {
        const li = document.createElement("li");
        li.setAttribute("role", "option");
        li.id = `${list.id}-${i}`;
        const a = document.createElement("a");
        a.href = `/movie/${encodeURIComponent(hit.slug)}`;
        if (hit.poster_url) {
          const img = new Image();
          img.src = hit.poster_url; img.alt = ""; img.width = 32; img.height = 48; img.loading = "lazy";
          a.append(img);
        }
        const title = document.createElement("span");
        title.className = "suggest__title"; title.textContent = hit.title;
        const year = document.createElement("span");
        year.className = "suggest__year"; year.textContent = hit.year ?? "";
        a.append(title, year);
        li.append(a);
        return li;
      }));
      options = [...list.querySelectorAll("[role=option]")];
      active = -1;
      open();
    };

    const setActive = (i) => {
      options.forEach((o) => o.classList.remove("is-active"));
      active = i;
      if (i >= 0) {
        options[i].classList.add("is-active");
        input.setAttribute("aria-activedescendant", options[i].id);
      } else {
        input.removeAttribute("aria-activedescendant");
      }
    };

    const query = async (q) => {
      controller?.abort();
      controller = new AbortController();
      showSkeleton();
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(q)}&limit=6`, { signal: controller.signal });
        if (!res.ok) throw new Error(res.status);
        const hits = await res.json();
        hits.length ? render(hits) : showMessage(`No movies found for \u201c${q}\u201d`);
      } catch (err) {
        if (err.name !== "AbortError") showMessage("Search is unavailable right now. Try again.");
      }
    };

    input.addEventListener("input", () => {
      clearTimeout(timer);
      const q = input.value.trim();
      if (q.length < 2) { controller?.abort(); close(); return; }
      timer = setTimeout(() => query(q), DEBOUNCE_MS);
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { close(); return; }
      if (list.hidden || !options.length) return;
      if (e.key === "ArrowDown") { e.preventDefault(); setActive((active + 1) % options.length); }
      else if (e.key === "ArrowUp") { e.preventDefault(); setActive((active - 1 + options.length) % options.length); }
      else if (e.key === "Enter" && active >= 0) { e.preventDefault(); options[active].querySelector("a").click(); }
    });

    input.addEventListener("focus", () => { if (options.length) open(); });
    document.addEventListener("click", (e) => { if (!form.contains(e.target)) close(); });
  });
})();
