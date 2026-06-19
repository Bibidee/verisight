"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { createSupabaseAdminClient } from "@/lib/supabase/admin";
import { sha256Hex } from "./hash";
import {
  AuditPacket,
  readGenLayerHasVerdict,
  readGenLayerVerdict,
  submitAuditToGenLayer,
  VeriSightConsensusVerdict,
} from "@/lib/genlayer/submit";
import { env } from "@/lib/env";

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

const PatchAuditSchema = z.object({
  metric_name: z.string().max(160).optional().nullable(),
  metric_definition: z.string().max(800).optional().nullable(),
  time_period: z.string().max(120).optional().nullable(),
  dataset_summary: z.string().max(800).optional().nullable(),
  segment_context: z.string().max(400).optional().nullable(),
  candidate_interpretation_a: z.string().max(400).optional().nullable(),
  candidate_interpretation_b: z.string().max(400).optional().nullable(),
  candidate_interpretation_c: z.string().max(400).optional().nullable(),
});

export async function patchAuditDraftAction(
  auditId: string,
  formData: FormData,
): Promise<{ ok: boolean; error?: string }> {
  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (!u.user) return { ok: false, error: "Not signed in" };

  const raw = readForm(formData);
  const parsed = PatchAuditSchema.safeParse(raw);
  if (!parsed.success) {
    return { ok: false, error: parsed.error.issues[0]?.message ?? "Invalid input" };
  }

  const patch: Record<string, string | null> = {};
  for (const [k, v] of Object.entries(parsed.data)) {
    if (v !== undefined) patch[k] = v || null;
  }

  const { error } = await supabase
    .from("insight_audit_cases")
    .update(patch)
    .eq("id", auditId)
    .eq("user_id", u.user.id);
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
  const m = name.toLowerCase().match(/\.([a-z0-9]+)$/);
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

  // Collect evidence digests for the on-chain submission.
  const { data: evidenceRows } = await admin
    .from("evidence_files")
    .select("evidence_hash")
    .eq("audit_case_id", auditId);
  const evidenceHashes = (evidenceRows ?? [])
    .map((r) => r.evidence_hash)
    .filter((h): h is string => !!h);

  // Concatenated evidence digest passed to the contract as a single hash.
  const evidenceDigest = await sha256Hex(
    new TextEncoder().encode(evidenceHashes.join("|") || "no-evidence"),
  );

  // Build the structured audit packet. We deliberately omit any verdict /
  // support_level fields; the contract refuses packets that pre-decide.
  const packet: AuditPacket = {
    audit_id: auditId,
    workspace_context: "workspace:" + (ac.workspace_id ?? ""),
    insight_claim: ac.insight_claim,
    business_question: ac.business_question,
    metric_name: ac.metric_name,
    metric_definition: ac.metric_definition,
    time_period: ac.time_period,
    segment_context: ac.segment_context,
    dataset_summary: ac.dataset_summary,
    dashboard_context: ac.dashboard_context,
    report_context: ac.report_context,
    analyst_notes: ac.analyst_notes,
    candidate_interpretation_a: ac.candidate_interpretation_a,
    candidate_interpretation_b: ac.candidate_interpretation_b,
    candidate_interpretation_c: ac.candidate_interpretation_c,
    evidence_hashes: evidenceHashes,
  };

  await admin
    .from("insight_audit_cases")
    .update({
      status: "submitted",
      submitted_to_genlayer_at: new Date().toISOString(),
    })
    .eq("id", auditId);

  // Dispatch to GenLayer.
  let transactionHash: string | null = null;
  try {
    const res = await submitAuditToGenLayer({
      auditId,
      packet,
      evidenceDigest,
    });
    transactionHash = res.transactionHash;

    await admin.from("contract_activity_logs").insert({
      user_id: u.user.id,
      audit_case_id: auditId,
      contract_address: env.verisightContractAddress,
      transaction_hash: transactionHash,
      action: "submit_audit",
      status: "ok",
    });

    // Insert a placeholder verdict row so the UI shows tx + contract
    // immediately. Mirroring the real verdict happens in pollVerdictAction.
    await admin.from("genlayer_audit_verdicts").insert({
      user_id: u.user.id,
      audit_case_id: auditId,
      contract_address: env.verisightContractAddress,
      transaction_hash: transactionHash,
      audit_id_on_chain: auditId,
      evidence_digest: evidenceDigest,
      consensus_status: "pending",
    });

    await admin
      .from("insight_audit_cases")
      .update({ status: "consensus_pending" })
      .eq("id", auditId);
  } catch (e: unknown) {
    const err = e as Record<string, unknown>;
    const msg = (err?.shortMessage ?? err?.message ?? "GenLayer dispatch failed") as string;
    console.error("[GENLAYER_SUBMIT_ERROR]", {
      error: err,
      name: err?.name,
      message: err?.message,
      shortMessage: err?.shortMessage,
      cause: err?.cause,
      details: err?.details,
    });
    await admin.from("contract_activity_logs").insert({
      user_id: u.user.id,
      audit_case_id: auditId,
      contract_address: env.verisightContractAddress,
      transaction_hash: transactionHash,
      action: "submit_audit",
      status: "error",
      error_message: String(msg).slice(0, 500),
    });
    return { ok: false, error: "GenLayer submission failed: " + msg };
  }

  revalidatePath(`/audits/${auditId}`);
  revalidatePath("/snapshots");
  revalidatePath("/verdicts");
  return { ok: true };
}

/**
 * Read the latest verdict from the contract for this audit and mirror it
 * into Supabase. Safe to call repeatedly — only updates the placeholder row
 * when the on-chain status flips to `issued`.
 */
export async function pollVerdictAction(
  auditId: string,
): Promise<{ ok: boolean; status: string; verdict?: string; error?: string }> {
  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (!u.user) return { ok: false, status: "unauthorised", error: "Not signed in" };

  const { data: ac } = await supabase
    .from("insight_audit_cases")
    .select("id,user_id,status")
    .eq("id", auditId)
    .single();
  if (!ac || ac.user_id !== u.user.id) {
    return { ok: false, status: "not_found", error: "Audit case not found" };
  }

  try {
    const has = await readGenLayerHasVerdict(auditId);
    if (!has) {
      return { ok: true, status: "pending" };
    }

    const parsed = await readGenLayerVerdict(auditId);
    if (!parsed || !parsed.verdict) {
      return { ok: true, status: "pending" };
    }

    const admin = createSupabaseAdminClient();

    await admin
      .from("genlayer_audit_verdicts")
      .update({
        verdict: parsed.verdict,
        support_level: parsed.support_level || null,
        confidence_label: parsed.confidence_label || null,
        selected_interpretation: parsed.selected_interpretation || null,
        reasoning_summary: parsed.reasoning_summary || null,
        unsupported_assumptions: parsed.unsupported_assumptions.length > 0
          ? parsed.unsupported_assumptions
          : null,
        business_risk: parsed.business_risk || null,
        consensus_status: "reached",
        consensus_timestamp: new Date().toISOString(),
      })
      .eq("audit_case_id", auditId);

    await admin
      .from("insight_audit_cases")
      .update({ status: "verdict_issued" })
      .eq("id", auditId);

    revalidatePath(`/audits/${auditId}`);
    revalidatePath("/verdicts");
    revalidatePath("/memos");
    revalidatePath("/dashboard");
    return { ok: true, status: "reached", verdict: parsed.verdict };
  } catch (e) {
    const msg = e instanceof Error ? e.message : "poll failed";
    return { ok: false, status: "error", error: msg };
  }
}
