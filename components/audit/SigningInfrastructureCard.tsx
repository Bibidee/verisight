import { Badge } from "./Badge";
import { HashText } from "./HashText";

export function SigningInfrastructureCard({
  address, createdAt,
}: { address: string; createdAt?: string | null }) {
  return (
    <div className="doc overflow-hidden">
      <div className="doc-header">
        <div>
          <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
            Signing infrastructure
          </div>
          <div className="display text-[16px] font-semibold">Embedded GenLayer signer</div>
        </div>
        <Badge tone="consensus" dot>Background signer</Badge>
      </div>
      <div className="doc-body space-y-3 text-[13px]">
        <div className="border-b border-auditline pb-3">
          <div className="text-[10.5px] uppercase tracking-[0.14em] text-slate mb-1">Wallet address</div>
          <div className="mono text-[13px] text-ink break-all select-all">{address}</div>
        </div>
        <Row label="Created" value={createdAt ? new Date(createdAt).toLocaleString() : "—"} />
        <Row label="Recovery key" value={<Badge tone="verified" dot>Active</Badge>} />
        <Row label="External wallet" value={<Badge tone="slate">Not required</Badge>} />
        <p className="text-[12px] text-slate">
          Your embedded wallet is linked to your VeriSight profile and is used to sign GenLayer
          audit actions in the background. You do not need MetaMask, Rabby, Rainbow, Zerion, or
          any external wallet for normal use.
        </p>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b border-auditline pb-2 last:border-b-0">
      <span className="text-slate">{label}</span>
      <span className="text-ink">{value}</span>
    </div>
  );
}
