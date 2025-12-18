import axios from "axios"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

/**
 * Call backend CPM prediction API
 */
export async function predictCPM(payload: Record<string, any>) {
  const response = await api.post("/api/predict", payload)
  return response.data
}

export default api
