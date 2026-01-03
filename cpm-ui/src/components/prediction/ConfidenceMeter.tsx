import { confidenceLabel } from "../../utils/confidence";

export default function ConfidenceMeter({ value }: { value: number }) {
  return (
    <div>
      <div className="h-2 bg-gray-200 rounded">
        <div
          className="h-2 bg-green-500 rounded"
          style={{ width: `${value * 100}%` }}
        />
      </div>
      <p className="text-xs mt-1">{confidenceLabel(value)}</p>
    </div>
  );
}
