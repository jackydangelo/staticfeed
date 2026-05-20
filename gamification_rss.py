import feedparser

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit, urlunsplit

from jinja2 import Environment, FileSystemLoader

from config import (
    SOURCE_RSS,
    DAYS_LIMIT,
    TIMEZONE,
    PAGE_TITLE,
    FOOTER_TEXT
)

"""A module-level shared Jinja environment to avoid unnecessary recreations and reuse the internal template cache."""
ENV = Environment(
    loader=FileSystemLoader("templates")
)

def get_cutoff_date(now: datetime, days_limit: int) -> datetime:
    """Returns the cutoff date for filtering articles."""
    return now - timedelta(days=days_limit)


def parse_entry_date(entry) -> datetime | None:
    """Converts the article date to a timezone-aware datetime."""
    raw_parsed = (
        getattr(entry, "published_parsed", None)
        or getattr(entry, "updated_parsed", None)
    )

    if not raw_parsed:
        return None

    try:
        return datetime(
            *raw_parsed[:6],
            tzinfo=ZoneInfo("UTC")
        ).astimezone()

    except Exception as e:
        print("Error parsing data:", getattr(entry, "title", "N/A"), e)
        return None

def normalize_url(url: str) -> str:
    parts = urlsplit(url)

    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        parts.path.rstrip("/"),
        "",
        ""
    ))

def extract_articles(
    feed_url: str,
    cutoff_date: datetime,
    custom_source_label: str,
    seen: set
) -> list:

    articles = []

    feed = feedparser.parse(feed_url)

    source = custom_source_label

    for entry in feed.entries:
        
        title = entry.title.strip()
        url = normalize_url(entry.link)
        
        if url in seen:
            continue
        
        parsed_date = parse_entry_date(entry)

        if not parsed_date:
            continue

        if parsed_date < cutoff_date:
            continue

        seen.add(url)

        articles.append({
            "title": title,
            "link": entry.link,
            "summary": getattr(entry, "summary", ""),
            "published": parsed_date.strftime("%d/%m/%Y %H:%M"),
            "source": source,
            "parsed_date": parsed_date,
        })

    return articles


def collect_articles(cutoff_date: datetime) -> list:

    all_articles = []
    seen = set()

    for url in SOURCE_RSS:

        articles = extract_articles(
            feed_url=source_info["url"],
            custom_source_label=source_info["label"],
            cutoff_date=cutoff_date,
            seen=seen
        )

        all_articles.extend(articles)

    all_articles.sort(
        key=lambda x: x["parsed_date"],
        reverse=True
    )

    """Removes the technical field used solely for sorting. This is done to separate the technical data from the data actually used by the HTML."""
    for article in all_articles: article.pop("parsed_date", None)

    return all_articles


def render_html(
    articles: list,
    now: datetime
) -> str:

    template = ENV.get_template("homepage.html")

    return template.render(
        page_title=PAGE_TITLE,
        footer_text=FOOTER_TEXT,
        updated_at=now.astimezone(TIMEZONE).strftime("%d/%m/%Y %H:%M"),
        articles=articles
    )


def save_html(
    html: str,
    output_path: str = "docs/index.html"
) -> None:

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():

    now = datetime.now().astimezone()

    cutoff_date = get_cutoff_date(
        now=now,
        days_limit=DAYS_LIMIT
    )

    articles = collect_articles(cutoff_date)

    html = render_html(
        articles=articles,
        now=now
    )

    save_html(html)

    print("HTML created: docs/index.html")


if __name__ == "__main__":
    main()
