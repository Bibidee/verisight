import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export async function requireUser() {
  const supabase = await createSupabaseServerClient();
  const { data } = await supabase.auth.getUser();
  if (!data.user) redirect("/login");
  return { user: data.user, supabase };
}

const ADMIN_EMAILS = new Set([
  "ojikutusarat@gmail.com",
]);

export function isAdminUser(email: string | undefined | null): boolean {
  return !!email && ADMIN_EMAILS.has(email.toLowerCase());
}

export async function getProfile() {
  const { user, supabase } = await requireUser();
  const { data: profile } = await supabase
    .from("profiles")
    .select("id,email,display_name,role,onboarding_completed")
    .eq("id", user.id)
    .single();
  return { user, profile, supabase };
}
