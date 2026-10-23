# Local model adapter

`backend/model.py` sends one structured text/image user message to the installed Claude CLI through `--input-format stream-json`; output is parsed from the final result event. `--tools ""`, empty setting sources, disabled skills, strict MCP configuration and a fresh temporary directory prevent repository context or source instructions from gaining tool authority. The temporary directory fixed an initially observed247k-token ambient-context load; an isolated readiness probe used585cached-input tokens.

Every invocation first verifies `claude auth status` reports `claude.ai` and a subscription. The inherited `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, and `ANTHROPIC_BASE_URL` are removed. No API-credit fallback exists. Recorded model usage may include list-price equivalents; those are provider metadata, not evidence that an API key was used.

Inputs: prompt and at most eight labeled assessor/tract map pages, each bounded to5MB. Output: a JSON object plus prompt hash, elapsed time, provider model identity/usage and auth method. Invalid JSON, provider errors, cancellation and timeout fail explicitly. A cancelled/expired process group is killed and reaped. Extraction never executes model code. Page regions, parcel identity, units and GIS corroboration are checked separately in `backend/extraction.py`.

Actual image probe: `data/delivery/probes/new-map-result.json`, new tract14429lot26,33.072seconds; it identified irregular boundaries and uncertain frontage. The complete frozen corpus runs are under `data/delivery/*-extraction.json`, with retained prior attempts under `attempts/`. The raw model response remains available even when identity validation fails.

Actual source-driven probe: original and changed-source candidates in `data/delivery/probes/rule-*.json`. Changing only the passage changed the operand; unresolved references prevent automatic approval. Actual grounded follow-up is recorded in `grounded-answer.json` (9.091seconds).

This adapter is for the authorized local POC. Production provider identity/terms and service authentication require a separate deployment decision; the local user subscription is not presented as a hosted-service credential.
