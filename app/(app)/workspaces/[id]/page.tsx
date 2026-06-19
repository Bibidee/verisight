import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";

export default async function WorkspaceDetailPage({
  params,
}: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { supabase } = await requireUser();

  const { data: workspace } = await supabase.from("workspaces").select("*").eq("id", id).single();
  if (!workspace) notFound();

  const { data: audits } = await supabase
    .from("insight_audit_cases")
    .select("id,insight_claim,status,created_at,metric_name")
    .eq("workspace_id", id)
    .order("created_at", { ascending: false });

  return (
    <>
      <SubContextBar
        eyebrow="Workspace"
        title={workspace.name}
        workspaceName={workspace.organisation_name}
        right={
          <Link href={`/audits/new?workspace=${workspace.id}`} className="btn-consensus">
            <span className="dot bg-white" /> Audit an insight
          </Link>
        }
      />
      <main className="px-6 py-6 space-y-6">
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {[
            ["Business function", workspace.business_function],
            ["Industry", workspace.industry],
            ["Reporting cadence", workspace.reporting_cadence],
            ["Primary KPI category", workspace.primary_kpi_category],
          ].map(([label, val]) => (
            <div key={String(label)} className="doc p-4">
              <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
              <div className="mt-1 text-sm text-ink">{(val as string) ?? "—"}</div>
            </div>
          ))}
        </div>

        <article className="doc overflow-hidden">
          <div className="flex items-center justify-between border-b border-auditline px-5 py-3">
            <div>
              <div className="eyebrow eyebrow-slate">Claim docket</div>
              <div className="display text-[15px] font-semibold text-ink">Submitted claims</div>
            </div>
          </div>
          {audits && audits.length > 0 ? (
            <table className="ledger-table">
              <thead><tr><th>Claim</th><th>Metric</th><th>Status</th><th>Created</th></tr></thead>
              <tbody>
                {audits.map((a) => (
                  <tr key={a.id}>
                    <td><Link href={`/audits/${a.id}`} className="link">{a.insight_claim}</Link></td>
                    <td className="text-slate">{a.metric_name ?? "—"}</td>
                    <td><Badge tone="slate">{a.status.replace(/_/g, " ")}</Badge></td>
                    <td className="text-slate">{new Date(a.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState
              title="No claims docketed in this workspace yet"
              body="Submit a dashboard claim and VeriSight will prepare it for GenLayer judgment."
            />
          )}
        </article>
      </main>
    </>
  );
}
