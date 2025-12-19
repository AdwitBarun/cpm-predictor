import axios from "axios"

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5173"

export async function predictCPM(payload: any) {
  const res = await axios.post(
    `${API_BASE_URL}/api/predict`,
    payload
  )
  return res.data
}
