<p align="center"> <img src="https://img.shields.io/github/stars/jackydangelo/gamification-news?style=for-the-badge&logo=github&labelColor=1e293b&color=f59e0b" /> <a href="https://makeapullrequest.com"> <img src="https://img.shields.io/badge/PRs-Welcome-10b981?style=for-the-badge&logo=github&labelColor=1e293b" /> </a> </p>

# Zero-Cost RSS Aggregator

A zero-cost RSS aggregation pipeline that runs entirely on GitHub Actions + GitHub Pages.

This repository fetches multiple RSS feeds, deduplicates and sorts articles, then generates both a static HTML website and a unified RSS feed.

No servers, databases, cron jobs, or paid services required.

The current demo tracks gamification-related news, but the repository is intentionally designed to be forked for any niche or topic.


## Why This Exists

Most RSS readers and monitoring platforms lock useful features behind expensive plans:

- keyword tracking
- multi-source aggregation
- feed merging
- filtering
- deduplication
- custom pipelines

I wanted a simpler alternative that:

- runs entirely on the GitHub free tier
- requires zero infrastructure maintenance
- is easy to fork and customize
- outputs static files instead of relying on a backend


## Architecture

```text
RSS feeds
    ↓
GitHub Action (daily)
    ↓
Python aggregation
    ↓
Deduplication + sorting
    ↓
Jinja template rendering
    ↓
Static HTML + RSS
    ↓
GitHub Pages
````

No VPS, Docker, Redis, Postgres, or external schedulers.


## Features

### Zero Infrastructure

Everything runs on GitHub's free tier:

* GitHub Actions → scheduled updates
* GitHub Pages → static hosting
* Python → aggregation pipeline
* Jinja → static rendering

No backend services required.


### Smart Deduplication

The deduplication layer normalizes URLs to avoid duplicate articles across feeds.

It handles:

* trailing slashes
* casing normalization
* tracking query parameters
* duplicate Google News links


### Timezone-Aware Sorting

Articles from different feeds are normalized using Python's `zoneinfo` support to ensure accurate chronological ordering.


### Dual Output

The pipeline generates:

* a static HTML frontend
* a unified RSS XML feed

This makes the project usable both as a standalone website and as a source for external RSS readers.


## Demo

* Static website: https://jackydangelo.github.io/staticfeed/
* RSS feed: https://jackydangelo.github.io/staticfeed/rss.xml


## Build Your Own RSS Tracker

You can fork this repository to monitor any niche:

* AI
* cybersecurity
* startups
* indie hacking
* Rust
* gaming
* finance
* scientific research
* custom Google News searches

### 1. Fork the repository

Click the **Fork** button on GitHub.


### 2. Configure your feeds

Edit `config.py`:

```python
SOURCE_RSS = [
    {
        "url": "https://news.google.com/rss/search?q=your_keyword",
        "label": "Google News",
        "keyword": "your_keyword"
    }
]

DAYS_LIMIT = 7
```


### 3. Enable GitHub Pages

Go to:

```text
Settings → Pages
```

Then:

* Source → Deploy from a branch
* Branch → `main`
* Folder → `/docs`

Save the configuration.


### 4. Enable GitHub Actions

Open the `Actions` tab and enable workflows.

The pipeline will now automatically refresh based on the cron schedule defined in:

```text
.github/workflows/update.yml
```


## Example Runtime

Typical GitHub Action execution:

* dozens of RSS feeds
* hundreds of aggregated articles
* a few seconds runtime
* static output only


## Project Structure

```text
.github/workflows/update.yml   → Scheduled GitHub Action
config.py                      → RSS source configuration
templates/homepage.html        → HTML template
templates/rss.xml              → RSS template

docs/index.html                → Generated static frontend
docs/rss.xml                   → Generated RSS feed
docs/static/style.css          → Frontend styling

gamification_rss.py            → Aggregation pipeline
requirements.txt               → Python dependencies
```


## Technical Notes

The project intentionally prioritizes:

* simplicity
* portability
* inspectability
* forkability
* zero maintenance

It is not intended to compete with full-featured RSS platforms like Feedly, Inoreader, or Miniflux.

The goal is to provide a lightweight, hackable, self-hosted aggregation pipeline with minimal operational complexity.


## Current Data Sources (Gamification Tracking) 
| Keywords | URL feed | Source | 
|---|---|---| 
| gamification | [https://www.google.com/alerts/feeds/15244278077982194024/11541540114411201767](https://news.google.com/rss/search?q=gamification) | Google news | 
| gamification | [https://www.google.com/alerts/feeds/15244278077982194024/10845276624304286453](https://news.google.com/rss/search?q=gamification&hl=it&gl=IT&ceid=IT:it) | Google news Italia | 
| gamified | https://news.google.com/rss/search?q=gamified | Google news | 
| gamificata |  https://news.google.com/rss/search?q=gamificata&hl=it&gl=IT&ceid=IT:it | Google news Italia | 
| gamificato |  https://news.google.com/rss/search?q=gamificato&hl=it&gl=IT&ceid=IT:it | Google news Italia | 
| gamification |  https://www.reddit.com/search.rss?q=gamification | Reddit |


## Contributing

Pull Requests are welcome, especially for:

* performance improvements
* additional feed normalization strategies
* UI enhancements
* better deduplication logic
* caching support

For major changes, please open an issue first.


## License

Open source and free to fork, modify, and reuse.


