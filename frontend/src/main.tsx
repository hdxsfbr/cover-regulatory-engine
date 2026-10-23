import { ParcelResearch, type ResearchResult } from "./parcel-research";
import { ResearchGuidance } from "./research-guidance";
import { DesignComparison, type DesignImplication } from "./design-comparison";
import { Operator } from "./operator";
import { api } from "./api";
import { AutomaticReadings, EvidenceJob, ProjectWorkspace } from "./workspace";
import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import L from "leaflet";
import type { GeoJsonObject } from "geojson";
import "leaflet/dist/leaflet.css";
import "./style.css";

type Candidate = {
  properties: { AIN: string; APN: string; SitusFullAddress: string };
};
type Source = {
  status: string;
  origin: string;
  vintage?: string;
  source_url: string;
  retrieved_at: string;
  error?: string;
};
type Observation = {
  id: string;
  key: string;
  value: number;
  units: string;
  status: string;
  lot: string;
  tract: string;
  page: number;
  location: string;
  method: string;
  source_url?: string;
  document_hash: string;
  derivation?: string;
  review: { reviewer: string; scope: string };
};
export type Context = {
  research?: Record<string, ResearchResult>;
  sourced_facts?: Record<
    string,
    { state: string; evidence: string; limitation: string; source_url?: string }
  >;
  automatic_evidence?: {
    observations: {
      key: string;
      value: number;
      units: string;
      reason: string;
      page: number;
      source_url: string;
      confidence_reason: string;
      method?: string;
      assumptions?: string[];
      operands?: {
        role: string;
        length_ft: number;
        bearing: string;
        page: number;
        source_url: string;
        document_hash: string;
      }[];
      citations?: { url: string; section: string; source_hash: string }[];
      document_hash: string;
      region: number[];
    }[];
    uncertainties: string[];
  };
  document?: {
    status: string;
    map_id?: string;
    legal_description?: string;
    source_url?: string;
    vintage: string;
    origin: string;
    error?: string;
    content_hash?: string;
  };
  observations?: Observation[];
  snapshot_id: string;
  applicability_fingerprint: string | null;
  diagnostics: {
    code: string;
    message: string;
    sources: string[];
    retryable: boolean;
  }[];
  mode: string;
  parcel?: Candidate["properties"];
  jurisdiction: string;
  zoning_status: string;
  zone: string | null;
  regime: string | null;
  estimated_area_sqft?: number;
  issues: string[];
  zone_matches: { zone: string; fraction: number; possible_sliver: boolean }[];
  records: Record<string, Source>;
  map: GeoJsonObject;
};
type Constraint = {
  category: string;
  conditional?: {
    value: number;
    units: string;
    label: string;
    assumptions: string[];
    derivation: string;
  };
  status: string;
  value: number | null;
  units: string;
  confidence: string;
  reasons: string[];
  blockers?: {
    code: string;
    message: string;
    target: string;
    action: string;
    label: string;
  }[];
  derivation: string | null;
  rule_version: string | null;
  scope?: string;
  additional_constraint?: string;
  exclusions?: string[];
  inputs: Record<
    string,
    { value: number; origin: string; evidence: string; source_url?: string }
  >;
  citations: {
    url: string;
    section: string;
    quote: string;
    source_hash: string;
  }[];
};
type Assessment = {
  status: string;
  geometry?: GeoJsonObject & {
    metadata?: { status: string; scope: string };
    status?: string;
    reason?: string;
    features?: { properties?: { category?: string } }[];
  };
  summary?: {
    headline: string;
    notes: string[];
    issues: string[];
    design_implications: DesignImplication[];
  };
  coverage: string;
  constraints: Constraint[];
};
type Config = {
  mode: string;
  checks: Record<string, string>;
  input_bounds: Record<string, [number, number]>;
};
const names: Record<string, string> = {
  "front-yard": "Front yard",
  "side-yard": "Side yard · each side",
  "rear-yard": "Rear yard",
  height: "Building height",
  "floor-area": "Residential floor area",
  separation: "Building separation",
};
const inputNames: Record<string, string> = {
  proposed_area_sqft: "Proposed floor area (sq ft)",
  existing_floor_area_sqft: "Existing residential floor area (sq ft)",
  bedrooms: "Bedrooms",
  stories: "Stories",
  lot_depth_ft: "Legal lot depth (ft)",
  lot_width_ft: "Legal lot width (ft)",
  lot_area_sqft: "Legal lot area (sq ft)",
  building_height_ft: "Proposed building height (ft)",
  roof_slope_percent: "Uppermost roof slope (%)",
};

