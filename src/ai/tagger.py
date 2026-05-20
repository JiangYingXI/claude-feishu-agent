import json
import logging

from anthropic import Anthropic

from src.utils.config import CLAUDE_API_KEY, CLAUDE_MODEL
from src.ai.prompts import SYSTEM_PROMPT, TAG_PROMPT, RECOMMEND_PROMPT

logger = logging.getLogger(__name__)

_client = Anthropic(api_key=CLAUDE_API_KEY)

VALID_TAGS = [
    "传感器硬件", "镜头与光学", "ISP & 影像芯片",
    "计算摄影 & AI 影像", "拆机 & 实测 & 样张",
    "产品洞察 & 行业资讯", "摄影美学 & 技术科普",
]


def _validate_tags(tags: list[str]) -> list[str]:
    """Ensure tags are valid, discard unknown ones."""
    result = []
    for t in tags:
        if t in VALID_TAGS:
            result.append(t)
    if not result:
        result.append("产品洞察 & 行业资讯")  # safe default
    return result[:2]


def tag_article(title: str, summary: str) -> tuple[list[str], float]:
    """Classify article into 1-2 of 7 categories via Claude. Returns (tags, confidence)."""
    try:
        resp = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=100,
            temperature=0.2,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": TAG_PROMPT.format(title=title, summary=summary),
            }],
        )
        text = resp.content[0].text if resp.content else "{}"
        # Extract JSON from possible markdown code block
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text.strip())
        tags = _validate_tags(data.get("tags", []))
        confidence = float(data.get("confidence", 0.5))
        return tags, confidence
    except Exception as e:
        logger.warning(f"Tagging failed: {e}")
        return ["产品洞察 & 行业资讯"], 0.3


def recommend(title: str, summary: str, tags: list[str]) -> tuple[str, int]:
    """Generate AI recommendation reason and quality score via Claude."""
    try:
        resp = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=200,
            temperature=0.4,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": RECOMMEND_PROMPT.format(
                    title=title, summary=summary, tags=", ".join(tags)),
            }],
        )
        text = resp.content[0].text if resp.content else "{}"
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text.strip())
        rec = data.get("recommendation", "")
        score = int(data.get("quality_score", 5))
        score = max(1, min(10, score))
        return rec, score
    except Exception as e:
        logger.warning(f"Recommendation failed: {e}")
        return "", 5
