"""Stage 5 — Open Claim Review: real form + evidence upload.

Writes:
 - lib/audit/hash.ts                     sha256 helper for browser/server
 - lib/audit/actions.ts                  server actions:
     createAuditCase, updateAuditCase, uploadEvidence,
     deleteEvidence, prepareAuditPacket
 - app/(app)/audits/new/page.tsx         server page (auth + workspaces query)
 - app/(app)/audits/new/NewAuditForm.tsx client form with evidence upload
 - app/(app)/audits/[id]/page.tsx        adds evidence + draft-edit affordances
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def write(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {rel}")


# ===================================================================
# lib/audit/hash.ts
# ===================================================================
write(
    "lib/audit/hash.ts",
    """// SHA-256 helper for evidence digests. Works in both server and browser.
import { webcrypto as nodeCrypto } from "node:crypto";

const subtle = (nodeCrypto as Crypto).subtle;

export async function sha256Hex(bytes: Uint8Array | ArrayBuffer): Promise<string> {
  const buf = bytes instanceof Uint8Array
    ? (() => {
        const ab = new ArrayBuffer(bytes.byteLength);
        new Uint8Array(ab).set(bytes);
        return ab;
      })()
    : bytes;
  const digest = await subtle.digest("SHA-256", buf);
  return [...new Uint8Array(digest)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}
""",
)

# ===================================================================
# lib/audit/actions.ts
# ===================================================================
write(
    "lib/audit/actions.ts",
    """"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { createSupabaseAdminClient } from "@/lib/supabase/admin";
import { sha256Hex } from "./hash";

const AuditCaseSchema = z.object({
  workspace_id: z.string().uuid(),
  insight_claim: z.string().min(8, "Claim is too short").max(600),
  business_question: z.string().max(600).optional().nullable(),
  metric_name: z.string().max(160).optional().nullable(),
  metric_definition: z.string().max(800).optional().nullable(),
  time_period: z.string().max(120).optional().nullable(),
  segment_context: z.string().max(400).optional().nullable(),
  dataset_summary: z.string().max(800).optional().nullable(),
  dashboard_context: z.string().max(400).optional().nullable(),
  report_context: z.string().max(400).optional().nullable(),
  analyst_notes: z.string().max(800).optional().nullable(),
  candidate_interpretation_a: z.string().max(400).optional().nullable(),
  candidate_interpretation_b: z.string().max(400).optional().nullable(),
  candidate_interpretation_c: z.string().max(400).optional().nullable(),
});

function readForm(fd: FormData) {
  const out: Record<string, string | null> = {};
  for (const k of [
    "workspace_id",
    "insight_claim",
    "business_question",
    "metric_name",
    "metric_definition",
    "time_period",
    "segment_context",
    "dataset_summary",
    "dashboard_context",
    "report_context",
    "analyst_notes",
    "candidate_interpretation_a",
    "candidate_interpretation_b",
    "candidate_interpretation_c",
  ]) {
    const v = fd.get(k);
    out[k] = v ? String(v) : null;
  }
  return out;
}

export type CreateAuditResult =
  | { ok: true; id: string }
  | { ok: false; error: string };

export async function createAuditCaseAction(
  formData: FormData,
): Promise<CreateAuditResult> {
  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (!u.user) return { ok: false, error: "Not signed in" };

  const parsed = AuditCaseSchema.safeParse(readForm(formData));
  if (!parsed.success) {
    return { ok: false, error: parsed.error.issues[0]?.message ?? "Invalid input" };
  }

  const { data, error } = await supabase
    .from("insight_audit_cases")
    .insert({
      ...parsed.data,
      user_id: u.user.id,
      status: "draft",
    })
    .select("id")
    .single();
  if (error || !data) {
    return { ok: false, error: error?.message ?? "Could not create audit case" };
  }

  revalidatePath("/audits");
  revalidatePath("/dashboard");
  return { ok: true, id: data.id };
}

export async function updateAuditCaseAction(
  auditId: string,
  formData: FormData,
): Promise<{ ok: boolean; error?: string }> {
  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (!u.user) return { ok: false, error: "Not signed in" };

  const parsed = AuditCaseSchema.safeParse(readForm(formData));
  if (!parsed.success) {
    return { ok: false, error: parsed.error.issues[0]?.message ?? "Invalid input" };
  }

  const { error } = await supabase
    .from("insight_audit_cases")
    .update({ ...parsed.data })
    .eq("id", auditId);
  if (error) return { ok: false, error: error.message };
  revalidatePath(`/audits/${auditId}`);
  return { ok: true };
}

const MAX = {
  image: 2 * 1024 * 1024,
  pdf:   5 * 1024 * 1024,
  csv:   3 * 1024 * 1024,
  json:  1 * 1024 * 1024,
};
const ALLOWED = new Set(["jpg", "jpeg", "png", "webp", "pdf", "csv", "json"]);
const MAX_PER_CASE = 4;

function extOf(name: string): string {
  const m = name.toLowerCase().match(/\\.([a-z0-9]+)$/);
  return m ? m[1] : "";
}
function maxFor(ext: string): number {
  if (["jpg", "jpeg", "png", "webp"].includes(ext)) return MAX.image;
  if (ext === "pdf") return MAX.pdf;
  if (ext === "csv") return MAX.csv;
  if (ext === "json") return MAX.json;
  return 0;
}

export async function uploadEvidenceAction(
  auditId: string,
  formData: FormData,
): Promise<{ ok: boolean; error?: string; count?: number }> {
  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (!u.user) return { ok: false, error: "Not signed in" };

  // Confirm ownership.
  const { data: ac } = await supabase
    .from("insight_audit_cases")
    .select("id,user_id,status")
    .eq("id", auditId)
    .single();
  if (!ac || ac.user_id !== u.user.id) {
    return { ok: false, error: "Audit case not found" };
  }

  const { count: existing } = await supabase
    .from("evidence_files")
    .select("*", { count: "exact", head: true })
    .eq("audit_case_id", auditId);

  const files = formData.getAll("files").filter((f): f is File => f instanceof File);
  if (files.length === 0) return { ok: false, error: "No files selected" };
  if ((existing ?? 0) + files.length > MAX_PER_CASE) {
    return { ok: false, error: `Maximum ${MAX_PER_CASE} evidence files per audit case` };
  }

  const admin = createSupabaseAdminClient();
  let uploaded = 0;

  for (const file of files) {
    const ext = extOf(file.name);
    if (!ALLOWED.has(ext)) {
      return { ok: false, error: `Disallowed file type: .${ext}` };
    }
    const limit = maxFor(ext);
    if (file.size > limit) {
      return { ok: false, error: `${file.name} exceeds ${Math.round(limit / 1024 / 1024)}MB limit` };
    }

    const buf = new Uint8Array(await file.arrayBuffer());
    const hash = await sha256Hex(buf);
    const path = `${u.user.id}/${auditId}/${hash}-${file.name}`;

    const upload = await admin.storage
      .from("evidence")
      .upload(path, buf, { contentType: file.type || "application/octet-stream", upsert: false });
    if (upload.error && !upload.error.message.includes("already exists")) {
      return { ok: false, error: upload.error.message };
    }

    const { data: pub } = admin.storage.from("evidence").getPublicUrl(path);
    const { error: insertErr } = await admin.from("evidence_files").insert({
      user_id: u.user.id,
      audit_case_id: auditId,
      file_url: pub.publicUrl,
      file_path: path,
      file_bucket: "evidence",
      file_type: ext,
      file_size: file.size,
      evidence_hash: hash,
      uploaded_by: u.user.id,
    });
    if (insertErr) return { ok: false, error: insertErr.message };
    uploaded++;
  }

  // Move case forward if it's still a draft.
  if (ac.status === "draft" && uploaded > 0) {
    await admin
      .from("insight_audit_cases")
      .update({ status: "evidence_added" })
      .eq("id", auditId);
  }

  revalidatePath(`/audits/${auditId}`);
  revalidatePath("/evidence");
  return { ok: true, count: uploaded };
}

export async function deleteEvidenceAction(
  evidenceId: string,
): Promise<{ ok: boolean; error?: string }> {
  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (!u.user) return { ok: false, error: "Not signed in" };

  const { data: ev } = await supabase
    .from("evidence_files")
    .select("id,user_id,audit_case_id,file_path,file_bucket")
    .eq("id", evidenceId)
    .single();
  if (!ev || ev.user_id !== u.user.id) {
    return { ok: false, error: "Evidence not found" };
  }

  const admin = createSupabaseAdminClient();
  await admin.storage.from(ev.file_bucket).remove([ev.file_path]);
  const { error } = await admin.from("evidence_files").delete().eq("id", evidenceId);
  if (error) return { ok: false, error: error.message };

  revalidatePath(`/audits/${ev.audit_case_id}`);
  revalidatePath("/evidence");
  return { ok: true };
}

/**
 * Mark a draft / evidence_added audit case as `ready` for GenLayer submission.
 * Building a dataset snapshot row at the same time so validators have structured
 * metric context to reason about. Actual GenLayer dispatch happens in Stage 7.
 */
export async function prepareAuditPacketAction(
  auditId: string,
): Promise<{ ok: boolean; error?: string }> {
  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (!u.user) return { ok: false, error: "Not signed in" };

  const { data: ac, error: acErr } = await supabase
    .from("insight_audit_cases")
    .select("*")
    .eq("id", auditId)
    .single();
  if (acErr || !ac) return { ok: false, error: "Audit case not found" };

  if (!ac.metric_name || !ac.metric_definition) {
    return { ok: false, error: "Add a metric name and definition before preparing the packet" };
  }
  if (!ac.dataset_summary) {
    return { ok: false, error: "Add a dataset summary before preparing the packet" };
  }

  const snapshot = {
    insight_claim: ac.insight_claim,
    metric_name: ac.metric_name,
    metric_definition: ac.metric_definition,
    time_period: ac.time_period,
    segment_context: ac.segment_context,
    dataset_summary: ac.dataset_summary,
    candidate_interpretations: [
      ac.candidate_interpretation_a,
      ac.candidate_interpretation_b,
      ac.candidate_interpretation_c,
    ].filter(Boolean),
  };
  const snapshot_hash = await sha256Hex(
    new TextEncoder().encode(JSON.stringify(snapshot)),
  );

  const admin = createSupabaseAdminClient();
  await admin.from("data_snapshots").insert({
    user_id: u.user.id,
    audit_case_id: auditId,
    source_type: "metric_snapshot",
    source_url: null,
    snapshot_json: snapshot,
    snapshot_hash,
  });

  await admin
    .from("insight_audit_cases")
    .update({ status: "ready" })
    .eq("id", auditId);

  revalidatePath(`/audits/${auditId}`);
  revalidatePath("/snapshots");
  return { ok: true };
}
""",
)

# ===================================================================
# app/(app)/audits/new/page.tsx
# ===================================================================
write(
    "app/(app)/audits/new/page.tsx",
    """import { redirect } from "next/navigation";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { NewAuditForm } from "./NewAuditForm";

export default async function OpenClaimReviewPage({
  searchParams,
}: {
  searchParams: Promise<{ workspace?: string }>;
}) {
  const { supabase } = await requireUser();
  const sp = await searchParams;

  const { data: workspaces } = await supabase
    .from("workspaces")
    .select("id,name,organisation_name,primary_kpi_category")
    .order("created_at", { ascending: false });

  if (!workspaces || workspaces.length === 0) {
    redirect("/onboarding");
  }

  return (
    <>
      <SubContextBar
        eyebrow="Audit intake"
        title="Open Claim Review"
        right={<Badge tone="consensus" dot>Draft · awaiting submission</Badge>}
      />
      <main className="px-6 py-6">
        <NewAuditForm
          workspaces={workspaces}
          initialWorkspaceId={sp.workspace ?? workspaces[0].id}
        />
      </main>
    </>
  );
}
""",
)

# ===================================================================
# app/(app)/audits/new/NewAuditForm.tsx
# ===================================================================
write(
    "app/(app)/audits/new/NewAuditForm.tsx",
    """"use client";

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
    candidate_a: "",
    candidate_b: "",
    candidate_c: "",
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
          const target = e.target as HTMLInputElement | HTMLTextAreaElement;
          if (target.name in vals) {
            setVals((v) => ({ ...v, [target.name]: target.value }));
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
                placeholder="Revenue growth this quarter was mainly driven by repeat customers."
              />
            </Field>
          </div>
          <div className="mt-4">
            <Field label="Business question (optional)">
              <Input name="business_question" placeholder="Should we double-down on repeat-customer marketing?" />
            </Field>
          </div>
        </Doc>

        {/* Step 2: metric basis */}
        <Doc step="Step 2 · Attach metric basis">
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Field label="Metric name">
              <Input name="metric_name" placeholder="Quarterly net revenue by customer type" />
            </Field>
            <Field label="Time period">
              <Input name="time_period" placeholder="Q3 2025" />
            </Field>
          </div>
          <div className="mt-4">
            <Field label="Metric definition" hint="How the metric is calculated, including filters.">
              <textarea
                name="metric_definition"
                rows={3}
                className="input"
                placeholder="Sum of net revenue grouped by customer_type for the selected quarter, excluding refunds."
              />
            </Field>
          </div>
        </Doc>

        {/* Step 3: reporting context */}
        <Doc step="Step 3 · Define reporting context">
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Field label="Segment / filter context">
              <Input name="segment_context" placeholder="Customer type ∈ {new, repeat}; channel = direct" />
            </Field>
            <Field label="Dashboard context (optional)">
              <Input name="dashboard_context" placeholder="Revenue Overview dashboard, panel 4" />
            </Field>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Field label="Report context (optional)">
              <Input name="report_context" placeholder="Q3 board update narrative" />
            </Field>
            <Field label="Analyst notes (optional)">
              <Input name="analyst_notes" placeholder="Discount effect not yet controlled" />
            </Field>
          </div>
          <div className="mt-4">
            <Field label="Dataset summary" hint="What the dataset contains, its grain, freshness, and known limits.">
              <textarea
                name="dataset_summary"
                rows={3}
                className="input"
                placeholder="fact_revenue snapshot from warehouse; row grain = order; refund-aware net revenue; refreshes hourly."
              />
            </Field>
          </div>
        </Doc>

        {/* Step 4: candidate interpretations */}
        <Doc step="Step 4 · Declare candidate interpretations" hint="Three competing readings of the claim. GenLayer validators choose which best fits the evidence.">
          <div className="grid grid-cols-1 gap-3">
            <Field label="Interpretation A">
              <Input name="candidate_interpretation_a" placeholder="Repeat customers were the main driver of net new revenue." />
            </Field>
            <Field label="Interpretation B">
              <Input name="candidate_interpretation_b" placeholder="Repeat revenue grew but new-customer revenue and discounts were larger contributors." />
            </Field>
            <Field label="Interpretation C">
              <Input name="candidate_interpretation_c" placeholder="Growth is driven by segment-mix change, not by any one customer type." />
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
              {[vals.candidate_a, vals.candidate_b, vals.candidate_c].filter(Boolean).length} / 3
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
    candidate_a: string;
    candidate_b: string;
    candidate_c: string;
  },
  evidenceCount: number,
) {
  const checks: { name: string; ok: boolean }[] = [
    { name: "claim",             ok: v.insight_claim.length >= 8 },
    { name: "metric name",       ok: !!v.metric_name },
    { name: "metric definition", ok: !!v.metric_definition },
    { name: "time period",       ok: !!v.time_period },
    { name: "dataset summary",   ok: !!v.dataset_summary },
    { name: "interpretations",   ok: !!v.candidate_a && !!v.candidate_b },
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
""",
)

# ===================================================================
# app/(app)/audits/[id]/page.tsx — show evidence + draft-edit controls
# ===================================================================
write(
    "app/(app)/audits/[id]/page.tsx",
    """import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { OfficialJudgmentHeader } from "@/components/audit/OfficialJudgmentHeader";
import { AssumptionReviewPanel } from "@/components/audit/AssumptionReviewPanel";
import { ConsensusBadge } from "@/components/audit/ConsensusBadge";
import { SupportBadge, Verdict } from "@/components/audit/SupportBadge";
import { Badge } from "@/components/audit/Badge";
import {
  EvidenceInspectorDrawer,
  InspectorRow,
} from "@/components/audit/EvidenceInspectorDrawer";
import { HashText } from "@/components/audit/HashText";

export default async function FullJudgmentRecordPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const { supabase } = await requireUser();

  const { data: audit } = await supabase
    .from("insight_audit_cases").select("*").eq("id", id).single();
  if (!audit) notFound();

  const { data: verdict } = await supabase
    .from("genlayer_audit_verdicts")
    .select("*")
    .eq("audit_case_id", id)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  const { data: evidence } = await supabase
    .from("evidence_files")
    .select("id,file_type,file_size,evidence_hash,created_at")
    .eq("audit_case_id", id)
    .order("created_at", { ascending: false });

  const v: Verdict = (verdict?.verdict ?? "needs_more_evidence") as Verdict;
  const hasVerdict = !!verdict;
  const isReady = audit.status === "ready" || audit.status === "submitted";

  return (
    <>
      <SubContextBar
        eyebrow="Full judgment record"
        title="Official Audit Judgment"
        right={
          <>
            {hasVerdict ? <SupportBadge verdict={v} /> : <Badge tone="amber" dot>Awaiting judgment</Badge>}
            <ConsensusBadge state={hasVerdict ? "reached" : "pending"} />
          </>
        }
      />
      <main className="px-6 py-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
        <div className="space-y-6">
          <OfficialJudgmentHeader
            auditId={audit.id}
            verdict={verdict?.verdict ?? (isReady ? "Awaiting GenLayer" : "Draft")}
            supportLevel={verdict?.support_level ?? "—"}
            confidence={verdict?.confidence_label ?? "—"}
            businessRisk={verdict?.business_risk ?? "—"}
          />

          <article className="doc">
            <div className="grid grid-cols-1 divide-y divide-auditline lg:grid-cols-2 lg:divide-x lg:divide-y-0">
              <Section label="Claim under review" body={audit.insight_claim} />
              <Section label="Business question" body={audit.business_question ?? "—"} />
            </div>
            <div className="grid grid-cols-1 divide-y divide-auditline lg:grid-cols-3 lg:divide-x lg:divide-y-0">
              <Section label="Metric basis" body={audit.metric_name ?? "—"} sub={audit.metric_definition ?? undefined} />
              <Section label="Time period" body={audit.time_period ?? "—"} />
              <Section label="Segment / filter" body={audit.segment_context ?? "—"} />
            </div>
            <div className="grid grid-cols-1 divide-y divide-auditline lg:grid-cols-2 lg:divide-x lg:divide-y-0">
              <Section label="Dataset summary" body={audit.dataset_summary ?? "—"} />
              <Section label="Report context" body={audit.report_context ?? "—"} />
            </div>
            <div className="grid grid-cols-1 divide-y divide-auditline lg:grid-cols-3 lg:divide-x lg:divide-y-0">
              <Section label="Interpretation A" body={audit.candidate_interpretation_a ?? "—"} />
              <Section label="Interpretation B" body={audit.candidate_interpretation_b ?? "—"} />
              <Section label="Interpretation C" body={audit.candidate_interpretation_c ?? "—"} />
            </div>
            <div className="border-t border-auditline">
              <Section
                label="Validator reasoning summary"
                body={verdict?.reasoning_summary ?? "GenLayer validators will reason over the packet and reach consensus."}
              />
            </div>
          </article>

          {/* Evidence ledger for this case */}
          <article className="doc overflow-hidden">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">Evidence reviewed</div>
              <div className="display text-[15px] font-semibold text-ink">
                Attached evidence ({evidence?.length ?? 0})
              </div>
            </div>
            {evidence && evidence.length > 0 ? (
              <table className="ledger-table">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Evidence hash</th>
                    <th>Uploaded</th>
                  </tr>
                </thead>
                <tbody>
                  {evidence.map((e) => (
                    <tr key={e.id}>
                      <td><Badge tone="blue">{e.file_type}</Badge></td>
                      <td className="text-slate">{Math.round((e.file_size ?? 0) / 1024)} KB</td>
                      <td><HashText value={e.evidence_hash ?? "—"} short /></td>
                      <td className="text-slate">{new Date(e.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="px-5 py-8 text-center text-[13px] text-slate">
                No evidence attached. Add files from the claim review form before submission.
              </div>
            )}
          </article>

          <AssumptionReviewPanel
            notes={
              hasVerdict
                ? [
                    {
                      kind: "causality",
                      text:
                        "New customer revenue, discount effects, and segment mix were not sufficiently controlled.",
                    },
                    {
                      kind: "comparison",
                      text: "No matched control group for the same quarter last year.",
                    },
                  ]
                : undefined
            }
          />

          <article className="doc">
            <div className="border-b border-auditline px-5 py-3">
              <div className="eyebrow eyebrow-slate">Recommended action</div>
              <div className="display text-[15px] font-semibold text-ink">Next step for the business</div>
            </div>
            <div className="px-5 py-4 text-[13.5px] text-ink">
              {hasVerdict
                ? "Treat the claim as directional only. Re-issue with controlled comparisons before allocating budget."
                : "Submit the packet to GenLayer to receive an executive-ready recommendation."}
            </div>
          </article>

          <div className="audit-strip">
            <span className="mono text-[10.5px] uppercase tracking-[0.16em] text-ledger-white/55">
              Audit trail
            </span>
            <span>Submitted · {new Date(audit.created_at).toLocaleString()}</span>
            <span className="mx-1 h-3 w-px bg-glass-grid" />
            <span>Status · {audit.status.replace(/_/g, " ")}</span>
            <Link
              href={`/memos?audit=${audit.id}`}
              className="ml-auto btn-secondary bg-white/[0.04] text-ledger-white border-glass-grid hover:bg-white/[0.08]"
            >
              Export decision memo
            </Link>
          </div>
        </div>

        <EvidenceInspectorDrawer title="GenLayer record">
          <InspectorRow left="Contract"        right={<HashText dark value={verdict?.contract_address ?? "—"} short />} />
          <InspectorRow left="Transaction"     right={<HashText dark value={verdict?.transaction_hash ?? "—"} short />} />
          <InspectorRow left="Audit ID"        right={<HashText dark value={audit.id} short />} />
          <InspectorRow left="Evidence digest" right={<HashText dark value={verdict?.evidence_digest ?? "—"} short />} />
          <InspectorRow left="Consensus"       right={<ConsensusBadge state={hasVerdict ? "reached" : "pending"} />} />
          <InspectorRow left="Evidence files"  right={<span className="mono">{evidence?.length ?? 0}</span>} />
        </EvidenceInspectorDrawer>
      </main>
    </>
  );
}

function Section({ label, body, sub }: { label: string; body: string; sub?: string }) {
  return (
    <div className="px-5 py-4">
      <div className="mono text-[10px] uppercase tracking-[0.14em] text-slate">{label}</div>
      <div className="mt-1 text-[14px] text-ink">{body}</div>
      {sub ? <div className="mt-1 text-[12.5px] text-slate">{sub}</div> : null}
    </div>
  );
}
""",
)

print("\nStage 5 files written.")
