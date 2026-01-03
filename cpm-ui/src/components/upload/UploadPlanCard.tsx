import { useState } from "react";
import Card from "../common/Card";
import { parseCSV } from "../../services/csv";

export default function UploadPlanCard({
  onParsed,
}: {
  onParsed: (row: any) => void;
}) {
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    try {
      const rows = await parseCSV(file);
      if (!rows.length) throw new Error("CSV is empty");
      onParsed(rows[0]); // single campaign
    } catch (e: any) {
      setError("Invalid CSV format. Please check guidelines.");
    }
  };

  return (
    <Card title="Upload Your Media Plan">
      <label className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-8 cursor-pointer hover:border-indigo-500 transition">
        <input
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => e.target.files && handleFile(e.target.files[0])}
        />

        <p className="text-sm text-gray-600">
          Upload your media plan CSV
        </p>
        <p className="text-xs text-gray-400 mt-1">
          One campaign per file
        </p>
      </label>

      {error && (
        <p className="text-red-600 text-sm mt-3">{error}</p>
      )}
    </Card>
  );
}
