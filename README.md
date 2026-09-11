# AI Daily Intelligence Agent

An end-to-end production-oriented agent that collects the latest AI developments, removes duplicates, ranks important stories, summarizes them with an LLM, and delivers a daily briefing by email and/or WhatsApp.

## Architecture

```text
RSS / APIs / trusted AI sources
        |
        v
   Ingestion layer
        |
        v
 Raw article normalization
        |
        v
 URL/content deduplication
        |
        v
 Relevance + ranking
        |
        v
 LLM synthesis
        |
        v
 Daily briefing
    /        \
 Email      WhatsApp
        |
        v
 Run metrics + logs
```

## Initial sources

- OpenAI News
- Google AI Blog
- Microsoft Research
- Hugging Face Blog
- Meta AI
- NVIDIA AI Blog
- arXiv AI/ML recent papers
- GitHub Trending AI/ML repositories

The source layer is deliberately modular so new RSS feeds, APIs, and scrapers can be added without changing the agent pipeline.

## Stack

- Python 3.11
- FastAPI
- feedparser / requests
- BeautifulSoup
- OpenAI API
- SQLite locally, PostgreSQL in production
- Docker
- GitHub Actions
- Azure Container Apps
- SMTP email delivery
- Twilio WhatsApp delivery

## Local development

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.api.main:app --reload --port 8000
```

Health check: `http://localhost:8000/health`

Run a briefing manually:

```bash
python -m app.jobs.daily_briefing
```

## Environment variables

See `.env.example`. Secrets are never committed to the repository.

## Daily schedule

The GitHub Actions workflow runs the briefing at **9:00 AM America/Toronto**. GitHub supports timezone-aware scheduled workflows, including IANA time zones. The workflow can also be dispatched manually for testing. citehttps://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

## Deployment

The application is containerized and designed for Azure Container Apps. Azure Container Apps supports deploying a public container image with `az containerapp up`; the final deployment will expose the FastAPI health endpoint for verification. citehttps://learn.microsoft.com/en-us/azure/container-apps/get-started

## Project status

This repository is being built incrementally from ingestion through production deployment. The first milestone establishes the ingestion, normalization, deduplication, ranking, summarization, delivery, tests, container, and scheduled workflow foundations.
