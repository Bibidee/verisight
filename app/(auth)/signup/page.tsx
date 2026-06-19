"use client";

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
    const words = recovery.phrase.split(/\s+/);
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
