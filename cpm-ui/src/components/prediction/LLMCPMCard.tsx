import Card from "../common/Card";
import { formatINR } from "../../utils/format";

export default function LLMCPMCard({ value }: { value: number }) {
  return (
    <Card title="LLM Adjusted CPM">
      <div className="text-2xl font-bold">{formatINR(value)}</div>
    </Card>
  );
}
