import Link from "next/link";
import { LogoMark } from "@/components/app/LogoMark";
import { Badge } from "@/components/audit/Badge";
import { SourceOfTruthBadge } from "@/components/audit/SourceOfTruthBadge";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[1.05fr_1fr]">
      <div className="relative hidden overflow-hidden bg-audit-black text-ledger-white lg:flex">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage:
              "radial-gradient(120% 80% at 20% 0%, rgba(124,58,237,0.18), transparent), radial-gradient(80% 60% at 80% 100%, rgba(6,182,212,0.12), transparent)",
          }}
        />
        <div className="relative z-10 flex w-full flex-col justify-between p-12">
          <Link href="/" className="flex items-center gap-2.5">
            <LogoMark size={30} />
            <div className="leading-tight">
              <div className="display text-[15px] font-semibold">VeriSight</div>
              <div className="mono text-[10px] uppercase tracking-[0.22em] text-consensus">
                Analytics Assurance Desk
              </div>
            </div>
          </Link>

          <div className="max-w-md space-y-5">
            <div className="flex flex-wrap gap-2">
              <SourceOfTruthBadge />
              <Badge tone="cyan" dot>Live · StudioNet</Badge>
            </div>
            <h1 className="display text-[36px] font-semibold leading-tight">
              The trust layer for business analytics.
            </h1>
            <p className="text-[14.5px] leading-relaxed text-ledger-white/70">
              VeriSight verifies whether dashboard insights and AI-generated report narratives
              are supported by the underlying data. Final judgments are produced by GenLayer
              validator consensus, not by VeriSight alone.
            </p>
            <div className="rounded-panel border border-glass-grid bg-white/[0.04] p-4 text-[12.5px] text-ledger-white/70">
              Your VeriSight profile includes a secure embedded wallet used only for GenLayer
              audit actions. You do not need a browser wallet for normal use.
            </div>
          </div>

          <div className="mono text-[11px] uppercase tracking-[0.18em] text-ledger-white/40">
            Email · Embedded wallet · Consensus judgment
          </div>
        </div>
      </div>

      <div className="flex items-center justify-center bg-frost-grey px-6 py-12">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  );
}
