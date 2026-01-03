export default function ExplanationItem({ impact, reasoning }: any) {
  const color =
    impact === "positive"
      ? "border-green-500"
      : impact === "negative"
      ? "border-red-500"
      : "border-gray-300";

  return (
    <div className={`border-l-4 ${color} p-3 mb-2 bg-white`}>
      <div className="font-medium capitalize">{impact}</div>
      <div className="text-sm text-gray-700 mt-1">
        {reasoning}
      </div>
    </div>
  );
}
