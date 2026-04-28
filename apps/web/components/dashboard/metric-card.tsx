import { ReactNode } from "react";
import { Card } from "@/components/ui/card";

export function MetricCard({
  label,
  value,
  detail,
  tone = "neutral",
  icon
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "neutral" | "good" | "bad" | "warn";
  icon?: ReactNode;
}) {
  const toneClass = tone === "good" ? "text-success" : tone === "bad" ? "text-danger" : tone === "warn" ? "text-amber" : "text-ink";
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted">{label}</span>
        <span className="text-muted">{icon}</span>
      </div>
      <div className={`mt-3 text-2xl font-semibold tracking-normal ${toneClass}`}>{value}</div>
      <div className="mt-2 text-sm text-muted">{detail}</div>
    </Card>
  );
}
