export default function FinalCPMCard({ value }: { value: number }) {
  return (
    <div className="card highlight">
      <h2>Final Blended CPM</h2>
      <div className="price">₹{value}</div>
    </div>
  );
}
