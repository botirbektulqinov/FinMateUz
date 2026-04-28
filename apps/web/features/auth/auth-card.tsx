"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { LockKeyhole, Mail } from "lucide-react";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Field, SelectInput, TextInput } from "@/components/ui/input";
import { apiClient, authStorage } from "@/lib/api-client";
import type { TokenPair } from "@/lib/types";
import { BrandLogo } from "@/components/ui/brand-logo";

const businessTypes = ["Store", "Education center", "Service business", "Clinic", "Agency", "Other"];

export function LoginForm() {
  const router = useRouter();
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const tokens = await apiClient.login({ email: String(form.get("email")), password: String(form.get("password")) });
      await finishAuth(tokens);
      router.push("/dashboard/overview");
    } catch {
      setError("Email yoki parol noto‘g‘ri. Qayta urinib ko‘ring.");
    }
  }

  return (
    <AuthPanel title="Welcome back" description="Sign in with your FinMate UZ workspace account.">
      <form className="space-y-4" onSubmit={submit}>
        <Field label="Email">
          <IconInput icon={<Mail className="h-4 w-4 text-muted" />}>
            <input name="email" className="w-full py-2 text-sm outline-none" type="email" placeholder="owner@company.uz" required />
          </IconInput>
        </Field>
        <Field label="Password">
          <IconInput icon={<LockKeyhole className="h-4 w-4 text-muted" />}>
            <input name="password" className="w-full py-2 text-sm outline-none" type="password" placeholder="Your password" required />
          </IconInput>
        </Field>
        {error ? <p className="text-sm text-danger">{error}</p> : null}
        <Button className="w-full" type="submit">Sign in</Button>
      </form>
      <Link href="/register" className="mt-4 block text-sm font-medium text-ink">Create a company account</Link>
    </AuthPanel>
  );
}

export function RegisterForm() {
  const router = useRouter();
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const tokens = await apiClient.register({
        email: String(form.get("email")),
        full_name: String(form.get("full_name")),
        password: String(form.get("password")),
        company_name: String(form.get("company_name")),
        business_type: String(form.get("business_type"))
      });
      await finishAuth(tokens);
      router.push("/onboarding");
    } catch {
      setError("Ro‘yxatdan o‘tishda xatolik bo‘ldi. Ma’lumotlarni tekshiring.");
    }
  }

  return (
    <AuthPanel title="Create FinMate workspace" description="Company setup starts with a secure owner account.">
      <form className="space-y-4" onSubmit={submit}>
        <Field label="Full name"><TextInput name="full_name" placeholder="Business owner" required /></Field>
        <Field label="Email"><TextInput name="email" type="email" placeholder="owner@company.uz" required /></Field>
        <Field label="Password"><TextInput name="password" type="password" minLength={8} placeholder="At least 8 characters" required /></Field>
        <Field label="Company name"><TextInput name="company_name" placeholder="Company name" required /></Field>
        <Field label="Business type">
          <SelectInput name="business_type">
            {businessTypes.map((type) => <option key={type}>{type}</option>)}
          </SelectInput>
        </Field>
        {error ? <p className="text-sm text-danger">{error}</p> : null}
        <Button className="w-full" type="submit">Create workspace</Button>
      </form>
      <Link href="/login" className="mt-4 block text-sm font-medium text-ink">I already have an account</Link>
    </AuthPanel>
  );
}

async function finishAuth(tokens: TokenPair) {
  authStorage.setTokens(tokens);
  const companies = await apiClient.companies();
  if (companies[0]) {
    authStorage.setCompanyId(companies[0].id);
  }
}

function AuthPanel({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <section className="w-full max-w-md rounded-md border border-line bg-panel p-6 shadow-soft">
      <BrandLogo size="lg" showWordmark />
      <h1 className="mt-5 text-2xl font-semibold text-ink">{title}</h1>
      <p className="mt-2 text-sm text-muted">{description}</p>
      <div className="mt-6">{children}</div>
    </section>
  );
}

function IconInput({ icon, children }: { icon: React.ReactNode; children: React.ReactNode }) {
  return <div className="flex items-center gap-2 rounded-md border border-line px-3">{icon}{children}</div>;
}
