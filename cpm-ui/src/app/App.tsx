import UploadPlanCard from "../components/upload/UploadPlanCard";
import { predictCPM } from "../services/api";
import { usePredictionStore } from "../state/predictionStore";

import ModelCPMCard from "../components/prediction/ModelCPMCard";
import LLMCPMCard from "../components/prediction/LLMCPMCard";
import FinalCPMCard from "../components/prediction/FinalCPMCard";
import ConfidenceMeter from "../components/prediction/ConfidenceMeter";
import ExplanationAccordion from "../components/explanation/ExplanationAccordion";
import SimilarCampaignTable from "../components/similarity/SimilarCampaignTable";
import AdminPanel from "../components/admin/AdminPanel";

export default function App() {
  const { result, setResult, setLoading } = usePredictionStore();

  const run = async (row: any) => {
    setLoading(true);
    const res = await predictCPM(row);
    setResult(res);
    setLoading(false);
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      <h1 className="text-2xl font-bold">CPM Prediction Tool</h1>

      <UploadPlanCard onParsed={run} />

      {result && (
        <>
          <div className="grid grid-cols-3 gap-6">
            <ModelCPMCard value={result.model_range.p50} />
            <LLMCPMCard value={result.llm_adjusted_range.llm_predicted_cpm.mid} />
            <FinalCPMCard value={result.final_blended_cpm} />
          </div>

          <ConfidenceMeter value={result.conformal_range.coverage_target} />

          <ExplanationAccordion
            impacts={result.llm_adjusted_range.tool_impacts}
          />

          <SimilarCampaignTable rows={result.similar_campaigns} />
        </>
      )}

      <AdminPanel />
    </div>
  );
}
