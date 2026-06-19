"""Stage 3 — Auth + embedded wallet.

Writes:
 - lib/wallet/{crypto,recovery,keystore}.ts
 - lib/auth/actions.ts
 - middleware.ts
 - app/auth/callback/route.ts
 - app/(auth)/{layout,signup,login,forgot-password,reset-password}/page.tsx
 - components/ui/{Button,Input,Label,Panel,Field}.tsx

Wallet model:
  * EOA generated with viem.
  * AES-256-GCM encrypts the private key using a Wallet Encryption Key (WEK).
  * The WEK itself is wrapped twice:
      - password wrap: PBKDF2(password+pepper, salt, 600k iters) -> KEK_pw, AES-GCM(WEK)
      - recovery wrap: PBKDF2(recovery_phrase+pepper, salt, 600k iters) -> KEK_rk, AES-GCM(WEK)
  * Password reset re-wraps the SAME wek with the new password. Wallet address never changes.
  * Recovery phrase is shown to the user exactly once on signup.
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def write(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {rel}")


# ===================================================================
# lib/wallet/crypto.ts
# ===================================================================
write(
    "lib/wallet/crypto.ts",
    """import { webcrypto as nodeCrypto } from "node:crypto";

const subtle = (nodeCrypto as Crypto).subtle;

const PBKDF2_ITERATIONS = 600_000;
const PBKDF2_HASH = "SHA-256";
const KEY_LEN_BITS = 256;

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
    enc.utf8(secret + "|" + pepper),
    "PBKDF2",
    false,
    ["deriveKey"],
  );
  return subtle.deriveKey(
    {
      name: "PBKDF2",
      salt,
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
    await subtle.encrypt({ name: "AES-GCM", iv }, key, plaintext),
  );
  return { ciphertext: b64encode(ct), iv: b64encode(iv) };
}

export async function aesGcmDecrypt(
  key: CryptoKey,
  payload: { ciphertext: string; iv: string },
): Promise<Uint8Array> {
  const ct = b64decode(payload.ciphertext);
  const iv = b64decode(payload.iv);
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
""",
)

# ===================================================================
# lib/wallet/recovery.ts
# ===================================================================
write(
    "lib/wallet/recovery.ts",
    """import { generateMnemonic, english } from "viem/accounts";

// 24 words gives 256-bit entropy.
export function generateRecoveryPhrase(): string {
  return generateMnemonic(english, 256);
}

// Normalise user input so capitalisation/whitespace doesn't break recovery.
export function normalisePhrase(input: string): string {
  return input
    .trim()
    .toLowerCase()
    .replace(/\\s+/g, " ");
}
""",
)

# ===================================================================
# lib/wallet/keystore.ts
# ===================================================================
write(
    "lib/wallet/keystore.ts",
    """import { privateKeyToAccount, generatePrivateKey } from "viem/accounts";
import {
  aesGcmDecrypt,
  aesGcmEncrypt,
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
    wek,
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
    wek,
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
""",
)

# ===================================================================
# components/ui primitives
# ===================================================================
write(
    "components/ui/Button.tsx",
    """import { ButtonHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

type Variant = "primary" | "secondary" | "consensus" | "danger";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const variantClass: Record<Variant, string> = {
  primary: "btn-primary",
  secondary: "btn-secondary",
  consensus: "btn-consensus",
  danger: "btn-danger",
};

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variant = "primary", className, ...rest },
  ref,
) {
  return (
    <button
      ref={ref}
      className={clsx(variantClass[variant], "disabled:opacity-60", className)}
      {...rest}
    />
  );
});
""",
)

write(
    "components/ui/Input.tsx",
    """import { InputHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  function Input({ className, ...rest }, ref) {
    return (
      <input
        ref={ref}
        className={clsx(
          "w-full rounded-btn border border-gridline bg-panel px-3 py-2 text-sm",
          "text-ink placeholder:text-slate focus:outline-none focus:ring-2 focus:ring-analyst",
          className,
        )}
        {...rest}
      />
    );
  },
);
""",
)

write(
    "components/ui/Label.tsx",
    """import { LabelHTMLAttributes } from "react";
