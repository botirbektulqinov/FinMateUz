"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader } from "@/components/ui/card";
import { SelectInput, TextInput } from "@/components/ui/input";
import { useCategories } from "@/hooks/use-dashboard-data";
import { apiClient } from "@/lib/api-client";

export function QuickAddForm() {
  const queryClient = useQueryClient();
  const categories = useCategories();
  const today = new Date().toISOString().slice(0, 10);
  const mutation = useMutation({
    mutationFn: apiClient.createTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-report"] });
    }
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(event.currentTarget);
    mutation.mutate(
      {
        type: form.get("type") as "income" | "expense",
        amount: String(form.get("amount")),
        category_id: String(form.get("category_id")),
        transaction_date: String(form.get("transaction_date")),
        note: String(form.get("note") ?? "")
      },
      { onSuccess: () => formElement.reset() }
    );
  }

  return (
    <Card>
      <CardHeader title="Quick add transaction" description="Dashboard entries use the same backend validation as Telegram." />
      <form className="grid gap-3 p-5 md:grid-cols-[120px_1fr_1fr_1fr_1.5fr_auto]" onSubmit={submit}>
        <SelectInput name="type" aria-label="Type">
          <option value="expense">Expense</option>
          <option value="income">Income</option>
        </SelectInput>
        <TextInput name="amount" placeholder="Amount" required />
        <SelectInput name="category_id" aria-label="Category" required>
          {categories.data?.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
        </SelectInput>
        <TextInput name="transaction_date" type="date" defaultValue={today} required />
        <TextInput name="note" placeholder="Note" />
        <Button type="submit" disabled={mutation.isPending}><Plus className="h-4 w-4" />Add</Button>
      </form>
      {mutation.isError ? <div className="border-t border-line px-5 py-3 text-sm text-danger">Saqlanmadi. Summani, kategoriyani va rolingiz ruxsatlarini tekshiring.</div> : null}
    </Card>
  );
}
