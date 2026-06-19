import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { OfficialJudgmentHeader } from "@/components/audit/OfficialJudgmentHeader";
import { AssumptionReviewPanel } from "@/components/audit/AssumptionReviewPanel";
import { ConsensusBadge } from "@/components/audit/ConsensusBadge";
import { SupportBadge, Verdict } from "@/components/audit/SupportBadge";
import { Badge } from "@/components/audit/Badge";
import {
  EvidenceInspectorDrawer,
  InspectorRow,
} from "@/components/audit/EvidenceInspectorDrawer";
import { HashText } from "@/components/audit/HashText";
import { PollVerdictButton } from "./PollVerdictButton";
import { ContinueDraftPanel } from "./ContinueDraftPanel";

export default async function FullJudgmentRecordPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const { supabase } = await requireUser();

  const { data: audit } = await supabase
    .from("insight_audit_cases").select("*").eq("id", id).single();
  if (!audit) notFound();

  const { data: verdict } = await supabase
    .from("genlayer_audit_verdicts")
    .select("*")
    .eq("audit_case_id", id)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  const { data: evidence } = await supabase
    .from("evidence_files")
    .select("id,file_type,file_size,evidence_hash,created_at")
    .eq("audit_case_id", id)
    .order("created_at", { ascending: false });

  const hasVerdict = !!verdict?.verdict;
  const v: Verdict = (verdict?.verdict ?? "needs_more_evidence") as Verdict;
  const isDraft = audit.status === "draft" || audit.status === "evidence_added";
  const isPending = audit.status === "consensus_pending" || audit.status === "submitted";

  // Parse unsupported_assumptions from Supabase (stored as jsonb)
  let assumptions: string[] = [];
  if (hasVerdict && verdict?.unsupported_assumptions) {
    const raw = verdict.unsupported_assumptions;
    if (Array.isArray(raw)) {
      assumptions = raw.map(String);
    } else if (typeof raw === "string") {
      try {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) assumptions = parsed.map(String);
      } catch { /* ignore */ }
    }
  }

  return (
    <>
      <SubContextBar
        eyebrow="Full judgment record"
        title="Official Audit Judgment"
        right={
          <>
            {isDraft
              ? <Badge tone="amber" dot>{audit.status.replace(/_/g, " ")}</Badge>
              : hasVerdict
                ? <SupportBadge verdict={v} />
                : <Badge tone="amber" dot>Awaiting judgment</Badge>}
            {!isDraft && <ConsensusBadge state={hasVerdict ? "reached" : "pending"} />}
          </>
        }
      />
      <main className="px-6 py-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
        <div className="space-y-6">

          {/* Draft banner */}
          {isDraft && (
            <article className="doc overflow-hidden">
              <div className="border-b border-auditline px-5 py-3 flex items-center justify-between">
                <div>
                  <div className="eyebrow eyebrow-slate">Draft in progress</div>
                  <div className="display text-[15px] font-semibold text-ink">Continue editing this audit</div>
                </div>
                <Badge tone="amber" dot>
                  {audit.status.replace(/_/g, " ")}
                </Badge>
              </div>
              <div className="px-5 py-4">
                <p className="text-[13px] text-slate mb-2">
                  Claim: <span className="text-ink font-medium">{audit.insight_claim}</span>
                </p>
                <p className="text-[12px] text-slate">
                  Metric: {audit.metric_name ?? "—"} · Period: {audit.time_period ?? "—"}
                </p>
              </div>
            </article>
          )}

          {isDraft ? (
            <ContinueDraftPanel
              auditId={audit.id}
              existingEvidenceCount={evidence?.length ?? 0}
              initialFields={{
                metric_name: audit.metric_name ?? null,
                metric_definition: audit.metric_definition ?? null,
                time_period: audit.time_period ?? null,
                dataset_summary: audit.dataset_summary ?? null,
                candidate_interpretation_a: audit.candidate_interpretation_a ?? null,
                candidate_interpretation_b: audit.candidate_interpretation_b ?? null,
                candidate_interpretation_c: audit.candidate_interpretation_c ?? null,
                segment_context: audit.segment_context ?? null,
              }}
            />
          ) : (<>
          <OfficialJudgmentHeader
            auditId={audit.id}
            verdict={hasVerdict ? verdict.verdict : isPending ? "Awaiting GenLayer" : "—"}
            supportLevel={hasVerdict ? verdict.support_level ?? "—" : "—"}
            confidence={hasVerdict ? verdict.confidence_label ?? "—" : "—"}
            businessRisk={hasVerdict ? verdict.business_risk ?? "—" : "—"}
          />

          {/* Claim + context details */}
          <article className="doc">
            <div className="grid grid-cols-1 divide-y divide-auditline lg:grid-cols-2 lg:divide-x lg:divide-y-0">
              <Section label="Claim under review" body={audit.insight_claim} />
              <Section label="Business question" body={audit.business_question ?? "—"} />
            </div>
            <div className="grid grid-cols-1 divide-y divide-auditline lg:grid-cols-3 lg:divide-x lg:divide-y-0">
              <Section label="Metric basis" body={audit.metric_name ?? "—"} sub={audit.metric_definition ?? undefined} />
              <Section label="Time period" body={audit.time_period ?? "—"} />
              <Section label="Segment / filter" body={audit.segment_context ?? "—"} />
            </div>
            <div className="grid grid-cols-1 divide-y divide-auditline lg:grid-cols-2 lg:divide-x lg:divide-y-0">
              <Section label="Dataset summary" body={audit.dataset_summary ?? "—"} />
              <Section label="Report context" body={audit.report_context ?? "—"} />
            </div>
            <div className="grid grid-cols-1 divide-y divide-auditline lg:grid-cols-3 lg:divide-x lg:divide-y-0">
              <Section label="Interpretation A" body={audit.candidate_interpretation_a ?? "—"} />
              <Section label="Interpretation B" body={audit.candidate_interpretation_b ?? "—"} />
              <Section label="Interpretation C" body={audit.candidate_interpretation_c ?? "—"} />
            </div>
          </article>

          {/* Validator reasoning — from contract, not hardcoded */}
          {hasVerdict && (
            <article className="doc">
              <div className="border-b border-auditline px-5 py-3">
                <div className="eyebrow eyebrow-slate">Consensus-backed audit verdict</div>
                <div className="display text-[15px] font-semibold text-ink">GenLayer validator reasoning</div>
              </div>
              <div className="px-5 py-4 space-y-4">
                <VerdictField label="Verdict" value={verdict.verdict} />
                <VerdictField label="Support level" value={verdict.support_level ?? "—"} />
                <VerdictField label="Confidence" value={verdict.confidence_label ?? "—"} />
                <VerdictField label="Selected interpretation" value={verdict.selected_interpretation ?? "—"} />
                <div>
                  <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">Reasoning summary</div>
                  <div className="mt-1 text-[14px] text-ink leading-relaxed">{verdict.reasoning_summary ?? "—"}</div>
                </div>
                <div>
                  <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">Business risk</div>
                  <div className="mt-1 text-[14px] text-ink leading-relaxed">{verdict.business_risk ?? "—"}</div>
                </div>
              </div>
            </article>
          )}

          {/* Evidence ledger */}
          <article className="doc overflow-hidden">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">Evidence reviewed</div>
              <div className="display text-[15px] font-semibold text-ink">
                Attached evidence ({evidence?.length ?? 0})
              </div>
            </div>
            {evidence && evidence.length > 0 ? (
              <table className="ledger-table">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Evidence hash</th>
                    <th>Uploaded</th>
                  </tr>
                </thead>
                <tbody>
                  {evidence.map((e) => (
                    <tr key={e.id}>
                      <td><Badge tone="blue">{e.file_type}</Badge></td>
                      <td className="text-slate">{Math.round((e.file_size ?? 0) / 1024)} KB</td>
                      <td><HashText value={e.evidence_hash ?? "—"} short /></td>
                      <td className="text-slate">{new Date(e.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="px-5 py-8 text-center text-[13px] text-slate">
                No evidence attached.
              </div>
            )}
          </article>

          {/* Unsupported assumptions — from contract return, not hardcoded */}
          <AssumptionReviewPanel
            notes={
              hasVerdict && assumptions.length > 0
                ? assumptions.map((text) => ({ kind: "evidence" as const, text }))
                : undefined
            }
          />

          {/* Sync / poll section — visible when pending OR when verdict exists (re-sync) */}
          {(isPending || hasVerdict) && (
            <div className="doc p-4 flex items-center justify-between gap-4">
              <div>
                <div className="eyebrow eyebrow-slate">
                  {hasVerdict ? "GenLayer sync" : "Awaiting consensus"}
                </div>
                <p className="mt-1 text-[13px] text-slate">
                  {hasVerdict
                    ? "Re-read the contract to refresh the mirrored verdict in Supabase."
                    : "Consensus transaction submitted, but contract return has not been indexed yet. Click to read the result."}
                </p>
              </div>
              <PollVerdictButton auditId={audit.id} />
            </div>
          )}

          {/* Audit trail strip */}
          <div className="audit-strip">
            <span className="mono text-[10.5px] uppercase tracking-[0.16em] text-ledger-white/55">
              Audit trail
            </span>
            <span>Created · {new Date(audit.created_at).toLocaleString()}</span>
            <span className="mx-1 h-3 w-px bg-glass-grid" />
            <span>Status · {audit.status.replace(/_/g, " ")}</span>
            {verdict?.transaction_hash && (
              <>
                <span className="mx-1 h-3 w-px bg-glass-grid" />
                <span>Tx · <HashText dark value={verdict.transaction_hash} short explorerType="tx" /></span>
              </>
            )}
            <Link
              href={`/memos?audit=${audit.id}`}
              className="ml-auto btn-secondary bg-white/[0.04] text-ledger-white border-glass-grid hover:bg-white/[0.08]"
            >
              Export decision memo
            </Link>
          </div>
          </>)}
        </div>

        {/* Inspector sidebar */}
        <EvidenceInspectorDrawer title="GenLayer record">
          <InspectorRow left="Contract"        right={<HashText dark value={verdict?.contract_address ?? "—"} short explorerType="address" />} />
          <InspectorRow left="Transaction"     right={<HashText dark value={verdict?.transaction_hash ?? "—"} short explorerType="tx" />} />
          <InspectorRow left="Audit ID"        right={<HashText dark value={audit.id} short />} />
          <InspectorRow left="Evidence digest" right={<HashText dark value={verdict?.evidence_digest ?? "—"} short />} />
          <InspectorRow left="Consensus"       right={<ConsensusBadge state={hasVerdict ? "reached" : "pending"} />} />
          <InspectorRow left="Evidence files"  right={<span className="mono">{evidence?.length ?? 0}</span>} />
          {hasVerdict && verdict?.selected_interpretation && (
            <InspectorRow left="Interpretation" right={<span className="mono">{verdict.selected_interpretation}</span>} />
          )}
        </EvidenceInspectorDrawer>
      </main>
    </>
  );
}

function Section({ label, body, sub }: { label: string; body: string; sub?: string }) {
  return (
    <div className="px-5 py-4">
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className="mt-1 text-[14px] text-ink">{body}</div>
      {sub ? <div className="mt-1 text-[12.5px] text-slate">{sub}</div> : null}
    </div>
  );
}

function VerdictField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className="mt-1 text-[16px] font-semibold text-consensus">{value}</div>
    </div>
  );
}
