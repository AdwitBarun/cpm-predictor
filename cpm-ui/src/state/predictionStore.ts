import { create } from "zustand";
import { PredictionResponse } from "../types/api";

interface PredictionState {
  loading: boolean;
  result: PredictionResponse | null;
  error: string | null;

  setLoading: (v: boolean) => void;
  setResult: (r: PredictionResponse) => void;
  setError: (e: string | null) => void;
}

export const usePredictionStore = create<PredictionState>((set) => ({
  loading: false,
  result: null,
  error: null,

  setLoading: (loading) => set({ loading }),
  setResult: (result) => set({ result, error: null }),
  setError: (error) => set({ error }),
}));
