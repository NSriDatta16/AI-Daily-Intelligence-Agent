# AI Signal Briefing

> A production-style GenAI intelligence pipeline that turns the last 24 hours of AI news into one focused daily briefing.

[![Tests](https://img.shields.io/github/actions/workflow/status/NSriDatta16/AI-Daily-Intelligence-Agent/tests.yml?label=tests&logo=github)](https://github.com/NSriDatta16/AI-Daily-Intelligence-Agent/actions)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/LLM-Gemini-4285F4)](https://ai.google.dev/)
[![GitHub Pages](https://img.shields.io/badge/Dashboard-GitHub%20Pages-222)](https://nsridatta16.github.io/AI-Daily-Intelligence-Agent/)

## Overview

AI moves faster than most people can realistically track. The challenge is not finding more information; it is separating meaningful developments from repetitive, low-value noise.

**AI Signal Briefing** is an end-to-end intelligence system designed to solve that problem. It collects recent AI developments from trusted feeds, applies deterministic data-quality and relevance logic, uses Gemini to synthesize the highest-value stories, persists historical intelligence, and publishes the result through an interactive dashboard and optional email delivery.

The system is intentionally designed as a pipeline rather than a simple LLM wrapper. Data ingestion, quality control, ranking, generation, persistence, delivery, testing, and deployment are separate concerns.

## Live Dashboard

**[Open AI Signal Briefing](https://nsridatta16.github.io/AI-Daily-Intelligence-Agent/)**

The dashboard provides:

- Executive daily briefing
- Ranked top stories with impact scores
- Search across stories, sources, and topics
- Category and source filtering
- Trending topics
- Source provenance
- Historical briefings
- Responsive desktop and mobile layouts
- Light and dark themes

## End-to-End Flow

```text
9:00 AM America/Toronto
        |
        v
GitHub Actions Scheduler
        |
        v
Python Intelligence Pipeline
        |
        v
RSS Ingestion
        |
        v
Time Filtering + Data Quality
        |
        v
Deduplication
        |
        v
Relevance / Impact Ranking
        |
        v
Gemini LLM Synthesis
        |
        +-------------------+
        |                   |
        v                   v
Historical JSON        Daily Delivery
        |               /          \
        |              /            \
        v             v              v
GitHub Pages       Email          WhatsApp
        |
        v
Searchable Intelligence Dashboard
```

## Architecture

```text
                         +----------------------+
                         | GitHub Actions       |
                         | Scheduled Trigger    |
                         | 9:00 AM              |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Python Application   |
                         +----------+-----------+
                                    |
                                    v
                  +----------------------------------+
                  |          Ingestion Layer         |
                  | RSS feeds from AI/news sources  |
                  +----------------+-----------------+
                                   |
                                   v
                  +----------------------------------+
                  |        Processing Layer          |
                  | Time window                     |
                  | Validation                      |
                  | Deduplication                   |
                  | Relevance / impact ranking      |
                  +----------------+-----------------+
                                   |
                                   v
                  +----------------------------------+
                  |         Intelligence Layer       |
                  | Gemini prompt + article context  |
                  | Daily briefing synthesis         |
                  +----------------+-----------------+
                                   |
                    +--------------+--------------+
                    |              |              |
                    v              v              v
              +-----------+  +-----------+  +------------+
              | JSON      |  | SMTP      |  | Dashboard  |
              | History   |  | Email     |  | GitHub     |
              +-----------+  +-----------+  | Pages      |
                                             +------------+
```

### Data flow

1. **Trigger** — GitHub Actions starts the scheduled production workflow.
2. **Ingest** — Python collects recent AI developments through RSS feeds.
3. **Filter** — Articles are restricted to the configured lookback window and invalid or future-dated timestamps are rejected.
4. **Deduplicate** — Repeated URLs and near-identical headlines are consolidated.
5. **Rank** — Stories are scored using relevance, impact, source authority, and freshness.
6. **Generate** — The highest-value stories are supplied to Gemini for briefing synthesis.
7. **Persist** — Articles, briefings, and analytics are stored as repository-backed JSON for durable dashboard history.
8. **Deliver** — The briefing can be delivered through email or WhatsApp, while the dashboard is published through GitHub Pages.

## Why This Is More Than an LLM Wrapper

A production GenAI application should not depend on the LLM to perform every part of the system.

This architecture separates deterministic engineering from probabilistic generation:

```text
External Sources
      |
      v
Ingestion
      |
      v
Data Quality
      |
      v
Deterministic Ranking
      |
      v
LLM Synthesis
      |
      v
Persistence
      |
      v
Delivery
      |
      v
User-facing Product
```

The LLM is responsible for synthesis and natural-language generation. The surrounding pipeline controls what information reaches the model, how information is prioritized, how results are stored, and how the final product is delivered.

The current implementation does **not** use a vector database or a conventional semantic-search RAG architecture. Retrieval is feed-based, followed by deterministic filtering and ranking before LLM generation.

## Technology Stack

| Layer | Technology | Responsibility |
|---|---|---|
| Application | Python 3.11 | Core pipeline and business logic |
| Ingestion | RSS, feedparser, requests, BeautifulSoup | Collect and normalize source content |
| Processing | Python | Filtering, validation, deduplication, ranking |
| GenAI | Google Gemini via google-genai | Briefing synthesis |
| Backend | FastAPI | Local/API application |
| Persistence | SQLite + JSON | Local state and durable history |
| Frontend | HTML, CSS, JavaScript | Intelligence dashboard |
| Automation | GitHub Actions | CI, scheduled processing, deployment |
| Hosting | GitHub Pages | Static dashboard hosting |
| Notifications | Gmail SMTP / Twilio WhatsApp | Briefing delivery |
| Packaging | Docker | Reproducible container execution |
| Testing | pytest | Automated validation |

## Automation and CI/CD

The repository separates software delivery from the recurring intelligence workload.

### Continuous Integration (CI)

When code changes, GitHub Actions installs the project dependencies and runs the automated test suite.

```text
Code Change
    |
    v
GitHub Actions
    |
    v
Install Dependencies
    |
    v
Run pytest
    |
    v
Validation
```

CI answers a simple engineering question:

> Did this code change break the application?

### Continuous Delivery / Deployment (CD)

The deployment workflow packages the dashboard and publishes it through GitHub Pages.

```text
Build
  |
  v
Create Pages Artifact
  |
  v
Deploy
  |
  v
GitHub Pages
```

CD answers:

> How do we move a validated application change into its target environment reliably?

### Scheduled Production Automation

The 9 AM workflow is not CI. It is scheduled application automation that executes the intelligence pipeline.

```text
9:00 AM
   |
   v
Collect -> Process -> Rank -> Gemini -> Persist
   |
   +------------------+
   |                  |
   v                  v
Email             Dashboard
```

This distinction is important: **CI/CD describes software integration and delivery, while the 9 AM schedule runs the application's recurring business workflow.**

## Project Structure

```text
.
├── .github/workflows/
│   ├── tests.yml              # CI: automated tests
│   ├── daily-briefing.yml     # Scheduled pipeline and Pages deployment
│   └── docker.yml             # Container build workflow
│
├── app/
│   ├── agent/
│   │   └── summarizer.py      # Gemini briefing generation
│   ├── ingestion/
│   │   └── rss.py             # RSS collection
│   ├── pipeline/
│   │   └── process.py         # Filtering, deduplication, ranking
│   ├── notifications/
│   │   ├── email.py           # SMTP delivery
│   │   └── whatsapp.py        # Twilio delivery
│   ├── storage/
│   │   ├── database.py        # Local persistence
│   │   └── analytics.py       # Dashboard analytics
│   ├── jobs/
│   │   └── publish_site.py    # End-to-end publishing job
│   └── api/
│       └── main.py            # FastAPI application
│
├── data/
│   ├── articles.json          # Article history
│   ├── briefings.json         # Briefing history
│   └── analytics.json         # Dashboard analytics
│
├── web/
│   └── index.html             # Dashboard UI
│
├── tests/                     # Automated tests
├── Dockerfile                 # Container image definition
├── requirements.txt           # Runtime dependencies
└── requirements-dev.txt       # Development/test dependencies
```

## Security

- Gemini credentials are stored in GitHub Actions Secrets.
- Email credentials are stored in GitHub Actions Secrets.
- Secrets are not committed to source control.
- The frontend never contains the Gemini API key.
- Authentication support exists in the FastAPI application for future protected deployments.
- The current GitHub Pages dashboard is a static public site.

## Configuration

Configuration is supplied through environment variables. See `.env.example` for the available settings.

Key settings include:

```text
GEMINI_API_KEY
GEMINI_MODEL
EMAIL_ENABLED
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
EMAIL_FROM
EMAIL_TO
DASHBOARD_URL
WHATSAPP_ENABLED
LOOKBACK_HOURS
MAX_ARTICLES
TOP_STORIES
```

## Testing

```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
```

The test suite covers pipeline behavior, dashboard publishing behavior, and authentication guards.

## Run Locally

```bash
pip install -r requirements.txt
cp .env.example .env
```

Configure the required environment variables and run:

```bash
PYTHONPATH=. python -m app.jobs.publish_site
```

To run the FastAPI application:

```bash
uvicorn app.api.main:app --reload
```

To run the containerized application:

```bash
docker build -t ai-signal-briefing .
docker run --env-file .env -p 8000:8000 ai-signal-briefing
```

## Engineering Concepts Demonstrated

- Event-driven and scheduled workflows
- ETL-style data processing
- RSS-based ingestion
- Data validation and quality control
- Deduplication strategies
- Deterministic relevance ranking
- Generative AI and LLM integration
- Prompt-driven synthesis
- Persistence and historical analytics
- Notification delivery
- Static web publishing
- CI/CD with GitHub Actions
- Automated testing
- Containerization with Docker
- Failure isolation and graceful degradation
- Secure secret management

## Roadmap

- Protected personal dashboard with Microsoft Entra ID
- Source health monitoring
- Article-level evidence and citations
- Semantic similarity for stronger deduplication
- Vector retrieval for a true RAG layer
- Personalized topic preferences
- Multi-user profiles
- Production WhatsApp delivery
- Pipeline observability and operational metrics

## Architecture in One Sentence

> **A scheduled, event-driven GenAI pipeline that ingests recent AI intelligence, applies deterministic data-quality and ranking logic, uses Gemini for synthesis, persists historical briefings, and delivers the result through email and a searchable dashboard.**

## License

This project is maintained as a personal engineering portfolio project.
