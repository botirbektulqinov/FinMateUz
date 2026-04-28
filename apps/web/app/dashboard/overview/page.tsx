"use client";

import { AlertCircle, ArrowDownCircle, ArrowUpCircle, WalletCards } from "lucide-react";
import { Card, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { IncomeExpenseChart } from "@/components/dashboard/charts";
import { MetricCard } from "@/components/dashboard/metric-card";
import { InsightCard } from "@/features/reports/insight-card";
import { QuickAddForm } from "@/features/transactions/quick-add-form";
import { TransactionTable } from "@/features/transactions/transaction-table";
import { useReport } from "@/hooks/use-dashboard-data";
import { formatMoney, formatPercent } from "@/lib/format";

export default function OverviewPage() {
  const { data, isLoading, isError } = useReport();
  if (isLoading) return <OverviewSkeleton />;
  if (isError || !data) return <EmptyState title="Could not load dashboard" description="API bilan aloqa uzildi. Birozdan keyin qayta urinib ko‘ring." />;

  const biggestExpense = data.top_expense_categories[0];
  const hasTransactions = data.recent_transactions.length > 0;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Current month income" value={formatMoney(data.summary.month_income)} detail={`${formatPercent(data.summary.income_change_percent)} vs previous month`} tone="good" icon={<ArrowUpCircle className="h-5 w-5" />} />
        <MetricCard label="Current month expenses" value={formatMoney(data.summary.month_expenses)} detail={`${formatPercent(data.summary.expense_change_percent)} vs previous month`} tone="bad" icon={<ArrowDownCircle className="h-5 w-5" />} />
        <MetricCard label="Net cash flow" value={formatMoney(data.summary.net_cash_flow)} detail="Confirmed transactions only" tone={Number(data.summary.net_cash_flow) >= 0 ? "good" : "bad"} icon={<WalletCards className="h-5 w-5" />} />
        <MetricCard label="Pending approvals" value={String(data.summary.pending_approval_count)} detail="Operator submissions waiting" tone="warn" icon={<AlertCircle className="h-5 w-5" />} />
      </div>
      {!hasTransactions ? (
        <EmptyState title="Hali transaction yo‘q" description="Birinchi kirim yoki chiqimni qo‘shing — keyin bu yerda cash flow ko‘rinadi." />
      ) : null}
      <QuickAddForm />
      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
        <Card>
          <CardHeader title="Income vs expenses" description="Monthly confirmed transaction movement." />
          <div className="p-5"><IncomeExpenseChart data={data.income_vs_expenses} /></div>
        </Card>
        <InsightCard summary={data.summary} biggestExpense={biggestExpense} />
      </div>
      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-ink">Recent transactions</h2>
        </div>
        <TransactionTable transactions={data.recent_transactions} />
      </section>
    </div>
  );
}

function OverviewSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-4">{Array.from({ length: 4 }).map((_, index) => <Skeleton key={index} className="h-32" />)}</div>
      <Skeleton className="h-44" />
      <Skeleton className="h-80" />
    </div>
  );
}
