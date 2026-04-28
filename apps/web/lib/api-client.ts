import type { Category, Company, DashboardReport, TelegramLinkCode, TokenPair, Transaction, TransactionList, User } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
const ACCESS_TOKEN_KEY = "finmate_access_token";
const REFRESH_TOKEN_KEY = "finmate_refresh_token";
const COMPANY_ID_KEY = "finmate_company_id";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function browserStorage() {
  return typeof window === "undefined" ? null : window.localStorage;
}

export const authStorage = {
  getAccessToken() {
    return browserStorage()?.getItem(ACCESS_TOKEN_KEY) ?? null;
  },
  getRefreshToken() {
    return browserStorage()?.getItem(REFRESH_TOKEN_KEY) ?? null;
  },
  isAuthenticated() {
    return Boolean(browserStorage()?.getItem(ACCESS_TOKEN_KEY));
  },
  getCompanyId() {
    return browserStorage()?.getItem(COMPANY_ID_KEY) ?? null;
  },
  setTokens(tokens: TokenPair) {
    const storage = browserStorage();
    storage?.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    storage?.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  },
  setCompanyId(companyId: string) {
    browserStorage()?.setItem(COMPANY_ID_KEY, companyId);
  },
  clear() {
    const storage = browserStorage();
    storage?.removeItem(ACCESS_TOKEN_KEY);
    storage?.removeItem(REFRESH_TOKEN_KEY);
    storage?.removeItem(COMPANY_ID_KEY);
  }
};

function requestHeaders(json = true): HeadersInit {
  const headers: Record<string, string> = {};
  if (json) headers["Content-Type"] = "application/json";
  const token = authStorage.getAccessToken();
  const companyId = authStorage.getCompanyId();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (companyId) headers["X-Company-Id"] = companyId;
  return headers;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { ...requestHeaders(options.body !== undefined), ...options.headers },
    cache: "no-store"
  });
  if (!response.ok) {
    let message = "Request failed";
    try {
      const body = (await response.json()) as { detail?: string };
      message = body.detail ?? message;
    } catch {
      message = response.statusText || message;
    }
    throw new ApiError(response.status, message);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const apiClient = {
  login(payload: { email: string; password: string }) {
    return request<TokenPair>("/auth/login", { method: "POST", body: JSON.stringify(payload) });
  },
  register(payload: { email: string; full_name: string; password: string; company_name: string; business_type?: string }) {
    return request<TokenPair>("/auth/register", { method: "POST", body: JSON.stringify(payload) });
  },
  me() {
    return request<User>("/auth/me");
  },
  currentCompany() {
    return request<Company>("/companies/current");
  },
  companies() {
    return request<Company[]>("/companies/me");
  },
  report() {
    return request<DashboardReport>("/reports/dashboard");
  },
  categories(type?: "income" | "expense") {
    const query = type ? `?type=${type}` : "";
    return request<Category[]>(`/categories${query}`);
  },
  transactions(params?: Record<string, string>) {
    const query = params ? `?${new URLSearchParams(params).toString()}` : "";
    return request<TransactionList>(`/transactions${query}`);
  },
  telegramLinkCode() {
    return request<TelegramLinkCode>("/bot/link-code");
  },
  createTransaction(payload: Partial<Transaction> & { amount: string; category_id: string; transaction_date: string; type: "income" | "expense" }) {
    return request<Transaction>("/transactions", { method: "POST", body: JSON.stringify({ ...payload, source: "dashboard" }) });
  },
  updateTransaction(id: string, payload: Partial<Transaction>) {
    return request<Transaction>(`/transactions/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
  },
  deleteTransaction(id: string) {
    return request<void>(`/transactions/${id}`, { method: "DELETE" });
  },
  approveTransaction(id: string) {
    return request<Transaction>(`/transactions/${id}/approve`, { method: "POST" });
  },
  rejectTransaction(id: string) {
    return request<Transaction>(`/transactions/${id}/reject`, { method: "POST" });
  },
  createCategory(payload: Pick<Category, "name" | "type" | "color" | "icon">) {
    return request<Category>("/categories", { method: "POST", body: JSON.stringify(payload) });
  },
  updateCategory(id: string, payload: Partial<Category>) {
    return request<Category>(`/categories/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
  },
  deleteCategory(id: string) {
    return request<void>(`/categories/${id}`, { method: "DELETE" });
  }
};
