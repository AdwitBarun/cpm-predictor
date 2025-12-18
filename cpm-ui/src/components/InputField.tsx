type Props = {
  field: any
  value: any
  onChange: (key: string, value: any) => void
}

export default function InputField({ field, value, onChange }: Props) {
  if (field.type === "select") {
    return (
      <div>
        <label className="block text-sm mb-1">{field.label}</label>
        <select
          className="w-full border px-3 py-2 rounded"
          value={value || ""}
          onChange={(e) => onChange(field.key, e.target.value)}
        >
          <option value="">Select</option>
          {field.options.map((opt: string) => (
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
      <label className="block text-sm mb-1">{field.label}</label>
      <input
        type="number"
        className="w-full border px-3 py-2 rounded"
        value={value || ""}
        onChange={(e) => onChange(field.key, Number(e.target.value))}
      />
    </div>
  )
}
