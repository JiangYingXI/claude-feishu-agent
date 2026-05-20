import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import feedparser
from dateutil import parser as dateparser

from src.crawlers.sources import Source, get_enabled_sources
from src.crawlers.dedup import content_hash

logger = logging.getLogger(__name__)

TZ_BEIJING = timezone(timedelta(hours=8))


@dataclass
class RawArticle:
    source_name: str
    source_priority: int
    title: str
    link: str
    publish_time: datetime | None
    language: str
    raw_summary: str | None
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = content_hash(self.title, self.link)


def _parse_date(entry: dict) -> datetime | None:
    """Try to extract a datetime from a feed entry."""
    for field in ("published_parsed", "updated_parsed"):
        tp = entry.get(field)
        if tp:
            try:
                from time import mktime
                dt = datetime.fromtimestamp(mktime(tp), tz=TZ_BEIJING)
                return dt
            except Exception:
                pass

    for field in ("published", "updated"):
        raw = entry.get(field, "")
        if raw:
            try:
                return dateparser.parse(raw).astimezone(TZ_BEIJING)
            except Exception:
                pass

    return None


def _filter_imaging_relevant(entry: dict) -> bool:
    """Quick keyword filter: only keep entries related to consumer imaging."""
    title = entry.get("title", "")
    summary = entry.get("summary", "")
    text = f"{title} {summary}".lower()

    # Must match at least one imaging keyword
    imaging_kw = [
        "camera", "lens", "sensor", "photography", "photo", "imaging",
        "aperture", "focal", "shutter", "iso", "megapixel", "cmos",
        "ccd", "bokeh", "stabilization", "pixel", "zoom", "wide",
        "telephoto", "ultrawide", "portrait", "video", "filmmaking",
        "相机", "镜头", "传感器", "摄影", "影像", "拍照", "像素",
        "光圈", "快门", "变焦", "长焦", "广角", "超广角", "人像",
        "视频", "录制", "防抖", "样张", "cmos", "拆机",
    ]
    if not any(kw in text for kw in imaging_kw):
        return False

    # Exclude non-consumer imaging
    exclude_kw = [
        "medical imaging", "industrial camera", "surveillance", "security camera",
        "endoscopy", "microscope", "thermal imaging", "mri", "ct scan", "x-ray",
        "scientific imaging", "astronomy camera", "医学影像", "工业相机", "安防",
        "监控", "内窥镜", "显微镜", "热成像",
    ]
    if any(kw in text for kw in exclude_kw):
        return False

    return True


def _extract_raw_summary(entry: dict) -> str | None:
    """Extract a short raw summary from feed entry."""
    for field in ("summary", "description", "content"):
        val = entry.get(field, "")
        if val:
            # Strip HTML tags
            import re
            text = re.sub(r"<[^>]+>", "", str(val))
            text = re.sub(r"\s+", " ", text).strip()
            return text[:500] if text else None
    return None


def crawl_source(source: Source) -> list[RawArticle]:
    """Crawl a single RSS source, return list of RawArticle."""
    articles: list[RawArticle] = []
    try:
        feed = feedparser.parse(source.url)
        if feed.bozo:
            logger.warning(f"Feed parse warning for {source.name}: {feed.bozo_exception}")
    except Exception as e:
        logger.error(f"Failed to fetch {source.name}: {e}")
        return articles

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue

        if not _filter_imaging_relevant(entry):
            continue

        pub_time = _parse_date(entry)
        raw_summary = _extract_raw_summary(entry)

        articles.append(RawArticle(
            source_name=source.name,
            source_priority=source.priority,
            title=title,
            link=link,
            publish_time=pub_time,
            language=source.language,
            raw_summary=raw_summary,
        ))

    logger.info(f"{source.name}: {len(articles)} articles fetched")
    return articles


def crawl_all_sources(max_workers: int = 6) -> list[RawArticle]:
    """Crawl all enabled sources in parallel."""
    sources = get_enabled_sources()
    all_articles: list[RawArticle] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(crawl_source, s): s for s in sources}
        for future in as_completed(future_map):
            try:
                all_articles.extend(future.result())
            except Exception as e:
                src = future_map[future]
                logger.error(f"Error crawling {src.name}: {e}")

    logger.info(f"Total: {len(all_articles)} articles from {len(sources)} sources")
    return all_articles
