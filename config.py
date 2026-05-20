from zoneinfo import ZoneInfo

SOURCE_RSS =
    {
        "url": "https://news.google.com/rss/search?q=gamification", 
        "label": "Google News"
    },
    {
        "url": "https://news.google.com/rss/search?q=gamification&hl=it&gl=IT&ceid=IT:it", 
        "label": "Google News Italia"
    },
    {
        "url": "https://news.google.com/rss/search?q=gamified", 
        "label": "Google News"
    },
    {
        "url": "https://news.google.com/rss/search?q=gamificata&hl=it&gl=IT&ceid=IT:it", 
        "label": "Google News Italia"
    },
    {
        "url": "https://news.google.com/rss/search?q=gamificato&hl=it&gl=IT&ceid=IT:it", 
        "label": "Google News Italia"
    },
    {
        "url": "https://www.reddit.com/search.rss?q=gamification", 
        "label": "Reddit"
    }

DAYS_LIMIT = 30

TIMEZONE = ZoneInfo("Europe/Rome")

PAGE_TITLE = "Gamification News"

FOOTER_TEXT = (
    'Feed per temi di gamification. '
    'Parte del progetto "Questa è gamification!" '
    "di Giacomo D'angelo."
)
