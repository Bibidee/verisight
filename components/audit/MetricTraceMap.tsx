import { ReactNode } from "react";

export function MetricTraceMap({
  metric = "Quarterly revenue by customer type",
  definition = "Sum of net revenue grouped by customer_type for the selected quarter.",
  timePeriod = "Q3 — North America",
  segment = "Customer type ∈ {new, repeat}; channel = direct",
  dataset = "fact_revenue (warehouse snapshot)",
  notes = "Excludes returns; refund-aware net revenue.",
  evidenceHash = "sha256:9f01…be21",
}: {
  metric?: string;
  definition?: string;
  timePeriod?: string;
  segment?: string;
  dataset?: string;
  notes?: string;
  evidenceHash?: string;
}) {
  return (
    <div className="doc p-6">
      <div className="eyebrow eyebrow-slate">Metric trace · lineage</div>
      <h2 className="display mt-1 text-section font-semibold text-ink">{metric}</h2>

      <div className="mt-6 grid grid-cols-1 gap-3 lg:grid-cols-[260px_1fr_260px]">
        <Node label="Metric definition" body={definition} />
        <Connector />
        <Node label="Time period" body={timePeriod} accent />
        <Connector vertical />
        <div />
        <Connector vertical />
        <Node label="Segment / filter context" body={segment} />
        <Connector />
        <Node label="Dataset summary" body={dataset} accent />
        <Connector vertical />
        <div />
        <Connector vertical />
        <Node label="Known limitations" body={notes} />
        <Connector />
        <Node label="Evidence hash" body={<span className="hash">{evidenceHash}</span>} accent />
      </div>
    </div>
  );
}

function Node({ label, body, accent }: { label: string; body: ReactNode; accent?: boolean }) {
  return (
    <div className={accent
      ? "rounded-panel border border-exec-blue/30 bg-blue-steel p-3"
      : "rounded-panel border border-auditline bg-white-ledger p-3"
    }>
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className="mt-1 text-[13px] text-ink">{body}</div>
    </div>
  );
}

function Connector({ vertical }: { vertical?: boolean }) {
  return (
    <div className="flex items-center justify-center">
      <div
        className={vertical
          ? "h-6 w-px bg-auditline"
          : "h-px w-full bg-auditline"
        }
      />
    </div>
  );
}
