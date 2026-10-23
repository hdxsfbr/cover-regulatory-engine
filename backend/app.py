import copy
import json
import os
import time
import uuid
from typing import Literal
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictBool
from backend.gis import ROOT, context_for, search, query_filter, summarize
from backend.rules import assess, CHECKS, NUMBERS
from backend import evidence


@asynccontextmanager
async def lifespan(app):
    from backend import jobs

    jobs.recover()
    yield


app = FastAPI(title="Cover Regulatory Engine", lifespan=lifespan)
SNAPSHOTS = {}
INVALIDATED_EVIDENCE = set()
FIXTURE_MODE = os.getenv("COVER_FIXTURE_MODE") == "1"


class AssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot_id: str
    project_type: Literal["single-family", "adu", "guest-house"] = "single-family"
    inputs: dict[str, StrictFloat | StrictInt] = Field(default_factory=dict)
    checks: dict[str, StrictBool] = Field(default_factory=dict)
    observation_ids: list[str] = Field(default_factory=list, max_length=3)
    evidence_note: str = Field(default="", max_length=2000)


def fixture(ain):
    path = ROOT / "data/fixtures" / f"{ain}.json"
    if not path.exists():
        raise HTTPException(404, "No recorded fixture for this parcel")
    result = json.loads(path.read_text())
    supplemental_path = evidence.STORE / "recorded" / f"{ain}.json"
    supplemental = (
        json.loads(supplemental_path.read_text()) if supplemental_path.exists() else {}
    )
    result["records"].update(supplemental.get("records", {}))
    for record in result["records"].values():
        record["origin"] = "fixture"
    return evidence.attach(
        summarize(result["records"]), supplemental.get("document"), recorded=True
    )


@app.get("/api/config")
def config():
    return {
        "mode": "fixture" if FIXTURE_MODE else "live",
        "checks": CHECKS,
        "input_bounds": NUMBERS,
    }


@app.get("/api/parcels")
async def parcels(query: str):
    try:
        query_filter(query)
    except ValueError as e:
        raise HTTPException(422, str(e))
    if FIXTURE_MODE:
        features = []
        for path in (ROOT / "data/fixtures").glob("*.json"):
            d = json.loads(path.read_text())
            p = d.get("parcel", {})
            if (
                query.replace("-", "").replace(" ", "") == p.get("AIN")
                or query.upper() in p.get("SitusFullAddress", "").upper()
            ):
                features.append(
                    {
                        "properties": {
                            k: p.get(k) for k in ("AIN", "APN", "SitusFullAddress")
                        }
                    }
                )
        return {
            "status": "matched" if features else "no-match",
            "features": features,
            "origin": "fixture",
        }
    return await search(query)


@app.get("/api/parcels/{ain}/context")
async def context(ain: str, fresh: bool = False, compact: bool = False):
    if len(ain) != 10 or not ain.isdigit():
        raise HTTPException(422, "Invalid parcel identifier")
    result = (
        fixture(ain) if FIXTURE_MODE else await context_for(ain, use_cache=not fresh)
    )
    from backend.facts import derive

    result["sourced_facts"] = derive(result)
    if fresh:
        for old_id, (_, old) in list(SNAPSHOTS.items()):
            if old.get("parcel", {}).get("AIN") == ain and (
                not result.get("applicability_fingerprint")
                or result.get("applicability_fingerprint")
                != old.get("applicability_fingerprint")
            ):
                INVALIDATED_EVIDENCE.add(old_id)
    INVALIDATED_EVIDENCE.intersection_update(SNAPSHOTS)
    identity = str(uuid.uuid4())
    if len(SNAPSHOTS) >= 100:
        SNAPSHOTS.pop(next(iter(SNAPSHOTS)))
    store.put("context", result, identity=identity)
    SNAPSHOTS[identity] = (time.monotonic(), copy.deepcopy(result))
    if compact:
        result = {
            **result,
            "records": {
                name: {
                    key: value
                    for key, value in record.items()
                    if key not in ("features", "query")
                }
                for name, record in result["records"].items()
            },
        }
    return {
        **result,
        "snapshot_id": identity,
        "mode": "fixture" if FIXTURE_MODE else "live",
    }


@app.post("/api/assessments")
def assessment(request: AssessmentRequest):
    if request.observation_ids and request.snapshot_id in INVALIDATED_EVIDENCE:
        raise HTTPException(
            410, "Parcel document acceptance expired; refresh and review evidence"
        )
    item = SNAPSHOTS.get(request.snapshot_id)
    if not item or time.monotonic() - item[0] >= 900:
        try:
            item = (time.monotonic(), store.get(request.snapshot_id, "context")["data"])
        except KeyError:
            pass
    if not item or time.monotonic() - item[0] >= 900:
        raise HTTPException(410, "Parcel context expired; reload it")
    try:
        result = assess(
            item[1],
            request.project_type,
            request.inputs,
            request.checks,
            request.evidence_note,
            observation_ids=request.observation_ids,
        )
    except ValueError as e:
        raise HTTPException(422, str(e))
    from backend.geometry import for_assessment
    from backend.summary import summarize as summarize_assessment

    result["summary"] = summarize_assessment(result, request.inputs)

    return {
        **result,
        "snapshot_id": request.snapshot_id,
        "geometry": for_assessment(item[1], result),
    }


