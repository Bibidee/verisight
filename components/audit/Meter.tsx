import clsx from "clsx";

const fill: Record<"emerald" | "amber" | "claim" | "blue" | "cyan" | "consensus", string> = {
  emerald: "bg-emerald", amber: "bg-amber", claim: "bg-claim",
  blue: "bg-exec-blue", cyan: "bg-data-cyan", consensus: "bg-consensus",
};

export function Meter({ value, tone = "blue", className }: {
  value: number; tone?: keyof typeof fill; className?: string;
}) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div className={clsx("meter", className)}>
      <div className={clsx("fill", fill[tone])} style={{ width: `${v}%` }} />
    </div>
  );
}
