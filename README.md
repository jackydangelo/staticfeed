<p align="center">
  <img src="https://img.shields.io/github/stars/jackydangelo/staticfeed?style=for-the-badge&logo=github&labelColor=000000&color=f59e0b" />
  <img src="https://img.shields.io/badge/PRs-Welcome-10b981?style=for-the-badge&logo=github&labelColor=000000" />
</p>

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


## Data Pipeline & Architecture

```text
RSS feeds
    ↓
GitHub Action (scheduled)
    ↓
config.py (typed configuration bridge)
    ↓
domain models (Article, FeedSource, OutputConfig)
    ↓
Python aggregation pipeline (app.py)
    ↓
stream processing (filtering, deduplication, sorting)
    ↓
Jinja template rendering
    ↓
Static HTML + RSS output
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


### Memory-Efficient Streaming

Unlike naive scrapers that load all data into memory, this pipeline processes articles as a continuous stream using Python generators (`yield`). This ensures a near-zero memory footprint even when scaling to dozens of high-traffic feeds.
The pipeline is structured as a domain-driven streaming system using typed models (Article, FeedSource) to ensure consistency across ingestion, processing, and rendering stages.


### Concurrency & High Performance

The pipeline utilizes Python's `ThreadPoolExecutor` to fetch and process multiple RSS feeds concurrently. Since network requests are highly I/O-bound, this architecture bypasses Python's Global Interpreter Lock (GIL) limitations. 

Instead of waiting for each feed to download sequentially, dozens of remote sources are queried in parallel within seconds. Additionally, the worker pool size dynamically auto-tunes based on your source count to prevent resource wasting or accidental rate-limiting.


### Smart Deduplication

The deduplication layer normalizes URLs to avoid duplicate articles across feeds.

It handles:

* trailing slashes
* casing normalization
* tracking query parameters
* duplicate Google News links


### Timezone-Aware Sorting

All timestamps are normalized into timezone-aware datetime objects using ```feedparser```'s native RFC-compliant time parsing and standard Python libraries. This ensures consistent chronological ordering across heterogeneous RSS and Atom feeds while keeping external dependencies to a strict minimum.

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

Open `config.json` and update the general settings or add your own RSS sources to the `SOURCE_RSS` array:

```json
{
  "DAYS_LIMIT": 7,
  "REQUEST_TIMEOUT": 20,
  "TIMEZONE_STR": "Europe/Rome",
  "URL": "https://your-username.github.io/staticfeed/",
  "PAGE_TITLE": "My Custom News",
  "FOOTER_TEXT": " have forked this repository!",
  "SOURCE_RSS": [
    {
      "url": "https://news.google.com/rss/search?q=your_keyword",
      "label": "Google News",
      "keyword": "your_keyword"
    }
  ]
}
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
config.json                    → RSS source configuration
templates/homepage.html        → HTML homepage template
templates/sources.html         → HTML sources template
templates/rss.xml              → RSS template

docs/index.html                → Generated static frontend
docs/sources.html              → Generated static page about sources
docs/rss.xml                   → Generated RSS feed
docs/static/style.css          → Frontend styling

app.py                         → Aggregation pipeline
config.py                      → Configuration loader (Python bridge)
domain.py                      → Domain models (Article, FeedSource, OutputConfig)
requirements.txt               → Python dependencies
```


## Technical Notes

The project intentionally prioritizes:

* simplicity
* portability
* inspectability
* forkability
* zero maintenance
* minimal external dependencies (relying on standard Python libraries wherever possible)


### Compatibility with Commercial Readers

This project is **not** intended to replace full-featured RSS platforms like Feedly, Inoreader, or Miniflux. 

Instead, it is designed to complement them. The unified `rss.xml` feed generated by this pipeline is fully standard-compliant and **ready to be added directly to Feedly, Inoreader, or any other RSS reader**. 

This allows you to use `StaticFeed` as a lightweight, zero-cost "pre-processing layer" to aggregate, filter, and deduplicate noisy web sources before reading them in your favorite RSS client.


## Current Data Sources (Gamification Tracking) 
| Keywords | URL feed | Source | 
|---|---|---| 
| gamification | https://news.google.com/rss/search?q=gamification | Google news | 
| gamification | https://news.google.com/rss/search?q=gamification&hl=it&gl=IT&ceid=IT:it | Google news Italia | 
| gamified | https://news.google.com/rss/search?q=gamified | Google news | 
| gamificata OR gamificato | https://news.google.com/rss/search?q=%22gamificata%22+OR+%22gamificato%22&hl=it&gl=IT&ceid=IT:it | Google news Italia | 
| gamificato |  https://news.google.com/rss/search?q=gamificato&hl=it&gl=IT&ceid=IT:it | Google news Italia | 
| gamification |  https://www.reddit.com/search.rss?q=gamification | Reddit |
| gamification |  https://hnrss.org/newest?q=gamification | Hacker News |


## Contributing

Pull Requests are welcome, especially for:

* performance improvements
* additional feed normalization strategies
* UI enhancements
* better deduplication logic
* caching support

Please open an issue first.


## License

Open source and free to fork, modify, and reuse.


