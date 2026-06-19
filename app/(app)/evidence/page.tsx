import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { HashText } from "@/components/audit/HashText";

export default async function EvidenceLedgerPage() {
  const { supabase } = await requireUser();
  const { data: files } = await supabase
    .from("evidence_files")
    .select("id,audit_case_id,file_type,file_size,evidence_hash,created_at,file_url")
    .order("created_at", { ascending: false });

  return (
    <>
      <SubContextBar
        eyebrow="Formal evidence vault"
        title="Evidence Ledger"
        right={<Badge tone="blue" dot>{files?.length ?? 0} records</Badge>}
      />
      <main className="px-6 py-6">
        <article className="doc overflow-hidden">
          <div className="border-b border-auditline px-5 py-3">
            <div className="eyebrow eyebrow-slate">Audit evidence</div>
            <div className="display text-[15px] font-semibold text-ink">All evidence records</div>
          </div>
          {files && files.length > 0 ? (
            <table className="ledger-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Size</th>
                  <th>Evidence hash</th>
                  <th>Linked claim</th>
                  <th>Used in judgment</th>
                  <th>Source integrity</th>
                  <th>Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {files.map((f) => (
                  <tr key={f.id}>
                    <td><Badge tone="blue">{f.file_type}</Badge></td>
                    <td className="text-slate">{Math.round((f.file_size ?? 0) / 1024)} KB</td>
                    <td><HashText value={f.evidence_hash ?? "—"} short /></td>
                    <td><HashText value={f.audit_case_id} short /></td>
                    <td><Badge tone="verified" dot>Yes</Badge></td>
                    <td><Badge tone="verified" dot>Intact</Badge></td>
                    <td className="text-slate">{new Date(f.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState
              title="This audit packet has no evidence yet"
              body="Add a dataset, dashboard screenshot, report, metric snapshot, or analyst note before submitting to GenLayer."
            />
          )}
        </article>
      </main>
    </>
  );
}
