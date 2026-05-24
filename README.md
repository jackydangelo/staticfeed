<p align="center">
  <img src="https://img.shields.io/github/stars/jackydangelo/gamification-news?style=for-the-badge&logo=github&labelColor=1e293b&color=f59e0b" />
  
  <a href="https://makeapullrequest.com">
    <img src="https://img.shields.io/badge/PRs-Welcome-10b981?style=for-the-badge&logo=github&labelColor=1e293b" />
  </a>
</p>

# Gamification news
Personal RSS feed for tracking gamification news. Part of the ["Questa è Gamification!"](https://giacomification.substack.com/) project, a monthly newsletter on Substack.


## Need
Free feeders do not allow you to collect information by filtering by keywords. To get inspiration for my articles, I often search online for gamification topics, and an aggregator is exactly what I wanted.


## Development
Developed with passion, curiosity, and by taking advantage of what is called vibe coding.
### Deploy
The site auto-updates through a GitHub Action and is hosted by a GitHub Page.
### Output
The program generate two files: a [static HTML](https://jackydangelo.github.io/gamification-news/) and a [RSS file](https://jackydangelo.github.io/gamification-news/rss) for feeder.
### Project Structure
- `.github/workflow/update.yml` - GitHub Action for daily refresh
- `docs/index.html` - Final HTML updated by the GitHub Action
- `docs/rss.xml` - RSS updated by the GitHub Action (ready for external feeder)
- `docs/static/style.css` - Graphical and static component
- `templates/homepage.html` - Structure of the HTML compiled by the Python code
- `templates/rss.xml` - Structure of the RSS compiled by the Python code
- `config.py` - RSS customization variables
- `gamification_rss.py` - Python code executed once a day by the GitHub Action
- `requirements.txt` - Libraries required to run the code

## Data Source
| Keywords | URL feed | Source |
|---|---|---|
| gamification | [https://www.google.com/alerts/feeds/15244278077982194024/11541540114411201767](https://news.google.com/rss/search?q=gamification) | Google news |
| gamification | [https://www.google.com/alerts/feeds/15244278077982194024/10845276624304286453](https://news.google.com/rss/search?q=gamification&hl=it&gl=IT&ceid=IT:it) | Google news Italia |
| gamified | https://news.google.com/rss/search?q=gamified | Google news |
| gamificata |  https://news.google.com/rss/search?q=gamificata&hl=it&gl=IT&ceid=IT:it | Google news Italia |
| gamificato |  https://news.google.com/rss/search?q=gamificato&hl=it&gl=IT&ceid=IT:it | Google news Italia |
| gamification |  https://www.reddit.com/search.rss?q=gamification | Reddit |


## Usage
Through the variables present in the `config.py` file, the site can be customized to your liking.


## License
Open source project. PRs are welcome, provided they are improvements. Please open an issue first.
Anyone who wants to can reuse the project by creating a fork; a citation of the source is appreciated.
