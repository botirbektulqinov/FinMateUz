"use client";

import { Edit3, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader } from "@/components/ui/card";
import type { Category, TransactionType } from "@/lib/types";

const swatches = ["#15803d", "#0f766e", "#2563eb", "#b91c1c", "#d97706", "#475569"];

export function CategoryBoard({ title, type, categories }: { title: string; type: TransactionType; categories: Category[] }) {
  return (
    <Card>
      <CardHeader
        title={title}
        description={type === "income" ? "Money entering the business." : "Money leaving the business."}
        action={<Button tone="secondary"><Plus className="h-4 w-4" />Create</Button>}
      />
      <div className="divide-y divide-line">
        {categories.map((category) => (
          <div key={category.id} className="flex items-center justify-between gap-3 px-5 py-3">
            <div className="flex min-w-0 items-center gap-3">
              <span className="h-3 w-3 rounded-full" style={{ background: category.color ?? "#172033" }} />
              <div className="min-w-0">
                <div className="truncate font-medium text-ink">{category.name}</div>
                <div className="text-xs text-muted">{category.is_default ? "Default" : "Custom"}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="hidden gap-1 sm:flex">
                {swatches.slice(0, 4).map((color) => <span key={color} className="h-4 w-4 rounded-full border border-white shadow" style={{ background: color }} />)}
              </div>
              <Button tone="ghost" className="h-8 w-8 p-0" aria-label="Edit"><Edit3 className="h-4 w-4" /></Button>
              <Button tone="ghost" className="h-8 w-8 p-0 text-danger" aria-label="Delete"><Trash2 className="h-4 w-4" /></Button>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
