export default function ExplanationItem({ text }: { text: string }) {
  return (
    <div className="border-l-4 border-indigo-500 pl-3 text-sm text-gray-700">
      {text.replace(/```json|```/g, "")}
    </div>
  );
}
