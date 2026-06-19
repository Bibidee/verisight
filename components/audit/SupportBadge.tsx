import { Badge } from "./Badge";

export type Verdict =
  | "supported" | "partially_supported" | "unsupported" | "misleading" | "needs_more_evidence";

const map: Record<Verdict, { tone: "verified" | "amber" | "claim" | "slate"; label: string }> = {
  supported:           { tone: "verified", label: "Supported" },
  partially_supported: { tone: "amber",    label: "Partially supported" },
  unsupported:         { tone: "claim",    label: "Unsupported" },
  misleading:          { tone: "claim",    label: "Misleading" },
  needs_more_evidence: { tone: "slate",    label: "Needs more evidence" },
};

export function SupportBadge({ verdict }: { verdict: Verdict }) {
  const v = map[verdict];
  return <Badge tone={v.tone} dot>{v.label}</Badge>;
}
