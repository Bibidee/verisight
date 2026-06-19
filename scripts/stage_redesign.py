"""Insight Assurance OS — full UI redesign.

Rewrites tailwind config, globals.css, UI primitives, app shell components,
and every existing page. Adds on-design placeholder pages for routes that
will be built in later stages (audits, evidence, snapshots, admin, profile,
settings) so the audit-rail navigation works end to end.

No product logic is changed.
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
# tailwind.config.ts — new colour tokens
# ===================================================================
write(
    "tailwind.config.ts",
    """import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Dark surfaces
        "audit-black": "#080A0F",
        "graphite-blue": "#0F172A",
        // Light surfaces
        "ledger-mist": "#F5F7FA",
        "white-ledger": "#FFFFFF",
        "blue-steel": "#EAF0F8",
        // Brand + signal
        "exec-blue": "#1D4ED8",
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
        auditline: "#DDE3EA",
        "glass-grid": "rgba(148,163,184,0.22)",
      },
      fontFamily: {
        display: ["var(--font-space-grotesk)", "system-ui", "sans-serif"],
        body: ["var(--font-manrope)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: { btn: "8px", panel: "14px" },
      fontSize: {
        hero: ["68px", { lineHeight: "1.04", letterSpacing: "-0.025em" }],
        pagetitle: ["42px", { lineHeight: "1.08", letterSpacing: "-0.015em" }],
        section: ["26px", { lineHeight: "1.2", letterSpacing: "-0.005em" }],
        cardtitle: ["19px", { lineHeight: "1.3" }],
      },
      boxShadow: {
        panel: "0 1px 0 rgba(15,23,42,0.04), 0 8px 24px -16px rgba(15,23,42,0.12)",
        rail: "inset -1px 0 0 rgba(148,163,184,0.18)",
        glow: "0 0 0 1px rgba(124,58,237,0.45), 0 0 32px -4px rgba(124,58,237,0.35)",
      },
      keyframes: {
        pulseDot: {
          "0%,100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.4", transform: "scale(0.85)" },
        },
        gridPan: {
          "0%": { backgroundPosition: "0 0" },
          "100%": { backgroundPosition: "40px 40px" },
        },
      },
      animation: {
        pulseDot: "pulseDot 1.6s ease-in-out infinite",
        gridPan: "gridPan 22s linear infinite",
      },
    },
  },
  plugins: [],
};
export default config;
""",
)

# ===================================================================
# app/globals.css — full system
# ===================================================================
write(
    "app/globals.css",
    """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --audit-black: #080A0F;
  --graphite-blue: #0F172A;
  --ledger-mist: #F5F7FA;
  --white-ledger: #FFFFFF;
  --blue-steel: #EAF0F8;
  --exec-blue: #1D4ED8;
  --data-cyan: #06B6D4;
  --amber: #F59E0B;
  --claim: #DC2626;
  --emerald: #059669;
  --consensus: #7C3AED;
  --ink: #0F172A;
  --ledger-white: #F8FAFC;
  --slate: #64748B;
  --auditline: #DDE3EA;
  --glass-grid: rgba(148, 163, 184, 0.22);
}

html, body {
  background: var(--ledger-mist);
  color: var(--ink);
  font-family: var(--font-manrope), system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.display { font-family: var(--font-space-grotesk), system-ui, sans-serif; letter-spacing: -0.01em; }
.mono { font-family: var(--font-jetbrains-mono), ui-monospace, monospace; font-feature-settings: "ss01","ss02"; }

/* ---------------- BUTTONS ---------------- */
.btn-primary {
  background: var(--audit-black); color: #fff;
  border-radius: 8px; padding: 10px 16px;
  font-weight: 600; font-size: 14px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 1px 0 rgba(15,23,42,0.06);
  transition: transform .05s ease, opacity .15s ease, box-shadow .2s ease;
  display: inline-flex; align-items: center; gap: 8px;
}
.btn-primary:hover { opacity: .94; }
.btn-primary:active { transform: translateY(1px); }

.btn-secondary {
  background: var(--white-ledger); color: var(--ink);
  border: 1px solid var(--auditline); border-radius: 8px;
  padding: 9px 14px; font-weight: 600; font-size: 14px;
  display: inline-flex; align-items: center; gap: 8px;
  transition: border-color .15s ease, background .15s ease;
}
.btn-secondary:hover { border-color: #C5CED9; background: var(--ledger-mist); }

.btn-exec {
  background: var(--exec-blue); color: #fff;
  border-radius: 8px; padding: 10px 16px;
  font-weight: 600; font-size: 14px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.16);
  display: inline-flex; align-items: center; gap: 8px;
}
.btn-exec:hover { background: #1A45C2; }

.btn-consensus {
  background: var(--consensus); color: #fff;
  border-radius: 8px; padding: 10px 16px;
  font-weight: 600; font-size: 14px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.16), 0 0 0 0 rgba(124,58,237,0);
  display: inline-flex; align-items: center; gap: 8px;
  transition: box-shadow .25s ease, background .15s ease;
}
.btn-consensus:hover { background: #6A30D6; box-shadow: 0 0 0 4px rgba(124,58,237,0.15); }

.btn-danger {
  background: var(--claim); color: #fff;
  border-radius: 8px; padding: 10px 16px;
  font-weight: 600; font-size: 14px;
}

.btn-ghost {
  background: transparent; color: var(--ink);
  border: 1px dashed var(--auditline); border-radius: 8px;
  padding: 9px 14px; font-weight: 500; font-size: 13px;
}

/* ---------------- PANELS ---------------- */
.panel {
  background: var(--white-ledger);
  border: 1px solid var(--auditline);
  border-radius: 14px;
  box-shadow: 0 1px 0 rgba(15,23,42,0.04), 0 8px 24px -16px rgba(15,23,42,0.12);
}
.panel-dark {
  background: var(--graphite-blue); color: var(--ledger-white);
  border: 1px solid var(--glass-grid);
  border-radius: 14px;
}
.panel-darker {
  background: var(--audit-black); color: var(--ledger-white);
  border: 1px solid var(--glass-grid);
  border-radius: 14px;
}
.panel-steel {
  background: var(--blue-steel); color: var(--ink);
  border: 1px solid var(--auditline);
  border-radius: 14px;
}
.panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px; border-bottom: 1px solid var(--auditline);
}
.panel-header.dark { border-bottom-color: var(--glass-grid); }

.eyebrow {
  font-family: var(--font-jetbrains-mono), ui-monospace, monospace;
  font-size: 10.5px; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--consensus);
}
.eyebrow-slate { color: var(--slate); }

/* ---------------- BADGES ---------------- */
.badge {
  display: inline-flex; align-items: center; gap: 6px;
  border-radius: 999px; padding: 3px 10px;
  font-size: 11.5px; font-weight: 600; letter-spacing: 0.02em;
  border: 1px solid transparent;
}
.badge-consensus { background: rgba(124,58,237,0.10); color: var(--consensus); border-color: rgba(124,58,237,0.30); }
.badge-verified  { background: rgba(5,150,105,0.10);  color: var(--emerald);  border-color: rgba(5,150,105,0.30); }
.badge-amber     { background: rgba(245,158,11,0.10); color: var(--amber);    border-color: rgba(245,158,11,0.32); }
.badge-claim     { background: rgba(220,38,38,0.10);  color: var(--claim);    border-color: rgba(220,38,38,0.32); }
.badge-cyan      { background: rgba(6,182,212,0.10);  color: var(--data-cyan);border-color: rgba(6,182,212,0.32); }
.badge-blue      { background: rgba(29,78,216,0.10);  color: var(--exec-blue);border-color: rgba(29,78,216,0.32); }
.badge-slate     { background: rgba(100,116,139,0.10);color: var(--slate);    border-color: rgba(100,116,139,0.28); }
.badge-dark      { background: rgba(248,250,252,0.07);color: var(--ledger-white); border-color: var(--glass-grid); }

/* ---------------- INPUTS ---------------- */
.input {
  width: 100%; border-radius: 8px;
  border: 1px solid var(--auditline); background: var(--white-ledger);
  padding: 10px 12px; font-size: 14px; color: var(--ink);
  transition: border-color .15s ease, box-shadow .15s ease;
}
.input::placeholder { color: var(--slate); }
.input:focus {
  outline: none; border-color: var(--exec-blue);
  box-shadow: 0 0 0 3px rgba(29,78,216,0.15);
}

/* ---------------- GRID BACKDROP ---------------- */
.grid-backdrop {
  background-image:
    linear-gradient(to right, rgba(148,163,184,0.10) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(148,163,184,0.10) 1px, transparent 1px);
  background-size: 40px 40px;
}
.grid-backdrop-dark {
  background-image:
    linear-gradient(to right, rgba(148,163,184,0.08) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(148,163,184,0.08) 1px, transparent 1px);
  background-size: 40px 40px;
}

/* ---------------- TABLES (LEDGER ROWS) ---------------- */
.ledger-table { width: 100%; font-size: 14px; }
.ledger-table thead th {
  text-align: left; padding: 10px 18px;
  font-size: 11px; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--slate);
  background: var(--ledger-mist); border-bottom: 1px solid var(--auditline);
}
.ledger-table tbody td { padding: 14px 18px; border-top: 1px solid var(--auditline); }
.ledger-table tbody tr:hover { background: var(--ledger-mist); }

/* ---------------- STATUS DOTS ---------------- */
.dot { width: 8px; height: 8px; border-radius: 999px; display: inline-block; }
.dot-consensus { background: var(--consensus); box-shadow: 0 0 0 4px rgba(124,58,237,0.18); animation: pulseDot 1.6s ease-in-out infinite; }
.dot-verified  { background: var(--emerald); }
.dot-amber     { background: var(--amber); }
.dot-claim     { background: var(--claim); }
.dot-cyan      { background: var(--data-cyan); box-shadow: 0 0 0 4px rgba(6,182,212,0.18); animation: pulseDot 1.6s ease-in-out infinite; }
.dot-slate     { background: var(--slate); }

/* ---------------- METER BARS ---------------- */
.meter { height: 6px; border-radius: 999px; background: var(--auditline); overflow: hidden; }
.meter > .fill { height: 100%; border-radius: 999px; }

