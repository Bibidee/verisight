"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { createSupabaseAdminClient } from "@/lib/supabase/admin";

const WorkspaceSchema = z.object({
  name: z.string().min(1).max(120),
  organisation_name: z.string().max(160).optional().nullable(),
  business_function: z.string().max(80).optional().nullable(),
  industry: z.string().max(80).optional().nullable(),
  reporting_cadence: z.string().max(40).optional().nullable(),
  primary_kpi_category: z.string().max(80).optional().nullable(),
});

function clean(fd: FormData) {
  const obj: Record<string, string | null> = {};
  for (const k of [
    "name",
    "organisation_name",
    "business_function",
    "industry",
    "reporting_cadence",
    "primary_kpi_category",
  ]) {
    const v = fd.get(k);
    obj[k] = v ? String(v) : null;
  }
  return obj;
}

export async function createWorkspaceAction(formData: FormData) {
  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (!u.user) return { ok: false as const, error: "Not signed in" };

  const parsed = WorkspaceSchema.safeParse(clean(formData));
  if (!parsed.success) {
    return { ok: false as const, error: parsed.error.issues[0]?.message ?? "Invalid input" };
  }

  const { data, error } = await supabase
    .from("workspaces")
    .insert({ ...parsed.data, user_id: u.user.id })
    .select("id")
    .single();
  if (error || !data) return { ok: false as const, error: error?.message ?? "Failed" };

  revalidatePath("/workspaces");
  revalidatePath("/dashboard");
  return { ok: true as const, id: data.id };
}

export async function completeOnboardingAction(formData: FormData) {
  const res = await createWorkspaceAction(formData);
  if (!res.ok) return res;

  const supabase = await createSupabaseServerClient();
  const { data: u } = await supabase.auth.getUser();
  if (u.user) {
    const admin = createSupabaseAdminClient();
    await admin
      .from("profiles")
      .update({ onboarding_completed: true })
      .eq("id", u.user.id);
  }
  redirect("/dashboard");
}

export async function deleteWorkspaceAction(id: string) {
  const supabase = await createSupabaseServerClient();
  const { error } = await supabase.from("workspaces").delete().eq("id", id);
  if (error) return { ok: false as const, error: error.message };
  revalidatePath("/workspaces");
  return { ok: true as const };
}
