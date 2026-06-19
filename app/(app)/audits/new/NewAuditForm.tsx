"use client";

import { useState, useTransition, useRef } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Badge } from "@/components/audit/Badge";
import { SourceOfTruthBadge } from "@/components/audit/SourceOfTruthBadge";
import {
  EvidenceInspectorDrawer,
  InspectorRow,
} from "@/components/audit/EvidenceInspectorDrawer";
import {
  createAuditCaseAction,
  prepareAuditPacketAction,
  uploadEvidenceAction,
} from "@/lib/audit/actions";

type Workspace = {
  id: string;
  name: string;
  organisation_name: string | null;
  primary_kpi_category: string | null;
};

const ACCEPT = ".jpg,.jpeg,.png,.webp,.pdf,.csv,.json";

export function NewAuditForm({
  workspaces,
  initialWorkspaceId,
}: {
  workspaces: Workspace[];
  initialWorkspaceId: string;
}) {
  const router = useRouter();
  const formRef = useRef<HTMLFormElement>(null);
  const [pending, start] = useTransition();
  const [uploadPending, startUpload] = useTransition();
  const [submitPending, startSubmit] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [draftId, setDraftId] = useState<string | null>(null);
  const [evidenceCount, setEvidenceCount] = useState(0);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  // Readiness tracking
  const [vals, setVals] = useState({
    insight_claim: "",
    metric_name: "",
    metric_definition: "",
    time_period: "",
    dataset_summary: "",
    candidate_interpretation_a: "",
    candidate_interpretation_b: "",
    candidate_interpretation_c: "",
  });

  const readiness = computeReadiness(vals, evidenceCount);

  function onSaveDraft(fd: FormData) {
    setError(null);
    start(async () => {
      const res = await createAuditCaseAction(fd);
      if (!res.ok) {
        setError(res.error);
        return;
      }
      setDraftId(res.id);
    });
  }

  function onUpload() {
    if (!draftId) {
      setError("Save the draft before uploading evidence.");
      return;
    }
    if (selectedFiles.length === 0) {
      setError("Select at least one file.");
      return;
    }
    const fd = new FormData();
    for (const f of selectedFiles) fd.append("files", f);
    setError(null);
    startUpload(async () => {
      const res = await uploadEvidenceAction(draftId, fd);
      if (!res.ok) {
        setError(res.error ?? "Upload failed");
        return;
      }
      setEvidenceCount((n) => n + (res.count ?? 0));
      setSelectedFiles([]);
    });
  }

  function onSubmitForJudgment() {
    if (!draftId) return;
    setError(null);
    startSubmit(async () => {
      const res = await prepareAuditPacketAction(draftId);
      if (!res.ok) {
        setError(res.error ?? "Could not prepare packet");
        return;
      }
      router.push(`/audits/${draftId}`);
    });
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
      <form
        ref={formRef}
        action={onSaveDraft}
        className="space-y-4"
        onChange={(e) => {
          const target = e.target as unknown as { name?: string; value?: string };
          const name = target.name;
          if (name && name in vals) {
            setVals((v) => ({ ...v, [name]: target.value ?? "" }));
          }
        }}
      >
        {/* Step 1: workspace + claim */}
        <Doc step="Step 1 · State the claim">
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-[260px_1fr]">
            <Field label="Workspace">
              <select
                name="workspace_id"
                defaultValue={initialWorkspaceId}
                disabled={!!draftId}
                className="input"
              >
                {workspaces.map((w) => (
                  <option key={w.id} value={w.id}>{w.name}</option>
                ))}
              </select>
            </Field>
            <Field label="Insight claim under review" hint="The dashboard insight, KPI narrative, or AI-generated claim.">
              <textarea
                name="insight_claim"
                required
                minLength={8}
                rows={3}
                className="input"
              />
            </Field>
          </div>
          <div className="mt-4">
            <Field label="Business question (optional)">
              <Input name="business_question" />
            </Field>
          </div>
        </Doc>

        {/* Step 2: metric basis */}
        <Doc step="Step 2 · Attach metric basis">
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Field label="Metric name">
              <Input name="metric_name" />
            </Field>
            <Field label="Time period">
              <Input name="time_period" />
            </Field>
          </div>
          <div className="mt-4">
            <Field label="Metric definition" hint="How the metric is calculated, including filters.">
              <textarea name="metric_definition" rows={3} className="input" />
            </Field>
          </div>
        </Doc>

        {/* Step 3: reporting context */}
        <Doc step="Step 3 · Define reporting context">
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Field label="Segment / filter context">
              <Input name="segment_context" />
            </Field>
            <Field label="Dashboard context (optional)">
              <Input name="dashboard_context" />
            </Field>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Field label="Report context (optional)">
              <Input name="report_context" />
            </Field>
            <Field label="Analyst notes (optional)">
              <Input name="analyst_notes" />
            </Field>
          </div>
          <div className="mt-4">
            <Field label="Dataset summary" hint="What the dataset contains, its grain, freshness, and known limits.">
              <textarea name="dataset_summary" rows={3} className="input" />
            </Field>
          </div>
        </Doc>

        {/* Step 4: candidate interpretations */}
        <Doc step="Step 4 · Declare candidate interpretations" hint="Three competing readings of the claim. GenLayer validators choose which best fits the evidence.">
          <div className="grid grid-cols-1 gap-3">
            <Field label="Interpretation A">
              <Input name="candidate_interpretation_a" />
            </Field>
            <Field label="Interpretation B">
              <Input name="candidate_interpretation_b" />
            </Field>
            <Field label="Interpretation C">
              <Input name="candidate_interpretation_c" />
            </Field>
          </div>
        </Doc>

        {/* Save / draft state */}
        <div className="doc-footer rounded-panel border border-auditline">
          <div className="text-[12.5px] text-slate">
            {draftId
              ? <span className="flex items-center gap-2">Draft saved · <span className="hash">{draftId.slice(0, 8)}</span></span>
              : "Draft has not been saved yet."}
          </div>
          <div className="flex gap-2">
            {!draftId ? (
              <Button type="submit" variant="exec" disabled={pending}>
                {pending ? "Saving draft…" : "Save draft and continue"}
              </Button>
            ) : (
              <Badge tone="verified" dot>Draft saved</Badge>
            )}
          </div>
        </div>

        {/* Step 5: evidence */}
        {draftId ? (
          <Doc step="Step 5 · Attach evidence references" hint="CSV ≤ 3MB · JSON ≤ 1MB · PDF ≤ 5MB · images ≤ 2MB · max 4 files per audit.">
            <div className="rounded-panel border border-dashed border-auditline bg-frost-grey p-5">
              <input
                id="evidence-input"
                type="file"
                multiple
                accept={ACCEPT}
                className="hidden"
                onChange={(e) => setSelectedFiles(Array.from(e.target.files ?? []))}
              />
              <label htmlFor="evidence-input" className="btn-secondary cursor-pointer">
                Select files
              </label>
              <span className="ml-3 text-[12.5px] text-slate">
                {selectedFiles.length > 0
                  ? `${selectedFiles.length} file(s) selected`
                  : "No files selected"}
              </span>

              {selectedFiles.length > 0 ? (
                <ul className="mt-3 space-y-1.5 text-[12.5px]">
                  {selectedFiles.map((f, i) => (
                    <li key={i} className="flex items-center justify-between rounded border border-auditline bg-white-ledger px-3 py-1.5">
                      <span className="mono">{f.name}</span>
                      <span className="text-slate">{Math.round(f.size / 1024)} KB</span>
                    </li>
                  ))}
                </ul>
              ) : null}

              <div className="mt-3 flex items-center justify-between">
                <span className="text-[12px] text-slate">
                  {evidenceCount} attached to this audit
                </span>
                <Button
                  type="button"
                  variant="exec"
                  onClick={onUpload}
                  disabled={uploadPending || selectedFiles.length === 0}
                >
                  {uploadPending ? "Uploading…" : "Upload evidence"}
                </Button>
              </div>
            </div>
          </Doc>
        ) : null}

        {/* Step 6: Judgment request */}
        {draftId ? (
          <article className="doc overflow-hidden">
            <div className="doc-header">
              <div>
                <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
                  Step 6 · Judgment request
                </div>
                <div className="display text-[16px] font-semibold">
                  Request GenLayer judgment
                </div>
              </div>
              <SourceOfTruthBadge small />
            </div>
            <div className="doc-body text-[13.5px] leading-relaxed text-ink">
              VeriSight will submit this claim, metric context, evidence references, and
              candidate interpretations to GenLayer. The frontend and Supabase do not decide
              whether the claim is supported. GenLayer validators independently review the
              evidence and produce the authoritative audit verdict.
            </div>
            <div className="doc-footer">
              <span className="text-[12.5px] text-slate">
                Readiness · {readiness.score}% ({readiness.missing.length === 0 ? "ready" : `missing ${readiness.missing.length}`})
              </span>
              <Button
                type="button"
                variant="consensus"
                disabled={!readiness.ready || submitPending}
                onClick={onSubmitForJudgment}
              >
                {submitPending ? "Preparing packet…" : "Request GenLayer judgment"}
              </Button>
            </div>
          </article>
        ) : null}

        {error ? (
          <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">
            {error}
          </div>
        ) : null}
      </form>

      {/* Inspector drawer */}
      <EvidenceInspectorDrawer title="Packet readiness">
        <InspectorRow
          left="Claim"
          right={vals.insight_claim ? <Badge tone="verified" dot>Yes</Badge> : <Badge tone="amber" dot>Missing</Badge>}
        />
        <InspectorRow
          left="Metric basis"
          right={vals.metric_name && vals.metric_definition ? <Badge tone="verified" dot>Yes</Badge> : <Badge tone="amber" dot>Partial</Badge>}
        />
        <InspectorRow
          left="Time period"
          right={vals.time_period ? <Badge tone="verified" dot>Yes</Badge> : <Badge tone="amber" dot>Missing</Badge>}
        />
        <InspectorRow
          left="Dataset summary"
          right={vals.dataset_summary ? <Badge tone="verified" dot>Yes</Badge> : <Badge tone="amber" dot>Missing</Badge>}
        />
        <InspectorRow
          left="Interpretations"
          right={
            <span className="mono">
              {[vals.candidate_interpretation_a, vals.candidate_interpretation_b, vals.candidate_interpretation_c].filter(Boolean).length} / 3
            </span>
          }
        />
        <InspectorRow
          left="Evidence files"
          right={<span className="mono">{evidenceCount} / 4</span>}
        />
        <InspectorRow
          left="Readiness"
          right={readiness.ready ? <Badge tone="verified" dot>Ready</Badge> : <Badge tone="amber" dot>{readiness.score}%</Badge>}
        />
        {draftId ? (
          <InspectorRow left="Draft" right={<span className="hash-dark">{draftId.slice(0, 8)}</span>} />
        ) : null}
      </EvidenceInspectorDrawer>
    </div>
  );
}

