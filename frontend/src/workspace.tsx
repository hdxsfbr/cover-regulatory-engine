import { DesignComparison, type DesignImplication } from "./design-comparison";
import { useEffect, useState, useRef } from "react";
import { api } from "./api";
import type { Context } from "./main";

type Job = {
  id: string;
  status: string;
  stage: string;
  error?: string;
  result?: { elapsed_seconds: number };
};
export function EvidenceJob({
  context,
  onComplete,
  onInspect,
  onResults,
  onInputs,
  resultCounts,
}: {
  context: Context;
  onComplete: (c: Context) => void;
  onInspect: () => void;
  onResults: () => void;
  onInputs: () => void;
  resultCounts?: { evaluated: number; total: number; conditional: number };
}) {
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const [starting, setStarting] = useState(false);
  useEffect(() => {
    if (
      context.mode !== "live" ||
      context.document?.status !== "available" ||
      context.automatic_evidence
    )
      return;
    let stopped = false;
    let timer: ReturnType<typeof setTimeout>;
    setStarting(true);
    setError("");
    const poll = async (id: string) => {
      try {
        const j = await api<Job>(`/api/evidence-jobs/${id}`);
        if (stopped) return;
        setJob(j);
        if (j.status === "completed") {
          const c = await api<Context>(`/api/evidence-jobs/${id}/context`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ snapshot_id: context.snapshot_id }),
          });
          if (!stopped) onComplete(c);
        } else if (!["failed", "cancelled"].includes(j.status))
          timer = setTimeout(() => poll(id), 1200);
      } catch (e) {
        if (!stopped) setError((e as Error).message);
      }
    };
    api<Job>("/api/evidence-jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        snapshot_id: context.snapshot_id,
        retry: attempt > 0,
      }),
    })
      .then((j) => {
        if (!stopped) {
          setJob(j);
          setStarting(false);
          void poll(j.id);
        }
      })
      .catch((e) => {
        if (!stopped) {
          setError(e.message);
          setStarting(false);
        }
      });
    return () => {
      stopped = true;
      clearTimeout(timer);
    };
  }, [context.snapshot_id, context.mode, context.document?.status, attempt]);
  const active =
    starting || (!!job && ["queued", "running"].includes(job.status));
  const stages: Record<string, [string, string]> = {
    queued: [
      "Waiting for the map reader",
      "Parcel facts and preliminary rules are available below.",
    ],
    starting: [
      "Preparing the map reading",
      "Finding documents for this parcel.",
    ],
    "finding-tract-map": [
      "Finding the recorded tract map",
      "Looking for the source that identifies the lot and its dimensions.",
    ],
    rendering: [
      "Preparing source pages",
      "Preparing assessor and recorded-map pages for reading.",
    ],
    "reading-map": [
      "Reading lot boundaries and dimensions",
      "Measurements remain pending until identity, units and geometry checks finish.",
    ],
    validating: [
      "Checking the map reading",
      "Checking parcel identity, units and agreement with mapped geometry.",
    ],
    saving: [
      "Adding checked measurements",
      "Dependent constraints will update automatically; your design inputs are retained.",
    ],
  };
  const stage =
    stages[job?.status === "queued" ? "queued" : job?.stage || "starting"] ||
    stages.starting;
  const relevant = context.mode === "live";
  return (
    <div className="document-job">
      {relevant && (
        <section
          className="progressive-results"
          aria-label="Assessment progress"
        >
          <h3>
            {context.automatic_evidence
              ? "Map reading finished — review the updated assessment"
              : "Start with these findings"}
          </h3>
          <dl className="available-facts">
            <div>
              <dt>Property identified</dt>
              <dd>
                {context.parcel?.SitusFullAddress ||
                  context.parcel?.APN ||
                  "Identity needs review"}
              </dd>
            </div>
            <div>
              <dt>Zoning from public sources</dt>
              <dd>
                {context.zoning_status === "resolved"
                  ? `${context.zone} · ${context.regime}`
                  : "Unresolved — inspect source evidence"}
              </dd>
            </div>
            <div>
              <dt>Parcel & building map</dt>
              <dd>
                {context.records.Parcels?.status === "matched"
                  ? "Parcel boundary available. "
                  : "Parcel boundary needs review. "}
                {context.records.Buildings?.status === "matched"
                  ? "Published building footprints available below."
                  : context.records.Buildings?.status === "no-match"
                    ? "No footprints returned by the published dataset."
                    : "Building footprint source unavailable or not checked."}
              </dd>
            </div>
            <div>
              <dt>Preliminary constraints</dt>
              <dd>
                {resultCounts
                  ? `${resultCounts.evaluated} of ${resultCounts.total} have values from available evidence; ${resultCounts.conditional} conditional paths to inspect`
                  : "Calculating from available evidence…"}
              </dd>
            </div>
          </dl>
          <p>
            These are findings within the selected rule scope, not a full
            buildability determination. Map dimensions and legal applicability
            checks are separate.
          </p>
          {!context.automatic_evidence && (
            <p>
              {context.document?.status !== "available" && (
                <>
                  <strong>Map document unavailable.</strong> Inspect source
                  evidence or refresh parcel sources to retry.{" "}
                </>
              )}
              <strong>Still needed:</strong> checked map dimensions where
              available. You can enter your design and inspect conditional
              results now.
            </p>
          )}
          <div className="progress-actions">
            <button type="button" className="secondary" onClick={onResults}>
              View available results
            </button>
            <button type="button" className="secondary" onClick={onInputs}>
              {active || starting
                ? "Enter design while maps load"
                : "Edit design inputs"}
            </button>
          </div>
        </section>
      )}

      {active && (
        <p role="status">
          <span className="spinner" aria-hidden="true" /> Reading public map:{" "}
          {stage[0]}. <small>{stage[1]}</small>
        </p>
      )}
      {active && job && (
        <button
          type="button"
          onClick={async () => {
            try {
              setJob(
                await api<Job>(`/api/evidence-jobs/${job.id}/cancel`, {
                  method: "POST",
                }),
              );
            } catch (e) {
              setError((e as Error).message);
            }
          }}
        >
          Cancel map reading
        </button>
      )}
      {(error || job?.error) && (
        <p role="alert">
          Map reading could not finish. Available parcel facts and preliminary
          results are still usable. {error || job?.error}
        </p>
      )}
      {job?.status === "cancelled" && !context.automatic_evidence && (
        <p role="status">
          Map reading stopped. Available findings and your design inputs are
          retained.
        </p>
      )}
      {(error || (job && ["failed", "cancelled"].includes(job.status))) && (
        <button type="button" onClick={() => setAttempt((x) => x + 1)}>
          Retry automatic map reading
        </button>
      )}
      {context.automatic_evidence && (
        <p className="reading-complete">
          Public map reading complete ·{" "}
          {context.automatic_evidence.observations.length} measurements
          available.{" "}
          {context.automatic_evidence.observations.length === 0
            ? "No usable dimensions were established. Inspect the reading uncertainties; remaining checks still need evidence. "
            : context.automatic_evidence.observations
                .map(
                  (o) => `${o.key.replaceAll("_", " ")}: ${o.value} ${o.units}`,
                )
                .join(" · ") +
              ". Remaining applicability checks still need evidence. "}
          <button className="text-button" onClick={onInspect}>
            Inspect map readings
          </button>
        </p>
      )}
    </div>
  );
}

