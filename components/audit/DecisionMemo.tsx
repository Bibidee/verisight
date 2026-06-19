import Link from "next/link";
import { Badge } from "./Badge";
import { HashText } from "./HashText";

export function DecisionMemo({
  auditId,
  claim,
  verdict,
  supportLevel,
  businessRisk,
  recommendedAction,
  evidenceSummary,
  contractAddress,
  transactionHash,
}: {
  auditId: string;
  claim: string;
  verdict: string;
  supportLevel: string;
  businessRisk: string;
  recommendedAction: string;
  evidenceSummary: string;
  contractAddress: string;
  transactionHash: string;
}) {
  return (
    <article className="doc overflow-hidden">
      <header className="doc-header">
        <div>
          <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
            Decision memo
          </div>
          <div className="display text-[18px] font-semibold">{claim}</div>
        </div>
        <Badge tone="consensus" dot>Memo · audit {auditId.slice(0, 6)}</Badge>
      </header>
      <div className="doc-body space-y-5">
        <Section label="Final GenLayer judgment">
          <div className="display text-[18px] font-semibold text-ink">{verdict}</div>
          <div className="text-[13px] text-slate">Support level · {supportLevel}</div>
        </Section>
        <Section label="Evidence summary"><p className="text-[13.5px] text-ink">{evidenceSummary}</p></Section>
        <Section label="Business risk"><p className="text-[13.5px] text-ink">{businessRisk}</p></Section>
        <Section label="Recommended action"><p className="text-[13.5px] text-ink">{recommendedAction}</p></Section>
      </div>
      <footer className="doc-footer">
        <div className="flex items-center gap-2 text-[12px] text-slate">
          <span>Contract</span><HashText value={contractAddress} short />
          <span>· tx</span><HashText value={transactionHash} short />
        </div>
        <Link href={`/audits/${auditId}`} className="btn-secondary">Open judgment</Link>
      </footer>
    </article>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mono text-[10.5px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className="mt-1">{children}</div>
    </div>
  );
}
