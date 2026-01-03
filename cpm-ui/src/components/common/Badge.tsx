export default function Badge({ text }: { text: string }) {
  return (
    <span className="bg-indigo-100 text-indigo-700 text-xs px-2 py-1 rounded">
      {text}
    </span>
  );
}
