import { HTMLAttributes } from "react";
import clsx from "clsx";

type Tone = "light" | "dark" | "darker" | "steel";
interface Props extends HTMLAttributes<HTMLDivElement> { tone?: Tone }

const toneClass: Record<Tone, string> = {
  light: "panel",
  dark: "panel-dark",
  darker: "panel-darker",
  steel: "panel-steel",
};

export function Panel({ tone = "light", className, ...rest }: Props) {
  return <div className={clsx(toneClass[tone], className)} {...rest} />;
}

export function PanelHeader({
  title, eyebrow, right, tone = "light",
}: { title: string; eyebrow?: string; right?: React.ReactNode; tone?: "light" | "dark" }) {
  return (
    <div className={clsx("panel-header", tone === "dark" && "dark")}>
      <div>
        {eyebrow ? <div className="eyebrow eyebrow-slate">{eyebrow}</div> : null}
        <div className="display text-[15px] font-semibold">{title}</div>
      </div>
      {right}
    </div>
  );
}
