import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { HashText } from "@/components/audit/HashText";
import { ConsensusBadge } from "@/components/audit/ConsensusBadge";

export default async function AdminPage() {
  const { profile, supabase } = await getProfile();
  if (profile?.role !== "admin") redirect("/dashboard");

  const { data: cases } = await supabase
    .from("insight_audit_cases").select("id,insight_claim,status,created_at")
    .order("created_at", { ascending: false }).limit(50);
  const { data: logs } = await supabase
    .from("contract_activity_logs")
    .select("id,contract_address,transaction_hash,action,status,created_at")
    .order("created_at", { ascending: false }).limit(50);

  return (
    <>
      <SubContextBar
        eyebrow="Audit operations"
        title="Admin Review"
        right={
          <>
            <Badge tone="consensus" dot>StudioNet</Badge>
            <ConsensusBadge />
          </>
        }
      />
      <main className="px-6 py-6 space-y-6">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1.4fr_1fr]">
          <article className="doc overflow-hidden">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">Operations ledger</div>
              <div className="display text-[15px] font-semibold text-ink">Pending judgment requests</div>
            </div>
            {cases && cases.length > 0 ? (
              <table className="ledger-table">
                <thead><tr><th>Audit ID</th><th>Claim</th><th>Status</th><th>Created</th></tr></thead>
                <tbody>
                  {cases.map((c) => (
                    <tr key={c.id}>
                      <td><HashText value={c.id} short /></td>
                      <td className="text-ink">{c.insight_claim}</td>
                      <td><Badge tone="slate">{c.status.replace(/_/g, " ")}</Badge></td>
                      <td className="text-slate">{new Date(c.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState title="No audits to review yet"
                body="Audits will appear here once users submit insight claims for GenLayer consensus." />
            )}
          </article>

          <article className="doc overflow-hidden">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">Contract trace</div>
              <div className="display text-[15px] font-semibold text-ink">Contract activity</div>
            </div>
            <div className="divide-y divide-auditline">
              {logs && logs.length > 0 ? logs.map((l) => (
                <div key={l.id} className="flex items-start justify-between gap-3 px-5 py-3 text-[12.5px]">
                  <div className="space-y-1">
                    <div className="text-ink">{l.action}</div>
                    <HashText value={l.transaction_hash ?? l.contract_address ?? "—"} short />
                  </div>
                  <Badge tone={l.status === "ok" ? "verified" : "amber"} dot>{l.status}</Badge>
                </div>
              )) : (
                <EmptyState title="No contract activity yet"
                  body="GenLayer calls and verdict mirroring events will stream here once audits run." />
              )}
            </div>
          </article>
        </div>
      </main>
    </>
  );
}
