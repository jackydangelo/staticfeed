import feedparser
import logging
import requests
import json
import os

from datetime import datetime, timedelta, timezone
from collections.abc import Iterable, Iterator
from urllib.parse import urlsplit, urlunsplit
from jinja2 import Environment, FileSystemLoader, select_autoescape
from email.utils import format_datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from feedparser import FeedParserDict
from threading import Lock
from domain import Article, FeedSource, OutputConfig

from config import (
    SOURCE_RSS,
    DAYS_LIMIT,
    REQUEST_TIMEOUT,
    TIMEZONE,
    URL,
    PAGE_TITLE,
    FOOTER_TEXT,
    USER_AGENT,
    RETRY_CONFIG
)

# Shared Jinja environment reused across renders to leverage template caching.
ENV = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml", "xhtml"])
)

CACHE_FILE = "feed_cache.json"

CACHE: dict = {}
CACHE_LOCK = Lock()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

retry_strategy = Retry(**RETRY_CONFIG)

adapter = HTTPAdapter(
    max_retries=retry_strategy
)

SESSION = requests.Session()

SESSION.mount("https://", adapter)
SESSION.mount("http://", adapter)

SESSION.headers.update({
    "User-Agent": USER_AGENT
})

class TemplateRenderError(Exception):
    pass

def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            logger.warning("Unable to read the cache file; I'll create a new one.")
    return {}

def save_cache(cache_data: dict) -> None:
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=4)
    except Exception:
        logger.exception("Unable to save the cache file.")

def get_cutoff_date(now: datetime, days_limit: int) -> datetime:
    """
    Computes the lower bound timestamp used to filter outdated articles.
    """
    return now - timedelta(days=days_limit)


