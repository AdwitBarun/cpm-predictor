import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function predictCPM(payload: Record<string, any>) {
  const res = await axios.post(`${API_BASE}/predict`, payload);
  return res.data;
}
