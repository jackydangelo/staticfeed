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

all_entries = []
seen = set()

now = datetime.now().astimezone()
# limite ultimi x giorni
cutoff_date = now - timedelta(days=DAYS_LIMIT)


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
        raw_parsed = (
            getattr(entry, "published_parsed", None)
            or getattr(entry, "updated_parsed", None)
        )

        try:

            # nessuna data -> scarta articolo
            if not raw_parsed:
                continue

            parsed_date = datetime(
                *raw_parsed[:6],
                tzinfo=ZoneInfo("UTC")
            ).astimezone()

            # filtra ultimi x giorni
            if parsed_date < cutoff_date:
                continue

            published = parsed_date.strftime("%d/%m/%Y %H:%M")

        except Exception as e:

            print("Errore parsing data:", title, e)

            # data non valida -> scarta
            continue

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
    updated_at=now
        .astimezone(TIMEZONE)
        .strftime("%d/%m/%Y %H:%M"),
    articles=all_entries
)

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML generato: index.html")
