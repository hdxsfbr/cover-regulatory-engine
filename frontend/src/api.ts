export async function api<T>(url: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(url, {
    ...options,
    signal: options.signal ?? AbortSignal.timeout(29000),
  });
  const raw = await response.text();
  let body;
  try {
    body = JSON.parse(raw);
  } catch {
    throw new Error(
      response.ok
        ? "The server returned an unreadable response. Please retry."
        : `The API is unavailable (HTTP ${response.status}). Please retry; if this continues, restart the backend.`,
    );
  }
  if (!response.ok)
    throw new Error(
      typeof body?.detail === "string"
        ? body.detail
        : "Please check your inputs and try again.",
    );
  return body;
}

