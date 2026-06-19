import { ButtonHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

type Variant = "primary" | "secondary" | "exec" | "consensus" | "danger" | "ghost";
interface Props extends ButtonHTMLAttributes<HTMLButtonElement> { variant?: Variant }

const variantClass: Record<Variant, string> = {
  primary: "btn-primary",
  secondary: "btn-secondary",
  exec: "btn-exec",
  consensus: "btn-consensus",
  danger: "btn-danger",
  ghost: "btn-ghost",
};

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variant = "primary", className, ...rest },
  ref,
) {
  return <button ref={ref} className={clsx(variantClass[variant], "disabled:opacity-60", className)} {...rest} />;
});
