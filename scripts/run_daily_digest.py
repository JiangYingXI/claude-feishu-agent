"""Generate daily AI-curated digest via Claude."""
import json
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from anthropic import Anthropic
from src.feishu.crud import fetch_articles_since
from src.ai.prompts import SYSTEM_PROMPT, DAILY_DIGEST_PROMPT
from src.utils.config import CLAUDE_API_KEY, CLAUDE_MODEL
from src.utils import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("daily_digest")


def main():
    try:
        config.validate()
    except RuntimeError as e:
        logger.error(f"Config error: {e}")
        sys.exit(1)

    logger.info("Fetching today's articles from Feishu...")
    records = fetch_articles_since(days=1)

    if not records:
        logger.info("No articles today, skipping digest.")
        return

    # Build simplified article list for Claude
    articles_for_ai = []
    for rec in records:
        fields = rec.get("fields", {})
        articles_for_ai.append({
            "record_id": rec.get("record_id", ""),
            "title": fields.get("标题", ""),
            "summary": fields.get("中文摘要", ""),
            "source": fields.get("来源", ""),
            "quality_score": fields.get("质量评分", 5),
            "categories": fields.get("分类标签", []),
        })

    logger.info(f"Sending {len(articles_for_ai)} articles to Claude for curation...")

    client = Anthropic(api_key=CLAUDE_API_KEY)
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        temperature=0.4,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": DAILY_DIGEST_PROMPT.format(
                articles_json=json.dumps(articles_for_ai, ensure_ascii=False, indent=2)),
        }],
    )

    text = resp.content[0].text if resp.content else "{}"
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        digest = json.loads(text.strip())
    except json.JSONDecodeError:
        logger.error(f"Failed to parse digest JSON: {text[:200]}")
        return

    selected_ids = digest.get("selected_ids", [])
    intro = digest.get("intro", "")
    editor_note = digest.get("editor_note", "")

    # Log the digest (in future: write to a separate Feishu table or generate digest.json)
    print(f"\n{'='*60}")
    print(f"📰 影像Hot · 每日精选日报")
    print(f"{'='*60}")
    print(f"\n📝 今日导读：{intro}")
    if editor_note:
        print(f"\n📌 编辑注：{editor_note}")
    print(f"\n📌 入选 {len(selected_ids)} 篇文章：")
    for aid in selected_ids:
        matched = [a for a in articles_for_ai if a["record_id"] == aid]
        if matched:
            a = matched[0]
            print(f"  ✅ [{a['quality_score']}分] {a['title']} — {a['source']}")

    # Write digest to frontend data
    output_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "data")
    os.makedirs(output_dir, exist_ok=True)
    digest_data = {
        "intro": intro,
        "editor_note": editor_note,
        "selected_ids": selected_ids,
    }
    with open(os.path.join(output_dir, "digest.json"), "w", encoding="utf-8") as f:
        json.dump(digest_data, f, ensure_ascii=False, indent=2)

    logger.info("Daily digest saved.")


if __name__ == "__main__":
    main()
