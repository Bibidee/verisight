"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { logoutAction } from "@/lib/auth/actions";
import { LogoMark } from "./LogoMark";

const PRIMARY = [
  { href: "/dashboard",  label: "Assurance Desk" },
  { href: "/audits",     label: "Claim Docket" },
  { href: "/evidence",   label: "Evidence Ledger" },
  { href: "/trace",      label: "Metric Trace" },
  { href: "/verdicts",   label: "GenLayer Judgments" },
  { href: "/memos",      label: "Decision Memos" },
  { href: "/workspaces", label: "Workspaces" },
];
const SECONDARY_BASE = [
  { href: "/profile",  label: "Profile" },
  { href: "/settings", label: "Settings" },
];

function isActive(path: string, href: string) {
  return path === href || path.startsWith(href + "/");
}

export function ExecutiveTopNav({
  email,
  displayName,
  isAdmin,
}: {
  email: string;
  displayName?: string | null;
  isAdmin?: boolean;
}) {
  const path = usePathname();
  const SECONDARY = isAdmin
    ? [{ href: "/admin", label: "Admin" }, ...SECONDARY_BASE]
    : SECONDARY_BASE;
  return (
    <header className="sticky top-0 z-30 border-b border-auditline bg-audit-black text-ledger-white">
      <div className="mx-auto flex max-w-[1400px] items-center justify-between gap-6 px-6 py-3">
        <Link href="/dashboard" className="flex items-center gap-2.5">
          <LogoMark size={28} />
          <div className="leading-tight">
            <div className="display text-[15px] font-semibold">VeriSight</div>
            <div className="mono text-[9.5px] uppercase tracking-[0.22em] text-consensus">
              Analytics Assurance Desk
            </div>
          </div>
        </Link>

        <nav className="hidden flex-1 items-center gap-1 lg:flex">
          {PRIMARY.map((l) => {
            const active = isActive(path, l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                className={clsx(
                  "relative rounded-md px-3 py-1.5 text-[12.5px] font-medium transition-colors",
                  active
                    ? "bg-white/10 text-ledger-white"
                    : "text-ledger-white/70 hover:bg-white/[0.06] hover:text-ledger-white",
                )}
              >
                {l.label}
                {active ? (
                  <span className="absolute inset-x-3 -bottom-[7px] h-[2px] rounded bg-consensus" />
                ) : null}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <Link href="/audits/new" className="btn-consensus">
            <span className="dot bg-white" />
            Audit an insight
          </Link>

          {/* account capsule */}
          <div className="hidden items-center gap-2 rounded-md border border-glass-grid bg-white/[0.04] px-2 py-1.5 md:flex">
            <div className="grid h-6 w-6 place-items-center rounded-full bg-exec-blue text-[10px] font-semibold">
              {(displayName ?? email).slice(0, 1).toUpperCase()}
            </div>
            <div className="leading-tight">
              <div className="text-[11.5px] font-medium">{displayName ?? email.split("@")[0]}</div>
              <div className="mono text-[9.5px] uppercase tracking-[0.16em] text-ledger-white/55">
                {SECONDARY.find((s) => isActive(path, s.href))?.label ?? "User"}
              </div>
            </div>
          </div>

          <form action={logoutAction}>
            <button type="submit" className="btn-secondary bg-white/[0.04] text-ledger-white border-glass-grid hover:bg-white/[0.08]">
              Sign out
            </button>
          </form>
        </div>
      </div>

      {/* secondary strip */}
      <div className="border-t border-glass-grid bg-graphite-blue">
        <div className="mx-auto flex max-w-[1400px] items-center justify-between gap-6 px-6 py-1.5">
          <div className="flex items-center gap-3 text-[11px] text-ledger-white/70">
            <span className="mono uppercase tracking-[0.16em] text-ledger-white/55">Quick</span>
            {SECONDARY.map((s) => (
              <Link
                key={s.href}
                href={s.href}
                className={clsx(
                  "rounded px-2 py-0.5 transition-colors",
                  isActive(path, s.href)
                    ? "bg-white/10 text-ledger-white"
                    : "hover:bg-white/[0.06] hover:text-ledger-white",
                )}
              >
                {s.label}
              </Link>
            ))}
          </div>
          <div className="flex items-center gap-3 text-[11px]">
            <span className="flex items-center gap-1.5 text-ledger-white/70">
              <span className="dot dot-cyan" />
              Datasets fresh
            </span>
            <span className="flex items-center gap-1.5 text-ledger-white/70">
              <span className="dot dot-consensus" />
              GenLayer · StudioNet
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
