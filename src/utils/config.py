import os


FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_BITABLE_APP_TOKEN = os.environ.get("FEISHU_BITABLE_APP_TOKEN", "")
FEISHU_TABLE_ID = os.environ.get("FEISHU_TABLE_ID", "")

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_ANTHROPIC_BASE_URL = os.environ.get(
    "DEEPSEEK_ANTHROPIC_BASE_URL", "https://api.deepseek.com/anthropic"
)

DATA_RETENTION_DAYS = int(os.environ.get("DATA_RETENTION_DAYS", "90"))
SUMMARY_MAX_CHARS = int(os.environ.get("SUMMARY_MAX_CHARS", "100"))


def validate():
    missing = []
    for key in ("FEISHU_APP_ID", "FEISHU_APP_SECRET",
                "FEISHU_BITABLE_APP_TOKEN", "FEISHU_TABLE_ID",
                "DEEPSEEK_API_KEY"):
        if not os.environ.get(key):
            missing.append(key)
    if missing:
        raise RuntimeError(f"Missing required config: {', '.join(missing)}")
