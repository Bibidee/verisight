import { ReactNode } from "react";

export function EmptyState({
  title, body, action,
}: { title: string; body: string; action?: ReactNode }) {
  return (
    <div className="px-6 py-12 text-center">
      <div className="mono mx-auto inline-flex items-center gap-2 rounded border border-auditline bg-frost-grey px-3 py-1 text-[10.5px] uppercase tracking-[0.16em] text-slate">
        <span className="dot dot-slate" /> Empty record
      </div>
      <div className="display mx-auto mt-4 max-w-md text-[18px] font-semibold text-ink">{title}</div>
      <p className="mx-auto mt-2 max-w-md text-[13px] text-slate">{body}</p>
      {action ? <div className="mt-4 inline-flex">{action}</div> : null}
    </div>
  );
}
