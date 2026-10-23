"""Operator-only extraction and review. Never called by public HTTP endpoints."""

import argparse
import hashlib
import httpx
from bs4 import BeautifulSoup
import json
import os
import subprocess
import time
from pathlib import Path
from backend.gis import ROOT, now
from backend.rules import source_records, validate_rule, digest, CATEGORIES


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def snapshot(section, output, extract_candidate=True):
    current = json.loads((ROOT / "data/sources/current.json").read_text())
    previous = source_records()[current[section]]
    deadline = time.monotonic() + 30
    with httpx.Client(timeout=6, headers=HEADERS, follow_redirects=False) as client:
        with client.stream("GET", previous["url"]) as response:
            response.raise_for_status()
            chunks = []
            size = 0
            for chunk in response.iter_bytes():
                if time.monotonic() > deadline:
                    raise TimeoutError("Regulatory retrieval exceeded 30 seconds")
                size += len(chunk)
                if size > 12_000_000:
                    raise ValueError("Regulatory source exceeds size limit")
                chunks.append(chunk)
    content = BeautifulSoup(b"".join(chunks), "html.parser").select_one("#codecontent")
    if content is None:
        raise ValueError("Publisher code content missing; possible challenge page")
    text = content.get_text("\n", strip=True)
    if len(text) < 500 or section not in text:
        raise ValueError("Incomplete regulatory text")
    content_hash = hashlib.sha256(text.encode()).hexdigest()
    if content_hash == previous["content_hash"]:
        return False
    record = {
        **previous,
        "text": text,
        "content_hash": content_hash,
        "retrieved_at": now(),
        "edition": "unverified on refresh",
        "effective_date": None,
    }
    path = ROOT / "data/sources/regulations" / f"{section}-{content_hash[:12]}.json"
    if not path.exists():
        with path.open("x") as f:
            json.dump(record, f, indent=2)
    current[section] = content_hash
    index = ROOT / "data/sources/current.json"
    temporary = index.with_suffix(".tmp")
    temporary.write_text(json.dumps(current, indent=2))
    temporary.replace(index)
    # Advance source state before extraction so provider failure cannot leave old rules current.
    if extract_candidate:
        extract(output)
    return True


def activate(reviewed):
    from backend.rules import load_rules

    bundle = json.loads(reviewed.read_text())
    sources = source_records()
    current = json.loads((ROOT / "data/sources/current.json").read_text())
    if len(bundle["rules"]) != 5 or {r["category"] for r in bundle["rules"]} != set(
        CATEGORIES
    ):
        raise ValueError("Expected five categories")
    for r in bundle["rules"]:
        validate_rule(r, sources)
        approval = r.get("review", {})
        if (
            not approval.get("reviewer")
            or not approval.get("at")
            or approval.get("digest")
            != digest({k: v for k, v in r.items() if k != "review"})
        ):
            raise ValueError("Unreviewed or modified rule")
        if r["source_versions"] != current:
            raise ValueError("Superseded sources")
    if bundle["version"] != digest(bundle["rules"])[:16]:
        raise ValueError("Invalid bundle version")
    archive = ROOT / "data/rules/versions" / f"{bundle['version']}.json"
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        with archive.open("x") as f:
            json.dump(bundle, f, indent=2)
    target = ROOT / "data/rules/active.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(bundle, indent=2))
    temporary.replace(target)
    load_rules()


def subscription_env():
    env = os.environ.copy()
    for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"):
        env.pop(key, None)
    return env