/* ---------------- HASH TEXT ---------------- */
.hash {
  font-family: var(--font-jetbrains-mono), ui-monospace, monospace;
  font-size: 12px; color: var(--ink);
  background: var(--ledger-mist); border: 1px solid var(--auditline);
  border-radius: 6px; padding: 2px 7px;
  word-break: break-all;
}
.hash-dark {
  font-family: var(--font-jetbrains-mono), ui-monospace, monospace;
  font-size: 12px; color: var(--ledger-white);
  background: rgba(248,250,252,0.06); border: 1px solid var(--glass-grid);
  border-radius: 6px; padding: 2px 7px; word-break: break-all;
}

/* ---------------- LINKS ---------------- */
.link { color: var(--exec-blue); text-decoration: underline; text-underline-offset: 3px; }
.link:hover { color: #1A45C2; }
""",
)

# ===================================================================
# app/layout.tsx — keep fonts wiring (already correct)
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
  title: "VeriSight — Insight Assurance OS",
  description:
    "Verify whether dashboard insights and AI-generated report narratives are actually supported by the underlying data. Adjudicated by GenLayer validator consensus.",
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
# components/ui primitives
# ===================================================================
write(
    "components/ui/Button.tsx",
    """import { ButtonHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

type Variant = "primary" | "secondary" | "exec" | "consensus" | "danger" | "ghost";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

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
  return (
    <button
      ref={ref}
      className={clsx(variantClass[variant], "disabled:opacity-60", className)}
      {...rest}
    />
  );
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
    "components/ui/Label.tsx",
    """import { LabelHTMLAttributes } from "react";
import clsx from "clsx";

export function Label({ className, ...rest }: LabelHTMLAttributes<HTMLLabelElement>) {
  return (
    <label
      className={clsx("text-[11px] font-semibold uppercase tracking-[0.08em] text-slate", className)}
      {...rest}
    />
  );
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
  title,
  eyebrow,
  right,
  tone = "light",
}: {
  title: string;
  eyebrow?: string;
  right?: React.ReactNode;
  tone?: "light" | "dark";
}) {
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

write(
    "components/ui/Field.tsx",
    """import { ReactNode } from "react";

export function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
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

# ===================================================================
# components/audit/* — primitives for the insight assurance OS
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

export function Badge({
  tone = "slate",
  children,
  className,
  dot,
}: {
  tone?: Tone;
  children: ReactNode;
  className?: string;
  dot?: boolean;
}) {
  const dotClass: Record<Tone, string> = {
    consensus: "dot dot-consensus",
    verified: "dot dot-verified",
    amber: "dot dot-amber",
    claim: "dot dot-claim",
    cyan: "dot dot-cyan",
    blue: "dot dot-cyan",
    slate: "dot dot-slate",
    dark: "dot dot-slate",
  };
  return (
    <span className={clsx("badge", toneClass[tone], className)}>
      {dot ? <span className={dotClass[tone]} /> : null}
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
  value,
  short,
  dark,
  className,
}: {
  value: string;
  short?: boolean;
  dark?: boolean;
  className?: string;
}) {
  const display =
    short && value.length > 14 ? `${value.slice(0, 8)}…${value.slice(-6)}` : value;
  return <span className={clsx(dark ? "hash-dark" : "hash", className)}>{display}</span>;
}
""",
)

write(
    "components/audit/Meter.tsx",
    """import clsx from "clsx";

const fill: Record<"emerald" | "amber" | "claim" | "blue" | "cyan" | "consensus", string> = {
  emerald: "bg-emerald",
  amber: "bg-amber",
  claim: "bg-claim",
  blue: "bg-exec-blue",
  cyan: "bg-data-cyan",
  consensus: "bg-consensus",
};

export function Meter({
  value,
  tone = "blue",
  className,
}: {
  value: number; // 0..100
  tone?: keyof typeof fill;
  className?: string;
}) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className={clsx("meter", className)}>
      <div className={clsx("fill", fill[tone])} style={{ width: `${clamped}%` }} />
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

export function ConsensusBadge({
  state = "reached",
}: {
  state?: "reached" | "pending" | "failed";
}) {
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
  | "supported"
  | "partially_supported"
  | "unsupported"
  | "misleading"
  | "needs_more_evidence";

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

export function RiskBadge({
  level = "moderate",
}: {
  level?: "low" | "moderate" | "high";
}) {
  if (level === "high") return <Badge tone="claim" dot>High business risk</Badge>;
  if (level === "low") return <Badge tone="verified" dot>Low business risk</Badge>;
  return <Badge tone="amber" dot>Moderate business risk</Badge>;
}
""",
)

write(
    "components/audit/EmptyState.tsx",
    """import { ReactNode } from "react";

export function EmptyState({
  title,
  body,
  action,
}: {
  title: string;
  body: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center gap-3 px-6 py-14 text-center">
      <div className="grid h-12 w-12 place-items-center rounded-full border border-auditline bg-blue-steel">
        <span className="dot dot-cyan" />
      </div>
      <div className="display text-cardtitle font-semibold text-ink">{title}</div>
      <p className="max-w-md text-sm text-slate">{body}</p>
      {action ? <div className="mt-2">{action}</div> : null}
    </div>
  );
}
""",
)

write(
    "components/audit/InsightVerdictPanel.tsx",
    """import { Panel } from "@/components/ui/Panel";
import { Badge } from "./Badge";
import { ConsensusBadge } from "./ConsensusBadge";
import { SourceOfTruthBadge } from "./SourceOfTruthBadge";
import { SupportBadge, Verdict } from "./SupportBadge";

export function InsightVerdictPanel({
  claim = "Revenue growth was mainly driven by repeat customers.",
  verdict = "partially_supported",
  supportLevel = "Moderate",
  businessRisk = "Claim may overstate causality",
  reasoning = "Repeat customer revenue increased, but new customer revenue, discount effects, and segment mix were not sufficiently controlled.",
  demo = false,
}: {
  claim?: string;
  verdict?: Verdict;
  supportLevel?: string;
  businessRisk?: string;
  reasoning?: string;
  demo?: boolean;
}) {
  return (
    <Panel className="overflow-hidden">
      <div className="grid grid-cols-1 lg:grid-cols-[1.4fr_1fr]">
        <div className="border-b border-auditline p-6 lg:border-b-0 lg:border-r">
          <div className="flex items-center justify-between">
            <span className="eyebrow">Insight verdict</span>
            {demo ? <Badge tone="slate">Demo</Badge> : null}
          </div>
          <div className="display mt-3 text-section font-semibold text-ink">
            {claim}
          </div>
          <p className="mt-3 text-sm text-slate">{reasoning}</p>
          <div className="mt-5 flex flex-wrap gap-2">
            <SupportBadge verdict={verdict} />
            <Badge tone="amber" dot>Risk · {businessRisk}</Badge>
          </div>
        </div>
        <div className="bg-blue-steel p-6">
          <div className="eyebrow eyebrow-slate">Adjudication</div>
          <div className="mt-3 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate">Support level</span>
              <span className="display text-cardtitle font-semibold">{supportLevel}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate">Consensus</span>
              <ConsensusBadge />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate">Source of truth</span>
              <SourceOfTruthBadge small />
            </div>
          </div>
        </div>
      </div>
    </Panel>
  );
}
""",
)

# ===================================================================
# components/app — Audit Command Shell
# ===================================================================
write(
    "components/app/AuditRail.tsx",
    """"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";

const links = [
  { href: "/dashboard",  label: "Dashboard",        icon: GridIcon },
  { href: "/workspaces", label: "Workspaces",       icon: StackIcon },
  { href: "/audits",     label: "Insight Audits",   icon: LensIcon },
  { href: "/evidence",   label: "Evidence Ledger",  icon: LedgerIcon },
  { href: "/snapshots",  label: "Dataset Snapshots",icon: SnapIcon },
  { href: "/verdicts",   label: "Verdicts",         icon: SealIcon },
  { href: "/admin",      label: "Admin",            icon: ShieldIcon },
  { href: "/profile",    label: "Profile",          icon: UserIcon },
  { href: "/settings",   label: "Settings",         icon: GearIcon },
];

export function AuditRail({ email, displayName }: { email: string; displayName?: string | null }) {
  const path = usePathname();
  return (
    <aside className="hidden h-screen w-[252px] shrink-0 flex-col border-r border-glass-grid bg-graphite-blue text-ledger-white lg:flex">
      <div className="px-5 pt-6">
        <Link href="/dashboard" className="flex items-center gap-2.5">
          <LogoMark />
          <div>
            <div className="display text-[15px] font-semibold leading-tight">VeriSight</div>
            <div className="mono text-[9.5px] uppercase tracking-[0.22em] text-consensus">
              Insight Assurance OS
            </div>
          </div>
        </Link>
      </div>

      <nav className="mt-6 flex-1 px-2">
        {links.map((l) => {
          const active = path === l.href || path.startsWith(l.href + "/");
          const Icon = l.icon;
          return (
            <Link
              key={l.href}
              href={l.href}
              className={clsx(
                "group mb-0.5 flex items-center gap-2.5 rounded-btn px-3 py-2 text-[13px] transition-colors",
                active
                  ? "bg-white/10 text-ledger-white"
                  : "text-ledger-white/70 hover:bg-white/[0.04] hover:text-ledger-white",
              )}
            >
              <Icon className={clsx("h-4 w-4", active ? "text-data-cyan" : "text-ledger-white/55")} />
              <span>{l.label}</span>
              {active ? <span className="dot dot-cyan ml-auto" /> : null}
            </Link>
          );
        })}
      </nav>

      <div className="px-3 pb-3">
        <div className="rounded-panel border border-glass-grid bg-white/[0.03] p-3">
          <div className="flex items-center gap-2">
            <span className="dot dot-consensus" />
            <span className="mono text-[10.5px] uppercase tracking-[0.18em] text-consensus">
              GenLayer · StudioNet
            </span>
          </div>
          <div className="mt-1.5 text-[11.5px] text-ledger-white/65">
            Validator consensus operational
          </div>
        </div>

        <div className="mt-3 flex items-center gap-2.5 rounded-panel border border-glass-grid bg-white/[0.03] p-3">
          <div className="grid h-8 w-8 place-items-center rounded-full bg-exec-blue text-[12px] font-semibold text-ledger-white">
            {(displayName ?? email).slice(0, 1).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <div className="truncate text-[12.5px] font-medium text-ledger-white">
              {displayName ?? email}
            </div>
            <div className="truncate text-[10.5px] text-ledger-white/55">{email}</div>
          </div>
        </div>
      </div>
    </aside>
  );
}

function LogoMark() {
  return (
    <svg viewBox="0 0 32 32" className="h-8 w-8" aria-hidden>
      <defs>
        <linearGradient id="vsg" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stopColor="#06B6D4" />
          <stop offset="1" stopColor="#7C3AED" />
        </linearGradient>
      </defs>
      <rect x="1.5" y="1.5" width="29" height="29" rx="8" fill="#0F172A" stroke="url(#vsg)" />
      <g stroke="#06B6D4" strokeWidth="1.1" opacity="0.55">
        <line x1="6" y1="11" x2="26" y2="11" />
        <line x1="6" y1="16" x2="26" y2="16" />
        <line x1="6" y1="21" x2="26" y2="21" />
      </g>
      <path d="M10 18 L14 22 L23 12" stroke="#7C3AED" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="23" cy="12" r="1.8" fill="#7C3AED" />
    </svg>
  );
}

type IconProps = { className?: string };
function GridIcon({ className }: IconProps) {
  return <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor" strokeWidth="1.4"><rect x="2" y="2" width="5" height="5"/><rect x="9" y="2" width="5" height="5"/><rect x="2" y="9" width="5" height="5"/><rect x="9" y="9" width="5" height="5"/></svg>;
}
function StackIcon({ className }: IconProps) {
  return <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor" strokeWidth="1.4"><path d="M8 2 L14 5 L8 8 L2 5 Z"/><path d="M2 9 L8 12 L14 9"/><path d="M2 12 L8 15 L14 12"/></svg>;
}
function LensIcon({ className }: IconProps) {
  return <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor" strokeWidth="1.4"><circle cx="7" cy="7" r="4.5"/><line x1="10.5" y1="10.5" x2="14" y2="14"/></svg>;
}
function LedgerIcon({ className }: IconProps) {
  return <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor" strokeWidth="1.4"><rect x="3" y="2" width="10" height="12"/><line x1="5.5" y1="5" x2="11" y2="5"/><line x1="5.5" y1="8" x2="11" y2="8"/><line x1="5.5" y1="11" x2="9" y2="11"/></svg>;
}
function SnapIcon({ className }: IconProps) {
  return <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor" strokeWidth="1.4"><rect x="2" y="3" width="12" height="10" rx="1"/><path d="M2 9 L6 6 L9 9 L11 7.5 L14 10"/></svg>;
}
function SealIcon({ className }: IconProps) {
  return <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor" strokeWidth="1.4"><circle cx="8" cy="7" r="4"/><path d="M5.5 10 L5 14 L8 12 L11 14 L10.5 10"/></svg>;
}
function ShieldIcon({ className }: IconProps) {
  return <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor" strokeWidth="1.4"><path d="M8 2 L13 4 V8 C13 11 11 13 8 14 C5 13 3 11 3 8 V4 Z"/></svg>;
}
function UserIcon({ className }: IconProps) {
  return <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor" strokeWidth="1.4"><circle cx="8" cy="6" r="2.6"/><path d="M3 14 C3.8 11 6 10 8 10 C10 10 12.2 11 13 14"/></svg>;
}
function GearIcon({ className }: IconProps) {
  return <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor" strokeWidth="1.4"><circle cx="8" cy="8" r="2.4"/><path d="M8 1.5 V3.5 M8 12.5 V14.5 M1.5 8 H3.5 M12.5 8 H14.5 M3.5 3.5 L4.9 4.9 M11.1 11.1 L12.5 12.5 M3.5 12.5 L4.9 11.1 M11.1 4.9 L12.5 3.5"/></svg>;
}
""",
)

write(
    "components/app/WorkspaceContextBar.tsx",
    """import Link from "next/link";
import { logoutAction } from "@/lib/auth/actions";
import { Badge } from "@/components/audit/Badge";

export function WorkspaceContextBar({
  sectionTitle,
  workspaceName,
  activeAuditCount = 0,
}: {
  sectionTitle: string;
  workspaceName?: string | null;
  activeAuditCount?: number;
}) {
  return (
    <header className="sticky top-0 z-20 border-b border-auditline bg-white-ledger/85 backdrop-blur">
      <div className="flex items-center justify-between gap-4 px-6 py-3">
        <div className="flex items-center gap-4 min-w-0">
          <div className="min-w-0">
            <div className="eyebrow eyebrow-slate">Audit terminal</div>
            <div className="display truncate text-cardtitle font-semibold text-ink">
              {sectionTitle}
            </div>
          </div>
          <div className="hidden h-7 w-px bg-auditline md:block" />
          <div className="hidden items-center gap-2 md:flex">
            <Badge tone="blue" dot>{workspaceName ?? "No workspace selected"}</Badge>
            <Badge tone="cyan" dot>Datasets fresh</Badge>
            <Badge tone="slate">{activeAuditCount} active audits</Badge>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/audits/new" className="btn-primary">
            <span className="dot dot-cyan" />
            Audit an insight
          </Link>
          <form action={logoutAction}>
            <button type="submit" className="btn-secondary">Sign out</button>
          </form>
        </div>
      </div>
    </header>
  );
}
""",
)

write(
    "components/app/InspectionDrawer.tsx",
    """import { ReactNode } from "react";

export function InspectionDrawer({
  title,
  eyebrow = "Inspection",
  children,
}: {
  title: string;
  eyebrow?: string;
  children: ReactNode;
}) {
  return (
    <aside className="hidden w-[320px] shrink-0 border-l border-glass-grid bg-graphite-blue text-ledger-white xl:block">
      <div className="px-5 py-4 border-b border-glass-grid">
        <div className="eyebrow">{eyebrow}</div>
        <div className="display mt-1 text-cardtitle font-semibold">{title}</div>
      </div>
      <div className="px-5 py-4 space-y-4">{children}</div>
    </aside>
  );
}
""",
)

# ===================================================================
# Marketing logo mark (reusable on landing/auth)
# ===================================================================
write(
    "components/app/LogoMark.tsx",
    """export function LogoMark({ size = 36 }: { size?: number }) {
  return (
    <svg viewBox="0 0 32 32" width={size} height={size} aria-hidden>
      <defs>
        <linearGradient id="vsg-mark" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stopColor="#06B6D4" />
          <stop offset="1" stopColor="#7C3AED" />
        </linearGradient>
      </defs>
      <rect x="1.5" y="1.5" width="29" height="29" rx="8" fill="#0F172A" stroke="url(#vsg-mark)" />
      <g stroke="#06B6D4" strokeWidth="1.1" opacity="0.55">
        <line x1="6" y1="11" x2="26" y2="11" />
        <line x1="6" y1="16" x2="26" y2="16" />
        <line x1="6" y1="21" x2="26" y2="21" />
      </g>
      <path d="M10 18 L14 22 L23 12" stroke="#7C3AED" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="23" cy="12" r="1.8" fill="#7C3AED" />
    </svg>
  );
}
""",
)

# ===================================================================
# Landing page — premium dark hero with audit terminal mockup
# ===================================================================
write(
    "app/page.tsx",
    """import Link from "next/link";
import { LogoMark } from "@/components/app/LogoMark";
import { Badge } from "@/components/audit/Badge";
import { SupportBadge } from "@/components/audit/SupportBadge";
import { ConsensusBadge } from "@/components/audit/ConsensusBadge";
import { SourceOfTruthBadge } from "@/components/audit/SourceOfTruthBadge";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-audit-black text-ledger-white">
      <div className="relative isolate overflow-hidden">
        <div className="absolute inset-0 grid-backdrop-dark opacity-60" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-audit-black" />

        {/* nav */}
        <header className="relative z-10">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
            <Link href="/" className="flex items-center gap-2.5">
              <LogoMark />
              <div>
                <div className="display text-[16px] font-semibold leading-tight">VeriSight</div>
                <div className="mono text-[10px] uppercase tracking-[0.22em] text-consensus">
                  Insight Assurance OS
                </div>
              </div>
            </Link>
            <nav className="flex items-center gap-2">
              <Link href="/login" className="btn-secondary">Sign in</Link>
              <Link href="/signup" className="btn-consensus">Create account</Link>
            </nav>
          </div>
        </header>

        {/* hero */}
        <section className="relative z-10 mx-auto grid max-w-7xl grid-cols-1 gap-10 px-6 pb-16 pt-12 lg:grid-cols-[1.05fr_1fr] lg:gap-12 lg:pb-24 lg:pt-20">
          <div>
            <div className="flex items-center gap-2">
              <SourceOfTruthBadge />
              <Badge tone="cyan" dot>GenLayer StudioNet</Badge>
            </div>
            <h1 className="display mt-6 text-[58px] font-semibold leading-[1.02] tracking-[-0.025em] sm:text-hero">
              Before an insight<br/>becomes a decision,<br/>
              <span className="text-data-cyan">verify it.</span>
            </h1>
            <p className="mt-6 max-w-xl text-[15px] leading-relaxed text-ledger-white/70">
              VeriSight is the Insight Assurance OS for business analytics. It verifies whether
              dashboard insights, KPI narratives, and AI-generated report summaries are actually
              supported by the underlying data — adjudicated by GenLayer validator consensus.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/signup" className="btn-consensus">
                <span className="dot bg-white" /> Audit an insight
              </Link>
              <Link href="/login" className="btn-secondary bg-white/5 text-ledger-white border-glass-grid hover:bg-white/10">
                View demo verdict
              </Link>
            </div>
            <div className="mono mt-10 grid max-w-md grid-cols-3 gap-3 text-[10.5px] uppercase tracking-[0.16em] text-ledger-white/55">
              <div>· Email auth</div>
              <div>· Embedded wallet</div>
              <div>· Consensus verdict</div>
            </div>
          </div>

          {/* floating audit terminal */}
          <div className="relative">
            <div className="absolute -inset-6 rounded-[28px] bg-gradient-to-tr from-consensus/20 via-exec-blue/10 to-transparent blur-2xl" />
            <div className="relative rounded-panel border border-glass-grid bg-graphite-blue/90 p-5 backdrop-blur shadow-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="dot dot-consensus" />
                  <span className="mono text-[10.5px] uppercase tracking-[0.18em] text-consensus">
                    Consensus audit terminal
                  </span>
                </div>
                <span className="mono text-[10.5px] text-ledger-white/55">audit-7f3e</span>
              </div>
              <div className="display mt-4 text-[18px] font-semibold leading-snug">
                Revenue growth was mainly driven by repeat customers.
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <Badge tone="dark">Q3 — North America</Badge>
                <Badge tone="dark">Quarterly revenue by customer type</Badge>
              </div>

              <div className="mt-5 grid grid-cols-2 gap-3 text-[12.5px]">
                <Tile label="Evidence" value="Dataset · Report PDF" />
                <Tile label="Support level" value="Moderate" tone="amber" />
                <Tile label="Validators" value="Reasoned + reviewed" />
                <Tile label="GenLayer status" value="Consensus reached" tone="consensus" />
              </div>

              <div className="mt-5 rounded-panel border border-glass-grid bg-white/[0.04] p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
                      Verdict
                    </div>
                    <div className="display mt-1 text-[18px] font-semibold">Partially supported</div>
                  </div>
                  <SupportBadge verdict="partially_supported" />
                </div>
                <div className="mt-3 flex items-center justify-between text-[12.5px] text-ledger-white/70">
                  <span>Business risk</span>
                  <Badge tone="amber" dot>Claim may overstate causality</Badge>
                </div>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-[12.5px] text-ledger-white/70">Consensus</span>
                  <ConsensusBadge />
                </div>
              </div>

              <div className="mt-4 flex items-center justify-between text-[11px] text-ledger-white/55">
                <span className="mono">tx · 0xa9c4…f2e1</span>
                <span className="mono">evidence · sha256:9f01…</span>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* why-confident-analytics-can-still-be-wrong */}
      <section className="relative border-t border-glass-grid bg-graphite-blue">
        <div className="mx-auto max-w-7xl px-6 py-20">
          <div className="max-w-2xl">
            <span className="eyebrow">Why confident analytics can still be wrong</span>
            <h2 className="display mt-3 text-[30px] font-semibold leading-tight sm:text-section">
              Confidence is not the same as truth. VeriSight separates one from the other.
            </h2>
          </div>
          <div className="mt-10 grid grid-cols-1 gap-4 md:grid-cols-3">
            <Compare
              tone="amber"
              tag="Normal dashboard summary"
              title="Generates a confident narrative"
              body="LLM-written summaries sound certain even when key context — segment mix, seasonality, discount effects — is missing."
            />
            <Compare
              tone="cyan"
              tag="KPI threshold tool"
              title="Checks the numbers, misses the context"
              body="Static rules verify thresholds but cannot judge whether a claim of causality is actually defensible."
            />
            <Compare
              tone="consensus"
              tag="VeriSight"
              title="Sends the claim and evidence to GenLayer validators"
              body="Validators independently reason about evidence strength, alternative interpretations, and business risk — then reach consensus on a verdict."
              highlight
            />
          </div>
        </div>
      </section>

      <footer className="border-t border-glass-grid bg-audit-black">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 text-[12px] text-ledger-white/55">
          <div>VeriSight · Insight Assurance OS</div>
          <div className="mono">GenLayer is the source of truth for the audit verdict.</div>
        </div>
      </footer>
    </main>
  );
}

function Tile({ label, value, tone }: { label: string; value: string; tone?: "amber" | "consensus" }) {
  const toneText = tone === "amber" ? "text-amber" : tone === "consensus" ? "text-consensus" : "text-ledger-white";
  return (
    <div className="rounded-panel border border-glass-grid bg-white/[0.03] p-3">
      <div className="mono text-[10px] uppercase tracking-[0.16em] text-ledger-white/55">{label}</div>
      <div className={`mt-1 text-[13.5px] font-medium ${toneText}`}>{value}</div>
    </div>
  );
}

function Compare({
  tag,
  title,
  body,
  tone,
  highlight,
}: {
  tag: string;
  title: string;
  body: string;
  tone: "amber" | "cyan" | "consensus";
  highlight?: boolean;
}) {
  const ring =
    tone === "consensus"
      ? "border-consensus/40"
      : tone === "amber"
      ? "border-amber/30"
      : "border-data-cyan/30";
  return (
    <div className={`rounded-panel border ${ring} bg-white/[0.03] p-5 ${highlight ? "shadow-glow" : ""}`}>
      <Badge tone={tone}>{tag}</Badge>
      <div className="display mt-3 text-cardtitle font-semibold text-ledger-white">{title}</div>
      <p className="mt-2 text-[13.5px] leading-relaxed text-ledger-white/70">{body}</p>
    </div>
  );
}
""",
)

# ===================================================================
# Auth layout — split executive access console
# ===================================================================
write(
    "app/(auth)/layout.tsx",
    """import Link from "next/link";
import { LogoMark } from "@/components/app/LogoMark";
import { Badge } from "@/components/audit/Badge";
import { SourceOfTruthBadge } from "@/components/audit/SourceOfTruthBadge";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-2">
      {/* left — executive console */}
      <div className="relative hidden overflow-hidden bg-audit-black text-ledger-white lg:flex">
        <div className="absolute inset-0 grid-backdrop-dark opacity-50 animate-gridPan" />
        <div className="absolute inset-0 bg-gradient-to-br from-consensus/15 via-transparent to-data-cyan/10" />
        <div className="relative z-10 flex w-full flex-col justify-between p-10">
          <Link href="/" className="flex items-center gap-2.5">
            <LogoMark />
            <div>
              <div className="display text-[15px] font-semibold leading-tight">VeriSight</div>
              <div className="mono text-[10px] uppercase tracking-[0.22em] text-consensus">
                Insight Assurance OS
              </div>
            </div>
          </Link>

          <div className="max-w-md space-y-5">
            <span className="eyebrow">Executive access console</span>
            <h1 className="display text-[36px] font-semibold leading-tight">
              The trust layer for business analytics.
            </h1>
            <p className="text-[14.5px] leading-relaxed text-ledger-white/70">
              VeriSight verifies whether dashboard insights and AI-generated report narratives
              are supported by the underlying data. Final verdicts are produced by GenLayer
              validator consensus, not by VeriSight alone.
            </p>
            <div className="flex flex-wrap gap-2">
              <SourceOfTruthBadge />
              <Badge tone="cyan" dot>Live · StudioNet</Badge>
            </div>
          </div>

          <div className="mono text-[11px] uppercase tracking-[0.18em] text-ledger-white/40">
            Email · Embedded wallet · Consensus verdict
          </div>
        </div>
      </div>

      {/* right — form panel */}
      <div className="flex items-center justify-center bg-ledger-mist px-6 py-12">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  );
}
""",
)

# ===================================================================
# Signup
# ===================================================================
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
import { Panel } from "@/components/ui/Panel";
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
          <h1 className="display mt-3 text-[30px] font-semibold text-ink">
            Save your recovery phrase
          </h1>
          <p className="mt-2 text-sm text-slate">
            These 24 words are the only way to restore your embedded wallet if you reset your
            password. Store them somewhere safe and offline. VeriSight cannot recover them for you.
          </p>
        </div>
        <Panel className="p-5">
          <div className="grid grid-cols-3 gap-2">
            {words.map((w, i) => (
              <div
                key={i}
                className="flex items-center gap-2 rounded-btn border border-auditline bg-ledger-mist px-2 py-1.5"
              >
                <span className="mono w-6 text-right text-[11px] text-slate">{i + 1}</span>
                <span className="mono text-[12.5px] text-ink">{w}</span>
              </div>
            ))}
          </div>
          <div className="mt-5">
            <Field label="Wallet address">
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
              I have saved my recovery phrase somewhere safe and understand it cannot be recovered if lost.
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
        </Panel>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <Badge tone="blue" dot>Create access</Badge>
        <h1 className="display mt-3 text-[30px] font-semibold text-ink">
          Create your VeriSight account
        </h1>
        <p className="mt-2 text-sm text-slate">
          Your VeriSight profile includes a secure embedded wallet used only for GenLayer audit
          actions. You do not need a browser wallet for normal use.
        </p>
      </div>

      <Panel className="p-6">
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
            {pending ? "Provisioning embedded wallet…" : "Create account"}
          </Button>
        </form>
      </Panel>

      <p className="text-sm text-slate">
        Already have an account?{" "}
        <Link href="/login" className="link">Sign in</Link>
      </p>
    </div>
  );
}
""",
)

