"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { pollVerdictAction } from "@/lib/audit/actions";

export function PollVerdictButton({ auditId }: { auditId: string }) {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [msg, setMsg] = useState<string | null>(null);

  return (
    <div className="flex items-center gap-3">
      <Button
        type="button"
        variant="consensus"
        disabled={pending}
        onClick={() => {
          setMsg(null);
          start(async () => {
            const res = await pollVerdictAction(auditId);
            if (!res.ok) {
              setMsg(res.error ?? "Sync failed");
              return;
            }
            if (res.status === "reached") {
              setMsg(`Verdict synced: ${res.verdict}`);
              router.refresh();
            } else {
              setMsg("Consensus pending — validators still reasoning. Try again in a moment.");
            }
          });
        }}
      >
        {pending ? "Reading contract…" : "Sync GenLayer Result"}
      </Button>
      {msg ? <span className="text-[12.5px] text-slate">{msg}</span> : null}
    </div>
  );
}
