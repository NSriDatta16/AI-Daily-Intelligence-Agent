# AI Signal Briefing

> **A production-style GenAI intelligence pipeline that turns the last 24 hours of AI news into one focused daily briefing.**

[![Tests](https://img.shields.io/github/actions/workflow/status/NSriDatta16/AI-Daily-Intelligence-Agent/tests.yml?label=tests&logo=github)](https://github.com/NSriDatta16/AI-Daily-Intelligence-Agent/actions)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/LLM-Gemini-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![GitHub Pages](https://img.shields.io/badge/Dashboard-GitHub%20Pages-222?logo=github)](https://nsridatta16.github.io/AI-Daily-Intelligence-Agent/)

## What is AI Signal Briefing?

AI moves too fast to follow everything.

**AI Signal Briefing is a personal AI intelligence system that does the filtering for you.** It continuously turns noisy streams of AI news into a concise, evidence-grounded briefing you can read in minutes.

Every morning, the system:

```text
⏰  9:00 AM
     │
     ▼
📰  Collect the latest AI developments
     │
     ▼
🧹  Filter the last 24 hours + remove duplicates
     │
     ▼
🎯  Rank stories by relevance, impact, authority & freshness
     │
     ▼
🤖  Gemini synthesizes the highest-value stories
     │
     ▼
💾  Persist articles, briefings & analytics
     │
     ├───────────────┐
     ▼               ▼
📧 Email          🌐 Dashboard
```

The result is a **daily intelligence layer**, not just another news scraper.

## 🚀 Live Dashboard

**[Open AI Signal Briefing →](https://nsridatta16.github.io/AI-Daily-Intelligence-Agent/)**

The dashboard is designed for repeated daily use, with:

- Executive briefing at a glance
- Top stories with impact scores
- Search across stories, sources and topics
- Category and source filtering
- Trending topics
- Source summaries and provenance
- Historical briefings
- Dark/light mode
- Responsive desktop and mobile experience

---

## 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │   GitHub Scheduler   │
                         │       9:00 AM        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Python Pipeline    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │        RSS INGESTION         │
                    │  Trusted AI/news sources    │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │      DATA PROCESSING         │
                    │  Time filter → deduplicate  │
                    │  → relevance/impact ranking │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │       GEMINI SYNTHESIS       │
                    │  Context → reasoning →       │
                    │       daily briefing        │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              ┌──────────┐  ┌────────────┐  ┌─────────────┐
              │  JSON    │  │   Email    │  │  Dashboard  │
              │ History  │  │   SMTP     │  │ GitHub Pages│
              └──────────┘  └────────────┘  └─────────────┘
```

### The data flow

**1. Trigger** → GitHub Actions starts the scheduled production job.

**2. Ingest** → Python collects AI developments through RSS feeds.

**3. Filter** → Articles are restricted to the configured intelligence window and invalid/future timestamps are rejected.

**4. Deduplicate** → Repeated URLs and near-identical headlines are consolidated.

**5. Rank** → Stories are scored using relevance, impact, source authority and freshness.

**6. Generate** → The highest-value stories are passed to Gemini to create the daily briefing.

**7. Persist** → Articles, briefings and analytics are stored as repository-backed JSON for the static dashboard history.

**8. Deliver** → The briefing can be delivered through email/WhatsApp while the dashboard is published to GitHub Pages.

---

## 🧠 Why this is more than an LLM wrapper

The LLM is only **one component** of the system.

The project demonstrates an end-to-end intelligence workflow:

```text
External data
     ↓
Ingestion
     ↓
Data quality
     ↓
Deterministic ranking
     ↓
LLM synthesis
     ↓
Persistence
     ↓
Delivery
     ↓
User-facing product
```

This separation matters because the system does not simply ask an LLM to "tell me today's AI news." It first builds a controlled set of recent source material, applies deterministic processing, and then uses the model for synthesis.

There is **no vector database or classic semantic-search RAG layer** in the current architecture. Retrieval is feed-based and ranking is deterministic before generation.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.11 | Core application and pipeline |
| Ingestion | RSS, `feedparser`, `requests`, BeautifulSoup | Collect and normalize external content |
| Processing | Python | Filtering, deduplication and ranking |
| GenAI | Google Gemini via `google-genai` | Briefing synthesis |
| Backend | FastAPI | Local/API application |
| Persistence | SQLite + JSON | Local state and durable dashboard history |
| Automation | GitHub Actions | CI, scheduled pipeline and deployment |
| Frontend | HTML/CSS/JavaScript | Interactive dashboard |
| Hosting | GitHub Pages | Public static dashboard |
| Notifications | Gmail SMTP / Twilio WhatsApp | Daily delivery |
| Packaging | Docker | Reproducible containerized execution |
| Testing | pytest | Automated validation |

---

## 🔄 Automation & CI/CD

The repository separates **software delivery** from the **daily intelligence workload**.

### CI — Continuous Integration

When code changes, GitHub Actions runs the automated test suite with `pytest`.

```text
Code change
    ↓
GitHub Actions
    ↓
Install dependencies
    ↓
Run tests
    ↓
✅ Safe to integrate
```

### CD — Continuous Delivery / Deployment

The deployment workflow builds the static site artifact and publishes it through GitHub Pages.

```text
Application/data update
        ↓
Build Pages artifact
        ↓
Deploy
        ↓
GitHub Pages
```

### Scheduled application automation

The 9 AM workflow is **not CI**. It is scheduled production automation that runs the intelligence pipeline:

```text
9 AM America/Toronto
        ↓
Collect → Process → Gemini → Persist
        ↓
Email + Dashboard
```

That distinction is intentional and is useful when discussing the architecture in technical interviews.

---

## 📁 Project Structure

```text
.
├── .github/workflows/
│   ├── tests.yml              # CI: automated tests
│   ├── daily-briefing.yml     # Scheduled intelligence pipeline + Pages deployment
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
│   └── index.html              # Dashboard UI
│
├── tests/                      # Automated tests
├── Dockerfile                  # Container image
├── requirements.txt            # Runtime dependencies
└── requirements-dev.txt        # Development/test dependencies
```

---

## 🔐 Security

- Gemini credentials are stored in GitHub Actions Secrets.
- Email credentials are stored in GitHub Actions Secrets.
- Secrets are never committed to source control.
- The frontend does not contain the Gemini API key.
- Authentication support is implemented in the FastAPI application for future protected deployments; the current GitHub Pages dashboard remains a static public site.

---

## ⚙️ Configuration

The application is configured through environment variables. See `.env.example` for the available settings.

Core configuration includes:

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

---

## 🧪 Testing

Run the test suite locally:

```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
```

The tests cover core pipeline behavior, site publishing behavior and authentication guards.

---

## 🐳 Run locally

```bash
pip install -r requirements.txt
cp .env.example .env
```

Add your configuration, then:

```bash
PYTHONPATH=. python -m app.jobs.publish_site
```

For the API version:

```bash
uvicorn app.api.main:app --reload
```

Or build the container:

```bash
docker build -t ai-signal-briefing .
docker run --env-file .env -p 8000:8000 ai-signal-briefing
```

---

## 🎯 Engineering Concepts Demonstrated

- Event-driven and scheduled workflows
- ETL-style data processing
- RSS/API-style ingestion
- Data normalization and quality control
- Deduplication strategies
- Deterministic relevance ranking
- Generative AI / LLM integration
- Prompt-driven synthesis
- Persistence and historical analytics
- Notification delivery
- Static web publishing
- CI/CD with GitHub Actions
- Automated testing
- Containerization with Docker
- Failure isolation and graceful degradation
- Secure secret management

---

## 🗺️ Roadmap

Potential next steps include:

- Microsoft Entra ID authentication for a protected personal dashboard
- richer source health monitoring
- article-level evidence and citations
- semantic similarity for stronger deduplication
- vector retrieval for a true RAG layer
- personalized topic preferences
- multi-user profiles
- WhatsApp production delivery
- observability and pipeline metrics

---

## 💡 The one-line architecture

> **A scheduled, event-driven GenAI pipeline that ingests recent AI intelligence, applies deterministic data processing and ranking, uses Gemini for synthesis, persists historical briefings, and delivers the result through email and a searchable dashboard.**

---

## License

This project is currently maintained as a personal engineering portfolio project.
