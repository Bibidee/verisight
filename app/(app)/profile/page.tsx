import { getProfile } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { SigningInfrastructureCard } from "@/components/audit/SigningInfrastructureCard";
import { PrivateKeyExportPanel } from "./PrivateKeyExportPanel";

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

        <PrivateKeyExportPanel />
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
