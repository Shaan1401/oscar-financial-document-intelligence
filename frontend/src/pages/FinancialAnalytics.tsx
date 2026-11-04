import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  PieChart as PieIcon,
  BarChart3,
  Calendar,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  LineChart,
  Line,
} from 'recharts';
import { api } from '../services/api';
import { SummaryMetrics, CategoryBreakdown, CashflowPoint } from '../types';

export const FinancialAnalytics: React.FC = () => {
  const [summary, setSummary] = useState<SummaryMetrics | null>(null);
  const [categories, setCategories] = useState<CategoryBreakdown[]>([]);
  const [cashflow, setCashflow] = useState<CashflowPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getAnalyticsSummary(),
      api.getCategoryAnalytics(),
      api.getCashflow(),
    ])
      .then(([sumData, catData, flowData]) => {
        setSummary(sumData);
        setCategories(catData);
        setCashflow(flowData);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
          Financial Analytics
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Portfolio spending trends, income versus expenditure, and category distributions.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Total Credits (Inflow)</span>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </div>
          <p className="mt-2 text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
            ₹ {(summary?.total_credits ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Total Debits (Outflow)</span>
            <TrendingDown className="h-4 w-4 text-rose-500" />
          </div>
          <p className="mt-2 text-2xl font-bold font-mono text-rose-600 dark:text-rose-400">
            ₹ {(summary?.total_debits ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Net Movement</span>
            <DollarSign className="h-4 w-4 text-brand-500" />
          </div>
          <p className={`mt-2 text-2xl font-bold font-mono ${
            (summary?.net_movement ?? 0) >= 0 ? 'text-emerald-600' : 'text-rose-600'
          }`}>
            ₹ {(summary?.net_movement ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
        </div>
      </div>

      {/* Cashflow Timeline Chart */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-1">
          Daily Cashflow Timeline (Inflow vs Outflow)
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
          Chronological distribution of credits and debits across all processed statements
        </p>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={cashflow} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#888888" />
              <YAxis tick={{ fontSize: 10 }} stroke="#888888" />
              <Tooltip
                formatter={(val: any) => [`₹ ${Number(val).toFixed(2)}`, '']}
                contentStyle={{ backgroundColor: '#1E293B', color: '#fff', borderRadius: '8px', border: 'none', fontSize: '11px' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
              <Bar dataKey="credits" fill="#10B981" name="Credits (Inflow)" radius={[3, 3, 0, 0]} />
              <Bar dataKey="debits" fill="#EF4444" name="Debits (Outflow)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Category Spend Distribution Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 overflow-hidden">
        <div className="border-b border-slate-200 px-4 py-3 dark:border-slate-800">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
            Category Spending Breakdown
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Total expenses and volume by classified category
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
              <tr>
                <th className="px-4 py-3 font-semibold">Category</th>
                <th className="px-4 py-3 font-semibold text-right">Transactions</th>
                <th className="px-4 py-3 font-semibold text-right">Total Debit (Expense)</th>
                <th className="px-4 py-3 font-semibold text-right">Total Credit (Income)</th>
                <th className="px-4 py-3 font-semibold text-right">Share of Expense</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {categories.map((c) => (
                <tr key={c.category} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                  <td className="px-4 py-3 font-medium text-slate-900 dark:text-white">
                    {c.category}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-slate-600 dark:text-slate-300">
                    {c.count}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-rose-600">
                    {c.total_debit > 0 ? `₹ ${c.total_debit.toFixed(2)}` : '-'}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-emerald-600">
                    {c.total_credit > 0 ? `₹ ${c.total_credit.toFixed(2)}` : '-'}
                  </td>
                  <td className="px-4 py-3 text-right font-mono font-medium text-slate-700 dark:text-slate-300">
                    {c.percentage_of_expense}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

