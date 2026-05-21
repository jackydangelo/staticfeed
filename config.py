from zoneinfo import ZoneInfo

SOURCE_RSS = [
    {
        "url": "https://news.google.com/rss/search?q=gamification", 
        "label": "Google News",
        "keyword": "gamification"
    },
    {
        "url": "https://news.google.com/rss/search?q=gamification&hl=it&gl=IT&ceid=IT:it", 
        "label": "Google News Italia",
        "keyword": "gamification" 
    },
    {
        "url": "https://news.google.com/rss/search?q=gamified", 
        "label": "Google News",
        "keyword": "gamified" 
    },
    {
        "url": "https://news.google.com/rss/search?q=gamificata&hl=it&gl=IT&ceid=IT:it", 
        "label": "Google News Italia",
        "keyword": "gamificata" 
    },
    {
        "url": "https://news.google.com/rss/search?q=gamificato&hl=it&gl=IT&ceid=IT:it", 
        "label": "Google News Italia",
        "keyword": "gamificato" 
    },
    {
        "url": "https://www.reddit.com/search.rss?q=gamification", 
        "label": "Reddit",
        "keyword": "gamification" 
    }
]

DAYS_LIMIT = 30

REQUEST_TIMEOUT = 20

TIMEZONE = ZoneInfo("Europe/Rome")

PAGE_TITLE = "Gamification News"

FOOTER_TEXT = (
    'Feed per temi di gamification. '
    'Parte del progetto "Questa è gamification!" '
    "di Giacomo D'angelo."
)