function readableBlocker(message: string) {
  const checks: Record<string, string> = {
    ordinary_context: "ordinary lot conditions and special restrictions",
    frontage_reviewed: "frontage and neighboring setbacks",
    side_conditions_reviewed: "side-yard exceptions",
    height_conditions_reviewed: "height exceptions",
    outside_hillside_coastal: "hillside and coastal applicability",
    accessory_location_reviewed: "accessory-building location",
    existing_primary_dwelling: "existing primary dwelling",
    new_detached: "new detached construction",
    has_kitchen: "kitchen facilities",
    near_transit: "transit proximity",
    roof_matches_primary: "roof alignment with the primary dwelling",
    coastal_requirements_resolved: "Coastal Act requirements",
    temporary_guests: "temporary guest use",
  };
  return message.replace(
    /\b[a-z][a-z0-9_]*\b/g,
    (key) => inputNames[key] || checks[key] || key,
  );
}

function ParcelMap({
  context,
  geometry,
  onSelect,
  selected,
}: {
  context: Context;
  geometry?: Assessment["geometry"];
  onSelect: (category: string) => void;
  selected: string | null;
}) {
  const el = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!el.current) return;
    const map = L.map(el.current, { scrollWheelZoom: false });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
      maxZoom: 20,
    }).addTo(map);
    const layer = L.geoJSON(context.map, {
      style: (f) => ({
        color: f?.properties.kind === "building" ? "#be7049" : "#254e42",
        weight: 2,
        fillColor: f?.properties.kind === "building" ? "#ce916a" : "#65937b",
        fillOpacity: 0.35,
      }),
    }).addTo(map);
    if (layer.getBounds().isValid())
      map.fitBounds(layer.getBounds(), { padding: [35, 35] });
    else map.setView([34.05, -118.25], 10);
    if (geometry && geometry.type === "FeatureCollection")
      L.geoJSON(geometry, {
        style: (f) => ({
          color: f?.properties.category === selected ? "#a44524" : "#c28124",
          weight: f?.properties.category === selected ? 6 : 3,
          fillOpacity: 0.12,
          dashArray:
            geometry.metadata?.status === "conditional" ? "6 5" : undefined,
        }),
        onEachFeature: (feature, layer) => {
          const p = feature.properties;
          layer.bindTooltip(
            `${p.category || "Setback envelope"}${p.setback_ft !== undefined ? `: ${p.setback_ft} ft` : ""} · ${geometry.metadata?.status || ""}`,
          );
          if (p.category) layer.on("click", () => onSelect(p.category));
        },
      }).addTo(map);
    return () => {
      map.remove();
    };
  }, [context, geometry, selected]);
  return (
    <div
      ref={el}
      className="map"
      role="img"
      aria-label="Selected parcel boundary and mapped building footprints"
    />
  );
}