import clsx from "clsx";

export function Label({ className, ...rest }: LabelHTMLAttributes<HTMLLabelElement>) {
  return (
    <label
      className={clsx("text-xs font-medium uppercase tracking-wide text-slate", className)}
      {...rest}
    />
  );
}
""",
)

write(
    "components/ui/Panel.tsx",
    """import { HTMLAttributes } from "react";
import clsx from "clsx";

export function Panel({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={clsx("panel", className)} {...rest} />;
}
""",
)

write(
    "components/ui/Field.tsx",
    """import { ReactNode } from "react";

export function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <div className="text-xs font-medium uppercase tracking-wide text-slate">{label}</div>
      {children}
      {hint ? <div className="text-xs text-slate">{hint}</div> : null}
    </div>
  );
}
""",
)

# ===================================================================
# middleware.ts — refresh sessions on every request
# ===================================================================
write(
    "middleware.ts",
    """import { NextRequest, NextResponse } from "next/server";
import { createServerClient, type CookieOptions } from "@supabase/ssr";

export async function middleware(req: NextRequest) {
  const res = NextResponse.next();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return req.cookies.getAll();
        },
        setAll(toSet: { name: string; value: string; options: CookieOptions }[]) {
          for (const { name, value, options } of toSet) {
            res.cookies.set(name, value, options);
          }
        },
      },
    },
  );
  await supabase.auth.getUser();
  return res;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\\\.svg).*)"],
};
""",
)

# ===================================================================
# app/auth/callback/route.ts — code exchange after email links
# ===================================================================
write(
    "app/auth/callback/route.ts",
    """import { NextRequest, NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export async function GET(req: NextRequest) {
  const { searchParams, origin } = new URL(req.url);
  const code = searchParams.get("code");
  const next = searchParams.get("next") ?? "/dashboard";

  if (code) {
    const supabase = await createSupabaseServerClient();
    await supabase.auth.exchangeCodeForSession(code);
  }
  return NextResponse.redirect(`${origin}${next}`);
}
""",
)

# ===================================================================
# lib/auth/actions.ts — server actions
# ===================================================================
write(
    "lib/auth/actions.ts",
    """"use server";

import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { headers } from "next/headers";
import { z } from "zod";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { createSupabaseAdminClient } from "@/lib/supabase/admin";
import { env } from "@/lib/env";
import { createEmbeddedWallet, decryptPrivateKey, keystore } from "@/lib/wallet/keystore";
import { generateRecoveryPhrase, normalisePhrase } from "@/lib/wallet/recovery";
import { enc } from "@/lib/wallet/crypto";

const SignupSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8, "Password must be at least 8 characters"),
  displayName: z.string().min(1).max(80),
});

const LoginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

export type SignupResult =
  | { ok: true; recoveryPhrase: string; walletAddress: string }
  | { ok: false; error: string };

