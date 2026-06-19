import { generateMnemonic, english } from "viem/accounts";

// 24 words gives 256-bit entropy.
export function generateRecoveryPhrase(): string {
  return generateMnemonic(english, 256);
}

// Normalise user input so capitalisation/whitespace doesn't break recovery.
export function normalisePhrase(input: string): string {
  return input
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}
