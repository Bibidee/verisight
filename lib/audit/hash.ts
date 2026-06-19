// SHA-256 helper for evidence digests. Works in both server and browser.
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
