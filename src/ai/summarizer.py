import json
import logging

from openai import OpenAI

from src.utils.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, SUMMARY_MAX_CHARS
from src.ai.prompts import SUMMARIZE_PROMPT

logger = logging.getLogger(__name__)

_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def summarize(title: str, raw_summary: str | None) -> str:
    """Generate a ≤100 char Chinese summary via DeepSeek."""
    try:
        resp = _client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "user", "content": SUMMARIZE_PROMPT.format(
                    title=title,
                    raw_summary=raw_summary or "",
                    max_chars=SUMMARY_MAX_CHARS,
                )}
            ],
            temperature=0.3,
            max_tokens=200,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content or "{}")
        summary = data.get("summary", "")
        # Enforce length
        if len(summary) > SUMMARY_MAX_CHARS:
            summary = summary[:SUMMARY_MAX_CHARS]
        return summary
    except Exception as e:
        logger.warning(f"Summarization failed: {e}")
        # Fallback: use raw summary truncated
        if raw_summary:
            return raw_summary[:SUMMARY_MAX_CHARS]
        return title[:SUMMARY_MAX_CHARS]
