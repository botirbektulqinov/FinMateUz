import Link from "next/link";
import { Bot, Building2, CheckCircle2, ReceiptText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const businessTypes = ["Store", "Education center", "Service business", "Clinic", "Agency", "Other"];

const steps = [
  { title: "Company setup", text: "Company name, owner role, and UZS default currency.", icon: Building2 },
  { title: "Default categories", text: "Uzbek SMB kirim/chiqim categories are created automatically.", icon: ReceiptText },
  { title: "Telegram bot", text: "Connect team members so operators can log transactions from chat.", icon: Bot },
  { title: "First transaction", text: "Add one transaction to activate useful cash-flow reports.", icon: CheckCircle2 }
];

export default function OnboardingPage() {
  return (
    <main className="min-h-screen bg-canvas px-4 py-10">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 max-w-3xl">
          <div className="text-sm font-semibold text-success">FinMate UZ onboarding</div>
          <h1 className="mt-2 text-3xl font-semibold text-ink">Set up a reliable finance workspace</h1>
          <p className="mt-3 text-muted">Yangi kompaniya uchun category, Telegram bot va birinchi transaction oqimini bir joyda tayyorlang.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          {steps.map((step) => {
            const Icon = step.icon;
            return (
              <Card key={step.title} className="p-5">
                <Icon className="h-5 w-5 text-ink" />
                <h2 className="mt-4 font-semibold text-ink">{step.title}</h2>
                <p className="mt-2 text-sm leading-6 text-muted">{step.text}</p>
              </Card>
            );
          })}
        </div>
        <Card className="mt-6 p-6">
          <div className="grid gap-4 md:grid-cols-[1fr_1fr_auto]">
            <input className="focus-ring rounded-md border border-line px-3 py-2 text-sm" placeholder="Company name" />
            <select className="focus-ring rounded-md border border-line bg-white px-3 py-2 text-sm">
              {businessTypes.map((type) => <option key={type}>{type}</option>)}
            </select>
            <Link href="/dashboard/overview">
              <Button className="w-full md:w-auto">Add first transaction</Button>
            </Link>
          </div>
          <div className="mt-5 rounded-md border border-line bg-canvas p-4 text-sm text-muted">
            Telegram ulash: @FinMateUzBot ni oching, dashboarddagi ulash kodini yuboring, keyin “bugun 250 ming logistika uchun ketdi” kabi yozing.
          </div>
        </Card>
      </div>
    </main>
  );
}
