const NICAI_API = import.meta.env.VITE_NICAI_API || "";

async function request(path, options = {}) {
  if (!NICAI_API) {
    throw new Error("VITE_NICAI_API is not configured");
  }

  const response = await fetch(`${NICAI_API}${path}`, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export async function getHealth() {
  return request("/health");
}

export async function getSignals() {
  const data = await request("/signals");
  return data.signals || [];
}

export async function getPatterns() {
  const data = await request("/patterns");
  return data.pattern || null;
}

export async function getSignalsWithSummary() {
  return request("/signals");
}

export async function triggerAction(data) {
  return request("/action", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export { NICAI_API };
