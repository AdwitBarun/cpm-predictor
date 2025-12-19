type Props = {
  label: string;
  value: any;
  onChange: (v: any) => void;
  type?: string;
  placeholder?: string;
};

export default function InputField({
  label,
  value,
  onChange,
  type = "text",
  placeholder,
}: Props) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      <input
        type={type}
        value={value ?? ""}
        placeholder={placeholder}
        onChange={(e) => onChange(type === "number" ? Number(e.target.value) : e.target.value)}
        className="border rounded px-3 py-2 focus:outline-none focus:ring focus:ring-blue-300"
      />
    </div>
  );
}
