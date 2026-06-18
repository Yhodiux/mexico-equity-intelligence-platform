# Demo Guide

## Goal

This guide helps reviewers run and evaluate the BMV Market Intelligence Platform locally with Docker.

The demo shows a complete data product flow:

```text
Public Market Data -> Raw -> Silver -> Quality -> Gold -> Metadata -> API -> Dashboard -> AI Agent
```

## Prerequisites

- Docker
- Docker Compose
- Internet access for Yahoo Finance downloads

No BMV credentials, paid services, cloud account, API token, or local Python environment are required.

## 1. Build the Data Products

Run the full pipeline:

```bash
docker compose run --rm pipeline
```

This command downloads market data and generates:

- Raw Parquet files under `data/raw/`
- Silver Parquet dataset under `data/silver/`
- Data quality report under `data/metadata/data_quality_report.json`
- Gold data products under `data/gold/`
- Dataset metadata catalog under `data/metadata/datasets_metadata.json`

Expected validation output:

- Raw rows greater than zero
- Silver rows greater than zero
- Data quality status: `passed`
- 15 quality checks passed
- 5 Gold datasets generated

## 2. Run Automated Tests

Run:

```bash
docker compose run --rm tests
```

Expected result:

```text
9 passed
```

The tests validate:

- Gold dataset generation
- Metadata catalog contents
- API endpoints
- AI Agent supported and unsupported question behavior

## 3. Review the Dashboard

Start the dashboard:

```bash
docker compose up dashboard
```

Open:

```text
http://localhost:8501
```

Recommended dashboard review path:

1. Confirm the Gold dataset status section shows available datasets.
2. Review executive KPIs.
3. Review 30-day performance charts.
4. Review risk and volatility charts.
5. Review liquidity and unusual volume views.
6. Review AI-ready insights.
7. Use the embedded Market Intelligence Agent question selector.

Reference screenshots:

- [Dashboard overview](screenshots/dashboard_overview.png)
- [Dashboard analytics](screenshots/dashboard_analytics.png)
- [Dashboard AI Agent](screenshots/dashboard_ai_agent.png)

Stop the dashboard with `Ctrl+C`.

## 4. Review the API

Start the API:

```bash
docker compose up api
```

Open the interactive FastAPI docs:

```text
http://localhost:8000/docs
```

Key endpoints:

```text
GET /health
GET /datasets
GET /performance
GET /volatility
GET /liquidity
GET /market-trends
GET /ai-insights
POST /ask
```

Example AI Agent request:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Which issuers had the best 30-day performance?\"}"
```

Reference screenshots:

- [Ask best performance](screenshots/ask_best_performance.png)
- [Ask guardrail](screenshots/ask_guardrail.png)

Stop the API with `Ctrl+C`.

## Supported Agent Questions

The AI Agent is deterministic and grounded in the Gold datasets. It does not answer unsupported external questions.

Supported questions:

- Which issuers had the best 30-day performance?
- Which issuers show sustained growth with controlled volatility?
- Which sectors show higher volatility?
- Which companies show unusual volume behavior?
- What are the most relevant market insights?

Unsupported questions return suggested supported questions instead of invented answers.

## Business Demo Question Set

Use these questions to show business value to non-technical reviewers. The goal is not to predict the market, but to demonstrate how governed historical data can be turned into market intelligence for decision support.

| Demo Step | Question | What It Demonstrates | Source Datasets | Business Value |
| --- | --- | --- | --- | --- |
| 1 | Which issuers had the best 30-day performance? | Ranks recent observed performance | `gold_performance` | Creates market summary feeds and issuer ranking products |
| 2 | Which issuers show sustained growth with controlled volatility? | Combines positive 30-day and 90-day returns with Low or Medium risk | `gold_performance`, `gold_volatility` | Helps analysts find stronger risk-return profiles without making predictions |
| 3 | Which companies show unusual volume behavior? | Detects volume changes versus each issuer's 30-day average | `gold_liquidity` | Supports alerts, market attention monitoring, and issuer relations conversations |
| 4 | What are the most relevant market insights? | Converts computed signals into business-readable narratives | `gold_ai_insights` | Feeds executive summaries, analyst prompts, and AI assistant responses |
| 5 | Can you predict next week's stock prices? | Rejects unsupported prediction requests | None | Shows guardrails, avoids unsupported claims, and protects trust |

Recommended demo order:

1. Start with 30-day performance to show a simple ranking.
2. Move to sustained growth with controlled volatility to show multi-dataset intelligence.
3. Ask about unusual volume to show alerting potential.
4. Ask for relevant insights to show executive-ready interpretation.
5. Ask for a prediction to prove the agent stays inside its governed scope.

Key message for reviewers:

```text
The agent does not forecast prices or give investment advice. It explains what is happening in the governed Gold datasets, how issuers compare, and which signals deserve attention.
```

## What to Evaluate

### Data Engineering

- Reproducible Docker pipeline
- Raw, Silver, and Gold layers
- Data quality checks
- Parquet outputs
- Metadata catalog

### Data Products

- Performance product
- Volatility product
- Liquidity product
- Market trends product
- AI insights product

### API and AI

- FastAPI endpoints over Gold data products
- Deterministic AI Agent
- Source datasets returned with answers
- Unsupported questions handled safely

### Demo Experience

- Streamlit dashboard
- Executive metrics
- Charts and data previews
- Embedded AI Agent interaction

## Notes

Yahoo Finance is used as the public technical data source for local reproducibility. The business framing remains Mexican market intelligence related to BMV issuers.

BMV Web Services are not used in this MVP because they require commercial access, credentials, and controlled connectivity.
