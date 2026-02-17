// import Card from "../common/Card";
// import { SimilarCampaign } from "../../types/api";

// export default function SimilarCampaignTable({
//   campaigns,
// }: {
//   campaigns: SimilarCampaign[];
// }) {
//   if (!campaigns || campaigns.length === 0) return null;

//   return (
//     <Card title="Similar Historical Campaigns">
//       <div className="overflow-x-auto">
//         <table className="w-full text-sm border">
//           <thead className="bg-gray-100">
//             <tr>
//               <th className="p-2 text-left">Name</th>
//               <th className="p-2 text-left">Similarity</th>
//               <th className="p-2 text-left">TG</th>
//               <th className="p-2 text-left">Markets</th>
//               <th className="p-2 text-left">Device</th>
//               <th className="p-2 text-left">Delivered CPM</th>
//             </tr>
//           </thead>

//           <tbody>
//             {campaigns.map((c, idx) => (
//               <tr key={`${c.campaign_name}-${idx}`} className="border-t">
//                 <td className="p-2 font-medium">
//                   {c.campaign_name || "—"}
//                 </td>

//                 <td className="p-2">
//                   {typeof c.similarity_score === "number"
//                     ? `${(c.similarity_score * 100).toFixed(1)}%`
//                     : "—"}
//                 </td>

//                 <td className="p-2">
//                   {c.tg_summary || "—"}
//                 </td>

//                 <td className="p-2">
//                   {c.markets || "—"}
//                 </td>

//                 <td className="p-2">
//                   {c.device_summary || "—"}
//                 </td>

//                 <td className="p-2">
//                   {c.delivered_cpm !== null
//                     ? `₹${c.delivered_cpm}`
//                     : "—"}
//                 </td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </div>
//     </Card>
//   );
// }
import { useState } from "react";
import { SimilarCampaign } from "../../types/api";
import Card from "../common/Card";

export default function SimilarCampaignTable({
  campaigns,
}: {
  campaigns: SimilarCampaign[];
}) {
  const [open, setOpen] = useState(false);

  if (!campaigns || campaigns.length === 0) return null;

  return (
    <Card>
      <button
        onClick={() => setOpen(!open)}
        style={{
          fontWeight: 600,
          cursor: "pointer",
          marginBottom: open ? "16px" : "0",
        }}
      >
        {open
          ? "Hide Similar Historical Campaigns ▲"
          : "Show Similar Historical Campaigns ▼"}
      </button>

      {open && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 text-left">Name</th>
                <th className="p-2 text-left">Similarity</th>
                <th className="p-2 text-left">TG</th>
                <th className="p-2 text-left">Markets</th>
                <th className="p-2 text-left">Device</th>
                <th className="p-2 text-left">Delivered CPM</th>
              </tr>
            </thead>

            <tbody>
              {campaigns.map((c, idx) => (
                <tr key={`${c.campaign_name}-${idx}`} className="border-t">
                  <td className="p-2 font-medium">
                    {c.campaign_name || "—"}
                  </td>

                  <td className="p-2">
                    {typeof c.similarity_score === "number"
                      ? `${(c.similarity_score * 100).toFixed(1)}%`
                      : "—"}
                  </td>

                  <td className="p-2">
                    {c.tg_summary || "—"}
                  </td>

                  <td className="p-2">
                    {c.markets || "—"}
                  </td>

                  <td className="p-2">
                    {c.device_summary || "—"}
                  </td>

                  <td className="p-2 font-semibold">
                    {c.delivered_cpm !== null
                      ? `₹${c.delivered_cpm}`
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
