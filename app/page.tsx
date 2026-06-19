import Link from "next/link";
import { LogoMark } from "@/components/app/LogoMark";
import { Badge } from "@/components/audit/Badge";
import { SourceOfTruthBadge } from "@/components/audit/SourceOfTruthBadge";
import { JudgmentStamp } from "@/components/audit/JudgmentStamp";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white-ledger text-ink">
      {/* nav */}
      <header className="border-b border-auditline bg-white-ledger">
        <div className="mx-auto flex max-w-[1280px] items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2.5">
            <LogoMark size={30} />
            <div className="leading-tight">
              <div className="display text-[15px] font-semibold">VeriSight</div>
              <div className="mono text-[9.5px] uppercase tracking-[0.22em] text-consensus">
                Analytics Assurance Desk
              </div>
            </div>
          </Link>
          <nav className="flex items-center gap-2">
            <Link href="/login" className="btn-secondary">Sign in</Link>
            <Link href="/signup" className="btn-primary">Create account</Link>
          </nav>
        </div>
      </header>

      {/* hero */}
      <section className="border-b border-auditline">
        <div className="mx-auto grid max-w-[1280px] grid-cols-1 gap-12 px-6 py-20 lg:grid-cols-[1.05fr_1fr]">
          <div>
            <Badge tone="consensus" dot>Assurance desk · v1</Badge>
            <h1 className="display mt-5 text-[52px] font-semibold leading-[1.04] tracking-[-0.02em] sm:text-hero">
              The assurance desk for <span className="text-consensus">analytics claims.</span>
            </h1>
            <p className="mt-5 max-w-xl text-[15.5px] leading-relaxed text-slate">
              Before a dashboard insight, KPI narrative, or AI-generated report becomes a business
              decision, VeriSight verifies whether the data actually supports it — adjudicated by
              GenLayer validator consensus.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/signup" className="btn-primary">
                <span className="dot bg-white" />
                Audit an insight
              </Link>
              <Link href="/login" className="btn-secondary">View sample judgment</Link>
            </div>
            <div className="mt-10 grid max-w-md grid-cols-3 gap-3">
              <Stat n="01" l="Claim submitted" />
              <Stat n="02" l="Evidence reviewed" />
              <Stat n="03" l="Judgment issued" />
            </div>
          </div>

          {/* boardroom audit memo */}
          <div className="relative">
            <div className="absolute -right-4 -top-4 hidden h-44 w-44 rounded-full bg-consensus/10 blur-2xl lg:block" />
            <div className="absolute -bottom-4 -left-2 hidden h-44 w-44 rounded-full bg-exec-blue/10 blur-2xl lg:block" />

            <div className="relative space-y-3">
              {/* stack — back paper */}
              <div className="ml-8 -mb-3 hidden rounded-panel border border-auditline bg-white-ledger/70 p-3 shadow-doc lg:block">
                <div className="mono text-[10px] uppercase tracking-[0.16em] text-slate">
                  Audit · 2025-Q3-04
                </div>
              </div>

              {/* main memo */}
              <article className="doc overflow-hidden">
                <div className="doc-header">
                  <div>
                    <div className="mono text-[10.5px] uppercase tracking-[0.2em] text-ledger-white/55">
                      Official Audit Judgment · sample
                    </div>
                    <div className="display text-[18px] font-semibold leading-tight">
                      Audit · <span className="mono text-[16px]">2025-Q3-A1F4</span>
                    </div>
                  </div>
                  <SourceOfTruthBadge small />
                </div>
                <div className="grid grid-cols-2 gap-px bg-auditline">
                  <Cell label="Verdict" value="Partially supported" accent />
                  <Cell label="Support level" value="Moderate" />
                  <Cell label="Confidence" value="Moderate" />
                  <Cell label="Business risk" value="Claim may overstate causality" />
                </div>
                <div className="space-y-3 px-5 py-5">
                  <Section label="Claim under review">
                    <p className="text-[14px] text-ink">
                      Revenue growth this quarter was mainly driven by repeat customers.
                    </p>
                  </Section>
                  <Section label="Evidence reviewed">
                    <div className="flex flex-wrap gap-2 text-[12px]">
                      <Badge tone="blue">Dataset · fact_revenue snapshot</Badge>
                      <Badge tone="blue">Report PDF</Badge>
                      <Badge tone="cyan">Metric definition</Badge>
                    </div>
                  </Section>
                  <Section label="Assumption note">
                    <div className="text-[12.5px] text-amber">
                      <span className="font-semibold">Causality risk · </span>
                      New customer revenue, discount effects, and segment mix were not sufficiently
                      controlled.
                    </div>
                  </Section>
                  <div className="flex items-center justify-between border-t border-auditline pt-3">
                    <span className="mono text-[10.5px] uppercase tracking-[0.16em] text-slate">
                      Issued · 2025-10-14 14:02 UTC
                    </span>
                    <JudgmentStamp />
                  </div>
                </div>
              </article>
            </div>
          </div>
        </div>
      </section>

      {/* confident insights still need proof — horizontal table */}
      <section className="border-b border-auditline bg-frost-grey">
        <div className="mx-auto max-w-[1280px] px-6 py-20">
          <Badge tone="amber" dot>Confident insights still need proof</Badge>
          <h2 className="display mt-3 max-w-2xl text-section font-semibold text-ink sm:text-[30px]">
            Confidence is not the same as truth. VeriSight separates one from the other.
          </h2>

          <div className="mt-10 overflow-hidden rounded-panel border border-auditline bg-white-ledger">
            <table className="ledger-table">
              <thead>
                <tr>
                  <th>Dashboard says</th>
                  <th>Evidence shows</th>
                  <th>Business risk</th>
                  <th>GenLayer judgment</th>
                </tr>
              </thead>
              <tbody>
                <CompareRow
                  said="Revenue growth driven by repeat customers"
                  shown="Repeat revenue ↑, but new revenue and discounts not controlled"
                  risk="Over-investing in repeat segment"
                  judgment="partially_supported"
                />
                <CompareRow
                  said="Onboarding completion drop caused churn"
                  shown="No comparison cohort; seasonality unaccounted for"
                  risk="Wrong remediation funded"
                  judgment="needs_more_evidence"
                />
                <CompareRow
                  said="Paid ads now the highest-ROI channel"
                  shown="Attribution window changed mid-quarter"
                  risk="Misallocating budget"
                  judgment="misleading"
                />
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <footer className="bg-audit-black text-ledger-white/70">
        <div className="mx-auto flex max-w-[1280px] items-center justify-between px-6 py-6 text-[12px]">
          <div className="flex items-center gap-2">
            <LogoMark size={20} />
            <span>VeriSight · Analytics Assurance Desk</span>
          </div>
          <div className="mono uppercase tracking-[0.16em]">
            GenLayer is the source of truth for the audit verdict.
          </div>
        </div>
      </footer>
    </main>
  );
}

function Stat({ n, l }: { n: string; l: string }) {
  return (
    <div className="rounded-panel border border-auditline bg-white-ledger p-3">
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{n}</div>
      <div className="mt-1 text-[12.5px] text-ink">{l}</div>
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

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className="mt-1">{children}</div>
    </div>
  );
}

function CompareRow({
  said, shown, risk, judgment,
}: { said: string; shown: string; risk: string; judgment: "partially_supported" | "needs_more_evidence" | "misleading" }) {
  const map = {
    partially_supported: { tone: "amber" as const, label: "Partially supported" },
    needs_more_evidence: { tone: "slate" as const, label: "Needs more evidence" },
    misleading: { tone: "claim" as const, label: "Misleading" },
  };
  const v = map[judgment];
  return (
    <tr>
      <td className="text-ink">{said}</td>
      <td className="text-slate">{shown}</td>
      <td className="text-claim">{risk}</td>
      <td><Badge tone={v.tone} dot>{v.label}</Badge></td>
    </tr>
  );
}
