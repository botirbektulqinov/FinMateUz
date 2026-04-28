import { describe, expect, it } from "vitest";
import { formatMoney, formatPercent } from "@/lib/format";

describe("format helpers", () => {
  it("formats UZS amounts for Uzbek business users", () => {
    expect(formatMoney("1250000")).toBe("1 250 000 so‘m");
  });

  it("marks positive percentage changes clearly", () => {
    expect(formatPercent("12.86")).toBe("+12.9%");
    expect(formatPercent(null)).toBe("New");
  });
});
