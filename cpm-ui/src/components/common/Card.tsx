export default function Card({
  title,
  children,
}: {
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white border rounded-xl p-5 shadow-sm">
      {title && <h3 className="font-semibold mb-4">{title}</h3>}
      {children}
    </div>
  );
}