function App() {
  const [selectedConstraint, setSelectedConstraint] = useState<string | null>(
    null,
  );
  const [config, setConfig] = useState<Config | null>(null);
  const [query, setQuery] = useState("");
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [context, setContext] = useState<Context | null>(null);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [busy, setBusy] = useState(false);
  const [selectedAin, setSelectedAin] = useState<string | null>(null);
  const [contextCurrent, setContextCurrent] = useState(false);
  const lookupController = useRef<AbortController | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [project, setProject] = useState("single-family");
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [checks, setChecks] = useState<Record<string, boolean>>({});
  const [note, setNote] = useState("");
  const [observationIds, setObservationIds] = useState<string[]>([]);
  const generation = useRef(0);
  const assessmentGeneration = useRef(0);
  useEffect(() => {
    api<Config>("/api/config")
      .then(setConfig)
      .catch((e) => setError(e.message));
  }, []);
  async function lookup(e: React.FormEvent) {
    e.preventDefault();
    const id = ++generation.current;
    assessmentGeneration.current++;
    setBusy(true);
    setError("");
    setNotice("");
    lookupController.current?.abort();
    setSelectedAin(null);
    setContextCurrent(false);
    setContext(null);
    setAssessment(null);
    setCandidates([]);
    setInputs({});
    setChecks({});
    setObservationIds([]);
    setNote("");
    try {
      const r = await api<{
        status: string;
        features: Candidate[];
        error?: string;
      }>(`/api/parcels?query=${encodeURIComponent(query)}`);
      if (id !== generation.current) return;
      if (r.status === "unavailable")
        throw new Error(
          r.error || "Parcel source unavailable. Retry this search.",
        );
      setCandidates(r.features);
      if (!r.features.length)
        setNotice(
          "No matching parcels. Try a shorter address or the ten-digit APN.",
        );
    } catch (e) {
      if (id === generation.current) setError((e as Error).message);
    } finally {
      if (id === generation.current) setBusy(false);
    }
  }
  async function select(ain: string, fresh = false) {
    const id = ++generation.current;
    assessmentGeneration.current++;
    lookupController.current?.abort();
    const controller = new AbortController();
    lookupController.current = controller;
    const previous = ain === selectedAin ? context : null;
    const refreshing = fresh && ain === selectedAin;
    setSelectedAin(ain);
    setBusy(true);
    setError("");
    setNotice("");
    setAssessment(null);
    setContextCurrent(false);
    if (!refreshing) {
      setContext(null);
      setInputs({});
      setChecks({});
      setObservationIds([]);
      setNote("");
    }
    try {
      const c = await api<Context>(
        `/api/parcels/${ain}/context?compact=true${fresh ? "&fresh=true" : ""}`,
        {
          signal: AbortSignal.any([
            controller.signal,
            AbortSignal.timeout(29000),
          ]),
        },
      );
      if (id !== generation.current) return;
      if (
        refreshing &&
        (!c.applicability_fingerprint ||
          c.applicability_fingerprint !== previous?.applicability_fingerprint)
      ) {
        setChecks({});
        setObservationIds([]);
        setNotice(
          "Applicability evidence changed or could not be confirmed. Review the source diagnostics and recheck applicability. Your dimensions and evidence note were kept.",
        );
      }
      setContext(c);
      setContextCurrent(true);
    } catch (e) {
      if (id === generation.current) {
        setChecks({});
        setObservationIds([]);
        setError((e as Error).message);
        if (refreshing)
          setNotice(
            "Refresh failed. Previous evidence is shown for reference only; applicability checks need review. Your dimensions and evidence note were kept.",
          );
      }
    } finally {
      if (id === generation.current) setBusy(false);
    }
  }
  useEffect(() => {
    if (context?.parcel?.AIN)
      document
        .getElementById("property-overview")
        ?.focus({ preventScroll: true });
  }, [context?.parcel?.AIN]);
  const replay = config?.mode === "fixture";
  const refreshLabel = replay
    ? "Replay recorded evidence"
    : "Refresh parcel sources";
  useEffect(() => {
    if (!context || !contextCurrent || busy) return;
    const id = ++assessmentGeneration.current;
    const controller = new AbortController();
    setAssessment(null);
    const timer = setTimeout(() => {
      const values = Object.fromEntries(
        Object.entries(inputs)
          .filter(([, v]) => v !== "")
          .map(([k, v]) => [k, Number(v)]),
      );
      api<Assessment>("/api/assessments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: AbortSignal.any([
          controller.signal,
          AbortSignal.timeout(29000),
        ]),
        body: JSON.stringify({
          snapshot_id: context.snapshot_id,
          project_type: project,
          inputs: values,
          checks,
          evidence_note: note,
          observation_ids: observationIds,
        }),
      })
        .then((r) => {
          if (id === assessmentGeneration.current) {
            setAssessment(r);
            setError("");
          }
        })
        .catch((e) => {
          if (!controller.signal.aborted && id === assessmentGeneration.current)
            setError(e.message);
        });
    }, 300);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [
    context,
    contextCurrent,
    busy,
    project,
    inputs,
    checks,
    note,
    observationIds,
  ]);
  const conflict = assessment?.summary?.design_implications?.find(
    (d) => d.status === "exceeds-limit",
  );
  function focusTarget(target: string) {
    const el = document.getElementById(target);
    if (!el) return;
    let parent: HTMLElement | null = el;
    while (parent) {
      if (parent instanceof HTMLDetailsElement) parent.open = true;
      parent = parent.parentElement;
    }
    el.scrollIntoView({ behavior: "auto", block: "center" });
    el.focus();
  }
  return (
    <>
      <header>
        <a
          className="brand"
          href="/"
          aria-label="Cover property intelligence home"
        >
          <img
            src="/brand/cover-logo.svg"
            alt="Cover"
            width="124"
            height="32"
          />
          <span className="brand-product">
            Property
            <br />
            intelligence
          </span>
        </a>
        <span className="header-note">
          LOS ANGELES ·{" "}
          {config ? (replay ? "RECORDED DEMO" : "LIVE SOURCES") : "CONNECTING"}
        </span>
      </header>
      <main className={context ? "assessment-workspace" : "search-workspace"}>
        {!context && (
          <section className="intro">
            <p className="eyebrow">FROM PARCEL TO POSSIBILITY</p>
            <h1>
              Know the ground
              <span>before you build.</span>
            </h1>
            <p className="lede">
              Explore a property’s zoning, mapped buildings, and supported
              residential constraints—with the evidence behind each answer.
            </p>
          </section>
        )}
        <details
          className="property-search"
          open={!context || undefined}
          id="property-search"
        >
          <summary>Change property</summary>
          <section className="search-card">
            <form onSubmit={lookup}>
              <label htmlFor="address">
                Property address or assessor parcel number
              </label>
              <div className="search-row">
                <input
                  id="address"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g. 6754 Rhea Ct or 2126-037-055"
                  required
                  maxLength={160}
                />
                <button
                  type="submit"
                  disabled={busy && !selectedAin}
                  aria-busy={busy && !selectedAin}
                >
                  {busy && !selectedAin ? (
                    <>
                      <span className="spinner" aria-hidden="true" /> Searching…
                    </>
                  ) : (
                    "Find property →"
                  )}
                </button>
              </div>
            </form>
            <p className="muted">
              LA City residential parcels ·{" "}
              {config?.mode === "fixture"
                ? "Recorded demonstration data"
                : config
                  ? "Live data · Public County and City sources"
                  : "Checking data mode…"}
            </p>
          </section>
        </details>
        {!context && (
          <p className="start-help">
            Search for a property, then choose a result to open its assessment.{" "}
            <button
              className="text-button"
              onClick={() => focusTarget("project-tools")}
            >
              Open a saved project
            </button>
          </p>
        )}
        {replay && (
          <p className="notice">
            Recorded demo: replay loads the same saved evidence and cannot
            obtain updated zoning. Start the server in live mode for new
            official-source queries.
          </p>
        )}
        <div aria-live="polite">
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          {notice && <p className="notice">{notice}</p>}
          {busy && (
            <p className="notice loading-status" role="status">
              <span className="spinner" aria-hidden="true" />
              {selectedAin
                ? "Loading parcel, zoning and building evidence…"
                : "Searching County parcel records…"}
              <span className="muted">
                {replay
                  ? "Loading saved evidence."
                  : "Live sources can take up to 25 seconds."}
              </span>
            </p>
          )}
        </div>
        {selectedAin && (
          <div className="recovery">
            <p>
              {context?.mode === "fixture"
                ? "Recorded result"
                : context
                  ? "Selected property"
                  : "Selected parcel"}{" "}
              · APN {selectedAin}
            </p>
            {context && !contextCurrent && (
              <p className="notice">
                Previous evidence — assessment pending a successful refresh.
              </p>
            )}
            <button
              className="secondary"
              disabled={busy}
              aria-busy={busy}
              onClick={() => select(selectedAin, true)}
            >
              {busy ? (
                <>
                  <span className="spinner" aria-hidden="true" /> Loading
                  sources…
                </>
              ) : (
                refreshLabel
              )}
            </button>
          </div>
        )}
        {candidates.length > 0 && !context && (
          <section className="candidates" aria-label="Matching parcels">
            <h2>Choose a property</h2>
            <p>Select a result to load its map and assessment.</p>
            {candidates.map((c) => (
              <button
                className="candidate"
                key={c.properties.AIN}
                aria-busy={busy && selectedAin === c.properties.AIN}
                disabled={busy && selectedAin === c.properties.AIN}
                onClick={() => select(c.properties.AIN)}
              >
                <strong>
                  {c.properties.SitusFullAddress || "Address unavailable"}
                </strong>
                <span>
                  {busy && selectedAin === c.properties.AIN ? (
                    <>
                      <span className="spinner" aria-hidden="true" /> Loading
                      property…
                    </>
                  ) : (
                    <>APN {c.properties.APN} · Open assessment →</>
                  )}
                </span>
              </button>
            ))}
          </section>
        )}
        {context && (
          <>
            <section
              className="property-title"
              id="property-overview"
              aria-label="Selected property"
              tabIndex={-1}
            >
              <div>
                <p className="eyebrow">PROPERTY OVERVIEW</p>
                <h2>
                  {context.parcel?.SitusFullAddress ||
                    "Parcel context unavailable"}
                </h2>
                <p>
                  APN {context.parcel?.APN || selectedAin} ·{" "}
                  {context.jurisdiction}
                </p>
              </div>
              <label>
                Project type
                <select
                  value={project}
                  onChange={(e) => setProject(e.target.value)}
                >
                  <option value="single-family">Single-family home</option>
                  <option value="adu">ADU</option>
                  <option value="guest-house">Guest house</option>
                </select>
              </label>
            </section>
            <nav className="workspace-nav" aria-label="Assessment sections">
              <button onClick={() => focusTarget("assessment-results")}>
                Results
              </button>
              <button onClick={() => focusTarget("input-panel")}>
                Edit project inputs
              </button>
              <button onClick={() => focusTarget("parcel-research")}>
                Property research
              </button>
              <button onClick={() => focusTarget("parcel-evidence")}>
                Inspect evidence
              </button>
              <button onClick={() => focusTarget("project-tools")}>
                Save / compare / ask
              </button>
            </nav>
            <EvidenceJob
              key={context.parcel?.AIN}
              context={context}
              onComplete={(next) =>
                setContext((current) =>
                  current && current.parcel?.AIN === next.parcel?.AIN
                    ? { ...next, research: current.research }
                    : current,
                )
              }
              onInspect={() => focusTarget("parcel-evidence")}
              onResults={() => focusTarget("assessment-results")}
              onInputs={() => focusTarget("input-panel")}
              resultCounts={
                assessment
                  ? {
                      evaluated: assessment.constraints.filter(
                        (r) => r.value !== null,
                      ).length,
                      total: assessment.constraints.length,
                      conditional: assessment.constraints.filter(
                        (r) => r.conditional,
                      ).length,
                    }
                  : undefined
              }
            />
            <section className="overview">
              <ParcelMap
                context={context}
                geometry={assessment?.geometry}
                selected={selectedConstraint}
                onSelect={(category) => {
                  setSelectedConstraint(category);
                  focusTarget(`constraint-${category}`);
                }}
              />
              <aside>
                {assessment?.summary && (
                  <div className="assessment-summary">
                    <p className="eyebrow">ASSESSMENT OVERVIEW</p>
                    <h3>{assessment.summary.headline}</h3>
                    {assessment.summary.design_implications?.map((d, i) => (
                      <p key={i}>
                        <strong>{d.status.replaceAll("-", " ")}:</strong>{" "}
                        {d.message}
                      </p>
                    ))}
                  </div>
                )}
                <p className="next-step">
                  <strong>Next step</strong>
                  <br />
                  {!contextCurrent
                    ? "Refresh parcel sources to resume this assessment."
                    : !assessment
                      ? "Calculating with the available evidence…"
                      : conflict
                        ? `Resolve the ${names[conflict.category]?.toLowerCase() || conflict.category} conflict before comparing or saving this design.`
                        : assessment.constraints.some((r) => r.blockers?.length)
                          ? "Review the unresolved items below. Each result links to the input or evidence it needs."
                          : "Review your results and assumptions, then save a scenario to compare options or ask a follow-up."}
                </p>
                {assessment && contextCurrent && (
                  <button
                    className="secondary"
                    onClick={() => {
                      if (conflict) {
                        focusTarget(
                          conflict.category === "height"
                            ? "input-building_height_ft"
                            : "input-proposed_area_sqft",
                        );
                        return;
                      }
                      const blocker = assessment.constraints.flatMap(
                        (r) => r.blockers || [],
                      )[0];
                      if (blocker?.action === "retry")
                        void select(selectedAin!, true);
                      else focusTarget(blocker?.target || "project-tools");
                    }}
                  >
                    {conflict
                      ? conflict.category === "height"
                        ? "Edit proposed height"
                        : "Edit proposed floor area"
                      : assessment.constraints.some((r) => r.blockers?.length)
                        ? "Review next item"
                        : "Save this scenario"}
                  </button>
                )}
                <p className="eyebrow">SOURCE FACTS</p>
                <dl>
                  <dt>Zoning</dt>
                  <dd>{context.zone || "Needs review"}</dd>
                  <dt>Code regime</dt>
                  <dd>{context.regime || "Unresolved"}</dd>
                  <dt>Geometry-derived area</dt>
                  <dd>
                    {context.estimated_area_sqft?.toLocaleString(undefined, {
                      maximumFractionDigits: 0,
                    }) || "Unknown"}{" "}
                    sq ft <small>Estimate, not surveyed lot area</small>
                  </dd>
                </dl>
                {context.zone_matches.map((z, i) => (
                  <p key={i} className="zone">
                    {z.zone}
                    <span>
                      {(z.fraction * 100).toFixed(4)}% overlap
                      {z.possible_sliver ? " · possible boundary sliver" : ""}
                    </span>
                  </p>
                ))}
                <p className="muted">
                  Green: parcel · Terracotta: mapped buildings. Building
                  footprints are from the 2020 dataset, not confirmation of
                  current or permitted structures.
                </p>
              </aside>
            </section>
            <section
              className="assessment"
              id="assessment-results"
              tabIndex={-1}
            >
              <div className="section-title">
                <div>
                  <p className="eyebrow">RESULTS FOR YOUR PROJECT</p>
                  <h2>Constraints & next steps</h2>
                </div>
              </div>
              <p className="muted">
                <span id="coverage" tabIndex={-1}>
                  {assessment?.coverage || "Evaluating available evidence…"}
                </span>
              </p>
              {(context.diagnostics || []).map((d, i) => (
                <p className="notice" key={i} data-reason={d.code}>
                  {d.message}{" "}
                  {d.sources.map((name) => (
                    <a
                      key={name}
                      href={context.records[name]?.source_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {name} ↗{" "}
                    </a>
                  ))}
                </p>
              ))}
              {assessment?.summary?.notes.map((n, i) => (
                <p className="notice" key={i}>
                  {n}
                </p>
              ))}
              {assessment?.geometry?.type === "FeatureCollection" && (
                <div>
                  <p>
                    {assessment.geometry.metadata?.status} setback envelope ·{" "}
                    {assessment.geometry.metadata?.scope}
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      const blob = new Blob(
                        [JSON.stringify(assessment.geometry, null, 2)],
                        { type: "application/geo+json" },
                      );
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `${selectedAin}-setbacks.geojson`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                  >
                    Export setback GeoJSON
                  </button>
                </div>
              )}
              {assessment?.geometry?.status === "withheld" && (
                <p>Setback geometry: {assessment.geometry.reason}</p>
              )}
              <div className="constraints">
                {assessment?.constraints.map((r) => (
                  <article
                    className="constraint"
                    id={`constraint-${r.category}`}
                    tabIndex={-1}
                    key={r.category}
                  >
                    <div className="constraint-label">
                      <h3>{names[r.category] || r.category}</h3>
                      <p className="muted">
                        {r.category.includes("yard")
                          ? "Required setback"
                          : r.category === "separation"
                            ? "Required distance between buildings"
                            : "Limit within selected scope"}
                      </p>
                      {assessment.geometry?.features?.some(
                        (f) => f.properties?.category === r.category,
                      ) && (
                        <button
                          type="button"
                          className="text-button"
                          onClick={() => {
                            setSelectedConstraint(r.category);
                            document
                              .querySelector(".map")
                              ?.scrollIntoView({ block: "center" });
                          }}
                        >
                          Locate on map
                        </button>
                      )}
                    </div>
                    <div className="constraint-result">
                      <p className="value">
                        {r.value !== null ? (
                          <>
                            {r.value.toLocaleString(undefined, {
                              maximumFractionDigits: 2,
                            })}
                            <span> {r.units}</span>
                          </>
                        ) : (
                          "Unresolved"
                        )}
                      </p>
                      <span className={`badge ${r.status}`}>
                        {r.status === "evaluated"
                          ? "Rule evaluated"
                          : r.status.replaceAll("-", " ")}
                      </span>
                    </div>
                    <div className="constraint-detail">
                      <DesignComparison
                        result={assessment.summary?.design_implications?.find(
                          (d) => d.category === r.category,
                        )}
                        units={r.units}
                      />
                      {r.conditional && (
                        <details className="conditional">
                          <summary>
                            Explore conditional result: {r.conditional.value}{" "}
                            {r.conditional.units}
                          </summary>
                          <p>{r.conditional.label}</p>
                          <p>{r.conditional.derivation}</p>
                          <ul>
                            {r.conditional.assumptions.map((a, i) => (
                              <li key={i}>{a}</li>
                            ))}
                          </ul>
                        </details>
                      )}
                      {!!r.blockers?.length && (
                        <div
                          className="blockers"
                          aria-label={`${names[r.category]} next steps`}
                        >
                          {r.blockers.slice(0, 1).map((b, i) => (
                            <div className="blocker" key={`${b.code}-${i}`}>
                              <p>{readableBlocker(b.message)}</p>
                              <button
                                type="button"
                                disabled={busy || !contextCurrent}
                                onClick={() =>
                                  b.action === "retry"
                                    ? select(selectedAin!, true)
                                    : focusTarget(b.target)
                                }
                              >
                                {b.label}
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                      <details>
                        <summary>Evidence & explanation</summary>
                        <p>Confidence: {r.confidence}</p>
                        {r.blockers?.slice(1).map((b, i) => (
                          <div className="blocker" key={i}>
                            <p>{readableBlocker(b.message)}</p>
                            <button
                              type="button"
                              disabled={busy || !contextCurrent}
                              onClick={() =>
                                b.action === "retry"
                                  ? select(selectedAin!, true)
                                  : focusTarget(b.target)
                              }
                            >
                              {b.label}
                            </button>
                          </div>
                        ))}
                        {r.reasons.map((reason, i) => (
                          <p key={i}>{reason}</p>
                        ))}
                        {r.scope && <p>{r.scope}</p>}
                        {r.rule_version && (
                          <p className="muted">
                            Rule version: {r.rule_version}
                          </p>
                        )}
                        {r.exclusions && (
                          <details>
                            <summary>Conditions outside this rule</summary>
                            <ul>
                              {r.exclusions.map((item) => (
                                <li key={item}>{item}</li>
                              ))}
                            </ul>
                          </details>
                        )}
                        {r.derivation && (
                          <p className="calculation">{r.derivation}</p>
                        )}
                        {r.additional_constraint && (
                          <p>{r.additional_constraint}</p>
                        )}
                        {Object.entries(r.inputs).map(([k, v]) => (
                          <p key={k}>
                            {inputNames[k]}: {v.value} · {v.origin}
                            <br />
                            {v.evidence}
                            {v.source_url && (
                              <a
                                href={v.source_url}
                                target="_blank"
                                rel="noreferrer"
                              >
                                {" "}
                                Open dimension source ↗
                              </a>
                            )}
                          </p>
                        ))}
                        {r.citations.map((citation, i) => (
                          <div className="citation" key={i}>
                            <a
                              href={citation.url}
                              target="_blank"
                              rel="noreferrer"
                            >
                              {citation.section.startsWith("HCD")
                                ? citation.section
                                : `LAMC §${citation.section}`}{" "}
                              ↗
                            </a>
                            <blockquote>{citation.quote}</blockquote>
                            <small>
                              Source version:{" "}
                              {citation.source_hash.slice(0, 12)}
                            </small>
                          </div>
                        ))}
                      </details>
                    </div>
                  </article>
                ))}
              </div>
            </section>
            <ParcelResearch
              context={context}
              onResult={(snapshot, result) =>
                setContext((current) =>
                  current?.snapshot_id === snapshot &&
                  current.parcel?.AIN === result.ain
                    ? {
                        ...current,
                        research: {
                          ...current.research,
                          [result.source]: result,
                        },
                      }
                    : current,
                )
              }
            />
            <details className="input-panel" id="input-panel" tabIndex={-1}>
              <summary>Project inputs & unresolved checks</summary>
              <p>
                Enter your proposed design and document any facts you can
                establish. Leave professional checks unknown unless you have
                supporting evidence; they are not a checklist to complete just
                to obtain a number. Calculations using your assertions carry
                medium confidence.
              </p>
              <div className="input-grid">
                {Object.entries(config?.input_bounds || {})
                  .filter(([key]) =>
                    project === "adu"
                      ? [
                          "building_height_ft",
                          "proposed_area_sqft",
                          "bedrooms",
                        ].includes(key)
                      : project === "guest-house"
                        ? ![
                            "existing_floor_area_sqft",
                            "roof_slope_percent",
                          ].includes(key)
                        : true,
                  )
                  .map(([key, [min, max]]) => (
                    <label key={key}>
                      {inputNames[key]}
                      {["bedrooms", "stories"].includes(key) && (
                        <small className="research-guidance">
                          Context only — saved with this design; does not change
                          current rule calculations.
                        </small>
                      )}
                      <input
                        id={`input-${key}`}
                        aria-label={inputNames[key]}
                        disabled={context.observations?.some(
                          (o) => o.key === key && observationIds.includes(o.id),
                        )}
                        type="number"
                        min={min}
                        max={max}
                        step="any"
                        value={inputs[key] || ""}
                        onChange={(e) =>
                          setInputs({ ...inputs, [key]: e.target.value })
                        }
                      />
                    </label>
                  ))}
              </div>
              {Object.entries(config?.checks || {})
                .filter(([key]) =>
                  project === "single-family"
                    ? [
                        "ordinary_context",
                        "outside_hillside_coastal",
                        "frontage_reviewed",
                        "side_conditions_reviewed",
                        "height_conditions_reviewed",
                      ].includes(key)
                    : project === "adu"
                      ? [
                          "existing_primary_dwelling",
                          "new_detached",
                          "has_kitchen",
                          "near_transit",
                          "roof_matches_primary",
                          "coastal_requirements_resolved",
                        ].includes(key)
                      : [
                          "existing_primary_dwelling",
                          "new_detached",
                          "has_kitchen",
                          "rented",
                          "temporary_guests",
                          "accessory_location_reviewed",
                          "ordinary_context",
                        ].includes(key),
                )
                .map(([key, label]) => (
                  <label className="check" key={key}>
                    {![
                      "ordinary_context",
                      "outside_hillside_coastal",
                      "frontage_reviewed",
                      "side_conditions_reviewed",
                      "height_conditions_reviewed",
                    ].includes(key) ? (
                      <select
                        aria-label={label}
                        value={
                          checks[key] === undefined
                            ? "unknown"
                            : checks[key]
                              ? "yes"
                              : "no"
                        }
                        onChange={(e) => {
                          const next = { ...checks };
                          if (e.target.value === "unknown") delete next[key];
                          else next[key] = e.target.value === "yes";
                          setChecks(next);
                        }}
                      >
                        <option value="unknown">
                          Use source evidence if available
                        </option>
                        <option value="yes">Yes</option>
                        <option value="no">No</option>
                      </select>
                    ) : (
                      <input
                        type="checkbox"
                        id={`check-${key}`}
                        aria-label={label}
                        checked={
                          checks[key] ??
                          (key === "outside_hillside_coastal" &&
                            context.sourced_facts?.outside_hillside_coastal
                              ?.state === "true")
                        }
                        onChange={(e) =>
                          setChecks({ ...checks, [key]: e.target.checked })
                        }
                      />
                    )}
                    <span>
                      {label}
                      <ResearchGuidance
                        context={context}
                        check={key}
                        overridden={checks[key] !== undefined}
                      />
                    </span>
                  </label>
                ))}
              <label>
                Evidence or basis for these inputs
                <textarea
                  id="evidence-note"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  maxLength={2000}
                  placeholder="Identify plans, surveys, source documents, or explicitly label a hypothetical scenario."
                />
              </label>
            </details>
            <details
              className="parcel-evidence"
              id="parcel-evidence"
              tabIndex={-1}
              aria-labelledby="parcel-evidence-heading"
            >
              <summary id="parcel-evidence-heading">
                Public parcel evidence · maps, measurements & screening
              </summary>
              <AutomaticReadings context={context} />
              {context.document && (
                <>
                  <p>
                    <strong>
                      Assessor map{" "}
                      {context.document.map_id || "reference unavailable"}
                    </strong>{" "}
                    · {context.document.status} · {context.document.origin}
                  </p>
                  <p>{context.document.legal_description}</p>
                  <p>
                    Document vintage: {context.document.vintage}. Retrieval does
                    not establish that later recorded changes are absent.
                  </p>
                  {context.document.source_url && (
                    <a
                      href={context.document.source_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open County assessor map ↗
                    </a>
                  )}
                  {context.document.status === "unavailable" && (
                    <p role="status">
                      The document could not be retrieved.{" "}
                      <button
                        type="button"
                        disabled={busy}
                        onClick={() => select(selectedAin!, true)}
                      >
                        Retry document sources
                      </button>
                    </p>
                  )}
                </>
              )}
              <p>
                Map readings are reviewed transcriptions, not verified legal lot
                dimensions. Accept a measurement only if it is appropriate for
                your assessment; explain that basis below. GIS area remains an
                estimate.
              </p>
              {!context.observations?.length && context.mode === "fixture" && (
                <p>
                  No reviewed dimensions are available for this parcel.{" "}
                  {context.document?.status === "available"
                    ? "The public sheet is available for review; supply dimensions and cite the relevant lot and page below."
                    : "Supply documented dimensions and their basis below."}
                </p>
              )}
              <div className="observation-grid">
                {context.observations?.map((o) => (
                  <article className="observation" key={o.id}>
                    <h3>{inputNames[o.key].replace("Legal", "Map")}</h3>
                    <p className="measurement">
                      {o.value.toLocaleString()} {o.units}
                    </p>
                    <p>
                      {o.method === "derived-rectangle"
                        ? "Derived area"
                        : "Map measurement"}{" "}
                      · {o.status}
                    </p>
                    <p>
                      Tract {o.tract}, lot {o.lot}, page {o.page}. {o.location}
                    </p>
                    {o.derivation && <p>{o.derivation}</p>}
                    <p className="muted">Reviewed by {o.review.reviewer}</p>
                    <label className="check">
                      <input
                        type="checkbox"
                        checked={observationIds.includes(o.id)}
                        disabled={
                          busy ||
                          !contextCurrent ||
                          o.status !== "reviewed" ||
                          !!inputs[o.key]
                        }
                        onChange={(e) =>
                          setObservationIds(
                            e.target.checked
                              ? [...observationIds, o.id]
                              : observationIds.filter((id) => id !== o.id),
                          )
                        }
                      />
                      Use{" "}
                      {inputNames[o.key].replace("Legal", "map").toLowerCase()}{" "}
                      for this assessment
                    </label>
                    {!!inputs[o.key] && (
                      <p>
                        Clear the manual value below to select this map
                        measurement.
                      </p>
                    )}
                  </article>
                ))}
              </div>
              {context.sourced_facts?.existing_primary_dwelling && (
                <div>
                  <h3>Reported property use</h3>
                  <p>
                    {context.sourced_facts.existing_primary_dwelling.evidence}
                  </p>
                  <p>
                    {context.sourced_facts.existing_primary_dwelling.limitation}
                  </p>
                </div>
              )}
              <h3>Applicability screening</h3>
              <p>
                These named layers are screening evidence. No match does not
                establish absence of every hillside or coastal restriction.
              </p>
              {["Hillside Ordinance", "Coastal Commission Permit Area"].map(
                (name) => (
                  <p key={name}>
                    <strong>{name}:</strong>{" "}
                    {context.records[name]?.status || "not-checked"}
                    {context.records[name] && (
                      <>
                        {" "}
                        ·{" "}
                        <a
                          href={context.records[name].source_url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Inspect source ↗
                        </a>{" "}
                        · {context.records[name].origin} · vintage{" "}
                        {context.records[name].vintage || "unknown"}
                      </>
                    )}
                  </p>
                ),
              )}
            </details>

            <details className="sources" id="source-evidence" tabIndex={-1}>
              <summary>Sources checked & data freshness</summary>
              <p>
                These selected layers are not an exhaustive check of all
                property restrictions.
              </p>
              {Object.entries(context.records).map(([name, r]) => (
                <div className="source-row" key={name}>
                  <a href={r.source_url} target="_blank" rel="noreferrer">
                    {name} ↗
                  </a>
                  <span>
                    {r.status} · {r.origin}
                  </span>
                  <small>
                    Retrieved {new Date(r.retrieved_at).toLocaleString()} ·
                    Vintage {r.vintage || "unknown"}
                    {r.error ? ` · ${r.error}` : ""}
                  </small>
                  {r.status === "unavailable" && selectedAin && (
                    <button
                      className="secondary"
                      disabled={busy}
                      onClick={() => select(selectedAin!, true)}
                    >
                      {busy ? (
                        <>
                          <span className="spinner" aria-hidden="true" />{" "}
                          Loading sources…
                        </>
                      ) : (
                        refreshLabel
                      )}
                    </button>
                  )}
                </div>
              ))}
            </details>
          </>
        )}
        <details className="project-tools" id="project-tools" tabIndex={-1}>
          <summary>Saved projects, comparison & follow-up</summary>
          <ProjectWorkspace
            context={context}
            projectType={project}
            inputs={inputs}
            checks={checks}
            note={note}
            observationIds={observationIds}
            onRestore={(c, p, i, k, n, ids) => {
              generation.current++;
              assessmentGeneration.current++;
              lookupController.current?.abort();
              setBusy(false);
              setCandidates([]);
              setContext(c);
              setContextCurrent(true);
              setSelectedAin(c.parcel?.AIN || null);
              setProject(p);
              setInputs(i);
              setChecks(k);
              setNote(n);
              setObservationIds(ids);
            }}
          />
        </details>
      </main>
      <footer>
        Cover · Home Building Regulatory Engine{" "}
        <a href="/operator">Operator review</a>
        <span>Evidence first. Possibilities second.</span>
      </footer>
    </>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {window.location.pathname === "/operator" ? <Operator /> : <App />}
  </React.StrictMode>,
);
