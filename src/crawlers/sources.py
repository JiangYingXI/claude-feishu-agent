from dataclasses import dataclass, field


@dataclass
class Source:
    name: str
    url: str
    language: str  # "en" | "zh"
    priority: int  # 1-5, higher = more authoritative for dedup tiebreak
    enabled: bool = True
    type: str = "rss"  # "rss" | "rsshub" | "web"


SOURCES: list[Source] = [
    # ── International (English) — Native RSS ──
    Source(name="PetaPixel", url="https://petapixel.com/feed/",
           language="en", priority=4),
    Source(name="DPReview", url="https://www.dpreview.com/feeds/news.xml",
           language="en", priority=5),
    Source(name="GSMArena", url="https://www.gsmarena.com/rss-news-reviews.php3",
           language="en", priority=4),
    Source(name="DXOMARK", url="https://www.dxomark.com/feed/",
           language="en", priority=5),
    Source(name="DigitalCameraWorld", url="https://www.digitalcameraworld.com/feed",
           language="en", priority=4),
    Source(name="SonyAlphaRumors", url="https://www.sonyalpharumors.com/feed/",
           language="en", priority=3),
    Source(name="CanonRumors", url="https://www.canonrumors.com/feed/",
           language="en", priority=3),
    Source(name="FujiRumors", url="https://www.fujirumors.com/feed/",
           language="en", priority=3),
    Source(name="NikonRumors", url="https://nikonrumors.com/feed/",
           language="en", priority=3),
    Source(name="PhotographyBlog", url="https://www.photographyblog.com/feeds/latest",
           language="en", priority=3),
    Source(name="ThePhoBlographer", url="https://www.thephoblographer.com/feed/",
           language="en", priority=3),

    # ── Chinese — RSSHub ──
    Source(name="Chiphell-摄影作品", url="https://rsshub.app/chiphell/forum/54",
           language="zh", priority=3, type="rsshub"),
    Source(name="Chiphell-相机", url="https://rsshub.app/chiphell/forum/20",
           language="zh", priority=3, type="rsshub"),

    # ── Chinese — Web Scraping (Phase 2, disabled for now) ──
    Source(name="智东西", url="https://www.zhidx.com/",
           language="zh", priority=4, enabled=False, type="web"),
    Source(name="ZEALER", url="https://www.zealer.com/",
           language="zh", priority=3, enabled=False, type="web"),
]


def get_enabled_sources() -> list[Source]:
    return [s for s in SOURCES if s.enabled]


SOURCE_PRIORITY: dict[str, int] = {s.name: s.priority for s in SOURCES}
