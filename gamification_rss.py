import feedparser

from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader

from config import (
    SOURCE_RSS,
    DAYS_LIMIT,
    TIMEZONE,
    PAGE_TITLE,
    FOOTER_TEXT
)

all_entries = []
seen = set()

# limite ultimi x giorni
cutoff_date = datetime.now().astimezone() - timedelta(days=DAYS_LIMIT)

for url in SOURCE_RSS:

    feed = feedparser.parse(url)

    # nome della fonte RSS
    source = getattr(feed.feed, "title", "Fonte sconosciuta")

    for entry in feed.entries:

        title = entry.title.strip()

        # evita duplicati
        if title in seen:
            continue

        # recupera data articolo
        raw_date = getattr(entry, "published", "")

        try:
            parsed_date = parsedate_to_datetime(raw_date)

            # filtra ultimi x giorni
            if parsed_date < cutoff_date:
                continue

            published = parsed_date.strftime("%d/%m/%Y %H:%M")

        except Exception:
            parsed_date = datetime.now().astimezone()
            published = "Data non disponibile"

        seen.add(title)

        all_entries.append({
            "title": title,
            "link": entry.link,
            "summary": getattr(entry, "summary", ""),
            "published": published,
            "source": source,
            "parsed_date": parsed_date,
        })

# ordina per data decrescente
all_entries.sort(
    key=lambda x: x["parsed_date"],
    reverse=True
)

# setup template engine
env = Environment(
    loader=FileSystemLoader("templates")
)

template = env.get_template("homepage.html")

html = template.render(
    page_title=PAGE_TITLE,
    footer_text=FOOTER_TEXT,
    updated_at=datetime.now()
        .astimezone(TIMEZONE)
        .strftime("%d/%m/%Y %H:%M"),
    articles=all_entries
)

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML generato: index.html")
