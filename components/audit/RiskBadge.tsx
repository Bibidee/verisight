import { Badge } from "./Badge";

export function RiskBadge({ level = "moderate" }: { level?: "low" | "moderate" | "high" }) {
  if (level === "high") return <Badge tone="claim" dot>High business risk</Badge>;
  if (level === "low") return <Badge tone="verified" dot>Low business risk</Badge>;
  return <Badge tone="amber" dot>Moderate business risk</Badge>;
}
