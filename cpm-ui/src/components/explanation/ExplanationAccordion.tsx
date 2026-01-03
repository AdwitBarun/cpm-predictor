import ExplanationItem from "./ExplanationItem";

export default function ExplanationAccordion({ impacts }: { impacts: any[] }) {
  return (
    <div className="space-y-3">
      {impacts.map((i, idx) => (
        <ExplanationItem key={idx} text={i.explanation} />
      ))}
    </div>
  );
}
