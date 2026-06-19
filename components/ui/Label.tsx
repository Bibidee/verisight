import { LabelHTMLAttributes } from "react";
import clsx from "clsx";
export function Label({ className, ...rest }: LabelHTMLAttributes<HTMLLabelElement>) {
  return <label className={clsx("text-[11px] font-semibold uppercase tracking-[0.08em] text-slate", className)} {...rest} />;
}
