"""Stage 1 — Bootstrap VeriSight Next.js 15 project.

Creates package.json, tsconfig, next config, tailwind v4 setup,
globals.css with the full VeriSight color & font system, root
layout with Space Grotesk / Manrope / JetBrains Mono, and a
placeholder landing page.

Run from project root: python scripts/stage1_bootstrap.py
"""
from __future__ import annotations
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def write(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {rel}")


def write_json(rel: str, obj) -> None:
    write(rel, json.dumps(obj, indent=2) + "\n")


# ---------------------------------------------------------------- package.json
package_json = {
    "name": "verisight",
    "version": "0.1.0",
    "private": True,
    "scripts": {
        "dev": "next dev",
        "build": "next build",
        "start": "next start",
        "lint": "next lint",
        "typecheck": "tsc --noEmit",
    },
    "dependencies": {
        "next": "15.1.3",
        "react": "19.0.0",
        "react-dom": "19.0.0",
        "@supabase/ssr": "^0.5.2",
        "@supabase/supabase-js": "^2.47.10",
        "viem": "^2.21.55",
        "zod": "^3.24.1",
        "clsx": "^2.1.1",
    },
    "devDependencies": {
        "typescript": "^5.7.2",
        "@types/node": "^22.10.2",
        "@types/react": "^19.0.2",
        "@types/react-dom": "^19.0.2",
        "tailwindcss": "^3.4.17",
        "postcss": "^8.4.49",
        "autoprefixer": "^10.4.20",
        "eslint": "^9.17.0",
        "eslint-config-next": "15.1.3",
    },
}
write_json("package.json", package_json)

# ---------------------------------------------------------------- tsconfig
tsconfig = {
    "compilerOptions": {
        "target": "ES2022",
        "lib": ["dom", "dom.iterable", "esnext"],
        "allowJs": False,
        "skipLibCheck": True,
        "strict": True,
        "noEmit": True,
        "esModuleInterop": True,
        "module": "esnext",
        "moduleResolution": "bundler",
        "resolveJsonModule": True,
        "isolatedModules": True,
        "jsx": "preserve",
        "incremental": True,
        "plugins": [{"name": "next"}],
        "paths": {"@/*": ["./*"]},
    },
    "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
    "exclude": ["node_modules"],
}
write_json("tsconfig.json", tsconfig)

# ---------------------------------------------------------------- next.config
write(
    "next.config.ts",
    """import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: { serverActions: { bodySizeLimit: "10mb" } },
};

export default nextConfig;
""",
)

# ---------------------------------------------------------------- next-env
write(
    "next-env.d.ts",
    """/// <reference types="next" />
/// <reference types="next/image-types/global" />
""",
)

# ---------------------------------------------------------------- tailwind
write(
    "tailwind.config.ts",
    """import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        obsidian: "#111318",
        analyst: "#2563EB",
        signal: "#22D3EE",
        amber: "#F59E0B",
        claim: "#EF4444",
        verified: "#10B981",
        graphite: "#F4F6F8",
        panel: "#FFFFFF",
        ink: "#0F172A",
        slate: "#64748B",
        gridline: "#E2E8F0",
        consensus: "#7C3AED",
      },
      fontFamily: {
        display: ["var(--font-space-grotesk)", "system-ui", "sans-serif"],
        body: ["var(--font-manrope)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: { btn: "8px" },
      fontSize: {
        hero: ["68px", { lineHeight: "1.05", letterSpacing: "-0.02em" }],
        pagetitle: ["42px", { lineHeight: "1.1", letterSpacing: "-0.01em" }],
        section: ["26px", { lineHeight: "1.2" }],
        cardtitle: ["19px", { lineHeight: "1.3" }],
      },
    },
  },
  plugins: [],
};
export default config;
""",
)

write(
    "postcss.config.mjs",
    """export default { plugins: { tailwindcss: {}, autoprefixer: {} } };
""",
)

# ---------------------------------------------------------------- globals.css
write(
    "app/globals.css",
    """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --obsidian: #111318;
  --analyst: #2563EB;
  --signal: #22D3EE;
  --amber: #F59E0B;
  --claim: #EF4444;
  --verified: #10B981;
  --graphite: #F4F6F8;
  --panel: #FFFFFF;
  --ink: #0F172A;
  --slate: #64748B;
  --gridline: #E2E8F0;
  --consensus: #7C3AED;
}

html, body { background: var(--graphite); color: var(--ink); }
body { font-family: var(--font-manrope), system-ui, sans-serif; }

.btn-primary {
  background: var(--obsidian); color: #fff; border-radius: 8px;
  padding: 10px 16px; font-weight: 600; font-size: 14px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
  transition: transform .05s ease, opacity .15s ease;
}
.btn-primary:hover { opacity: .92; }
.btn-primary:active { transform: translateY(1px); }

.btn-secondary {
  background: var(--panel); color: var(--ink);
  border: 1px solid var(--gridline); border-radius: 8px;
  padding: 10px 16px; font-weight: 600; font-size: 14px;
}

.btn-consensus {
  background: var(--consensus); color: #fff; border-radius: 8px;
  padding: 10px 16px; font-weight: 600; font-size: 14px;
}

.btn-danger {
  background: var(--claim); color: #fff; border-radius: 8px;
  padding: 10px 16px; font-weight: 600; font-size: 14px;
}

.panel {
  background: var(--panel); border: 1px solid var(--gridline);
  border-radius: 12px;
}

.mono { font-family: var(--font-jetbrains-mono), ui-monospace, monospace; }
.display { font-family: var(--font-space-grotesk), system-ui, sans-serif; }
""",
)

# ---------------------------------------------------------------- layout
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
  title: "VeriSight — Consensus backed analytics assurance",
  description:
    "VeriSight is a GenLayer powered analytics assurance platform that verifies whether dashboard insights and report narratives are supported by the underlying data.",
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

# ---------------------------------------------------------------- landing page
write(
    "app/page.tsx",
    """import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen">
      <header className="border-b border-gridline bg-panel">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="display text-xl font-bold tracking-tight text-obsidian">
            VeriSight
          </Link>
          <nav className="flex items-center gap-3">
            <Link href="/login" className="btn-secondary">Sign in</Link>
            <Link href="/signup" className="btn-primary">Create account</Link>
          </nav>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-6 py-24">
        <p className="mono mb-4 text-xs uppercase tracking-[0.18em] text-consensus">
          Consensus backed analytics assurance
        </p>
        <h1 className="display text-hero font-bold text-obsidian">
          Verify every insight before
          <br />
          it becomes a decision.
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-slate">
          VeriSight is a GenLayer powered analytics assurance platform that verifies
          whether dashboard insights and AI-generated report narratives are actually
          supported by the underlying data.
        </p>
        <div className="mt-10 flex gap-3">
          <Link href="/signup" className="btn-primary">Audit an insight</Link>
          <Link href="/demo" className="btn-secondary">View demo verdict</Link>
        </div>

        <div className="mt-20 grid grid-cols-1 gap-4 md:grid-cols-3">
          {[
            {
              title: "Insight claim",
              body: "Submit a dashboard claim, metric definition, and time period.",
            },
            {
              title: "Evidence ledger",
              body: "Attach datasets, screenshots, and report context as audit evidence.",
            },
            {
              title: "GenLayer consensus",
              body:
                "Validators independently reason over your claim and reach consensus on whether the data supports it.",
            },
          ].map((c) => (
            <div key={c.title} className="panel p-5">
              <div className="display text-cardtitle font-semibold text-obsidian">
                {c.title}
              </div>
              <p className="mt-2 text-sm text-slate">{c.body}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-gridline bg-panel">
        <div className="mx-auto max-w-6xl px-6 py-6 text-xs text-slate">
          VeriSight · GenLayer is the source of truth for the audit verdict.
        </div>
      </footer>
    </main>
  );
}
""",
)

# ---------------------------------------------------------------- env example
write(
    ".env.example",
    """# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# GenLayer StudioNet
NEXT_PUBLIC_GENLAYER_RPC_URL=https://studio.genlayer.com:8443/api
NEXT_PUBLIC_GENLAYER_CHAIN_ID=61999
NEXT_PUBLIC_VERISIGHT_CONTRACT_ADDRESS=

# Wallet crypto
WALLET_PEPPER=replace_with_64_hex_chars
""",
)

# ---------------------------------------------------------------- gitignore
write(
    ".gitignore",
    """node_modules
.next
out
.env
.env.local
.env*.local
.DS_Store
*.log
.vercel
""",
)

# ---------------------------------------------------------------- README
write(
    "README.md",
    """# VeriSight

Consensus backed analytics assurance. Built on Next.js 15, Supabase, and GenLayer.

## Local dev

```bash
npm install
cp .env.example .env.local
# fill Supabase + GenLayer values
npm run dev
```

GenLayer is the source of truth for audit verdicts.
""",
)

print("\nStage 1 scaffold complete.")
