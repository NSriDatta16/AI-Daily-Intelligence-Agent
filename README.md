# AI Daily Intelligence Agent

An end-to-end AI intelligence agent that collects important AI developments from the previous 24 hours, removes duplicates, ranks stories, synthesizes a daily briefing with Gemini, persists historical intelligence, and publishes a searchable dashboard on GitHub Pages.

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
            Intelligence dashboard
```

## What it does

- Collects AI news, research, model releases and open-source developments.
- Limits the intelligence window to the latest 24 hours by default.
- Deduplicates repeated URLs and near-identical headlines.
- Scores stories using relevance, impact, source authority and freshness.
- Uses Gemini to produce an evidence-grounded daily briefing.
- Stores up to 30 briefing snapshots and 500 recent articles in repository-backed JSON history.
- Publishes a static dashboard with search, category/source filters, story scores, trending topics and briefing history.
- Optionally sends the briefing by SMTP email and Twilio WhatsApp.

## Dashboard

GitHub Pages is the hosting layer. The dashboard is completely static: GitHub Actions generates the data files and deploys them with the site.

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

## Automation

The daily intelligence workflow runs at **9:00 AM America/Toronto** and can also be started manually from GitHub Actions. Normal code pushes do not trigger the Gemini briefing workflow, preventing unnecessary model calls and notification noise.

The workflow commits the generated historical JSON back to the repository using `GITHUB_TOKEN`. GitHub's workflow model prevents events created with `GITHUB_TOKEN` from recursively starting another workflow run.

## Local development

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.api.main:app --reload --port 8000
```

Health check: `http://localhost:8000/health`

Run the daily pipeline locally:

```bash
PYTHONPATH=. python -m app.jobs.publish_site
```

## Optional notifications

Email and WhatsApp are disabled by default. Enable them through environment variables only after configuring the required SMTP or Twilio credentials. Never commit credentials to the repository.

## Tests

```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
```