function Doc({
  step,
  hint,
  children,
}: {
  step: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <article className="doc">
      <div className="border-b border-auditline px-5 py-3">
        <div className="eyebrow eyebrow-slate">{step}</div>
        {hint ? <p className="mt-1 text-[12.5px] text-slate">{hint}</p> : null}
      </div>
      <div className="docket-lines px-5 py-5">{children}</div>
    </article>
  );
}

function computeReadiness(
  v: {
    insight_claim: string;
    metric_name: string;
    metric_definition: string;
    time_period: string;
    dataset_summary: string;
    candidate_interpretation_a: string;
    candidate_interpretation_b: string;
    candidate_interpretation_c: string;
  },
  evidenceCount: number,
) {
  const checks: { name: string; ok: boolean }[] = [
    { name: "claim",             ok: v.insight_claim.length >= 8 },
    { name: "metric name",       ok: !!v.metric_name },
    { name: "metric definition", ok: !!v.metric_definition },
    { name: "time period",       ok: !!v.time_period },
    { name: "dataset summary",   ok: !!v.dataset_summary },
    { name: "interpretations",   ok: !!v.candidate_interpretation_a && !!v.candidate_interpretation_b },
    { name: "evidence",          ok: evidenceCount > 0 },
  ];
  const passed = checks.filter((c) => c.ok).length;
  const score = Math.round((passed / checks.length) * 100);
  return {
    score,
    ready: passed === checks.length,
    missing: checks.filter((c) => !c.ok).map((c) => c.name),
  };
}