# ===================================================================
# Login
# ===================================================================
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
import { Panel } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";

export default function LoginPage() {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="space-y-5">
      <div>
        <Badge tone="blue" dot>Executive login terminal</Badge>
        <h1 className="display mt-3 text-[30px] font-semibold text-ink">
          Sign in to VeriSight
        </h1>
        <p className="mt-2 text-sm text-slate">
          Email and password only. Your embedded wallet is unlocked in the background.
        </p>
      </div>
      <Panel className="p-6">
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
          <Field label="Email">
            <Input type="email" name="email" required />
          </Field>
          <Field label="Password">
            <Input type="password" name="password" required />
          </Field>
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
      </Panel>
    </div>
  );
}
""",
)

# ===================================================================
# Forgot password
# ===================================================================
write(
    "app/(auth)/forgot-password/page.tsx",
    """"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { forgotPasswordAction } from "@/lib/auth/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Panel } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";

export default function ForgotPasswordPage() {
  const [pending, start] = useTransition();
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="space-y-5">
      <div>
        <Badge tone="amber" dot>Security recovery panel</Badge>
        <h1 className="display mt-3 text-[30px] font-semibold text-ink">Forgot password</h1>
        <p className="mt-2 text-sm text-slate">
          Password reset does not create a new wallet. Your existing embedded wallet remains
          linked to your VeriSight profile and may require recovery key verification.
        </p>
      </div>
      <Panel className="p-6">
        <form
          className="space-y-4"
          action={(fd) => {
            setError(null);
            setMsg(null);
            start(async () => {
              const res = await forgotPasswordAction(fd);
              if (!res.ok) setError(res.error ?? "Failed");
              else setMsg("Check your email for a reset link.");
            });
          }}
        >
          <Field label="Email">
            <Input type="email" name="email" required />
          </Field>
          {error ? (
            <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">
              {error}
            </div>
          ) : null}
          {msg ? (
            <div className="rounded-btn border border-emerald/40 bg-emerald/5 p-3 text-sm text-emerald">
              {msg}
            </div>
          ) : null}
          <Button type="submit" variant="exec" className="w-full" disabled={pending}>
            {pending ? "Sending…" : "Send reset link"}
          </Button>
        </form>
        <div className="mt-4 text-sm">
          <Link href="/login" className="link">Back to sign in</Link>
        </div>
      </Panel>
    </div>
  );
}
""",
)

# ===================================================================
# Reset password
# ===================================================================
write(
    "app/(auth)/reset-password/page.tsx",
    """"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { resetPasswordAction } from "@/lib/auth/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Panel } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="space-y-5">
      <div>
        <Badge tone="consensus" dot>Wallet re-wrap</Badge>
        <h1 className="display mt-3 text-[30px] font-semibold text-ink">
          Reset password
        </h1>
        <p className="mt-2 text-sm text-slate">
          Resetting your password must not replace your embedded wallet. VeriSight will
          preserve the wallet linked to your Supabase user profile.
        </p>
      </div>
      <Panel className="p-6">
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
          <Field label="New password">
            <Input type="password" name="newPassword" required minLength={8} />
          </Field>
          <Field label="Recovery phrase" hint="24 words from your VeriSight signup.">
            <textarea
              name="recoveryPhrase"
              required
              rows={3}
              className="input mono"
              placeholder="word1 word2 word3 …"
            />
          </Field>
          <div className="rounded-btn border border-auditline bg-blue-steel p-3 text-xs text-ink">
            VeriSight will unwrap your existing wallet key using the recovery phrase, then
            re-encrypt it under your new password. Your wallet address will not change.
          </div>
          {error ? (
            <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">
              {error}
            </div>
          ) : null}
          <Button type="submit" variant="exec" className="w-full" disabled={pending}>
            {pending ? "Re-wrapping wallet key…" : "Set new password"}
          </Button>
        </form>
      </Panel>
    </div>
  );
}
""",
)

# ===================================================================
# Signed-in app layout
# ===================================================================
write(
    "app/(app)/layout.tsx",
    """import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { AuditRail } from "@/components/app/AuditRail";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, profile } = await getProfile();
  if (!profile) redirect("/login");

  return (
    <div className="flex min-h-screen bg-ledger-mist">
      <AuditRail email={user.email ?? ""} displayName={profile.display_name} />
      <div className="flex min-w-0 flex-1 flex-col">{children}</div>
    </div>
  );
}
""",
)

# ===================================================================
# Dashboard
# ===================================================================
write(
    "app/(app)/dashboard/page.tsx",
    """import Link from "next/link";
