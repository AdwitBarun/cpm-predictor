// export default function FinalCPMCard({ value }: { value: number }) {
//   return (
//     <div className="card highlight">
//       <h2>Final Blended CPM</h2>
//       <div className="price">₹{value}</div>
//     </div>
//   );
// }
export default function FinalCPMCard({ value }: { value: number }) {
  return (
    <div className="card highlight" style={{ textAlign: "center" }}>
      <h2>Final Blended CPM</h2>
      <div className="price" style={{ fontSize: "32px", fontWeight: 700 }}>
        ₹{value}
      </div>
    </div>
  );
}
