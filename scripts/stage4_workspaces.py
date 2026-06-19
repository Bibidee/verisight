"""Stage 4 — Onboarding + Workspaces.

Writes:
 - lib/auth/getUser.ts                       (require signed-in user)
 - lib/workspaces/actions.ts                 (server actions)
 - app/(app)/layout.tsx                      (signed-in shell with sidebar)
 - app/(app)/dashboard/page.tsx              (placeholder; full content in Stage 9)
 - app/(app)/workspaces/page.tsx             (list + create)
 - app/(app)/workspaces/[id]/page.tsx        (detail)
 - app/(app)/onboarding/page.tsx             (workspace + KPI focus)
 - components/app/Sidebar.tsx
 - components/app/Topbar.tsx
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
# lib/auth/getUser.ts
# ===================================================================
write(
    "lib/auth/getUser.ts",
    """import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export async function requireUser() {
  const supabase = await createSupabaseServerClient();
  const { data } = await supabase.auth.getUser();
  if (!data.user) redirect("/login");
  return { user: data.user, supabase };
}

export async function getProfile() {
  const { user, supabase } = await requireUser();
  const { data: profile } = await supabase
    .from("profiles")
    .select("id,email,display_name,role,onboarding_completed")
    .eq("id", user.id)
    .single();
  return { user, profile, supabase };
}
""",
)

# ===================================================================
# lib/workspaces/actions.ts
# ===================================================================
write(
    "lib/workspaces/actions.ts",
    """"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { createSupabaseAdminClient } from "@/lib/supabase/admin";

const WorkspaceSchema = z.object({
  name: z.string().min(1).max(120),
  organisation_name: z.string().max(160).optional().nullable(),
  business_function: z.string().max(80).optional().nullable(),
  industry: z.string().max(80).optional().nullable(),
  reporting_cadence: z.string().max(40).optional().nullable(),
  primary_kpi_category: z.string().max(80).optional().nullable(),
});

function clean(fd: FormData) {
  const obj: Record<string, string | null> = {};
  for (const k of [
    "name",
    "organisation_name",
    "business_function",
    "industry",
    "reporting_cadence",
    "primary_kpi_category",
  ]) {
    const v = fd.get(k);
    obj[k] = v ? String(v) : null;
  }
  return obj;
}

export async function createWorkspaceAction(formData: FormData) {
  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (!u.user) return { ok: false as const, error: "Not signed in" };

  const parsed = WorkspaceSchema.safeParse(clean(formData));
  if (!parsed.success) {
    return { ok: false as const, error: parsed.error.issues[0]?.message ?? "Invalid input" };
  }

  const { data, error } = await supabase
    .from("workspaces")
    .insert({ ...parsed.data, user_id: u.user.id })
    .select("id")
    .single();
  if (error || !data) return { ok: false as const, error: error?.message ?? "Failed" };

  revalidatePath("/workspaces");
  revalidatePath("/dashboard");
  return { ok: true as const, id: data.id };
}

export async function completeOnboardingAction(formData: FormData) {
  const res = await createWorkspaceAction(formData);
  if (!res.ok) return res;

  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (u.user) {
    const admin = createSupabaseAdminClient();
    await admin
      .from("profiles")
      .update({ onboarding_completed: true })
      .eq("id", u.user.id);
  }
  redirect("/dashboard");
}

export async function deleteWorkspaceAction(id: string) {
  const supabase = await createSupabaseServerClient();
  const { error } = await supabase.from("workspaces").delete().eq("id", id);
  if (error) return { ok: false as const, error: error.message };
  revalidatePath("/workspaces");
  return { ok: true as const };
}
""",
)

# ===================================================================
# components/app/Sidebar.tsx
# ===================================================================
write(
    "components/app/Sidebar.tsx",
    """import Link from "next/link";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/workspaces", label: "Workspaces" },
  { href: "/audits", label: "Insight Audits" },
  { href: "/evidence", label: "Evidence Ledger" },
  { href: "/snapshots", label: "Dataset Snapshots" },
  { href: "/admin", label: "Admin" },
  { href: "/profile", label: "Profile" },
  { href: "/settings", label: "Settings" },
];

