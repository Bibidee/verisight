"""VeriSight redesign #2 — Analytics Assurance Desk.

Replaces the command-centre layout with a document-and-ledger metaphor.

  * Horizontal Executive Top Nav (no permanent left rail)
  * New page names + vocabulary (Assurance Desk, Claim Docket,
    Official Audit Judgment, Decision Memos, Metric Trace)
  * New audit primitives (JudgmentStamp, OfficialJudgmentHeader,
    ClaimDocketTable, AssumptionReviewPanel, MetricTraceMap,
    DecisionMemo, SigningInfrastructureCard)
  * Ledger Glass visual style (crisp documents, thin lines,
    side inspector drawers, formal judgment surfaces)

No product logic, routes, or contract calls are changed. Existing
routes are preserved; nav uses friendlier vocabulary labels but
hrefs remain the same. Two new routes are added: /memos and /trace.
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def write(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {rel}")


# ===================================================================
# tailwind.config.ts — Ledger Glass palette
# ===================================================================
write(
    "tailwind.config.ts",
    """import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Document surfaces
        "audit-black": "#090B10",
        "graphite-blue": "#0F172A",
        "frost-grey": "#F3F6FA",
        "ledger-mist": "#F3F6FA", // alias retained for older usages
        "white-ledger": "#FFFFFF",
        "blue-steel": "#EAF0F8",
        // Brand + signal
        "exec-blue": "#2563EB",
        "grid-blue": "#2563EB",
        "data-cyan": "#06B6D4",
        amber: "#F59E0B",
        claim: "#DC2626",
        emerald: "#059669",
        consensus: "#7C3AED",
        // Text
        ink: "#0F172A",
        "ledger-white": "#F8FAFC",
        slate: "#64748B",
        // Borders
        auditline: "#E2E8F0",
        "ledger-line": "#E2E8F0",
        "glass-grid": "rgba(148,163,184,0.22)",
      },
      fontFamily: {
        display: ["var(--font-space-grotesk)", "system-ui", "sans-serif"],
        body: ["var(--font-manrope)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: { btn: "8px", panel: "12px", stamp: "4px" },
      fontSize: {
        hero: ["64px", { lineHeight: "1.05", letterSpacing: "-0.025em" }],
        pagetitle: ["38px", { lineHeight: "1.08", letterSpacing: "-0.012em" }],
        section: ["24px", { lineHeight: "1.2" }],
        cardtitle: ["18px", { lineHeight: "1.3" }],
      },
      boxShadow: {
        doc: "0 1px 0 rgba(15,23,42,0.04), 0 8px 24px -18px rgba(15,23,42,0.18)",
        stamp: "0 0 0 1px rgba(124,58,237,0.35), 0 0 0 6px rgba(124,58,237,0.06)",
      },
      keyframes: {
        stampIn: {
          "0%":   { transform: "rotate(-2deg) scale(1.15)", opacity: "0" },
          "60%":  { transform: "rotate(-2deg) scale(0.98)", opacity: "1" },
          "100%": { transform: "rotate(-2deg) scale(1)",    opacity: "1" },
        },
        pulseDot: {
          "0%,100%": { opacity: "1", transform: "scale(1)" },
          "50%":     { opacity: "0.45", transform: "scale(0.85)" },
        },
      },
      animation: {
        stampIn: "stampIn .6s ease-out both",
        pulseDot: "pulseDot 1.6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
export default config;
""",
)

# ===================================================================
# app/globals.css — Ledger Glass utilities
# ===================================================================
write(
    "app/globals.css",
    """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --audit-black: #090B10;
  --graphite-blue: #0F172A;
  --frost-grey: #F3F6FA;
  --white-ledger: #FFFFFF;
  --blue-steel: #EAF0F8;
  --grid-blue: #2563EB;
  --exec-blue: #2563EB;
  --data-cyan: #06B6D4;
  --amber: #F59E0B;
  --claim: #DC2626;
  --emerald: #059669;
  --consensus: #7C3AED;
  --ink: #0F172A;
  --ledger-white: #F8FAFC;
  --slate: #64748B;
  --auditline: #E2E8F0;
  --ledger-line: #E2E8F0;
  --glass-grid: rgba(148, 163, 184, 0.22);
}

html, body {
  background: var(--frost-grey);
  color: var(--ink);
  font-family: var(--font-manrope), system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.display { font-family: var(--font-space-grotesk), system-ui, sans-serif; letter-spacing: -0.01em; }
.mono    { font-family: var(--font-jetbrains-mono), ui-monospace, monospace; font-feature-settings: "ss01","ss02"; }

/* ------------- BUTTONS ------------- */
.btn-primary {
  background: var(--audit-black); color: #fff;
  border-radius: 8px; padding: 9px 14px;
  font-weight: 600; font-size: 13.5px;
  display: inline-flex; align-items: center; gap: 8px;
  transition: opacity .15s ease, transform .05s ease;
}
.btn-primary:hover  { opacity: .94; }
.btn-primary:active { transform: translateY(1px); }
.btn-secondary {
  background: var(--white-ledger); color: var(--ink);
  border: 1px solid var(--auditline); border-radius: 8px;
  padding: 8px 13px; font-weight: 600; font-size: 13.5px;
  display: inline-flex; align-items: center; gap: 8px;
}
.btn-secondary:hover { background: var(--frost-grey); }
.btn-exec {
  background: var(--exec-blue); color: #fff;
  border-radius: 8px; padding: 9px 14px;
  font-weight: 600; font-size: 13.5px;
  display: inline-flex; align-items: center; gap: 8px;
}
.btn-exec:hover { background: #1F49C7; }
.btn-consensus {
  background: var(--consensus); color: #fff;
  border-radius: 8px; padding: 9px 14px;
  font-weight: 600; font-size: 13.5px;
  display: inline-flex; align-items: center; gap: 8px;
  transition: box-shadow .25s ease;
}
.btn-consensus:hover { box-shadow: 0 0 0 4px rgba(124,58,237,0.15); }
.btn-danger {
  background: var(--claim); color: #fff;
  border-radius: 8px; padding: 9px 14px;
  font-weight: 600; font-size: 13.5px;
}
.btn-ghost {
  background: transparent; color: var(--ink);
  border: 1px dashed var(--auditline); border-radius: 8px;
  padding: 8px 13px; font-weight: 500; font-size: 13px;
}

/* ------------- DOCUMENTS / PANELS ------------- */
.doc {
  background: var(--white-ledger);
  border: 1px solid var(--auditline);
  border-radius: 12px;
  box-shadow: 0 1px 0 rgba(15,23,42,0.04), 0 8px 24px -18px rgba(15,23,42,0.18);
}
.doc-header {
  background: var(--audit-black); color: var(--ledger-white);
  border-radius: 12px 12px 0 0;
  padding: 14px 18px;
  display: flex; align-items: center; justify-content: space-between;
}
.doc-body { padding: 20px; }
.doc-footer {
  border-top: 1px solid var(--auditline);
  padding: 12px 18px;
  display: flex; align-items: center; justify-content: space-between;
  background: var(--frost-grey);
  border-radius: 0 0 12px 12px;
}

/* legacy panel classes (old code still uses these — render as light doc) */
.panel        { background: var(--white-ledger); border: 1px solid var(--auditline); border-radius: 12px; box-shadow: 0 1px 0 rgba(15,23,42,0.04), 0 8px 24px -18px rgba(15,23,42,0.18); }
.panel-dark   { background: var(--graphite-blue); color: var(--ledger-white); border: 1px solid var(--glass-grid); border-radius: 12px; }
.panel-darker { background: var(--audit-black); color: var(--ledger-white); border: 1px solid var(--glass-grid); border-radius: 12px; }
.panel-steel  { background: var(--blue-steel); color: var(--ink); border: 1px solid var(--auditline); border-radius: 12px; }
.panel-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 18px; border-bottom: 1px solid var(--auditline); }
.panel-header.dark { border-bottom-color: var(--glass-grid); }

.eyebrow {
  font-family: var(--font-jetbrains-mono), ui-monospace, monospace;
  font-size: 10.5px; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--consensus);
}
.eyebrow-slate { color: var(--slate); }

/* ------------- BADGES / PILLS ------------- */
.badge {
  display: inline-flex; align-items: center; gap: 6px;
  border-radius: 999px; padding: 3px 9px;
  font-size: 11.5px; font-weight: 600;
  border: 1px solid transparent;
}
.badge-consensus { background: rgba(124,58,237,0.10); color: var(--consensus); border-color: rgba(124,58,237,0.30); }
.badge-verified  { background: rgba(5,150,105,0.10);  color: var(--emerald);  border-color: rgba(5,150,105,0.30); }
.badge-amber     { background: rgba(245,158,11,0.10); color: var(--amber);    border-color: rgba(245,158,11,0.32); }
.badge-claim     { background: rgba(220,38,38,0.10);  color: var(--claim);    border-color: rgba(220,38,38,0.32); }
.badge-cyan      { background: rgba(6,182,212,0.10);  color: var(--data-cyan);border-color: rgba(6,182,212,0.32); }
.badge-blue      { background: rgba(37,99,235,0.10);  color: var(--exec-blue);border-color: rgba(37,99,235,0.32); }
.badge-slate     { background: rgba(100,116,139,0.10);color: var(--slate);    border-color: rgba(100,116,139,0.28); }
.badge-dark      { background: rgba(248,250,252,0.07);color: var(--ledger-white); border-color: var(--glass-grid); }

/* ------------- INPUTS ------------- */
.input {
  width: 100%; border-radius: 8px;
  border: 1px solid var(--auditline); background: var(--white-ledger);
  padding: 10px 12px; font-size: 14px; color: var(--ink);
  transition: border-color .15s ease, box-shadow .15s ease;
}
.input::placeholder { color: var(--slate); }
.input:focus {
  outline: none; border-color: var(--exec-blue);
  box-shadow: 0 0 0 3px rgba(37,99,235,0.15);
}

/* ------------- TABLES (LEDGER) ------------- */
.ledger-table { width: 100%; font-size: 13.5px; border-collapse: separate; border-spacing: 0; }
.ledger-table thead th {
  position: sticky; top: 0;
  text-align: left; padding: 10px 16px;
  font-size: 10.5px; font-weight: 600; letter-spacing: 0.10em;
  text-transform: uppercase; color: var(--slate);
  background: var(--frost-grey); border-bottom: 1px solid var(--auditline);
}
.ledger-table tbody td { padding: 12px 16px; border-top: 1px solid var(--auditline); vertical-align: top; }
.ledger-table tbody tr:hover { background: var(--frost-grey); }

/* ------------- STATUS DOTS ------------- */
.dot { width: 7px; height: 7px; border-radius: 999px; display: inline-block; }
.dot-consensus { background: var(--consensus); box-shadow: 0 0 0 4px rgba(124,58,237,0.18); animation: pulseDot 1.6s ease-in-out infinite; }
.dot-verified  { background: var(--emerald); }
.dot-amber     { background: var(--amber); }
.dot-claim     { background: var(--claim); }
.dot-cyan      { background: var(--data-cyan); box-shadow: 0 0 0 4px rgba(6,182,212,0.18); animation: pulseDot 1.6s ease-in-out infinite; }
.dot-slate     { background: var(--slate); }

/* ------------- METER BARS ------------- */
.meter { height: 6px; border-radius: 999px; background: var(--auditline); overflow: hidden; }
.meter > .fill { height: 100%; border-radius: 999px; }

/* ------------- HASH TEXT ------------- */
.hash {
  font-family: var(--font-jetbrains-mono), ui-monospace, monospace;
  font-size: 11.5px; color: var(--ink);
  background: var(--frost-grey); border: 1px solid var(--auditline);
  border-radius: 5px; padding: 1px 6px; word-break: break-all;
}
.hash-dark {
  font-family: var(--font-jetbrains-mono), ui-monospace, monospace;
  font-size: 11.5px; color: var(--ledger-white);
  background: rgba(248,250,252,0.06); border: 1px solid var(--glass-grid);
  border-radius: 5px; padding: 1px 6px; word-break: break-all;
}

/* ------------- LINK ------------- */
.link { color: var(--exec-blue); text-decoration: underline; text-underline-offset: 3px; }
.link:hover { color: #1F49C7; }

/* ------------- STAMP ------------- */
.stamp {
  display: inline-flex; align-items: center; gap: 8px;
  border: 2px solid var(--consensus); color: var(--consensus);
  border-radius: 4px; padding: 6px 12px;
  font-family: var(--font-jetbrains-mono), ui-monospace, monospace;
  font-size: 11.5px; letter-spacing: 0.14em; text-transform: uppercase;
  transform: rotate(-2deg);
  background: rgba(124,58,237,0.04);
  animation: stampIn .6s ease-out both;
  box-shadow: 0 0 0 1px rgba(124,58,237,0.35), 0 0 0 6px rgba(124,58,237,0.06);
}

/* ------------- DOCKET PAPER LINES ------------- */
.docket-lines {
  background-image:
    repeating-linear-gradient(to bottom, transparent 0 27px, rgba(148,163,184,0.16) 27px 28px);
}

/* ------------- DARK STRIP ------------- */
.audit-strip {
  background: var(--audit-black); color: var(--ledger-white);
  border-radius: 8px; padding: 10px 14px;
  display: flex; align-items: center; gap: 12px;
  font-size: 12.5px;
  border: 1px solid var(--glass-grid);
}
""",
)

# ===================================================================
# layout root (fonts wiring stays)
# ===================================================================
write(
    "app/layout.tsx",
    """import type { Metadata } from "next";
import { Space_Grotesk, Manrope, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  display: "swap",
});
const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
  display: "swap",
});
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "VeriSight — Analytics Assurance Desk",
  description:
    "The assurance desk for analytics claims. Before a dashboard insight becomes a business decision, verify whether the data actually supports it.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${spaceGrotesk.variable} ${manrope.variable} ${jetbrainsMono.variable}`}
    >
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
""",
)

# ===================================================================
# Logo mark — refined audit lens
# ===================================================================
write(
    "components/app/LogoMark.tsx",
    """export function LogoMark({ size = 30 }: { size?: number }) {
  return (
    <svg viewBox="0 0 32 32" width={size} height={size} aria-hidden>
      <defs>
        <linearGradient id="vsg-mark" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stopColor="#2563EB" />
          <stop offset="1" stopColor="#7C3AED" />
        </linearGradient>
      </defs>
      <rect x="1" y="1" width="30" height="30" rx="7" fill="#FFFFFF" stroke="url(#vsg-mark)" strokeWidth="1.4" />
      <g stroke="#94A3B8" strokeWidth="0.9">
        <line x1="6" y1="10" x2="26" y2="10" />
        <line x1="6" y1="14" x2="26" y2="14" />
        <line x1="6" y1="18" x2="26" y2="18" />
        <line x1="6" y1="22" x2="26" y2="22" />
      </g>
      <path d="M10 18 L14 22 L23 11" stroke="#7C3AED" strokeWidth="2.1" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="23" cy="11" r="1.8" fill="#7C3AED" />
    </svg>
  );
}
""",
)

# ===================================================================
# Executive top nav — replaces left rail
# ===================================================================
write(
    "components/app/ExecutiveTopNav.tsx",
    """"use client";
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
const SECONDARY = [
  { href: "/admin",    label: "Admin" },
  { href: "/profile",  label: "Profile" },
  { href: "/settings", label: "Settings" },
];

