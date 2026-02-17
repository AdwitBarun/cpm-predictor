// import { useState } from "react";

// import { predictCPM } from "../services/api";
// import { PredictResponse } from "../types/api";

// import UploadPlanCard from "../components/upload/UploadPlanCard";
// import CampaignSummary from "../components/campaign/CampaignSummary";

// import ModelCPMCard from "../components/prediction/ModelCPMCard";
// import LLMCPMCard from "../components/prediction/LLMCPMCard";
// import FinalCPMCard from "../components/prediction/FinalCPMCard";

// import ExplanationAccordion from "../components/explanation/ExplanationAccordion";
// import SimilarCampaignTable from "../components/similarity/SimilarCampaignTable";
// import AdminPanel from "../components/admin/AdminPanel";

// import Loader from "../components/common/Loader";

// export default function App() {
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState<string | null>(null);

//   const [csvData, setCsvData] = useState<Record<string, any> | null>(null);
//   const [result, setResult] = useState<PredictResponse | null>(null);

//   // -----------------------------
//   // Handle CSV Upload → Predict
//   // -----------------------------
//   const handleCsvSubmit = async (parsedCsv: Record<string, any>) => {
//     setLoading(true);
//     setError(null);
//     setResult(null);

//     try {
//       setCsvData(parsedCsv);

//       const response = await predictCPM(parsedCsv);
//       setResult(response);
//     } catch (e: any) {
//       console.error(e);
//       setError(
//         e?.message ??
//           "Prediction failed. Please check CSV format and backend logs."
//       );
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="app-container">
//       {/* ============================
//           Header
//       ============================ */}
//       <header className="app-header">
//         <h1>CPM Prediction Tool</h1>
//         <p className="muted">
//           ML + LLM assisted CPM estimation for programmatic video campaigns
//         </p>
//       </header>

//       {/* ============================
//           Upload Section
//       ============================ */}
//       <UploadPlanCard onSubmit={handleCsvSubmit} />

//       {/* ============================
//           CSV Preview
//       ============================ */}
//       {csvData && (
//         <CampaignSummary campaign={csvData} />
//       )}

//       {/* ============================
//           Loading / Error
//       ============================ */}
//       {loading && <Loader text="Running prediction…" />}

//       {error && (
//         <div className="card error">
//           <strong>Error</strong>
//           <p>{error}</p>
//         </div>
//       )}

//       {/* ============================
//           Prediction Results
//       ============================ */}
//       {result && !loading && (
//         <>
//           {/* ---- CPM Cards ---- */}
//           <div className="grid-3">
//             <ModelCPMCard
//               model={result.model_range}
//               conformal={result.conformal_range}
//             />

//             <LLMCPMCard llm={result.llm_adjusted_range} />

//             <FinalCPMCard value={result.final_blended_cpm} />
//           </div>

//           {/* ---- Explanation ---- */}
//           <ExplanationAccordion llm={result.llm_adjusted_range} />

//           {/* ---- Similar Campaigns ---- */}
//           <SimilarCampaignTable
//             campaigns={result.similar_campaigns}
//           />

//           {/* ---- Admin Controls ---- */}
//           <AdminPanel />
//         </>
//       )}

//       {/* ============================
//           Footer
//       ============================ */}
//       <footer className="app-footer">
//         <span className="muted">
//           Predictions include uncertainty. Use as a planning guide, not a guarantee.
//         </span>
//       </footer>
//     </div>
//   );
// }
import { useState } from "react";

import { predictCPM } from "../services/api";
import { PredictResponse } from "../types/api";

import UploadPlanCard from "../components/upload/UploadPlanCard";
import CampaignSummary from "../components/campaign/CampaignSummary";

import ModelCPMCard from "../components/prediction/ModelCPMCard";
import LLMCPMCard from "../components/prediction/LLMCPMCard";
import FinalCPMCard from "../components/prediction/FinalCPMCard";

import ExplanationAccordion from "../components/explanation/ExplanationAccordion";
import SimilarCampaignTable from "../components/similarity/SimilarCampaignTable";
import AdminPanel from "../components/admin/AdminPanel";

