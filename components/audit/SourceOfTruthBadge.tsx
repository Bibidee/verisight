import { Badge } from "./Badge";

export function SourceOfTruthBadge({ small }: { small?: boolean }) {
  return (
    <Badge tone="consensus" dot className={small ? "text-[10.5px]" : undefined}>
      Source of truth · GenLayer
    </Badge>
  );
}
