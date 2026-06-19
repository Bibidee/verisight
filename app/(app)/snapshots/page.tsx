import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { HashText } from "@/components/audit/HashText";

export default async function SnapshotsPage() {
  const { supabase } = await requireUser();
  const { data: snaps } = await supabase
    .from("data_snapshots")
    .select("id,audit_case_id,source_type,source_url,snapshot_hash,created_at")
    .order("created_at", { ascending: false });

  return (
    <>
      <SubContextBar
        eyebrow="Metric evidence registry"
        title="Dataset Snapshots"
        right={<Badge tone="cyan" dot>{snaps?.length ?? 0} snapshots</Badge>}
      />
      <main className="px-6 py-6">
        <article className="doc overflow-hidden">
          <div className="border-b border-auditline px-5 py-3">
            <div className="eyebrow eyebrow-slate">Snapshot ledger</div>
            <div className="display text-[15px] font-semibold text-ink">All registered snapshots</div>
          </div>
          {snaps && snaps.length > 0 ? (
            <table className="ledger-table">
              <thead><tr><th>Source</th><th>Snapshot hash</th><th>Linked claim</th><th>Created</th></tr></thead>
              <tbody>
                {snaps.map((s) => (
                  <tr key={s.id}>
                    <td><Badge tone="cyan">{s.source_type ?? "—"}</Badge></td>
                    <td><HashText value={s.snapshot_hash ?? "—"} short /></td>
                    <td><HashText value={s.audit_case_id} short /></td>
                    <td className="text-slate">{new Date(s.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState
              title="No dataset snapshots yet"
              body="Dataset snapshots help validators understand the metric context behind an insight claim."
            />
          )}
        </article>
      </main>
    </>
  );
}
