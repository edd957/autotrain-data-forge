# AutoTrain Data Forge

Open-source AI platform for permissioned web data collection, LLM-assisted job planning, local dataset building, and lightweight model training.

AutoTrain Data Forge lets a user describe a training goal such as:

> "Collect text and permitted images from these approved sites, build a local dataset in `data/jobs/site1`, train a searchable assistant memory, then delete raw collected data after training."

The project is intentionally safety-first. It does not bypass authentication, scrape paywalled/private areas, ignore robots.txt, evade rate limits, or delete data from remote websites. Cleanup only applies to local collected data.

## What It Does

- Creates auditable collection jobs from YAML or natural language.
- Uses optional LLM providers through user-supplied API keys to draft collection plans.
- Crawls only user-approved domains and respects robots.txt by default.
- Extracts page text, metadata, links, and filtered content.
- Downloads permitted images only when enabled and within configured limits.
- Saves structured data into job folders.
- Trains a local TF-IDF retrieval model from collected text and image metadata.
- Queries the trained local retrieval model through CLI or API.
- Produces a training card, dataset manifest, and security review.
- Supports local cleanup policies such as `retain`, `delete_raw_after_training`, or `delete_all_after_training`.
- Exposes a CLI and FastAPI service.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
adf init jobs/example.yml
adf review jobs/example.yml
adf run jobs/example.yml --dry-run
adf train jobs/example.yml
adf query data/jobs/example-authorized-site/model "What did the dataset contain?"
adf serve
```

Open `http://localhost:8020/docs` after starting the API.
Open `http://localhost:8020/ui` for the local web interface.

## Example Job

```yaml
name: example-authorized-site
goal: Collect public documentation text for a local assistant.
seeds:
  - https://example.com/
allowed_domains:
  - example.com
include_text: true
include_images: false
include_text_patterns: []
exclude_text_patterns: []
include_url_patterns: []
max_pages: 25
max_depth: 1
rate_limit_seconds: 1.0
respect_robots_txt: true
output_dir: data/jobs/example-authorized-site
cleanup_policy: retain
llm:
  provider: openai_compatible
  model: gpt-4.1-mini
  api_key_env: OPENAI_API_KEY
```

## Safety Rules

AutoTrain Data Forge is for authorized, legitimate data collection and local ML training. It includes security reviews for:

- domain allowlists;
- localhost/private-network SSRF risk;
- robots.txt enforcement;
- unsafe output paths;
- excessive page limits;
- missing dataset purpose;
- local deletion scope;
- API key handling;
- image collection risk;
- LLM request policy.

## Natural-Language Planning

```bash
adf parse-request 'Collect text from https://example.com/news mentioning "release notes", train locally, then delete raw data.'
```

The planner creates a draft job only. Review it before running:

```bash
adf review examples/filtered_posts_delete_raw.yml
adf run examples/filtered_posts_delete_raw.yml --execute
adf train examples/filtered_posts_delete_raw.yml
```

## API

```bash
adf serve
```

Then open `http://localhost:8020/docs`.
The local GUI is available at `http://localhost:8020/ui`.

Core endpoints:

- `POST /v1/parse-request`
- `POST /v1/review`
- `POST /v1/crawl`
- `POST /v1/train`
- `POST /v1/query`

## Repository Layout

```text
autotrain-data-forge/
|-- docs/
|-- examples/
|-- src/autotrain_data_forge/
|-- tests/
|-- Dockerfile
|-- docker-compose.yml
|-- Makefile
`-- pyproject.toml
```

## Legal and Ethical Notice

Only collect data you are allowed to access, use, store, and train on. Respect website terms, robots.txt, rate limits, copyright, privacy laws, platform policies, and user consent. This project provides guardrails, but the operator is responsible for lawful use.
