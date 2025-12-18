import axios from "axios"

export const api = axios.create({
  baseURL: "https://cpm-predictor-production.up.railway.app/"
})

export async function predictCPM(payload: any) {
  const res = await api.post("/predict", payload)
  return res.data
}