import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";
import { InsightVerdictPanel } from "@/components/audit/InsightVerdictPanel";
import { ConsensusBadge } from "@/components/audit/ConsensusBadge";
import { SourceOfTruthBadge } from "@/components/audit/SourceOfTruthBadge";
import { Meter } from "@/components/audit/Meter";
import { EmptyState } from "@/components/audit/EmptyState";

export default async function DashboardPage() {
  const { profile, supabase } = await getProfile();
  if (!profile?.onboarding_completed) redirect("/onboarding");

  const { data: workspaces, count: workspaceCount } = await supabase
    .from("workspaces")
    .select("id,name", { count: "exact" })
    .order("created_at", { ascending: false })
    .limit(1);
  const activeWorkspace = workspaces?.[0];

  const { count: auditCount } = await supabase
    .from("insight_audit_cases")
    .select("*", { count: "exact", head: true });

  return (
    <>
      <WorkspaceContextBar
        sectionTitle="Dashboard"
        workspaceName={activeWorkspace?.name}
        activeAuditCount={auditCount ?? 0}
      />

      <main className="flex-1 px-6 py-6">
        <div className="space-y-6">
          {/* greeting strip */}
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <span className="eyebrow">Insight assurance overview</span>
              <h1 className="display mt-1 text-pagetitle font-semibold text-ink">
                Welcome back, {profile.display_name ?? "analyst"}
              </h1>
              <p className="text-sm text-slate">
                Every verdict displayed here is produced by GenLayer validator consensus.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge tone="blue" dot>{workspaceCount ?? 0} workspaces</Badge>
              <Badge tone="cyan" dot>Dataset freshness · live</Badge>
              <SourceOfTruthBadge />
            </div>
          </div>

          {/* main row */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1.7fr_1fr_1fr]">
            <div className="lg:row-span-1">
              <InsightVerdictPanel demo />
            </div>

            <Panel className="p-5">
              <span className="eyebrow eyebrow-slate">Claim risk radar</span>
              <div className="display mt-2 text-section font-semibold text-ink">Moderate</div>
              <p className="mt-1 text-sm text-slate">
                Across pending audits, the dominant risk is unverified causality.
              </p>
              <div className="mt-4 space-y-3">
                <RiskRow label="Causality risk"          tone="amber"   value={62} />
                <RiskRow label="Evidence completeness"    tone="emerald" value={74} />
                <RiskRow label="Metric definition gaps"   tone="claim"   value={28} />
              </div>
            </Panel>

            <Panel tone="dark" className="p-5">
              <div className="flex items-center justify-between">
                <span className="eyebrow">GenLayer consensus</span>
                <ConsensusBadge />
              </div>
              <div className="display mt-3 text-section font-semibold">Operational</div>
              <p className="mt-1 text-[13px] text-ledger-white/65">
                Validators reasoning over packets independently. Equivalence criteria active.
              </p>
              <div className="mt-4 space-y-1.5 text-[12.5px]">
                <Row left="Contract" right={<span className="hash-dark">VeriSightInsightAuditor</span>} />
                <Row left="Network" right={<span className="badge badge-dark">StudioNet · 61999</span>} />
                <Row left="Last verdict" right={<ConsensusBadge />} />
              </div>
            </Panel>
          </div>

          {/* second row — ledger + queues */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-[2fr_1fr]">
            <Panel>
              <PanelHeader
                eyebrow="Audit matrix"
                title="Active insight audits"
                right={
                  <Link href="/audits/new" className="btn-secondary">New audit</Link>
                }
              />
              <EmptyState
                title="No insights have been audited yet"
                body="Start by submitting a dashboard claim. VeriSight will prepare the packet and GenLayer validators will reach consensus on whether the data supports it."
                action={
                  <Link href="/audits/new" className="btn-consensus">
                    Audit an insight
                  </Link>
                }
              />
            </Panel>

            <div className="space-y-4">
              <Panel className="p-5">
                <span className="eyebrow eyebrow-slate">Evidence quality</span>
                <div className="mt-3 flex items-center justify-between">
                  <div>
                    <div className="display text-section font-semibold text-ink">Fresh</div>
                    <p className="mt-1 text-sm text-slate">No stale evidence detected.</p>
                  </div>
                  <Badge tone="verified" dot>OK</Badge>
                </div>
              </Panel>
              <Panel className="p-5">
                <span className="eyebrow eyebrow-slate">Dataset snapshot health</span>
                <div className="mt-3 flex items-center justify-between">
                  <div>
                    <div className="display text-section font-semibold text-ink">Healthy</div>
                    <p className="mt-1 text-sm text-slate">Snapshots match metric definitions.</p>
                  </div>
                  <Badge tone="cyan" dot>Live</Badge>
                </div>
              </Panel>
            </div>
          </div>

          {/* third row — queues + contract activity */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <Panel className="p-5">
              <span className="eyebrow eyebrow-slate">Unsupported assumptions queue</span>
              <EmptyState
                title="Nothing flagged yet"
                body="VeriSight will surface claim assumptions that lack supporting evidence after the first audit completes."
              />
            </Panel>
            <Panel className="p-5">
              <span className="eyebrow eyebrow-slate">Business risk queue</span>
              <EmptyState
                title="No risks queued"
                body="High-risk verdicts will appear here so executives can review them before acting."
              />
            </Panel>
            <Panel tone="darker" className="p-5">
              <div className="flex items-center justify-between">
                <span className="eyebrow">Contract activity stream</span>
                <Badge tone="dark">StudioNet</Badge>
              </div>
              <div className="mt-4 space-y-2 text-[12.5px] text-ledger-white/75">
                <ActivityRow label="Validator quorum" value="ready" />
                <ActivityRow label="Equivalence criteria" value="loaded" />
                <ActivityRow label="Pending submissions" value="0" />
              </div>
            </Panel>
          </div>
        </div>
      </main>
    </>
  );
}

function RiskRow({ label, tone, value }: { label: string; tone: "amber" | "emerald" | "claim"; value: number }) {
  return (
    <div>
      <div className="flex items-center justify-between text-[12.5px] text-slate">
        <span>{label}</span>
        <span className="mono text-ink">{value}%</span>
      </div>
      <Meter value={value} tone={tone} className="mt-1.5" />
    </div>
  );
}

function Row({ left, right }: { left: string; right: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-ledger-white/65">{left}</span>
      {right}
    </div>
  );
}

function ActivityRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-glass-grid pb-1.5 last:border-b-0">
      <span>{label}</span>
      <span className="mono uppercase tracking-[0.12em] text-ledger-white/55">{value}</span>
    </div>
  );
}
""",
)

# ===================================================================
# Onboarding — staged setup
# ===================================================================
write(
    "app/(app)/onboarding/page.tsx",
    """import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { Panel } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";
