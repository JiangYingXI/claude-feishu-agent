"""Main pipeline: crawl → dedup → AI process → store in Feishu."""
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.crawlers.rss_crawler import crawl_all_sources
from src.crawlers.dedup import content_hash
from src.feishu.crud import check_duplicates_batch, insert_article
from src.ai.pipeline import process_article
from src.utils import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("pipeline")


def main():
    # Validate config (will warn but not crash if optional vars missing in local dev)
    try:
        config.validate()
    except RuntimeError as e:
        logger.error(f"Config error: {e}")
        sys.exit(1)

    # Step 1: Crawl all sources
    logger.info("=== Step 1: Crawling all sources ===")
    raw_articles = crawl_all_sources()
    if not raw_articles:
        logger.info("No new articles found.")
        return

    # Step 2: Dedup against Feishu
    logger.info(f"=== Step 2: Dedup {len(raw_articles)} articles ===")
    hashes = [a.content_hash for a in raw_articles]
    existing = check_duplicates_batch(hashes)
    new_articles = [a for a in raw_articles if a.content_hash not in existing]
    logger.info(f"After dedup: {len(new_articles)} new, {len(existing)} duplicates")

    if not new_articles:
        logger.info("All articles already stored.")
        return

    # Step 3: AI process each new article
    logger.info(f"=== Step 3: AI processing {len(new_articles)} articles ===")
    processed_count = 0
    for i, raw in enumerate(new_articles):
        try:
            processed = process_article(raw)
            # Step 4: Insert into Feishu
            record_id = insert_article(
                title_zh=processed.title_zh,
                original_title=raw.title,
                source=raw.source_name,
                source_url=raw.link,
                publish_time=raw.publish_time,
                summary=processed.summary,
                recommendation=processed.recommendation,
                tags=processed.tags,
                language="中文" if raw.language == "zh" else "English",
                hash_val=raw.content_hash,
                quality_score=processed.quality_score,
            )
            if record_id:
                processed_count += 1
                logger.info(f"[{i+1}/{len(new_articles)}] ✓ {processed.title_zh[:40]}...")
            else:
                logger.warning(f"[{i+1}/{len(new_articles)}] ✗ Insert failed: {raw.title[:40]}")
        except Exception as e:
            logger.error(f"[{i+1}/{len(new_articles)}] ✗ Error: {raw.title[:40]}: {e}")

    logger.info(f"=== Done: {processed_count}/{len(new_articles)} articles stored ===")


if __name__ == "__main__":
    main()
