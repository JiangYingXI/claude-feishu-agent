const API = (() => {
  const DATA_URL = "./data/articles.json";
  const CACHE_KEY = "imaginghot_cache";
  const CACHE_TTL = 60 * 60 * 1000; // 1 hour

  let _data = null;

  function _loadFromCache() {
    try {
      const raw = localStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      const cached = JSON.parse(raw);
      if (Date.now() - cached.timestamp < CACHE_TTL) {
        return cached.data;
      }
    } catch { /* ignore */ }
    return null;
  }

  function _saveToCache(data) {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify({
        timestamp: Date.now(),
        data: data,
      }));
    } catch { /* quota exceeded, ignore */ }
  }

  async function loadArticles() {
    // Try cache first
    const cached = _loadFromCache();
    if (cached) {
      _data = cached;
    }

    // Fetch fresh data
    try {
      const resp = await fetch(DATA_URL);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const fresh = await resp.json();
      if (fresh && fresh.articles) {
        _data = fresh;
        _saveToCache(fresh);
      }
    } catch (err) {
      console.warn("Failed to fetch articles, using cache:", err.message);
      if (!_data) throw err;
    }

    return _data;
  }

  function getData() {
    return _data;
  }

  return { loadArticles, getData };
})();