def check_auth(env):
    result = subprocess.run(
        ["claude", "auth", "status"],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    auth = json.loads(result.stdout)
    if (
        not auth.get("loggedIn")
        or auth.get("authMethod") != "claude.ai"
        or not auth.get("subscriptionType")
    ):
        raise RuntimeError(
            "Claude subscription authentication is required; API credentials are not supported."
        )


def prompt(sources):
    selected = []
    for s in sources.values():
        text = s["text"]
        if s["section"] == "12.22":
            text = text[text.index("AREA.\n1.\nBuilding Lines") :]
        selected.append(
            {"section": s["section"], "source_hash": s["content_hash"], "text": text}
        )
    from backend.synthesis import SCHEMA

    instructions = (
        SCHEMA
        + "\nExtract five ordinary R1-1 single-family constraints. Include the legacy fields version=1, operation=category, zone=R1-1, source_hash, quote, scope, exclusions, required_checks, required_inputs, unresolved_references for compatibility. Checks must cover ordinary_context and outside_hillside_coastal, frontage_reviewed for front yard, side_conditions_reviewed for side yard, and height_conditions_reviewed for height. Derive expressions, operands and dependencies from sources; never assume a value from a category name. Required input names use lot_depth_ft, lot_width_ft, lot_area_sqft, building_height_ft, roof_slope_percent where relevant. Return candidates only.\n"
    )
    return instructions + "\n" + json.dumps(selected, ensure_ascii=False)


def extract(output):
    env = subscription_env()
    check_auth(env)
    all_sources = source_records()
    current = json.loads((ROOT / "data/sources/current.json").read_text())
    sources = {h: all_sources[h] for h in current.values()}
    message = prompt(sources)
    result = subprocess.run(
        [
            "claude",
            "-p",
            "--tools",
            "",
            "--no-session-persistence",
            "--output-format",
            "json",
        ],
        input=message,
        env=env,
        capture_output=True,
        text=True,
        timeout=240,
        check=True,
    )
    envelope = json.loads(result.stdout)
    if envelope.get("is_error"):
        raise RuntimeError("Model extraction failed")
    raw = envelope.get("result", "").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    bundle = json.loads(raw)
    if len(bundle["rules"]) != 5 or {r["category"] for r in bundle["rules"]} != set(
        CATEGORIES
    ):
        raise ValueError("Expected five categories")
    errors = []
    for r in bundle["rules"]:
        r["source_versions"] = current
        try:
            validate_rule(r, sources)
        except ValueError as error:
            errors.append({"rule": r.get("id"), "error": str(error)})
    bundle["extraction"] = {
        "at": now(),
        "model_usage": envelope.get("modelUsage", {}),
        "instructions_hash": digest(message),
        "source_versions": list(sources),
        "validation": "rejected" if errors else "passed",
        "errors": errors,
        "auth_method": "claude.ai",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as f:
        json.dump(bundle, f, indent=2)


def review(candidate, reviewer, output):
    bundle = json.loads(candidate.read_text())
    sources = source_records()
    if len(bundle["rules"]) != 5 or {r["category"] for r in bundle["rules"]} != set(
        CATEGORIES
    ):
        raise ValueError("Expected five categories")
    current = json.loads((ROOT / "data/sources/current.json").read_text())
    for r in bundle["rules"]:
        if r.get("source_versions") != current:
            raise ValueError("Superseded candidate sources")
        validate_rule(r, sources)
        if "review" in r:
            raise ValueError("Already reviewed candidate")
        r["review"] = {"reviewer": reviewer, "at": now(), "digest": digest(r)}
    bundle["version"] = digest(bundle["rules"])[:16]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as f:
        json.dump(bundle, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    e = sub.add_parser("extract")
    e.add_argument("output", type=Path)
    r = sub.add_parser("review")
    r.add_argument("candidate", type=Path)
    r.add_argument("output", type=Path)
    r.add_argument("--reviewer", required=True)
    a = sub.add_parser("activate")
    a.add_argument("reviewed", type=Path)
    f = sub.add_parser("refresh")
    f.add_argument("section", choices=["12.03", "12.08", "12.21.1", "12.22"])
    f.add_argument("candidate", type=Path)
    args = parser.parse_args()
    if args.command == "extract":
        extract(args.output)
    elif args.command == "review":
        review(args.candidate, args.reviewer, args.output)
    elif args.command == "activate":
        activate(args.reviewed)
    else:
        snapshot(args.section, args.candidate)
