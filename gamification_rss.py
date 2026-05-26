import feedparser
import logging
import socket

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit, urlunsplit
from email.utils import format_datetime
from jinja2 import Environment, FileSystemLoader
from xml.sax.saxutils import escape

from config import (
    SOURCE_RSS,
    DAYS_LIMIT,
    REQUEST_TIMEOUT,
    TIMEZONE,
    URL,
    PAGE_TITLE,
    FOOTER_TEXT
)

"""A module-level shared Jinja environment to avoid unnecessary recreations and reuse the internal template cache."""
ENV = Environment(
    loader=FileSystemLoader("templates")
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

"""Timeout global net"""
socket.setdefaulttimeout(float(REQUEST_TIMEOUT))

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

    except Exception:
        logging.exception(
            "Error parsing date for: %s",
            getattr(entry, "title", "N/A")
        )
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

def fetch_feed(feed_url: str):
    feed = feedparser.parse(feed_url)

    if feed.bozo:
        logging.warning(
            "Malformed feed: %s (%s)",
            feed_url,
            feed.bozo_exception
        )

    entries = getattr(feed, "entries", None)

    if not entries:
        logging.warning("Empty feed: %s", feed_url)
        return []

    return entries

def build_article(entry, source: str, keyword: str):

    title = getattr(entry, "title", "").strip()
    link = getattr(entry, "link", "").strip()

    if not title or not link:
        return None

    parsed_date = parse_entry_date(entry)

    if not parsed_date:
        return None

    """Search best description possible"""
    summary = ""

    if getattr(entry, "content", None):
        summary = entry.content[0].value

    elif getattr(entry, "summary", None):
        summary = entry.summary

    elif getattr(entry, "description", None):
        summary = entry.description

    return {
        "title": title,
        "link": link,
        "summary": getattr(entry, "summary", ""),
        "published": format_datetime(parsed_date),
        "published_display": parsed_date.strftime("%d/%m/%Y %H:%M"),
        "source": source,
        "keyword": keyword,
        "parsed_date": parsed_date,
        "normalized_url": normalize_url(link),
    }

def extract_articles(
    feed_url: str,
    cutoff_date: datetime,
    custom_source_label: str,
    keyword: str,
    seen: set
) -> list:

    articles = []

    entries = fetch_feed(feed_url)

    for entry in entries:

        article = build_article(
            entry,
            custom_source_label,
            keyword
        )

        if not article:
            continue

        if article["parsed_date"] < cutoff_date:
            continue

        normalized_url = article.pop("normalized_url")

        if normalized_url in seen:
            continue

        seen.add(normalized_url)

        articles.append(article)

    return articles

def collect_articles(cutoff_date: datetime) -> list:

    all_articles = []
    seen = set()

    for source_info in SOURCE_RSS:

        articles = extract_articles(
            feed_url=source_info["url"],
            custom_source_label=source_info["label"],
            keyword=source_info["keyword"],
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

def prepare_rss_articles(articles):
    cleaned = []

    for a in articles:
        cleaned.append({
            "title": escape(a.get("title", "")),
            "link": escape(a.get("link", "")),
            "summary": a.get("summary", ""),
            "published": a.get("published", "")
        })

    return cleaned

def generate_rss(articles, now, output_path="docs/rss.xml"):
    template = ENV.get_template("rss.xml")

    rss = template.render(
        page_title=PAGE_TITLE,
        url=URL,
        last_build_date=format_datetime(now),
        articles=prepare_rss_articles(articles)
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rss)


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
    try:
        save_html(html)
        logging.info(
            "Collected %d articles - HTML created: docs/index.html",
            len(articles)
        )
    
    except Exception:
        logging.exception("Failed to save HTML")

    try:
        generate_rss(articles,now)
        logging.info(
            "Collected %d articles - RSS created: docs/rss.xml", 
            len(articles)
        )
    
    except Exception:
        logging.exception("Failed to create RSS")


if __name__ == "__main__":
    main()
