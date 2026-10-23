import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import type { Context } from "./main";

export type ResearchItem = {
  title: string;
  value: string;
  source_url?: string;
  group?: string;
  pin?: string;
  date?: string;
  address?: string;
  document_available?: boolean;
  case_url?: string;
  case_details?: Record<string, string>;
  document_status?: string;
  documents?: { title: string; url: string; date?: string }[];
  fields?: Record<string, unknown>;
  route_status?: string;
  walking_miles?: number;
  walking_minutes?: number;
  route_source?: string;
  route_error?: string;
  directions?: string[];
};
export type ResearchResult = {
  id: string;
  source: string;
  title: string;
  ain: string;
  status: string;
  summary: string;
  source_url: string;
  retrieved_at: string;
  origin: string;
  vintage: string;
  cached?: boolean;
  association?: string;
  next_action?: string;
  warnings: string[];
  error?: string;
  items: ResearchItem[];
  layers?: {
    title: string;
    status: string;
    error?: string;
    source_url: string;
  }[];
};
const sources = {
  planning: "Planning profile & cases",
  permits: "Permit history",
  engineering: "Engineering & easements",
  transit: "Transit & walking access",
};
const labels: Record<string, string> = {
  matched: "Records found",
  "no-match": "No matches in checked source",
  partial: "Partial results",
  unavailable: "Unavailable",
  "not-checked": "Not checked",
};
function Link({ url, children }: { url?: string; children: React.ReactNode }) {
  return url ? (
    <a href={url} target="_blank" rel="noreferrer">
      {children} ↗
    </a>
  ) : (
    <>{children}</>
  );
}
function RecordDetails({ item }: { item: ResearchItem }) {
  return (
    <li className="research-record">
      <strong>{item.title}</strong>
      <p>{item.value}</p>
      {item.pin && <small>City PIN {item.pin}</small>}
      {item.address && (
        <p>
          {item.address} · {item.date?.slice(0, 10) || "Date not supplied"}
        </p>
      )}
      {item.walking_miles !== undefined && (
        <p>
          <strong>{item.walking_miles.toFixed(2)} mi estimated walk</strong> ·{" "}
          {item.walking_minutes} minutes
        </p>
      )}
      {item.route_error && (
        <p>Walking estimate unavailable: {item.route_error}</p>
      )}
      <Link url={item.case_url || item.source_url}>
        {item.document_available
          ? "Open permit document"
          : "Open source record"}
      </Link>
      {item.case_details && Object.keys(item.case_details).length > 0 && (
        <dl className="research-fields">
          {Object.entries(item.case_details)
            .filter(([, v]) => v)
            .map(([k, v]) => (
              <div key={k}>
                <dt>{k}</dt>
                <dd>{v}</dd>
              </div>
            ))}
        </dl>
      )}
      {item.documents && (
        <>
          <p>
            {item.documents.length} linked documents. {item.document_status}
          </p>
          <ul>
            {item.documents.map((d, i) => (
              <li key={i}>
                <Link url={d.url}>{d.title}</Link>
                {d.date && ` · ${d.date.slice(0, 10)}`}
              </li>
            ))}
          </ul>
        </>
      )}
      {item.fields && (
        <details>
          <summary>Feature attributes and plan references</summary>
          <dl className="research-fields">
            {Object.entries(item.fields).map(([k, v]) => (
              <div key={k}>
                <dt>{k}</dt>
                <dd>{String(v)}</dd>
              </div>
            ))}
          </dl>
        </details>
      )}
      {item.directions && (
        <details>
          <summary>Estimated walking directions</summary>
          <ol>
            {item.directions.map((d, i) => (
              <li key={i}>{d}</li>
            ))}
          </ol>
          <Link url={item.route_source}>
            Route response · Valhalla / OpenStreetMap
          </Link>
        </details>
      )}
    </li>
  );
}
function Records({ result }: { result: ResearchResult }) {
  if (result.source !== "planning")
    return (
      <ul className="research-records">
        {result.items.map((item, i) => (
          <RecordDetails key={i} item={item} />
        ))}
      </ul>
    );
  const groups = [...new Set(result.items.map((i) => i.group || "Profile"))];
  return (
    <>
      {groups
        .sort(
          (a, b) => Number(b === "Case Numbers") - Number(a === "Case Numbers"),
        )
        .map((group) => (
          <details key={group} className="research-group">
            <summary>
              {group} · {result.items.filter((i) => i.group === group).length}{" "}
              entries
            </summary>
            <ul className="research-records">
              {result.items
                .filter((i) => i.group === group)
                .map((item, i) => (
                  <RecordDetails key={i} item={item} />
                ))}
            </ul>
          </details>
        ))}
    </>
  );
}
export function ParcelResearch({
  context,
  onResult,
}: {
  context: Context;
  onResult: (snapshot: string, result: ResearchResult) => void;
}) {
  const [pending, setPending] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const controllers = useRef<Record<string, AbortController>>({});
  const latest = useRef(context);
  latest.current = context;
  const callback = useRef(onResult);
  callback.current = onResult;
  async function load(source: string, fresh = false) {
    controllers.current[source]?.abort();
    const abort = new AbortController();
    controllers.current[source] = abort;
    const snapshot = latest.current.snapshot_id;
    setPending((p) => ({ ...p, [source]: true }));
    setErrors((p) => ({ ...p, [source]: "" }));
    try {
      const result = await api<ResearchResult>(`/api/research/${source}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ snapshot_id: snapshot, fresh }),
        signal: abort.signal,
      });
      if (!abort.signal.aborted) callback.current(snapshot, result);
    } catch (e) {
      if (!abort.signal.aborted)
        setErrors((p) => ({ ...p, [source]: (e as Error).message }));
    } finally {
      if (!abort.signal.aborted) setPending((p) => ({ ...p, [source]: false }));
    }
  }
  useEffect(() => {
    setPending({});
    setErrors({});
    for (const source of Object.keys(sources))
      if (!context.research?.[source]) void load(source);
    return () => {
      Object.values(controllers.current).forEach((c) => c.abort());
    };
  }, [context.snapshot_id]);
  const completed = Object.keys(context.research || {}).length;
  return (
    <section
      id="parcel-research"
      tabIndex={-1}
      className="parcel-research"
      aria-labelledby="research-heading"
    >
      <h2 id="research-heading">Property research</h2>
      <p>
        Planning, permits, engineering and transit in one place. {completed}/4
        sources returned. Save a scenario to retain these records with your
        design.
      </p>
      <div className="research-grid">
        {Object.entries(sources).map(([source, title]) => {
          const result = context.research?.[source];
          return (
            <details key={source} className="research-card" aria-label={title}>
              <summary>
                <strong>{title}</strong>
                <span>
                  {pending[source]
                    ? "Loading records…"
                    : errors[source]
                      ? "Lookup failed"
                      : labels[result?.status || ""] || "Waiting to load"}
                </span>
                <p>
                  {result?.summary ||
                    "Existing assessment results remain available while this source loads."}
                </p>
              </summary>
              {pending[source] && (
                <p role="status">
                  <span className="spinner" aria-hidden="true" /> Retrieving{" "}
                  {title.toLowerCase()}…
                </p>
              )}
              {errors[source] && <p role="alert">{errors[source]}</p>}
              {result && (
                <>
                  <p>
                    <strong>Next:</strong>{" "}
                    {result.next_action ||
                      "Open the source to continue research."}
                  </p>
                  <p className="muted">{result.association}</p>
                  <p className="muted">
                    {result.origin === "fixture"
                      ? "Recorded mode"
                      : result.cached
                        ? "Cached source response"
                        : "Live source response"}{" "}
                    · Retrieved {new Date(result.retrieved_at).toLocaleString()}{" "}
                    · Vintage: {result.vintage}
                  </p>
                  {result.error && <p role="alert">{result.error}</p>}
                  <ul>
                    {result.warnings.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                  {result.layers && (
                    <ul>
                      {result.layers.map((l) => (
                        <li key={l.title}>
                          <Link url={l.source_url}>{l.title}</Link>:{" "}
                          {labels[l.status] || l.status}
                          {l.error && ` — ${l.error}`}
                        </li>
                      ))}
                    </ul>
                  )}
                  <Records result={result} />
                  <p>
                    <Link url={result.source_url}>
                      Open {title.toLowerCase()} source
                    </Link>
                  </p>
                </>
              )}
              <button
                type="button"
                className="secondary"
                disabled={pending[source]}
                onClick={() => void load(source, true)}
              >
                {result?.status === "unavailable" ||
                result?.status === "partial" ||
                errors[source]
                  ? "Retry"
                  : "Refresh"}{" "}
                {title.toLowerCase()}
              </button>
            </details>
          );
        })}
      </div>
    </section>
  );
}
