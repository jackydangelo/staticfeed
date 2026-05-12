<p align="center">
  <img src="https://img.shields.io/github/stars/jackydangelo/gamification-news?style=for-the-badge&logo=github&labelColor=1e293b&color=f59e0b" />
  
  <a href="https://makeapullrequest.com">
    <img src="https://img.shields.io/badge/PRs-Welcome-10b981?style=for-the-badge&logo=github&labelColor=1e293b" />
  </a>
</p>

# Gamification news
RSS feeder personale per tracciare notizie di gamification. Parte del progetto [Questa è gamification!](https://giacomification.substack.com/), newsletter su substack mensile.


## Esigenza
I feeder gratuiti non permettono di raccogliere informazioni filtrando per parole chiave. Per trarre ispirazione dai miei articoli cerco spesso online temi di gamification ed un aggregatore è ciò che desideravo.


## Sviluppo
Sviluppato con passione, curiosità e sfruttando quello che è chiamato vibe coding.
### Deploy
Il sito si auto-aggiorna attraverso una github action, ed è ospitato da una github page.
### Struttura del progetto
- `.github/workflow/update.yml` - Github action per refresh giornaliero
- `docs/index.html` - Html finale aggiornato dalla github action
- `docs/static/style.css` - Componente grafica e statica
- `templates/homepage.html` - Struttura dell'html compilato dal codice py
- `config.py` - Variabili di personalizzazione RSS
- `gamification_rss.py` - Codice Python eseguito una volta al giorno dalla github action
- `requirements.txt` - Librerie necessarie per eseguire il codice

## Fonte dati
| Parola chiave | URL feed | Fonte |
|---|---|---|
| gamification | [https://www.google.com/alerts/feeds/15244278077982194024/11541540114411201767](https://news.google.com/rss/search?q=gamification) | Google news |
| gamification | [https://www.google.com/alerts/feeds/15244278077982194024/10845276624304286453](https://news.google.com/rss/search?q=gamification&hl=it&gl=IT&ceid=IT:it) | Google news Italia |
| gamified | https://news.google.com/rss/search?q=gamified | Google news |
| gamificata |  https://news.google.com/rss/search?q=gamificata&hl=it&gl=IT&ceid=IT:it | Google news Italia |
| gamificato |  https://news.google.com/rss/search?q=gamificato&hl=it&gl=IT&ceid=IT:it | Google news Italia |
| gamification |  https://www.reddit.com/search.rss?q=gamification | Reddit |


## Utilizzo
Attraverso le variabili presenti nel file `config.py` il sito può essere personalizzato a proprio piacimento.


## Licenza
Progetto open source. Le PR sono benvenute, qualora siano migliorative. Aprire prima un'issue.
Chiunque voglia può riutilizzare il progetto creando un fork, è gradito se ci cita la fonte.