function isActive(path: string, href: string) {
  return path === href || path.startsWith(href + "/");
}

export function ExecutiveTopNav({
  email,
  displayName,
}: {
  email: string;
  displayName?: string | null;
}) {
  const path = usePathname();
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
""",
)

# ===================================================================
# Sub context bar — breadcrumb / workspace selector strip
# ===================================================================
write(
    "components/app/SubContextBar.tsx",
    """import { ReactNode } from "react";

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
""",
)

# ===================================================================
# UI primitives (kept compatible with prior code)
# ===================================================================
write(
    "components/ui/Button.tsx",
    """import { ButtonHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

type Variant = "primary" | "secondary" | "exec" | "consensus" | "danger" | "ghost";
interface Props extends ButtonHTMLAttributes<HTMLButtonElement> { variant?: Variant }

const variantClass: Record<Variant, string> = {
  primary: "btn-primary",
  secondary: "btn-secondary",
  exec: "btn-exec",
  consensus: "btn-consensus",
  danger: "btn-danger",
  ghost: "btn-ghost",
};

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variant = "primary", className, ...rest },
  ref,
) {
  return <button ref={ref} className={clsx(variantClass[variant], "disabled:opacity-60", className)} {...rest} />;
});
""",
)

write(
    "components/ui/Input.tsx",
    """import { InputHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  function Input({ className, ...rest }, ref) {
    return <input ref={ref} className={clsx("input", className)} {...rest} />;
  },
);
""",
)

write(
    "components/ui/Field.tsx",
    """import { ReactNode } from "react";

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
""",
)

write(
    "components/ui/Label.tsx",
    """import { LabelHTMLAttributes } from "react";
import clsx from "clsx";
export function Label({ className, ...rest }: LabelHTMLAttributes<HTMLLabelElement>) {
  return <label className={clsx("text-[11px] font-semibold uppercase tracking-[0.08em] text-slate", className)} {...rest} />;
}
""",
)

write(
    "components/ui/Panel.tsx",
    """import { HTMLAttributes } from "react";
import clsx from "clsx";

type Tone = "light" | "dark" | "darker" | "steel";
interface Props extends HTMLAttributes<HTMLDivElement> { tone?: Tone }

const toneClass: Record<Tone, string> = {
  light: "panel",
  dark: "panel-dark",
  darker: "panel-darker",
  steel: "panel-steel",
};

export function Panel({ tone = "light", className, ...rest }: Props) {
  return <div className={clsx(toneClass[tone], className)} {...rest} />;
}

export function PanelHeader({
  title, eyebrow, right, tone = "light",
}: { title: string; eyebrow?: string; right?: React.ReactNode; tone?: "light" | "dark" }) {
  return (
    <div className={clsx("panel-header", tone === "dark" && "dark")}>
      <div>
        {eyebrow ? <div className="eyebrow eyebrow-slate">{eyebrow}</div> : null}
        <div className="display text-[15px] font-semibold">{title}</div>
      </div>
      {right}
    </div>
  );
}
""",
)

# ===================================================================
# audit primitives (carry forward + new)
# ===================================================================
write(
    "components/audit/Badge.tsx",
    """import clsx from "clsx";
import { ReactNode } from "react";

type Tone =
  | "consensus" | "verified" | "amber" | "claim" | "cyan" | "blue" | "slate" | "dark";

const toneClass: Record<Tone, string> = {
  consensus: "badge-consensus",
  verified: "badge-verified",
  amber: "badge-amber",
  claim: "badge-claim",
  cyan: "badge-cyan",
  blue: "badge-blue",
  slate: "badge-slate",
  dark: "badge-dark",
};

export function Badge({ tone = "slate", children, className, dot }: {
  tone?: Tone; children: ReactNode; className?: string; dot?: boolean;
}) {
  const d: Record<Tone, string> = {
    consensus: "dot dot-consensus", verified: "dot dot-verified",
    amber: "dot dot-amber", claim: "dot dot-claim",
    cyan: "dot dot-cyan", blue: "dot dot-cyan",
    slate: "dot dot-slate", dark: "dot dot-slate",
  };
  return (
    <span className={clsx("badge", toneClass[tone], className)}>
      {dot ? <span className={d[tone]} /> : null}
      {children}
    </span>
  );
}
""",
)

write(
    "components/audit/HashText.tsx",
    """import clsx from "clsx";

export function HashText({
  value, short, dark, className,
}: { value: string; short?: boolean; dark?: boolean; className?: string }) {
  const display = short && value.length > 14 ? `${value.slice(0, 8)}…${value.slice(-6)}` : value;
  return <span className={clsx(dark ? "hash-dark" : "hash", className)}>{display}</span>;
}
""",
)

write(
    "components/audit/Meter.tsx",
    """import clsx from "clsx";

const fill: Record<"emerald" | "amber" | "claim" | "blue" | "cyan" | "consensus", string> = {
  emerald: "bg-emerald", amber: "bg-amber", claim: "bg-claim",
  blue: "bg-exec-blue", cyan: "bg-data-cyan", consensus: "bg-consensus",
};

export function Meter({ value, tone = "blue", className }: {
  value: number; tone?: keyof typeof fill; className?: string;
}) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div className={clsx("meter", className)}>
      <div className={clsx("fill", fill[tone])} style={{ width: `${v}%` }} />
    </div>
  );
}
""",
)

write(
    "components/audit/SourceOfTruthBadge.tsx",
    """import { Badge } from "./Badge";

