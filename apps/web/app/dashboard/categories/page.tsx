"use client";

import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Field, SelectInput, TextInput } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { CategoryBoard } from "@/features/categories/category-board";
import { useCategories } from "@/hooks/use-dashboard-data";

export default function CategoriesPage() {
  const { data = [], isError } = useCategories();
  const income = data.filter((category) => category.type === "income");
  const expense = data.filter((category) => category.type === "expense");
  if (isError) return <EmptyState title="Categories unavailable" description="Kategoriyalarni yuklab bo‘lmadi. Backend ulanishini tekshiring." />;

  return (
    <div className="space-y-6">
      <Card className="p-5">
        <div className="grid gap-4 xl:grid-cols-[1fr_1.4fr] xl:items-end">
          <div>
            <h1 className="text-xl font-semibold text-ink">Categories</h1>
            <p className="mt-1 text-sm text-muted">Default categories fit Uzbek SMB operations. Custom categories stay company-scoped.</p>
          </div>
          <form className="grid gap-2 md:grid-cols-[1fr_160px_120px_auto]">
            <Field label="Name"><TextInput placeholder="Packaging" /></Field>
            <Field label="Type"><SelectInput><option>expense</option><option>income</option></SelectInput></Field>
            <Field label="Color"><TextInput type="color" defaultValue="#172033" /></Field>
            <Button type="button">Create</Button>
          </form>
        </div>
      </Card>
      <div className="grid gap-6 xl:grid-cols-2">
        <CategoryBoard title="Income categories" type="income" categories={income} />
        <CategoryBoard title="Expense categories" type="expense" categories={expense} />
      </div>
    </div>
  );
}
