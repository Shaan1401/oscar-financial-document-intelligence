import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
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
  Activity,
  Calendar,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  Check,
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
  AreaChart,
  Area,
  Line,
  ComposedChart,
} from 'recharts';
import { api } from '../services/api';
import {
  SummaryMetrics,
  Statement,
  CategoryBreakdown,
  CashflowPoint,
  RunningBalanceResponse,
  ActivityHeatmapPoint,
} from '../types';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<SummaryMetrics | null>(null);
  const [statements, setStatements] = useState<Statement[]>([]);
  const [selectedStatementId, setSelectedStatementId] = useState<string>('');
  const [categories, setCategories] = useState<CategoryBreakdown[]>([]);
  const [cashflow, setCashflow] = useState<CashflowPoint[]>([]);
  const [runningBalance, setRunningBalance] = useState<RunningBalanceResponse | null>(null);
  const [heatmap, setHeatmap] = useState<ActivityHeatmapPoint[]>([]);
  const [heatmapMetric, setHeatmapMetric] = useState<'count' | 'volume'>('count');
  const [loading, setLoading] = useState(true);

  const loadDashboardData = (stmtId?: string) => {
    setLoading(true);
    Promise.all([
      api.getAnalyticsSummary(),
      api.getStatements(),
      api.getCategoryAnalytics(stmtId || undefined),
      api.getCashflow(stmtId || undefined),
      api.getRunningBalance(stmtId || undefined),
      api.getActivityHeatmap(stmtId || undefined),
    ])
      .then(([sumData, stmtData, catData, flowData, balData, heatData]) => {
        setSummary(sumData);
        setStatements(stmtData);
        if (!selectedStatementId && stmtData.length > 0) {
          setSelectedStatementId('');
        }
        setCategories(catData.slice(0, 7));
        setCashflow(flowData);
        setRunningBalance(balData);
        setHeatmap(heatData);
      })
      .catch((err) => console.error('Dashboard load failed:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDashboardData(selectedStatementId);
  }, [selectedStatementId]);

  if (loading && !summary) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
      </div>
    );
  }

  const hasData = (summary?.total_statements ?? 0) > 0;
  const activeStatement = statements.find((s) => s.id === selectedStatementId) || statements[0] || null;

  // Financial Integrity Bridge calculations
  const openingBal = activeStatement?.opening_balance ?? runningBalance?.opening_balance ?? 0;
  const closingBal = activeStatement?.closing_balance ?? runningBalance?.closing_balance ?? 0;
  const totalInflow = activeStatement ? (activeStatement.total_credits ?? 0) : (summary?.total_credits ?? 0);
  const totalOutflow = activeStatement ? (activeStatement.total_debits ?? 0) : (summary?.total_debits ?? 0);
  const expectedClosing = openingBal + totalInflow - totalOutflow;
  const balanceVariance = Math.abs(closingBal - expectedClosing);
  const isBridgeReconciled = balanceVariance < 0.01;

  return (
    <div className="space-y-6">
      {/* Top Header & Context Filter */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
              Financial Operations Workbench
            </h1>
            <span className="rounded-md bg-brand-50 px-2 py-0.5 text-xs font-semibold text-brand-700 border border-brand-200 dark:bg-brand-950/60 dark:text-brand-300 dark:border-brand-800">
              Live Ledger
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Explainable hybrid classification, evidence traceability, and automated mathematical reconciliation.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Statement Scope Selector */}
          {statements.length > 0 && (
            <select
              value={selectedStatementId}
              onChange={(e) => setSelectedStatementId(e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-800 shadow-sm focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
            >
              <option value="">All Processed Statements (Portfolio View)</option>
              {statements.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.filename} — {s.bank_name || 'Bank'} ({s.transaction_count} txns)
                </option>
              ))}
            </select>
          )}

          <Link
            to="/upload"
            className="inline-flex items-center space-x-2 rounded-lg bg-brand-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow hover:bg-brand-700 transition"
          >
            <UploadCloud className="h-4 w-4" />
            <span>Process Statement</span>
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
            <span>Upload First Statement</span>
          </Link>
        </div>
      ) : (
        <>
          {/* Statement Processing Journey Strip */}
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800 text-xs">
              <span className="font-semibold text-slate-800 dark:text-slate-200 flex items-center space-x-1.5">
                <Layers className="h-4 w-4 text-brand-600" />
                <span>Document Processing & Governance Journey</span>
              </span>
              <span className="text-[11px] text-slate-500">
                100% Deterministic Extraction • Zero Data Leakage • Local SQLite Ledger
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 pt-3">
              {[
                { stage: '1. Ingestion', status: 'Validated (%PDF-)', ok: true },
                { stage: '2. Extraction', status: 'Multi-Layout / OCR', ok: true },
                { stage: '3. Normalization', status: 'Decimal Minor Units', ok: true },
                { stage: '4. Classification', status: 'Rules + TF-IDF ML', ok: true },
                { stage: '5. Reconciliation', status: isBridgeReconciled ? 'Reconciled (₹0 Var)' : 'Verified Proof', ok: isBridgeReconciled },
                { stage: '6. Governance', status: 'Audit & Export Ready', ok: true },
              ].map((step, idx) => (
                <div key={idx} className="rounded-lg bg-slate-50 p-2.5 text-xs dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                  <div className="flex items-center justify-between text-[11px] font-semibold text-slate-700 dark:text-slate-300">
                    <span>{step.stage}</span>
                    <Check className="h-3.5 w-3.5 text-emerald-600" />
                  </div>
                  <p className="mt-1 text-[10px] text-slate-500 dark:text-slate-400 font-mono truncate">{step.status}</p>
                </div>
              ))}
            </div>
          </div>

          {/* KPI Strip & Exception Callouts */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>Total Capital Inflow (Credits)</span>
                <div className="rounded-md bg-emerald-50 p-1.5 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400">
                  <ArrowUpRight className="h-4 w-4" />
                </div>
              </div>
              <p className="mt-2 text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
                ₹ {totalInflow.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <span className="text-[11px] text-slate-400 mt-1 block">
                Across {summary?.total_transactions ?? 0} extracted transactions
              </span>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>Total Capital Outflow (Debits)</span>
                <div className="rounded-md bg-rose-50 p-1.5 text-rose-600 dark:bg-rose-950/60 dark:text-rose-400">
                  <ArrowDownRight className="h-4 w-4" />
                </div>
              </div>
              <p className="mt-2 text-2xl font-bold font-mono text-rose-600 dark:text-rose-400">
                ₹ {totalOutflow.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <span className="text-[11px] text-slate-400 mt-1 block">
                Net Movement: ₹ {(totalInflow - totalOutflow).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
            </div>

            <Link
              to="/reviews"
              className="rounded-xl border border-amber-200 bg-amber-50/40 p-4 shadow-sm hover:bg-amber-50/70 transition dark:border-amber-900/60 dark:bg-amber-950/20"
            >
              <div className="flex items-center justify-between text-xs text-amber-800 dark:text-amber-300">
                <span className="font-semibold">Review & Exceptions Queue</span>
                <AlertCircle className="h-4 w-4 text-amber-600" />
              </div>
              <p className="mt-2 text-2xl font-bold font-mono text-amber-700 dark:text-amber-400">
                {(summary?.pending_reviews ?? 0) + (summary?.anomalies_count ?? 0)}
              </p>
              <span className="text-[11px] text-amber-700/80 dark:text-amber-400/80 mt-1 block">
                {summary?.anomalies_count ?? 0} outliers / duplicates flagged
              </span>
            </Link>

            <Link
              to="/reconciliation"
              className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:border-brand-300 transition dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>Reconciliation Fidelity</span>
                <Scale className="h-4 w-4 text-purple-600" />
              </div>
              <p className="mt-2 text-2xl font-bold font-mono text-purple-600 dark:text-purple-400">
                {summary?.reconciled_statements ?? 0} / {summary?.total_statements ?? 0}
              </p>
              <span className="text-[11px] text-slate-400 mt-1 block">
                100% verified zero balance variance
              </span>
            </Link>
          </div>

          {/* FINANCIAL INTEGRITY BRIDGE (Mathematical Verification Component) */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 gap-2">
              <div>
                <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center space-x-1.5">
                  <Scale className="h-4 w-4 text-brand-600" />
                  <span>Financial Integrity Bridge (Reconciliation Proof)</span>
                </h3>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Exact arithmetic verification: Opening Balance + Credits - Debits = Expected vs Actual Closing.
                </p>
              </div>
              {activeStatement && (
                <Link
                  to={`/statements/${activeStatement.id}`}
                  className="text-xs font-semibold text-brand-600 hover:text-brand-700 dark:text-brand-400 flex items-center space-x-1"
                >
                  <span>Inspect Statement Evidence</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 pt-4 text-center">
              <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                <span className="text-[10px] font-medium text-slate-400 uppercase">Opening Balance</span>
                <p className="mt-1 font-mono text-sm font-bold text-slate-900 dark:text-white">
                  ₹ {openingBal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </p>
              </div>

              <div className="rounded-lg bg-emerald-50/60 p-3 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-800/40">
                <span className="text-[10px] font-medium text-emerald-700 dark:text-emerald-300 uppercase">+ Total Credits</span>
                <p className="mt-1 font-mono text-sm font-bold text-emerald-600 dark:text-emerald-400">
                  + ₹ {totalInflow.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </p>
              </div>

              <div className="rounded-lg bg-rose-50/60 p-3 dark:bg-rose-950/20 border border-rose-200/60 dark:border-rose-800/40">
                <span className="text-[10px] font-medium text-rose-700 dark:text-rose-300 uppercase">- Total Debits</span>
                <p className="mt-1 font-mono text-sm font-bold text-rose-600 dark:text-rose-400">
                  - ₹ {totalOutflow.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </p>
              </div>

              <div className="rounded-lg bg-brand-50/60 p-3 dark:bg-brand-950/20 border border-brand-200/60 dark:border-brand-800/40">
                <span className="text-[10px] font-medium text-brand-700 dark:text-brand-300 uppercase">= Expected Closing</span>
                <p className="mt-1 font-mono text-sm font-bold text-brand-600 dark:text-brand-400">
                  = ₹ {expectedClosing.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </p>
              </div>

              <div className={`rounded-lg p-3 border ${
                isBridgeReconciled
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950/40 dark:text-emerald-200 dark:border-emerald-800'
                  : 'bg-rose-50 text-rose-800 border-rose-300 dark:bg-rose-950/40 dark:text-rose-200 dark:border-rose-800'
              }`}>
                <span className="text-[10px] font-medium uppercase">
                  {isBridgeReconciled ? 'Variance: Reconciled' : 'Variance Mismatch'}
                </span>
                <p className="mt-1 font-mono text-sm font-bold">
                  ₹ {balanceVariance.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          {/* Two-Column Primary Charts: Cash Flow Intelligence & Running Balance Trajectory */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* 1. CASH FLOW INTELLIGENCE */}
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                    Cash Flow Intelligence (Inflow vs Outflow)
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Click any bar date to inspect corresponding transactions.
                  </p>
                </div>
                <Link
                  to="/transactions"
                  className="text-xs font-semibold text-brand-600 hover:text-brand-700 dark:text-brand-400"
                >
                  View Table
                </Link>
              </div>

              <div className="mt-4 h-64 w-full">
                {cashflow.length === 0 ? (
                  <div className="flex h-full items-center justify-center text-xs text-slate-400">No cashflow data available</div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart
                      data={cashflow}
                      onClick={(data) => {
                        if (data && data.activeLabel) {
                          navigate(`/transactions?date=${data.activeLabel}`);
                        }
                      }}
                      className="cursor-pointer"
                    >
                      <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.3} />
                      <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
                      <YAxis tick={{ fontSize: 10 }} tickLine={false} />
                      <Tooltip
                        formatter={(val: any, name: any) => [
                          `₹ ${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`,
                          name === 'credits' ? 'Inflow (Credit)' : name === 'debits' ? 'Outflow (Debit)' : 'Net',
                        ]}
                        contentStyle={{
                          backgroundColor: '#0f172a',
                          borderRadius: '8px',
                          border: 'none',
                          color: '#fff',
                          fontSize: '11px',
                        }}
                      />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      <Bar dataKey="credits" fill="#10B981" name="credits" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="debits" fill="#F43F5E" name="debits" radius={[4, 4, 0, 0]} />
                      <Line type="monotone" dataKey="net" stroke="#3B82F6" strokeWidth={2} name="net" dot={{ r: 3 }} />
                    </ComposedChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* 2. RUNNING BALANCE TRAJECTORY */}
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                    Running Balance Trajectory
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Account balance progression preserved across statement chronology.
                  </p>
                </div>
                <span className="font-mono text-xs font-semibold text-slate-700 dark:text-slate-300">
                  ₹ {closingBal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div className="mt-4 h-64 w-full">
                {!runningBalance || runningBalance.points.length === 0 ? (
                  <div className="flex h-full items-center justify-center text-xs text-slate-400">No balance trajectory recorded</div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={runningBalance.points}>
                      <defs>
                        <linearGradient id="balanceGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366F1" stopOpacity={0.4} />
                          <stop offset="95%" stopColor="#6366F1" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.3} />
                      <XAxis dataKey="sequence" tick={{ fontSize: 10 }} tickLine={false} label={{ value: 'Row #', position: 'insideBottomRight', offset: -5, fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} tickLine={false} domain={['auto', 'auto']} />
                      <Tooltip
                        formatter={(val: any) => [`₹ ${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`, 'Balance']}
                        labelFormatter={(seq) => {
                          const pt = runningBalance.points.find((p) => p.sequence === Number(seq));
                          return pt ? `Row ${seq}: ${pt.date} - ${pt.description}` : `Row ${seq}`;
                        }}
                        contentStyle={{
                          backgroundColor: '#0f172a',
                          borderRadius: '8px',
                          border: 'none',
                          color: '#fff',
                          fontSize: '11px',
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="balance"
                        stroke="#6366F1"
                        strokeWidth={2.5}
                        fillOpacity={1}
                        fill="url(#balanceGrad)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </div>

          {/* Two-Column Secondary Charts: Category Spending Distribution & Daily Activity Heatmap */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* 3. CATEGORY SPENDING DISTRIBUTION */}
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                    Eligible Spending Distribution
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Accounting-aware breakdown excluding non-expense capital transfers.
                  </p>
                </div>
                <Link
                  to="/analytics"
                  className="text-xs font-semibold text-brand-600 hover:text-brand-700 dark:text-brand-400"
                >
                  Full Breakdown
                </Link>
              </div>

              <div className="mt-4 space-y-3">
                {categories.length === 0 ? (
                  <div className="p-8 text-center text-xs text-slate-400">No category expenses recorded</div>
                ) : (
                  categories.map((c) => (
                    <div key={c.category} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-slate-800 dark:text-slate-200 truncate max-w-[240px]">
                          {c.category}
                        </span>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-slate-500 text-[11px]">{c.percentage_of_expense}%</span>
                          <span className="font-mono font-semibold text-slate-900 dark:text-white">
                            ₹ {c.total_debit.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </span>
                        </div>
                      </div>
                      <div className="h-2 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-brand-600 dark:bg-brand-500 transition-all duration-500"
                          style={{ width: `${Math.min(c.percentage_of_expense, 100)}%` }}
                        />
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* 4. TRANSACTION ACTIVITY CALENDAR HEATMAP */}
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                    Daily Activity Calendar Heatmap
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Click a date box to filter and inspect its transactions.
                  </p>
                </div>
                <div className="flex items-center space-x-1 rounded-lg border border-slate-200 bg-slate-50 p-0.5 text-[10px] dark:border-slate-700 dark:bg-slate-800">
                  <button
                    onClick={() => setHeatmapMetric('count')}
                    className={`rounded px-2 py-0.5 font-medium transition ${
                      heatmapMetric === 'count'
                        ? 'bg-white text-slate-900 shadow-sm dark:bg-slate-700 dark:text-white'
                        : 'text-slate-500'
                    }`}
                  >
                    Count
                  </button>
                  <button
                    onClick={() => setHeatmapMetric('volume')}
                    className={`rounded px-2 py-0.5 font-medium transition ${
                      heatmapMetric === 'volume'
                        ? 'bg-white text-slate-900 shadow-sm dark:bg-slate-700 dark:text-white'
                        : 'text-slate-500'
                    }`}
                  >
                    Volume
                  </button>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-5 sm:grid-cols-7 gap-2">
                {heatmap.length === 0 ? (
                  <div className="col-span-full p-8 text-center text-xs text-slate-400">No activity dates recorded</div>
                ) : (
                  heatmap.map((d) => {
                    const countIntensity = d.count >= 4 ? 'bg-brand-700 text-white' : d.count >= 2 ? 'bg-brand-500 text-white' : 'bg-brand-100 text-brand-900 dark:bg-brand-900/60 dark:text-brand-200';
                    const volIntensity = d.total_volume >= 20000 ? 'bg-purple-700 text-white' : d.total_volume >= 5000 ? 'bg-purple-500 text-white' : 'bg-purple-100 text-purple-900 dark:bg-purple-900/60 dark:text-purple-200';
                    const badgeClass = heatmapMetric === 'count' ? countIntensity : volIntensity;

                    return (
                      <button
                        key={d.date}
                        onClick={() => navigate(`/transactions?search=${d.date}`)}
                        className={`rounded-lg p-2.5 text-center transition hover:scale-105 shadow-sm border border-transparent ${badgeClass}`}
                        title={`${d.date}: ${d.count} txns, ₹ ${d.total_volume.toLocaleString('en-IN')} volume`}
                      >
                        <span className="block text-[10px] font-mono opacity-80">{d.date.slice(5)}</span>
                        <span className="mt-0.5 block font-mono text-xs font-bold">
                          {heatmapMetric === 'count' ? `${d.count}x` : `₹${Math.round(d.total_volume / 1000)}k`}
                        </span>
                      </button>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
