import { useState } from "react";
import Papa from "papaparse";
import Card from "../common/Card";

export default function UploadPlanCard({ onSubmit }: any) {
  const [fileName, setFileName] = useState("");

  const handleFile = (file: File) => {
    setFileName(file.name);

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (res) => {
        const raw = res.data[0];

        const normalized = {
          Campaign_Name: raw["Campaign Name"],
          Advertiser: raw["Advertiser"],
          Device: raw["Device"],
          Mobile_CTV: raw["Mobile / CTV"],
          TG: raw["TG"],
          Markets: raw["Markets"],
          Start_Date: raw["Start Date"],
          End_Date: raw["End Date"],
          Planned_Reach_1_plus: Number(raw["Planned Reach 1+"]),
          Planned_Freq: Number(raw["Planned Freq"]),
          Planned_Budget: Number(raw["Planned Budget"]),
          Planned_Impressions: Number(raw["Planned Impressions"]),
          Inventory_Mode: raw["Inventory Mode"],
          Buying_Platform: raw["Buying Platform"],
        };

        console.log("✅ Normalized payload:", normalized);

        onSubmit(normalized); // send to backend
      },
    });
  };

  return (
    <Card title="Upload Your Media Plan">
      <div
        className="border-2 border-dashed rounded p-6 text-center cursor-pointer bg-gray-50 hover:bg-gray-100 transition"
        onClick={() => document.getElementById("file")?.click()}
      >
        <input
          id="file"
          type="file"
          accept=".csv"
          hidden
          onChange={(e) =>
            e.target.files && handleFile(e.target.files[0])
          }
        />

        <p className="font-medium">
          Drag & drop your CSV or click to upload
        </p>
        <p className="text-sm text-gray-500 mt-1">
          One campaign per file
        </p>
      </div>

      <div className="flex gap-4 mt-3 text-sm">
        <a
          href="/campaign.csv"
          download
          className="text-blue-600 underline"
        >
          Download example CSV
        </a>
        <span className="text-gray-500">
          Required columns shown in example
        </span>
      </div>

      {fileName && (
        <p className="mt-3 text-green-700 font-medium">
          ✅ Uploaded: {fileName}
        </p>
      )}
    </Card>
  );
}