def parse_entry_date(entry: FeedParserDict) -> datetime | None:
    """
    Extracts a normalized publication datetime from an RSS entry
    using feedparser's parsed time structures.

    Returns None when the entry does not contain a valid or usable date.
    """

    # RSS feeds may provide either "published" or "updated" timestamps
    parsed_struct = (
        getattr(entry, "published_parsed", None)
        or getattr(entry, "updated_parsed", None)
    )

    if not parsed_struct:
        return None

    try:
        # This avoids local timezone ambiguity and ensures consistent comparison
        dt = datetime(
            parsed_struct.tm_year,
            parsed_struct.tm_mon,
            parsed_struct.tm_mday,
            parsed_struct.tm_hour,
            parsed_struct.tm_min,
            parsed_struct.tm_sec,
            tzinfo=timezone.utc
        )

        return dt.astimezone(TIMEZONE)

    except (ValueError, TypeError):
        logger.warning(
            "Impossible to extract date for: %s",
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
    Retrieves RSS entries from a remote feed source, leveraging HTTP caching (304 Not Modified).
    Returns an empty list if the feed is not modified, cannot be fetched, or is empty.
    """
    # 1. Load the current cache
    with CACHE_LOCK:
        feed_cache = CACHE.get(feed_url, {}).copy()

    # 2. Set up conditional headers
    headers = {}
    if "etag" in feed_cache:
        headers["If-None-Match"] = feed_cache["etag"]
    if "last_modified" in feed_cache:
        headers["If-Modified-Since"] = feed_cache["last_modified"]

    try:
        # Send the request including the cache headers (if any)
        response = SESSION.get(
            feed_url,
            timeout=REQUEST_TIMEOUT,
            headers=headers
        )

        # 3. Handling of 304 Not Modified
        if response.status_code == 304:
            logger.info("Unmodified feed (304): %s", feed_url)
            return []  

        response.raise_for_status()

        # 4. Handling new data
        feed = feedparser.parse(response.content)

    except requests.RequestException as exc:
        if hasattr(exc.response, 'status_code') and exc.response.status_code == 304:
            return []
            
        logger.exception("Failed to download feed: %s (%s)", feed_url, exc)
        return []

    if feed.bozo:
        logger.warning("Malformed feed: %s (%s)", feed_url, feed.bozo_exception)

    entries = getattr(feed, "entries", None)
    if not entries:
        logger.warning("Empty feed: %s", feed_url)
        return []

    # 5. Save the new cache data provided by the server for the next run
    new_etag = response.headers.get("ETag")
    new_last_modified = response.headers.get("Last-Modified")
    
    if new_etag or new_last_modified:
        with CACHE_LOCK:
            CACHE[feed_url] = {
                "etag": new_etag,
                "last_modified": new_last_modified
            }

    return entries

def process_source(source_info: FeedSource) -> list[Article]:
    """
    Download and normalize all articles from a single RSS feed.
    """
    logger.info(
        "Fetching: %s: %s", 
        source_info.label,
        source_info.keyword
    )    
    articles: list[Article] = []

    try:
        entries = fetch_feed(source_info.url)
        
        for entry in entries:
            article = build_article(
                entry,
                source_info.label,
                source_info.keyword
            )
            if article:
                articles.append(article)

        logger.info(
            "Fetched %d articles from %s: %s",
            len(articles),
            source_info.label,
            source_info.keyword
        )
        
    except Exception:
        # Prevent a single failing feed from breaking the entire orchestration loop.
        logger.exception(
            "Unexpected error processing source %s",
            source_info.label
        )
        return []

    return articles


def build_article(
    entry: FeedParserDict,
    source: str,
    keyword: str
) -> Article | None:
    """
    Builds a normalized article object from a raw RSS entry.

    Returns None if required fields are missing or invalid.
    """

    title = getattr(entry, "title", "").strip()
    link = getattr(entry, "link", "").strip()

    if not title or not link:
        return None

    published_at = parse_entry_date(entry)

    if not published_at:
        return None

    return Article(
        title=title,
        link=link,
        summary=getattr(entry, "summary", ""),
        source=source,
        keyword=keyword,
        published_at=published_at
    )


def stream_raw_articles() -> Iterator[Article]:
    """
    Retrieves and normalizes RSS entries concurrently with safe error handling.
    """
    max_workers = max(1, min(16, len(SOURCE_RSS)))

    with ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix="rss"
    ) as executor:

        futures = {
            executor.submit(process_source, source_info): source_info
            for source_info in SOURCE_RSS
        }

        for future in as_completed(futures):
            source_info = futures[future]
            try:
                yield from future.result()

            except Exception:
                logger.exception(
                    "Critical thread failure for %s",
                    source_info.label
                )         

def filter_by_date(
    articles: Iterable[Article],
    cutoff_date: datetime
) -> Iterator[Article]:
    """
    Filters out articles that are older than the specified cutoff date.
    """
    for article in articles:
        if article.published_at >= cutoff_date:
            yield article


def filter_duplicates(
    articles: Iterable[Article],
    seen_set: set[str]
) -> Iterator[Article]:
    """
    Removes duplicate articles from the stream based on their canonical URL.
    """
    for article in articles:
        # Generate the canonical URL for comparison
        url = normalize_url(article.link)

        if url not in seen_set:
            seen_set.add(url)
            yield article


def collect_articles(cutoff_date: datetime) -> list[Article]:
    """
    Produces the unified article dataset used by all output formats.

    This is the single source of truth for RSS ingestion and normalization.
    """
    seen: set[str] = set()

    raw_stream = stream_raw_articles()
    filtered_by_date = filter_by_date(raw_stream, cutoff_date)
    final_stream = filter_duplicates(filtered_by_date, seen)

    all_articles = list(final_stream)

    all_articles.sort(
        key=lambda article: article.published_at,
        reverse=True
    )

    return all_articles


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

    except FileNotFoundError as exc:
        logger.exception("Template not found: %s", template_name)
        raise TemplateRenderError("Missing template") from exc

    except OSError as exc:
        logger.exception("File write error: %s", output_path)
        raise TemplateRenderError("Cannot write output file") from exc

    except Exception as exc:
        logger.exception("Unexpected render error")
        raise TemplateRenderError("Render failed") from exc


def get_output_configuration(
    now: datetime,
    articles: list[Article]
) -> list[OutputConfig]:

    """
    Defines the supported output formats and their respective Jinja contexts.
    Easily extensible with new formats (e.g., JSON Feed, Sitemap).
    """

    formatted_now = now.strftime("%d/%m/%Y %H:%M")

    return [
        OutputConfig(
            template="homepage.html",
            path="docs/index.html",
            type_label="HTML home",
            content_count=len(articles),
            context={
                "page_title": PAGE_TITLE,
                "footer_text": FOOTER_TEXT,
                "updated_at": formatted_now,
                "articles": articles
            }
        ),
        OutputConfig(
            template="sources.html",
            path="docs/sources.html",
            type_label="HTML sources",
            content_count=len(SOURCE_RSS),
            context={
                "page_title": PAGE_TITLE,
                "footer_text": FOOTER_TEXT,
                "updated_at": formatted_now,
                "sources": SOURCE_RSS
            }
        ),
        OutputConfig(
            template="rss.xml",
            path="docs/rss.xml",
            type_label="RSS",
            content_count=len(articles),
            context={
                "page_title": PAGE_TITLE,
                "url": URL,
                "last_build_date": format_datetime(now),
                "articles": articles
            }
        )
    ]

def main():
    global CACHE

    CACHE = load_cache()
    
    now = datetime.now(TIMEZONE)

    cutoff_date = get_cutoff_date(
        now=now,
        days_limit=DAYS_LIMIT
    )

    # 1. Ingestion and normalization (Stream-based pipeline)
    articles = collect_articles(cutoff_date)
    num_articles = len(articles)

    logger.info(
        "Collected %d articles from %d RSS sources",
        num_articles,
        len(SOURCE_RSS)
    )

    # 2. Output generation (Data-Driven Architecture)
    outputs = get_output_configuration(now, articles)

    for output in outputs:
        try:
            render_template(
                template_name=output.template,
                output_path=output.path,
                **output.context
            )
    
            logger.info(
                "%s created: %s (%d items)",
                output.type_label,
                output.path,
                output.content_count
            )
    
        except TemplateRenderError:
            logger.error(
                "%s template rendering failed",
                output.type_label
            )
    save_cache(CACHE)

if __name__ == "__main__":
    main()
