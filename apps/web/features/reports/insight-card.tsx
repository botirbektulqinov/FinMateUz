import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { formatMoney, formatPercent } from "@/lib/format";
import type { CategoryBreakdownPoint, ReportSummary } from "@/lib/types";

export function InsightCard({ summary, biggestExpense }: { summary: ReportSummary; biggestExpense?: CategoryBreakdownPoint }) {
  const net = Number(summary.net_cash_flow);
  const positive = net >= 0;
  const approvalCopy =
    summary.pending_approval_count > 0
      ? `${summary.pending_approval_count} pending transaction final reportga kirmagan. Tasdiqlangandan keyin cash flow yangilanadi.`
      : "Pending approval yo‘q. Final report confirmed transactionlarga tayanmoqda.";
  return (
    <Card className="p-5">
      <div className="flex items-center gap-2 text-sm font-semibold text-ink">
        {positive ? <ArrowUpRight className="h-4 w-4 text-success" /> : <ArrowDownRight className="h-4 w-4 text-danger" />}
        Cash flow insight
      </div>
      <p className="mt-3 text-sm leading-6 text-muted">
        Net cash flow is <span className={positive ? "font-semibold text-success" : "font-semibold text-danger"}>{formatMoney(summary.net_cash_flow)}</span>.
        Income changed {formatPercent(summary.income_change_percent)} from the previous month. Biggest expense category is {biggestExpense?.category_name ?? "not available yet"}.
      </p>
      <p className="mt-3 text-sm text-muted">{approvalCopy}</p>
    </Card>
  );
}
