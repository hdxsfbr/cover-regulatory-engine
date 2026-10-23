# Local persistence and evidence jobs

The POC uses standard-library SQLite (`data/workspace.sqlite3`, override with `COVER_DATABASE`) in WAL mode and immutable original files under `data/`. Migration1 creates records, jobs and their indexes. Each API save is transactional; scenario records retain their complete request, assessment and context, including rule/document identities. Updates append review/activation events instead of rewriting historical scenarios.

`uv run python -m backend.store` indexes existing regulation snapshots, reviewed rule versions and parcel PDFs by their byte hashes. Repeating the import is idempotent. It neither rewrites originals nor gives imported evidence new review status.

One local worker processes bounded evidence jobs. Document cache keys include parcel identity, document hash and extraction prompt version. Repeated requests deduplicate; failed/cancelled attempts can be retried under a new job ID. Cancellation wins over late completion. A restarted worker marks interrupted running jobs failed and resumes queued jobs. Long queue waits expire; model subprocesses and rendering have independent time limits within the240second job budget. The browser polls status and can continue rendering context during extraction.

Job stages: queued → starting → rendering → reading-map → validating → saving → completed, or failed/cancelled/interrupted/expired. Operator jobs also expose fetching-source and extracting-rules. Failed rendering, unavailable subscription auth, invalid model output and source problems stay explicit. Live mode never falls back to authored parcel fixtures.

For backup, stop the local API/worker, copy the SQLite database and all `data/sources`, `data/rules`, `data/parcel-evidence` originals together, and preserve the operator token separately with mode0600. For an online backup use SQLite's backup API instead of copying only the main file while WAL writes are active. Restore both records and originals; verify hashes and run a saved-scenario replay before reopening the service.

The local operator token is `COVER_OPERATOR_TOKEN` if configured, otherwise a generated0600file next to the database with suffix `.operator-token`. Enter it at `/operator`. It is never sent by the public configuration endpoint. Public project APIs assume a single local user; production requires project ownership authorization and managed identities.

The API initializes recovery on startup. Job cache keys also include the primary document acquisition timestamp, so a fresh context rechecks related tract documents. Tract retrieval follows the County form to an allowlisted PDF URL; scripts are parsed as data and never executed. It has a20second streaming deadline, per-request timeouts and a30MB cap. Extraction labels up to8 source pages and keeps supplemental document hashes. Larger records are explicitly withheld from automatic reading.

A watchdog marks a running job failed at its240second budget (including queue time); late completion cannot overwrite failed/cancelled states. Model polling observes terminal cancellation/failure. Completed projects and jobs remain available after process restart. Snapshot memory expiration reloads retained context rather than destroying a saved project.
