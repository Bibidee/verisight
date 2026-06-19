import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { HashText } from "@/components/audit/HashText";

export default async function GenLayerJudgmentsPage() {
  const { supabase } = await requireUser();
  const { data: verdicts } = await supabase
    .from("genlayer_audit_verdicts")
    .select("id,audit_case_id,verdict,support_level,business_risk,contract_address,transaction_hash,evidence_digest,created_at")
    .order("created_at", { ascending: false });

  return (
    <>
      <SubContextBar
        eyebrow="Judgment archive"
        title="GenLayer Judgments"
        right={<Badge tone="consensus" dot>{verdicts?.length ?? 0} on record</Badge>}
      />
      <main className="px-6 py-6">
        <article className="doc overflow-hidden">
          <div className="border-b border-auditline px-5 py-3">
            <div className="eyebrow eyebrow-slate">Consensus verdict ledger</div>
            <div className="display text-[15px] font-semibold text-ink">All judgments issued</div>
          </div>
          {verdicts && verdicts.length > 0 ? (
            <table className="ledger-table">
              <thead>
                <tr>
                  <th>Audit ID</th>
                  <th>Verdict</th>
                  <th>Support</th>
                  <th>Business risk</th>
                  <th>Contract</th>
                  <th>Tx hash</th>
                  <th>Evidence digest</th>
                  <th>Issued</th>
                </tr>
              </thead>
              <tbody>
                {verdicts.map((v) => (
                  <tr key={v.id}>
                    <td>
                      <Link href={`/audits/${v.audit_case_id}`} className="link">
                        <HashText value={v.audit_case_id} short />
                      </Link>
                    </td>
                    <td className="text-ink">{v.verdict ?? "—"}</td>
                    <td><Badge tone="slate">{v.support_level ?? "—"}</Badge></td>
                    <td className="text-slate">{v.business_risk ?? "—"}</td>
                    <td><HashText value={v.contract_address ?? "—"} short /></td>
                    <td><HashText value={v.transaction_hash ?? "—"} short /></td>
                    <td><HashText value={v.evidence_digest ?? "—"} short /></td>
                    <td className="text-slate">{new Date(v.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState
              title="No judgments issued yet"
              body="Once GenLayer validators reach consensus on your first audit, judgments will appear here as a formal record."
            />
          )}
        </article>
      </main>
    </>
  );
}
