"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BarChart3, Building2, FolderKanban, LayoutDashboard, LogOut, Menu, ReceiptText, Settings } from "lucide-react";
import { ReactNode, useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient, ApiError, authStorage } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { BrandLogo } from "@/components/ui/brand-logo";

const nav = [
  { href: "/dashboard/overview", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/transactions", label: "Transactions", icon: ReceiptText },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/categories", label: "Categories", icon: FolderKanban },
  { href: "/dashboard/settings", label: "Settings", icon: Settings }
];

export function DashboardShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [authReady, setAuthReady] = useState(false);
  const company = useQuery({ queryKey: ["company-current"], queryFn: apiClient.currentCompany, enabled: authReady, retry: false });
  const user = useQuery({ queryKey: ["me"], queryFn: apiClient.me, enabled: authReady, retry: false });

  useEffect(() => {
    let active = true;
    async function bootstrapAuth() {
      if (!authStorage.getAccessToken()) {
        router.replace("/login");
        return;
      }
      try {
        if (!authStorage.getCompanyId()) {
          const companies = await apiClient.companies();
          if (companies[0]) {
            authStorage.setCompanyId(companies[0].id);
          }
        }
        if (active) setAuthReady(true);
      } catch {
        authStorage.clear();
        router.replace("/login");
      }
    }
    void bootstrapAuth();
    return () => {
      active = false;
    };
  }, [router]);

  useEffect(() => {
    const error = user.error ?? company.error;
    if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
      authStorage.clear();
      router.replace("/login");
    }
  }, [company.error, router, user.error]);

  function logout() {
    authStorage.clear();
    router.replace("/login");
  }

  if (!authReady) {
    return (
      <main className="grid min-h-screen place-items-center bg-canvas px-4 text-sm text-muted">
        Session tekshirilmoqda...
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-canvas">
      <aside className={`fixed inset-y-0 left-0 z-30 w-72 border-r border-line bg-panel px-4 py-5 transition-transform lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
        <Link href="/dashboard/overview" className="flex items-center gap-3 rounded-md px-2 py-2">
          <BrandLogo size="md" />
          <div>
            <div className="font-semibold text-ink">FinMate UZ</div>
            <div className="text-xs text-muted">Cash flow nazorati</div>
          </div>
        </Link>
        <nav className="mt-8 space-y-1">
          {nav.map((item) => {
            const active = pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium ${active ? "bg-ink text-white" : "text-muted hover:bg-canvas hover:text-ink"}`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="absolute bottom-5 left-4 right-4 rounded-md border border-line bg-canvas p-3 text-sm">
          <div className="flex items-center gap-2 font-medium text-ink">
            <Building2 className="h-4 w-4" />
            Telegram bot
          </div>
          <div className="mt-1 text-muted">Settings orqali ulash kodi oling</div>
        </div>
      </aside>
      {open ? <button aria-label="Close menu" className="fixed inset-0 z-20 bg-black/20 lg:hidden" onClick={() => setOpen(false)} /> : null}
      <div className="lg:pl-72">
        <header className="sticky top-0 z-10 border-b border-line bg-panel/95 px-4 py-3 backdrop-blur md:px-8">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button className="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-line text-ink lg:hidden" onClick={() => setOpen(true)} aria-label="Open menu">
                <Menu className="h-4 w-4" />
              </button>
              <div>
                <div className="text-sm text-muted">{company.data?.name ?? "Workspace"}</div>
                <h1 className="text-xl font-semibold text-ink">Finance dashboard</h1>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <select className="focus-ring rounded-md border border-line bg-white px-3 py-2 text-sm text-ink" aria-label="Period">
                <option>This month</option>
                <option>Last month</option>
                <option>This quarter</option>
              </select>
              <div className="hidden items-center gap-2 rounded-md border border-line bg-white px-3 py-2 text-sm text-ink sm:flex">
                <BrandLogo size="sm" />
                <span>{user.data?.full_name ?? "User"}</span>
              </div>
              <Button type="button" tone="secondary" className="hidden gap-2 sm:inline-flex" onClick={logout}>
                <LogOut className="h-4 w-4" />
                Logout
              </Button>
            </div>
          </div>
        </header>
        <main className="px-4 py-6 md:px-8">{children}</main>
      </div>
    </div>
  );
}
