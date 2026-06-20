import { redirect } from "next/navigation";
import { getProfile, isAdminUser } from "@/lib/auth/getUser";
import { ExecutiveTopNav } from "@/components/app/ExecutiveTopNav";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, profile } = await getProfile();
  if (!profile) redirect("/login");

  return (
    <div className="min-h-screen bg-frost-grey">
      <ExecutiveTopNav
        email={user.email ?? ""}
        displayName={profile.display_name}
        isAdmin={isAdminUser(user.email)}
      />
      <div className="mx-auto w-full max-w-[1400px]">{children}</div>
    </div>
  );
}
