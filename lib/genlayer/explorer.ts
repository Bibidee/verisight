export const GENLAYER_EXPLORER_BASE = "https://explorer-studio.genlayer.com";

export function getGenLayerTxUrl(txHash: string) {
  if (!txHash || txHash === "—") return "";
  return `${GENLAYER_EXPLORER_BASE}/tx/${txHash}`;
}

export function getGenLayerAddressUrl(address: string) {
  if (!address || address === "—") return "";
  return `${GENLAYER_EXPLORER_BASE}/address/${address}`;
}
