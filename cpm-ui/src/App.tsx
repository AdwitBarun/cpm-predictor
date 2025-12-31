import { useState } from "react";
import Papa from "papaparse";

import InputField from "./components/InputField";
import Loader from "./components/Loader";
import ResultCard from "./components/ResultCard";

import { numericFields, categoricalFields } from "./schema/featureSchema";
import { predictCPM } from "./services/api";

export default function App() {
  const [form, setForm] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const update = (key: string, value: any) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  // ------------------------------
  // CSV Upload Handler
  // ------------------------------
  const handleCSV = (e: any) => {
    const file = e.target.files?.[0];
    if (!file) return;

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (res) => {
        const row = res.data[0] as any;
        setForm((prev) => ({ ...prev, ...row }));
        alert("CSV loaded — fields auto-filled!");
      },
    });
  };

  // ------------------------------
  // Templates
  // ------------------------------
  const applyTemplate = (template: string) => {
    if (!template) return;

    if (template === "nsk_awareness") {
      setForm((prev) => ({
        ...prev,
        Video_Ad_Format: "Non Skippable",
        Inventory_Mode: "Limited",
        Pacing: "Daily",
        Planned_Freq: 2,
        Type: "Awareness",
      }));
    }

    if (template === "trueview_performance") {
      setForm((prev) => ({
        ...prev,
        Video_Ad_Format: "Skippable",
        Inventory_Mode: "Expanded",
        Type: "Performance",
        Pacing: "Accelerated",
      }));
    }
  };

  // ------------------------------
  // Submit
  // ------------------------------
  const submit = async () => {
    setLoading(true);
    setResult(null);

    const payload: Record<string, any> = {};

    Object.entries(form).forEach(([k, v]) => {
      if (v === "" || v === undefined) payload[k] = null;
      else payload[k] = v;
    });

    try {
      const res = await predictCPM(payload);
      setResult(res);
    } catch (e) {
      console.error(e);
      alert("Prediction failed — check backend logs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">CPM Prediction Tool</h1>

        {/* CSV Upload + Templates */}
        <div className="bg-white p-4 rounded shadow mb-6 flex gap-6">
          <div>
            <p className="font-medium mb-1">Upload Campaign CSV</p>
            <input type="file" accept=".csv" onChange={handleCSV} />
          </div>

          <div>
            <p className="font-medium mb-1">Quick Templates</p>
            <select
              className="border rounded px-3 py-2"
              onChange={(e) => applyTemplate(e.target.value)}
            >
              <option value="">Select…</option>
              <option value="nsk_awareness">
                YouTube Non-Skippable — Awareness
              </option>
              <option value="trueview_performance">
                TrueView — Performance
              </option>
            </select>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white p-6 rounded shadow grid grid-cols-3 gap-4">
          {numericFields.map((f) => (
            <InputField
              key={f.key}
              label={f.label}
              type="number"
              value={form[f.key]}
              onChange={(v) => update(f.key, v)}
            />
          ))}

          {categoricalFields.map((f) => (
            <InputField
              key={f.key}
              label={f.label}
              value={form[f.key]}
              placeholder={f.placeholder}
              onChange={(v) => update(f.key, v)}
            />
          ))}
        </div>

        {/* Submit */}
        <button
          onClick={submit}
          className="mt-6 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
        >
          Predict CPM
        </button>

        {loading && <Loader />}
        {result && <ResultCard data={result} />}
      </div>
    </div>
  );
}
