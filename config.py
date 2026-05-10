from zoneinfo import ZoneInfo

SOURCE_RSS = [
    "https://news.google.com/rss/search?q=gamification",
    "https://news.google.com/rss/search?q=gamification&hl=it&gl=IT&ceid=IT:it"
    "https://news.google.com/rss/search?q=gamified",
    "https://news.google.com/rss/search?q=gamificata&hl=it&gl=IT&ceid=IT:it"
    "https://news.google.com/rss/search?q=gamificato&hl=it&gl=IT&ceid=IT:it"
    "https://www.reddit.com/search.rss?q=gamification"
]

DAYS_LIMIT = 30

TIMEZONE = ZoneInfo("Europe/Rome")

PAGE_TITLE = "Gamification News"

FOOTER_TEXT = (
    'Feed per temi di gamification. '
    'Parte del progetto "Questa è gamification!" '
    "di Giacomo D'angelo."
)
