import { useState } from "react"
import { featureSchema } from "./schema/featureSchema"
import InputField from "./components/InputField"
import Loader from "./components/Loader"
import ResultCard from "./components/ResultCard"
import { predictCPM } from "./services/api"

export default function App() {
  const [form, setForm] = useState<any>({})
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const updateField = (key: string, value: any) => {
    setForm({ ...form, [key]: value })
  }

  const submit = async () => {
    setLoading(true)
    setResult(null)
    const res = await predictCPM(form)
    setResult(res)
    setLoading(false)
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-6">
        CPM Prediction Tool
      </h1>

      <div className="grid grid-cols-2 gap-4">
        {featureSchema.map((f) => (
          <InputField
            key={f.key}
            field={f}
            value={form[f.key]}
            onChange={updateField}
          />
        ))}
      </div>

      <button
        onClick={submit}
        className="mt-6 px-6 py-2 bg-primary text-white rounded"
      >
        Predict CPM
      </button>

      {loading && <Loader />}
      {result && <ResultCard result={result} />}
    </div>
  )
}
