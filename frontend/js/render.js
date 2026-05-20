const Render = (() => {

  const VALID_TAGS = [
    "传感器硬件", "镜头与光学", "ISP & 影像芯片",
    "计算摄影 & AI 影像", "拆机 & 实测 & 样张",
    "产品洞察 & 行业资讯", "摄影美学 & 技术科普",
  ];

  function formatTime(isoStr) {
    if (!isoStr) return "";
    try {
      const d = new Date(isoStr);
      const hh = String(d.getHours()).padStart(2, "0");
      const mm = String(d.getMinutes()).padStart(2, "0");
      return `${hh}:${mm}`;
    } catch { return ""; }
  }

  function formatDate(isoStr) {
    if (!isoStr) return "";
    try {
      const d = new Date(isoStr);
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      const weekDays = ["日", "一", "二", "三", "四", "五", "六"];
      const w = weekDays[d.getDay()];
      return `${y}年${m}月${day}日 星期${w}`;
    } catch { return ""; }
  }

  function getDateKey(isoStr) {
    if (!isoStr) return "未知日期";
    try {
      return new Date(isoStr).toLocaleDateString("zh-CN");
    } catch { return "未知日期"; }
  }

  function renderTagBar(categories, activeTag) {
    const bar = document.getElementById("tagBar");
    let html = '<div class="tag-bar-inner">';
    html += `<button class="tag-chip${activeTag === "" ? " active" : ""}" data-tag="">全部</button>`;
    for (const cat of categories) {
      const isActive = activeTag === cat.key;
      html += `<button class="tag-chip${isActive ? " active" : ""}" data-tag="${cat.key}">
        ${cat.label}<span class="count"> ${cat.count}</span>
      </button>`;
    }
    html += "</div>";
    bar.innerHTML = html;
  }

  function renderArticleList(articles) {
    const container = document.getElementById("articleList");
    if (!articles.length) {
      document.getElementById("empty").style.display = "block";
      container.innerHTML = "";
      return;
    }
    document.getElementById("empty").style.display = "none";

    // Group by date
    const groups = new Map();
    for (const a of articles) {
      const key = getDateKey(a.publish_time);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(a);
    }

    let html = "";
    for (const [dateKey, items] of groups) {
      const dateLabel = formatDate(items[0].publish_time);
      html += `<section class="date-group">`;
      html += `<div class="date-label">${dateLabel}</div>`;
      for (const a of items) {
        html += renderCard(a);
      }
      html += `</section>`;
    }
    container.innerHTML = html;
  }

  function renderCard(a) {
    const time = formatTime(a.publish_time);
    const tags = (a.categories || []).filter(t => VALID_TAGS.includes(t));
    const tagHtml = tags.map(t => `<span class="card-tag">${t}</span>`).join("");

    return `
      <article class="article-card" data-id="${a.id}">
        <div class="card-header">
          <h2 class="card-title">
            <a href="${escapeHtml(a.source_url)}" target="_blank" rel="noopener">
              ${escapeHtml(a.title)}
            </a>
          </h2>
          <div class="card-meta">
            <span class="card-source">${escapeHtml(a.source)}</span>
            ${time ? `<span>${time}</span>` : ""}
          </div>
        </div>
        ${a.summary ? `<p class="card-summary">${escapeHtml(a.summary)}</p>` : ""}
        ${a.recommendation ? `<p class="card-recommendation">${escapeHtml(a.recommendation)}</p>` : ""}
        ${tagHtml ? `<div class="card-tags">${tagHtml}</div>` : ""}
      </article>`;
  }

  function escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  return { formatTime, formatDate, getDateKey, renderTagBar, renderArticleList };
})();