import { OnboardingForm } from "./OnboardingForm";

export default async function OnboardingPage() {
  const { profile } = await getProfile();
  if (profile?.onboarding_completed) redirect("/dashboard");

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-12">
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_1.4fr]">
        <div className="space-y-4">
          <Badge tone="consensus" dot>Workspace assurance setup</Badge>
          <h1 className="display text-pagetitle font-semibold text-ink">
            Configure your first analytics workspace
          </h1>
          <p className="text-sm text-slate">
            A workspace groups one company, team, client, or project. Insight audits, evidence,
            dataset snapshots, and verdicts all belong to a workspace.
          </p>

          <div className="mt-4 space-y-3 rounded-panel border border-auditline bg-white-ledger p-5">
            <Stage n={1} label="Account profile" done />
            <Stage n={2} label="Workspace identity" active />
            <Stage n={3} label="Analytics function" />
            <Stage n={4} label="KPI focus" />
            <Stage n={5} label="Recovery key setup" />
          </div>

          <div className="rounded-panel border border-auditline bg-blue-steel p-4 text-[13px] text-ink">
            Tip · Pick a KPI category that matches the kind of dashboard insight you most often
            audit. You can change it later.
          </div>
        </div>

        <Panel className="p-6">
          <OnboardingForm />
        </Panel>
      </div>
    </main>
  );
}

