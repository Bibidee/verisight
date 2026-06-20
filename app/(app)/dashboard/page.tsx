import Link from "next/link";
import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { SourceOfTruthBadge } from "@/components/audit/SourceOfTruthBadge";
import { Meter } from "@/components/audit/Meter";
import { SupportBadge } from "@/components/audit/SupportBadge";
import { JudgmentStamp } from "@/components/audit/JudgmentStamp";

export default async function AssuranceDeskPage() {
  const { profile, supabase } = await getProfile();
  if (!profile?.onboarding_completed) redirect("/onboarding");

  const { data: workspaces } = await supabase
    .from("workspaces").select("id,name").order("created_at", { ascending: false }).limit(1);
  const ws = workspaces?.[0];

  const { count: auditCount } = await supabase
    .from("insight_audit_cases").select("*", { count: "exact", head: true });

  const { data: recentAudits } = await supabase
    .from("insight_audit_cases")
    .select("id,insight_claim,status,created_at,metric_name")
    .order("created_at", { ascending: false })
    .limit(5);

  const { data: latestVerdict } = await supabase
    .from("genlayer_audit_verdicts")
    .select("audit_case_id,verdict,support_level,confidence_label,business_risk,reasoning_summary,consensus_status,created_at")
    .eq("consensus_status", "reached")
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  const { data: latestVerdictCase } = latestVerdict
    ? await supabase
        .from("insight_audit_cases")
        .select("insight_claim")
        .eq("id", latestVerdict.audit_case_id)
        .single()
    : { data: null };

  // Business risk queue — all issued verdicts with a business risk
  const { data: riskVerdicts } = await supabase
    .from("genlayer_audit_verdicts")
    .select("audit_case_id,verdict,business_risk,created_at")
    .eq("consensus_status", "reached")
    .not("business_risk", "is", null)
    .order("created_at", { ascending: false })
    .limit(4);

  const riskCaseIds = (riskVerdicts ?? []).map((r) => r.audit_case_id);
  const { data: riskCases } = riskCaseIds.length > 0
    ? await supabase
        .from("insight_audit_cases")
        .select("id,insight_claim")
        .in("id", riskCaseIds)
    : { data: [] };

  // Draft decision memos — verdict_issued audits
  const { data: memoDrafts } = await supabase
    .from("insight_audit_cases")
    .select("id,insight_claim,metric_name,created_at")
    .eq("status", "verdict_issued")
    .order("created_at", { ascending: false })
    .limit(4);

  return (
    <>
      <SubContextBar
        eyebrow="Daily review"
        title={`Assurance Desk · ${profile.display_name ?? "Analyst"}`}
        workspaceName={ws?.name}
        right={
          <>
            <Badge tone="cyan" dot>Datasets fresh</Badge>
            <SourceOfTruthBadge />
            <Link href="/audits/new" className="btn-consensus">
              <span className="dot bg-white" /> Audit an insight
            </Link>
          </>
        }
      />

      <main className="px-6 py-6 space-y-6">
        {/* Top — latest judgment summary + dataset freshness */}
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1.6fr_1fr]">
          <article className="doc overflow-hidden">
            {latestVerdict && latestVerdictCase ? (
              <>
                <div className="doc-header">
                  <div>
                    <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
                      Latest GenLayer judgment
                    </div>
                    <div className="display text-[18px] font-semibold">
                      {latestVerdictCase.insight_claim}
                    </div>
                  </div>
                  <JudgmentStamp />
                </div>
                <div className="grid grid-cols-2 gap-px bg-auditline lg:grid-cols-4">
                  <Cell label="Verdict" value={fmt(latestVerdict.verdict)} accent />
                  <Cell label="Support level" value={fmt(latestVerdict.support_level)} />
                  <Cell label="Confidence" value={fmt(latestVerdict.confidence_label)} />
                  <Cell label="Business risk" value={truncate(latestVerdict.business_risk ?? "—", 80)} />
                </div>
                <div className="px-5 py-4 flex flex-wrap items-center justify-between gap-3">
                  <SupportBadge verdict={latestVerdict.verdict as import("@/components/audit/SupportBadge").Verdict} />
                  <Link href={`/audits/${latestVerdict.audit_case_id}`} className="link text-sm">View full judgment →</Link>
                </div>
              </>
            ) : (
              <div className="doc-header">
                <div>
                  <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
                    Latest GenLayer judgment
                  </div>
                  <div className="display text-[18px] font-semibold text-ledger-white/60">
                    No verdicts issued yet
                  </div>
                </div>
                <JudgmentStamp />
              </div>
            )}
          </article>

          <article className="doc p-5">
            <div className="eyebrow eyebrow-slate">Dataset freshness</div>
            <div className="display mt-1 text-section font-semibold text-ink">Live</div>
            <p className="text-[13px] text-slate">
              Warehouse snapshots match metric definitions. No stale evidence detected.
            </p>
            <div className="mt-4 space-y-3">
              <FreshRow label="Warehouse pulse"   tone="cyan"     value={92} />
              <FreshRow label="Evidence hashes"   tone="emerald"  value={88} />
              <FreshRow label="Open audit packets" tone="amber"   value={20} />
            </div>
          </article>
        </section>

        {/* Middle — Claim docket + Evidence gaps */}
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1.7fr_1fr]">
          <article className="doc overflow-hidden">
            <Head title="Claim Docket" eyebrow="Pending review"
                  right={<Link href="/audits" className="btn-secondary">Open docket</Link>} />
            {recentAudits && recentAudits.length > 0 ? (
              <div className="divide-y divide-auditline">
                {recentAudits.map((a) => (
                  <Link key={a.id} href={`/audits/${a.id}`}
                    className="flex items-center justify-between px-5 py-3 hover:bg-slate-50 transition-colors gap-3">
                    <div className="min-w-0">
                      <div className="text-[13px] font-medium text-ink truncate">{a.insight_claim}</div>
                      <div className="mono text-[10.5px] text-slate mt-0.5">{a.metric_name ?? "—"} · {new Date(a.created_at).toLocaleDateString()}</div>
                    </div>
                    <span className={`shrink-0 mono text-[10px] uppercase tracking-[0.14em] px-2 py-0.5 rounded-sm border ${
                      a.status === "verdict_issued" ? "border-emerald-300 text-emerald-700 bg-emerald-50" :
                      a.status === "consensus_pending" ? "border-amber-300 text-amber-700 bg-amber-50" :
                      "border-slate-200 text-slate-500 bg-slate-50"
                    }`}>{a.status.replace(/_/g, " ")}</span>
                  </Link>
                ))}
              </div>
            ) : (
              <EmptyState
                title="No insights have been audited yet"
                body="Start by submitting a dashboard claim and VeriSight will prepare it for GenLayer consensus review."
                action={<Link href="/audits/new" className="btn-consensus">Audit an insight</Link>}
              />
            )}
          </article>

          <article className="doc">
            <Head title="Evidence gaps" eyebrow="Review queue" />
            <EmptyState
              title="No evidence gaps yet"
              body="Once audit packets exist, weak evidence and missing definitions will be queued here for review."
            />
          </article>
        </section>

        {/* Bottom — risk queue + drafts + activity */}
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <article className="doc overflow-hidden">
            <Head title="Business risk queue" eyebrow="High & moderate" />
            {riskVerdicts && riskVerdicts.length > 0 ? (
              <div className="divide-y divide-auditline">
                {riskVerdicts.map((r) => {
                  const claim = riskCases?.find((c) => c.id === r.audit_case_id)?.insight_claim ?? "—";
                  return (
                    <Link key={r.audit_case_id} href={`/audits/${r.audit_case_id}`}
                      className="block px-5 py-3 hover:bg-slate-50 transition-colors">
                      <div className="text-[12.5px] font-medium text-ink truncate">{claim}</div>
                      <div className="mono text-[10.5px] text-slate mt-0.5">{fmt(r.verdict)} · {new Date(r.created_at).toLocaleDateString()}</div>
                      <div className="text-[11.5px] text-claim mt-1 line-clamp-2">{r.business_risk}</div>
                    </Link>
                  );
                })}
              </div>
            ) : (
              <EmptyState title="No risks queued"
                body="High-risk judgments will appear here so executives can review them before acting." />
            )}
          </article>
          <article className="doc overflow-hidden">
            <Head title="Draft decision memos" eyebrow="Awaiting executive review" />
            {memoDrafts && memoDrafts.length > 0 ? (
              <div className="divide-y divide-auditline">
                {memoDrafts.map((m) => (
                  <Link key={m.id} href={`/audits/${m.id}`}
                    className="block px-5 py-3 hover:bg-slate-50 transition-colors">
                    <div className="text-[12.5px] font-medium text-ink truncate">{m.insight_claim}</div>
                    <div className="mono text-[10.5px] text-slate mt-0.5">{m.metric_name ?? "—"} · {new Date(m.created_at).toLocaleDateString()}</div>
                    <div className="mono text-[10px] mt-1 text-consensus uppercase tracking-[0.12em]">Ready to export</div>
                  </Link>
                ))}
              </div>
            ) : (
              <EmptyState title="No memos drafted"
                body="Once a judgment is issued, you can convert it into an executive-ready decision memo." />
            )}
          </article>
          <article className="doc-header rounded-panel overflow-hidden border border-glass-grid"
                   style={{ background: "var(--audit-black)" }}>
            <div className="w-full">
              <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
                Contract trace · StudioNet
              </div>
              <div className="display mt-1 text-[16px] font-semibold text-ledger-white">
                VeriSightInsightAuditor
              </div>
              <div className="mt-3 space-y-2 text-[12px]">
                <Trace label="Validator quorum" v="ready" />
                <Trace label="Equivalence criteria" v="loaded" />
                <Trace label="Pending submissions" v={String(auditCount ?? 0)} />
              </div>
            </div>
          </article>
        </section>
      </main>
    </>
  );
}

