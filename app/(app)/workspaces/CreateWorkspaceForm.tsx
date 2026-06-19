"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { createWorkspaceAction } from "@/lib/workspaces/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";

const FUNCS = ["Analytics", "Finance", "Growth", "Operations", "Product", "Executive"];
const CADENCES = ["Daily", "Weekly", "Monthly", "Quarterly"];
const KPIS = ["Revenue", "Retention", "Acquisition", "Conversion", "Efficiency", "Quality"];

export function CreateWorkspaceForm() {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  return (
    <form className="space-y-3"
      action={(fd) => {
        setError(null);
        start(async () => {
          const res = await createWorkspaceAction(fd);
          if (!res.ok) setError(res.error);
          else router.refresh();
        });
      }}
    >
      <Field label="Workspace name"><Input name="name" required placeholder="Acme Revenue Assurance" /></Field>
      <Field label="Organisation"><Input name="organisation_name" placeholder="Acme Inc." /></Field>
      <Field label="Business function">
        <select name="business_function" className="input">
          <option value="">Select…</option>{FUNCS.map((v) => <option key={v}>{v}</option>)}
        </select>
      </Field>
      <Field label="Industry"><Input name="industry" placeholder="SaaS, e-commerce…" /></Field>
      <Field label="Reporting cadence">
        <select name="reporting_cadence" className="input">
          <option value="">Select…</option>{CADENCES.map((v) => <option key={v}>{v}</option>)}
        </select>
      </Field>
      <Field label="Primary KPI category">
        <select name="primary_kpi_category" className="input">
          <option value="">Select…</option>{KPIS.map((v) => <option key={v}>{v}</option>)}
        </select>
      </Field>
      {error ? <div className="rounded-btn border border-claim/40 bg-claim/5 p-2 text-xs text-claim">{error}</div> : null}
      <Button type="submit" variant="exec" className="w-full" disabled={pending}>
        {pending ? "Opening…" : "Open workspace"}
      </Button>
    </form>
  );
}