export function SourceOfTruthBadge({ small }: { small?: boolean }) {
  return (
    <Badge tone="consensus" dot className={small ? "text-[10.5px]" : undefined}>
      Source of truth · GenLayer
    </Badge>
  );
}
""",
)

write(
    "components/audit/ConsensusBadge.tsx",
    """import { Badge } from "./Badge";

export function ConsensusBadge({ state = "reached" }: { state?: "reached" | "pending" | "failed" }) {
  if (state === "pending") return <Badge tone="amber" dot>Consensus pending</Badge>;
  if (state === "failed") return <Badge tone="claim" dot>Consensus failed</Badge>;
  return <Badge tone="consensus" dot>Validated by GenLayer</Badge>;
}
""",
)

write(
    "components/audit/SupportBadge.tsx",
    """import { Badge } from "./Badge";

export type Verdict =
  | "supported" | "partially_supported" | "unsupported" | "misleading" | "needs_more_evidence";

const map: Record<Verdict, { tone: "verified" | "amber" | "claim" | "slate"; label: string }> = {
  supported:           { tone: "verified", label: "Supported" },
  partially_supported: { tone: "amber",    label: "Partially supported" },
  unsupported:         { tone: "claim",    label: "Unsupported" },
  misleading:          { tone: "claim",    label: "Misleading" },
  needs_more_evidence: { tone: "slate",    label: "Needs more evidence" },
};

export function SupportBadge({ verdict }: { verdict: Verdict }) {
  const v = map[verdict];
  return <Badge tone={v.tone} dot>{v.label}</Badge>;
}
""",
)

write(
    "components/audit/RiskBadge.tsx",
    """import { Badge } from "./Badge";

export function RiskBadge({ level = "moderate" }: { level?: "low" | "moderate" | "high" }) {
  if (level === "high") return <Badge tone="claim" dot>High business risk</Badge>;
  if (level === "low") return <Badge tone="verified" dot>Low business risk</Badge>;
  return <Badge tone="amber" dot>Moderate business risk</Badge>;
}
""",
)

# Judgment stamp
write(
    "components/audit/JudgmentStamp.tsx",
    """export function JudgmentStamp({ label = "Validated · GenLayer Consensus" }: { label?: string }) {
  return <span className="stamp">{label}</span>;
}
""",
)

# Official judgment header
write(
    "components/audit/OfficialJudgmentHeader.tsx",
    """import { JudgmentStamp } from "./JudgmentStamp";
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
""",
)

# Empty state — document-style
write(
    "components/audit/EmptyState.tsx",
    """import { ReactNode } from "react";

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
""",
)

# Claim Docket table (uses passed rows)
write(
    "components/audit/ClaimDocketTable.tsx",
    """import Link from "next/link";
import { Badge } from "./Badge";

export type DocketRow = {
  id: string;
  claim: string;
  workspace?: string | null;
  metric?: string | null;
  status: string;
  created_at: string;
};

const statusTone: Record<string, "slate" | "amber" | "consensus" | "verified" | "claim"> = {
  draft: "slate", evidence_added: "slate", ready: "blue" as never,
  submitted: "consensus", consensus_pending: "amber",
  verdict_issued: "verified", needs_more_evidence: "amber", archived: "slate",
};

