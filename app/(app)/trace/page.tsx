import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { MetricTraceMap } from "@/components/audit/MetricTraceMap";

export default async function MetricTracePage() {
  await requireUser();
  return (
    <>
      <SubContextBar
        eyebrow="Lineage and traceability"
        title="Metric Trace"
        right={<Badge tone="cyan" dot>Demo lineage</Badge>}
      />
      <main className="px-6 py-6 space-y-4">
        <p className="max-w-3xl text-[13.5px] text-slate">
          Metric Trace maps how a claim connects to its definition, time period, segment context,
          source dataset, calculation notes, and evidence hash. Validators rely on this lineage
          to judge whether a claim is supported by the underlying data.
        </p>
        <MetricTraceMap />
      </main>
    </>
  );
}
