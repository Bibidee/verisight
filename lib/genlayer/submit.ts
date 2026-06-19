// Server-only GenLayer dispatch helpers.
import { TransactionStatus } from "genlayer-js/types";
import { getContractAddress, getGenLayerClient } from "./client";
import { parseGenLayerReturn, VeriSightConsensusVerdict } from "./parseVerdict";

export interface AuditPacket {
  audit_id: string;
  workspace_context: string;
  insight_claim: string;
  business_question: string | null;
  metric_name: string | null;
  metric_definition: string | null;
  time_period: string | null;
  segment_context: string | null;
  dataset_summary: string | null;
  dashboard_context: string | null;
  report_context: string | null;
  analyst_notes: string | null;
  candidate_interpretation_a: string | null;
  candidate_interpretation_b: string | null;
  candidate_interpretation_c: string | null;
  evidence_hashes: string[];
}

export type { VeriSightConsensusVerdict };

export async function submitAuditToGenLayer(args: {
  auditId: string;
  packet: AuditPacket;
  evidenceDigest: string;
}): Promise<{ transactionHash: `0x${string}`; contractAddress: `0x${string}` }> {
  const client = getGenLayerClient();
  const address = getContractAddress();

  const packetJson = JSON.stringify(args.packet);

  console.log("[GENLAYER_TX] Preparing submit_audit", {
    contractAddress: address,
    auditId: args.auditId,
    evidenceDigest: args.evidenceDigest,
    packetLength: packetJson.length,
  });

  let transactionHash: `0x${string}`;
  try {
    transactionHash = await client.writeContract({
      address,
      functionName: "submit_audit",
      args: [args.auditId, packetJson, args.evidenceDigest],
      value: BigInt(0),
    });

    console.log("[GENLAYER_TX] Transaction sent", {
      transactionHash,
      contractAddress: address,
      explorerUrl: `https://explorer-studio.genlayer.com/tx/${transactionHash}`,
    });
  } catch (error: unknown) {
    const e = error as Record<string, unknown>;
    console.error("[GENLAYER_TX_ERROR] writeContract failed", {
      error: e,
      name: e?.name,
      message: e?.message,
      shortMessage: e?.shortMessage,
      cause: e?.cause,
      details: e?.details,
      contractAddress: address,
      auditId: args.auditId,
    });
    throw error;
  }

  if (!transactionHash) {
    throw new Error(
      "GenLayer writeContract returned no transaction hash — transaction was not broadcast",
    );
  }

  return { transactionHash, contractAddress: address };
}

export async function waitForGenLayerAccepted(
  hash: `0x${string}`,
  opts?: { retries?: number; intervalMs?: number },
) {
  console.log("[GENLAYER_TX] Waiting for acceptance", { hash });
  const client = getGenLayerClient();
  const receipt = await client.waitForTransactionReceipt({
    hash: hash as unknown as `0x${string}` & { length: 66 },
    status: TransactionStatus.ACCEPTED,
    retries: opts?.retries ?? 50,
    interval: opts?.intervalMs ?? 3000,
  });
  console.log("[GENLAYER_TX] Receipt received", {
    hash,
    status: receipt?.status,
  });
  return receipt;
}

export async function readGenLayerVerdict(
  auditId: string,
): Promise<VeriSightConsensusVerdict | null> {
  const client = getGenLayerClient();
  const address = getContractAddress();

  console.log("[GENLAYER_READ] get_verdict", { auditId, contractAddress: address });

  let raw: unknown;
  try {
    raw = await client.readContract({
      address,
      functionName: "get_verdict",
      args: [auditId],
    });
    console.log("[GENLAYER_READ] Raw response", {
      auditId,
      rawType: typeof raw,
      raw: typeof raw === "string" ? raw.slice(0, 500) : JSON.stringify(raw).slice(0, 500),
    });
  } catch (error: unknown) {
    const e = error as Record<string, unknown>;
    console.error("[GENLAYER_READ_ERROR] get_verdict failed", {
      error: e,
      name: e?.name,
      message: e?.message,
      shortMessage: e?.shortMessage,
      cause: e?.cause,
      details: e?.details,
    });
    throw error;
  }

  const parsed = parseGenLayerReturn(raw);
  console.log("[GENLAYER_READ] Parsed verdict", {
    auditId,
    hasVerdict: !!parsed?.verdict,
    verdict: parsed?.verdict,
  });
  return parsed;
}

export async function readGenLayerHasVerdict(auditId: string): Promise<boolean> {
  const client = getGenLayerClient();
  const address = getContractAddress();

  console.log("[GENLAYER_READ] has_verdict", { auditId, contractAddress: address });

  let raw: unknown;
  try {
    raw = await client.readContract({
      address,
      functionName: "has_verdict",
      args: [auditId],
    });
    console.log("[GENLAYER_READ] has_verdict raw", {
      auditId,
      rawType: typeof raw,
      raw,
    });
  } catch (error: unknown) {
    const e = error as Record<string, unknown>;
    console.error("[GENLAYER_READ_ERROR] has_verdict failed", {
      error: e,
      name: e?.name,
      message: e?.message,
      shortMessage: e?.shortMessage,
      cause: e?.cause,
      details: e?.details,
    });
    throw error;
  }

  if (typeof raw === "boolean") return raw;
  if (typeof raw === "string") return raw === "true" || raw === "True";
  if (typeof raw === "object" && raw !== null) {
    if ("Return" in raw) {
      const v = (raw as Record<string, unknown>).Return;
      if (typeof v === "boolean") return v;
      if (typeof v === "string") return v === "true" || v === "True";
    }
    if ("return" in raw) {
      const v = (raw as Record<string, unknown>).return;
      if (typeof v === "boolean") return v;
      if (typeof v === "string") return v === "true" || v === "True";
    }
  }
  return false;
}
