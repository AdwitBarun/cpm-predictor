import Card from "../common/Card";

export default function ExampleDownload() {
  const download = () => {
    const csv = `Device,TG,Markets,Start Date,End Date,Planned Reach 1+,Planned Freq,Planned Budget,Planned Impressions
YT NSK,F 25-44 NCCS AB,Maharashtra;Gujarat,2025-07-15,2025-09-15,480000,6.5,3200000,2900000`;

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "example_media_plan.csv";
    a.click();
  };

  return (
    <Card title="Need an Example?">
      <button
        onClick={download}
        className="text-indigo-600 text-sm font-medium hover:underline"
      >
        Download example media plan CSV
      </button>
    </Card>
  );
}
