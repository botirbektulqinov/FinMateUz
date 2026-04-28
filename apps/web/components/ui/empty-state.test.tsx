import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmptyState } from "@/components/ui/empty-state";

describe("EmptyState", () => {
  it("renders helpful Uzbek copy", () => {
    render(
      <EmptyState
        title="Hali transaction yo‘q"
        description="Birinchi kirim yoki chiqimni qo‘shing — keyin bu yerda cash flow ko‘rinadi."
      />
    );

    expect(screen.getByText("Hali transaction yo‘q")).toBeInTheDocument();
    expect(screen.getByText(/Birinchi kirim/)).toBeInTheDocument();
  });
});
