import { useState } from "react"
import { predictCPM } from "./services/api"

import InputField from "./components/InputField"
import ResultCard from "./components/ResultCard"
import Loader from "./components/Loader"
import { featureSchema } from "./schema/featureSchema"

export default function App() {
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (key: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }))
  }

const handleSubmit = async () => {
  setLoading(true)
  setError(null)
  setResult(null)

  try {
    // 🔑 Convert numeric fields here
    const payload = { ...formData }

    featureSchema.forEach((f) => {
      if (f.type === "number" && payload[f.key] !== "") {
        payload[f.key] = Number(payload[f.key])
      }
    })

    const response = await predictCPM(payload)
    setResult(response)
  } catch (err) {
    setError("Failed to predict CPM.")
  } finally {
    setLoading(false)
  }
}

  // ✅ IMPORTANT: JSX MUST BE RETURNED
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-4xl space-y-6">

        {/* Header */}
        <header className="rounded-lg bg-white p-6 shadow">
          <h1 className="text-2xl font-semibold text-gray-900">
            CPM Predictor
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Estimate campaign CPM using historical data and AI adjustment
          </p>
        </header>

        {/* Input Section */}
        <section className="rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-lg font-medium text-gray-800">
            Campaign Inputs
          </h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {featureSchema.map((field) => (
              <InputField
                key={field.key}
                field={field}
                value={formData[field.key]}
                onChange={(value) => handleChange(field.key, value)}
              />
            ))}
          </div>

          <div className="mt-6">
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full rounded-md bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Predicting..." : "Predict CPM"}
            </button>
          </div>

          {error && (
            <p className="mt-3 text-sm text-red-600">
              {error}
            </p>
          )}
        </section>

        {/* Loading */}
        {loading && <Loader />}

        {/* Result */}
        {result && <ResultCard result={result} />}
      </div>
    </div>
  )
}
console.log(import.meta.env.VITE_API_BASE_URL)
