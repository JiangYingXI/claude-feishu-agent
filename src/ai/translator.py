import json
import logging

from openai import OpenAI

from src.utils.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from src.ai.prompts import TRANSLATE_PROMPT, TRANSLATE_SUMMARY_PROMPT

logger = logging.getLogger(__name__)

_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def translate_title(title: str) -> str:
    """Translate an English title to Chinese via DeepSeek."""
    if not title or not title.strip():
        return title
    # Quick check: if already mostly Chinese, skip
    cn_chars = sum(1 for c in title if "一" <= c <= "鿿")
    if cn_chars / max(len(title), 1) > 0.5:
        return title

    try:
        resp = _client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "user", "content": TRANSLATE_PROMPT.format(title=title)}
            ],
            temperature=0.2,
            max_tokens=100,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content or "{}")
        return data.get("title_zh", title)
    except Exception as e:
        logger.warning(f"Translation failed for title: {e}")
        return title


def translate_summary(summary: str) -> str:
    """Translate an English summary to Chinese via DeepSeek."""
    if not summary or not summary.strip():
        return summary or ""

    cn_chars = sum(1 for c in summary if "一" <= c <= "鿿")
    if cn_chars / max(len(summary), 1) > 0.5:
        return summary

    try:
        resp = _client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "user", "content": TRANSLATE_SUMMARY_PROMPT.format(summary=summary[:1000])}
            ],
            temperature=0.2,
            max_tokens=300,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content or "{}")
        return data.get("summary_zh", summary)
    except Exception as e:
        logger.warning(f"Translation failed for summary: {e}")
        return summary
