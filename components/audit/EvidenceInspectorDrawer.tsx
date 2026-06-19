import { ReactNode } from "react";

export function EvidenceInspectorDrawer({
  title = "Evidence inspector",
  eyebrow = "Inspector",
  children,
}: { title?: string; eyebrow?: string; children?: ReactNode }) {
  return (
    <aside className="hidden h-fit shrink-0 lg:block lg:w-[320px]">
      <div className="sticky top-[88px] rounded-panel border border-glass-grid bg-graphite-blue text-ledger-white">
        <div className="border-b border-glass-grid px-5 py-3">
          <div className="eyebrow">{eyebrow}</div>
          <div className="display mt-0.5 text-cardtitle font-semibold">{title}</div>
        </div>
        <div className="space-y-3 px-5 py-4">{children}</div>
      </div>
    </aside>
  );
}

export function InspectorRow({ left, right }: { left: string; right: ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-glass-grid pb-2 text-[12.5px] last:border-b-0">
      <span className="text-ledger-white/65">{left}</span>
      <span className="text-ledger-white">{right}</span>
    </div>
  );
}
