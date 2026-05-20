import os


FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_BITABLE_APP_TOKEN = os.environ.get("FEISHU_BITABLE_APP_TOKEN", "")
FEISHU_TABLE_ID = os.environ.get("FEISHU_TABLE_ID", "")

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

DATA_RETENTION_DAYS = int(os.environ.get("DATA_RETENTION_DAYS", "90"))
CRAWL_INTERVAL_HOURS = int(os.environ.get("CRAWL_INTERVAL_HOURS", "6"))
MAX_ARTICLES_PER_SOURCE = int(os.environ.get("MAX_ARTICLES_PER_SOURCE", "20"))
SUMMARY_MAX_CHARS = int(os.environ.get("SUMMARY_MAX_CHARS", "100"))


def validate():
    missing = []
    for key in ("FEISHU_APP_ID", "FEISHU_APP_SECRET", "FEISHU_BITABLE_APP_TOKEN", "FEISHU_TABLE_ID",
                "CLAUDE_API_KEY", "DEEPSEEK_API_KEY"):
        if not os.environ.get(key):
            missing.append(key)
    if missing:
        raise RuntimeError(f"Missing required config: {', '.join(missing)}")
