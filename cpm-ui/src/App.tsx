import { useState } from "react";
import InputField from "./components/InputField";
import Loader from "./components/Loader";
import ResultCard from "./components/ResultCard";
import { numericFields, categoricalFields } from "./schema/FeatureSchema";
import { predictCPM } from "./services/api";

export default function App() {
  const [form, setForm] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const update = (key: string, value: any) =>
    setForm({ ...form, [key]: value });

  const submit = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await predictCPM(form);
      setResult(res);
    } catch (e) {
      alert("Prediction failed. Check backend logs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">CPM Prediction Tool</h1>

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
