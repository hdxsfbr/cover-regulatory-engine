"""Explicit local operator boundary for source and rule mutations."""

import hmac
import json
import os
import secrets
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from backend import store, jobs, synthesis
from backend.rules import source_records, digest

router = APIRouter(prefix="/api/operator")


def token():
    configured = os.getenv("COVER_OPERATOR_TOKEN")
    if configured:
        return configured
    path = store.database().with_suffix(".operator-token")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(secrets.token_urlsafe(32))
    except FileExistsError:
        pass
    return path.read_text().strip()


def authorized(authorization: str = Header(default="")):
    expected = "Bearer " + token()
    if not hmac.compare_digest(authorization, expected):
        raise HTTPException(401, "Operator token required")


@router.get("/sources", dependencies=[Depends(authorized)])
def sources():
    return list(source_records().values())


class ExtractRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hashes: list[str] = Field(min_length=1, max_length=8)
    scope: str = Field(min_length=1, max_length=2000)


@router.post("/extract", dependencies=[Depends(authorized)])
def extract(request: ExtractRequest):
    all_sources = source_records()
    if any(h not in all_sources for h in request.hashes):
        raise HTTPException(422, "Unknown source version")
    payload = {
        "kind": "rule-extraction",
        "sources": {h: all_sources[h] for h in request.hashes},
        "scope": request.scope,
    }
    return jobs.submit_task(payload, digest(payload))


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_id: str
    candidate: dict
    reviewer: str = Field(min_length=1, max_length=120)
    decision: str = Field(pattern="^(review|reject)$")
    note: str = Field(min_length=1, max_length=4000)


@router.post("/reviews", dependencies=[Depends(authorized)])
def review(request: ReviewRequest):
    try:
        job = jobs.read(request.job_id)
    except KeyError:
        raise HTTPException(404, "Extraction job not found")
    if job["status"] != "completed" or job["payload"].get("kind") != "rule-extraction":
        raise HTTPException(409, "Completed rule extraction required")
    sources = job["payload"]["sources"]
    try:
        errors = synthesis.validate(request.candidate, sources)
    except ValueError as error:
        raise HTTPException(422, str(error))
    if request.decision == "review" and errors:
        raise HTTPException(422, json.dumps(errors))
    identity = store.put(
        "rule-review",
        {
            **request.model_dump(),
            "sources": sources,
            "candidate_digest": digest(request.candidate),
            "validation_errors": errors,
        },
    )
    return store.get(identity, "rule-review")


@router.get("/reviews", dependencies=[Depends(authorized)])
def reviews():
    return store.listing("rule-review")


@router.get("/feedback", dependencies=[Depends(authorized)])
def feedback():
    results = store.listing("feedback")
    for item in results:
        history = store.listing("feedback-review", item["id"])
        item["reviews"] = history
        if history:
            item["data"]["status"] = history[0]["data"]["status"]
    return results


class TriageRequest(BaseModel):
    reviewer: str = Field(min_length=1, max_length=120)
    status: str = Field(pattern="^(reviewing|resolved|rejected)$")
    note: str = Field(min_length=1, max_length=4000)


@router.post("/feedback/{identity}", dependencies=[Depends(authorized)])
def triage(identity: str, request: TriageRequest):
    try:
        store.get(identity, "feedback")
    except KeyError:
        raise HTTPException(404, "Feedback not found")
    return {"id": store.put("feedback-review", request.model_dump(), identity)}


class ActivateRequest(BaseModel):
    reviewer: str = Field(min_length=1, max_length=120)
    note: str = Field(min_length=1, max_length=4000)


@router.post("/reviews/{identity}/activate", dependencies=[Depends(authorized)])
def activate(identity: str, request: ActivateRequest):
    from backend.reviewed import validate_activation

    try:
        reviewed = store.get(identity, "rule-review")
        project_type = validate_activation(reviewed)
    except KeyError:
        raise HTTPException(404, "Review not found")
    except ValueError as e:
        raise HTTPException(409, str(e))
    return {
        "id": store.put(
            "rule-activation",
            {"review_id": identity, **request.model_dump()},
            project_type,
        )
    }


@router.get("/activations", dependencies=[Depends(authorized)])
def activations():
    return store.listing("rule-activation")


class RefreshRequest(BaseModel):
    section: str = Field(pattern=r"^(12\.03|12\.08|12\.21\.1|12\.22)$")


@router.post("/refresh", dependencies=[Depends(authorized)])
def refresh(request: RefreshRequest):
    import uuid

    payload = {"kind": "source-refresh", "section": request.section}
    return jobs.submit_task(payload, "source-refresh:" + str(uuid.uuid4()))


@router.get("/packages", dependencies=[Depends(authorized)])
def packages():
    from backend.rules import ROOT

    return {
        "single_family": json.loads((ROOT / "data/rules/active.json").read_text()),
        "accessory_source_pins": json.loads(
            (ROOT / "data/rules/package-source-pins.json").read_text()
        ),
        "activations": store.listing("rule-activation"),
    }


@router.get("/jobs", dependencies=[Depends(authorized)])
def operator_jobs():
    with store.transaction() as db:
        rows = db.execute(
            "SELECT id,status,stage,payload FROM jobs ORDER BY created_at DESC LIMIT 100"
        ).fetchall()
    return [
        {"id": r["id"], "status": r["status"], "stage": r["stage"]}
        for r in rows
        if json.loads(r["payload"]).get("kind") in ("rule-extraction", "source-refresh")
    ]
