from dataclasses import dataclass
from datetime import datetime
from email.utils import format_datetime


@dataclass(slots=True)
class Article:
    title: str
    link: str
    summary: str
    source: str
    keyword: str
    published_at: datetime

    @property
    def published(self) -> str:
        return format_datetime(self.published_at)

    @property
    def published_display(self) -> str:
        return self.published_at.strftime("%d/%m/%Y %H:%M")

    @property
    def rss_description(self) -> str:
        return (
            f"Keyword: {self.keyword} | "
            f"Fonte: {self.source}"
        )


@dataclass(frozen=True, slots=True)
class FeedSource:
    url: str
    label: str
    keyword: str
