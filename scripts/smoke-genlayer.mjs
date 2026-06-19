#!/usr/bin/env node
/**
 * Smoke test: submit a test audit to GenLayer, read the verdict back.
 *
 * Usage: node scripts/smoke-genlayer.mjs
 *
 * Loads .env.local automatically. Requires genlayer-js 1.1.8+.
 */
import { readFileSync } from "fs";
import { resolve } from "path";

// Load .env.local
const envPath = resolve(process.cwd(), ".env.local");
try {
  const envContent = readFileSync(envPath, "utf8");
  for (const line of envContent.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx === -1) continue;
    const key = trimmed.slice(0, eqIdx).trim();
    const val = trimmed.slice(eqIdx + 1).trim();
    if (!process.env[key]) process.env[key] = val;
  }
} catch {
  console.error("Could not read .env.local");
  process.exit(1);
}

const { createClient, createAccount } = await import("genlayer-js");
const { studionet } = await import("genlayer-js/chains");
const { TransactionStatus } = await import("genlayer-js/types");

const RPC_URL = process.env.NEXT_PUBLIC_GENLAYER_RPC_URL || "https://studio.genlayer.com/api";
const CHAIN_ID = Number(process.env.NEXT_PUBLIC_GENLAYER_CHAIN_ID || "61999");
const CONTRACT = process.env.NEXT_PUBLIC_VERISIGHT_CONTRACT_ADDRESS;
const RELAY_PK = process.env.GENLAYER_RELAY_PRIVATE_KEY;

console.log("=== GENLAYER SMOKE TEST ===");
console.log("RPC URL:          ", RPC_URL);
console.log("Chain ID:         ", CHAIN_ID);
console.log("Contract address: ", CONTRACT);
console.log("Explorer:          https://explorer-studio.genlayer.com");
console.log();

if (!CONTRACT) { console.error("Missing NEXT_PUBLIC_VERISIGHT_CONTRACT_ADDRESS"); process.exit(1); }
if (!RELAY_PK) { console.error("Missing GENLAYER_RELAY_PRIVATE_KEY"); process.exit(1); }

const chain = {
  ...studionet,
  id: CHAIN_ID,
  rpcUrls: {
    default: { http: [RPC_URL] },
    public: { http: [RPC_URL] },
  },
};

const account = createAccount(RELAY_PK);
console.log("Relay address:    ", account.address);
console.log();

const client = createClient({ chain, account });

const testAuditId = `smoke-test-${Date.now()}`;
const testPacket = JSON.stringify({
  audit_id: testAuditId,
  workspace_context: "smoke-test",
  insight_claim: "Revenue grew 15% QoQ",
  business_question: "Is this growth real?",
  metric_name: "Revenue",
  metric_definition: "Total invoiced revenue",
  time_period: "Q1 2026",
  segment_context: "All segments",
  dataset_summary: "100 invoices totaling $1.5M",
  candidate_interpretation_a: "Growth is organic",
  candidate_interpretation_b: "Growth is from one-time contract",
  candidate_interpretation_c: "Growth is seasonal",
  evidence_hashes: ["abc123"],
});

console.log("--- Step 1: Submit audit ---");
console.log("Audit ID:", testAuditId);

let txHash;
try {
  txHash = await client.writeContract({
    address: CONTRACT,
    functionName: "submit_audit",
    args: [testAuditId, testPacket, "smoke-evidence-digest"],
    value: BigInt(0),
  });
  console.log("TX Hash:          ", txHash);
  console.log("Explorer TX URL:   https://explorer-studio.genlayer.com/tx/" + txHash);
  console.log("Explorer Contract: https://explorer-studio.genlayer.com/address/" + CONTRACT);
} catch (error) {
  console.error("SUBMIT FAILED:");
  console.error({
    name: error?.name,
    message: error?.message,
    shortMessage: error?.shortMessage,
    cause: error?.cause,
    details: error?.details,
  });
  console.error("Full error:", error);
  process.exit(1);
}

if (!txHash) {
  console.error("No tx hash returned — transaction not broadcast");
  process.exit(1);
}

console.log();
console.log("--- Step 2: Wait for acceptance ---");
try {
  const receipt = await client.waitForTransactionReceipt({
    hash: txHash,
    status: TransactionStatus.ACCEPTED,
    retries: 40,
    interval: 3000,
  });
  console.log("Receipt status:", receipt?.status);
  console.log("Receipt:", JSON.stringify(receipt, (_, v) => typeof v === "bigint" ? v.toString() : v, 2).slice(0, 1000));
} catch (error) {
  console.warn("Wait failed (may still be processing):", error?.message || error);
}

console.log();
console.log("--- Step 3: Read has_verdict ---");
try {
  const has = await client.readContract({
    address: CONTRACT,
    functionName: "has_verdict",
    args: [testAuditId],
  });
  console.log("has_verdict raw:", has);
} catch (error) {
  console.error("has_verdict failed:", error?.message || error);
}

console.log();
console.log("--- Step 4: Read get_verdict ---");
try {
  const verdict = await client.readContract({
    address: CONTRACT,
    functionName: "get_verdict",
    args: [testAuditId],
  });
  console.log("get_verdict raw type:", typeof verdict);
  console.log("get_verdict raw:", JSON.stringify(verdict).slice(0, 2000));

  // Try to parse
  let value = verdict;
  if (typeof value === "object" && value !== null && "Return" in value) {
    value = value.Return;
  }
  if (typeof value === "string") {
    try { value = JSON.parse(value); } catch {}
  }
  if (typeof value === "string") {
    try { value = JSON.parse(value); } catch {}
  }
  console.log("Parsed verdict:", JSON.stringify(value, null, 2)?.slice(0, 2000));
} catch (error) {
  console.error("get_verdict failed:", error?.message || error);
}

console.log();
console.log("=== SMOKE TEST COMPLETE ===");
