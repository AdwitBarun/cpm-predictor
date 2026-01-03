export const REQUIRED_COLUMNS = [
  "Device",
  "TG",
  "Markets",
  "Start Date",
  "End Date",
  "Planned Reach 1+",
  "Planned Freq",
  "Planned Budget",
  "Planned Impressions",
];

export const OPTIONAL_COLUMNS = [
  "Campaign Name",
  "Advertiser",
  "Mobile / CTV",
];

export const ALL_COLUMNS = [
  ...REQUIRED_COLUMNS,
  ...OPTIONAL_COLUMNS,
];
