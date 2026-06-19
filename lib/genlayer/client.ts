// Server-only GenLayer client. Do not import from client components.
import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

let cached: ReturnType<typeof createClient> | null = null;
let cachedRpc: string | undefined;

const CHAIN_ID = 61999;
const DEFAULT_RPC = "https://studio.genlayer.com/api";

function buildChain(rpcUrl: string) {
  return {
    ...studionet,
    id: CHAIN_ID,
    name: "GenLayer StudioNet",
    rpcUrls: {
      default: { http: [rpcUrl] },
      public: { http: [rpcUrl] },
    },
    blockExplorers: {
      default: {
        name: "GenLayer Studio Explorer",
        url: "https://explorer-studio.genlayer.com",
      },
    },
  };
}

export function getGenLayerClient() {
  const rpc = process.env.NEXT_PUBLIC_GENLAYER_RPC_URL || DEFAULT_RPC;
  if (cached && cachedRpc === rpc) return cached;

  const pk = process.env.GENLAYER_RELAY_PRIVATE_KEY;
  if (!pk) {
    throw new Error("GENLAYER_RELAY_PRIVATE_KEY is not set");
  }

  const chain = buildChain(rpc);
  const account = createAccount(pk as `0x${string}`);
  cached = createClient({ chain, account });
  cachedRpc = rpc;

  console.log("[GENLAYER_CLIENT] Initialized", {
    rpcUrl: rpc,
    chainId: CHAIN_ID,
    relayAddress: account.address,
  });

  return cached;
}

export function getContractAddress(): `0x${string}` {
  const addr = process.env.NEXT_PUBLIC_VERISIGHT_CONTRACT_ADDRESS;
  if (!addr) {
    throw new Error(
      "Missing NEXT_PUBLIC_VERISIGHT_CONTRACT_ADDRESS — set it in .env.local",
    );
  }
  if (!addr.startsWith("0x") || addr.length !== 42) {
    throw new Error(
      `Invalid NEXT_PUBLIC_VERISIGHT_CONTRACT_ADDRESS: "${addr}" — must be 0x-prefixed 20-byte hex`,
    );
  }
  return addr as `0x${string}`;
}
