import Card from "../common/Card";

export default function CsvGuidelines() {
  return (
    <Card title="CSV Guidelines">
      <ul className="text-sm text-gray-700 space-y-2">
        <li>• Columns must match training format</li>
        <li>• Date format: YYYY-MM-DD</li>
        <li>• One campaign per CSV</li>
        <li>• Geography separated by semicolons</li>
        <li>• TG example: <b>F 25-44 NCCS AB</b></li>
      </ul>
    </Card>
  );
}
