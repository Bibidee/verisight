import { createClient } from "@supabase/supabase-js";
import { env } from "../env";

// Service-role client. SERVER ONLY. Never import from client components.
export function createSupabaseAdminClient() {
  if (!env.supabaseServiceRoleKey) {
    throw new Error("SUPABASE_SERVICE_ROLE_KEY is not set");
  }
  return createClient(env.supabaseUrl, env.supabaseServiceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}