export async function signupAction(formData: FormData): Promise<SignupResult> {
  const parsed = SignupSchema.safeParse({
    email: formData.get("email"),
    password: formData.get("password"),
    displayName: formData.get("displayName"),
  });
  if (!parsed.success) {
    return { ok: false, error: parsed.error.issues[0]?.message ?? "Invalid input" };
  }
  const { email, password, displayName } = parsed.data;

  const supabase = await createSupabaseServerClient();
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { data: { display_name: displayName } },
  });
  if (error || !data.user) {
    return { ok: false, error: error?.message ?? "Could not create account" };
  }
  const userId = data.user.id;

  const recoveryPhrase = generateRecoveryPhrase();
  const material = await createEmbeddedWallet(password, recoveryPhrase, env.walletPepper);

  const admin = createSupabaseAdminClient();

  const { error: profileErr } = await admin.from("profiles").insert({
    id: userId,
    email,
    display_name: displayName,
    role: "user",
    onboarding_completed: false,
  });
  if (profileErr) return { ok: false, error: "Profile creation failed: " + profileErr.message };

  const { data: walletRow, error: walletErr } = await admin
    .from("wallets")
    .insert({
      user_id: userId,
      address: material.address,
      encrypted_private_key: material.encryptedPrivateKey,
      encryption_version: 1,
    })
    .select("id")
    .single();
  if (walletErr || !walletRow) {
    return { ok: false, error: "Wallet creation failed: " + (walletErr?.message ?? "unknown") };
  }

  const { error: wrapErr } = await admin.from("wallet_key_wraps").insert([
    {
      wallet_id: walletRow.id,
      user_id: userId,
      method: "password",
      encrypted_wallet_key: material.passwordWrap.encryptedWalletKey,
      salt: material.passwordWrap.salt,
      kdf_params: material.passwordWrap.kdfParams,
    },
    {
      wallet_id: walletRow.id,
      user_id: userId,
      method: "recovery_key",
      encrypted_wallet_key: material.recoveryWrap.encryptedWalletKey,
      salt: material.recoveryWrap.salt,
      kdf_params: material.recoveryWrap.kdfParams,
    },
  ]);
  if (wrapErr) return { ok: false, error: "Key wrap failed: " + wrapErr.message };

  return { ok: true, recoveryPhrase, walletAddress: material.address };
}

export async function loginAction(formData: FormData): Promise<{ ok: boolean; error?: string }> {
  const parsed = LoginSchema.safeParse({
    email: formData.get("email"),
    password: formData.get("password"),
  });
  if (!parsed.success) return { ok: false, error: "Invalid email or password" };

  const supabase = await createSupabaseServerClient();
  const { error } = await supabase.auth.signInWithPassword(parsed.data);
  if (error) return { ok: false, error: error.message };
  return { ok: true };
}

export async function logoutAction() {
  const supabase = await createSupabaseServerClient();
  await supabase.auth.signOut();
  revalidatePath("/", "layout");
  redirect("/login");
}

