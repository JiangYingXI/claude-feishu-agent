import logging
from datetime import datetime, timezone, timedelta

from src.feishu.client import api
from src.utils.config import FEISHU_BITABLE_APP_TOKEN, FEISHU_TABLE_ID
from src.crawlers.dedup import content_hash

logger = logging.getLogger(__name__)

TZ_BEIJING = timezone(timedelta(hours=8))
TABLE_PATH = f"/bitable/v1/apps/{FEISHU_BITABLE_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records"


def _fmt_dt(dt: datetime | None) -> str | None:
    """Format datetime to milliseconds timestamp for Feishu."""
    if dt is None:
        return None
    return str(int(dt.timestamp() * 1000))


def check_duplicate(hash_val: str) -> bool:
    """Check if an article with this content_hash already exists in Feishu."""
    resp = api("GET", TABLE_PATH, params={
        "filter": f'CurrentValue.[内容哈希]="{hash_val}"',
        "page_size": 1,
    })
    if resp.get("code") == 0:
        items = resp.get("data", {}).get("items", [])
        return len(items) > 0
    return False


def check_duplicates_batch(hashes: list[str]) -> set[str]:
    """Check multiple hashes. Returns set of hashes that already exist."""
    existing = set()
    for h in hashes:
        if check_duplicate(h):
            existing.add(h)
    return existing


def insert_article(
    title_zh: str,
    original_title: str,
    source: str,
    source_url: str,
    publish_time: datetime | None,
    summary: str,
    recommendation: str,
    tags: list[str],
    language: str,
    hash_val: str,
    quality_score: int,
) -> str | None:
    """Insert a processed article into Feishu. Returns record_id or None."""
    fields = {
        "标题": title_zh,
        "原标题": original_title,
        "来源": source,
        "原文链接": {"link": source_url, "text": "阅读原文"},
        "发布时间": _fmt_dt(publish_time) or _fmt_dt(datetime.now(TZ_BEIJING)),
        "中文摘要": summary,
        "AI推荐理由": recommendation,
        "分类标签": tags,
        "语言": language,
        "内容哈希": hash_val,
        "质量评分": quality_score,
        "处理状态": "ready",
    }

    resp = api("POST", TABLE_PATH, json={"fields": fields})
    if resp.get("code") == 0:
        record = resp.get("data", {}).get("record", {})
        return record.get("record_id", "")
    logger.error(f"Insert failed: {resp}")
    return None


def fetch_recent_articles(page_size: int = 200,
                          page_token: str | None = None) -> dict:
    """Fetch recent articles sorted by publish_time desc."""
    params = {
        "sort": [{"field_name": "发布时间", "desc": True}],
        "page_size": page_size,
    }
    if page_token:
        params["page_token"] = page_token
    resp = api("GET", TABLE_PATH, params=params)
    return resp


def fetch_articles_since(days: int = 1) -> list[dict]:
    """Fetch articles from the last N days for digest generation."""
    since = datetime.now(TZ_BEIJING) - timedelta(days=days)
    since_ts = str(int(since.timestamp() * 1000))

    all_records = []
    page_token = None
    while True:
        params = {
            "filter": f'CurrentValue.[发布时间]>{since_ts}',
            "sort": [{"field_name": "质量评分", "desc": True}],
            "page_size": 100,
        }
        if page_token:
            params["page_token"] = page_token
        resp = api("GET", TABLE_PATH, params=params)
        if resp.get("code") != 0:
            break
        items = resp.get("data", {}).get("items", [])
        all_records.extend(items)
        if not resp.get("data", {}).get("has_more"):
            break
        page_token = resp.get("data", {}).get("page_token", "")
        if not page_token:
            break
    return all_records
