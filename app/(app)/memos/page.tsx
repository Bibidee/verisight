import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { DecisionMemo } from "@/components/audit/DecisionMemo";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";

export default async function DecisionMemosPage() {
  const { supabase } = await requireUser();
  const { data: verdicts } = await supabase
    .from("genlayer_audit_verdicts")
    .select("id,audit_case_id,verdict,support_level,business_risk,contract_address,transaction_hash,reasoning_summary,created_at,insight_audit_cases(insight_claim)")
    .order("created_at", { ascending: false });

  type Row = NonNullable<typeof verdicts>[number] & { insight_audit_cases?: { insight_claim: string } | null };
  const rows = (verdicts ?? []) as Row[];

  return (
    <>
      <SubContextBar
        eyebrow="Executive-ready summaries"
        title="Decision Memos"
        right={<Badge tone="blue" dot>{rows.length} memos</Badge>}
      />
      <main className="px-6 py-6 space-y-4">
        {rows.length > 0 ? rows.map((v) => (
          <DecisionMemo
            key={v.id}
            auditId={v.audit_case_id}
            claim={v.insight_audit_cases?.insight_claim ?? "Claim under review"}
            verdict={v.verdict ?? "Pending"}
            supportLevel={v.support_level ?? "—"}
            businessRisk={v.business_risk ?? "—"}
            recommendedAction="Treat the claim as directional only until controlled comparisons are introduced."
            evidenceSummary={v.reasoning_summary ?? "Validators reviewed the metric definition, dataset snapshot, and report context."}
            contractAddress={v.contract_address}
            transactionHash={v.transaction_hash}
          />
        )) : (
          <div className="doc">
            <EmptyState
              title="No decision memos yet"
              body="Once a GenLayer judgment is issued, VeriSight converts it into an executive-ready memo you can share with the boardroom."
            />
          </div>
        )}
      </main>
    </>
  );
}
