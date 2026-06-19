import clsx from "clsx";
import { ReactNode } from "react";

type Tone =
  | "consensus" | "verified" | "amber" | "claim" | "cyan" | "blue" | "slate" | "dark";

const toneClass: Record<Tone, string> = {
  consensus: "badge-consensus",
  verified: "badge-verified",
  amber: "badge-amber",
  claim: "badge-claim",
  cyan: "badge-cyan",
  blue: "badge-blue",
  slate: "badge-slate",
  dark: "badge-dark",
};

export function Badge({ tone = "slate", children, className, dot }: {
  tone?: Tone; children: ReactNode; className?: string; dot?: boolean;
}) {
  const d: Record<Tone, string> = {
    consensus: "dot dot-consensus", verified: "dot dot-verified",
    amber: "dot dot-amber", claim: "dot dot-claim",
    cyan: "dot dot-cyan", blue: "dot dot-cyan",
    slate: "dot dot-slate", dark: "dot dot-slate",
  };
  return (
    <span className={clsx("badge", toneClass[tone], className)}>
      {dot ? <span className={d[tone]} /> : null}
      {children}
    </span>
  );
}
