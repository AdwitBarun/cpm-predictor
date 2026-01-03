import { LLMRange } from "../../types/api";

export default function ExplanationAccordion({ llm }: { llm: LLMRange }) {
  return (
    <div className="card">
      <h3>Why this CPM?</h3>

      {llm.tool_impacts.map((tool, idx) => {
        const json = tool.explanation.match(/\{[\s\S]*\}/);
        if (!json) return null;

        const parsed = JSON.parse(json[0]);

        return (
          <div key={idx} className="explanation">
            <strong>{parsed.impact.toUpperCase()}</strong>{" "}
            ({parsed.adjustment_factor}×)
            <p>{parsed.reasoning}</p>
          </div>
        );
      })}
    </div>
  );
}
