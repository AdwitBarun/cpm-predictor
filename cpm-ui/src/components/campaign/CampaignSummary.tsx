import Card from "../common/Card";

interface Props {
  campaign: Record<string, any>;
}

function getValue(
  data: Record<string, any>,
  keys: string[],
  fallback: string = "—"
) {
  for (const key of keys) {
    if (data?.[key] !== undefined && data?.[key] !== "") {
      return data[key];
    }
  }
  return fallback;
}

export default function CampaignSummary({ campaign }: Props) {
  if (!campaign || typeof campaign !== "object") return null;

  return (
    <Card title="Campaign Summary (From Uploaded CSV)">
      <div className="grid-2 text-sm">
        <SummaryItem
          label="Campaign Name"
          value={getValue(campaign, ["Campaign Name", "Campaign_Name"])}
        />
        <SummaryItem
          label="Advertiser"
          value={getValue(campaign, ["Advertiser"])}
        />
        <SummaryItem
          label="Planned Budget"
          value={getValue(campaign, ["Planned Budget", "Planned_Budget"])}
        />
        <SummaryItem
          label="Planned Reach"
          value={getValue(campaign, ["Planned Reach 1+", "Planned_Reach_1_plus"])}
        />
        <SummaryItem
          label="Planned Frequency"
          value={getValue(campaign, ["Planned Freq", "Planned_Freq"])}
        />
        <SummaryItem
          label="Target Group"
          value={getValue(campaign, ["TG", "Target Group"])}
        />
        <SummaryItem
          label="Device"
          value={getValue(campaign, ["Device"])}
        />
        <SummaryItem
          label="Markets"
          value={getValue(campaign, [
            "Markets",
            "Geography_Targeting_Include",
          ])}
        />
      </div>
    </Card>
  );
}

function SummaryItem({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="flex flex-col">
      <span className="text-xs text-gray-500">{label}</span>
      <span className="font-medium break-words">{value}</span>
    </div>
  );
}
