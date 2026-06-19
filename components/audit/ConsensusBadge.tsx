import { Badge } from "./Badge";

export function ConsensusBadge({ state = "reached" }: { state?: "reached" | "pending" | "failed" }) {
  if (state === "pending") return <Badge tone="amber" dot>Consensus pending</Badge>;
  if (state === "failed") return <Badge tone="claim" dot>Consensus failed</Badge>;
  return <Badge tone="consensus" dot>Validated by GenLayer</Badge>;
}
