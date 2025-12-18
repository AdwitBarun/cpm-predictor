type Props = {
  result: any
}

export default function ResultCard({ result }: Props) {
  return (
    <div className="mt-6 border rounded p-4 bg-white">
      <h2 className="text-lg font-semibold mb-2">Predicted CPM Range</h2>

      <p>
        <strong>Final Range:</strong>{" "}
        {result.final_range.low} – {result.final_range.high}
      </p>

      <p className="mt-2 text-sm text-gray-600">
        {result.llm_range.explanation}
      </p>
    </div>
  )
}
