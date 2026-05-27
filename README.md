<p align="center">
  <img src="https://img.shields.io/github/stars/jackydangelo/gamification-news?style=for-the-badge&logo=github&labelColor=1e293b&color=f59e0b" />
  
  <a href="https://makeapullrequest.com">
    <img src="https://img.shields.io/badge/PRs-Welcome-10b981?style=for-the-badge&logo=github&labelColor=1e293b" />
  </a>
</p>

# Gamification news
A self-hosted, **zero-cost**, and automated RSS aggregator and static site generator. 

This project is part of the ["Questa è Gamification!"](https://giacomification.substack.com/) monthly newsletter on Substack, used to track and curate industry trends without algorithmic manipulation.


## The Need

Most commercial RSS readers (like Feedly or Inoreader) lock advanced features—such as combining multiple feeds, filtering by specific keywords, or advanced deduplication—behind expensive premium tiers. 

This project solves that by providing a **lightweight, open-source alternative** that handles multi-source tracking for specific niches with zero infrastructure costs.

## Features

* **Zero Infrastructure / Zero Cost:** No databases, no cron jobs, and no VPS to maintain. It runs entirely via GitHub Actions and is hosted for free on GitHub Pages.
* **Smart Deduplication:** URL normalization handles trailing slashes, casing, and query parameters to ensure you never see the same article twice, even across different sources.
* **Timezone Aware:** Accurate chronological sorting by processing multi-source feeds using Python's modern `zoneinfo`.
* **Dual Output:** Generates both a clean, mobile-friendly [Static HTML Frontend](https://jackydangelo.github.io/gamification-news/) and a unified, escaped [RSS XML Feed](https://jackydangelo.github.io/gamification-news/rss.xml) ready for external feeders.


## Quick Start: Build Your Own Aggregator in 2 Minutes

You can easily fork this repository to track **any niche or keywords** you want (e.g., AI, Rust, Indie Hacking).

1. **Fork this repository** to your GitHub account by clicking the **Fork** button at the top right of this page.
2. **Customize your sources:** Open and edit the `config.py` file directly on GitHub (or locally) to add your own RSS URLs, keywords, and metadata:
   ```python
   SOURCE_RSS = [
       {
           "url": "[https://news.google.com/rss/search?q=your_keyword](https://news.google.com/rss/search?q=your_keyword)", 
           "label": "Google News", 
           "keyword": "your_keyword"
       }
   ]
   DAYS_LIMIT = 7  # Keep only articles from the last X days


## Project Structure
- `.github/workflow/update.yml` - GitHub Action for daily refresh
- `docs/index.html` - Final HTML updated by the GitHub Action
- `docs/rss.xml` - RSS updated by the GitHub Action (ready for external feeder)
- `docs/static/style.css` - Graphical and static component
- `templates/homepage.html` - Structure of the HTML compiled by the Python code
- `templates/rss.xml` - Structure of the RSS compiled by the Python code
- `config.py` - RSS customization variables
- `gamification_rss.py` - Python code executed once a day by the GitHub Action
- `requirements.txt` - Libraries required to run the code

## Current Data Sources (Gamification Tracking)
| Keywords | URL feed | Source |
|---|---|---|
| gamification | [https://www.google.com/alerts/feeds/15244278077982194024/11541540114411201767](https://news.google.com/rss/search?q=gamification) | Google news |
| gamification | [https://www.google.com/alerts/feeds/15244278077982194024/10845276624304286453](https://news.google.com/rss/search?q=gamification&hl=it&gl=IT&ceid=IT:it) | Google news Italia |
| gamified | https://news.google.com/rss/search?q=gamified | Google news |
| gamificata |  https://news.google.com/rss/search?q=gamificata&hl=it&gl=IT&ceid=IT:it | Google news Italia |
| gamificato |  https://news.google.com/rss/search?q=gamificato&hl=it&gl=IT&ceid=IT:it | Google news Italia |
| gamification |  https://www.reddit.com/search.rss?q=gamification | Reddit |


## License
This is an open-source project. Pull Requests are highly welcome for performance improvements or UI enhancements. Please open an issue first to discuss major changes.
Anyone is free to fork, modify, and reuse this project. A citation or link back to the source is appreciated!
