# Cover Regulatory Engine

A local Python/TypeScript POC for evidence-backed residential parcel assessment in Los Angeles. Search an address or APN, inspect live parcel/zoning/building evidence, and let a background job read public assessor and referenced tract maps. Results distinguish sourced facts, machine interpretations, project assumptions and unresolved conditions.

The workspace supports bounded single-family, detached ADU and guest-house packages, saved scenarios and comparison, cited follow-up questions, result feedback, linked map annotations and source-attributed setback exports. `/operator` exposes source acquisition, actual model extraction, correction, review and activation. See [package coverage](docs/project-packages.md) for the exact branches; a searchable property is not necessarily covered by a regulatory package.

## Run

Requires Python3.11+, uv, Node22.12+, Poppler (`pdfinfo`, `pdftoppm`), and a subscription-authenticated Claude Code installation for live map reading, rule extraction and follow-up. Deterministic assessments and recorded tests do not require model credentials.

```bash
uv sync --locked
npm --prefix frontend ci --no-audit --no-fund
uv run python -m backend.store
uv run uvicorn backend.app:app --host 127.0.0.1 --port 18080
```

In another terminal:

```bash
npm --prefix frontend run dev
```

Open [the workspace](http://127.0.0.1:5173), [operator review](http://127.0.0.1:5173/operator), or [API documentation](http://127.0.0.1:18080/docs). The development server proxies `/api` to18080. `COVER_API_URL` overrides that target.

The model adapter removes inherited Anthropic API credentials/endpoint overrides and verifies `claude.ai` authentication. Authenticate Claude Code with your subscription before using model features. It never falls back to API credits. See [adapter contract](docs/model-adapter.md).

Persistence defaults to `data/workspace.sqlite3`; set `COVER_DATABASE` to isolate a workspace. Operator access uses `COVER_OPERATOR_TOKEN` or a generated mode0600 `.operator-token` file beside the database. Enter that value in the operator UI; do not publish it. These project APIs assume a single local user.

For the labeled recorded demonstration, start the backend with `COVER_FIXTURE_MODE=1`. Recorded examples are regression/demo fixtures; live failures never fall back to them. Live map extraction attempts the same pipeline for new parcels, without adding addresses to code.

## Verify

```bash
uv run pytest -q
npm --prefix frontend run build
npm --prefix frontend exec playwright install chromium
npm --prefix frontend test
openspec validate prd-complete-delivery --strict
```

Browser tests use an isolated backend on18081 and frontend on5179. Live application ports remain available. Validation runs and model probes are retained under `data/delivery`; the [full delivery plan](docs/prd-delivery-plan.md) defines release gates separately from test counts.

## Documentation

- [Project package sources, precedence and exclusions](docs/project-packages.md)
- [Persistence, jobs and backup](docs/persistence-and-jobs.md)
- [API contract](docs/api.md)
- [Demo and acceptance workflow](docs/demo.md)
- [Implemented architecture and proposed AWS production path](docs/architecture.md)
- [Delivery progress](docs/full-delivery-progress.md)

The POC models a small zoning subset as the PRD requests. It does not determine complete construction-code compliance or permit approval. Source interpretation and acceptance checks in this repository are agent-authored, not independent professional zoning approval. OpenSpec change `prd-complete-delivery` remains active until its release gates pass.
