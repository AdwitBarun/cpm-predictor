import React from "react"

interface FieldSchema {
  key: string
  label: string
  type: "number" | "select" | "text"
  options?: string[]
  placeholder?: string
}

interface Props {
  field: FieldSchema
  value: any
  onChange: (value: any) => void
}

export default function InputField({ field, value, onChange }: Props) {
  // 🔑 Always pass a string to inputs
  const safeValue = value ?? ""

  if (field.type === "select") {
    return (
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {field.label}
        </label>
        <select
          value={safeValue}
          onChange={(e) => onChange(e.target.value)}
          className="w-full rounded-md border px-3 py-2 text-sm"
        >
          <option value="">Select</option>
          {field.options?.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>
    )
  }

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {field.label}
      </label>
      <input
        type={field.type}
        value={safeValue}
        placeholder={field.placeholder}
        onChange={(e) => onChange(e.target.value)} // 👈 DO NOT Number() here
        className="w-full rounded-md border px-3 py-2 text-sm"
      />
    </div>
  )
}
