const API_BASE = import.meta.env.VITE_API_BASE;

export async function predictCPM(payload: any) {
  const res = await fetch(`${API_BASE}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Prediction failed");
  }

  return res.json();
}

export async function refreshHistorical() {
  const res = await fetch(
    `${API_BASE}/api/admin/refresh-historical-from-gsheet`,
    { method: "POST" }
  );

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Refresh failed");
  }

  return res.json();
}
