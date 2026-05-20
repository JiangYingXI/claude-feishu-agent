"""Generate frontend/data/articles.json from Feishu records."""
import json
import logging
import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.feishu.crud import fetch_recent_articles
from src.utils import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("generate_json")

TZ_BEIJING = timezone(timedelta(hours=8))

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "data", "articles.json")

VALID_TAGS = [
    "传感器硬件", "镜头与光学", "ISP & 影像芯片",
    "计算摄影 & AI 影像", "拆机 & 实测 & 样张",
    "产品洞察 & 行业资讯", "摄影美学 & 技术科普",
]


def _extract_field(record: dict, field: str, default=None):
    """Safely extract a field from a Feishu record."""
    fields = record.get("fields", {})
    val = fields.get(field)
    if val is None:
        return default
    # Handle link fields: {"link": "...", "text": "..."}
    if isinstance(val, dict) and "link" in val:
        return val["link"]
    # Handle datetime: milliseconds timestamp
    if isinstance(val, str) and val.isdigit() and len(val) == 13:
        try:
            ts = int(val) / 1000
            dt = datetime.fromtimestamp(ts, tz=TZ_BEIJING)
            return dt.isoformat()
        except (ValueError, OSError):
            return val
    return val


def _count_by_category(articles: list[dict]) -> list[dict]:
    """Pre-compute article counts for each category tag."""
    counts = {tag: 0 for tag in VALID_TAGS}
    for a in articles:
        for tag in a.get("categories", []):
            if tag in counts:
                counts[tag] += 1
    return [{"key": tag, "label": tag, "count": counts[tag]} for tag in VALID_TAGS]


def main():
    try:
        config.validate()
    except RuntimeError as e:
        logger.error(f"Config error: {e}")
        sys.exit(1)

    logger.info("Fetching articles from Feishu...")
    resp = fetch_recent_articles(page_size=200)

    if resp.get("code") != 0:
        logger.error(f"Failed to fetch: {resp}")
        sys.exit(1)

    records = resp.get("data", {}).get("items", [])

    articles = []
    for rec in records:
        fields = rec.get("fields", {})
        title = _extract_field(rec, "标题", "")
        source_url = _extract_field(rec, "原文链接", "")
        if not title or not source_url:
            continue

        pub_time = _extract_field(rec, "发布时间", "")

        articles.append({
            "id": rec.get("record_id", ""),
            "title": title,
            "source": _extract_field(rec, "来源", "未知"),
            "source_url": source_url,
            "publish_time": pub_time,
            "summary": _extract_field(rec, "中文摘要", ""),
            "recommendation": _extract_field(rec, "AI推荐理由", ""),
            "categories": _extract_field(rec, "分类标签", []),
        })

    data = {
        "meta": {
            "updated_at": datetime.now(TZ_BEIJING).isoformat(),
            "total_articles": len(articles),
            "data_range_days": 90,
        },
        "categories": _count_by_category(articles),
        "articles": articles,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Generated {OUTPUT_PATH} with {len(articles)} articles")


if __name__ == "__main__":
    main()
