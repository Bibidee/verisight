"use client";

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
