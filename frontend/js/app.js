const App = (() => {
  let allArticles = [];
  let activeTag = "";

  function getActiveTagFromHash() {
    const hash = window.location.hash.slice(1);
    if (hash.startsWith("tag=")) {
      return decodeURIComponent(hash.slice(4));
    }
    return "";
  }

  function setHash(tag) {
    if (tag) {
      window.location.hash = `tag=${encodeURIComponent(tag)}`;
    } else {
      history.replaceState(null, "", window.location.pathname);
    }
  }

  function filterArticles() {
    const query = document.getElementById("searchInput").value.trim().toLowerCase();

    let filtered = allArticles;

    if (activeTag) {
      filtered = filtered.filter(a =>
        (a.categories || []).includes(activeTag)
      );
    }

    if (query) {
      filtered = filtered.filter(a =>
        a.title.toLowerCase().includes(query) ||
        (a.summary || "").toLowerCase().includes(query)
      );
    }

    return filtered;
  }

  function refreshUI() {
    const data = API.getData();
    if (!data) return;

    // Render tag bar with counts based on current filter
    Render.renderTagBar(data.categories, activeTag);

    // Filter and render
    const filtered = filterArticles();
    Render.renderArticleList(filtered);

    // Update active tag button
    document.querySelectorAll(".tag-chip").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.tag === activeTag);
    });
  }

  function onTagClick(tag) {
    activeTag = tag;
    setHash(tag);
    refreshUI();
  }

  function onSearchInput() {
    refreshUI();
  }

  async function init() {
    const loading = document.getElementById("loading");
    const error = document.getElementById("error");

    loading.style.display = "block";
    error.style.display = "none";

    try {
      const data = await API.loadArticles();
      allArticles = data.articles || [];

      // Restore tag from URL hash
      activeTag = getActiveTagFromHash();

      refreshUI();
    } catch (err) {
      console.error("Init failed:", err);
      error.style.display = "block";
    } finally {
      loading.style.display = "none";
    }
  }

  // Event delegation for tag bar clicks
  document.getElementById("tagBar").addEventListener("click", (e) => {
    const chip = e.target.closest(".tag-chip");
    if (!chip) return;
    onTagClick(chip.dataset.tag);
  });

  // Search input with debounce
  let searchTimer;
  document.getElementById("searchInput").addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(onSearchInput, 200);
  });

  // Listen for hash changes (browser back/forward)
  window.addEventListener("hashchange", () => {
    activeTag = getActiveTagFromHash();
    refreshUI();
  });

  document.addEventListener("DOMContentLoaded", init);

  return { refreshUI, init };
})();
