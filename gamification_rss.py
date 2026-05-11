import feedparser

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader

from config import (
    SOURCE_RSS,
    DAYS_LIMIT,
    TIMEZONE,
    PAGE_TITLE,
    FOOTER_TEXT
)


def get_cutoff_date(now: datetime, days_limit: int) -> datetime:
    """Restituisce la data limite per filtrare gli articoli."""
    return now - timedelta(days=days_limit)


def parse_entry_date(entry) -> datetime | None:
    """Converte la data dell'articolo in datetime timezone-aware."""

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
        print("Errore parsing data:", getattr(entry, "title", "N/A"), e)
        return None


def extract_articles(
    feed_url: str,
    cutoff_date: datetime,
    seen: set
) -> list:

    articles = []

    feed = feedparser.parse(feed_url)

    source = getattr(feed.feed, "title", "Fonte sconosciuta")

    for entry in feed.entries:

        title = entry.title.strip()

        if title in seen:
            continue

        parsed_date = parse_entry_date(entry)

        if not parsed_date:
            continue

        if parsed_date < cutoff_date:
            continue

        seen.add(title)

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
            feed_url=url,
            cutoff_date=cutoff_date,
            seen=seen
        )

        all_articles.extend(articles)

    all_articles.sort(
        key=lambda x: x["parsed_date"],
        reverse=True
    )

    return all_articles


def render_html(
    articles: list,
    now: datetime
) -> str:

    env = Environment(
        loader=FileSystemLoader("templates")
    )

    template = env.get_template("homepage.html")

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

    print("HTML generato: docs/index.html")


if __name__ == "__main__":
    main()
