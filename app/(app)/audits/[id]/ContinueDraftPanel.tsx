"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Badge } from "@/components/audit/Badge";
import {
  uploadEvidenceAction,
  prepareAuditPacketAction,
  patchAuditDraftAction,
} from "@/lib/audit/actions";

const ACCEPT = ".jpg,.jpeg,.png,.webp,.pdf,.csv,.json";

type Props = {
  auditId: string;
  existingEvidenceCount: number;
  initialFields: {
    metric_name: string | null;
    metric_definition: string | null;
    time_period: string | null;
    dataset_summary: string | null;
    candidate_interpretation_a: string | null;
    candidate_interpretation_b: string | null;
    candidate_interpretation_c: string | null;
    segment_context: string | null;
  };
};

export function ContinueDraftPanel({ auditId, existingEvidenceCount, initialFields }: Props) {
  const router = useRouter();
  const [savePending, startSave] = useTransition();
  const [uploadPending, startUpload] = useTransition();
  const [submitPending, startSubmit] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [evidenceCount, setEvidenceCount] = useState(existingEvidenceCount);

  function onSaveFields(fd: FormData) {
    setError(null);
    setSuccess(null);
    startSave(async () => {
      const res = await patchAuditDraftAction(auditId, fd);
      if (!res.ok) { setError(res.error ?? "Save failed"); return; }
      setSuccess("Fields saved.");
    });
  }

  function onUpload() {
    if (selectedFiles.length === 0) { setError("Select at least one file."); return; }
    const fd = new FormData();
    for (const f of selectedFiles) fd.append("files", f);
    setError(null);
    startUpload(async () => {
      const res = await uploadEvidenceAction(auditId, fd);
      if (!res.ok) { setError(res.error ?? "Upload failed"); return; }
      setEvidenceCount((n) => n + (res.count ?? 0));
      setSelectedFiles([]);
    });
  }

  function onSubmit() {
    setError(null);
    startSubmit(async () => {
      const res = await prepareAuditPacketAction(auditId);
      if (!res.ok) { setError(res.error ?? "Could not prepare packet"); return; }
      router.refresh();
    });
  }

  return (
    <div className="space-y-4">

      {/* Step 2–4 completion — fill any missing fields */}
      <form action={onSaveFields}>
        <article className="doc">
          <div className="border-b border-auditline px-5 py-3">
            <div className="eyebrow eyebrow-slate">Complete missing fields</div>
            <p className="mt-1 text-[12.5px] text-slate">
              Fill any blank fields then click Save before requesting judgment.
            </p>
          </div>
          <div className="px-5 py-5 space-y-4">
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <Field label="Metric name">
                <Input
                  name="metric_name"
                  defaultValue={initialFields.metric_name ?? ""}
                  placeholder="Quarterly net revenue by customer type"
                />
              </Field>
              <Field label="Time period">
                <Input
                  name="time_period"
                  defaultValue={initialFields.time_period ?? ""}
                  placeholder="Q3 2025"
                />
              </Field>
            </div>
            <Field label="Metric definition">
              <textarea
                name="metric_definition"
                defaultValue={initialFields.metric_definition ?? ""}
                rows={2}
                className="input"
                placeholder="Sum of net revenue grouped by customer_type for the selected quarter, excluding refunds."
              />
            </Field>
            <Field label="Dataset summary">
              <textarea
                name="dataset_summary"
                defaultValue={initialFields.dataset_summary ?? ""}
                rows={2}
                className="input"
                placeholder="fact_revenue snapshot from warehouse; row grain = order; refund-aware net revenue; refreshes hourly."
              />
            </Field>
            <div className="grid grid-cols-1 gap-3">
              <Field label="Interpretation A">
                <Input
                  name="candidate_interpretation_a"
                  defaultValue={initialFields.candidate_interpretation_a ?? ""}
                  placeholder="Repeat customers were the main driver of net new revenue."
                />
              </Field>
              <Field label="Interpretation B">
                <Input
                  name="candidate_interpretation_b"
                  defaultValue={initialFields.candidate_interpretation_b ?? ""}
                  placeholder="Repeat revenue grew but new-customer revenue and discounts were larger contributors."
                />
              </Field>
              <Field label="Interpretation C">
                <Input
                  name="candidate_interpretation_c"
                  defaultValue={initialFields.candidate_interpretation_c ?? ""}
                  placeholder="Growth is driven by segment-mix change, not by any one customer type."
                />
              </Field>
            </div>
          </div>
          <div className="doc-footer">
            {success && <span className="text-[12px] text-emerald-600">{success}</span>}
            <Button type="submit" variant="exec" disabled={savePending}>
              {savePending ? "Saving…" : "Save fields"}
            </Button>
          </div>
        </article>
      </form>

      {/* Step 5 – Evidence */}
      <article className="doc">
        <div className="border-b border-auditline px-5 py-3">
          <div className="eyebrow eyebrow-slate">Step 5 · Attach evidence references</div>
          <p className="mt-1 text-[12.5px] text-slate">
            CSV ≤ 3 MB · JSON ≤ 1 MB · PDF ≤ 5 MB · images ≤ 2 MB · max 4 files per audit.
          </p>
        </div>
        <div className="px-5 py-5">
          <div className="rounded-panel border border-dashed border-auditline bg-frost-grey p-5">
            <input
              id="evidence-resume"
              type="file"
              multiple
              accept={ACCEPT}
              className="hidden"
              onChange={(e) => setSelectedFiles(Array.from(e.target.files ?? []))}
            />
            <label htmlFor="evidence-resume" className="btn-secondary cursor-pointer">
              Select files
            </label>
            <span className="ml-3 text-[12.5px] text-slate">
              {selectedFiles.length > 0 ? `${selectedFiles.length} file(s) selected` : "No files selected"}
            </span>
            {selectedFiles.length > 0 && (
              <ul className="mt-3 space-y-1.5 text-[12.5px]">
                {selectedFiles.map((f, i) => (
                  <li key={i} className="flex items-center justify-between rounded border border-auditline bg-white-ledger px-3 py-1.5">
                    <span className="mono">{f.name}</span>
                    <span className="text-slate">{Math.round(f.size / 1024)} KB</span>
                  </li>
                ))}
              </ul>
            )}
            <div className="mt-3 flex items-center justify-between">
              <span className="text-[12px] text-slate">{evidenceCount} file(s) attached to this audit</span>
              <Button type="button" variant="exec" onClick={onUpload} disabled={uploadPending || selectedFiles.length === 0}>
                {uploadPending ? "Uploading…" : "Upload evidence"}
              </Button>
            </div>
          </div>
        </div>
      </article>

      {/* Step 6 – Judgment */}
      <article className="doc overflow-hidden">
        <div className="doc-header">
          <div>
            <div className="mono text-[10.5px] uppercase tracking-[0.18em] text-ledger-white/55">
              Step 6 · Judgment request
            </div>
            <div className="display text-[16px] font-semibold">Request GenLayer judgment</div>
          </div>
          <Badge tone="blue" dot>StudioNet</Badge>
        </div>
        <div className="doc-body text-[13.5px] leading-relaxed text-ink">
          VeriSight will submit this claim, metric context, evidence references, and candidate
          interpretations to GenLayer. Validators independently review the evidence and produce
          the authoritative audit verdict.
        </div>
        <div className="doc-footer">
          <span className="text-[12.5px] text-slate">
            {evidenceCount === 0
              ? "Add at least one evidence file before requesting judgment."
              : `${evidenceCount} evidence file(s) ready`}
          </span>
          <Button type="button" variant="consensus" disabled={submitPending || evidenceCount === 0} onClick={onSubmit}>
            {submitPending ? "Preparing packet…" : "Request GenLayer judgment"}
          </Button>
        </div>
      </article>

      {error && (
        <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">{error}</div>
      )}
    </div>
  );
}
