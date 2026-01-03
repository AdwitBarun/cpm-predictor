import Card from "../common/Card";


export default function ExampleDownload() {
  return (
    <Card title="Need an Example?">
      <a
        href="/campaign.csv"
        download="campaign.csv"
        className="text-indigo-600 text-sm font-medium hover:underline"
      >
        Download example media plan CSV
      </a>
    </Card>
  );
}


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
