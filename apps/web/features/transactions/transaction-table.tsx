"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, Pencil, Trash2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { SourceBadge, StatusBadge } from "@/components/ui/status-badge";
import { apiClient } from "@/lib/api-client";
import { formatMoney } from "@/lib/format";
import type { Transaction } from "@/lib/types";

export function TransactionTable({ transactions }: { transactions: Transaction[] }) {
  const queryClient = useQueryClient();
  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["transactions"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard-report"] });
  };
  const approve = useMutation({ mutationFn: apiClient.approveTransaction, onSuccess: refresh });
  const reject = useMutation({ mutationFn: apiClient.rejectTransaction, onSuccess: refresh });
  const remove = useMutation({ mutationFn: apiClient.deleteTransaction, onSuccess: refresh });
  const busy = approve.isPending || reject.isPending || remove.isPending;

  if (!transactions.length) {
    return (
      <EmptyState
        title="Hali transaction yo‘q"
        description="Birinchi kirim yoki chiqimni qo‘shing — keyin bu yerda cash flow ko‘rinadi."
      />
    );
  }

  return (
    <div className="overflow-x-auto rounded-md border border-line bg-panel shadow-soft">
      <table className="w-full min-w-[920px] text-left text-sm">
        <thead className="bg-canvas text-xs uppercase text-muted">
          <tr>
            <th className="px-4 py-3">Date</th>
            <th className="px-4 py-3">Category</th>
            <th className="px-4 py-3">Note</th>
            <th className="px-4 py-3">Source</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3 text-right">Amount</th>
            <th className="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {transactions.map((tx) => (
            <tr key={tx.id}>
              <td className="px-4 py-3 text-muted">{tx.transaction_date}</td>
              <td className="px-4 py-3 font-medium text-ink">{tx.category_name ?? "Uncategorized"}</td>
              <td className="px-4 py-3 text-muted">{tx.note ?? "-"}</td>
              <td className="px-4 py-3"><SourceBadge source={tx.source} /></td>
              <td className="px-4 py-3"><StatusBadge status={tx.status} /></td>
              <td className={`px-4 py-3 text-right font-semibold ${tx.type === "income" ? "text-success" : "text-danger"}`}>
                {tx.type === "income" ? "+" : "-"}{formatMoney(tx.amount, tx.currency)}
              </td>
              <td className="px-4 py-3">
                <div className="flex justify-end gap-2">
                  {tx.status === "pending" ? (
                    <>
                      <Button tone="secondary" className="h-8 w-8 p-0" aria-label="Approve" disabled={busy} onClick={() => approve.mutate(tx.id)}><Check className="h-4 w-4" /></Button>
                      <Button tone="danger" className="h-8 w-8 p-0" aria-label="Reject" disabled={busy} onClick={() => reject.mutate(tx.id)}><X className="h-4 w-4" /></Button>
                    </>
                  ) : null}
                  <Button tone="secondary" className="h-8 w-8 p-0" aria-label="Edit"><Pencil className="h-4 w-4" /></Button>
                  <Button tone="danger" className="h-8 w-8 p-0" aria-label="Delete" disabled={busy} onClick={() => remove.mutate(tx.id)}><Trash2 className="h-4 w-4" /></Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
