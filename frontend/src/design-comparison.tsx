export type DesignImplication = {
  category: string;
  message: string;
  status: string;
  proposed?: number;
  limit?: number;
  assumptions?: string[];
};

export function DesignComparison({
  result,
  units,
}: {
  result?: DesignImplication;
  units: string;
}) {
  if (!result) return null;
  return (
    <div className={`design-comparison ${result.status}`}>
      <strong>{result.status.replaceAll("-", " ")}</strong>
      {result.proposed !== undefined && result.limit !== undefined ? (
        <p>
          Proposed {result.proposed.toLocaleString()} {units} · Limit{" "}
          {result.limit.toLocaleString()} {units}
          {result.status === "exceeds-limit" && (
            <>
              {" "}
              · Exceeds by{" "}
              {Number(
                (result.proposed - result.limit).toFixed(2),
              ).toLocaleString()}{" "}
              {units}
            </>
          )}
        </p>
      ) : (
        <p>{result.message}</p>
      )}
      {result.status === "conditional" && (
        <p>
          Depends on unresolved assumptions; review the evidence before using
          this limit.
        </p>
      )}
    </div>
  );
}
