import Card from "../common/Card";
import SummaryItem from "./SummaryItem";

export default function CampaignSummary({ data }: { data: any }) {
  return (
    <Card title="Campaign Summary">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <SummaryItem label="Budget (₹)" value={data["Planned Budget"]} />
        <SummaryItem label="Reach" value={data["Planned Reach 1+"]} />
        <SummaryItem label="Frequency" value={data["Planned Freq"]} />
        <SummaryItem label="Target Group" value={data["TG"]} />
        <SummaryItem label="Device" value={data["Device"]} />
        <SummaryItem label="Markets" value={data["Markets"]} />
      </div>
    </Card>
  );
}
