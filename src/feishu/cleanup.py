import logging
from datetime import datetime, timezone, timedelta

from src.feishu.client import api
from src.feishu.crud import TABLE_PATH
from src.utils.config import DATA_RETENTION_DAYS

logger = logging.getLogger(__name__)

TZ_BEIJING = timezone(timedelta(hours=8))


def cleanup_old_records() -> int:
    """Delete records older than DATA_RETENTION_DAYS. Returns count deleted."""
    cutoff = datetime.now(TZ_BEIJING) - timedelta(days=DATA_RETENTION_DAYS)
    cutoff_ts = str(int(cutoff.timestamp() * 1000))

    deleted = 0
    page_token = None

    while True:
        params: dict = {
            "filter": f'CurrentValue.[发布时间]<{cutoff_ts}',
            "page_size": 100,
        }
        if page_token:
            params["page_token"] = page_token

        resp = api("GET", TABLE_PATH, params=params)
        if resp.get("code") != 0:
            logger.error(f"Cleanup fetch failed: {resp}")
            break

        items = resp.get("data", {}).get("items", [])
        if not items:
            break

        # Delete in batch
        for item in items:
            record_id = item.get("record_id", "")
            if record_id:
                del_resp = api("DELETE", f"{TABLE_PATH}/{record_id}")
                if del_resp.get("code") == 0:
                    deleted += 1
                else:
                    logger.warning(f"Delete {record_id} failed: {del_resp}")

        if not resp.get("data", {}).get("has_more"):
            break
        page_token = resp.get("data", {}).get("page_token", "")
        if not page_token:
            break

    logger.info(f"Cleanup: {deleted} records older than {DATA_RETENTION_DAYS} days")
    return deleted