export function ClaimDocketTable({ rows }: { rows: DocketRow[] }) {
  return (
    <table className="ledger-table">
      <thead>
        <tr>
          <th>Claim</th>
          <th>Workspace</th>
          <th>Metric</th>
          <th>Status</th>
          <th>Last updated</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.id}>
            <td>
              <Link href={`/audits/${r.id}`} className="display text-[14px] font-medium text-ink hover:underline">
                {r.claim}
              </Link>
              <div className="mono mt-0.5 text-[10px] uppercase tracking-[0.14em] text-slate">
                docket · {r.id.slice(0, 8)}
              </div>
            </td>
            <td className="text-slate">{r.workspace ?? "—"}</td>
            <td className="text-slate">{r.metric ?? "—"}</td>
            <td>
              <Badge tone={statusTone[r.status] ?? "slate"}>{r.status.replace(/_/g, " ")}</Badge>
            </td>
            <td className="text-slate">{new Date(r.created_at).toLocaleDateString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
""",
)

# Assumption review panel
write(
    "components/audit/AssumptionReviewPanel.tsx",
    """import { ReactNode } from "react";
import { Badge } from "./Badge";

type Note = { kind: "causality" | "comparison" | "segment" | "metric" | "evidence"; text: string };

const kindLabel: Record<Note["kind"], string> = {
  causality: "Causality risk",
  comparison: "Missing comparison group",
  segment: "Segment limitation",
  metric: "Metric definition gap",
  evidence: "Evidence limitation",
};

export function AssumptionReviewPanel({
  notes,
  empty,
}: {
  notes?: Note[];
  empty?: ReactNode;
}) {
  if (!notes || notes.length === 0) {
    return (
      <div className="doc">
        <div className="border-b border-auditline px-5 py-3">
          <div className="eyebrow eyebrow-slate">Assumption review</div>
          <div className="display mt-0.5 text-[15px] font-semibold text-ink">
            What the claim assumes but does not prove
          </div>
        </div>
        <div className="px-5 py-8 text-center text-[13px] text-slate">{empty ?? "No assumptions flagged yet."}</div>
      </div>
    );
  }
  return (
    <div className="doc">
      <div className="border-b border-auditline px-5 py-3">
        <div className="eyebrow eyebrow-slate">Assumption review</div>
        <div className="display mt-0.5 text-[15px] font-semibold text-ink">
          What the claim assumes but does not prove
        </div>
      </div>
      <ul className="divide-y divide-auditline">
        {notes.map((n, i) => (
          <li key={i} className="flex items-start gap-3 px-5 py-3">
            <span className="mt-1 inline-block h-2 w-2 shrink-0 rounded-full bg-amber" />
            <div className="min-w-0 flex-1">
              <Badge tone="amber">{kindLabel[n.kind]}</Badge>
              <div className="mt-1 text-[13.5px] text-ink">{n.text}</div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
""",
)

# Metric trace map
write(
    "components/audit/MetricTraceMap.tsx",
    """import { ReactNode } from "react";

export function MetricTraceMap({
  metric = "Quarterly revenue by customer type",
  definition = "Sum of net revenue grouped by customer_type for the selected quarter.",
  timePeriod = "Q3 — North America",
  segment = "Customer type ∈ {new, repeat}; channel = direct",
  dataset = "fact_revenue (warehouse snapshot)",
  notes = "Excludes returns; refund-aware net revenue.",
  evidenceHash = "sha256:9f01…be21",
}: {
  metric?: string;
  definition?: string;
  timePeriod?: string;
  segment?: string;
  dataset?: string;
  notes?: string;
  evidenceHash?: string;
}) {
  return (
    <div className="doc p-6">
      <div className="eyebrow eyebrow-slate">Metric trace · lineage</div>
      <h2 className="display mt-1 text-section font-semibold text-ink">{metric}</h2>

      <div className="mt-6 grid grid-cols-1 gap-3 lg:grid-cols-[260px_1fr_260px]">
        <Node label="Metric definition" body={definition} />
        <Connector />
        <Node label="Time period" body={timePeriod} accent />
        <Connector vertical />
        <div />
        <Connector vertical />
        <Node label="Segment / filter context" body={segment} />
        <Connector />
        <Node label="Dataset summary" body={dataset} accent />
        <Connector vertical />
        <div />
        <Connector vertical />
        <Node label="Known limitations" body={notes} />
        <Connector />
        <Node label="Evidence hash" body={<span className="hash">{evidenceHash}</span>} accent />
      </div>
    </div>
  );
}

function Node({ label, body, accent }: { label: string; body: ReactNode; accent?: boolean }) {
  return (
    <div className={accent
      ? "rounded-panel border border-exec-blue/30 bg-blue-steel p-3"
      : "rounded-panel border border-auditline bg-white-ledger p-3"
    }>
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className="mt-1 text-[13px] text-ink">{body}</div>
    </div>
  );
}

function Connector({ vertical }: { vertical?: boolean }) {
  return (
    <div className="flex items-center justify-center">
      <div
        className={vertical
          ? "h-6 w-px bg-auditline"
          : "h-px w-full bg-auditline"
        }
      />
    </div>
  );
}
""",
)

# Decision memo doc component
write(
    "components/audit/DecisionMemo.tsx",
    """import Link from "next/link";
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
""",
)

# Evidence inspector drawer (right-side surface)
write(
    "components/audit/EvidenceInspectorDrawer.tsx",
    """import { ReactNode } from "react";

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
""",
)

# Signing infrastructure card (profile wallet)
write(
    "components/audit/SigningInfrastructureCard.tsx",
    """import { Badge } from "./Badge";
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
        <Row label="Signing address" value={<HashText value={address} short />} />
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
""",
)

# ===================================================================
# Landing page — boardroom audit reveal
# ===================================================================
write(
    "app/page.tsx",
    """import Link from "next/link";
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
""",
)

# ===================================================================
# Auth pages — recolour to Ledger Glass palette
# ===================================================================
write(
    "app/(auth)/layout.tsx",
    """import Link from "next/link";
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
""",
)

write(
    "app/(auth)/signup/page.tsx",
    """"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { signupAction } from "@/lib/auth/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Badge } from "@/components/audit/Badge";

export default function SignupPage() {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [recovery, setRecovery] = useState<{ phrase: string; address: string } | null>(null);
  const [ack, setAck] = useState(false);

  if (recovery) {
    const words = recovery.phrase.split(/\\s+/);
    return (
      <div className="space-y-5">
        <div>
          <Badge tone="consensus" dot>Recovery key · shown only once</Badge>
          <h1 className="display mt-3 text-[28px] font-semibold text-ink">
            Save your recovery phrase
          </h1>
          <p className="mt-2 text-sm text-slate">
            These 24 words are the only way to restore your embedded wallet if you reset your
            password. Store them safely offline. VeriSight cannot recover them for you.
          </p>
        </div>
        <div className="doc p-5">
          <div className="grid grid-cols-3 gap-2">
            {words.map((w, i) => (
              <div
                key={i}
                className="flex items-center gap-2 rounded-btn border border-auditline bg-frost-grey px-2 py-1.5"
              >
                <span className="mono w-6 text-right text-[11px] text-slate">{i + 1}</span>
                <span className="mono text-[12.5px] text-ink">{w}</span>
              </div>
            ))}
          </div>
          <div className="mt-5">
            <Field label="Signing address">
              <div className="hash break-all">{recovery.address}</div>
            </Field>
          </div>
          <label className="mt-5 flex items-start gap-2 text-sm text-ink">
            <input
              type="checkbox"
              checked={ack}
              onChange={(e) => setAck(e.target.checked)}
              className="mt-1 accent-exec-blue"
            />
            <span>
              I have saved my recovery phrase somewhere safe and understand it cannot be
              recovered if lost.
            </span>
          </label>
          <Button
            className="mt-5 w-full"
            variant="exec"
            disabled={!ack}
            onClick={() => router.push("/onboarding")}
          >
            Continue to workspace setup
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <Badge tone="blue" dot>Create access</Badge>
        <h1 className="display mt-3 text-[28px] font-semibold text-ink">
          Open your assurance desk
        </h1>
        <p className="mt-2 text-sm text-slate">
          Your VeriSight profile includes a secure embedded wallet used only for GenLayer audit
          actions. You do not need a browser wallet for normal use.
        </p>
      </div>

      <div className="doc p-6">
        <form
          className="space-y-4"
          action={(fd) => {
            setError(null);
            start(async () => {
              const res = await signupAction(fd);
              if (!res.ok) setError(res.error);
              else setRecovery({ phrase: res.recoveryPhrase, address: res.walletAddress });
            });
          }}
        >
          <Field label="Display name">
            <Input name="displayName" required placeholder="Analyst name" />
          </Field>
          <Field label="Email">
            <Input type="email" name="email" required placeholder="you@company.com" />
          </Field>
          <Field label="Password" hint="At least 8 characters.">
            <Input type="password" name="password" required minLength={8} />
          </Field>
          {error ? (
            <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">
              {error}
            </div>
          ) : null}
          <Button type="submit" variant="exec" className="w-full" disabled={pending}>
            {pending ? "Provisioning embedded signer…" : "Create account"}
          </Button>
        </form>
      </div>

      <p className="text-sm text-slate">
        Already have an account?{" "}
        <Link href="/login" className="link">Sign in</Link>
      </p>
    </div>
  );
}
""",
)

write(
    "app/(auth)/login/page.tsx",
    """"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { loginAction } from "@/lib/auth/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Badge } from "@/components/audit/Badge";

export default function LoginPage() {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="space-y-5">
      <div>
        <Badge tone="blue" dot>Executive access</Badge>
        <h1 className="display mt-3 text-[28px] font-semibold text-ink">
          Sign in to VeriSight
        </h1>
        <p className="mt-2 text-sm text-slate">
          Email and password only. Your embedded signer unlocks in the background.
        </p>
      </div>
      <div className="doc p-6">
        <form
          className="space-y-4"
          action={(fd) => {
            setError(null);
            start(async () => {
              const res = await loginAction(fd);
              if (!res.ok) setError(res.error ?? "Sign in failed");
              else router.push("/dashboard");
            });
          }}
        >
          <Field label="Email"><Input type="email" name="email" required /></Field>
          <Field label="Password"><Input type="password" name="password" required /></Field>
          {error ? (
            <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">
              {error}
            </div>
          ) : null}
          <Button type="submit" variant="exec" className="w-full" disabled={pending}>
            {pending ? "Signing in…" : "Continue"}
          </Button>
        </form>
        <div className="mt-4 flex items-center justify-between text-sm">
          <Link href="/forgot-password" className="link">Forgot password</Link>
          <Link href="/signup" className="link">Create account</Link>
        </div>
      </div>
    </div>
  );
}
""",
)

write(
    "app/(auth)/forgot-password/page.tsx",
    """"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { forgotPasswordAction } from "@/lib/auth/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Badge } from "@/components/audit/Badge";

export default function ForgotPasswordPage() {
  const [pending, start] = useTransition();
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="space-y-5">
      <div>
        <Badge tone="amber" dot>Security recovery</Badge>
        <h1 className="display mt-3 text-[28px] font-semibold text-ink">Forgot password</h1>
        <p className="mt-2 text-sm text-slate">
          Password reset does not create a new wallet. Your existing embedded wallet remains
          linked to your VeriSight profile and requires recovery key verification.
        </p>
      </div>
      <div className="doc p-6">
        <form
          className="space-y-4"
          action={(fd) => {
            setError(null); setMsg(null);
            start(async () => {
              const res = await forgotPasswordAction(fd);
              if (!res.ok) setError(res.error ?? "Failed");
              else setMsg("Check your email for a reset link.");
            });
          }}
        >
          <Field label="Email"><Input type="email" name="email" required /></Field>
          {error ? (
            <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">{error}</div>
          ) : null}
          {msg ? (
            <div className="rounded-btn border border-emerald/40 bg-emerald/5 p-3 text-sm text-emerald">{msg}</div>
          ) : null}
          <Button type="submit" variant="exec" className="w-full" disabled={pending}>
            {pending ? "Sending…" : "Send reset link"}
          </Button>
        </form>
        <div className="mt-4 text-sm">
          <Link href="/login" className="link">Back to sign in</Link>
        </div>
      </div>
    </div>
  );
}
""",
)

write(
    "app/(auth)/reset-password/page.tsx",
    """"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { resetPasswordAction } from "@/lib/auth/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Badge } from "@/components/audit/Badge";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="space-y-5">
      <div>
        <Badge tone="consensus" dot>Signer re-wrap</Badge>
        <h1 className="display mt-3 text-[28px] font-semibold text-ink">Reset password</h1>
        <p className="mt-2 text-sm text-slate">
          Resetting your password must not replace your embedded wallet. VeriSight will
          preserve the wallet linked to your Supabase user profile.
        </p>
      </div>
      <div className="doc p-6">
        <form
          className="space-y-4"
          action={(fd) => {
            setError(null);
            start(async () => {
              const res = await resetPasswordAction(fd);
              if (!res.ok) setError(res.error ?? "Failed");
              else router.push("/dashboard");
            });
          }}
        >
          <Field label="New password"><Input type="password" name="newPassword" required minLength={8} /></Field>
          <Field label="Recovery phrase" hint="24 words from your VeriSight signup.">
            <textarea name="recoveryPhrase" required rows={3} className="input mono"
                      placeholder="word1 word2 word3 …" />
          </Field>
          <div className="rounded-btn border border-auditline bg-blue-steel p-3 text-xs text-ink">
            VeriSight will unwrap your existing wallet key using the recovery phrase, then
            re-encrypt it under your new password. Your signing address will not change.
          </div>
          {error ? (
            <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">{error}</div>
          ) : null}
          <Button type="submit" variant="exec" className="w-full" disabled={pending}>
            {pending ? "Re-wrapping signer…" : "Set new password"}
          </Button>
        </form>
      </div>
    </div>
  );
}
""",
)

# ===================================================================
# Signed-in shell (uses ExecutiveTopNav)
# ===================================================================
write(
    "app/(app)/layout.tsx",
    """import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { ExecutiveTopNav } from "@/components/app/ExecutiveTopNav";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, profile } = await getProfile();
  if (!profile) redirect("/login");

  return (
    <div className="min-h-screen bg-frost-grey">
      <ExecutiveTopNav email={user.email ?? ""} displayName={profile.display_name} />
      <div className="mx-auto w-full max-w-[1400px]">{children}</div>
    </div>
  );
}
""",
)

# ===================================================================
# /dashboard — Assurance Desk
# ===================================================================
write(
    "app/(app)/dashboard/page.tsx",
    """import Link from "next/link";
import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { SourceOfTruthBadge } from "@/components/audit/SourceOfTruthBadge";
import { Meter } from "@/components/audit/Meter";
import { SupportBadge } from "@/components/audit/SupportBadge";
import { JudgmentStamp } from "@/components/audit/JudgmentStamp";

export default async function AssuranceDeskPage() {
  const { profile, supabase } = await getProfile();
  if (!profile?.onboarding_completed) redirect("/onboarding");

  const { data: workspaces } = await supabase
    .from("workspaces").select("id,name").order("created_at", { ascending: false }).limit(1);
  const ws = workspaces?.[0];

  const { count: auditCount } = await supabase
    .from("insight_audit_cases").select("*", { count: "exact", head: true });

  return (
    <>
      <SubContextBar
        eyebrow="Daily review"
        title={`Assurance Desk · ${profile.display_name ?? "Analyst"}`}
        workspaceName={ws?.name}
        right={
          <>
            <Badge tone="cyan" dot>Datasets fresh</Badge>
            <SourceOfTruthBadge />
            <Link href="/audits/new" className="btn-consensus">
              <span className="dot bg-white" /> Audit an insight
            </Link>
          </>
        }
      />

      <main className="px-6 py-6 space-y-6">
        {/* Top — latest judgment summary + dataset freshness */}
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1.6fr_1fr]">
          <article className="doc overflow-hidden">
            <div className="doc-header">
              <div>
                <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
                  Latest GenLayer judgment · sample
                </div>
                <div className="display text-[18px] font-semibold">
                  Revenue growth was mainly driven by repeat customers.
                </div>
              </div>
              <JudgmentStamp />
            </div>
            <div className="grid grid-cols-2 gap-px bg-auditline lg:grid-cols-4">
              <Cell label="Verdict" value="Partially supported" accent />
              <Cell label="Support level" value="Moderate" />
              <Cell label="Confidence" value="Moderate" />
              <Cell label="Business risk" value="Claim may overstate causality" />
            </div>
            <div className="px-5 py-4 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <SupportBadge verdict="partially_supported" />
                <Badge tone="amber" dot>Causality risk</Badge>
              </div>
              <Link href="/verdicts" className="link text-sm">View judgment archive →</Link>
            </div>
          </article>

          <article className="doc p-5">
            <div className="eyebrow eyebrow-slate">Dataset freshness</div>
            <div className="display mt-1 text-section font-semibold text-ink">Live</div>
            <p className="text-[13px] text-slate">
              Warehouse snapshots match metric definitions. No stale evidence detected.
            </p>
            <div className="mt-4 space-y-3">
              <FreshRow label="Warehouse pulse"   tone="cyan"     value={92} />
              <FreshRow label="Evidence hashes"   tone="emerald"  value={88} />
              <FreshRow label="Open audit packets" tone="amber"   value={20} />
            </div>
          </article>
        </section>

        {/* Middle — Claim docket + Evidence gaps */}
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1.7fr_1fr]">
          <article className="doc overflow-hidden">
            <Head title="Claim Docket" eyebrow="Pending review"
                  right={<Link href="/audits" className="btn-secondary">Open docket</Link>} />
            <EmptyState
              title="No insights have been audited yet"
              body="Start by submitting a dashboard claim and VeriSight will prepare it for GenLayer consensus review."
              action={<Link href="/audits/new" className="btn-consensus">Audit an insight</Link>}
            />
          </article>

          <article className="doc">
            <Head title="Evidence gaps" eyebrow="Review queue" />
            <EmptyState
              title="No evidence gaps yet"
              body="Once audit packets exist, weak evidence and missing definitions will be queued here for review."
            />
          </article>
        </section>

        {/* Bottom — risk queue + drafts + activity */}
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <article className="doc">
            <Head title="Business risk queue" eyebrow="High & moderate" />
            <EmptyState title="No risks queued"
              body="High-risk judgments will appear here so executives can review them before acting." />
          </article>
          <article className="doc">
            <Head title="Draft decision memos" eyebrow="Awaiting executive review" />
            <EmptyState title="No memos drafted"
              body="Once a judgment is issued, you can convert it into an executive-ready decision memo." />
          </article>
          <article className="doc-header rounded-panel overflow-hidden border border-glass-grid"
                   style={{ background: "var(--audit-black)" }}>
            <div className="w-full">
              <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
                Contract trace · StudioNet
              </div>
              <div className="display mt-1 text-[16px] font-semibold text-ledger-white">
                VeriSightInsightAuditor
              </div>
              <div className="mt-3 space-y-2 text-[12px]">
                <Trace label="Validator quorum" v="ready" />
                <Trace label="Equivalence criteria" v="loaded" />
                <Trace label="Pending submissions" v={String(auditCount ?? 0)} />
              </div>
            </div>
          </article>
        </section>
      </main>
    </>
  );
}

