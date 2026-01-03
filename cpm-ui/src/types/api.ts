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

export interface SimilarCampaign {
  campaign_name: string;
  markets: string;
  tg_summary: string;
  device_summary: string;
  delivered_cpm: number | null;
  similarity_score: number;
}

export interface PredictionResponse {
  model_range: ModelRange;
  conformal_range: ConformalRange;
  shap_top_features: [string, number][];
  similar_campaigns: SimilarCampaign[];
  final_blended_cpm: number;
  llm_adjusted_range: {
    adjustment_factor: number;
    tool_impacts: {
      explanation: string;
    }[];
  };
}
