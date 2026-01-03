export default function ConfidenceMeter({ confidence }: any) {
  return (
    <div className="mt-6 p-4 border rounded bg-blue-50">
      <div className="flex justify-between">
        <span className="font-medium">Prediction Confidence</span>
        <span>{confidence * 100}%</span>
      </div>

      <div className="h-2 bg-gray-200 rounded mt-2">
        <div
          className="h-2 bg-blue-600 rounded"
          style={{ width: `${confidence * 100}%` }}
        />
      </div>

      <p className="text-xs text-gray-600 mt-2">
        Based on conformal prediction coverage
      </p>
    </div>
  );
}
