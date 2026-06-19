import { ReactNode } from "react";

export function Field({
  label,
  hint,
  children,
}: { label: string; hint?: string; children: ReactNode }) {
  return (
    <div className="space-y-1.5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.08em] text-slate">{label}</div>
      {children}
      {hint ? <div className="text-[12px] text-slate">{hint}</div> : null}
    </div>
  );
}
