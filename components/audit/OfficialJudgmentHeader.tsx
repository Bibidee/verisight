import { JudgmentStamp } from "./JudgmentStamp";
import { SourceOfTruthBadge } from "./SourceOfTruthBadge";

export function OfficialJudgmentHeader({
  auditId,
  verdict = "Partially supported",
  supportLevel = "Moderate",
  confidence = "Moderate",
  businessRisk = "Claim may overstate causality",
}: {
  auditId: string;
  verdict?: string;
  supportLevel?: string;
  confidence?: string;
  businessRisk?: string;
}) {
  return (
    <div className="doc overflow-hidden">
      <div className="doc-header">
        <div className="flex items-center gap-3">
          <div>
            <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
              Official Audit Judgment
            </div>
            <div className="display text-[22px] font-semibold leading-tight">
              Audit · <span className="mono text-[18px]">{auditId.slice(0, 10)}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <SourceOfTruthBadge small />
          <JudgmentStamp />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-px bg-auditline lg:grid-cols-4">
        <HeaderCell label="Verdict"        value={verdict} accent />
        <HeaderCell label="Support level"  value={supportLevel} />
        <HeaderCell label="Confidence"     value={confidence} />
        <HeaderCell label="Business risk"  value={businessRisk} />
      </div>
    </div>
  );
}

function HeaderCell({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="bg-white-ledger px-5 py-4">
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className={accent ? "display mt-1 text-[18px] font-semibold text-consensus" : "display mt-1 text-[18px] font-semibold text-ink"}>
        {value}
      </div>
    </div>
  );
}