# Durable workspace APIs retain immutable source and assessment revisions.
from backend import store, jobs


def snapshot_context(identity):
    item = SNAPSHOTS.get(identity)
    if item:
        return copy.deepcopy(item[1])
    try:
        return store.get(identity, "context")["data"]
    except KeyError:
        raise HTTPException(404, "Parcel context not found")


class ResearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot_id: str
    fresh: bool = False


@app.post("/api/research/{source}")
async def parcel_research(source: str, request: ResearchRequest):
    from backend import research

    if source not in research.SOURCES:
        raise HTTPException(404, "Unknown research source")
    context = snapshot_context(request.snapshot_id)
    ain = str(context.get("parcel", {}).get("AIN", ""))
    if len(ain) != 10 or not ain.isdigit():
        raise HTTPException(409, "Resolve a parcel before requesting research")
    return await research.fetch(source, context, request.fresh, FIXTURE_MODE)


class EvidenceJobRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot_id: str
    retry: bool = False


@app.post("/api/evidence-jobs")
def create_evidence_job(request: EvidenceJobRequest):
    if FIXTURE_MODE:
        raise HTTPException(409, "Automatic model extraction requires live mode")
    try:
        return jobs.submit(snapshot_context(request.snapshot_id), request.retry)
    except ValueError as error:
        raise HTTPException(422, str(error))


@app.get("/api/evidence-jobs/{identity}")
def evidence_job(identity: str, authorization: str = Header(default="")):
    try:
        job = jobs.read(identity)
        if job["payload"].get("kind"):
            from backend.operator import authorized

            authorized(authorization)
        job.pop("payload", None)
        return job
    except KeyError:
        raise HTTPException(404, "Job not found")


@app.post("/api/evidence-jobs/{identity}/cancel")
def cancel_evidence_job(identity: str, authorization: str = Header(default="")):
    try:
        evidence_job(identity, authorization)
        jobs.cancel(identity)
        return evidence_job(identity, authorization)
    except KeyError:
        raise HTTPException(404, "Job not found")


@app.post("/api/evidence-jobs/{identity}/context")
def extracted_context(identity: str, request: EvidenceJobRequest):
    try:
        job = jobs.read(identity)
    except KeyError:
        raise HTTPException(404, "Job not found")
    if job["payload"].get("kind"):
        raise HTTPException(409, "This job does not contain parcel evidence")
    if job["status"] != "completed":
        raise HTTPException(409, "Evidence job has not completed")
    result = snapshot_context(request.snapshot_id)
    if (
        result.get("parcel", {}).get("AIN")
        != job["payload"].get("parcel", {}).get("AIN")
        or result.get("document", {}).get("content_hash")
        != job["payload"].get("document", {}).get("content_hash")
        or any(
            result.get(k) != job["payload"].get(k)
            for k in ("parcel", "regime", "jurisdiction")
        )
        or [
            f.get("geometry")
            for f in result.get("records", {}).get("Parcels", {}).get("features", [])
        ]
        != [
            f.get("geometry")
            for f in job["payload"]
            .get("records", {})
            .get("Parcels", {})
            .get("features", [])
        ]
        or request.snapshot_id in INVALIDATED_EVIDENCE
    ):
        raise HTTPException(
            409, "Map result belongs to different or superseded evidence"
        )
    result["automatic_evidence"] = job["result"]
    result["machine_observations"] = job["result"]["observations"]
    new_id = store.put("context", result)
    SNAPSHOTS[new_id] = (time.monotonic(), copy.deepcopy(result))
    return {**result, "snapshot_id": new_id, "mode": "live"}


class ProjectRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=120)
    snapshot_id: str


class ScenarioRequest(AssessmentRequest):
    research_ids: dict[str, str] = Field(default_factory=dict, max_length=4)
    name: str = Field(min_length=1, max_length=120)


@app.get("/api/projects")
def projects():
    return store.listing("project")


@app.post("/api/projects")
def create_project(request: ProjectRequest):
    c = snapshot_context(request.snapshot_id)
    identity = store.put(
        "project",
        {
            "name": request.name,
            "ain": c.get("parcel", {}).get("AIN"),
            "snapshot_id": request.snapshot_id,
        },
    )
    return store.get(identity, "project")