export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 border-r border-gridline bg-panel lg:block">
      <div className="px-5 py-5">
        <Link href="/dashboard" className="display text-lg font-bold text-obsidian">
          VeriSight
        </Link>
        <div className="mono mt-1 text-[10px] uppercase tracking-[0.18em] text-consensus">
          Audit terminal
        </div>
      </div>
      <nav className="px-2 pb-4">
        {links.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className="block rounded-btn px-3 py-2 text-sm text-ink hover:bg-graphite"
          >
            {l.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
""",
)

# ===================================================================
# components/app/Topbar.tsx
# ===================================================================
write(
    "components/app/Topbar.tsx",
    """import Link from "next/link";
import { logoutAction } from "@/lib/auth/actions";

export function Topbar({ email, displayName }: { email: string; displayName?: string | null }) {
  return (
    <header className="flex items-center justify-between border-b border-gridline bg-panel px-6 py-3">
      <div>
        <div className="text-xs text-slate">Signed in as</div>
        <div className="text-sm font-medium text-ink">
          {displayName ?? email}
        </div>
      </div>
      <div className="flex items-center gap-3">
        <Link href="/audits/new" className="btn-primary">
          Audit an insight
        </Link>
        <form action={logoutAction}>
          <button type="submit" className="btn-secondary">
            Sign out
          </button>
        </form>
      </div>
    </header>
  );
}
""",
)

# ===================================================================
# app/(app)/layout.tsx
# ===================================================================
write(
    "app/(app)/layout.tsx",
    """import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { Sidebar } from "@/components/app/Sidebar";
import { Topbar } from "@/components/app/Topbar";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, profile } = await getProfile();
  if (!profile) redirect("/login");

  return (
    <div className="flex min-h-screen bg-graphite">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar email={user.email ?? ""} displayName={profile.display_name} />
        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
""",
)

# ===================================================================
# app/(app)/dashboard/page.tsx — minimal; expanded in Stage 9
# ===================================================================
write(
    "app/(app)/dashboard/page.tsx",
    """import Link from "next/link";
import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { Panel } from "@/components/ui/Panel";

export default async function DashboardPage() {
  const { profile, supabase } = await getProfile();
  if (!profile?.onboarding_completed) redirect("/onboarding");

  const { count: workspaceCount } = await supabase
    .from("workspaces")
    .select("*", { count: "exact", head: true });
  const { count: auditCount } = await supabase
    .from("insight_audit_cases")
    .select("*", { count: "exact", head: true });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="display text-pagetitle font-semibold text-obsidian">
          Welcome back, {profile.display_name ?? "analyst"}
        </h1>
        <p className="text-sm text-slate">
          VeriSight is your trust layer for analytics claims. Every verdict is judged by
          GenLayer consensus.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Panel className="p-5">
          <div className="text-xs uppercase tracking-wide text-slate">Workspaces</div>
          <div className="display mt-1 text-pagetitle font-semibold text-obsidian">
            {workspaceCount ?? 0}
          </div>
          <Link href="/workspaces" className="mt-2 inline-block text-sm text-analyst underline">
            Manage workspaces
          </Link>
        </Panel>
        <Panel className="p-5">
          <div className="text-xs uppercase tracking-wide text-slate">Insight audits</div>
          <div className="display mt-1 text-pagetitle font-semibold text-obsidian">
            {auditCount ?? 0}
          </div>
          <Link href="/audits/new" className="mt-2 inline-block text-sm text-analyst underline">
            Audit an insight
          </Link>
        </Panel>
        <Panel className="p-5">
          <div className="mono text-xs uppercase tracking-[0.18em] text-consensus">
            Source of truth
          </div>
          <div className="display mt-1 text-cardtitle font-semibold text-obsidian">
            GenLayer Intelligent Contract
          </div>
          <p className="mt-2 text-sm text-slate">
            Verdicts are produced by validator consensus, not by VeriSight.
          </p>
        </Panel>
      </div>

      <Panel className="p-5">
        <div className="text-xs uppercase tracking-wide text-slate">Next step</div>
        <p className="mt-2 text-sm text-ink">
          Create an insight audit case — submit a dashboard claim, attach evidence, and let
          GenLayer validators decide whether the data supports it.
        </p>
        <Link href="/audits/new" className="btn-primary mt-3 inline-block">
          Audit an insight
        </Link>
      </Panel>
    </div>
  );
}
""",
)

# ===================================================================
# app/(app)/workspaces/page.tsx
# ===================================================================
write(
    "app/(app)/workspaces/page.tsx",
    """import Link from "next/link";
import { requireUser } from "@/lib/auth/getUser";
import { Panel } from "@/components/ui/Panel";
import { CreateWorkspaceForm } from "./CreateWorkspaceForm";

export default async function WorkspacesPage() {
  const { supabase } = await requireUser();
  const { data: workspaces } = await supabase
    .from("workspaces")
    .select("id,name,organisation_name,business_function,industry,primary_kpi_category,created_at")
    .order("created_at", { ascending: false });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="display text-pagetitle font-semibold text-obsidian">Workspaces</h1>
          <p className="text-sm text-slate">
            One workspace per company, team, client, or project.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[2fr_1fr]">
        <Panel className="overflow-hidden">
          <div className="border-b border-gridline px-5 py-3 text-xs uppercase tracking-wide text-slate">
            Your workspaces
          </div>
          {workspaces && workspaces.length > 0 ? (
            <table className="w-full text-sm">
              <thead className="bg-graphite text-left text-xs uppercase tracking-wide text-slate">
                <tr>
                  <th className="px-5 py-2">Name</th>
                  <th className="px-5 py-2">Organisation</th>
                  <th className="px-5 py-2">Function</th>
                  <th className="px-5 py-2">KPI category</th>
                </tr>
              </thead>
              <tbody>
                {workspaces.map((w) => (
                  <tr key={w.id} className="border-t border-gridline hover:bg-graphite">
                    <td className="px-5 py-3">
                      <Link href={`/workspaces/${w.id}`} className="text-ink hover:underline">
                        {w.name}
                      </Link>
                    </td>
                    <td className="px-5 py-3 text-slate">{w.organisation_name ?? "—"}</td>
                    <td className="px-5 py-3 text-slate">{w.business_function ?? "—"}</td>
                    <td className="px-5 py-3 text-slate">{w.primary_kpi_category ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="px-5 py-10 text-center text-sm text-slate">
              No workspaces yet. Create one to start auditing insights.
            </div>
          )}
        </Panel>

        <Panel className="p-5">
          <div className="text-xs uppercase tracking-wide text-slate">Create workspace</div>
          <CreateWorkspaceForm />
        </Panel>
      </div>
    </div>
  );
}
""",
)

# ===================================================================
# app/(app)/workspaces/CreateWorkspaceForm.tsx
# ===================================================================
write(
    "app/(app)/workspaces/CreateWorkspaceForm.tsx",
    """"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { createWorkspaceAction } from "@/lib/workspaces/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";

const FUNCTIONS = ["Analytics", "Finance", "Growth", "Operations", "Product", "Executive"];
const CADENCES = ["Daily", "Weekly", "Monthly", "Quarterly"];
const KPIS = ["Revenue", "Retention", "Acquisition", "Conversion", "Efficiency", "Quality"];

export function CreateWorkspaceForm() {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  return (
    <form
      className="mt-3 space-y-3"
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
        <select
          name="business_function"
          className="w-full rounded-btn border border-gridline bg-panel px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-analyst"
        >
          <option value="">Select…</option>
          {FUNCTIONS.map((v) => (
            <option key={v}>{v}</option>
          ))}
        </select>
      </Field>
      <Field label="Industry">
        <Input name="industry" placeholder="SaaS, e-commerce, fintech…" />
      </Field>
      <Field label="Reporting cadence">
        <select
          name="reporting_cadence"
          className="w-full rounded-btn border border-gridline bg-panel px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-analyst"
        >
          <option value="">Select…</option>
          {CADENCES.map((v) => (
            <option key={v}>{v}</option>
          ))}
        </select>
      </Field>
      <Field label="Primary KPI category">
        <select
          name="primary_kpi_category"
          className="w-full rounded-btn border border-gridline bg-panel px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-analyst"
        >
          <option value="">Select…</option>
          {KPIS.map((v) => (
            <option key={v}>{v}</option>
          ))}
        </select>
      </Field>
      {error ? (
        <div className="rounded-btn border border-claim/40 bg-claim/5 p-2 text-xs text-claim">
          {error}
        </div>
      ) : null}
      <Button type="submit" className="w-full" disabled={pending}>
        {pending ? "Creating…" : "Create workspace"}
      </Button>
    </form>
  );
}
""",
)

# ===================================================================
# app/(app)/workspaces/[id]/page.tsx
# ===================================================================
write(
    "app/(app)/workspaces/[id]/page.tsx",
    """import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/auth/getUser";
import { Panel } from "@/components/ui/Panel";

export default async function WorkspaceDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const { supabase } = await requireUser();

  const { data: workspace } = await supabase
    .from("workspaces")
    .select("*")
    .eq("id", id)
    .single();
  if (!workspace) notFound();

  const { data: audits } = await supabase
    .from("insight_audit_cases")
    .select("id,insight_claim,status,created_at")
    .eq("workspace_id", id)
    .order("created_at", { ascending: false });

  return (
    <div className="space-y-6">
      <div>
        <Link href="/workspaces" className="text-xs text-slate hover:underline">
          ← Workspaces
        </Link>
        <h1 className="display mt-1 text-pagetitle font-semibold text-obsidian">
          {workspace.name}
        </h1>
        <p className="text-sm text-slate">{workspace.organisation_name ?? "—"}</p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {[
          ["Business function", workspace.business_function],
          ["Industry", workspace.industry],
          ["Reporting cadence", workspace.reporting_cadence],
          ["Primary KPI category", workspace.primary_kpi_category],
        ].map(([label, val]) => (
          <Panel key={String(label)} className="p-4">
            <div className="text-xs uppercase tracking-wide text-slate">{label}</div>
            <div className="mt-1 text-sm text-ink">{val ?? "—"}</div>
          </Panel>
        ))}
      </div>

      <Panel>
        <div className="flex items-center justify-between border-b border-gridline px-5 py-3">
          <div className="text-xs uppercase tracking-wide text-slate">
            Insight audit cases
          </div>
          <Link href={`/audits/new?workspace=${workspace.id}`} className="btn-primary text-xs">
            New audit
          </Link>
        </div>
        {audits && audits.length > 0 ? (
          <table className="w-full text-sm">
            <thead className="bg-graphite text-left text-xs uppercase tracking-wide text-slate">
              <tr>
                <th className="px-5 py-2">Claim</th>
                <th className="px-5 py-2">Status</th>
                <th className="px-5 py-2">Created</th>
              </tr>
            </thead>
            <tbody>
              {audits.map((a) => (
                <tr key={a.id} className="border-t border-gridline hover:bg-graphite">
                  <td className="px-5 py-3">
                    <Link href={`/audits/${a.id}`} className="text-ink hover:underline">
                      {a.insight_claim}
                    </Link>
                  </td>
                  <td className="px-5 py-3 text-slate">{a.status}</td>
                  <td className="px-5 py-3 text-slate">
                    {new Date(a.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="px-5 py-10 text-center text-sm text-slate">
            No audit cases yet for this workspace.
          </div>
        )}
      </Panel>
    </div>
  );
}
""",
)

# ===================================================================
# app/(app)/onboarding/page.tsx
# ===================================================================
write(
    "app/(app)/onboarding/page.tsx",
    """import { redirect } from "next/navigation";
import { getProfile } from "@/lib/auth/getUser";
import { Panel } from "@/components/ui/Panel";
import { OnboardingForm } from "./OnboardingForm";

export default async function OnboardingPage() {
  const { profile } = await getProfile();
  if (profile?.onboarding_completed) redirect("/dashboard");

  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <div>
        <div className="mono text-xs uppercase tracking-[0.18em] text-consensus">
          Step 1 of 1
        </div>
        <h1 className="display mt-2 text-pagetitle font-semibold text-obsidian">
          Set up your first analytics workspace
        </h1>
        <p className="mt-2 text-sm text-slate">
          A workspace groups one company, team, client, or project. You can add more later.
        </p>
      </div>
      <Panel className="p-6">
        <OnboardingForm />
      </Panel>
    </div>
  );
}
""",
)

# ===================================================================
# app/(app)/onboarding/OnboardingForm.tsx
# ===================================================================
write(
    "app/(app)/onboarding/OnboardingForm.tsx",
    """"use client";

import { useState, useTransition } from "react";
import { completeOnboardingAction } from "@/lib/workspaces/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";

export function OnboardingForm() {
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  return (
    <form
      className="space-y-4"
      action={(fd) => {
        setError(null);
        start(async () => {
          const res = await completeOnboardingAction(fd);
          // redirects on success; only see a return value on failure.
          if (res && "ok" in res && !res.ok) setError(res.error);
        });
      }}
    >
      <Field label="Workspace name">
        <Input name="name" required placeholder="Acme Analytics" />
      </Field>
      <Field label="Organisation">
        <Input name="organisation_name" placeholder="Acme Inc." />
      </Field>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Field label="Business function">
          <select
            name="business_function"
            className="w-full rounded-btn border border-gridline bg-panel px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-analyst"
          >
            <option value="">Select…</option>
            {["Analytics", "Finance", "Growth", "Operations", "Product", "Executive"].map((v) => (
              <option key={v}>{v}</option>
            ))}
          </select>
        </Field>
        <Field label="Industry">
          <Input name="industry" placeholder="SaaS, e-commerce…" />
        </Field>
        <Field label="Reporting cadence">
          <select
            name="reporting_cadence"
            className="w-full rounded-btn border border-gridline bg-panel px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-analyst"
          >
            <option value="">Select…</option>
            {["Daily", "Weekly", "Monthly", "Quarterly"].map((v) => (
              <option key={v}>{v}</option>
            ))}
          </select>
        </Field>
        <Field label="Primary KPI category">
          <select
            name="primary_kpi_category"
            className="w-full rounded-btn border border-gridline bg-panel px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-analyst"
          >
            <option value="">Select…</option>
            {["Revenue", "Retention", "Acquisition", "Conversion", "Efficiency", "Quality"].map(
              (v) => (
                <option key={v}>{v}</option>
              ),
            )}
          </select>
        </Field>
      </div>
      {error ? (
        <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">
          {error}
        </div>
      ) : null}
      <Button type="submit" className="w-full" disabled={pending}>
        {pending ? "Creating…" : "Create workspace and continue"}
      </Button>
    </form>
  );
}
""",
)

print("\nStage 4 files written.")
