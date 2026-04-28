"use client";

import { Card, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { BreakdownChart, CashFlowTrend, IncomeExpenseChart } from "@/components/dashboard/charts";
import { InsightCard } from "@/features/reports/insight-card";
import { useReport } from "@/hooks/use-dashboard-data";
import { formatMoney } from "@/lib/format";

export default function AnalyticsPage() {
  const { data, isLoading, isError } = useReport();
  if (isLoading) return <Skeleton className="h-[620px]" />;
  if (isError || !data) return <EmptyState title="Analytics unavailable" description="Hisobotlarni yuklab bo‘lmadi. Backend ulanishini tekshiring." />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Analytics</h1>
        <p className="mt-1 text-sm text-muted">Reports use confirmed transactions by default. Pending approvals stay separate.</p>
      </div>
      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader title="Income vs expenses" description="Side-by-side monthly movement." />
          <div className="p-5"><IncomeExpenseChart data={data.income_vs_expenses} /></div>
        </Card>
        <Card>
          <CardHeader title="Monthly cash flow trend" description="Net movement after expenses." />
          <div className="p-5"><CashFlowTrend data={data.income_vs_expenses} /></div>
        </Card>
        <Card>
          <CardHeader title="Expense breakdown by category" />
          <div className="p-5"><BreakdownChart data={data.expense_breakdown} /></div>
        </Card>
        <Card>
          <CardHeader title="Income breakdown by category" />
          <div className="p-5"><BreakdownChart data={data.income_breakdown} /></div>
        </Card>
      </div>
      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <InsightCard summary={data.summary} biggestExpense={data.top_expense_categories[0]} />
        <Card>
          <CardHeader title="Top expense categories" description="Highest confirmed spend this month." />
          <div className="divide-y divide-line">
            {data.top_expense_categories.map((item) => (
              <div key={item.category_id} className="flex items-center justify-between px-5 py-3">
                <span className="font-medium text-ink">{item.category_name}</span>
                <span className="font-semibold text-danger">{formatMoney(item.total)}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
