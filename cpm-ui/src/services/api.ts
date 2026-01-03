import { PredictResponse } from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE;

export async function predictCPM(payload: any): Promise<PredictResponse> {
  const res = await fetch(`${API_BASE}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text);
  }

  return res.json(); // ⛔ DO NOT modify response
}
export async function refreshHistorical(): Promise<{ status: string }> {
  const res = await fetch(
    `${API_BASE}/api/admin/refresh-historical-from-gsheet`,
    {
      method: "POST",
    }
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Failed to refresh historical data");
  }

  return res.json();
}
