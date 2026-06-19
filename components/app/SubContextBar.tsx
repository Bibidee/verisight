import { ReactNode } from "react";

export function SubContextBar({
  title,
  eyebrow,
  workspaceName,
  right,
}: {
  title: string;
  eyebrow?: string;
  workspaceName?: string | null;
  right?: ReactNode;
}) {
  return (
    <div className="border-b border-auditline bg-white-ledger">
      <div className="mx-auto flex max-w-[1400px] flex-wrap items-end justify-between gap-3 px-6 py-4">
        <div className="min-w-0">
          {eyebrow ? <div className="eyebrow eyebrow-slate">{eyebrow}</div> : null}
          <h1 className="display mt-0.5 truncate text-[28px] font-semibold text-ink">
            {title}
          </h1>
          {workspaceName ? (
            <div className="mt-1 flex items-center gap-2 text-[12.5px] text-slate">
              <span className="dot dot-cyan" />
              <span>Workspace</span>
              <span className="mono text-ink">{workspaceName}</span>
            </div>
          ) : null}
        </div>
        {right ? <div className="flex flex-wrap gap-2">{right}</div> : null}
      </div>
    </div>
  );
}
