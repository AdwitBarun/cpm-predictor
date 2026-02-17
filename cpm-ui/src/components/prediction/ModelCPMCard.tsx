// import { ModelRange, ConformalRange } from "../../types/api";

// export default function ModelCPMCard({
//   model,
//   conformal,
// }: {
//   model: ModelRange;
//   conformal: ConformalRange;
// }) {
//   return (
//     <div className="card">
//       <h3>ML Model Prediction</h3>

//       <div className="grid">
//         <div>P10: ₹{model.p10}</div>
//         <div>P50 (Median): ₹{model.p50}</div>
//         <div>P90: ₹{model.p90}</div>
//       </div>

//       <hr />

//       <div className="muted">
//         Conformal Range ({Math.round(conformal.coverage_target * 100)}% confidence)
//       </div>
//       <div>
//         ₹{conformal.low} – ₹{conformal.high}
//       </div>
//     </div>
//   // );
// }
import { ConformalRange } from "../../types/api";

export default function ModelCPMCard({
  conformal,
}: {
  conformal: ConformalRange;
}) {
  return (
    <div className="card">
      <h3>Historical Suggested CPM</h3>

      <div className="muted">
        ({Math.round(conformal.coverage_target * 100)}% Conformal Max)
      </div>

      <div className="price" style={{ fontWeight: 700 }}>
        ₹{conformal.high}
      </div>
    </div>
  );
}
