import { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonTone = "primary" | "secondary" | "danger" | "ghost";

const tones: Record<ButtonTone, string> = {
  primary: "bg-ink text-white hover:bg-[#243049]",
  secondary: "border border-line bg-white text-ink hover:bg-canvas",
  danger: "border border-red-200 bg-red-50 text-danger hover:bg-red-100",
  ghost: "text-muted hover:bg-canvas hover:text-ink"
};

export function Button({
  children,
  tone = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { tone?: ButtonTone; children: ReactNode }) {
  return (
    <button
      className={`focus-ring inline-flex items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-semibold transition ${tones[tone]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
