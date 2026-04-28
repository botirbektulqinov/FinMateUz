"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export function useReport() {
  return useQuery({ queryKey: ["dashboard-report"], queryFn: apiClient.report });
}

export function useTransactions(params?: Record<string, string>) {
  return useQuery({ queryKey: ["transactions", params], queryFn: () => apiClient.transactions(params) });
}

export function useCategories(type?: "income" | "expense") {
  return useQuery({ queryKey: ["categories", type], queryFn: () => apiClient.categories(type) });
}
