import Card from "../common/Card";
import { formatINR } from "../../utils/format";

export default function FinalCPMCard({ value }: { value: number }) {
  return (
    <Card title="Final Blended CPM">
      <div className="text-3xl font-extrabold text-indigo-600">
        {formatINR(value)}
      </div>
    </Card>
  );
}