function Stage({ n, label, active, done }: { n: number; label: string; active?: boolean; done?: boolean }) {
  return (
    <div className="flex items-center gap-3">
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
      <span className={done || active ? "text-sm font-medium text-ink" : "text-sm text-slate"}>
        {label}
      </span>
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
        <Field label="Workspace name">
          <Input name="name" required placeholder="Acme Analytics" />
        </Field>
        <Field label="Organisation">
          <Input name="organisation_name" placeholder="Acme Inc." />
        </Field>
        <Field label="Business function">
          <select name="business_function" className="input">
            <option value="">Select…</option>
            {FUNCS.map((v) => <option key={v}>{v}</option>)}
          </select>
        </Field>
        <Field label="Industry">
          <Input name="industry" placeholder="SaaS, e-commerce…" />
        </Field>
        <Field label="Reporting cadence">
          <select name="reporting_cadence" className="input">
            <option value="">Select…</option>
            {CADENCES.map((v) => <option key={v}>{v}</option>)}
          </select>
        </Field>
        <Field label="Primary KPI category">
          <select name="primary_kpi_category" className="input">
            <option value="">Select…</option>
            {KPIS.map((v) => <option key={v}>{v}</option>)}
          </select>
        </Field>
      </div>
      {error ? (
        <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">
          {error}
        </div>
      ) : null}
      <Button type="submit" variant="exec" className="w-full" disabled={pending}>
        {pending ? "Creating workspace…" : "Create workspace and continue"}
      </Button>
    </form>
  );
}
""",
)

# ===================================================================
# Workspaces list + detail
# ===================================================================
write(
    "app/(app)/workspaces/page.tsx",
    """import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
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
      <WorkspaceContextBar
        sectionTitle="Workspaces"
        workspaceName={workspaces?.[0]?.name}
        activeAuditCount={0}
      />

      <main className="flex-1 px-6 py-6">
        <div className="space-y-6">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <span className="eyebrow">Analytics environments</span>
              <h1 className="display mt-1 text-pagetitle font-semibold text-ink">Workspaces</h1>
              <p className="text-sm text-slate">One workspace per company, team, client, or project.</p>
            </div>
            <Badge tone="blue" dot>{workspaces?.length ?? 0} total</Badge>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.7fr_1fr]">
            <div className="space-y-4">
              {workspaces && workspaces.length > 0 ? (
                workspaces.map((w) => (
                  <Panel key={w.id} className="overflow-hidden">
                    <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr]">
                      <div className="border-b border-auditline p-5 lg:border-b-0 lg:border-r">
                        <Link href={`/workspaces/${w.id}`} className="display text-cardtitle font-semibold text-ink hover:underline">
                          {w.name}
                        </Link>
                        <p className="text-sm text-slate">{w.organisation_name ?? "—"}</p>
                        <div className="mt-4 grid grid-cols-2 gap-3 text-[12.5px] sm:grid-cols-4">
                          <Stat label="Function" value={w.business_function} />
                          <Stat label="Industry" value={w.industry} />
                          <Stat label="Cadence" value={w.reporting_cadence} />
                          <Stat label="KPI" value={w.primary_kpi_category} />
                        </div>
                      </div>
                      <div className="bg-blue-steel p-5">
                        <span className="eyebrow eyebrow-slate">Audit posture</span>
                        <div className="mt-3 space-y-2 text-[13px]">
                          <Row label="Active audits"  value={<Badge tone="slate">0</Badge>} />
                          <Row label="Last verdict"   value={<Badge tone="slate">none yet</Badge>} />
                          <Row label="Evidence health" value={<Badge tone="verified" dot>OK</Badge>} />
                        </div>
                        <Link href={`/workspaces/${w.id}`} className="btn-secondary mt-4 w-full justify-center">
                          Open workspace
                        </Link>
                      </div>
                    </div>
                  </Panel>
                ))
              ) : (
                <Panel>
                  <EmptyState
                    title="No workspaces yet"
                    body="Workspaces group your analytics environments. Create one to start auditing insights."
                  />
                </Panel>
              )}
            </div>

            <Panel className="h-fit">
              <PanelHeader eyebrow="New workspace" title="Create workspace" />
              <div className="p-5">
                <CreateWorkspaceForm />
              </div>
            </Panel>
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
    <form
      className="space-y-3"
      action={(fd) => {
        setError(null);
        start(async () => {
          const res = await createWorkspaceAction(fd);
          if (!res.ok) setError(res.error);
          else router.refresh();
        });
      }}
    >
      <Field label="Workspace name">
        <Input name="name" required placeholder="Acme Analytics" />
      </Field>
      <Field label="Organisation">
        <Input name="organisation_name" placeholder="Acme Inc." />
      </Field>
      <Field label="Business function">
        <select name="business_function" className="input">
          <option value="">Select…</option>
          {FUNCS.map((v) => <option key={v}>{v}</option>)}
        </select>
      </Field>
      <Field label="Industry"><Input name="industry" placeholder="SaaS, e-commerce…" /></Field>
      <Field label="Reporting cadence">
        <select name="reporting_cadence" className="input">
          <option value="">Select…</option>
          {CADENCES.map((v) => <option key={v}>{v}</option>)}
        </select>
      </Field>
      <Field label="Primary KPI category">
        <select name="primary_kpi_category" className="input">
          <option value="">Select…</option>
          {KPIS.map((v) => <option key={v}>{v}</option>)}
        </select>
      </Field>
      {error ? (
        <div className="rounded-btn border border-claim/40 bg-claim/5 p-2 text-xs text-claim">{error}</div>
      ) : null}
      <Button type="submit" variant="exec" className="w-full" disabled={pending}>
        {pending ? "Creating…" : "Create workspace"}
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
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";

