import time
import logging

import httpx

from src.utils.config import FEISHU_APP_ID, FEISHU_APP_SECRET

logger = logging.getLogger(__name__)

TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
BASE_URL = "https://open.feishu.cn/open-apis"

_token_cache: dict = {"token": "", "expires_at": 0}


def _get_token() -> str:
    """Get tenant_access_token with caching."""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    resp = httpx.post(TOKEN_URL, json={
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET,
    }, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Feishu auth failed: {data}")

    _token_cache["token"] = data["tenant_access_token"]
    _token_cache["expires_at"] = now + data.get("expire", 3600)
    return _token_cache["token"]


def api(method: str, path: str, json: dict | None = None,
        params: dict | None = None) -> dict:
    """Make an authenticated Feishu API call."""
    token = _get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    url = f"{BASE_URL}{path}"

    for attempt in range(3):
        try:
            resp = httpx.request(method, url, json=json, params=params,
                                 headers=headers, timeout=30)
            data = resp.json()
            if data.get("code") == 0:
                return data
            # Token expired
            if data.get("code") in (99991663, 99991664):
                _token_cache["token"] = ""
                token = _get_token()
                headers["Authorization"] = f"Bearer {token}"
                continue
            logger.error(f"Feishu API error: {data}")
            return data
        except httpx.RequestError as e:
            logger.warning(f"Feishu API attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
    return {"code": -1, "msg": "max retries exceeded"}
