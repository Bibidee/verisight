import { ReactNode } from "react";
import { Badge } from "./Badge";

type Note = { kind: "causality" | "comparison" | "segment" | "metric" | "evidence"; text: string };

const kindLabel: Record<Note["kind"], string> = {
  causality: "Causality risk",
  comparison: "Missing comparison group",
  segment: "Segment limitation",
  metric: "Metric definition gap",
  evidence: "Evidence limitation",
};

export function AssumptionReviewPanel({
  notes,
  empty,
}: {
  notes?: Note[];
  empty?: ReactNode;
}) {
  if (!notes || notes.length === 0) {
    return (
      <div className="doc">
        <div className="border-b border-auditline px-5 py-3">
          <div className="eyebrow eyebrow-slate">Assumption review</div>
          <div className="display mt-0.5 text-[15px] font-semibold text-ink">
            What the claim assumes but does not prove
          </div>
        </div>
        <div className="px-5 py-8 text-center text-[13px] text-slate">{empty ?? "No assumptions flagged yet."}</div>
      </div>
    );
  }
  return (
    <div className="doc">
      <div className="border-b border-auditline px-5 py-3">
        <div className="eyebrow eyebrow-slate">Assumption review</div>
        <div className="display mt-0.5 text-[15px] font-semibold text-ink">
          What the claim assumes but does not prove
        </div>
      </div>
      <ul className="divide-y divide-auditline">
        {notes.map((n, i) => (
          <li key={i} className="flex items-start gap-3 px-5 py-3">
            <span className="mt-1 inline-block h-2 w-2 shrink-0 rounded-full bg-amber" />
            <div className="min-w-0 flex-1">
              <Badge tone="amber">{kindLabel[n.kind]}</Badge>
              <div className="mt-1 text-[13.5px] text-ink">{n.text}</div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
