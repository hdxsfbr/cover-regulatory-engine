import { useState, useEffect } from "react";
import { api } from "./api";
type Source = {
  section: string;
  content_hash: string;
  text: string;
  url: string;
  retrieved_at: string;
};
type Review = {
  id: string;
  data: {
    reviewer: string;
    decision: string;
    note: string;
    candidate: unknown;
  };
};
type Job = {
  id: string;
  status: string;
  stage: string;
  error?: string;
  result?: { output?: unknown; validation_errors?: unknown; changed?: boolean };
};
export function Operator() {
  const [history, setHistory] = useState<Job[]>([]);
  const [notice, setNotice] = useState("");
  const [current, setCurrent] = useState<unknown>(null);
  const [token, setToken] = useState(""),
    [sources, setSources] = useState<Source[]>([]),
    [hashes, setHashes] = useState<string[]>([]),
    [scope, setScope] = useState(
      "Chapter 1 R1-1 single-family ordinary-case front, side, rear, height and residential floor area constraints",
    ),
    [reviewer, setReviewer] = useState(""),
    [note, setNote] = useState(""),
    [candidate, setCandidate] = useState(""),
    [job, setJob] = useState<Job | null>(null),
    [reviews, setReviews] = useState<Review[]>([]),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [feedback, setFeedback] = useState<
      {
        id: string;
        data: { comment: string; category: string; status: string };
      }[]
    >([]);
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  async function load() {
    setBusy(true);
    setError("");
    try {
      setHistory(await api<Job[]>("/api/operator/jobs", { headers }));
      setCurrent(await api("/api/operator/packages", { headers }));
      setSources(await api<Source[]>("/api/operator/sources", { headers }));
      setReviews(await api<Review[]>("/api/operator/reviews", { headers }));
      setFeedback(await api("/api/operator/feedback", { headers }));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function poll() {
    if (!job) return;
    try {
      const j = await api<Job>(`/api/evidence-jobs/${job.id}`, { headers });
      setJob(j);
      if (j.result?.output)
        setCandidate(JSON.stringify(j.result.output, null, 2));
    } catch (e) {
      setError((e as Error).message);
    }
  }
  useEffect(() => {
    if (!job || !["queued", "running"].includes(job.status)) return;
    const timer = setTimeout(() => void poll(), 1200);
    return () => clearTimeout(timer);
  }, [job]);
  async function resume(id: string) {
    try {
      const j = await api<Job>(`/api/evidence-jobs/${id}`, { headers });
      setJob(j);
      setCandidate(
        j.result?.output ? JSON.stringify(j.result.output, null, 2) : "",
      );
    } catch (e) {
      setError((e as Error).message);
    }
  }
  async function post<T>(url: string, body: unknown) {
    return api<T>(url, { method: "POST", headers, body: JSON.stringify(body) });
  }
  return (
    <section className="project-workspace">
      <h1>Regulatory source review</h1>
      <p>
        Local operator access. Review source-derived candidates before
        activating them. Project feedback never changes rules automatically.
      </p>
      <label>
        Operator token
        <input
          type="password"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          autoComplete="off"
        />
      </label>
      <button disabled={busy || !token} onClick={load}>
        Unlock review workspace
      </button>
      {error && <p role="alert">{error}</p>}
      {notice && <p role="status">{notice}</p>}
      {sources.length > 0 && (
        <>
          <label>
            Resume operator job
            <select
              value={job?.id || ""}
              onChange={(e) => void resume(e.target.value)}
            >
              <option value="">Choose a source or extraction job</option>
              {history.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.id} · {j.stage}
                </option>
              ))}
            </select>
          </label>
          <h2>Sources and passages</h2>
          {sources.map((s) => (
            <details key={s.content_hash}>
              <summary>
                {s.section} · {s.content_hash.slice(0, 12)}
              </summary>
              <label>
                <input
                  type="checkbox"
                  checked={hashes.includes(s.content_hash)}
                  onChange={(e) =>
                    setHashes((h) =>
                      e.target.checked
                        ? [...h, s.content_hash]
                        : h.filter((x) => x !== s.content_hash),
                    )
                  }
                />{" "}
                Include in extraction
              </label>
              <p>
                Retrieved {s.retrieved_at} ·{" "}
                <a href={s.url} target="_blank" rel="noreferrer">
                  Publisher ↗
                </a>
              </p>
              <pre className="source-text">{s.text}</pre>
              {["12.03", "12.08", "12.21.1", "12.22"].includes(s.section) && (
                <button
                  onClick={async () => {
                    try {
                      setJob(
                        await post<Job>("/api/operator/refresh", {
                          section: s.section,
                        }),
                      );
                    } catch (e) {
                      setError((e as Error).message);
                    }
                  }}
                >
                  Fetch current source
                </button>
              )}
            </details>
          ))}
          <label>
            Extraction scope
            <textarea
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              maxLength={2000}
            />
          </label>
          <button
            disabled={!hashes.length || !scope}
            onClick={async () => {
              try {
                setJob(
                  await post<Job>("/api/operator/extract", { hashes, scope }),
                );
                setCandidate("");
              } catch (e) {
                setError((e as Error).message);
              }
            }}
          >
            Extract rule candidates
          </button>
          {job && (
            <div role="status">
              <p>
                {job.stage} · {job.status}
              </p>
              {job.error && <p>{job.error}</p>}
              <button onClick={poll}>Check job progress</button>
              <pre>
                {JSON.stringify(job.result?.validation_errors, null, 2)}
              </pre>
            </div>
          )}
          <h2>Candidate correction and review</h2>
          <details>
            <summary>Current packages and activated versions</summary>
            <pre className="source-text">
              {JSON.stringify(current, null, 2)}
            </pre>
          </details>
          <p>
            Compare each candidate with the passages above. Activation requires
            canonical jurisdiction, regime, zone, project type, a complete
            package and mapped applicability predicates. Unresolved references
            or superseded sources prevent activation.
          </p>
          <label>
            Candidate JSON
            <textarea
              className="candidate-json"
              value={candidate}
              onChange={(e) => setCandidate(e.target.value)}
              spellCheck={false}
            />
          </label>
          <label>
            Reviewer
            <input
              value={reviewer}
              onChange={(e) => setReviewer(e.target.value)}
              maxLength={120}
            />
          </label>
          <label>
            Review rationale
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              maxLength={4000}
            />
          </label>
          {["review", "reject"].map((decision) => (
            <button
              key={decision}
              disabled={!candidate || !reviewer || !note || !job}
              onClick={async () => {
                try {
                  await post("/api/operator/reviews", {
                    job_id: job?.id,
                    candidate: JSON.parse(candidate),
                    reviewer,
                    note,
                    decision,
                  });
                  await load();
                } catch (e) {
                  setError((e as Error).message);
                }
              }}
            >
              {decision === "review"
                ? "Record reviewed correction"
                : "Reject candidate"}
            </button>
          ))}
          <h2>Review history and activation</h2>
          {reviews.map((r) => (
            <details key={r.id}>
              <summary>
                {r.data.decision} · {r.data.reviewer} · {r.id.slice(0, 8)}
              </summary>
              <p>{r.data.note}</p>
              <pre className="source-text">
                {JSON.stringify(r.data.candidate, null, 2)}
              </pre>
              <button
                disabled={r.data.decision !== "review" || !reviewer || !note}
                onClick={async () => {
                  try {
                    await post(`/api/operator/reviews/${r.id}/activate`, {
                      reviewer,
                      note,
                    });
                    setError("");
                    setNotice(
                      "Reviewed package activated. New assessments use this version.",
                    );
                    await load();
                  } catch (e) {
                    setError((e as Error).message);
                  }
                }}
              >
                Activate this reviewed version
              </button>
            </details>
          ))}
          <h2>Result feedback</h2>
          {feedback.map((f) => (
            <article key={f.id}>
              <h3>{f.data.category}</h3>
              <p>{f.data.comment}</p>
              <p>Status: {f.data.status}</p>
              {["reviewing", "resolved", "rejected"].map((status) => (
                <button
                  disabled={!reviewer || !note}
                  key={status}
                  onClick={async () => {
                    try {
                      await post(`/api/operator/feedback/${f.id}`, {
                        reviewer,
                        note,
                        status,
                      });
                      await load();
                    } catch (e) {
                      setError((e as Error).message);
                    }
                  }}
                >
                  {status}
                </button>
              ))}
            </article>
          ))}
        </>
      )}
    </section>
  );
}
