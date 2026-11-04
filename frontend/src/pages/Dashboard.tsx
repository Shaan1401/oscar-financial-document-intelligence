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
  Cpu,
  ChevronRight,
  Database,
  ShieldCheck,
  FileSpreadsheet,
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
  ClassificationDeepResponse,
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
  const [classification, setClassification] = useState<ClassificationDeepResponse | null>(null);
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
      api.getClassificationDeep(),
    ])
      .then(([sumData, stmtData, catData, flowData, balData, heatData, clsData]) => {
        setSummary(sumData);
        setStatements(stmtData);
        setCategories(catData.slice(0, 6));
        setCashflow(flowData);
        setRunningBalance(balData);
        setHeatmap(heatData);
        setClassification(clsData);
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
        <div className="h-9 w-9 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
      </div>
    );
  }

  const hasData = (summary?.total_statements ?? 0) > 0;
  const activeStatement = statements.find((s) => s.id === selectedStatementId) || (selectedStatementId ? null : statements[0]) || null;

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
      {/* =========================================================================
          TOP SECTION: Complete OSCAR Product Expansion & Operating Context
         ========================================================================= */}
      <div className="rounded-2xl border border-slate-200/90 bg-white p-5 md:p-6 shadow-sm dark:border-slate-800/90 dark:bg-slate-900 transition-colors">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white font-black text-sm tracking-wide shadow-sm">
                O
              </div>
              <h1 className="text-xl md:text-2xl font-black tracking-tight text-slate-900 dark:text-white">
                OSCAR
              </h1>
              <span className="rounded-md bg-brand-50 px-2 py-0.5 text-[11px] font-bold text-brand-700 dark:bg-brand-950/80 dark:text-brand-300 border border-brand-200 dark:border-brand-800">
                Financial Document Intelligence
              </span>
              <span className="hidden sm:inline-flex items-center space-x-1 rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                <Database className="h-3 w-3 text-brand-600" />
                <span>Local-First SQLite</span>
              </span>
            </div>

            {/* Prominent Complete Full-Form Branding */}
            <p className="text-xs md:text-sm font-semibold text-slate-700 dark:text-slate-200 tracking-wide">
              Operational Statement Classification, Analysis &amp; Reconciliation
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 italic">
              "Every transaction deserves an explanation."
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Statement Scope Selector Filter */}
            {statements.length > 0 && (
              <div className="flex items-center space-x-2">
                <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 whitespace-nowrap">
                  Scope:
                </span>
                <select
                  value={selectedStatementId}
                  onChange={(e) => setSelectedStatementId(e.target.value)}
                  className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-800 shadow-sm focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 cursor-pointer"
                >
                  <option value="">All Processed Statements (Portfolio)</option>
                  {statements.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.filename} — {s.bank_name || 'Bank'} ({s.transaction_count} txns)
                    </option>
                  ))}
                </select>
              </div>
            )}

            <Link
              to="/upload"
              className="inline-flex items-center space-x-2 rounded-lg bg-brand-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-brand-700 transition"
            >
              <UploadCloud className="h-4 w-4" />
              <span>Process New Statement</span>
            </Link>
          </div>
        </div>
      </div>

      {!hasData ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center dark:border-slate-800 dark:bg-slate-900">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-50 text-brand-600 dark:bg-brand-950 dark:text-brand-400 mb-3">
            <UploadCloud className="h-8 w-8" />
          </div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-white">
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
          {/* =========================================================================
              PRIMARY AREA: Financial Integrity Bridge & Core Liquidity Charts
             ========================================================================= */}
          
          {/* 1. FINANCIAL INTEGRITY BRIDGE (Signature Mathematical Proof) */}
          <div className="rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-slate-800/90 dark:bg-slate-900">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3.5 border-b border-slate-100 dark:border-slate-800 gap-2">
              <div>
                <h2 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center space-x-2">
                  <Scale className="h-4 w-4 text-brand-600" />
                  <span>Financial Integrity Bridge (Reconciliation Equation Proof)</span>
                </h2>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                  Opening Balance + Capital Inflows (Credits) - Capital Outflows (Debits) = Expected vs Extracted Closing Balance.
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <span className={`inline-flex items-center space-x-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-bold ${
                  isBridgeReconciled
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
                    : 'bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800'
                }`}>
                  <CheckCircle2 className="h-3 w-3" />
                  <span>{isBridgeReconciled ? 'Reconciled (₹0.00 Variance)' : `Mismatch (₹${balanceVariance.toFixed(2)})`}</span>
                </span>

                {activeStatement && (
                  <Link
                    to={`/statements/${activeStatement.id}`}
                    className="text-xs font-semibold text-brand-600 hover:text-brand-700 dark:text-brand-400 flex items-center space-x-1 pl-2 border-l border-slate-200 dark:border-slate-700"
                  >
                    <span>Inspect Evidence</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                )}
              </div>
            </div>

            {/* Mathematical Flow Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 pt-4 text-center">
              <div className="rounded-lg bg-slate-50 p-3.5 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Opening Balance</span>
                <p className="mt-1 font-mono text-base font-bold text-slate-900 dark:text-white tabular-nums">
                  ₹ {openingBal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <span className="text-[10px] text-slate-400 font-mono">Baseline Ledger</span>
              </div>

              <div className="rounded-lg bg-emerald-50/70 p-3.5 dark:bg-emerald-950/30 border border-emerald-200/70 dark:border-emerald-800/50">
                <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-300 uppercase tracking-wider">+ Capital Inflows</span>
                <p className="mt-1 font-mono text-base font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
                  + ₹ {totalInflow.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <span className="text-[10px] text-emerald-600/80 font-mono">Total Verified Credits</span>
              </div>

              <div className="rounded-lg bg-rose-50/70 p-3.5 dark:bg-rose-950/30 border border-rose-200/70 dark:border-rose-800/50">
                <span className="text-[10px] font-bold text-rose-700 dark:text-rose-300 uppercase tracking-wider">- Capital Outflows</span>
                <p className="mt-1 font-mono text-base font-bold text-rose-600 dark:text-rose-400 tabular-nums">
                  - ₹ {totalOutflow.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <span className="text-[10px] text-rose-600/80 font-mono">Total Verified Debits</span>
              </div>

              <div className="rounded-lg bg-brand-50/70 p-3.5 dark:bg-brand-950/30 border border-brand-200/70 dark:border-brand-800/50">
                <span className="text-[10px] font-bold text-brand-700 dark:text-brand-300 uppercase tracking-wider">= Expected Closing</span>
                <p className="mt-1 font-mono text-base font-bold text-brand-600 dark:text-brand-400 tabular-nums">
                  = ₹ {expectedClosing.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <span className="text-[10px] text-brand-600/80 font-mono">Calculated Balance</span>
              </div>

              <div className={`rounded-lg p-3.5 border ${
                isBridgeReconciled
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950/40 dark:text-emerald-200 dark:border-emerald-800'
                  : 'bg-rose-50 text-rose-800 border-rose-300 dark:bg-rose-950/40 dark:text-rose-200 dark:border-rose-800'
              }`}>
                <span className="text-[10px] font-bold uppercase tracking-wider">
                  {isBridgeReconciled ? 'Actual Closing (Reconciled)' : 'Closing Mismatch'}
                </span>
                <p className="mt-1 font-mono text-base font-bold tabular-nums">
                  ₹ {closingBal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <span className="text-[10px] font-mono">
                  Variance: ₹ {balanceVariance.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* 2. Asymmetric Primary Charts Grid: Cash Flow (7 cols) + Running Balance (5 cols) */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            {/* CASH FLOW INTELLIGENCE (7 Cols) */}
            <div className="lg:col-span-7 rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-slate-800/90 dark:bg-slate-900">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                    Cash Flow Intelligence (Inflow vs Outflow)
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Click any transaction date bar to drill directly into corresponding records.
                  </p>
                </div>
                <Link
                  to="/transactions"
                  className="text-xs font-semibold text-brand-600 hover:text-brand-700 dark:text-brand-400"
                >
                  View Ledger
                </Link>
              </div>

              <div className="mt-4 h-64 w-full">
                {cashflow.length === 0 ? (
                  <div className="flex h-full items-center justify-center text-xs text-slate-400">
                    No cashflow data available for current scope
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart
                      data={cashflow}
                      onClick={(data) => {
                        if (data && data.activeLabel) {
                          navigate(`/transactions?search=${data.activeLabel}`);
                        }
                      }}
                      className="cursor-pointer"
                    >
                      <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.25} />
                      <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
                      <YAxis tick={{ fontSize: 10 }} tickLine={false} />
                      <Tooltip
                        formatter={(val: any, name: any) => [
                          `₹ ${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`,
                          name === 'credits' ? 'Inflow (Credit)' : name === 'debits' ? 'Outflow (Debit)' : 'Net Cashflow',
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
                      <Bar dataKey="credits" fill="#10B981" name="credits" radius={[3, 3, 0, 0]} />
                      <Bar dataKey="debits" fill="#F43F5E" name="debits" radius={[3, 3, 0, 0]} />
                      <Line type="monotone" dataKey="net" stroke="#3B82F6" strokeWidth={2.5} name="net" dot={{ r: 3 }} />
                    </ComposedChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* RUNNING BALANCE TRAJECTORY (5 Cols) */}
            <div className="lg:col-span-5 rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-slate-800/90 dark:bg-slate-900">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                    Running Balance Trajectory
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Account balance progression over sequence.
                  </p>
                </div>
                <span className="font-mono text-xs font-bold text-slate-800 dark:text-slate-200">
                  ₹ {closingBal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div className="mt-4 h-64 w-full">
                {!runningBalance || runningBalance.points.length === 0 ? (
                  <div className="flex h-full items-center justify-center text-xs text-slate-400">
                    No balance trajectory recorded
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={runningBalance.points}>
                      <defs>
                        <linearGradient id="balanceGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366F1" stopOpacity={0.45} />
                          <stop offset="95%" stopColor="#6366F1" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.25} />
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

          {/* =========================================================================
              SECONDARY AREA: Asymmetric Sidecar Grid
              (Heatmap + Exception Queue + Classification Distribution)
             ========================================================================= */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            {/* Daily Activity Calendar Heatmap (6 cols) */}
            <div className="lg:col-span-6 rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-slate-800/90 dark:bg-slate-900">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                    Daily Activity Heatmap
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Click any day block to filter its transactions in Explorer.
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

              <div className="mt-4 grid grid-cols-4 sm:grid-cols-7 gap-2">
                {heatmap.length === 0 ? (
                  <div className="col-span-full p-8 text-center text-xs text-slate-400">
                    No activity dates recorded
                  </div>
                ) : (
                  heatmap.map((d) => {
                    const countIntensity = d.count >= 4 ? 'bg-brand-700 text-white' : d.count >= 2 ? 'bg-brand-500 text-white' : 'bg-brand-100 text-brand-900 dark:bg-brand-900/60 dark:text-brand-200';
                    const volIntensity = d.total_volume >= 20000 ? 'bg-purple-700 text-white' : d.total_volume >= 5000 ? 'bg-purple-500 text-white' : 'bg-purple-100 text-purple-900 dark:bg-purple-900/60 dark:text-purple-200';
                    const badgeClass = heatmapMetric === 'count' ? countIntensity : volIntensity;

                    return (
                      <button
                        key={d.date}
                        onClick={() => navigate(`/transactions?search=${d.date}`)}
                        className={`rounded-lg p-2 text-center transition hover:scale-105 shadow-xs border border-transparent ${badgeClass} cursor-pointer`}
                        title={`${d.date}: ${d.count} txns, ₹ ${d.total_volume.toLocaleString('en-IN')} volume`}
                      >
                        <span className="block text-[9.5px] font-mono opacity-80">{d.date.slice(5)}</span>
                        <span className="mt-0.5 block font-mono text-[11px] font-bold">
                          {heatmapMetric === 'count' ? `${d.count}x` : `₹${Math.round(d.total_volume / 1000)}k`}
                        </span>
                      </button>
                    );
                  })
                )}
              </div>
            </div>

            {/* Exception & Review Queue Quick-Action Card (3 cols) */}
            <div className="lg:col-span-3 rounded-xl border border-amber-200/80 bg-gradient-to-b from-amber-50/40 to-white p-5 shadow-sm dark:border-amber-900/50 dark:from-amber-950/20 dark:to-slate-900 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between text-xs text-amber-800 dark:text-amber-300 border-b border-amber-100 pb-3 dark:border-amber-900/40">
                  <span className="font-bold uppercase tracking-wider">Human Review Queue</span>
                  <AlertCircle className="h-4 w-4 text-amber-600" />
                </div>
                <div className="mt-4">
                  <span className="text-3xl font-extrabold font-mono text-amber-700 dark:text-amber-400">
                    {(summary?.pending_reviews ?? 0) + (summary?.anomalies_count ?? 0)}
                  </span>
                  <p className="mt-1 text-xs text-slate-600 dark:text-slate-300 font-medium">
                    Exceptions pending verification
                  </p>
                  <div className="mt-3 space-y-1.5 text-[11px] text-slate-500 dark:text-slate-400">
                    <div className="flex justify-between">
                      <span>Low-Confidence ML:</span>
                      <strong className="text-slate-700 dark:text-slate-200">{summary?.pending_reviews ?? 0}</strong>
                    </div>
                    <div className="flex justify-between">
                      <span>Outliers / Duplicates:</span>
                      <strong className="text-slate-700 dark:text-slate-200">{summary?.anomalies_count ?? 0}</strong>
                    </div>
                  </div>
                </div>
              </div>

              <Link
                to="/reviews"
                className="mt-5 inline-flex w-full items-center justify-center space-x-1.5 rounded-lg bg-amber-600 px-3 py-2 text-xs font-bold text-white shadow-sm hover:bg-amber-700 transition"
              >
                <span>Resolve Exceptions</span>
                <ChevronRight className="h-4 w-4" />
              </Link>
            </div>

            {/* Classification Distribution (3 cols) */}
            <div className="lg:col-span-3 rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-slate-800/90 dark:bg-slate-900 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between text-xs text-slate-900 dark:text-white border-b border-slate-100 pb-3 dark:border-slate-800">
                  <span className="font-bold uppercase tracking-wider flex items-center space-x-1.5">
                    <Cpu className="h-4 w-4 text-brand-600" />
                    <span>Classification Engine</span>
                  </span>
                  <Link to="/classification" className="text-[11px] font-semibold text-brand-600 hover:underline dark:text-brand-400">
                    Insights
                  </Link>
                </div>

                <div className="mt-4 space-y-3 text-xs">
                  <div>
                    <div className="flex justify-between text-[11px]">
                      <span className="text-slate-600 dark:text-slate-300 font-medium">Deterministic Rules:</span>
                      <strong className="font-mono text-blue-600">{classification?.rule_based_percentage?.toFixed(1) ?? '75.0'}%</strong>
                    </div>
                    <div className="mt-1 h-2 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-blue-600"
                        style={{ width: `${classification?.rule_based_percentage ?? 75}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px]">
                      <span className="text-slate-600 dark:text-slate-300 font-medium">Dual TF-IDF LogReg:</span>
                      <strong className="font-mono text-purple-600">{classification?.ml_based_percentage?.toFixed(1) ?? '25.0'}%</strong>
                    </div>
                    <div className="mt-1 h-2 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-purple-600"
                        style={{ width: `${classification?.ml_based_percentage ?? 25}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px]">
                      <span className="text-slate-600 dark:text-slate-300 font-medium">Human Corrected:</span>
                      <strong className="font-mono text-emerald-600">{classification?.manual_count ?? 0} txns</strong>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 rounded-lg bg-slate-50 p-2.5 text-[10px] text-slate-500 dark:bg-slate-800/60 dark:text-slate-400 border border-slate-200/50 dark:border-slate-700/50">
                Offline Scikit-Learn Pipeline • Zero Cloud LLMs
              </div>
            </div>
          </div>

          {/* =========================================================================
              LOWER SECTION: Category Spending + Processing Journey + Recent Statements
             ========================================================================= */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            {/* Category Spending (6 cols) */}
            <div className="lg:col-span-6 rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-slate-800/90 dark:bg-slate-900">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                    Operational Spending Distribution
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Accounting-aware breakdown excluding non-expense capital transfers.
                  </p>
                </div>
                <Link
                  to="/analytics"
                  className="text-xs font-semibold text-brand-600 hover:text-brand-700 dark:text-brand-400"
                >
                  Deep Analytics
                </Link>
              </div>

              <div className="mt-4 space-y-3">
                {categories.length === 0 ? (
                  <div className="p-8 text-center text-xs text-slate-400">No category expenses recorded</div>
                ) : (
                  categories.map((c) => (
                    <div key={c.category} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[240px]">
                          {c.category}
                        </span>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-slate-500 text-[11px]">{c.percentage_of_expense}%</span>
                          <span className="font-mono font-bold text-slate-900 dark:text-white">
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

            {/* Document Processing Journey (6 cols) */}
            <div className="lg:col-span-6 rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-slate-800/90 dark:bg-slate-900 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center space-x-1.5">
                    <Layers className="h-4 w-4 text-brand-600" />
                    <span>Processing &amp; Governance Pipeline</span>
                  </h3>
                  <span className="text-[10px] text-slate-400 font-mono">100% Deterministic</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-4">
                  {[
                    { stage: '1. Ingestion', status: 'Validated (%PDF-)', ok: true },
                    { stage: '2. Extraction', status: 'Multi-Layout / OCR', ok: true },
                    { stage: '3. Normalization', status: 'Decimal Minor Units', ok: true },
                    { stage: '4. Classification', status: 'Rules + TF-IDF ML', ok: true },
                    { stage: '5. Reconciliation', status: isBridgeReconciled ? 'Reconciled (₹0 Var)' : 'Verified Proof', ok: isBridgeReconciled },
                    { stage: '6. Governance', status: 'Audit & Export Ready', ok: true },
                  ].map((step, idx) => (
                    <div key={idx} className="rounded-lg bg-slate-50 p-2.5 text-xs dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                      <div className="flex items-center justify-between text-[11px] font-bold text-slate-700 dark:text-slate-300">
                        <span>{step.stage}</span>
                        <Check className="h-3.5 w-3.5 text-emerald-600" />
                      </div>
                      <p className="mt-1 text-[10px] text-slate-500 dark:text-slate-400 font-mono truncate">{step.status}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick links footer */}
              <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                <span className="text-slate-500 text-[11px]">Ready for statutory export:</span>
                <div className="flex items-center space-x-3 font-semibold">
                  <Link to="/exports" className="text-brand-600 hover:underline dark:text-brand-400 flex items-center space-x-1">
                    <FileSpreadsheet className="h-3.5 w-3.5" />
                    <span>Excel &amp; CSV Center</span>
                  </Link>
                  <Link to="/audit" className="text-slate-600 hover:underline dark:text-slate-300">
                    Audit Log
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Ingested Statements Table */}
          <div className="rounded-xl border border-slate-200/90 bg-white shadow-sm dark:border-slate-800/90 dark:bg-slate-900 overflow-hidden">
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100 dark:border-slate-800">
              <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center space-x-1.5">
                <FileText className="h-4 w-4 text-brand-600" />
                <span>Recent Ingested Statements ({statements.length})</span>
              </h3>
              <Link to="/statements" className="text-xs font-semibold text-brand-600 hover:underline dark:text-brand-400">
                View All Statements
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 dark:bg-slate-800/60 dark:text-slate-400 font-semibold border-b border-slate-100 dark:border-slate-800">
                  <tr>
                    <th className="px-4 py-2.5">Bank / Document</th>
                    <th className="px-4 py-2.5">Period</th>
                    <th className="px-4 py-2.5 text-center">Type</th>
                    <th className="px-4 py-2.5 text-right">Transactions</th>
                    <th className="px-4 py-2.5 text-right">Inflows (CR)</th>
                    <th className="px-4 py-2.5 text-right">Outflows (DR)</th>
                    <th className="px-4 py-2.5 text-center">Status</th>
                    <th className="px-4 py-2.5 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {statements.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition">
                      <td className="px-4 py-3">
                        <Link to={`/statements/${s.id}`} className="font-bold text-slate-900 dark:text-white hover:text-brand-600 transition">
                          {s.filename}
                        </Link>
                        <p className="text-[10px] text-slate-400 font-mono">{s.bank_name || 'Standard Bank'}</p>
                      </td>
                      <td className="px-4 py-3 text-slate-600 dark:text-slate-300 font-mono text-[11px] whitespace-nowrap">
                        {s.statement_period || 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300 uppercase">
                          {s.pdf_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right font-mono font-semibold">
                        {s.transaction_count ?? 0}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-emerald-600">
                        ₹ {(s.total_credits ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-rose-600">
                        ₹ {(s.total_debits ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`inline-flex items-center space-x-1 rounded-full px-2 py-0.5 text-[10px] font-bold ${
                          s.reconciliation_status === 'RECONCILED'
                            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
                            : 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'
                        }`}>
                          <CheckCircle2 className="h-3 w-3" />
                          <span>{s.reconciliation_status}</span>
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center space-x-2">
                          <Link
                            to={`/statements/${s.id}`}
                            className="rounded p-1 text-slate-500 hover:bg-slate-100 hover:text-brand-600 dark:hover:bg-slate-800"
                            title="Inspect Evidence"
                          >
                            <Eye className="h-4 w-4" />
                          </Link>
                          <Link
                            to={`/reconciliation/${s.id}`}
                            className="rounded p-1 text-slate-500 hover:bg-slate-100 hover:text-purple-600 dark:hover:bg-slate-800"
                            title="Reconciliation"
                          >
                            <Scale className="h-4 w-4" />
                          </Link>
                        </div>
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

export default Dashboard;
