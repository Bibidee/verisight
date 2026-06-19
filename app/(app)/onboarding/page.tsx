import { redirect } from "next/navigation";
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
