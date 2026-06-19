import clsx from "clsx";
import {
  getGenLayerTxUrl,
  getGenLayerAddressUrl,
} from "@/lib/genlayer/explorer";

export function HashText({
  value,
  short,
  dark,
  className,
  explorerType,
}: {
  value: string;
  short?: boolean;
  dark?: boolean;
  className?: string;
  explorerType?: "tx" | "address";
}) {
  const display =
    short && value.length > 14
      ? `${value.slice(0, 8)}…${value.slice(-6)}`
      : value;
  const cls = clsx(dark ? "hash-dark" : "hash", className);

  if (explorerType && value.startsWith("0x")) {
    const href =
      explorerType === "tx"
        ? getGenLayerTxUrl(value)
        : getGenLayerAddressUrl(value);

    if (href) {
      return (
        <a
          href={href}
          target="_blank"
          rel="noreferrer"
          className={clsx(
            cls,
            "underline decoration-dotted hover:decoration-solid",
          )}
          title={value}
        >
          {display} ↗
        </a>
      );
    }
  }

  return (
    <span className={cls} title={value.length > 14 ? value : undefined}>
      {display}
    </span>
  );
}