export async function forgotPasswordAction(formData: FormData) {
  const email = String(formData.get("email") ?? "");
  if (!/.+@.+/.test(email)) return { ok: false, error: "Enter a valid email" };
  const h = await headers();
  const origin = h.get("origin") ?? "http://localhost:3000";
  const supabase = await createSupabaseServerClient();
  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${origin}/auth/callback?next=/reset-password`,
  });
  if (error) return { ok: false, error: error.message };
  return { ok: true };
}

/**
 * Reset password using the recovery phrase to re-wrap the SAME wallet
 * encryption key under a new password. Wallet address never changes.
 *
 * Requires the user to be in a recovery session (Supabase places them
 * in one when they click the reset email link and the /auth/callback
 * route exchanges the code).
 */
export async function resetPasswordAction(formData: FormData) {
  const newPassword = String(formData.get("newPassword") ?? "");
  const recoveryPhrase = String(formData.get("recoveryPhrase") ?? "");
  if (newPassword.length < 8) return { ok: false, error: "Password must be at least 8 characters" };
  if (!recoveryPhrase) return { ok: false, error: "Recovery phrase is required" };

  const supabase = await createSupabaseServerClient();
  const { data: userData } = await supabase.auth.getUser();
  if (!userData.user) return { ok: false, error: "No active recovery session. Re-open the email link." };
  const userId = userData.user.id;

  const admin = createSupabaseAdminClient();
  const { data: wallet, error: wErr } = await admin
    .from("wallets")
    .select("id")
    .eq("user_id", userId)
    .single();
  if (wErr || !wallet) return { ok: false, error: "Wallet not found" };

  const { data: wraps, error: wrapsErr } = await admin
    .from("wallet_key_wraps")
    .select("method,encrypted_wallet_key,salt,kdf_params")
    .eq("wallet_id", wallet.id);
  if (wrapsErr || !wraps) return { ok: false, error: "Key wraps not found" };

  const recovery = wraps.find((w) => w.method === "recovery_key");
  if (!recovery) return { ok: false, error: "Recovery wrap not found" };

  let wek: Uint8Array;
  try {
    wek = await keystore.unwrapWek(
      normalisePhrase(recoveryPhrase),
      {
        encryptedWalletKey: recovery.encrypted_wallet_key,
        salt: recovery.salt,
        kdfParams: recovery.kdf_params,
      },
      env.walletPepper,
    );
  } catch {
    return { ok: false, error: "Recovery phrase did not unlock the wallet" };
  }

  const newPwWrap = await keystore.wrapWek(newPassword, wek, env.walletPepper);

  const { error: updErr } = await admin
    .from("wallet_key_wraps")
    .update({
      encrypted_wallet_key: newPwWrap.encryptedWalletKey,
      salt: newPwWrap.salt,
      kdf_params: newPwWrap.kdfParams,
    })
    .eq("wallet_id", wallet.id)
    .eq("method", "password");
  if (updErr) return { ok: false, error: "Failed to re-wrap key: " + updErr.message };

  const { error: pwErr } = await supabase.auth.updateUser({ password: newPassword });
  if (pwErr) return { ok: false, error: pwErr.message };

  await admin.from("recovery_audit_logs").insert({
    user_id: userId,
    wallet_id: wallet.id,
    action: "password_reset_via_recovery",
  });

  return { ok: true };
}

export async function exportPrivateKeyAction(formData: FormData) {
  const password = String(formData.get("password") ?? "");
  const recoveryPhrase = String(formData.get("recoveryPhrase") ?? "");
  if (!password || !recoveryPhrase) {
    return { ok: false as const, error: "Password and recovery phrase are required" };
  }

  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (!u.user) return { ok: false as const, error: "Not signed in" };

  // Re-verify password against Supabase Auth.
  const reauth = await supabase.auth.signInWithPassword({
    email: u.user.email!,
    password,
  });
  if (reauth.error) return { ok: false as const, error: "Password incorrect" };

  const admin = createSupabaseAdminClient();
  const { data: wallet } = await admin
    .from("wallets")
    .select("id,address,encrypted_private_key")
    .eq("user_id", u.user.id)
    .single();
  if (!wallet) return { ok: false as const, error: "Wallet not found" };

  const { data: wraps } = await admin
    .from("wallet_key_wraps")
    .select("method,encrypted_wallet_key,salt,kdf_params")
    .eq("wallet_id", wallet.id);
  const rk = wraps?.find((w) => w.method === "recovery_key");
  if (!rk) return { ok: false as const, error: "Recovery wrap missing" };

  let wek: Uint8Array;
  try {
    wek = await keystore.unwrapWek(
      normalisePhrase(recoveryPhrase),
      {
        encryptedWalletKey: rk.encrypted_wallet_key,
        salt: rk.salt,
        kdfParams: rk.kdf_params,
      },
      env.walletPepper,
    );
  } catch {
    return { ok: false as const, error: "Recovery phrase invalid" };
  }

  const pk = await decryptPrivateKey(wallet.encrypted_private_key, wek);

  await admin.from("recovery_audit_logs").insert({
    user_id: u.user.id,
    wallet_id: wallet.id,
    action: "private_key_export",
  });

  return { ok: true as const, address: wallet.address, privateKey: pk };
}
""",
)

# ===================================================================
# app/(auth)/layout.tsx
# ===================================================================
write(
    "app/(auth)/layout.tsx",
    """import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-graphite">
      <header className="border-b border-gridline bg-panel">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="display text-xl font-bold text-obsidian">
            VeriSight
          </Link>
          <span className="mono text-xs uppercase tracking-[0.18em] text-consensus">
            Consensus backed analytics assurance
          </span>
        </div>
      </header>
      <main className="mx-auto flex max-w-md flex-col px-6 py-16">{children}</main>
    </div>
  );
}
""",
)

# ===================================================================
# Signup page (client form, calls server action, renders recovery phrase)
# ===================================================================
write(
    "app/(auth)/signup/page.tsx",
    """"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { signupAction } from "@/lib/auth/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Panel } from "@/components/ui/Panel";

export default function SignupPage() {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [recovery, setRecovery] = useState<{ phrase: string; address: string } | null>(null);
  const [ack, setAck] = useState(false);

  if (recovery) {
    return (
      <div className="space-y-5">
        <Panel className="p-6">
          <div className="mono text-xs uppercase tracking-[0.18em] text-consensus">
            Recovery key — shown only once
          </div>
          <h1 className="display mt-2 text-section font-semibold text-obsidian">
            Save your recovery phrase
          </h1>
          <p className="mt-2 text-sm text-slate">
            This 24-word phrase is the only way to restore your embedded wallet if you reset
            your password. Store it somewhere safe and offline. VeriSight cannot recover it
            for you.
          </p>
          <div className="mono mt-4 rounded-btn border border-gridline bg-graphite p-4 text-sm leading-relaxed text-ink">
            {recovery.phrase}
          </div>
          <div className="mt-4 text-xs text-slate">
            Wallet address
            <div className="mono mt-1 break-all text-ink">{recovery.address}</div>
          </div>
          <label className="mt-5 flex items-start gap-2 text-sm text-ink">
            <input
              type="checkbox"
              checked={ack}
              onChange={(e) => setAck(e.target.checked)}
              className="mt-1"
            />
            <span>
              I have saved my recovery phrase somewhere safe and understand it cannot be
              recovered if lost.
            </span>
          </label>
          <Button
            className="mt-5 w-full"
            disabled={!ack}
            onClick={() => router.push("/onboarding")}
          >
            Continue to onboarding
          </Button>
        </Panel>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="display text-pagetitle font-semibold text-obsidian">
          Create your VeriSight account
        </h1>
        <p className="mt-2 text-sm text-slate">
          Your VeriSight profile includes a secure embedded wallet used only for GenLayer
          audit actions. No MetaMask. No Rabby.
        </p>
      </div>

      <Panel className="p-6">
        <form
          className="space-y-4"
          action={(fd) => {
            setError(null);
            start(async () => {
              const res = await signupAction(fd);
              if (!res.ok) setError(res.error);
              else setRecovery({ phrase: res.recoveryPhrase, address: res.walletAddress });
            });
          }}
        >
          <Field label="Display name">
            <Input name="displayName" required placeholder="Analyst name" />
          </Field>
          <Field label="Email">
            <Input type="email" name="email" required placeholder="you@company.com" />
          </Field>
          <Field label="Password" hint="At least 8 characters.">
            <Input type="password" name="password" required minLength={8} />
          </Field>
          {error ? (
            <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">
              {error}
            </div>
          ) : null}
          <Button type="submit" className="w-full" disabled={pending}>
            {pending ? "Creating account…" : "Create account"}
          </Button>
        </form>
      </Panel>

      <p className="text-sm text-slate">
        Already have an account?{" "}
        <Link href="/login" className="text-analyst underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
""",
)

# ===================================================================
# Login page
# ===================================================================
write(
    "app/(auth)/login/page.tsx",
    """"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { loginAction } from "@/lib/auth/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Panel } from "@/components/ui/Panel";

export default function LoginPage() {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="display text-pagetitle font-semibold text-obsidian">
          Sign in to VeriSight
        </h1>
        <p className="mt-2 text-sm text-slate">
          Email and password only. Your embedded wallet is unlocked in the background.
        </p>
      </div>
      <Panel className="p-6">
        <form
          className="space-y-4"
          action={(fd) => {
            setError(null);
            start(async () => {
              const res = await loginAction(fd);
              if (!res.ok) setError(res.error ?? "Sign in failed");
              else router.push("/dashboard");
            });
          }}
        >
          <Field label="Email">
            <Input type="email" name="email" required />
          </Field>
          <Field label="Password">
            <Input type="password" name="password" required />
          </Field>
          {error ? (
            <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">
              {error}
            </div>
          ) : null}
          <Button type="submit" className="w-full" disabled={pending}>
            {pending ? "Signing in…" : "Continue"}
          </Button>
        </form>
        <div className="mt-4 flex items-center justify-between text-sm">
          <Link href="/forgot-password" className="text-analyst underline">
            Forgot password
          </Link>
          <Link href="/signup" className="text-analyst underline">
            Create account
          </Link>
        </div>
      </Panel>
    </div>
  );
}
""",
)

# ===================================================================
# Forgot password page
# ===================================================================
write(
    "app/(auth)/forgot-password/page.tsx",
    """"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { forgotPasswordAction } from "@/lib/auth/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Panel } from "@/components/ui/Panel";

export default function ForgotPasswordPage() {
  const [pending, start] = useTransition();
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="display text-pagetitle font-semibold text-obsidian">
          Forgot password
        </h1>
        <p className="mt-2 text-sm text-slate">
          We will email you a reset link. Your wallet is not reset — you will need your
          recovery phrase to finish the reset.
        </p>
      </div>
      <Panel className="p-6">
        <form
          className="space-y-4"
          action={(fd) => {
            setError(null);
            setMsg(null);
            start(async () => {
              const res = await forgotPasswordAction(fd);
              if (!res.ok) setError(res.error ?? "Failed");
              else setMsg("Check your email for a reset link.");
            });
          }}
        >
          <Field label="Email">
            <Input type="email" name="email" required />
          </Field>
          {error ? (
            <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">
              {error}
            </div>
          ) : null}
          {msg ? (
            <div className="rounded-btn border border-verified/40 bg-verified/5 p-3 text-sm text-verified">
              {msg}
            </div>
          ) : null}
          <Button type="submit" className="w-full" disabled={pending}>
            {pending ? "Sending…" : "Send reset link"}
          </Button>
        </form>
        <div className="mt-4 text-sm">
          <Link href="/login" className="text-analyst underline">
            Back to sign in
          </Link>
        </div>
      </Panel>
    </div>
  );
}
""",
)

# ===================================================================
# Reset password page
# ===================================================================
write(
    "app/(auth)/reset-password/page.tsx",
    """"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { resetPasswordAction } from "@/lib/auth/actions";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Panel } from "@/components/ui/Panel";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="display text-pagetitle font-semibold text-obsidian">
          Reset password
        </h1>
        <p className="mt-2 text-sm text-slate">
          Enter your recovery phrase so VeriSight can re-encrypt your embedded wallet
          under the new password. Your wallet address will not change.
        </p>
      </div>
      <Panel className="p-6">
        <form
          className="space-y-4"
          action={(fd) => {
            setError(null);
            start(async () => {
              const res = await resetPasswordAction(fd);
              if (!res.ok) setError(res.error ?? "Failed");
              else router.push("/dashboard");
            });
          }}
        >
          <Field label="New password">
            <Input type="password" name="newPassword" required minLength={8} />
          </Field>
          <Field label="Recovery phrase">
            <textarea
              name="recoveryPhrase"
              required
              rows={3}
              className="mono w-full rounded-btn border border-gridline bg-panel px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-analyst"
              placeholder="word1 word2 word3 … (24 words)"
            />
          </Field>
          {error ? (
            <div className="rounded-btn border border-claim/40 bg-claim/5 p-3 text-sm text-claim">
              {error}
            </div>
          ) : null}
          <Button type="submit" className="w-full" disabled={pending}>
            {pending ? "Re-wrapping wallet…" : "Set new password"}
          </Button>
        </form>
      </Panel>
    </div>
  );
}
""",
)

print("\nStage 3 files written.")