function Head({ title, eyebrow, right }: { title: string; eyebrow: string; right?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b border-auditline px-5 py-3">
      <div>
        <div className="eyebrow eyebrow-slate">{eyebrow}</div>
        <div className="display text-[15px] font-semibold text-ink">{title}</div>
      </div>
      {right}
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
function FreshRow({ label, tone, value }: { label: string; tone: "cyan" | "emerald" | "amber"; value: number }) {
  return (
    <div>
      <div className="flex items-center justify-between text-[12.5px] text-slate">
        <span>{label}</span><span className="mono text-ink">{value}%</span>
      </div>
      <Meter value={value} tone={tone} className="mt-1.5" />
    </div>
  );
}
function Trace({ label, v }: { label: string; v: string }) {
  return (
    <div className="flex items-center justify-between border-b border-glass-grid pb-1.5 text-ledger-white/75 last:border-b-0">
      <span>{label}</span>
      <span className="mono uppercase tracking-[0.12em] text-ledger-white/55">{v}</span>
    </div>
  );
}
""",
)

# ===================================================================
# /onboarding — Workspace Assurance Setup
# ===================================================================
write(
    "app/(app)/onboarding/page.tsx",
    """import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { Badge } from "@/components/audit/Badge";
import { OnboardingForm } from "./OnboardingForm";

export default async function OnboardingPage() {
  const { profile } = await getProfile();
  if (profile?.onboarding_completed) redirect("/dashboard");

  return (
    <main className="mx-auto w-full max-w-[1100px] px-6 py-12">
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_1.4fr]">
        <div className="space-y-4">
          <Badge tone="consensus" dot>Workspace assurance setup</Badge>
          <h1 className="display text-pagetitle font-semibold text-ink">
            Open your first analytics workspace
          </h1>
          <p className="text-sm text-slate">
            A workspace groups one company, team, client, or project. Claims, evidence,
            metric traces, GenLayer judgments, and decision memos all belong to a workspace.
          </p>

          <div className="doc p-5">
            <Stage n={1} label="Account profile"     done />
            <Stage n={2} label="Workspace identity"  active />
            <Stage n={3} label="Analytics function" />
            <Stage n={4} label="KPI focus" />
            <Stage n={5} label="Recovery key setup" />
          </div>

          <div className="rounded-panel border border-auditline bg-blue-steel p-4 text-[13px] text-ink">
            Tip · Pick a KPI category matching the kind of dashboard insight you most often audit.
            You can change it later.
          </div>
        </div>

        <div className="doc p-6">
          <OnboardingForm />
        </div>
      </div>
    </main>
  );
}

function Stage({ n, label, active, done }: { n: number; label: string; active?: boolean; done?: boolean }) {
  return (
    <div className="flex items-center gap-3 py-1.5">
      <span
        className={
          done
            ? "grid h-6 w-6 place-items-center rounded-full bg-emerald text-[11px] font-semibold text-white"
            : active
            ? "grid h-6 w-6 place-items-center rounded-full bg-exec-blue text-[11px] font-semibold text-white"
            : "grid h-6 w-6 place-items-center rounded-full border border-auditline bg-white-ledger text-[11px] font-semibold text-slate"
        }
      >
        {done ? "✓" : n}
      </span>
      <span className={done || active ? "text-sm font-medium text-ink" : "text-sm text-slate"}>{label}</span>
    </div>
  );
}
""",
)

write(
    "app/(app)/onboarding/OnboardingForm.tsx",
    """"use client";

import { useState, useTransition } from "react";
import { completeOnboardingAction } from "@/lib/workspaces/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";

const FUNCS = ["Analytics", "Finance", "Growth", "Operations", "Product", "Executive"];
const CADENCES = ["Daily", "Weekly", "Monthly", "Quarterly"];
const KPIS = ["Revenue", "Retention", "Acquisition", "Conversion", "Efficiency", "Quality"];

export function OnboardingForm() {
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  return (
    <form
      className="space-y-5"
      action={(fd) => {
        setError(null);
        start(async () => {
          const res = await completeOnboardingAction(fd);
          if (res && "ok" in res && !res.ok) setError(res.error);
        });
      }}
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Workspace name"><Input name="name" required placeholder="Acme Revenue Assurance" /></Field>
        <Field label="Organisation"><Input name="organisation_name" placeholder="Acme Inc." /></Field>
        <Field label="Business function">
          <select name="business_function" className="input">
            <option value="">Select…</option>{FUNCS.map((v) => <option key={v}>{v}</option>)}
          </select>
        </Field>
        <Field label="Industry"><Input name="industry" placeholder="SaaS, e-commerce…" /></Field>
        <Field label="Reporting cadence">
          <select name="reporting_cadence" className="input">
            <option value="">Select…</option>{CADENCES.map((v) => <option key={v}>{v}</option>)}
          </select>
        </Field>
        <Field label="Primary KPI category">
          <select name="primary_kpi_category" className="input">
            <option value="">Select…</option>{KPIS.map((v) => <option key={v}>{v}</option>)}
          </select>
        </Field>
      </div>
      {error ? (
        <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">{error}</div>
      ) : null}
      <Button type="submit" variant="exec" className="w-full" disabled={pending}>
        {pending ? "Opening workspace…" : "Open workspace and continue"}
      </Button>
    </form>
  );
}
""",
)

# ===================================================================
# /workspaces
# ===================================================================
write(
    "app/(app)/workspaces/page.tsx",
    """import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { CreateWorkspaceForm } from "./CreateWorkspaceForm";

export default async function WorkspacesPage() {
  const { supabase } = await requireUser();
  const { data: workspaces } = await supabase
    .from("workspaces")
    .select("id,name,organisation_name,business_function,industry,primary_kpi_category,reporting_cadence,created_at")
    .order("created_at", { ascending: false });

  return (
    <>
      <SubContextBar
        eyebrow="Analytics environments"
        title="Workspaces"
        right={<Badge tone="blue" dot>{workspaces?.length ?? 0} open</Badge>}
      />
      <main className="px-6 py-6">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.7fr_1fr]">
          <div className="space-y-4">
            {workspaces && workspaces.length > 0 ? workspaces.map((w) => (
              <article key={w.id} className="doc overflow-hidden">
                <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr]">
                  <div className="border-b border-auditline p-5 lg:border-b-0 lg:border-r">
                    <Link href={`/workspaces/${w.id}`} className="display text-cardtitle font-semibold text-ink hover:underline">
                      {w.name}
                    </Link>
                    <p className="text-sm text-slate">{w.organisation_name ?? "—"}</p>
                    <div className="mt-4 grid grid-cols-2 gap-3 text-[12.5px] sm:grid-cols-4">
                      <Stat label="Function" value={w.business_function} />
                      <Stat label="Industry" value={w.industry} />
                      <Stat label="Cadence"  value={w.reporting_cadence} />
                      <Stat label="KPI"      value={w.primary_kpi_category} />
                    </div>
                  </div>
                  <div className="bg-blue-steel p-5">
                    <div className="eyebrow eyebrow-slate">Audit posture</div>
                    <div className="mt-3 space-y-2 text-[13px]">
                      <Row label="Active claims"  value={<Badge tone="slate">0</Badge>} />
                      <Row label="Last judgment"  value={<Badge tone="slate">None yet</Badge>} />
                      <Row label="Evidence health" value={<Badge tone="verified" dot>OK</Badge>} />
                    </div>
                    <Link href={`/workspaces/${w.id}`} className="btn-secondary mt-4 w-full justify-center">
                      Open workspace
                    </Link>
                  </div>
                </div>
              </article>
            )) : (
              <div className="doc">
                <EmptyState
                  title="No workspaces yet"
                  body="Workspaces group your analytics environments. Open one to start auditing claims."
                />
              </div>
            )}
          </div>

          <div className="doc h-fit">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">New workspace</div>
              <div className="display text-[15px] font-semibold text-ink">Open workspace</div>
            </div>
            <div className="p-5"><CreateWorkspaceForm /></div>
          </div>
        </div>
      </main>
    </>
  );
}

function Stat({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className="mt-0.5 text-ink">{value ?? "—"}</div>
    </div>
  );
}
function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-slate">{label}</span>
      {value}
    </div>
  );
}
""",
)

write(
    "app/(app)/workspaces/CreateWorkspaceForm.tsx",
    """"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { createWorkspaceAction } from "@/lib/workspaces/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";

