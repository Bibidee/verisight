import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { CreateWorkspaceForm } from "./CreateWorkspaceForm";

export default async function WorkspacesPage() {
  const { supabase } = await requireUser();
  const { data: workspaces } = await supabase
    .from("workspaces")
    .select("id,name,organisation_name,business_function,industry,primary_kpi_category,reporting_cadence,created_at")
    .order("created_at", { ascending: false });

  return (
    <>
      <SubContextBar
        eyebrow="Analytics environments"
        title="Workspaces"
        right={<Badge tone="blue" dot>{workspaces?.length ?? 0} open</Badge>}
      />
      <main className="px-6 py-6">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.7fr_1fr]">
          <div className="space-y-4">
            {workspaces && workspaces.length > 0 ? workspaces.map((w) => (
              <article key={w.id} className="doc overflow-hidden">
                <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr]">
                  <div className="border-b border-auditline p-5 lg:border-b-0 lg:border-r">
                    <Link href={`/workspaces/${w.id}`} className="display text-cardtitle font-semibold text-ink hover:underline">
                      {w.name}
                    </Link>
                    <p className="text-sm text-slate">{w.organisation_name ?? "—"}</p>
                    <div className="mt-4 grid grid-cols-2 gap-3 text-[12.5px] sm:grid-cols-4">
                      <Stat label="Function" value={w.business_function} />
                      <Stat label="Industry" value={w.industry} />
                      <Stat label="Cadence"  value={w.reporting_cadence} />
                      <Stat label="KPI"      value={w.primary_kpi_category} />
                    </div>
                  </div>
                  <div className="bg-blue-steel p-5">
                    <div className="eyebrow eyebrow-slate">Audit posture</div>
                    <div className="mt-3 space-y-2 text-[13px]">
                      <Row label="Active claims"  value={<Badge tone="slate">0</Badge>} />
                      <Row label="Last judgment"  value={<Badge tone="slate">None yet</Badge>} />
                      <Row label="Evidence health" value={<Badge tone="verified" dot>OK</Badge>} />
                    </div>
                    <Link href={`/workspaces/${w.id}`} className="btn-secondary mt-4 w-full justify-center">
                      Open workspace
                    </Link>
                  </div>
                </div>
              </article>
            )) : (
              <div className="doc">
                <EmptyState
                  title="No workspaces yet"
                  body="Workspaces group your analytics environments. Open one to start auditing claims."
                />
              </div>
            )}
          </div>

          <div className="doc h-fit">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">New workspace</div>
              <div className="display text-[15px] font-semibold text-ink">Open workspace</div>
            </div>
            <div className="p-5"><CreateWorkspaceForm /></div>
          </div>
        </div>
      </main>
    </>
  );
}

function Stat({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className="mt-0.5 text-ink">{value ?? "—"}</div>
    </div>
  );
}
function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-slate">{label}</span>
      {value}
    </div>
  );
}
