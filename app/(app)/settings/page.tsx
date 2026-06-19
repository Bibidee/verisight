import { getProfile } from "@/lib/auth/getUser";
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
