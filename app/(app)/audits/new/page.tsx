import { redirect } from "next/navigation";
import { requireUser } from "@/lib/auth/getUser";
import { SubContextBar } from "@/components/app/SubContextBar";
import { Badge } from "@/components/audit/Badge";
import { NewAuditForm } from "./NewAuditForm";

export default async function OpenClaimReviewPage({
  searchParams,
}: {
  searchParams: Promise<{ workspace?: string }>;
}) {
  const { supabase } = await requireUser();
  const sp = await searchParams;

  const { data: workspaces } = await supabase
    .from("workspaces")
    .select("id,name,organisation_name,primary_kpi_category")
    .order("created_at", { ascending: false });

  if (!workspaces || workspaces.length === 0) {
    redirect("/onboarding");
  }

  return (
    <>
      <SubContextBar
        eyebrow="Audit intake"
        title="Open Claim Review"
        right={<Badge tone="consensus" dot>Draft · awaiting submission</Badge>}
      />
      <main className="px-6 py-6">
        <NewAuditForm
          workspaces={workspaces}
          initialWorkspaceId={sp.workspace ?? workspaces[0].id}
        />
      </main>
    </>
  );
}