export default async function WorkspaceDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const { supabase } = await requireUser();

  const { data: workspace } = await supabase
    .from("workspaces").select("*").eq("id", id).single();
  if (!workspace) notFound();

  const { data: audits } = await supabase
    .from("insight_audit_cases")
    .select("id,insight_claim,status,created_at")
    .eq("workspace_id", id)
    .order("created_at", { ascending: false });

  return (
    <>
      <WorkspaceContextBar
        sectionTitle={workspace.name}
        workspaceName={workspace.name}
        activeAuditCount={audits?.length ?? 0}
      />
      <main className="flex-1 px-6 py-6">
        <div className="space-y-6">
          <div>
            <Link href="/workspaces" className="text-xs text-slate hover:underline">
              ← Workspaces
            </Link>
            <h1 className="display mt-1 text-pagetitle font-semibold text-ink">
              {workspace.name}
            </h1>
            <p className="text-sm text-slate">{workspace.organisation_name ?? "—"}</p>
          </div>

          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {[
              ["Business function", workspace.business_function],
              ["Industry", workspace.industry],
              ["Reporting cadence", workspace.reporting_cadence],
              ["Primary KPI category", workspace.primary_kpi_category],
            ].map(([label, val]) => (
              <Panel key={String(label)} className="p-4">
                <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
                <div className="mt-1 text-sm text-ink">{(val as string) ?? "—"}</div>
              </Panel>
            ))}
          </div>

          <Panel>
            <PanelHeader
              eyebrow="Audit activity"
              title="Insight audit cases"
              right={
                <Link href={`/audits/new?workspace=${workspace.id}`} className="btn-consensus">
                  New audit
                </Link>
              }
            />
            {audits && audits.length > 0 ? (
              <table className="ledger-table">
                <thead>
                  <tr>
                    <th>Claim</th>
                    <th>Status</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {audits.map((a) => (
                    <tr key={a.id}>
                      <td>
                        <Link href={`/audits/${a.id}`} className="link">{a.insight_claim}</Link>
                      </td>
                      <td><Badge tone="slate">{a.status}</Badge></td>
                      <td className="text-slate">{new Date(a.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState
                title="No audit cases yet for this workspace"
                body="Start by submitting a dashboard claim. VeriSight will prepare the packet for GenLayer consensus review."
              />
            )}
          </Panel>
        </div>
      </main>
    </>
  );
}
""",
)

# ===================================================================
# Placeholder on-design pages for routes built in later stages
# ===================================================================
def placeholder(rel, title, eyebrow, body, action_label="Audit an insight", action_href="/audits/new"):
    write(
        rel,
        f""""""
    )

# Insight Audits list
write(
    "app/(app)/audits/page.tsx",
    """import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";

export default async function AuditsPage() {
  const { supabase } = await requireUser();
  const { data: audits } = await supabase
    .from("insight_audit_cases")
    .select("id,insight_claim,status,created_at,workspace_id")
    .order("created_at", { ascending: false });

  return (
    <>
      <WorkspaceContextBar sectionTitle="Insight Audits" activeAuditCount={audits?.length ?? 0} />
      <main className="flex-1 px-6 py-6">
        <div className="space-y-6">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <span className="eyebrow">Audit ledger</span>
              <h1 className="display mt-1 text-pagetitle font-semibold text-ink">Insight Audits</h1>
              <p className="text-sm text-slate">
                Every audit packet prepared for GenLayer consensus review.
              </p>
            </div>
            <Link href="/audits/new" className="btn-consensus">
              <span className="dot bg-white" /> Audit an insight
            </Link>
          </div>

          <Panel>
            <PanelHeader eyebrow="Audit cases" title="All audits" />
            {audits && audits.length > 0 ? (
              <table className="ledger-table">
                <thead><tr><th>Claim</th><th>Status</th><th>Created</th></tr></thead>
                <tbody>
                  {audits.map((a) => (
                    <tr key={a.id}>
                      <td><Link href={`/audits/${a.id}`} className="link">{a.insight_claim}</Link></td>
                      <td><Badge tone="slate">{a.status}</Badge></td>
                      <td className="text-slate">{new Date(a.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState
                title="No insights have been audited yet"
                body="Start by submitting a dashboard claim and VeriSight will prepare it for GenLayer consensus review."
                action={<Link href="/audits/new" className="btn-consensus">Audit an insight</Link>}
              />
            )}
          </Panel>
        </div>
      </main>
    </>
  );
}
""",
)

# Audits/new — placeholder packet builder shell
write(
    "app/(app)/audits/new/page.tsx",
    """import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";
import { SourceOfTruthBadge } from "@/components/audit/SourceOfTruthBadge";

export default async function NewAuditPage() {
  await requireUser();
  return (
    <>
      <WorkspaceContextBar sectionTitle="Insight Audit Packet Builder" />
      <main className="flex-1 px-6 py-6">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[260px_1fr_320px]">
          {/* left audit rail */}
          <Panel className="h-fit p-5">
            <span className="eyebrow eyebrow-slate">Packet readiness</span>
            <ul className="mt-4 space-y-3 text-[13px]">
              <StepRow n={1} label="Workspace selected" />
              <StepRow n={2} label="Insight claim" />
              <StepRow n={3} label="Metric definition" />
              <StepRow n={4} label="Time period" />
              <StepRow n={5} label="Segment / filter context" />
              <StepRow n={6} label="Dataset summary" />
              <StepRow n={7} label="Evidence uploaded" />
              <StepRow n={8} label="Audit packet reviewed" />
              <StepRow n={9} label="Submitted to GenLayer" />
            </ul>
          </Panel>

          <div className="space-y-4">
            <Panel className="p-6">
              <Badge tone="amber" dot>Stage 5 · coming online</Badge>
              <h1 className="display mt-3 text-section font-semibold text-ink">
                The Insight Audit Packet Builder will appear here.
              </h1>
              <p className="mt-2 text-sm text-slate">
                You'll assemble each audit packet — claim, metric definition, dataset summary,
                segment context, evidence files, and competing interpretations — and submit it
                to GenLayer for consensus review.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Badge tone="blue">Next.js prepares the packet</Badge>
                <Badge tone="cyan">Supabase stores product state</Badge>
                <SourceOfTruthBadge />
              </div>
              <div className="mt-5">
                <Link href="/dashboard" className="btn-secondary">Back to dashboard</Link>
              </div>
            </Panel>

            <Panel tone="darker" className="p-5">
              <span className="eyebrow">GenLayer review</span>
              <p className="mt-2 text-[13.5px] text-ledger-white/75">
                This insight will be evaluated by GenLayer validators. VeriSight prepares the
                audit packet, but the final audit verdict is not produced by the frontend,
                Supabase, or a private backend. Validators independently compare the claim
                against the evidence and reach consensus on whether the insight is supported.
              </p>
            </Panel>
          </div>

          {/* right inspection drawer */}
          <Panel tone="dark" className="h-fit p-5">
            <PanelHeader tone="dark" eyebrow="Live preview" title="Audit packet" />
            <div className="mt-4 space-y-3 text-[13px]">
              <Drow left="Claim" right="—" />
              <Drow left="Metric" right="—" />
              <Drow left="Time period" right="—" />
              <Drow left="Evidence files" right="0" />
              <Drow left="GenLayer readiness" right={<Badge tone="amber" dot>Not ready</Badge>} />
            </div>
          </Panel>
        </div>
      </main>
    </>
  );
}

function StepRow({ n, label }: { n: number; label: string }) {
  return (
    <li className="flex items-center gap-2.5">
      <span className="grid h-6 w-6 place-items-center rounded-full border border-auditline bg-white-ledger text-[11px] font-semibold text-slate">{n}</span>
      <span className="text-slate">{label}</span>
    </li>
  );
}
function Drow({ left, right }: { left: string; right: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b border-glass-grid pb-2 last:border-b-0">
      <span className="text-ledger-white/65">{left}</span>
      <span className="text-ledger-white">{right}</span>
    </div>
  );
}
""",
)

# Audit detail
write(
    "app/(app)/audits/[id]/page.tsx",
    """import { notFound } from "next/navigation";
import { requireUser } from "@/lib/auth/getUser";
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";
import { ConsensusBadge } from "@/components/audit/ConsensusBadge";
import { SourceOfTruthBadge } from "@/components/audit/SourceOfTruthBadge";
import { SupportBadge } from "@/components/audit/SupportBadge";
import { HashText } from "@/components/audit/HashText";

export default async function AuditDetailPage({ params }: { params: Promise<{ id: string }> }) {
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

  return (
    <>
      <WorkspaceContextBar sectionTitle="Consensus Audit Terminal" />
      <main className="flex-1 px-6 py-6">
        <div className="space-y-6">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <Badge tone="consensus" dot>Audit · {audit.id.slice(0, 8)}</Badge>
              <h1 className="display mt-2 text-pagetitle font-semibold text-ink">
                {audit.insight_claim}
              </h1>
              <p className="text-sm text-slate">{audit.business_question ?? "—"}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {verdict ? <SupportBadge verdict={(verdict.verdict ?? "needs_more_evidence") as never} /> : <Badge tone="amber" dot>Awaiting verdict</Badge>}
              <ConsensusBadge state={verdict ? "reached" : "pending"} />
              <SourceOfTruthBadge />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1.4fr_1.2fr_320px]">
            <Panel className="p-6">
              <span className="eyebrow eyebrow-slate">Verdict</span>
              <div className="display mt-3 text-section font-semibold text-ink">
                {verdict?.verdict ?? "Pending"}
              </div>
              <p className="mt-2 text-sm text-slate">
                {verdict?.reasoning_summary ?? "GenLayer validators will reason over the packet and reach consensus."}
              </p>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <Mini label="Support level" value={verdict?.support_level ?? "—"} />
                <Mini label="Confidence" value={verdict?.confidence_label ?? "—"} />
                <Mini label="Business risk" value={verdict?.business_risk ?? "—"} />
                <Mini label="Status" value={audit.status} />
              </div>
            </Panel>

            <Panel className="p-6">
              <span className="eyebrow eyebrow-slate">Evidence considered</span>
              <p className="mt-2 text-sm text-slate">
                Evidence files, metric definitions, and dataset snapshots used by validators.
              </p>
              <div className="mt-4 space-y-2 text-[13.5px]">
                <Row label="Metric" value={audit.metric_name ?? "—"} />
                <Row label="Time period" value={audit.time_period ?? "—"} />
                <Row label="Segment context" value={audit.segment_context ?? "—"} />
                <Row label="Dataset summary" value={audit.dataset_summary ?? "—"} />
              </div>
            </Panel>

            <Panel tone="dark" className="p-5">
              <PanelHeader tone="dark" eyebrow="Inspection" title="GenLayer consensus" />
              <div className="mt-4 space-y-3 text-[12.5px]">
                <Drow left="Contract"
                       right={<HashText dark value={verdict?.contract_address ?? "—"} short />} />
                <Drow left="Tx hash"
                       right={<HashText dark value={verdict?.transaction_hash ?? "—"} short />} />
                <Drow left="Audit ID"
                       right={<HashText dark value={audit.id} short />} />
                <Drow left="Evidence digest"
                       right={<HashText dark value={verdict?.evidence_digest ?? "—"} short />} />
                <Drow left="Consensus" right={<ConsensusBadge state={verdict ? "reached" : "pending"} />} />
              </div>
            </Panel>
          </div>
        </div>
      </main>
    </>
  );
}

function Mini({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-btn border border-auditline bg-ledger-mist p-3">
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className="mt-1 text-[13.5px] text-ink">{value}</div>
    </div>
  );
}
function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-auditline pb-2 last:border-b-0">
      <span className="text-slate">{label}</span>
      <span className="text-right text-ink">{value}</span>
    </div>
  );
}
function Drow({ left, right }: { left: string; right: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b border-glass-grid pb-2 last:border-b-0">
      <span className="text-ledger-white/65">{left}</span>
      <span>{right}</span>
    </div>
  );
}
""",
)

# Evidence Ledger
write(
    "app/(app)/evidence/page.tsx",
    """import { requireUser } from "@/lib/auth/getUser";
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { HashText } from "@/components/audit/HashText";

export default async function EvidencePage() {
  const { supabase } = await requireUser();
  const { data: files } = await supabase
    .from("evidence_files")
    .select("id,audit_case_id,file_type,file_size,evidence_hash,created_at,file_url")
    .order("created_at", { ascending: false });

  return (
    <>
      <WorkspaceContextBar sectionTitle="Evidence Ledger" />
      <main className="flex-1 px-6 py-6">
        <div className="space-y-6">
          <div>
            <span className="eyebrow">Audit evidence vault</span>
            <h1 className="display mt-1 text-pagetitle font-semibold text-ink">Evidence Ledger</h1>
            <p className="text-sm text-slate">
              Every dataset, screenshot, report, snapshot, and analyst note submitted as audit evidence.
            </p>
          </div>

          <Panel>
            <PanelHeader eyebrow="Ledger" title="All evidence files" />
            {files && files.length > 0 ? (
              <table className="ledger-table">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Evidence hash</th>
                    <th>Linked audit</th>
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
                      <td className="text-slate">{new Date(f.created_at).toLocaleString()}</td>
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
          </Panel>
        </div>
      </main>
    </>
  );
}
""",
)

# Dataset snapshots
write(
    "app/(app)/snapshots/page.tsx",
    """import { requireUser } from "@/lib/auth/getUser";
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { EmptyState } from "@/components/audit/EmptyState";
import { HashText } from "@/components/audit/HashText";
import { Badge } from "@/components/audit/Badge";

export default async function SnapshotsPage() {
  const { supabase } = await requireUser();
  const { data: snaps } = await supabase
    .from("data_snapshots")
    .select("id,audit_case_id,source_type,source_url,snapshot_hash,created_at")
    .order("created_at", { ascending: false });

  return (
    <>
      <WorkspaceContextBar sectionTitle="Dataset Snapshots" />
      <main className="flex-1 px-6 py-6">
        <div className="space-y-6">
          <div>
            <span className="eyebrow">Metric evidence registry</span>
            <h1 className="display mt-1 text-pagetitle font-semibold text-ink">Dataset Snapshots</h1>
            <p className="text-sm text-slate">
              Structured metric snapshots help validators understand the context behind a claim.
            </p>
          </div>
          <Panel>
            <PanelHeader eyebrow="Snapshots" title="All registered snapshots" />
            {snaps && snaps.length > 0 ? (
              <table className="ledger-table">
                <thead>
                  <tr>
                    <th>Source</th>
                    <th>Snapshot hash</th>
                    <th>Linked audit</th>
                    <th>Created</th>
                  </tr>
                </thead>
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
          </Panel>
        </div>
      </main>
    </>
  );
}
""",
)

# Verdicts list
write(
    "app/(app)/verdicts/page.tsx",
    """import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";
import { EmptyState } from "@/components/audit/EmptyState";
import { HashText } from "@/components/audit/HashText";

export default async function VerdictsPage() {
  const { supabase } = await requireUser();
  const { data: verdicts } = await supabase
    .from("genlayer_audit_verdicts")
    .select("id,audit_case_id,verdict,support_level,business_risk,transaction_hash,created_at")
    .order("created_at", { ascending: false });

  return (
    <>
      <WorkspaceContextBar sectionTitle="Verdicts" />
      <main className="flex-1 px-6 py-6">
        <div className="space-y-6">
          <div>
            <span className="eyebrow">Consensus verdict history</span>
            <h1 className="display mt-1 text-pagetitle font-semibold text-ink">Verdicts</h1>
            <p className="text-sm text-slate">
              Mirrored consensus results from the VeriSight Intelligent Contract.
            </p>
          </div>
          <Panel>
            <PanelHeader eyebrow="History" title="All verdicts" />
            {verdicts && verdicts.length > 0 ? (
              <table className="ledger-table">
                <thead>
                  <tr>
                    <th>Verdict</th>
                    <th>Support level</th>
                    <th>Business risk</th>
                    <th>Tx hash</th>
                    <th>Issued</th>
                  </tr>
                </thead>
                <tbody>
                  {verdicts.map((v) => (
                    <tr key={v.id}>
                      <td>
                        <Link href={`/audits/${v.audit_case_id}`} className="link">
                          {v.verdict ?? "—"}
                        </Link>
                      </td>
                      <td><Badge tone="slate">{v.support_level ?? "—"}</Badge></td>
                      <td className="text-slate">{v.business_risk ?? "—"}</td>
                      <td><HashText value={v.transaction_hash ?? "—"} short /></td>
                      <td className="text-slate">{new Date(v.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState
                title="No verdicts issued yet"
                body="Once GenLayer validators reach consensus on your first audit, the verdict will appear here."
              />
            )}
          </Panel>
        </div>
      </main>
    </>
  );
}
""",
)

# Admin
write(
    "app/(app)/admin/page.tsx",
    """import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
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
      <WorkspaceContextBar sectionTitle="Admin · Contract Ops" />
      <main className="flex-1 bg-audit-black px-6 py-6 text-ledger-white">
        <div className="space-y-6">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <span className="eyebrow">Contract operations & audit control room</span>
              <h1 className="display mt-1 text-pagetitle font-semibold text-ledger-white">Admin Review</h1>
              <p className="text-sm text-ledger-white/65">
                Inspect every audit case, contract call, and validator outcome.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge tone="consensus" dot>StudioNet</Badge>
              <ConsensusBadge />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1.4fr_1fr]">
            <Panel tone="darker">
              <PanelHeader tone="dark" eyebrow="Audit cases" title="All insight audits" />
              {cases && cases.length > 0 ? (
                <table className="ledger-table">
                  <thead><tr><th>Audit ID</th><th>Claim</th><th>Status</th><th>Created</th></tr></thead>
                  <tbody>
                    {cases.map((c) => (
                      <tr key={c.id}>
                        <td><HashText dark value={c.id} short /></td>
                        <td className="text-ledger-white/85">{c.insight_claim}</td>
                        <td><Badge tone="dark">{c.status}</Badge></td>
                        <td className="text-ledger-white/55">{new Date(c.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <EmptyState
                  title="No audits to review yet"
                  body="Audits will appear here once users submit insight claims for GenLayer consensus."
                />
              )}
            </Panel>

            <Panel tone="darker">
              <PanelHeader tone="dark" eyebrow="Activity stream" title="Contract activity" />
              <div className="divide-y divide-glass-grid">
                {logs && logs.length > 0 ? logs.map((l) => (
                  <div key={l.id} className="flex items-start justify-between gap-3 px-5 py-3 text-[12.5px]">
                    <div className="space-y-1">
                      <div className="text-ledger-white/85">{l.action}</div>
                      <HashText dark value={l.transaction_hash ?? l.contract_address ?? "—"} short />
                    </div>
                    <Badge tone={l.status === "ok" ? "verified" : "amber"} dot>{l.status}</Badge>
                  </div>
                )) : (
                  <EmptyState title="No contract activity yet"
                    body="GenLayer calls and verdict mirroring events will stream here once audits run." />
                )}
              </div>
            </Panel>
          </div>
        </div>
      </main>
    </>
  );
}
""",
)

# Profile and wallet
write(
    "app/(app)/profile/page.tsx",
    """import { getProfile } from "@/lib/auth/getUser";
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";
import { HashText } from "@/components/audit/HashText";

export default async function ProfilePage() {
  const { user, profile, supabase } = await getProfile();
  const { data: wallet } = await supabase
    .from("wallets").select("address,created_at").eq("user_id", user.id).single();

  return (
    <>
      <WorkspaceContextBar sectionTitle="Profile · Wallet" />
      <main className="flex-1 px-6 py-6">
        <div className="space-y-6">
          <div>
            <span className="eyebrow">Profile and embedded wallet infrastructure</span>
            <h1 className="display mt-1 text-pagetitle font-semibold text-ink">Profile</h1>
            <p className="text-sm text-slate">
              Your wallet is embedded into your VeriSight profile. It is used to sign GenLayer
              audit actions in the background. You do not need MetaMask, Rabby, Rainbow, Zerion,
              or any external wallet for normal use.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Panel className="p-6">
              <span className="eyebrow eyebrow-slate">Email profile</span>
              <div className="mt-3 space-y-2 text-sm">
                <Row label="Display name" value={profile?.display_name ?? "—"} />
                <Row label="Email" value={user.email ?? "—"} />
                <Row label="Role" value={profile?.role ?? "user"} />
                <Row label="Onboarding" value={profile?.onboarding_completed ? "complete" : "pending"} />
              </div>
            </Panel>

            <Panel tone="dark" className="p-6">
              <div className="flex items-center justify-between">
                <span className="eyebrow">Embedded wallet</span>
                <Badge tone="consensus" dot>GenLayer signer</Badge>
              </div>
              <div className="mt-4 space-y-3 text-[13px]">
                <Drow left="Address" right={<HashText dark value={wallet?.address ?? "—"} short />} />
                <Drow left="Created" right={wallet?.created_at ? new Date(wallet.created_at).toLocaleString() : "—"} />
                <Drow left="Recovery key" right={<Badge tone="verified" dot>Active</Badge>} />
                <Drow left="External wallets" right={<Badge tone="dark">Not required</Badge>} />
              </div>
              <p className="mt-4 text-[12.5px] text-ledger-white/65">
                Resetting your password will not replace this wallet. VeriSight re-wraps the
                same wallet encryption key under the new password after recovery verification.
              </p>
            </Panel>
          </div>

          <Panel>
            <PanelHeader eyebrow="Security" title="Private key export" />
            <div className="p-6 text-sm text-ink">
              Private key export requires strong re-authentication and is logged. The export
              flow lives in <span className="mono">/settings · security</span> in a later stage.
            </div>
          </Panel>
        </div>
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
function Drow({ left, right }: { left: string; right: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b border-glass-grid pb-2 last:border-b-0">
      <span className="text-ledger-white/65">{left}</span>
      <span>{right}</span>
    </div>
  );
}
""",
)

# Settings
write(
    "app/(app)/settings/page.tsx",
    """import { getProfile } from "@/lib/auth/getUser";
import { WorkspaceContextBar } from "@/components/app/WorkspaceContextBar";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { Badge } from "@/components/audit/Badge";

export default async function SettingsPage() {
  const { profile, user } = await getProfile();
  return (
    <>
      <WorkspaceContextBar sectionTitle="Settings" />
      <main className="flex-1 px-6 py-6">
        <div className="space-y-6">
          <div>
            <span className="eyebrow">Account, security, recovery</span>
            <h1 className="display mt-1 text-pagetitle font-semibold text-ink">Settings</h1>
            <p className="text-sm text-slate">Audit-grade controls for your VeriSight profile.</p>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Panel>
              <PanelHeader eyebrow="Account" title="Email and identity" />
              <div className="p-6 space-y-2 text-sm">
                <Row label="Email" value={user.email ?? "—"} />
                <Row label="Display name" value={profile?.display_name ?? "—"} />
                <Row label="Role" value={profile?.role ?? "user"} />
              </div>
            </Panel>

            <Panel>
              <PanelHeader eyebrow="Security" title="Authentication and signing" />
              <div className="p-6 space-y-3 text-sm">
                <Row label="Password" value="Set" />
                <Row label="Embedded wallet" value="Provisioned" />
                <Row label="External wallet" value="Not required" />
              </div>
            </Panel>

            <Panel>
              <PanelHeader eyebrow="Recovery" title="Recovery key" />
              <div className="p-6 space-y-3 text-sm">
                <Row label="Recovery key" value="Stored offline by you" />
                <p className="text-xs text-slate">
                  Used to re-wrap your embedded wallet key after a password reset. Never shared
                  with VeriSight after signup.
                </p>
              </div>
            </Panel>

            <Panel>
              <PanelHeader eyebrow="Notifications" title="Audit alerts" />
              <div className="p-6 text-sm">
                <Row label="Email on new verdict" value={<Badge tone="slate">Default on</Badge>} />
              </div>
            </Panel>

            <Panel>
              <PanelHeader eyebrow="Data" title="Export" />
              <div className="p-6 text-sm">
                <Row label="Profile data export" value="Available on request" />
              </div>
            </Panel>

            <Panel className="border-claim/30">
              <PanelHeader eyebrow="Danger zone" title="Destructive actions" />
              <div className="p-6 text-sm text-claim">
                Account deletion will remove product state but the GenLayer contract record of
                past consensus verdicts remains on chain.
              </div>
            </Panel>
          </div>
        </div>
      </main>
    </>
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

print("\nRedesign files written.")
