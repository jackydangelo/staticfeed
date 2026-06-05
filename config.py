import json
import os
from zoneinfo import ZoneInfo
from domain import FeedSource

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    _data = json.load(f)

DAYS_LIMIT = int(_data["DAYS_LIMIT"])
REQUEST_TIMEOUT = float(_data["REQUEST_TIMEOUT"])
URL = _data["URL"]
PAGE_TITLE = _data["PAGE_TITLE"]
FOOTER_TEXT = _data["FOOTER_TEXT"]
TIMEZONE = ZoneInfo(_data["TIMEZONE_STR"])
USER_AGENT = _data["USER_AGENT"]
RETRY_CONFIG = _data["RETRY_CONFIG"]

SOURCE_RSS: list[FeedSource] = [
    FeedSource(**source)
    for source in _data["SOURCE_RSS"]
]
