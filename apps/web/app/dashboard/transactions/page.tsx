"use client";

import { Search } from "lucide-react";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SelectInput, TextInput } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { QuickAddForm } from "@/features/transactions/quick-add-form";
import { TransactionTable } from "@/features/transactions/transaction-table";
import { useCategories, useTransactions } from "@/hooks/use-dashboard-data";

export default function TransactionsPage() {
  const transactions = useTransactions();
  const categories = useCategories();

  return (
    <div className="space-y-5">
      <Card className="p-5">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <h1 className="text-xl font-semibold text-ink">Transactions</h1>
            <p className="mt-1 text-sm text-muted">Review Telegram and dashboard entries, approve pending items, and keep cash flow clean.</p>
          </div>
          <div className="grid gap-2 md:grid-cols-[1.4fr_1fr_1fr_1fr_1fr]">
            <div className="flex items-center gap-2 rounded-md border border-line bg-white px-3">
              <Search className="h-4 w-4 text-muted" />
              <input className="w-full py-2 text-sm outline-none" placeholder="Search note or category" />
            </div>
            <TextInput type="date" aria-label="Start date" />
            <TextInput type="date" aria-label="End date" />
            <SelectInput aria-label="Type filter">
              <option>All types</option>
              <option>Income</option>
              <option>Expense</option>
            </SelectInput>
            <SelectInput aria-label="Category filter">
              <option>All categories</option>
              {categories.data?.map((category) => <option key={category.id}>{category.name}</option>)}
            </SelectInput>
          </div>
        </div>
      </Card>
      <QuickAddForm />
      {transactions.isLoading ? <Skeleton className="h-96" /> : null}
      {transactions.isError ? <EmptyState title="Transactions unavailable" description="API bilan aloqa uzildi. Filterlarni tekshirib qayta urinib ko‘ring." /> : null}
      {transactions.data ? <TransactionTable transactions={transactions.data.items} /> : null}
    </div>
  );
}
