"use client";

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
