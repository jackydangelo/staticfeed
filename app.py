import feedparser
import logging
import requests

from datetime import datetime, timedelta
from urllib.parse import urlsplit, urlunsplit
from jinja2 import Environment, FileSystemLoader
from xml.sax.saxutils import escape
from dateutil.parser import parse as parse_date, ParserError
from email.utils import format_datetime

from config import (
    SOURCE_RSS,
    DAYS_LIMIT,
    REQUEST_TIMEOUT,
    TIMEZONE,
    URL,
    PAGE_TITLE,
    FOOTER_TEXT,
    USER_AGENT
)

# Shared Jinja environment reused across renders to leverage template caching.
ENV = Environment(
    loader=FileSystemLoader("templates")
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

SESSION = requests.Session()

SESSION.headers.update({
    "User-Agent": USER_AGENT
})

class TemplateRenderError(Exception):
    pass

def get_cutoff_date(now: datetime, days_limit: int) -> datetime:
    """
    Computes the lower bound timestamp used to filter outdated articles.
    """
    return now - timedelta(days=days_limit)


def parse_entry_date(entry) -> datetime | None:
    """
    Extracts a normalized publication datetime from an RSS entry.

    Returns None when the entry does not contain a valid or parsable date.
    """
    raw_date = (
        getattr(entry, "published", None)
        or getattr(entry, "updated", None)
    )

    if not raw_date:
        return None

    try:
        return parse_date(raw_date).astimezone(TIMEZONE)

    except (ValueError, TypeError, ParserError):
        logger.warning(
            "Invalid date format: %r for entry: %s",
            raw_date,
            getattr(entry, "title", "N/A")
        )
        return None


def normalize_url(url: str) -> str:
    """
    Produces a canonical URL used for article deduplication.
    """
    parts = urlsplit(url)

    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        parts.path.rstrip("/"),
        "",
        ""
    ))


def fetch_feed(feed_url: str):
    """
    Retrieves RSS entries from a remote feed source.

    Returns an empty list if the feed cannot be fetched or parsed.
    """
    
    try:
        response = SESSION.get(
            feed_url,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        feed = feedparser.parse(
            response.content
        )

    except requests.RequestException:
        logger.exception(
            "Failed to download feed: %s",
            feed_url
        )
        return []

    if feed.bozo:
        logger.warning(
            "Malformed feed: %s (%s)",
            feed_url,
            feed.bozo_exception
        )

    entries = getattr(feed, "entries", None)

    if not entries:
        logger.warning(
            "Empty feed: %s",
            feed_url
        )
        return []

    return entries


def build_article(entry, source: str, keyword: str):
    """
    Builds a normalized article object from a raw RSS entry.

    Returns None if required fields are missing or invalid.
    """
    
    title = getattr(entry, "title", "").strip()
    link = getattr(entry, "link", "").strip()

    if not title or not link:
        return None

    parsed_date = parse_entry_date(entry)

    if not parsed_date:
        return None

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
    """
    Extracts valid articles from a single RSS feed.

    Applies global consistency rules:
    - removes outdated entries
    - removes duplicates across all feeds
    - normalizes article structure
    """
    articles = []

    for entry in fetch_feed(feed_url):

        article = build_article(
            entry,
            custom_source_label,
            keyword
        )

        if (
            not article
            or article["parsed_date"] < cutoff_date
        ):
            continue

        normalized_url = article.pop("normalized_url")

        if normalized_url in seen:
            continue

        seen.add(normalized_url)

        articles.append(article)

    return articles


def collect_articles(cutoff_date: datetime) -> list:
    """
    Produces the unified article dataset used by all output formats.

    This is the single source of truth for RSS ingestion and normalization.
    """
    
    all_articles = []
    seen = set()

    for source_info in SOURCE_RSS:

        all_articles.extend(
            extract_articles(
                feed_url=source_info["url"],
                custom_source_label=source_info["label"],
                keyword=source_info["keyword"],
                cutoff_date=cutoff_date,
                seen=seen
            )
        )

    all_articles.sort(
        key=lambda x: x["parsed_date"],
        reverse=True
    )

    # Remove internal field used only for sorting.
    for article in all_articles:
        article.pop("parsed_date", None)

    return all_articles


def prepare_rss_articles(articles):
    """
    Prepares article data for RSS output by sanitizing fields
    and ensuring XML-safe content.
    """
    return [
        {
            "title": escape(a.get("title", "")),
            "link": escape(a.get("link", "")),
            "summary": escape(a.get("summary", "")),
            "published": a.get("published", "")
        }
        for a in articles
    ]


def render_template(
    template_name: str,
    output_path: str,
    **context
) -> None:
    """
    Renders a Jinja template and writes the result to disk.
    """
    try:
        template = ENV.get_template(template_name)
    
        content = template.render(**context)
    
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    except FileNotFoundError as e:
        logger.exception("Template not found: %s", template_name)
        raise TemplateRenderError("Missing template") from e

    except OSError as e:
        logger.exception("File write error: %s", output_path)
        raise TemplateRenderError("Cannot write output file") from e

    except Exception as e:
        logger.exception("Unexpected render error")
        raise TemplateRenderError("Render failed") from e


def main():

    now = datetime.now().astimezone()

    cutoff_date = get_cutoff_date(
        now=now,
        days_limit=DAYS_LIMIT
    )

    articles = collect_articles(cutoff_date)

    try:
        render_template(
            template_name="homepage.html",
            output_path="docs/index.html",
            page_title=PAGE_TITLE,
            footer_text=FOOTER_TEXT,
            updated_at=now.astimezone(TIMEZONE).strftime("%d/%m/%Y %H:%M"),
            articles=articles
        )

        logger.info(
            "Collected %d articles - HTML created: docs/index.html",
            len(articles)
        )

    except TemplateRenderError:
        logger.error("HTML template rendering failed") 

    try:
        render_template(
            template_name="rss.xml",
            output_path="docs/rss.xml",
            page_title=PAGE_TITLE,
            url=URL,
            last_build_date=format_datetime(now),
            articles=prepare_rss_articles(articles)
        )

        logger.info(
            "Collected %d articles - RSS created: docs/rss.xml",
            len(articles)
        )

    except TemplateRenderError:
        logger.error("RSS template rendering failed") 


if __name__ == "__main__":
    main()
