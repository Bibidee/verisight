// Centralised env access. Throws clearly when a required value is missing.
function req(name: string, val: string | undefined): string {
  if (!val) throw new Error(`Missing env var: ${name}`);
  return val;
}

export const env = {
  supabaseUrl: req("NEXT_PUBLIC_SUPABASE_URL", process.env.NEXT_PUBLIC_SUPABASE_URL),
  supabaseAnonKey: req(
    "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  ),
  // Server-only — do not import this file into client components.
  supabaseServiceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY ?? "",
  walletPepper: process.env.WALLET_PEPPER ?? "",
  genlayerRpcUrl: process.env.NEXT_PUBLIC_GENLAYER_RPC_URL ?? "",
  genlayerChainId: Number(process.env.NEXT_PUBLIC_GENLAYER_CHAIN_ID ?? "61999"),
  verisightContractAddress:
    process.env.NEXT_PUBLIC_VERISIGHT_CONTRACT_ADDRESS ?? "",
};
