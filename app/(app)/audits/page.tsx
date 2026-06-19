import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { EmptyState } from "@/components/audit/EmptyState";
import { ClaimDocketTable, DocketRow } from "@/components/audit/ClaimDocketTable";
import { Badge } from "@/components/audit/Badge";

export default async function ClaimDocketPage() {
  const { supabase } = await requireUser();
  const { data: audits } = await supabase
    .from("insight_audit_cases")
    .select("id,insight_claim,status,created_at,metric_name,workspace_id,workspaces(name)")
    .order("created_at", { ascending: false });

  const rows: DocketRow[] = (audits ?? []).map((a) => ({
    id: a.id,
    claim: a.insight_claim,
    workspace: ((a.workspaces as unknown) as { name: string } | null)?.name ?? null,
    metric: a.metric_name,
    status: a.status,
    created_at: a.created_at,
  }));

  return (
    <>
      <SubContextBar
        eyebrow="Audit ledger"
        title="Claim Docket"
        right={
          <>
            <Badge tone="blue" dot>{rows.length} registered</Badge>
            <Link href="/audits/new" className="btn-consensus">
              <span className="dot bg-white" /> Open claim review
            </Link>
          </>
        }
      />
      <main className="px-6 py-6">
        <article className="doc overflow-hidden">
          <div className="border-b border-auditline px-5 py-3">
            <div className="eyebrow eyebrow-slate">Register of analytics claims</div>
            <div className="display text-[15px] font-semibold text-ink">All claims under review</div>
          </div>
          {rows.length > 0 ? (
            <ClaimDocketTable rows={rows} />
          ) : (
            <EmptyState
              title="No insights have been audited yet"
              body="Open a claim review to submit a dashboard claim, attach evidence, and request a GenLayer judgment."
              action={<Link href="/audits/new" className="btn-consensus">Open claim review</Link>}
            />
          )}
        </article>
      </main>
    </>
  );
}
