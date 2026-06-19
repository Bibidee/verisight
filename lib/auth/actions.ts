"use server";

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

  // Auto-confirm email so the user can sign in immediately. The embedded wallet
  // is the security artefact for VeriSight, not email verification.
  await admin.auth.admin.updateUserById(userId, { email_confirm: true });

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
