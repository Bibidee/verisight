"use client";

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