export function AutomaticReadings({ context }: { context: Context }) {
  if (!context.automatic_evidence) return null;
  return (
    <div className="map-readings">
      {context.automatic_evidence && (
        <>
          <h3>Automatic map readings</h3>
          <p>
            These readings were checked against parcel geometry. They are used
            automatically and remain identified as machine interpretations.
          </p>
          <div className="observation-grid">
            {context.automatic_evidence.observations.map((o) => (
              <article className="observation" key={o.key}>
                <h4>
                  {o.method === "derived-midpoint-depth"
                    ? "Lot depth · derived"
                    : o.key.replaceAll("_", " ")}
                </h4>
                <p className="measurement">
                  {o.method === "derived-midpoint-depth" ? "≈ " : ""}
                  {o.value} {o.units}
                </p>
                <p>{o.reason}</p>
                <p>{o.confidence_reason}</p>
                {o.assumptions?.map((a, i) => (
                  <p className="notice" key={i}>
                    {a}
                  </p>
                ))}
                {o.operands && (
                  <details>
                    <summary>How this depth was derived</summary>
                    <ul>
                      {o.operands.map((edge, i) => (
                        <li key={i}>
                          {edge.role.replaceAll("_", " ")}: {edge.length_ft} ft
                          · {edge.bearing}{" "}
                          <a
                            href={edge.source_url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Recorded map · page {edge.page} ↗
                          </a>
                          <small>
                            Document version: {edge.document_hash.slice(0, 12)}
                          </small>
                        </li>
                      ))}
                    </ul>
                    {o.citations?.map((c) => (
                      <p key={c.url}>
                        <a href={c.url} target="_blank" rel="noreferrer">
                          {c.section} ↗
                        </a>
                        <small>
                          Source version: {c.source_hash.slice(0, 12)}
                        </small>
                      </p>
                    ))}
                  </details>
                )}

                {o.region && (
                  <details>
                    <summary>Inspect printed measurement</summary>
                    <svg
                      role="img"
                      aria-label={`Source crop for ${o.key}`}
                      viewBox={`${Math.max(0, o.region[0] - 0.02)} ${Math.max(0, o.region[1] - 0.02)} ${o.region[2] - o.region[0] + 0.04} ${o.region[3] - o.region[1] + 0.04}`}
                      style={{ width: "100%", height: 180 }}
                    >
                      <image
                        href={`/api/documents/${o.document_hash}/pages/${o.page}`}
                        width="1"
                        height="1"
                        preserveAspectRatio="none"
                      />
                    </svg>
                    <a
                      href={`/api/documents/${o.document_hash}/pages/${o.page}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open full source page ↗
                    </a>
                  </details>
                )}
                <a href={o.source_url} target="_blank" rel="noreferrer">
                  Map source · page {o.page} ↗
                </a>
              </article>
            ))}
          </div>
          {context.automatic_evidence.uncertainties?.map((u, i) => (
            <p className="notice" key={i}>
              {u}
            </p>
          ))}
          {!context.automatic_evidence.observations.length && (
            <p>
              No readings passed validation. The source map remains available
              for inspection.
            </p>
          )}
        </>
      )}
    </div>
  );
}

type Saved = {
  id: string;
  parent?: string;
  data: {
    name: string;
    request?: {
      snapshot_id: string;
      project_type: string;
      inputs: Record<string, number>;
      checks: Record<string, boolean>;
      evidence_note: string;
      observation_ids: string[];
    };
    assessment?: {
      rule_set_version?: string;
      summary?: { design_implications?: DesignImplication[] };
      geometry?: {
        status?: string;
        reason?: string;
        metadata?: { status?: string };
        features?: { properties?: { kind?: string; area_sqft?: number } }[];
      };
      constraints: {
        category: string;
        value: number | null;
        status: string;
        units: string;
      }[];
    };
    context?: Context;
  };
};
type Answer = {
  answer: string;
  insufficient_evidence: boolean;
  citations: {
    id: string;
    quote: string;
    evidence: { url?: string; category?: string; section?: string };
  }[];
  suggested_changes?: string[];
};
export function ProjectWorkspace({
  context,
  projectType,
  inputs,
  checks,
  note,
  observationIds,
  onRestore,
}: {
  context: Context | null;
  projectType: string;
  inputs: Record<string, string>;
  checks: Record<string, boolean>;
  note: string;
  observationIds: string[];
  onRestore: (
    c: Context,
    p: string,
    i: Record<string, string>,
    k: Record<string, boolean>,
    n: string,
    ids: string[],
  ) => void;
}) {
  const [feedbackCategory, setFeedbackCategory] = useState("assessment");
  const restoring = useRef<string | null>(null);
  const questionAbort = useRef<AbortController | null>(null);
  const [projects, setProjects] = useState<Saved[]>([]),
    [projectId, setProjectId] = useState(""),
    [scenarios, setScenarios] = useState<Saved[]>([]),
    [scenarioId, setScenarioId] = useState("");
  const [name, setName] = useState("Design option"),
    [error, setError] = useState(""),
    [working, setWorking] = useState(false),
    [question, setQuestion] = useState(""),
    [answer, setAnswer] = useState<Answer | null>(null),
    [comment, setComment] = useState(""),
    [notice, setNotice] = useState("");
  const selected = scenarios.find((s) => s.id === scenarioId);
  const savedRequest = selected?.data.request;
  const numericInputs = Object.fromEntries(
    Object.entries(inputs)
      .filter(([, v]) => v !== "")
      .map(([k, v]) => [k, Number(v)]),
  );
  function sameEntries(a: Record<string, unknown>, b: Record<string, unknown>) {
    const entries = (v: Record<string, unknown>) =>
      JSON.stringify(Object.entries(v).sort(([a], [b]) => a.localeCompare(b)));
    return entries(a) === entries(b);
  }
  const dirty =
    !!savedRequest &&
    (savedRequest.snapshot_id !== context?.snapshot_id ||
      !sameEntries(
        Object.fromEntries(
          Object.entries(selected?.data.context?.research || {}).map(
            ([k, v]) => [k, v.id],
          ),
        ),
        Object.fromEntries(
          Object.entries(context?.research || {}).map(([k, v]) => [k, v.id]),
        ),
      ) ||
      savedRequest.project_type !== projectType ||
      !sameEntries(savedRequest.inputs, numericInputs) ||
      !sameEntries(savedRequest.checks, checks) ||
      (savedRequest.evidence_note || "") !== note ||
      JSON.stringify([...(savedRequest.observation_ids || [])].sort()) !==
        JSON.stringify([...observationIds].sort()));
  useEffect(() => {
    if (dirty) {
      questionAbort.current?.abort();
      setAnswer(null);
    }
  }, [dirty]);
  const json = (body: unknown) => ({
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  useEffect(() => {
    api<Saved[]>("/api/projects")
      .then(setProjects)
      .catch((e) => setError(e.message));
  }, []);
  useEffect(() => {
    if (restoring.current && restoring.current === context?.parcel?.AIN) {
      restoring.current = null;
      return;
    }
    restoring.current = null;
    setProjectId("");
    setScenarios([]);
    setScenarioId("");
    setAnswer(null);
  }, [context?.parcel?.AIN]);
  useEffect(() => {
    setFeedbackCategory("assessment");
    questionAbort.current?.abort();
    setAnswer(null);
  }, [scenarioId]);
  async function open(id: string) {
    setWorking(true);
    setError("");
    try {
      const p = await api<Saved & { scenarios: Saved[]; context: Context }>(
        `/api/projects/${id}`,
      );
      restoring.current = p.context.parcel?.AIN || null;
      setProjectId(id);
      setScenarios(p.scenarios);
      setAnswer(null);
      if (p.scenarios.length) {
        restore(p.scenarios[0]);
        setNotice(`Opened latest saved design: ${p.scenarios[0].data.name}.`);
      } else {
        setScenarioId("");
        onRestore(p.context, "single-family", {}, {}, "", []);
        setNotice(
          "This project has no saved designs. Start a new unsaved design.",
        );
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setWorking(false);
    }
  }
  async function save() {
    if (!context) return;
    setWorking(true);
    setError("");
    setNotice("");
    try {
      let id = projectId;
      if (!id) {
        const p = await api<Saved>(
          "/api/projects",
          json({
            name: context.parcel?.SitusFullAddress || "Property project",
            snapshot_id: context.snapshot_id,
          }),
        );
        id = p.id;
        setProjectId(id);
        setProjects((ps) => [p, ...ps]);
      }
      const s = await api<Saved>(
        `/api/projects/${id}/scenarios`,
        json({
          name,
          research_ids: Object.fromEntries(
            Object.entries(context.research || {}).map(([k, v]) => [k, v.id]),
          ),
          snapshot_id: context.snapshot_id,
          project_type: projectType,
          inputs: Object.fromEntries(
            Object.entries(inputs)
              .filter(([, v]) => v !== "")
              .map(([k, v]) => [k, Number(v)]),
          ),
          checks,
          evidence_note: note,
          observation_ids: observationIds,
        }),
      );
      setScenarios((ss) => [s, ...ss]);
      setScenarioId(s.id);
      setNotice("Scenario saved with its evidence and rule versions.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setWorking(false);
    }
  }
  function restore(s: Saved) {
    const r = s.data.request;
    if (!r || !s.data.context) return;
    onRestore(
      {
        ...s.data.context,
        snapshot_id: r.snapshot_id,
        mode: context?.mode || "live",
      },
      r.project_type,
      Object.fromEntries(
        Object.entries(r.inputs).map(([k, v]) => [k, String(v)]),
      ),
      r.checks,
      r.evidence_note,
      r.observation_ids,
    );
    setScenarioId(s.id);
    setName(s.data.name);
    setNotice(`Restored saved design: ${s.data.name}.`);
    setAnswer(null);
  }
  return (
    <section className="project-workspace">
      <h2>Saved projects & scenarios</h2>
      <p>
        Save a snapshot of this assessment to compare designs, ask a cited
        follow-up, or report a problem.
      </p>
      <label>
        Open saved project
        <select
          value={projectId}
          disabled={working}
          onChange={(e) => {
            if (e.target.value) void open(e.target.value);
          }}
        >
          <option value="">Choose a project</option>
          {projects.map((p) => (
            <option value={p.id} key={p.id}>
              {p.data.name}
            </option>
          ))}
        </select>
      </label>
      <div className="revision-status" role="status">
        {selected ? (
          <>
            <strong>Saved assessment: {selected.data.name}</strong>
            <p>
              {dirty
                ? "Unsaved changes: save this revision before asking a question or submitting feedback, or restore the saved design."
                : "Current inputs match this saved design. Follow-up and feedback target this saved assessment."}
            </p>
            {dirty && (
              <button
                type="button"
                className="secondary"
                onClick={() => restore(selected)}
              >
                Restore saved design
              </button>
            )}
          </>
        ) : (
          <p>
            New unsaved design. Save a scenario to ask questions or submit
            feedback.
          </p>
        )}
      </div>
      <div className="search-row">
        <label>
          Scenario name
          <input
            value={name}
            maxLength={120}
            onChange={(e) => setName(e.target.value)}
          />
        </label>
        <button
          type="button"
          disabled={working || !context || !name.trim()}
          onClick={save}
        >
          {working ? "Working…" : "Save scenario"}
        </button>
      </div>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {notice && <p role="status">{notice}</p>}
      {scenarios.length > 0 && (
        <>
          <h3>Compare saved scenarios</h3>
          <div className="scenario-comparison">
            {scenarios.map((s) => (
              <article key={s.id}>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => restore(s)}
                >
                  {s.data.name}
                  {scenarioId === s.id ? " · selected" : ""}
                </button>
                <p>{s.data.request?.project_type?.replaceAll("-", " ")}</p>
                <dl>
                  {s.data.assessment?.constraints.map((c) => (
                    <div key={c.category}>
                      <dt>{c.category.replaceAll("-", " ")}</dt>
                      <dd>
                        {c.value === null ? c.status : `${c.value} ${c.units}`}
                        <DesignComparison
                          result={s.data.assessment?.summary?.design_implications?.find(
                            (d) => d.category === c.category,
                          )}
                          units={c.units}
                        />
                      </dd>
                    </div>
                  ))}
                </dl>
                {!s.data.assessment?.summary?.design_implications?.length && (
                  <p>
                    No design comparison recorded. Inspect inputs and evidence
                    before drawing conclusions.
                  </p>
                )}
                <details>
                  <summary>Compare inputs and evidence versions</summary>
                  <dl>
                    {Object.entries(s.data.request?.inputs || {}).map(
                      ([key, value]) => (
                        <div key={key}>
                          <dt>{key.replaceAll("_", " ")}</dt>
                          <dd>{value}</dd>
                        </div>
                      ),
                    )}
                  </dl>
                  <p>
                    Rules:{" "}
                    {s.data.assessment?.rule_set_version || "not recorded"}
                  </p>
                  <p>
                    Map:{" "}
                    {s.data.context?.document?.content_hash?.slice(0, 12) ||
                      "unavailable"}
                  </p>
                  <p>
                    Geometry:{" "}
                    {s.data.assessment?.geometry?.metadata?.status ||
                      s.data.assessment?.geometry?.status ||
                      "not recorded"}
                    ; envelope area{" "}
                    {s.data.assessment?.geometry?.features
                      ?.find((f) => f.properties?.kind === "setback-envelope")
                      ?.properties?.area_sqft?.toFixed(1) || "unresolved"}{" "}
                    sq ft.
                  </p>
                  <p>
                    Assumptions:{" "}
                    {Object.entries(s.data.request?.checks || {})
                      .map(([k, v]) => `${k}: ${v}`)
                      .join("; ") || "none supplied"}
                  </p>
                </details>
              </article>
            ))}
          </div>
          <p>
            Saved values are historical and retain their evidence versions.
            Selecting a scenario recalculates with current eligible rules;
            refresh parcel sources for new research. Follow-up and feedback
            target the selected saved scenario. Save again after changing your
            design to ask about the new revision.
          </p>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              if (!scenarioId || dirty) return;
              setWorking(true);
              setError("");
              try {
                questionAbort.current = new AbortController();
                setAnswer(
                  await api<Answer>(`/api/scenarios/${scenarioId}/questions`, {
                    ...json({ question }),
                    signal: questionAbort.current.signal,
                  }),
                );
              } catch (e) {
                setError((e as Error).message);
              } finally {
                questionAbort.current = null;
                setWorking(false);
              }
            }}
          >
            <label>
              Ask about this saved assessment
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                maxLength={2000}
                required
                placeholder="Why is this setback conditional?"
              />
            </label>
            <button disabled={working || !scenarioId || dirty}>
              Ask follow-up
            </button>
            {working && questionAbort.current && (
              <button
                type="button"
                onClick={() => questionAbort.current?.abort()}
              >
                Cancel follow-up
              </button>
            )}
          </form>
          {answer && !dirty && (
            <div className="answer">
              <p>
                {answer.insufficient_evidence ? "Evidence gap: " : ""}
                {answer.answer}
              </p>
              {answer.citations.map((c, i) => (
                <details key={i}>
                  <summary>
                    Evidence {i + 1} ·{" "}
                    {c.evidence.section || c.evidence.category || c.id}
                  </summary>
                  <blockquote>{c.quote}</blockquote>
                  {c.evidence.url && (
                    <a href={c.evidence.url} target="_blank" rel="noreferrer">
                      Open source ↗
                    </a>
                  )}
                </details>
              ))}
              {answer.suggested_changes?.map((s, i) => (
                <p key={i}>Suggested scenario change: {s}</p>
              ))}
            </div>
          )}
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              if (!scenarioId || dirty) return;
              setWorking(true);
              setError("");
              try {
                await api(
                  "/api/feedback",
                  json({
                    scenario_id: scenarioId,
                    category: feedbackCategory,
                    comment,
                  }),
                );
                setComment("");
                setNotice("Feedback saved for operator review.");
              } catch (e) {
                setError((e as Error).message);
              } finally {
                setWorking(false);
              }
            }}
          >
            <label>
              Feedback target
              <select
                value={feedbackCategory}
                onChange={(e) => setFeedbackCategory(e.target.value)}
              >
                <option value="assessment">Whole assessment</option>
                {scenarios
                  .find((s) => s.id === scenarioId)
                  ?.data.assessment?.constraints.map((c) => (
                    <option key={c.category} value={c.category}>
                      {c.category}
                    </option>
                  ))}
              </select>
            </label>
            <label>
              Report a problem with this result
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                required
                maxLength={4000}
              />
            </label>
            <button disabled={working || !scenarioId || dirty}>
              Submit feedback
            </button>
          </form>
        </>
      )}
    </section>
  );
}
