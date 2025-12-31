import axios from "axios";

const API = "https://cpm-predictor-production.up.railway.app";

export const predictCPM = async (payload: any) => {
  const res = await axios.post(`${API}/predict`, payload);
  return res.data;
};
