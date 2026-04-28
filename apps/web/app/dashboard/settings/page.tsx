"use client";

import { Bot, Copy, LogOut, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Card, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Field, TextInput } from "@/components/ui/input";
import { apiClient, authStorage } from "@/lib/api-client";
import { BrandLogo } from "@/components/ui/brand-logo";

export default function SettingsPage() {
  const router = useRouter();
  const company = useQuery({ queryKey: ["company-current"], queryFn: apiClient.currentCompany });
  const user = useQuery({ queryKey: ["me"], queryFn: apiClient.me });
  const linkCode = useQuery({ queryKey: ["telegram-link-code"], queryFn: apiClient.telegramLinkCode, retry: false });

  function logout() {
    authStorage.clear();
    router.replace("/login");
  }

  async function copyLinkCommand() {
    if (linkCode.data?.command) {
      await navigator.clipboard?.writeText(linkCode.data.command);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Settings</h1>
        <p className="mt-1 text-sm text-muted">Company profile, Telegram connection, currency, and role context.</p>
      </div>
      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader title="Company profile" description="Owner and manager roles can update this from the backend." />
          <div className="grid gap-4 p-5 md:grid-cols-2">
            <Field label="Company name"><TextInput defaultValue={company.data?.name ?? ""} /></Field>
            <Field label="Business type"><TextInput defaultValue={company.data?.business_type ?? "Store"} /></Field>
            <Field label="Currency default"><TextInput value="UZS" readOnly /></Field>
            <Field label="Role"><TextInput value={company.data?.role ?? "owner"} readOnly /></Field>
          </div>
        </Card>
        <Card>
          <CardHeader title="Telegram connection" description="Operators can submit pending transactions from Telegram." />
          <div className="space-y-4 p-5 text-sm text-muted">
            <div className="flex items-center gap-3 text-ink"><Bot className="h-5 w-5" />@FinMateUzBot ulash tayyor</div>
            <p>Quyidagi commandni botga yuboring. Kod {linkCode.data?.expires_in_minutes ?? 15} daqiqa amal qiladi.</p>
            <div className="rounded-md border border-line bg-canvas p-3 font-mono text-xs text-ink break-all">
              {linkCode.isLoading ? "Kod tayyorlanmoqda..." : linkCode.data?.command ?? "Kod olinmadi. Qayta yuklab ko‘ring."}
            </div>
            <Button type="button" tone="secondary" onClick={copyLinkCommand}>
              <Copy className="h-4 w-4" />
              Copy link command
            </Button>
          </div>
        </Card>
        <Card>
          <CardHeader title="Current user" />
          <div className="space-y-3 p-5 text-sm">
            <div className="flex items-center gap-3 text-ink"><BrandLogo size="sm" />{user.data?.full_name ?? "User"}</div>
            <div className="text-muted">{user.data?.email ?? "No email loaded"}</div>
            <Button type="button" tone="danger" onClick={logout}>
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </Card>
        <Card>
          <CardHeader title="Security posture" />
          <div className="space-y-3 p-5 text-sm text-muted">
            <div className="flex items-center gap-3 text-ink"><ShieldCheck className="h-5 w-5" />Company-scoped access</div>
            <p>All finance API calls use the selected company id and backend RBAC. Viewers cannot modify records.</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
