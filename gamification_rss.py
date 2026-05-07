import feedparser
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

SOURCE_RSS = [
    "https://news.google.com/rss/search?q=gamification",
    "https://news.google.com/rss/search?q=gamification&hl=it&gl=IT&ceid=IT:it",
    "https://hnrss.org/newest?q=gamification"
]

all_entries = []
seen = set()

# limite ultimi 30 giorni
cutoff_date = datetime.now().astimezone() - timedelta(days=30)

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

            # filtra ultimi 30 giorni
            if parsed_date < cutoff_date:
                continue

            published = parsed_date.strftime("%d/%m/%Y %H:%M")

        except:
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

# ordina per data decrescente (più recente prima)
all_entries.sort(
    key=lambda x: x["parsed_date"],
    reverse=True
)

html = f"""
<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Gamification News</title>

<style>
body {{
    font-family: Arial, sans-serif;
    max-width: 900px;
    margin: 40px auto;
    padding: 20px;
    background: #f5f5f5;
}}

h1 {{
    color: #222;
}}

.article {{
    background: white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}}

.article a {{
    text-decoration: none;
    color: #1565c0;
}}

.article a:hover {{
    text-decoration: underline;
}}

.summary {{
    color: #555;
    margin-top: 10px;
}}

.meta {{
    font-size: 14px;
    color: #777;
    margin-bottom: 10px;
}}

.footer {{
    margin-top: 40px;
    color: #777;
    font-size: 14px;
}}
</style>

</head>
<body>

<h1>🎮 Gamification News</h1>

<p>Ultimo aggiornamento: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
"""

for article in all_entries:
    html += f"""
    <div class="article">

        <div class="meta">
            <strong>Fonte:</strong> {article['source']} |
            <strong>Data:</strong> {article['published']}
        </div>

        <h2>
            <a href="{article['link']}" target="_blank">
                {article['title']}
            </a>
        </h2>

        <div class="summary">
            {article['summary']}
        </div>
    </div>
    """

html += """
<div class="footer">
Feed aggregato automaticamente con Python.
</div>

</body>
</html>
"""

with open("gamification.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML generato: gamification.html")
