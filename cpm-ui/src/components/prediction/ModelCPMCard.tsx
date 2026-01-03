import Card from "../common/Card";
import { formatINR } from "../../utils/format";

export default function ModelCPMCard({ value }: { value: number }) {
  return (
    <Card title="Model CPM">
      <div className="text-2xl font-bold">{formatINR(value)}</div>
    </Card>
  );
}
