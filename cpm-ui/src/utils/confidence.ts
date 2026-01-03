export const confidenceLabel = (c: number) => {
  if (c >= 0.9) return "High confidence";
  if (c >= 0.75) return "Medium confidence";
  return "Low confidence";
};