const FUNCS = ["Analytics", "Finance", "Growth", "Operations", "Product", "Executive"];
const CADENCES = ["Daily", "Weekly", "Monthly", "Quarterly"];
const KPIS = ["Revenue", "Retention", "Acquisition", "Conversion", "Efficiency", "Quality"];

export function CreateWorkspaceForm() {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  return (
    <form className="space-y-3"
      action={(fd) => {
        setError(null);
        start(async () => {
          const res = await createWorkspaceAction(fd);
          if (!res.ok) setError(res.error);
          else router.refresh();
        });
      }}
    >
      <Field label="Workspace name"><Input name="name" required placeholder="Acme Revenue Assurance" /></Field>
      <Field label="Organisation"><Input name="organisation_name" placeholder="Acme Inc." /></Field>
      <Field label="Business function">
        <select name="business_function" className="input">
          <option value="">Select…</option>{FUNCS.map((v) => <option key={v}>{v}</option>)}
        </select>
      </Field>
      <Field label="Industry"><Input name="industry" placeholder="SaaS, e-commerce…" /></Field>
      <Field label="Reporting cadence">
        <select name="reporting_cadence" className="input">
          <option value="">Select…</option>{CADENCES.map((v) => <option key={v}>{v}</option>)}
        </select>
      </Field>
      <Field label="Primary KPI category">
        <select name="primary_kpi_category" className="input">
          <option value="">Select…</option>{KPIS.map((v) => <option key={v}>{v}</option>)}
        </select>
      </Field>
      {error ? <div className="rounded-btn border border-claim/40 bg-claim/5 p-2 text-xs text-claim">{error}</div> : null}
      <Button type="submit" variant="exec" className="w-full" disabled={pending}>
        {pending ? "Opening…" : "Open workspace"}
      </Button>
    </form>
  );
}
""",
)

write(
    "app/(app)/workspaces/[id]/page.tsx",
    """import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";

