import { InputHTMLAttributes, SelectHTMLAttributes } from "react";

export function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-ink">{label}</span>
      <div className="mt-1">{children}</div>
    </label>
  );
}

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input className="focus-ring w-full rounded-md border border-line bg-white px-3 py-2 text-sm text-ink placeholder:text-muted" {...props} />;
}

export function SelectInput(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className="focus-ring w-full rounded-md border border-line bg-white px-3 py-2 text-sm text-ink" {...props} />;
}
