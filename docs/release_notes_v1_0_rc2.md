# v1.0-rc2 Release Notes

Release candidate for the Mexico Equity Intelligence Platform.

```text
Transforming public market data into AI-ready data products for Market Intelligence and data monetization.
```

This release packages a reproducible Data Engineering and AI MVP that transforms public Mexican equity market observations into governed data products and controlled information services. It is not a trading system, investment recommender, price prediction platform, or forecasting product.

## Included Capabilities

- Reproducible Docker-based pipeline and runtime.
- Raw, Silver, Gold, Quality, and Metadata layers.
- Gold data products for performance, volatility, liquidity, market trends, and AI-ready insights.
- FastAPI endpoints and a Streamlit executive dashboard.
- Deterministic governed question answering over Gold datasets.
- Optional LLM-assisted answers grounded in structured Gold evidence.
- Guardrails against unsupported topics, forecasts, price targets, and investment recommendations.
- Architecture, operations, data product, monetization, and reviewer documentation.

## Changes Since v1.0-rc1

- Completed the product and repository rename to Mexico Equity Intelligence Platform.
- Clarified proprietary licensing, third-party data sourcing, and BMV non-affiliation.
- Aligned runtime startup commands and repository review guidance.
- Added a documented `Future AI Enhancements` roadmap covering:
  - AI-assisted data quality explanations.
  - Executive daily market brief generation.
  - AI-assisted metadata enrichment.
- Kept all future AI initiatives explicitly outside the current MVP implementation.

## Validation

Expected final validation:

```text
Data quality: 15 checks passed, 0 failed
Automated tests: 23 passed
API health: status ok
Dashboard: loads successfully
```

## Review Flow

```bash
git checkout v1.0-rc2
docker compose run --rm pipeline
docker compose run --rm tests
docker compose up
```

Open:

```text
http://localhost:8501
http://localhost:8000/docs
```

The platform works without an OpenAI API key. Real API keys must remain private and must not be committed or included in release materials.