@app.get("/api/projects/{identity}")
def project_detail(identity: str):
    try:
        project = store.get(identity, "project")
        return {
            **project,
            "scenarios": store.listing("scenario", identity),
            "context": {
                **snapshot_context(project["data"]["snapshot_id"]),
                "snapshot_id": project["data"]["snapshot_id"],
                "mode": "fixture" if FIXTURE_MODE else "live",
            },
        }
    except KeyError:
        raise HTTPException(404, "Project not found")


@app.post("/api/projects/{identity}/scenarios")
def save_scenario(identity: str, request: ScenarioRequest):
    try:
        p = store.get(identity, "project")
    except KeyError:
        raise HTTPException(404, "Project not found")
    c = snapshot_context(request.snapshot_id)
    if p["data"]["ain"] != c.get("parcel", {}).get("AIN"):
        raise HTTPException(409, "Scenario parcel does not belong to this project")
    from backend import research

    try:
        c["research"] = research.capture(c, request.research_ids)
    except (KeyError, ValueError) as e:
        raise HTTPException(409, str(e))
    req = AssessmentRequest(**request.model_dump(exclude={"name", "research_ids"}))
    result = assessment(req)
    sid = store.put(
        "scenario",
        {
            "name": request.name,
            "request": req.model_dump(),
            "assessment": result,
            "context": c,
        },
        identity,
    )
    return store.get(sid, "scenario")


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario_id: str
    category: str = Field(max_length=80)
    comment: str = Field(min_length=1, max_length=4000)


@app.post("/api/feedback")
def feedback(request: FeedbackRequest):
    try:
        scenario = store.get(request.scenario_id, "scenario")
    except KeyError:
        raise HTTPException(404, "Save a scenario before submitting feedback")
    constraints = scenario["data"]["assessment"]["constraints"]
    if request.category not in {c["category"] for c in constraints} | {"assessment"}:
        raise HTTPException(422, "Unknown result category")
    return {
        "id": store.put(
            "feedback",
            {
                **request.model_dump(),
                "status": "open",
                "assessment": scenario["data"]["assessment"],
            },
            scenario["parent"],
        )
    }


from backend.operator import router as operator_router

app.include_router(operator_router)


class QuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=2000)


@app.post("/api/scenarios/{identity}/questions")
async def question(identity: str, body: QuestionRequest, request: Request):
    import asyncio
    import threading
    from backend.questions import answer

    try:
        scenario = store.get(identity, "scenario")
    except KeyError:
        raise HTTPException(404, "Saved scenario not found")
    cancelled = threading.Event()
    try:
        task = asyncio.create_task(
            asyncio.to_thread(answer, scenario["data"], body.question, cancelled.is_set)
        )
        deadline = time.monotonic() + 28
        while not task.done():
            if await request.is_disconnected():
                cancelled.set()
                task.cancel()
                raise HTTPException(499, "Question cancelled")
            if time.monotonic() >= deadline:
                task.cancel()
                raise TimeoutError()
            await asyncio.wait({task}, timeout=0.2)
        result = await task
        qid = store.put(
            "question", {"question": body.question, "answer": result}, identity
        )
        return {**result, "id": qid, "scenario_id": identity}
    except TimeoutError:
        raise HTTPException(504, "Answer provider timed out; your scenario is saved")
    except (ValueError, RuntimeError) as error:
        raise HTTPException(502, str(error))
    finally:
        cancelled.set()


@app.get("/api/documents/{content_hash}/pages/{page}")
def document_page(content_hash: str, page: int):
    import re
    import hashlib
    import subprocess
    from fastapi.responses import FileResponse

    if not re.fullmatch(r"[a-f0-9]{64}", content_hash) or not 1 <= page <= 8:
        raise HTTPException(422, "Invalid document page")
    source = evidence.STORE / (content_hash + ".pdf")
    if not source.exists():
        raise HTTPException(404, "Document not found")
    if hashlib.sha256(source.read_bytes()).hexdigest() != content_hash:
        raise HTTPException(409, "Document integrity check failed")
    folder = evidence.STORE / "pages"
    folder.mkdir(exist_ok=True)
    target = folder / f"{content_hash}-{page}.png"
    if not target.exists():
        try:
            subprocess.run(
                [
                    "pdftoppm",
                    "-f",
                    str(page),
                    "-l",
                    str(page),
                    "-singlefile",
                    "-scale-to",
                    "3000",
                    "-png",
                    str(source),
                    str(target.with_suffix("")),
                ],
                capture_output=True,
                timeout=20,
                check=True,
            )
        except (subprocess.SubprocessError, OSError):
            raise HTTPException(422, "Page could not be rendered")
    if not target.exists():
        raise HTTPException(404, "Page not present")
    return FileResponse(
        target,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