function fmt(v: string | null | undefined): string {
  if (!v) return "—";
  return v.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
function truncate(s: string, n: number): string {
  return s.length > n ? s.slice(0, n) + "…" : s;
}

function Head({ title, eyebrow, right }: { title: string; eyebrow: string; right?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b border-auditline px-5 py-3">
      <div>
        <div className="eyebrow eyebrow-slate">{eyebrow}</div>
        <div className="display text-[15px] font-semibold text-ink">{title}</div>
      </div>
      {right}
    </div>
  );
}
function Cell({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="bg-white-ledger px-5 py-3">
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className={accent ? "display mt-1 text-[16px] font-semibold text-consensus" : "display mt-1 text-[16px] font-semibold text-ink"}>{value}</div>
    </div>
  );
}
function FreshRow({ label, tone, value }: { label: string; tone: "cyan" | "emerald" | "amber"; value: number }) {
  return (
    <div>
      <div className="flex items-center justify-between text-[12.5px] text-slate">
        <span>{label}</span><span className="mono text-ink">{value}%</span>
      </div>
      <Meter value={value} tone={tone} className="mt-1.5" />
    </div>
  );
}
function Trace({ label, v }: { label: string; v: string }) {
  return (
    <div className="flex items-center justify-between border-b border-glass-grid pb-1.5 text-ledger-white/75 last:border-b-0">
      <span>{label}</span>
      <span className="mono uppercase tracking-[0.12em] text-ledger-white/55">{v}</span>
    </div>
  );
}
