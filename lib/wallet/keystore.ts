import { privateKeyToAccount, generatePrivateKey } from "viem/accounts";
import {
  aesGcmDecrypt,
  aesGcmEncrypt,
  asAB,
  deriveKey,
  enc,
  kdfParams,
  packBlob,
  randomBytes,
  unpackBlob,
} from "./crypto";
import { normalisePhrase } from "./recovery";

export interface NewWalletMaterial {
  address: `0x${string}`;
  encryptedPrivateKey: string;       // base64(JSON({ciphertext,iv}))
  passwordWrap: WrapRecord;
  recoveryWrap: WrapRecord;
}
export interface WrapRecord {
  encryptedWalletKey: string;        // base64(JSON({ciphertext,iv}))
  salt: string;                      // base64
  kdfParams: typeof kdfParams;
}

async function wrapWek(secret: string, wek: Uint8Array, pepper: string): Promise<WrapRecord> {
  const salt = randomBytes(16);
  const kek = await deriveKey(secret, salt, pepper);
  const blob = await aesGcmEncrypt(kek, wek);
  return {
    encryptedWalletKey: packBlob(blob),
    salt: enc.b64encode(salt),
    kdfParams,
  };
}

async function unwrapWek(secret: string, wrap: WrapRecord, pepper: string): Promise<Uint8Array> {
  const kek = await deriveKey(secret, enc.b64decode(wrap.salt), pepper);
  return aesGcmDecrypt(kek, unpackBlob(wrap.encryptedWalletKey));
}

function privateKeyBytes(hex: string): Uint8Array {
  const clean = hex.startsWith("0x") ? hex.slice(2) : hex;
  return new Uint8Array(Buffer.from(clean, "hex"));
}
function privateKeyHex(bytes: Uint8Array): `0x${string}` {
  return (`0x` + Buffer.from(bytes).toString("hex")) as `0x${string}`;
}

export async function createEmbeddedWallet(
  password: string,
  recoveryPhrase: string,
  pepper: string,
): Promise<NewWalletMaterial> {
  const pk = generatePrivateKey();
  const account = privateKeyToAccount(pk);
  const pkBytes = privateKeyBytes(pk);

  const wek = randomBytes(32);
  const wekKey = await crypto.subtle.importKey(
    "raw",
    asAB(wek),
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"],
  );
  const encryptedPk = await aesGcmEncrypt(wekKey, pkBytes);

  const passwordWrap = await wrapWek(password, wek, pepper);
  const recoveryWrap = await wrapWek(normalisePhrase(recoveryPhrase), wek, pepper);

  return {
    address: account.address,
    encryptedPrivateKey: packBlob(encryptedPk),
    passwordWrap,
    recoveryWrap,
  };
}

export async function decryptPrivateKey(
  encryptedPrivateKey: string,
  wek: Uint8Array,
): Promise<`0x${string}`> {
  const wekKey = await crypto.subtle.importKey(
    "raw",
    asAB(wek),
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"],
  );
  const pk = await aesGcmDecrypt(wekKey, unpackBlob(encryptedPrivateKey));
  return privateKeyHex(pk);
}

export const keystore = {
  wrapWek,
  unwrapWek,
};
