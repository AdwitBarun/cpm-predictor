import Card from "../common/Card";
import { formatINR } from "../../utils/format";

export default function SimilarCampaignTable({ rows }: { rows: any[] }) {
  return (
    <Card title="Similar Historical Campaigns">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-gray-500 border-b">
            <th>Name</th>
            <th>Markets</th>
            <th>TG</th>
            <th>Device</th>
            <th>CPM</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-b">
              <td>{r.campaign_name}</td>
              <td>{r.markets}</td>
              <td>{r.tg_summary}</td>
              <td>{r.device_summary}</td>
              <td>{formatINR(r.delivered_cpm)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}
