import { ReactNode } from "react";

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <div className="rounded-md border border-dashed border-line bg-panel px-6 py-10 text-center">
      <div className="mx-auto max-w-md">
        <h3 className="text-base font-semibold text-ink">{title}</h3>
        <p className="mt-2 text-sm leading-6 text-muted">{description}</p>
        {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
      </div>
    </div>
  );
}
