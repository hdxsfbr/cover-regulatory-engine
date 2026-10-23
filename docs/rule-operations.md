# Regulatory ingestion and review

The public API never invokes an LLM or exposes these commands. Local JSON snapshots are immutable by hash; `data/sources/current.json` selects current sections. Each rule pins all four applicability sources. Changing any dependency blocks current evaluation until review, including definition or exception changes that leave the primary calculation paragraph untouched.

The original real extraction is retained in `data/rules/candidates/initial.json`, with model usage, instruction hash, source versions, subscription authentication method and rejected validation results. It correctly identified incomplete citation context. `resolved.json` preserves that extraction record and adds an explicit manual-resolution record: expanded side-yard quote, complete definitions, and mixed-roof exclusion. The active set records Codex source comparison, not a human professional approval. Archived reviewed versions live under `data/rules/versions/`.

## Extract and activate

Requires Claude Code signed in with a Claude subscription. The command removes API-key/token/base-URL overrides and checks `claude auth status` for `claude.ai` and a subscription before extraction. No API-credit fallback is available. Provider failures leave existing reviewed rules untouched.

```bash
uv run python -m backend.ingest extract data/rules/candidates/new.json
```

Review every exact passage, required input, predicate, exception and unresolved reference against the preserved text and applicability matrix. The finite operation names select application-owned arithmetic; generated expressions never execute. Rejected candidates remain ineligible. If manual corrections are needed, preserve the original candidate and add an attributed resolution record in a new candidate file.

```bash
uv run python -m backend.ingest review data/rules/candidates/new.json data/rules/reviewed-new.json --reviewer 'Your reviewer identity'
uv run python -m backend.ingest activate data/rules/reviewed-new.json
```

Review alone creates a reviewed artifact; activation validates review digests, all source versions, the five categories and the bundle version, archives it and atomically replaces `active.json`. It refuses tampering, incomplete sets and superseded sources. Use a fresh output path; extraction/review never overwrite existing artifacts.

## Refresh and rollback

```bash
uv run python -m backend.ingest refresh 12.08 data/rules/candidates/refreshed-12.08.json
```

Refresh uses the previously configured official URL, browser-compatible request headers, a bounded body and the publisher's `#codecontent`. A changed section creates a new snapshot, advances current source state and extracts a new candidate. The refreshed edition/effective date remain explicitly unverified until reviewed. If extraction then fails, the old affected rules are already blocked; rerun `extract` after resolving provider access. An unchanged text hash creates no candidate. Historical evidence is never deleted.

After review, activate the new version. Roll back rules by activating the desired file in `data/rules/versions/`; it succeeds only if every source dependency still matches current source state. Do not reset source currency merely to make an old rule run. Historical files remain available for reproduction even when they are no longer eligible for current assessments.

No automatic publisher monitoring is implemented. The recorded edition is evidence of the acquisition, not a promise of current law. `docs/source-verification.md` explains the observed Cloudflare 403 and header fix. A future challenge or publisher error is an acquisition failure, never evidence that a regulation does not exist.

## Typed expression packages and operator review

The full workspace uses a finite JSON expression tree (`backend/expressions.py`). Leaves are `constant(value,unit)` and `input(name,unit)`; supported operations are min/max/add/subtract/multiply/divide/ceil/lt/lte/eq/if. Units are ft, sq ft, scalar, %, bool. Addition/comparison require compatible units, dimensional multiplication/division must remain scalar/length/area, and non-finite values/zero division/unknown operations are rejected. Trees have a depth and operand bound. There is no `eval`, generated Python, or arbitrary function call.

Candidate rules carry jurisdiction, regime, project type, category, inputs, expression, exact source-hash/passages, predicates, exceptions and unresolved references. Optional `valid_from`/`valid_until` are ISO dates; unknown dates stay null. Activation checks current source versions and a valid interval, complete package categories, canonical scope and mapped applicability keys. `reviewed_as_of` is the review date, not a claimed statutory effective date. A synthetic second-jurisdiction test validates the same schema/interpreter; live activation remains deliberately bounded to reviewed LA scope.

The source-derived operator demonstration is in `data/delivery/probes/operator-live-job.json`. The candidate omitted the foot unit from a side-yard increment count; unit validation caught it. `operator-reviewed-candidate.json` adds the source-stated one-foot multiplier, normalizes scope identifiers, and records dependency dispositions. Numeric thresholds remain source-derived. `data/delivery/operator-rollback-proof.json` records activation of another eligible attributed review and rollback. Invalid candidate attempts remain in review history; activation is never inferred from extraction completion.

Open `/operator`, enter the local token, select source versions and extraction scope, then extract. Job status updates automatically; resume a retained job after reloading. Inspect the source passages and validation errors, correct candidate JSON, enter reviewer/rationale, record review, then activate the specific version. Source refresh uses the actual publisher;403/timeout is an explicit failed source job and does not fabricate a newer snapshot. Resolve feedback in the same workspace. Neither feedback nor chat can mutate rules.
