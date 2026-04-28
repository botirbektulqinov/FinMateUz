export type Role = "owner" | "manager" | "accountant" | "operator" | "viewer";
export type TransactionType = "income" | "expense";
export type TransactionSource = "telegram" | "dashboard";
export type TransactionStatus = "pending" | "confirmed" | "rejected" | "deleted";

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
};

export type TelegramLinkCode = {
  link_code: string;
  command: string;
  expires_in_minutes: number;
};

export type User = {
  id: string;
  email: string;
  full_name: string;
};

export type Company = {
  id: string;
  name: string;
  business_type: string | null;
  default_currency: string;
  role?: Role | null;
};

export type Category = {
  id: string;
  company_id?: string;
  name: string;
  type: TransactionType;
  color?: string | null;
  icon?: string | null;
  is_default: boolean;
};

export type Transaction = {
  id: string;
  company_id?: string;
  created_by_user_id?: string;
  type: TransactionType;
  amount: string;
  currency: string;
  category_id: string;
  category_name?: string | null;
  transaction_date: string;
  note?: string | null;
  source: TransactionSource;
  raw_text?: string | null;
  confidence_score?: string | null;
  status: TransactionStatus;
  created_at: string;
  updated_at?: string;
  deleted_at?: string | null;
};

export type TransactionList = {
  items: Transaction[];
  total: number;
};

export type ReportSummary = {
  month_income: string;
  month_expenses: string;
  net_cash_flow: string;
  previous_month_income: string;
  previous_month_expenses: string;
  income_change_percent?: string | null;
  expense_change_percent?: string | null;
  pending_approval_count: number;
};

export type TimeSeriesPoint = {
  period: string;
  income: string;
  expense: string;
  net: string;
};

export type CategoryBreakdownPoint = {
  category_id: string;
  category_name: string;
  total: string;
};

export type DashboardReport = {
  summary: ReportSummary;
  income_vs_expenses: TimeSeriesPoint[];
  expense_breakdown: CategoryBreakdownPoint[];
  income_breakdown: CategoryBreakdownPoint[];
  top_expense_categories: CategoryBreakdownPoint[];
  top_income_categories: CategoryBreakdownPoint[];
  recent_transactions: Transaction[];
};
