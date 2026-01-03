export interface ModelRange {
  p10: number;
  p50: number;
  p90: number;
}

export interface ConformalRange {
  low: number;
  high: number;
  coverage_target: number;
}

export interface LLMRange {
  llm_predicted_cpm: {
    low: number;
    mid: number;
    high: number;
  };
  base_model_range: {
    low: number;
    mid: number;
    high: number;
    confidence: number;
  };
  adjustment_factor: number;
  tool_impacts: {
    adjustment_factor: number;
    explanation: string;
  }[];
  explanation: string;
  confidence_note: string;
}

export interface SimilarCampaign {
  campaign_name: string;
  similarity_score: number;
  delivered_cpm: number | null;
  markets: string;
  device_summary: string;
  tg_summary: string;
  start_month: number | null;
  campaign_intensity: number;
}

export interface PredictResponse {
  model_range: ModelRange;
  conformal_range: ConformalRange;
  shap_top_features: [string, number][];
  similar_campaigns: SimilarCampaign[];
  llm_adjusted_range: LLMRange;
  final_blended_cpm: number;
}
