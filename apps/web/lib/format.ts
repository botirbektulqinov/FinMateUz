export function formatMoney(value: string | number, currency = "UZS") {
  const amount = Number(value);
  const formatted = new Intl.NumberFormat("uz-UZ", { maximumFractionDigits: 0 })
    .format(Number.isFinite(amount) ? amount : 0)
    .replace(/\u00a0/g, " ");
  return currency === "UZS" ? `${formatted} so‘m` : `${formatted} ${currency}`;
}

export function formatPercent(value?: string | null) {
  if (value === null || value === undefined) return "New";
  const number = Number(value);
  return `${number > 0 ? "+" : ""}${number.toFixed(1)}%`;
}
