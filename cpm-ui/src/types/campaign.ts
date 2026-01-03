export interface CampaignInput {
  Device: string;
  TG: string;
  Markets: string;
  "Mobile / CTV"?: string;

  "Start Date": string;
  "End Date": string;

  "Planned Reach 1+": number;
  "Planned Freq": number;
  "Planned Budget": number;
  "Planned Impressions": number;

  "Campaign Name"?: string;
  Advertiser?: string;
}
