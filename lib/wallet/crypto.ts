import { webcrypto as nodeCrypto } from "node:crypto";

const subtle = (nodeCrypto as Crypto).subtle;

const PBKDF2_ITERATIONS = 600_000;
const PBKDF2_HASH = "SHA-256";
const KEY_LEN_BITS = 256;

// WebCrypto in TS lib.dom expects BufferSource backed by ArrayBuffer.
// Uint8Array<ArrayBufferLike> doesn't satisfy that under strict mode, so
// we copy into a fresh ArrayBuffer-backed Uint8Array at boundaries.
function asAB(u: Uint8Array): ArrayBuffer {
  const ab = new ArrayBuffer(u.byteLength);
  new Uint8Array(ab).set(u);
  return ab;
}

function b64encode(bytes: Uint8Array): string {
  return Buffer.from(bytes).toString("base64");
}
function b64decode(s: string): Uint8Array {
  return new Uint8Array(Buffer.from(s, "base64"));
}

export const enc = {
  b64encode,
  b64decode,
  utf8: (s: string) => new TextEncoder().encode(s),
};

export function randomBytes(n: number): Uint8Array {
  const b = new Uint8Array(n);
  (nodeCrypto as Crypto).getRandomValues(b);
  return b;
}

export async function deriveKey(
  secret: string,
  salt: Uint8Array,
  pepper: string,
): Promise<CryptoKey> {
  const material = await subtle.importKey(
    "raw",
    asAB(enc.utf8(secret + "|" + pepper)),
    "PBKDF2",
    false,
    ["deriveKey"],
  );
  return subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: asAB(salt),
      iterations: PBKDF2_ITERATIONS,
      hash: PBKDF2_HASH,
    },
    material,
    { name: "AES-GCM", length: KEY_LEN_BITS },
    false,
    ["encrypt", "decrypt"],
  );
}

export async function aesGcmEncrypt(
  key: CryptoKey,
  plaintext: Uint8Array,
): Promise<{ ciphertext: string; iv: string }> {
  const iv = randomBytes(12);
  const ct = new Uint8Array(
    await subtle.encrypt({ name: "AES-GCM", iv: asAB(iv) }, key, asAB(plaintext)),
  );
  return { ciphertext: b64encode(ct), iv: b64encode(iv) };
}

export async function aesGcmDecrypt(
  key: CryptoKey,
  payload: { ciphertext: string; iv: string },
): Promise<Uint8Array> {
  const ct = asAB(b64decode(payload.ciphertext));
  const iv = asAB(b64decode(payload.iv));
  const pt = await subtle.decrypt({ name: "AES-GCM", iv }, key, ct);
  return new Uint8Array(pt);
}

// We pack the (ciphertext, iv) pair as a single base64 JSON blob for storage.
export function packBlob(p: { ciphertext: string; iv: string }): string {
  return Buffer.from(JSON.stringify(p), "utf8").toString("base64");
}
export function unpackBlob(s: string): { ciphertext: string; iv: string } {
  const json = Buffer.from(s, "base64").toString("utf8");
  return JSON.parse(json);
}

export const kdfParams = {
  algorithm: "PBKDF2",
  hash: PBKDF2_HASH,
  iterations: PBKDF2_ITERATIONS,
  keyLength: KEY_LEN_BITS,
};

export { asAB };