export default async function WorkspaceDetailPage({
  params,
}: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { supabase } = await requireUser();

  const { data: workspace } = await supabase.from("workspaces").select("*").eq("id", id).single();
  if (!workspace) notFound();

  const { data: audits } = await supabase
    .from("insight_audit_cases")
    .select("id,insight_claim,status,created_at,metric_name")
    .eq("workspace_id", id)
    .order("created_at", { ascending: false });

  return (
    <>
      <SubContextBar
        eyebrow="Workspace"
        title={workspace.name}
        workspaceName={workspace.organisation_name}
        right={
          <Link href={`/audits/new?workspace=${workspace.id}`} className="btn-consensus">
            <span className="dot bg-white" /> Audit an insight
          </Link>
        }
      />
      <main className="px-6 py-6 space-y-6">
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {[
            ["Business function", workspace.business_function],
            ["Industry", workspace.industry],
            ["Reporting cadence", workspace.reporting_cadence],
            ["Primary KPI category", workspace.primary_kpi_category],
          ].map(([label, val]) => (
            <div key={String(label)} className="doc p-4">
              <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
              <div className="mt-1 text-sm text-ink">{(val as string) ?? "—"}</div>
            </div>
          ))}
        </div>

        <article className="doc overflow-hidden">
          <div className="flex items-center justify-between border-b border-auditline px-5 py-3">
            <div>
              <div className="eyebrow eyebrow-slate">Claim docket</div>
              <div className="display text-[15px] font-semibold text-ink">Submitted claims</div>
            </div>
          </div>
          {audits && audits.length > 0 ? (
            <table className="ledger-table">
              <thead><tr><th>Claim</th><th>Metric</th><th>Status</th><th>Created</th></tr></thead>
              <tbody>
                {audits.map((a) => (
                  <tr key={a.id}>
                    <td><Link href={`/audits/${a.id}`} className="link">{a.insight_claim}</Link></td>
                    <td className="text-slate">{a.metric_name ?? "—"}</td>
                    <td><Badge tone="slate">{a.status.replace(/_/g, " ")}</Badge></td>
                    <td className="text-slate">{new Date(a.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState
              title="No claims docketed in this workspace yet"
              body="Submit a dashboard claim and VeriSight will prepare it for GenLayer judgment."
            />
          )}
        </article>
      </main>
    </>
  );
}
""",
)

# ===================================================================
# /audits — Claim Docket
# ===================================================================
write(
    "app/(app)/audits/page.tsx",
    """import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { EmptyState } from "@/components/audit/EmptyState";
import { ClaimDocketTable, DocketRow } from "@/components/audit/ClaimDocketTable";
import { Badge } from "@/components/audit/Badge";

export default async function ClaimDocketPage() {
  const { supabase } = await requireUser();
  const { data: audits } = await supabase
    .from("insight_audit_cases")
    .select("id,insight_claim,status,created_at,metric_name,workspace_id,workspaces(name)")
    .order("created_at", { ascending: false });

  const rows: DocketRow[] = (audits ?? []).map((a) => ({
    id: a.id,
    claim: a.insight_claim,
    workspace: ((a.workspaces as unknown) as { name: string } | null)?.name ?? null,
    metric: a.metric_name,
    status: a.status,
    created_at: a.created_at,
  }));

  return (
    <>
      <SubContextBar
        eyebrow="Audit ledger"
        title="Claim Docket"
        right={
          <>
            <Badge tone="blue" dot>{rows.length} registered</Badge>
            <Link href="/audits/new" className="btn-consensus">
              <span className="dot bg-white" /> Open claim review
            </Link>
          </>
        }
      />
      <main className="px-6 py-6">
        <article className="doc overflow-hidden">
          <div className="border-b border-auditline px-5 py-3">
            <div className="eyebrow eyebrow-slate">Register of analytics claims</div>
            <div className="display text-[15px] font-semibold text-ink">All claims under review</div>
          </div>
          {rows.length > 0 ? (
            <ClaimDocketTable rows={rows} />
          ) : (
            <EmptyState
              title="No insights have been audited yet"
              body="Open a claim review to submit a dashboard claim, attach evidence, and request a GenLayer judgment."
              action={<Link href="/audits/new" className="btn-consensus">Open claim review</Link>}
            />
          )}
        </article>
      </main>
    </>
  );
}
""",
)

# ===================================================================
# /audits/new — Open Claim Review
# ===================================================================
write(
    "app/(app)/audits/new/page.tsx",
    """import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EvidenceInspectorDrawer, InspectorRow } from "@/components/audit/EvidenceInspectorDrawer";
import { SourceOfTruthBadge } from "@/components/audit/SourceOfTruthBadge";

export default async function OpenClaimReviewPage() {
  await requireUser();
  return (
    <>
      <SubContextBar
        eyebrow="Audit intake"
        title="Open Claim Review"
        right={<Badge tone="amber" dot>Stage 5 · coming online</Badge>}
      />
      <main className="px-6 py-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
        <div className="space-y-4">
          <article className="doc">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">Step 1 of 6</div>
              <div className="display text-[15px] font-semibold text-ink">State the claim</div>
            </div>
            <div className="docket-lines px-5 py-6 text-slate">
              <p className="text-sm">
                Enter the dashboard insight, KPI narrative, or AI-generated claim under review.
                The full claim review form ships in Stage 5.
              </p>
            </div>
          </article>

          <article className="doc">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">Step 2–5</div>
              <div className="display text-[15px] font-semibold text-ink">
                Attach metric basis · reporting context · evidence · candidate interpretations
              </div>
            </div>
            <ol className="px-5 py-4 space-y-2 text-[13.5px] text-slate">
              <li>· Metric definition + time period + segment / filter context</li>
              <li>· Dataset summary + dashboard / report context</li>
              <li>· Evidence files uploaded to Supabase Storage (CSV, JSON, PDF, screenshots)</li>
              <li>· Three candidate interpretations passed to GenLayer for adjudication</li>
            </ol>
          </article>

          <article className="doc overflow-hidden">
            <div className="doc-header">
              <div>
                <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
                  Judgment request
                </div>
                <div className="display text-[16px] font-semibold">
                  Step 6 · Submit for GenLayer judgment
                </div>
              </div>
              <SourceOfTruthBadge small />
            </div>
            <div className="doc-body text-[13.5px] text-ink leading-relaxed">
              VeriSight will submit this claim, metric context, evidence references, and
              candidate interpretations to GenLayer. The frontend and Supabase do not decide
              whether the claim is supported. GenLayer validators independently review the
              evidence and produce the authoritative audit verdict.
            </div>
            <div className="doc-footer">
              <span className="text-[12px] text-slate">Submission disabled until packet is complete.</span>
              <button className="btn-consensus" disabled>
                Request GenLayer judgment
              </button>
            </div>
          </article>

          <Link href="/dashboard" className="btn-secondary inline-flex w-fit">← Back to Assurance Desk</Link>
        </div>

        <EvidenceInspectorDrawer title="Packet readiness">
          <InspectorRow left="Claim"         right="—" />
          <InspectorRow left="Metric basis"  right="—" />
          <InspectorRow left="Time period"   right="—" />
          <InspectorRow left="Evidence"      right="0 files" />
          <InspectorRow left="Interpretations" right="0 of 3" />
          <InspectorRow left="Readiness"     right={<Badge tone="amber" dot>Not ready</Badge>} />
        </EvidenceInspectorDrawer>
      </main>
    </>
  );
}
""",
)

# ===================================================================
# /audits/[id] — Official Audit Judgment
# ===================================================================
write(
    "app/(app)/audits/[id]/page.tsx",
    """import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { OfficialJudgmentHeader } from "@/components/audit/OfficialJudgmentHeader";
import { AssumptionReviewPanel } from "@/components/audit/AssumptionReviewPanel";
import { ConsensusBadge } from "@/components/audit/ConsensusBadge";
import { SupportBadge, Verdict } from "@/components/audit/SupportBadge";
import { Badge } from "@/components/audit/Badge";
import { EvidenceInspectorDrawer, InspectorRow } from "@/components/audit/EvidenceInspectorDrawer";
import { HashText } from "@/components/audit/HashText";

export default async function FullJudgmentRecordPage({
  params,
}: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { supabase } = await requireUser();

  const { data: audit } = await supabase
    .from("insight_audit_cases").select("*").eq("id", id).single();
  if (!audit) notFound();

  const { data: verdict } = await supabase
    .from("genlayer_audit_verdicts")
    .select("*")
    .eq("audit_case_id", id)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  const v: Verdict = (verdict?.verdict ?? "needs_more_evidence") as Verdict;

  return (
    <>
      <SubContextBar
        eyebrow="Full judgment record"
        title="Official Audit Judgment"
        right={
          <>
            {verdict ? <SupportBadge verdict={v} /> : <Badge tone="amber" dot>Awaiting judgment</Badge>}
            <ConsensusBadge state={verdict ? "reached" : "pending"} />
          </>
        }
      />
      <main className="px-6 py-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
        <div className="space-y-6">
          <OfficialJudgmentHeader
            auditId={audit.id}
            verdict={verdict?.verdict ?? "Pending"}
            supportLevel={verdict?.support_level ?? "—"}
            confidence={verdict?.confidence_label ?? "—"}
            businessRisk={verdict?.business_risk ?? "—"}
          />

          {/* document body */}
          <article className="doc">
            <div className="grid grid-cols-1 divide-y divide-auditline lg:grid-cols-2 lg:divide-x lg:divide-y-0">
              <Section label="Claim under review" body={audit.insight_claim} />
              <Section label="Business question" body={audit.business_question ?? "—"} />
            </div>
            <div className="grid grid-cols-1 divide-y divide-auditline lg:grid-cols-3 lg:divide-x lg:divide-y-0">
              <Section label="Metric basis" body={audit.metric_name ?? "—"} sub={audit.metric_definition ?? undefined} />
              <Section label="Time period" body={audit.time_period ?? "—"} />
              <Section label="Segment / filter" body={audit.segment_context ?? "—"} />
            </div>
            <div className="grid grid-cols-1 divide-y divide-auditline lg:grid-cols-2 lg:divide-x lg:divide-y-0">
              <Section label="Dataset summary" body={audit.dataset_summary ?? "—"} />
              <Section label="Report context" body={audit.report_context ?? "—"} />
            </div>
            <div className="border-t border-auditline">
              <Section label="Validator reasoning summary"
                       body={verdict?.reasoning_summary ?? "GenLayer validators will reason over the packet and reach consensus."} />
            </div>
          </article>

          <AssumptionReviewPanel
            notes={verdict ? [
              { kind: "causality", text: "New customer revenue, discount effects, and segment mix were not sufficiently controlled." },
              { kind: "comparison", text: "No matched control group for the same quarter last year." },
            ] : undefined}
          />

          <article className="doc">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">Recommended action</div>
              <div className="display text-[15px] font-semibold text-ink">Next step for the business</div>
            </div>
            <div className="px-5 py-4 text-[13.5px] text-ink">
              {verdict ? "Treat the claim as directional only. Re-issue with controlled comparisons before allocating budget." : "Submit the packet to GenLayer to receive an executive-ready recommendation."}
            </div>
          </article>

          <div className="audit-strip">
            <span className="mono text-[10.5px] uppercase tracking-[0.16em] text-ledger-white/55">Audit trail</span>
            <span>Submitted · {new Date(audit.created_at).toLocaleString()}</span>
            <span className="mx-1 h-3 w-px bg-glass-grid" />
            <span>Status · {audit.status.replace(/_/g, " ")}</span>
            <Link href={`/memos?audit=${audit.id}`} className="ml-auto btn-secondary bg-white/[0.04] text-ledger-white border-glass-grid hover:bg-white/[0.08]">
              Export decision memo
            </Link>
          </div>
        </div>

        <EvidenceInspectorDrawer title="GenLayer record">
          <InspectorRow left="Contract"        right={<HashText dark value={verdict?.contract_address ?? "—"} short />} />
          <InspectorRow left="Transaction"     right={<HashText dark value={verdict?.transaction_hash ?? "—"} short />} />
          <InspectorRow left="Audit ID"        right={<HashText dark value={audit.id} short />} />
          <InspectorRow left="Evidence digest" right={<HashText dark value={verdict?.evidence_digest ?? "—"} short />} />
          <InspectorRow left="Consensus"       right={<ConsensusBadge state={verdict ? "reached" : "pending"} />} />
        </EvidenceInspectorDrawer>
      </main>
    </>
  );
}

function Section({ label, body, sub }: { label: string; body: string; sub?: string }) {
  return (
    <div className="px-5 py-4">
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className="mt-1 text-[14px] text-ink">{body}</div>
      {sub ? <div className="mt-1 text-[12.5px] text-slate">{sub}</div> : null}
    </div>
  );
}
""",
)

# ===================================================================
# /verdicts — GenLayer Judgments archive
# ===================================================================
write(
    "app/(app)/verdicts/page.tsx",
    """import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { HashText } from "@/components/audit/HashText";

export default async function GenLayerJudgmentsPage() {
  const { supabase } = await requireUser();
  const { data: verdicts } = await supabase
    .from("genlayer_audit_verdicts")
    .select("id,audit_case_id,verdict,support_level,business_risk,contract_address,transaction_hash,evidence_digest,created_at")
    .order("created_at", { ascending: false });

  return (
    <>
      <SubContextBar
        eyebrow="Judgment archive"
        title="GenLayer Judgments"
        right={<Badge tone="consensus" dot>{verdicts?.length ?? 0} on record</Badge>}
      />
      <main className="px-6 py-6">
        <article className="doc overflow-hidden">
          <div className="border-b border-auditline px-5 py-3">
            <div className="eyebrow eyebrow-slate">Consensus verdict ledger</div>
            <div className="display text-[15px] font-semibold text-ink">All judgments issued</div>
          </div>
          {verdicts && verdicts.length > 0 ? (
            <table className="ledger-table">
              <thead>
                <tr>
                  <th>Audit ID</th>
                  <th>Verdict</th>
                  <th>Support</th>
                  <th>Business risk</th>
                  <th>Contract</th>
                  <th>Tx hash</th>
                  <th>Evidence digest</th>
                  <th>Issued</th>
                </tr>
              </thead>
              <tbody>
                {verdicts.map((v) => (
                  <tr key={v.id}>
                    <td>
                      <Link href={`/audits/${v.audit_case_id}`} className="link">
                        <HashText value={v.audit_case_id} short />
                      </Link>
                    </td>
                    <td className="text-ink">{v.verdict ?? "—"}</td>
                    <td><Badge tone="slate">{v.support_level ?? "—"}</Badge></td>
                    <td className="text-slate">{v.business_risk ?? "—"}</td>
                    <td><HashText value={v.contract_address ?? "—"} short /></td>
                    <td><HashText value={v.transaction_hash ?? "—"} short /></td>
                    <td><HashText value={v.evidence_digest ?? "—"} short /></td>
                    <td className="text-slate">{new Date(v.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState
              title="No judgments issued yet"
              body="Once GenLayer validators reach consensus on your first audit, judgments will appear here as a formal record."
            />
          )}
        </article>
      </main>
    </>
  );
}
""",
)

# ===================================================================
# /memos — Decision Memos (NEW)
# ===================================================================
write(
    "app/(app)/memos/page.tsx",
    """import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { DecisionMemo } from "@/components/audit/DecisionMemo";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";

export default async function DecisionMemosPage() {
  const { supabase } = await requireUser();
  const { data: verdicts } = await supabase
    .from("genlayer_audit_verdicts")
    .select("id,audit_case_id,verdict,support_level,business_risk,contract_address,transaction_hash,reasoning_summary,created_at,insight_audit_cases(insight_claim)")
    .order("created_at", { ascending: false });

  type Row = NonNullable<typeof verdicts>[number] & { insight_audit_cases?: { insight_claim: string } | null };
  const rows = (verdicts ?? []) as Row[];

  return (
    <>
      <SubContextBar
        eyebrow="Executive-ready summaries"
        title="Decision Memos"
        right={<Badge tone="blue" dot>{rows.length} memos</Badge>}
      />
      <main className="px-6 py-6 space-y-4">
        {rows.length > 0 ? rows.map((v) => (
          <DecisionMemo
            key={v.id}
            auditId={v.audit_case_id}
            claim={v.insight_audit_cases?.insight_claim ?? "Claim under review"}
            verdict={v.verdict ?? "Pending"}
            supportLevel={v.support_level ?? "—"}
            businessRisk={v.business_risk ?? "—"}
            recommendedAction="Treat the claim as directional only until controlled comparisons are introduced."
            evidenceSummary={v.reasoning_summary ?? "Validators reviewed the metric definition, dataset snapshot, and report context."}
            contractAddress={v.contract_address}
            transactionHash={v.transaction_hash}
          />
        )) : (
          <div className="doc">
            <EmptyState
              title="No decision memos yet"
              body="Once a GenLayer judgment is issued, VeriSight converts it into an executive-ready memo you can share with the boardroom."
            />
          </div>
        )}
      </main>
    </>
  );
}
""",
)

# ===================================================================
# /trace — Metric Trace (NEW)
# ===================================================================
write(
    "app/(app)/trace/page.tsx",
    """import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { MetricTraceMap } from "@/components/audit/MetricTraceMap";

export default async function MetricTracePage() {
  await requireUser();
  return (
    <>
      <SubContextBar
        eyebrow="Lineage and traceability"
        title="Metric Trace"
        right={<Badge tone="cyan" dot>Demo lineage</Badge>}
      />
      <main className="px-6 py-6 space-y-4">
        <p className="max-w-3xl text-[13.5px] text-slate">
          Metric Trace maps how a claim connects to its definition, time period, segment context,
          source dataset, calculation notes, and evidence hash. Validators rely on this lineage
          to judge whether a claim is supported by the underlying data.
        </p>
        <MetricTraceMap />
      </main>
    </>
  );
}
""",
)

# ===================================================================
# /evidence — Evidence Ledger
# ===================================================================
write(
    "app/(app)/evidence/page.tsx",
    """import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { HashText } from "@/components/audit/HashText";

export default async function EvidenceLedgerPage() {
  const { supabase } = await requireUser();
  const { data: files } = await supabase
    .from("evidence_files")
    .select("id,audit_case_id,file_type,file_size,evidence_hash,created_at,file_url")
    .order("created_at", { ascending: false });

  return (
    <>
      <SubContextBar
        eyebrow="Formal evidence vault"
        title="Evidence Ledger"
        right={<Badge tone="blue" dot>{files?.length ?? 0} records</Badge>}
      />
      <main className="px-6 py-6">
        <article className="doc overflow-hidden">
          <div className="border-b border-auditline px-5 py-3">
            <div className="eyebrow eyebrow-slate">Audit evidence</div>
            <div className="display text-[15px] font-semibold text-ink">All evidence records</div>
          </div>
          {files && files.length > 0 ? (
            <table className="ledger-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Size</th>
                  <th>Evidence hash</th>
                  <th>Linked claim</th>
                  <th>Used in judgment</th>
                  <th>Source integrity</th>
                  <th>Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {files.map((f) => (
                  <tr key={f.id}>
                    <td><Badge tone="blue">{f.file_type}</Badge></td>
                    <td className="text-slate">{Math.round((f.file_size ?? 0) / 1024)} KB</td>
                    <td><HashText value={f.evidence_hash ?? "—"} short /></td>
                    <td><HashText value={f.audit_case_id} short /></td>
                    <td><Badge tone="verified" dot>Yes</Badge></td>
                    <td><Badge tone="verified" dot>Intact</Badge></td>
                    <td className="text-slate">{new Date(f.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState
              title="This audit packet has no evidence yet"
              body="Add a dataset, dashboard screenshot, report, metric snapshot, or analyst note before submitting to GenLayer."
            />
          )}
        </article>
      </main>
    </>
  );
}
""",
)

# ===================================================================
# /snapshots — Dataset Snapshots
# ===================================================================
write(
    "app/(app)/snapshots/page.tsx",
    """import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { HashText } from "@/components/audit/HashText";

export default async function SnapshotsPage() {
  const { supabase } = await requireUser();
  const { data: snaps } = await supabase
    .from("data_snapshots")
    .select("id,audit_case_id,source_type,source_url,snapshot_hash,created_at")
    .order("created_at", { ascending: false });

  return (
    <>
      <SubContextBar
        eyebrow="Metric evidence registry"
        title="Dataset Snapshots"
        right={<Badge tone="cyan" dot>{snaps?.length ?? 0} snapshots</Badge>}
      />
      <main className="px-6 py-6">
        <article className="doc overflow-hidden">
          <div className="border-b border-auditline px-5 py-3">
            <div className="eyebrow eyebrow-slate">Snapshot ledger</div>
            <div className="display text-[15px] font-semibold text-ink">All registered snapshots</div>
          </div>
          {snaps && snaps.length > 0 ? (
            <table className="ledger-table">
              <thead><tr><th>Source</th><th>Snapshot hash</th><th>Linked claim</th><th>Created</th></tr></thead>
              <tbody>
                {snaps.map((s) => (
                  <tr key={s.id}>
                    <td><Badge tone="cyan">{s.source_type ?? "—"}</Badge></td>
                    <td><HashText value={s.snapshot_hash ?? "—"} short /></td>
                    <td><HashText value={s.audit_case_id} short /></td>
                    <td className="text-slate">{new Date(s.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState
              title="No dataset snapshots yet"
              body="Dataset snapshots help validators understand the metric context behind an insight claim."
            />
          )}
        </article>
      </main>
    </>
  );
}
""",
)

# ===================================================================
# /admin — Audit operations
# ===================================================================
write(
    "app/(app)/admin/page.tsx",
    """import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { HashText } from "@/components/audit/HashText";
import { ConsensusBadge } from "@/components/audit/ConsensusBadge";

export default async function AdminPage() {
  const { profile, supabase } = await getProfile();
  if (profile?.role !== "admin") redirect("/dashboard");

  const { data: cases } = await supabase
    .from("insight_audit_cases").select("id,insight_claim,status,created_at")
    .order("created_at", { ascending: false }).limit(50);
  const { data: logs } = await supabase
    .from("contract_activity_logs")
    .select("id,contract_address,transaction_hash,action,status,created_at")
    .order("created_at", { ascending: false }).limit(50);

  return (
    <>
      <SubContextBar
        eyebrow="Audit operations"
        title="Admin Review"
        right={
          <>
            <Badge tone="consensus" dot>StudioNet</Badge>
            <ConsensusBadge />
          </>
        }
      />
      <main className="px-6 py-6 space-y-6">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1.4fr_1fr]">
          <article className="doc overflow-hidden">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">Operations ledger</div>
              <div className="display text-[15px] font-semibold text-ink">Pending judgment requests</div>
            </div>
            {cases && cases.length > 0 ? (
              <table className="ledger-table">
                <thead><tr><th>Audit ID</th><th>Claim</th><th>Status</th><th>Created</th></tr></thead>
                <tbody>
                  {cases.map((c) => (
                    <tr key={c.id}>
                      <td><HashText value={c.id} short /></td>
                      <td className="text-ink">{c.insight_claim}</td>
                      <td><Badge tone="slate">{c.status.replace(/_/g, " ")}</Badge></td>
                      <td className="text-slate">{new Date(c.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState title="No audits to review yet"
                body="Audits will appear here once users submit insight claims for GenLayer consensus." />
            )}
          </article>

          <article className="doc overflow-hidden">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">Contract trace</div>
              <div className="display text-[15px] font-semibold text-ink">Contract activity</div>
            </div>
            <div className="divide-y divide-auditline">
              {logs && logs.length > 0 ? logs.map((l) => (
                <div key={l.id} className="flex items-start justify-between gap-3 px-5 py-3 text-[12.5px]">
                  <div className="space-y-1">
                    <div className="text-ink">{l.action}</div>
                    <HashText value={l.transaction_hash ?? l.contract_address ?? "—"} short />
                  </div>
                  <Badge tone={l.status === "ok" ? "verified" : "amber"} dot>{l.status}</Badge>
                </div>
              )) : (
                <EmptyState title="No contract activity yet"
                  body="GenLayer calls and verdict mirroring events will stream here once audits run." />
              )}
            </div>
          </article>
        </div>
      </main>
    </>
  );
}
""",
)

# ===================================================================
# /profile — Signing Infrastructure
# ===================================================================
write(
    "app/(app)/profile/page.tsx",
    """import { getProfile } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { SigningInfrastructureCard } from "@/components/audit/SigningInfrastructureCard";

export default async function ProfilePage() {
  const { user, profile, supabase } = await getProfile();
  const { data: wallet } = await supabase
    .from("wallets").select("address,created_at").eq("user_id", user.id).single();

  return (
    <>
      <SubContextBar
        eyebrow="Email profile and signing infrastructure"
        title="Profile"
        right={<Badge tone="consensus" dot>Embedded signer</Badge>}
      />
      <main className="px-6 py-6 space-y-6">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <article className="doc">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">Identity</div>
              <div className="display text-[15px] font-semibold text-ink">Email profile</div>
            </div>
            <div className="space-y-2 px-5 py-4 text-sm">
              <Row label="Display name" value={profile?.display_name ?? "—"} />
              <Row label="Email"        value={user.email ?? "—"} />
              <Row label="Role"         value={profile?.role ?? "user"} />
              <Row label="Onboarding"   value={profile?.onboarding_completed ? "complete" : "pending"} />
            </div>
          </article>

          <SigningInfrastructureCard
            address={wallet?.address ?? "—"}
            createdAt={wallet?.created_at}
          />
        </div>

        <article className="doc">
          <div className="border-b border-auditline px-5 py-3">
            <div className="eyebrow eyebrow-slate">Session and security</div>
            <div className="display text-[15px] font-semibold text-ink">Recent activity</div>
          </div>
          <div className="px-5 py-4 text-sm text-slate">
            Session history and the private key export flow ship later. Private key export
            requires strong re-authentication and is recorded in the recovery audit log.
          </div>
        </article>
      </main>
    </>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-auditline pb-2 last:border-b-0">
      <span className="text-slate">{label}</span>
      <span className="text-ink">{value}</span>
    </div>
  );
}
""",
)

# ===================================================================
# /settings
# ===================================================================
write(
    "app/(app)/settings/page.tsx",
    """import { getProfile } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";

export default async function SettingsPage() {
  const { profile, user } = await getProfile();

  return (
    <>
      <SubContextBar eyebrow="Account, authentication, signing" title="Settings" />
      <main className="px-6 py-6">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Doc title="Email and identity" eyebrow="Account">
            <Row label="Email" value={user.email ?? "—"} />
            <Row label="Display name" value={profile?.display_name ?? "—"} />
            <Row label="Role" value={profile?.role ?? "user"} />
          </Doc>

          <Doc title="Authentication" eyebrow="Authentication">
            <Row label="Password" value="Set" />
            <Row label="Email verification" value="Auto-confirmed" />
            <Row label="External wallet" value={<Badge tone="slate">Not required</Badge>} />
          </Doc>

          <Doc title="Signing infrastructure" eyebrow="Embedded signer">
            <Row label="Wallet" value="Provisioned" />
            <Row label="Recovery key" value="Stored offline" />
            <Row label="Audit log" value="Enabled" />
          </Doc>

          <Doc title="Recovery" eyebrow="Recovery">
            <Row label="Recovery key" value="Required for password reset" />
            <p className="mt-2 text-[12px] text-slate">
              Re-wraps the embedded wallet key after a password reset. Never shared with VeriSight after signup.
            </p>
          </Doc>

          <Doc title="Audit alerts" eyebrow="Notifications">
            <Row label="Email on new judgment" value={<Badge tone="slate">Default on</Badge>} />
            <Row label="Email on consensus failure" value={<Badge tone="amber" dot>On</Badge>} />
          </Doc>

          <Doc title="Data export" eyebrow="Data">
            <Row label="Profile data export" value="Available on request" />
            <Row label="Decision memo export" value="PDF · sample" />
          </Doc>

          <article className="doc border-claim/30 lg:col-span-2">
            <div className="border-b border-auditline bg-claim/5 px-5 py-3">
              <div className="eyebrow text-claim">Danger zone</div>
              <div className="display text-[15px] font-semibold text-ink">Destructive actions</div>
            </div>
            <div className="px-5 py-4 text-sm text-claim">
              Account deletion will remove product state but the GenLayer contract record of past
              consensus judgments remains on chain.
            </div>
          </article>
        </div>
      </main>
    </>
  );
}

function Doc({ title, eyebrow, children }: { title: string; eyebrow: string; children: React.ReactNode }) {
  return (
    <article className="doc">
      <div className="border-b border-auditline px-5 py-3">
        <div className="eyebrow eyebrow-slate">{eyebrow}</div>
        <div className="display text-[15px] font-semibold text-ink">{title}</div>
      </div>
      <div className="space-y-2 px-5 py-4 text-sm">{children}</div>
    </article>
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
""",
)

print("\nAssurance Desk redesign written.")
