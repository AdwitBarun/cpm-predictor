export type FeatureField = {
  key: string
  label: string
  type: "number" | "select"
  options?: string[]
}

export const featureSchema: FeatureField[] = [
  {
    key: "Device",
    label: "Device",
    type: "select",
    options: ["YT NSK", "YT Skippable", "CTV"]
  },
  {
    key: "TG",
    label: "Target Group",
    type: "select",
    options: ["M18-24", "F25-44", "M25-44"]
  },
  {
    key: "Planned_Budget",
    label: "Planned Budget",
    type: "number"
  },
  {
    key: "Planned_Impressions",
    label: "Planned Impressions",
    type: "number"
  },
  {
    key: "Planned_Freq",
    label: "Planned Frequency",
    type: "number"
  },
  {
    key: "Inventory_Mode",
    label: "Inventory Mode",
    type: "select",
    options: ["Limited", "Standard"]
  },
  {
    key: "Video_Ad_Format",
    label: "Video Ad Format",
    type: "select",
    options: ["Non Skippable", "Skippable"]
  },
  {
    key: "campaign_duration_days",
    label: "Campaign Duration (days)",
    type: "number"
  }
]
