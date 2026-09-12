# My Daily AI Updates

An end-to-end AI intelligence agent that collects important AI developments from the previous 24 hours, removes duplicates, ranks stories, synthesizes a daily briefing with Gemini, persists historical intelligence, and publishes a calm, searchable dashboard on GitHub Pages.

## Live architecture

```text
Official / trusted AI RSS sources
            |
            v
       RSS ingestion
            |
            v
   Normalize + deduplicate
            |
            v
      Relevance ranking
            |
            v
      Gemini synthesis
            |
      +-----+------+
      |            |
      v            v
  Email/WhatsApp  JSON history
                     |
                     v
               GitHub Pages
                     |
                     v
            My Daily AI Updates
```

## What it does

- Collects AI news, research, model releases and open-source developments.
- Limits the intelligence window to the latest 24 hours by default.
- Rejects future-dated feed items caused by bad publisher timestamps.
- Deduplicates repeated URLs and near-identical headlines.
- Scores stories using relevance, impact, source authority and freshness.
- Uses Gemini to produce an evidence-grounded daily briefing.
- Stores up to 30 briefing snapshots and 500 recent articles in repository-backed JSON history.
- Publishes a responsive dashboard with search, category/source filters, impact scores, trending topics, source summaries, dark mode and briefing history.
- Optionally sends the briefing by SMTP email and Twilio WhatsApp.

## Dashboard

GitHub Pages is the hosting layer. The dashboard is completely static: GitHub Actions generates the data files and deploys them with the site.

The dashboard is designed as a daily-use product rather than an AI-generated landing page: quiet navigation, clear hierarchy, source provenance, restrained color, dense-but-readable story cards and a fast search/filter workflow.

The site does not expose the Gemini API key. The key is used only inside the GitHub Actions job through `GEMINI_API_KEY`.

## Stack

- Python 3.11
- FastAPI for the local/API version
- feedparser / requests / BeautifulSoup
- Google Gemini API via `google-genai`
- SQLite for local persistence
- Repository-backed JSON for durable GitHub Pages history
- GitHub Actions for daily orchestration
- GitHub Pages for static hosting
- SMTP email delivery
- Twilio WhatsApp delivery
- Docker for local/containerized execution
```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
```
