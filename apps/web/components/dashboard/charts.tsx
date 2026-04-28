"use client";

import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { CategoryBreakdownPoint, TimeSeriesPoint } from "@/lib/types";

export function IncomeExpenseChart({ data }: { data: TimeSeriesPoint[] }) {
  const rows = data.map((item) => ({ ...item, income: Number(item.income), expense: Number(item.expense) }));
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <BarChart data={rows}>
          <CartesianGrid stroke="#e6eaf0" vertical={false} />
          <XAxis dataKey="period" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} tickFormatter={(value) => `${Math.round(Number(value) / 1000000)}m`} />
          <Tooltip formatter={(value) => Number(value).toLocaleString("uz-UZ")} />
          <Legend />
          <Bar dataKey="income" fill="#15803d" radius={[4, 4, 0, 0]} />
          <Bar dataKey="expense" fill="#b42318" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function CashFlowTrend({ data }: { data: TimeSeriesPoint[] }) {
  const rows = data.map((item) => ({ ...item, net: Number(item.net) }));
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <LineChart data={rows}>
          <CartesianGrid stroke="#e6eaf0" vertical={false} />
          <XAxis dataKey="period" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} tickFormatter={(value) => `${Math.round(Number(value) / 1000000)}m`} />
          <Tooltip formatter={(value) => Number(value).toLocaleString("uz-UZ")} />
          <Line type="monotone" dataKey="net" stroke="#172033" strokeWidth={3} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function BreakdownChart({ data }: { data: CategoryBreakdownPoint[] }) {
  const rows = data.map((item) => ({ name: item.category_name, value: Number(item.total) }));
  const colors = ["#172033", "#15803d", "#b42318", "#0f766e", "#b7791f", "#475569"];
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <PieChart>
          <Pie data={rows} dataKey="value" nameKey="name" innerRadius={54} outerRadius={92} paddingAngle={3}>
            {rows.map((_, index) => (
              <Cell key={index} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => Number(value).toLocaleString("uz-UZ")} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
