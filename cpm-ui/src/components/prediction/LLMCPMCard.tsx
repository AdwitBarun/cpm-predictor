// import { LLMRange } from "../../types/api";

// export default function LLMCPMCard({ llm }: { llm: LLMRange }) {
//   return (
//     <div className="card">
//       <h3>LLM Adjusted Range</h3>

//       <div className="grid">
//         <div>Low: ₹{llm.llm_predicted_cpm.low}</div>
//         <div>Mid: ₹{llm.llm_predicted_cpm.mid}</div>
//         <div>High: ₹{llm.llm_predicted_cpm.high}</div>
//       </div>

//       <div className="badge">
//         Adjustment ×{llm.adjustment_factor}
//       </div>

//       <p className="muted">{llm.explanation}</p>
//     </div>
//   );
// }
import { LLMRange } from "../../types/api";

export default function LLMCPMCard({ llm }: { llm: LLMRange }) {
  return (
    <div className="card">
      <h3>External Factor Peak CPM</h3>

      <div className="price" style={{ fontWeight: 700 }}>
        ₹{llm.llm_predicted_cpm.high}
      </div>
    </div>
  );
}
