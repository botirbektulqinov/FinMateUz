import type { TransactionSource, TransactionStatus } from "@/lib/types";

export function StatusBadge({ status }: { status: TransactionStatus }) {
  const classes = {
    confirmed: "bg-green-50 text-success",
    pending: "bg-yellow-50 text-amber",
    rejected: "bg-red-50 text-danger",
    deleted: "bg-slate-100 text-muted"
  };
  return <span className={`rounded-md px-2 py-1 text-xs font-semibold ${classes[status]}`}>{status}</span>;
}

export function SourceBadge({ source }: { source: TransactionSource }) {
  return <span className="rounded-md bg-canvas px-2 py-1 text-xs font-semibold text-ink">{source === "telegram" ? "Telegram" : "Dashboard"}</span>;
}
