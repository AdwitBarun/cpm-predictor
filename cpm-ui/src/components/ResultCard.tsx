type Props = {
  data: any;
};

export default function ResultCard({ data }: Props) {
  const { historical, llm, final } = data;

  return (
    <div className="bg-white shadow-lg rounded-lg p-6 mt-6 space-y-4">
      <h2 className="text-xl font-semibold text-gray-800">
        CPM Forecast (₹)
      </h2>

      <div className="grid grid-cols-3 gap-4">
        <Metric title="Low (P10)" value={historical.p10} />
        <Metric title="Expected (P50)" value={historical.p50} />
        <Metric title="High (P90)" value={historical.p90} />
      </div>

      <div className="border-t pt-4">
        <p className="text-sm text-gray-600">Final Recommended Range</p>
        <p className="text-2xl font-bold text-blue-600">
          ₹ {final.low} – ₹ {final.high}
        </p>
      </div>

      {llm?.commentary && (
        <p className="text-sm text-gray-700 italic">
          {llm.commentary}
        </p>
      )}
    </div>
  );
}

function Metric({ title, value }: { title: string; value: number }) {
  return (
    <div className="bg-gray-50 rounded p-4 text-center">
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-lg font-semibold">₹ {value}</p>
    </div>
  );
}
