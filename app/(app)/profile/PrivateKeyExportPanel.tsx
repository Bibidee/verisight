"use client";

import { useState, useTransition } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Badge } from "@/components/audit/Badge";
import { exportPrivateKeyAction } from "@/lib/auth/actions";

export function PrivateKeyExportPanel() {
  const [open, setOpen] = useState(false);
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [revealed, setRevealed] = useState<{ address: string; privateKey: string } | null>(null);

  function close() {
    setOpen(false);
    setRevealed(null);
    setError(null);
  }

  return (
    <>
      <article className="doc">
        <div className="border-b border-auditline px-5 py-3">
          <div className="eyebrow eyebrow-slate">Security</div>
          <div className="display text-[15px] font-semibold text-ink">Private key export</div>
        </div>
        <div className="space-y-3 px-5 py-4 text-sm">
          <div className="flex items-center justify-between border-b border-auditline pb-2">
            <span className="text-slate">Re-authentication</span>
            <Badge tone="amber" dot>Required</Badge>
          </div>
          <div className="flex items-center justify-between border-b border-auditline pb-2">
            <span className="text-slate">Recovery phrase</span>
            <Badge tone="amber" dot>Required</Badge>
          </div>
          <div className="flex items-center justify-between border-b border-auditline pb-2">
            <span className="text-slate">Audit log</span>
            <Badge tone="verified" dot>Recorded</Badge>
          </div>
          <p className="text-[12.5px] text-slate">
            Exporting your private key reveals the signing key of your embedded wallet. Only export
            if you are migrating to a self-custody wallet. VeriSight cannot recover an exported key.
          </p>
          <Button type="button" variant="danger" onClick={() => setOpen(true)}>
            Export private key
          </Button>
        </div>
      </article>

      {open ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-audit-black/70 p-4"
          role="dialog"
          aria-modal="true"
        >
          <div className="w-full max-w-md doc overflow-hidden">
            <div className="doc-header">
              <div>
                <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
                  Private key export
                </div>
                <div className="display text-[16px] font-semibold">Strong re-authentication</div>
              </div>
              <Badge tone="claim" dot>Danger</Badge>
            </div>
            <div className="doc-body">
              {revealed ? (
                <div className="space-y-3">
                  <Field label="Wallet address">
                    <div className="hash break-all">{revealed.address}</div>
                  </Field>
                  <Field label="Private key" hint="Copy now — VeriSight will not show this again.">
                    <div className="hash break-all">{revealed.privateKey}</div>
                  </Field>
                  <p className="text-[12px] text-claim">
                    Anyone with this key can sign GenLayer transactions as you. Store it offline.
                  </p>
                </div>
              ) : (
                <form
                  className="space-y-3"
                  action={(fd) => {
                    setError(null);
                    start(async () => {
                      const res = await exportPrivateKeyAction(fd);
                      if (!res.ok) setError(res.error);
                      else
                        setRevealed({
                          address: res.address ?? "",
                          privateKey: res.privateKey ?? "",
                        });
                    });
                  }}
                >
                  <Field label="Current password">
                    <Input type="password" name="password" required minLength={8} />
                  </Field>
                  <Field label="Recovery phrase" hint="24 words from your signup.">
                    <textarea
                      name="recoveryPhrase"
                      required
                      rows={3}
                      className="input mono"
                      placeholder="word1 word2 word3 …"
                    />
                  </Field>
                  {error ? (
                    <div className="rounded-btn border border-claim/40 bg-claim/5 p-2 text-xs text-claim">
                      {error}
                    </div>
                  ) : null}
                  <Button type="submit" variant="danger" className="w-full" disabled={pending}>
                    {pending ? "Verifying…" : "Reveal private key"}
                  </Button>
                </form>
              )}
            </div>
            <div className="doc-footer">
              <span className="text-[12px] text-slate">
                {revealed ? "Stored. Close to clear from screen." : "Both checks must pass."}
              </span>
              <Button type="button" variant="secondary" onClick={close}>
                {revealed ? "Done" : "Cancel"}
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
