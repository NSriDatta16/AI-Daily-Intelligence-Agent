# AI Signal Briefing

> A production-style GenAI intelligence pipeline that turns the last 24 hours of AI news into a focused daily briefing.

[![Tests](https://img.shields.io/github/actions/workflow/status/NSriDatta16/AI-Daily-Intelligence-Agent/tests.yml?label=tests&logo=github)](https://github.com/NSriDatta16/AI-Daily-Intelligence-Agent/actions)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/LLM-Gemini-4285F4)](https://ai.google.dev/)
[![GitHub Pages](https://img.shields.io/badge/Dashboard-GitHub%20Pages-222)](https://nsridatta16.github.io/AI-Daily-Intelligence-Agent/)

## Overview

AI Signal Briefing is an end-to-end intelligence application that collects recent AI developments, filters and ranks the highest-value stories, uses Gemini to synthesize a daily briefing, persists historical intelligence, and publishes the result through a searchable dashboard with optional email delivery.

The system separates deterministic data processing from LLM generation. Ingestion, validation, deduplication, ranking, persistence, delivery, testing, and deployment are implemented as distinct components rather than placing the entire workflow behind a single LLM call.

## Live Dashboard

**[Open AI Signal Briefing](https://nsridatta16.github.io/AI-Daily-Intelligence-Agent/)**

The dashboard includes:

- Daily executive briefing
- Ranked stories with impact scores
- Search across stories, sources, and topics
- Category and source filtering
- Trending topics
- Source provenance
- Historical briefings
- Responsive desktop and mobile layouts
- Light and dark themes

## Architecture

```text
                         +----------------------+
                         | GitHub Actions       |
                         | Scheduled Trigger    |
                         | 9:00 AM Toronto      |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Python Pipeline      |
                         +----------+-----------+
                                    |
                                    v
                  +----------------------------------+
                  | Ingestion                        |
                  | RSS feeds / source normalization |
                  +----------------+-----------------+
                                   |
                                   v
                  +----------------------------------+
                  | Processing                       |
                  | Time filtering                   |
                  | Validation                       |
                  | Deduplication                    |
                  | Relevance / impact ranking       |
                  +----------------+-----------------+
                                   |
                                   v
                  +----------------------------------+
                  | GenAI Synthesis                  |
                  | Gemini + ranked article context  |
                  +----------------+-----------------+
                                   |
                    +--------------+--------------+
                    |              |              |
                    v              v              v
              +-----------+  +-----------+  +------------+
              | Historical|  | Email     |  | GitHub     |
              | Data      |  | Delivery  |  | Pages      |
              +-----------+  +-----------+  +------------+
                                                  |
                                                  v
                                      Searchable Dashboard
```

### Processing Flow

1. Collect recent articles from configured RSS sources.
2. Apply the configured time window and data-quality checks.
3. Deduplicate repeated URLs and similar headlines.
4. Rank stories using relevance, impact, source authority, and freshness.
5. Provide the highest-value stories and supporting context to Gemini.
6. Generate the daily briefing and structured dashboard data.
7. Persist historical articles, briefings, and analytics.
8. Deliver the briefing through configured notification channels and publish the dashboard.

## GenAI Design

The application uses Gemini for synthesis rather than delegating the entire pipeline to the model.

```text
Source Data
    |
    v
Deterministic Filtering
    |
    v
Deduplication
    |
    v
Relevance Ranking
    |
    v
Gemini Synthesis
    |
    v
Structured Briefing
```

This approach limits the model's input to higher-value information and keeps data-quality and prioritization logic deterministic and testable.

The current implementation uses feed-based retrieval and deterministic ranking. It does not currently use a vector database or conventional semantic-search RAG.

## Technology Stack

| Layer | Technology | Role |
|---|---|---|
| Application | Python 3.11 | Core application and pipeline |
| Ingestion | RSS, feedparser, requests, BeautifulSoup | Source collection and normalization |
| Processing | Python | Filtering, validation, deduplication, ranking |
| GenAI | Google Gemini via google-genai | Briefing synthesis |
| Backend | FastAPI | API and local application server |
| Persistence | SQLite + JSON | Local state and dashboard history |
| Frontend | HTML, CSS, JavaScript | Dashboard interface |
| Automation | GitHub Actions | Testing, scheduled processing, deployment |
| Hosting | GitHub Pages | Static dashboard hosting |
| Notifications | Gmail SMTP / Twilio WhatsApp | Briefing delivery |
| Packaging | Docker | Containerized execution |
| Testing | pytest | Automated validation |

## Automation and Deployment

GitHub Actions provides separate workflows for application validation, scheduled intelligence generation, and container builds.

- **Tests:** Automated pytest execution on repository changes.
- **Daily pipeline:** Scheduled execution at 9:00 AM America/Toronto to collect, process, synthesize, persist, and publish the daily briefing.
- **Pages deployment:** Generated dashboard artifacts are deployed to GitHub Pages.
- **Docker:** Container images are built through GitHub Actions for reproducible execution.

## Project Structure

```text
.
├── .github/workflows/
│   ├── tests.yml              # Automated test workflow
│   ├── daily-briefing.yml     # Scheduled intelligence pipeline
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

- API credentials are stored through GitHub Actions Secrets or environment variables.
- Secrets are not committed to source control.
- The frontend does not expose the Gemini API key.
- Authentication support is implemented in the FastAPI application for protected deployments.
- The current GitHub Pages dashboard is a static public site.

## Configuration

Runtime configuration is supplied through environment variables. See `.env.example` for the complete configuration surface.

Core settings include:

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

The test suite covers pipeline behavior, publishing behavior, and authentication guards.

## Local Development

```bash
pip install -r requirements.txt
cp .env.example .env
```

Configure the required environment variables and run the publishing job:

```bash
PYTHONPATH=. python -m app.jobs.publish_site
```

Run the FastAPI application:

```bash
uvicorn app.api.main:app --reload
```

Run with Docker:

```bash
docker build -t ai-signal-briefing .
docker run --env-file .env -p 8000:8000 ai-signal-briefing
```

## Engineering Scope

- Event-driven and scheduled processing
- RSS-based data ingestion
- Data validation and quality control
- URL and headline deduplication
- Deterministic relevance and impact ranking
- GenAI integration and prompt-based synthesis
- Historical persistence and analytics
- Notification delivery
- Static web publishing
- GitHub Actions automation
- Automated testing
- Docker containerization
- Failure isolation and graceful degradation
- Secret management

## Roadmap

- Protected personal dashboard with Microsoft Entra ID
- Source health monitoring
- Article-level evidence and citations
- Semantic similarity for stronger deduplication
- Vector retrieval for a RAG layer
- Personalized topic preferences
- Multi-user profiles
- Production WhatsApp delivery
- Pipeline observability and operational metrics

## Architecture Summary

> A scheduled GenAI pipeline that ingests recent AI developments, applies deterministic quality and ranking logic, synthesizes a focused briefing with Gemini, persists historical intelligence, and publishes it through a searchable dashboard and notification channels.

## License

This project is maintained as a personal engineering portfolio project.