import Loader from "../components/common/Loader";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [csvData, setCsvData] = useState<Record<string, any> | null>(null);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [plannedCPM, setPlannedCPM] = useState<number | null>(null);

  // -----------------------------
  // Handle CSV Upload → Predict
  // -----------------------------
  const handleCsvSubmit = async (parsedCsv: Record<string, any>) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setPlannedCPM(null);

    try {
      setCsvData(parsedCsv);

      const response = await predictCPM(parsedCsv);
      setResult(response);
    } catch (e: any) {
      console.error(e);
      setError(
        e?.message ??
          "Prediction failed. Please check CSV format and backend logs."
      );
    } finally {
      setLoading(false);
    }
  };

  const isAccept =
    plannedCPM !== null &&
    result &&
    plannedCPM >= result.final_blended_cpm;

  return (
    <div className="app-container">
      {/* ============================
          Header
      ============================ */}
      <header className="app-header">
        <h1>BidVid Benchmarking Tool</h1>
        <p className="muted">
          ML + LLM assisted CPM estimation for programmatic video campaigns
        </p>
      </header>

      {/* ============================
          Upload Section
      ============================ */}
      <UploadPlanCard onSubmit={handleCsvSubmit} />

      {/* ============================
          Campaign Summary
      ============================ */}
      {csvData && <CampaignSummary campaign={csvData} />}

      {/* ============================
          Planned CPM Input
      ============================ */}
      {csvData && (
        <div className="card mt-4">
          <h3>Enter Planned CPM</h3>
          <input
            type="number"
            placeholder="Type planned CPM..."
            className="mt-2 p-2 border rounded w-full"
            value={plannedCPM ?? ""}
            onChange={(e) =>
              setPlannedCPM(
                e.target.value ? Number(e.target.value) : null
              )
            }
          />
        </div>
      )}

      {/* ============================
          Loading / Error
      ============================ */}
      {loading && <Loader text="Running prediction…" />}

      {error && (
        <div className="card error">
          <strong>Error</strong>
          <p>{error}</p>
        </div>
      )}

      {/* ============================
          Decision + Results
      ============================ */}
      {result && !loading && plannedCPM !== null && (
        <>
          {/* ----------------------------------
              ACCEPT / REJECT DECISION
          ---------------------------------- */}
          <div
            className="card highlight text-center"
            style={{
              backgroundColor: isAccept ? "#e6f7ed" : "#fdecea",
              border:
                isAccept
                  ? "1px solid #2e7d32"
                  : "1px solid #c62828",
            }}
          >
            <h2>Campaign Decision</h2>

            {isAccept ? (
              <div
                style={{
                  color: "#2e7d32",
                  fontWeight: 700,
                  fontSize: "20px",
                }}
              >
                ✅ ACCEPT CAMPAIGN
              </div>
            ) : (
              <div
                style={{
                  color: "#c62828",
                  fontWeight: 700,
                  fontSize: "20px",
                }}
              >
                ❌ REJECT CAMPAIGN
              </div>
            )}

            <p className="muted mt-2">
              Planned CPM: ₹{plannedCPM} | Recommended: ₹
              {result.final_blended_cpm}
            </p>
          </div>

          {/* ----------------------------------
              FINAL CPM (Hero)
          ---------------------------------- */}
          <FinalCPMCard value={result.final_blended_cpm} />

          {/* ----------------------------------
              Supporting Ranges
          ---------------------------------- */}
          <div className="grid-2">
            <ModelCPMCard
              conformal={result.conformal_range}
            />
            <LLMCPMCard
              llm={result.llm_adjusted_range}
            />
          </div>

          {/* ----------------------------------
              Why This CPM
          ---------------------------------- */}
          <ExplanationAccordion
            llm={result.llm_adjusted_range}
          />

          {/* ----------------------------------
              Similar Campaigns
          ---------------------------------- */}
          <SimilarCampaignTable
            campaigns={result.similar_campaigns}
          />

          {/* ----------------------------------
              Admin Controls
          ---------------------------------- */}
          <AdminPanel />
        </>
      )}

      {/* ============================
          Footer
      ============================ */}
      <footer className="app-footer">
        <span className="muted">
          Predictions include uncertainty. Use as a planning guide, not a guarantee.
        </span>
      </foote
