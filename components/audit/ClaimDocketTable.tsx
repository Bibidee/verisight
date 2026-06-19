import Link from "next/link";
import { Badge } from "./Badge";

export type DocketRow = {
  id: string;
  claim: string;
  workspace?: string | null;
  metric?: string | null;
  status: string;
  created_at: string;
};

const statusTone: Record<string, "slate" | "amber" | "consensus" | "verified" | "claim"> = {
  draft: "slate", evidence_added: "slate", ready: "blue" as never,
  submitted: "consensus", consensus_pending: "amber",
  verdict_issued: "verified", needs_more_evidence: "amber", archived: "slate",
};

export function ClaimDocketTable({ rows }: { rows: DocketRow[] }) {
  return (
    <table className="ledger-table">
      <thead>
        <tr>
          <th>Claim</th>
          <th>Workspace</th>
          <th>Metric</th>
          <th>Status</th>
          <th>Last updated</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.id}>
            <td>
              <Link href={`/audits/${r.id}`} className="display text-[14px] font-medium text-ink hover:underline">
                {r.claim}
              </Link>
              <div className="mono mt-0.5 text-[10px] uppercase tracking-[0.14em] text-slate">
                docket · {r.id.slice(0, 8)}
              </div>
            </td>
            <td className="text-slate">{r.workspace ?? "—"}</td>
            <td className="text-slate">{r.metric ?? "—"}</td>
            <td>
              <Badge tone={statusTone[r.status] ?? "slate"}>{r.status.replace(/_/g, " ")}</Badge>
            </td>
            <td className="text-slate">{new Date(r.created_at).toLocaleDateString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
