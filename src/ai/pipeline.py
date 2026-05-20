import logging

from src.crawlers.rss_crawler import RawArticle
from src.ai.translator import translate_title, translate_summary
from src.ai.summarizer import summarize
from src.ai.tagger import tag_article, recommend

logger = logging.getLogger(__name__)


class ProcessedArticle:
    def __init__(self, raw: RawArticle, title_zh: str, summary: str,
                 tags: list[str], confidence: float,
                 recommendation: str, quality_score: int):
        self.raw = raw
        self.title_zh = title_zh
        self.summary = summary
        self.tags = tags
        self.confidence = confidence
        self.recommendation = recommendation
        self.quality_score = quality_score


def process_article(raw: RawArticle) -> ProcessedArticle:
    """Run full AI pipeline on a single raw article."""
    # Step 1: Translate title if English
    if raw.language == "en":
        title_zh = translate_title(raw.title)
    else:
        title_zh = raw.title

    # Step 2: Translate raw summary if English
    raw_summary_zh = raw.raw_summary
    if raw.language == "en" and raw.raw_summary:
        raw_summary_zh = translate_summary(raw.raw_summary)

    # Step 3: Summarize
    summary = summarize(title_zh, raw_summary_zh)

    # Step 4: Tag with categories (Claude)
    tags, confidence = tag_article(title_zh, summary)

    # Step 5: Recommendation + quality score (Claude)
    recommendation, quality_score = recommend(title_zh, summary, tags)

    return ProcessedArticle(
        raw=raw, title_zh=title_zh, summary=summary,
        tags=tags, confidence=confidence,
        recommendation=recommendation, quality_score=quality_score,
    )
