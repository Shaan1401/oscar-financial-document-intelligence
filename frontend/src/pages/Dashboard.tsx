import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  TrendingUp,
  TrendingDown,
  Scale,
  AlertCircle,
  UploadCloud,
  CheckCircle2,
  ArrowRight,
  ShieldAlert,
  Layers,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
  Legend,
} from 'recharts';
import { api } from '../services/api';
import { SummaryMetrics, Statement, CategoryBreakdown, MethodDistribution } from '../types';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EC4899', '#8B5CF6', '#06B6D4', '#64748B'];

export const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<SummaryMetrics | null>(null);
  const [statements, setStatements] = useState<Statement[]>([]);
  const [categories, setCategories] = useState<CategoryBreakdown[]>([]);
  const [distribution, setDistribution] = useState<MethodDistribution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getAnalyticsSummary(),
      api.getStatements(),
      api.getCategoryAnalytics(),
      api.getDistribution(),
    ])
      .then(([sumData, stmtData, catData, distData]) => {
        setSummary(sumData);
        setStatements(stmtData);
        setCategories(catData.slice(0, 6));
        setDistribution(distData);
      })
      .catch((err) => console.error('Dashboard load failed:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
      </div>
    );
  }

  const hasData = (summary?.total_statements ?? 0) > 0;

  return (
    <div className="space-y-6">
      {/* Header & Subtitle */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Operational Statement Intelligence
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Non-LLM document extraction, explainable classification, and mathematical reconciliation.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            to="/upload"
            className="inline-flex items-center space-x-2 rounded-lg bg-brand-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-brand-700 transition"
          >
            <UploadCloud className="h-4 w-4" />
            <span>Process New Statement</span>
          </Link>
        </div>
      </div>

      {!hasData ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center dark:border-slate-800 dark:bg-slate-900">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-50 text-brand-600 dark:bg-brand-950 dark:text-brand-400">
            <UploadCloud className="h-8 w-8" />
          </div>
          <h3 className="mt-4 text-base font-semibold text-slate-900 dark:text-white">
            No bank statements processed yet
          </h3>
          <p className="mt-1 max-w-sm text-xs text-slate-500 dark:text-slate-400">
            Upload a text-based, scanned, or multi-page bank statement PDF to extract transactions, classify expenses, and verify reconciliation.
          </p>
          <Link
            to="/upload"
            className="mt-6 inline-flex items-center space-x-2 rounded-lg bg-brand-600 px-4 py-2 text-xs font-semibold text-white shadow hover:bg-brand-700"
          >
            <UploadCloud className="h-4 w-4" />
            <span>Upload Demo Statement</span>
          </Link>
        </div>
      ) : (
        <>
          {/* KPI Summary Cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Total Statements</span>
                <span className="rounded-lg bg-blue-50 p-2 text-brand-600 dark:bg-blue-950/60 dark:text-brand-400">
                  <FileText className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline space-x-2">
                <span className="text-2xl font-bold text-slate-900 dark:text-white">
                  {summary?.total_statements}
                </span>
                <span className="text-xs text-slate-500">({summary?.total_transactions} txns)</span>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Total Credits (Inflow)</span>
                <span className="rounded-lg bg-emerald-50 p-2 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400">
                  <TrendingUp className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3">
                <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                  ₹ {summary?.total_credits.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Total Debits (Outflow)</span>
                <span className="rounded-lg bg-rose-50 p-2 text-rose-600 dark:bg-rose-950/60 dark:text-rose-400">
                  <TrendingDown className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3">
                <span className="text-2xl font-bold text-rose-600 dark:text-rose-400">
                  ₹ {summary?.total_debits.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Reconciled / Exceptions</span>
                <span className="rounded-lg bg-purple-50 p-2 text-purple-600 dark:bg-purple-950/60 dark:text-purple-400">
                  <Scale className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline justify-between">
                <span className="text-2xl font-bold text-slate-900 dark:text-white">
                  {summary?.reconciled_statements} / {summary?.total_statements}
                </span>
                <Link
                  to="/reviews"
                  className="inline-flex items-center space-x-1 text-xs font-medium text-amber-600 hover:underline dark:text-amber-400"
                >
                  <AlertCircle className="h-3.5 w-3.5" />
                  <span>{summary?.pending_reviews} review pending</span>
                </Link>
              </div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Top Categories Chart */}
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 lg:col-span-2">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                    Top Expenditure Categories
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Calculated from actual extracted transactions
                  </p>
                </div>
                <Link to="/analytics" className="text-xs font-medium text-brand-600 hover:underline dark:text-brand-400">
                  View Full Analytics →
                </Link>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={categories} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                    <XAxis
                      dataKey="category"
                      angle={-20}
                      textAnchor="end"
                      interval={0}
                      tick={{ fontSize: 10 }}
                      stroke="#888888"
                    />
                    <YAxis tick={{ fontSize: 10 }} stroke="#888888" />
                    <Tooltip
                      formatter={(value: any) => [`₹ ${Number(value).toFixed(2)}`, 'Expense']}
                      contentStyle={{ backgroundColor: '#1E293B', color: '#fff', borderRadius: '8px', border: 'none', fontSize: '11px' }}
                    />
                    <Bar dataKey="total_debit" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Classification Method Breakdown */}
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                    Classification Engine
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Strictly Non-LLM</p>
                </div>
                <Link to="/classification" className="text-xs font-medium text-brand-600 hover:underline dark:text-brand-400">
                  Metrics →
                </Link>
              </div>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={distribution}
                      dataKey="count"
                      nameKey="method"
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={70}
                      paddingAngle={4}
                    >
                      {distribution.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1E293B', color: '#fff', borderRadius: '8px', border: 'none', fontSize: '11px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-2 space-y-1.5 text-xs">
                {distribution.map((d, idx) => (
                  <div key={d.method} className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                    <div className="flex items-center space-x-2">
                      <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                      <span className="font-medium text-slate-700 dark:text-slate-300">{d.method}</span>
                    </div>
                    <span className="font-semibold">{d.count} ({d.percentage}%)</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Statements Table */}
          <div className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center justify-between border-b border-slate-200 p-4 dark:border-slate-800">
              <div>
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Recent Statements</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Uploaded documents, layout profiling, and reconciliation status
                </p>
              </div>
              <Link to="/statements" className="text-xs font-medium text-brand-600 hover:underline dark:text-brand-400">
                View All Statements →
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Document / Bank</th>
                    <th className="px-4 py-3 font-semibold">Type & Layout</th>
                    <th className="px-4 py-3 font-semibold">Transactions</th>
                    <th className="px-4 py-3 font-semibold">Debits / Credits</th>
                    <th className="px-4 py-3 font-semibold">Reconciliation</th>
                    <th className="px-4 py-3 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                  {statements.slice(0, 5).map((stmt) => (
                    <tr key={stmt.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                      <td className="px-4 py-3">
                        <Link to={`/statements/${stmt.id}`} className="font-semibold text-brand-600 hover:underline dark:text-brand-400">
                          {stmt.filename}
                        </Link>
                        <p className="text-[11px] text-slate-500">{stmt.bank_name || 'Generic Bank'}</p>
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center rounded bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                          {stmt.pdf_type.toUpperCase()} • {stmt.layout_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-mono font-medium">
                        {stmt.transaction_count ?? '-'}
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-rose-600 font-mono">
                          - ₹ {(stmt.total_debits ?? 0).toFixed(2)}
                        </div>
                        <div className="text-emerald-600 font-mono">
                          + ₹ {(stmt.total_credits ?? 0).toFixed(2)}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center space-x-1 rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                            stmt.reconciliation_status === 'RECONCILED'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300'
                              : stmt.reconciliation_status === 'MISMATCH'
                              ? 'bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300'
                              : 'bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300'
                          }`}
                        >
                          {stmt.reconciliation_status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Link
                          to={`/statements/${stmt.id}`}
                          className="inline-flex items-center space-x-1 rounded bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                        >
                          <span>Evidence</span>
                          <ArrowRight className="h-3 w-3" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

